"""Preflight check for a GPU job bundle.

Scans a job's script + model artifacts and emits a single recommended
pip-pin list + a list of run-time gotchas. Catches in 5 seconds the
class of failure that otherwise burns 5-15 cycles of rent-a-GPU,
pip-resolve, model-download, crash, fix, retry.

Usage:
    python preflight_gpu_job.py \
        --script         runpod_bundle/run_inference.py \
        --tarball        runpod_bundle/biobert_checkpoint.tar.gz \
        --tarball        runpod_bundle/llama_lora.tar.gz \
        --adapter-dir    models/llama-3-seen-oov-results/llama-3-seen-oov-results \
        --base-model     meta-llama/Meta-Llama-3-8B-Instruct

Output: a structured report on stdout, exit 0 if no FATAL issues, 1 otherwise.

Checks performed:
  1. AST-parse the script: list third-party imports
  2. Cross-reference imports vs a curated "ships with base image" set
     (torch, numpy, pandas, transformers); emit a pip list for the rest
  3. Inspect each LoRA adapter_config.json: extract peft_version, scan
     for keys that require a specific peft (alora_invocation_tokens,
     qalora_group_size, lora_bias, trainable_token_indices, ...).
     Emit "peft>=X,<X+1" pin.
  4. Inspect each tokenizer_config.json: check tokenizer_class. If it
     uses a class that doesn't ship with transformers<4.50 (e.g.
     "TokenizersBackend"), warn and recommend either bumping transformers
     or falling back to the base tokenizer.
  5. Inspect adapter's base_model_name_or_path: warn if it's an
     instruct-tuned base (script must call apply_chat_template) or a
     quantized base (script must use matching bnb config).
  6. Probe each base model on HF anonymously: if 401, recommend
     non-gated mirrors (NousResearch, unsloth, etc.).
  7. tar-list each .tar.gz: detect tarballs created on Windows
     (numeric uid/gid that's not 0 or 1000); recommend --no-same-owner.

The output is intentionally a flat report, not an exit code suite,
because preflight findings are advisory: the user/skill operator
decides how to act on each one.
"""
from __future__ import annotations
import argparse
import ast
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path

# -- shipped-in-default-image packages (RunPod runpod/pytorch:2.4 + vast.ai
#    vastai/pytorch:2.5 both ship these); a script that imports only these
#    needs no extra pip install
SHIPS_WITH_BASE = {
    "torch", "torchvision", "torchaudio", "numpy", "pandas", "scipy",
    "matplotlib", "PIL", "sklearn", "tqdm", "yaml", "requests",
    "pathlib", "subprocess", "json", "os", "sys", "re", "time", "io",
    "logging", "warnings", "collections", "itertools", "functools",
    "typing", "dataclasses", "argparse", "datetime", "enum", "math",
    "random", "abc", "copy", "contextlib", "ast", "inspect",
}

# -- canonical PyPI names for common third-party imports the script uses
IMPORT_TO_PIP = {
    "transformers": "transformers",
    "peft": "peft",
    "bitsandbytes": "bitsandbytes",
    "accelerate": "accelerate",
    "trl": "trl",
    "datasets": "datasets",
    "dateparser": "dateparser",
    "huggingface_hub": "huggingface_hub",
    "sentence_transformers": "sentence-transformers",
    "tokenizers": "tokenizers",
    "safetensors": "safetensors",
    "wandb": "wandb",
    "tensorboard": "tensorboard",
    "evaluate": "evaluate",
    "rouge_score": "rouge-score",
    "nltk": "nltk",
    "spacy": "spacy",
}

# -- adapter_config.json keys introduced after a specific peft version.
#    Loading an adapter whose config has these keys with an older peft
#    raises TypeError on LoraConfig.__init__.
PEFT_KEY_INTRODUCED = {
    "alora_invocation_tokens": "0.15",
    "qalora_group_size":        "0.15",
    "lora_bias":                "0.14",
    "trainable_token_indices":  "0.15",
    "use_bdlora":               "0.15",
    "use_qalora":               "0.15",
    "use_dora":                 "0.10",
    "use_rslora":               "0.10",
    "lora_ga_config":           "0.15",
    "eva_config":               "0.13",
    "corda_config":             "0.13",
    "arrow_config":             "0.15",
    "ensure_weight_tying":      "0.15",
    "exclude_modules":          "0.13",
    "loftq_config":             "0.7",
    "megatron_config":          "0.5",
}

# -- tokenizer_class names that aren't in transformers<4.50
TOKENIZER_CLASS_MIN_TRANSFORMERS = {
    "TokenizersBackend": "4.50",
}


class Report:
    def __init__(self) -> None:
        self.findings: list[tuple[str, str, str]] = []   # (level, area, text)
        self.pip_pins: dict[str, str] = {}
        self.has_fatal = False

    def add(self, level: str, area: str, text: str) -> None:
        self.findings.append((level, area, text))
        if level == "FATAL":
            self.has_fatal = True

    def pin(self, pkg: str, spec: str) -> None:
        # If multiple sources demand different pins, narrow the intersection
        existing = self.pip_pins.get(pkg)
        if existing and existing != spec:
            self.add("WARN", "pin", f"Conflicting pins for {pkg}: {existing} vs {spec}; keeping latest")
        self.pip_pins[pkg] = spec

    def emit(self) -> int:
        print("=" * 70)
        print("  PREFLIGHT REPORT")
        print("=" * 70)
        by_area: dict[str, list[tuple[str, str]]] = {}
        for level, area, text in self.findings:
            by_area.setdefault(area, []).append((level, text))
        for area in by_area:
            print(f"\n[{area}]")
            for level, text in by_area[area]:
                print(f"  {level:<6} {text}")
        print()
        print("-" * 70)
        print("  Recommended pip pin set")
        print("-" * 70)
        for pkg, spec in sorted(self.pip_pins.items()):
            print(f"  {pkg}{spec}")
        print()
        if self.has_fatal:
            print("FATAL ISSUES FOUND; do not launch.")
            return 1
        if any(level == "WARN" for level, _, _ in self.findings):
            print("Warnings present; review before launch.")
        else:
            print("OK to launch.")
        return 0


def scan_script(script_path: Path, rep: Report) -> set[str]:
    """AST-parse the script, return third-party imports (canonical PyPI names)."""
    try:
        tree = ast.parse(script_path.read_text())
    except SyntaxError as e:
        rep.add("FATAL", "script", f"{script_path}: {e}")
        return set()
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                imports.add(node.module.split(".")[0])
    # Exclude stdlib aliases and any module whose .py sits alongside the script
    # (vendored sibling modules like time_utils, data_utils, ontology — those
    # ship in the data bundle, not in pip).
    sibling_modules = {p.stem for p in script_path.parent.glob("*.py")}
    STDLIB_ALIASES = {"__future__", "builtins"}
    third_party = {m for m in imports
                   if m not in SHIPS_WITH_BASE
                   and m not in sibling_modules
                   and m not in STDLIB_ALIASES}
    pinned = set()
    for mod in sorted(third_party):
        if mod in IMPORT_TO_PIP:
            rep.pin(IMPORT_TO_PIP[mod], "")  # unpinned by default
            pinned.add(IMPORT_TO_PIP[mod])
            rep.add("INFO", "imports", f"third-party import '{mod}' -> pip '{IMPORT_TO_PIP[mod]}'")
        else:
            rep.add("WARN", "imports", f"third-party import '{mod}' not in known map; add to pip list manually if not stock")
    return pinned


def scan_adapter(adapter_dir: Path, rep: Report) -> None:
    """Inspect a single LoRA adapter directory."""
    cfg_path = adapter_dir / "adapter_config.json"
    if not cfg_path.exists():
        rep.add("WARN", "adapter", f"{adapter_dir}: no adapter_config.json")
        return
    cfg = json.loads(cfg_path.read_text())
    saved_peft = cfg.get("peft_version", "?")
    rep.add("INFO", "adapter", f"{adapter_dir.name}: saved with peft {saved_peft}")
    base = cfg.get("base_model_name_or_path", "?")
    rep.add("INFO", "adapter", f"{adapter_dir.name}: trained on base '{base}'")
    if "instruct" in base.lower() or "chat" in base.lower():
        rep.add("WARN", "adapter",
                f"Adapter trained on INSTRUCT/CHAT base; inference must use a "
                f"matching instruct base AND the script must call "
                f"tokenizer.apply_chat_template(...) for prompts. Using a "
                f"non-chat base will silently emit "
                f"'<ERROR: Cannot use chat template functions ...>'")
    if "bnb-4bit" in base.lower() or "4bit" in base.lower():
        rep.add("WARN", "adapter",
                f"Adapter trained on a 4-bit quantized base; inference must "
                f"use matching BitsAndBytesConfig or the LoRA delta lands on "
                f"the wrong-precision activations")
    max_required = None
    for k, v in cfg.items():
        if k in PEFT_KEY_INTRODUCED:
            req = PEFT_KEY_INTRODUCED[k]
            rep.add("INFO", "adapter", f"  config key '{k}' present -> requires peft>={req}")
            if max_required is None or _ver_gt(req, max_required):
                max_required = req
    pin_pair = _next_minor(max_required) if max_required else None
    if saved_peft and saved_peft not in ("?", "0", ""):
        saved_pair = _next_minor(saved_peft)
        if not pin_pair or _ver_gt(saved_peft, max_required or "0"):
            pin_pair = saved_pair
    if pin_pair:
        floor, ceil = pin_pair
        rep.pin("peft", f">={floor},<{ceil}")


def _next_minor(ver: str) -> tuple[str, str] | None:
    """Return (floor, ceil) where ceil is the next minor after ver.
    e.g. '0.19.1' -> ('0.19', '0.20'); '0.15' -> ('0.15', '0.16')."""
    parts = re.findall(r"\d+", ver)
    if len(parts) < 2:
        return None
    major, minor = int(parts[0]), int(parts[1])
    return f"{major}.{minor}", f"{major}.{minor + 1}"


def _ver_gt(a: str, b: str) -> bool:
    pa = list(map(int, re.findall(r"\d+", a)))
    pb = list(map(int, re.findall(r"\d+", b)))
    return pa > pb


def scan_tokenizer(adapter_dir: Path, rep: Report) -> None:
    cfg_path = adapter_dir / "tokenizer_config.json"
    if not cfg_path.exists():
        rep.add("INFO", "tokenizer", f"{adapter_dir.name}: no tokenizer_config.json (will use base)")
        return
    cfg = json.loads(cfg_path.read_text())
    cls = cfg.get("tokenizer_class", "?")
    rep.add("INFO", "tokenizer", f"{adapter_dir.name}: tokenizer_class={cls}")
    if cls in TOKENIZER_CLASS_MIN_TRANSFORMERS:
        req = TOKENIZER_CLASS_MIN_TRANSFORMERS[cls]
        rep.add("WARN", "tokenizer",
                f"tokenizer_class '{cls}' requires transformers>={req}; "
                f"either bump transformers pin or fall back to base tokenizer "
                f"in the script (catch ValueError)")
        rep.pin("transformers", f">={req}")


def scan_tarball(tar_path: Path, rep: Report) -> None:
    try:
        with tarfile.open(tar_path, "r:gz") as t:
            sample = t.next()
            if sample is None:
                return
            owner = sample.uid
            if owner > 1000:
                rep.add("WARN", "tarball",
                        f"{tar_path.name}: created on a host with uid={owner} "
                        f"(likely Windows). Extract with tar "
                        f"--no-same-owner --no-same-permissions to avoid "
                        f"'Cannot change ownership' in unprivileged containers")
    except Exception as e:
        rep.add("WARN", "tarball", f"{tar_path}: cannot inspect ({e})")


def probe_hf(model_id: str, rep: Report) -> None:
    """Anonymous HEAD on config.json to detect gating."""
    try:
        import urllib.request
        url = f"https://huggingface.co/{model_id}/resolve/main/config.json"
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=10) as r:
            if r.status == 200:
                rep.add("INFO", "hf", f"{model_id}: publicly accessible")
                return
            rep.add("WARN", "hf", f"{model_id}: HEAD returned {r.status}")
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            mirror = _suggest_mirror(model_id)
            note = f" (suggest non-gated mirror: {mirror})" if mirror else ""
            rep.add("WARN", "hf",
                    f"{model_id}: GATED (HTTP {e.code}){note}; set HF_TOKEN or switch base")
        else:
            rep.add("WARN", "hf", f"{model_id}: HTTP {e.code}")
    except Exception as e:
        rep.add("INFO", "hf", f"{model_id}: probe failed ({e}); proceeding")


def _suggest_mirror(model_id: str) -> str | None:
    table = {
        "meta-llama/Meta-Llama-3-8B":         "NousResearch/Meta-Llama-3-8B",
        "meta-llama/Meta-Llama-3-8B-Instruct": "unsloth/llama-3-8b-Instruct",
        "meta-llama/Llama-2-7b-hf":           "NousResearch/Llama-2-7b-hf",
        "meta-llama/Llama-2-7b-chat-hf":      "NousResearch/Llama-2-7b-chat-hf",
        "meta-llama/Meta-Llama-3-70B":        "NousResearch/Meta-Llama-3-70B",
        "google/gemma-7b":                    "unsloth/gemma-7b",
        "mistralai/Mistral-7B-v0.1":          "unsloth/mistral-7b-v0.1",
        "mistralai/Mistral-7B-Instruct-v0.2": "unsloth/mistral-7b-instruct-v0.2",
    }
    return table.get(model_id)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", type=Path, required=True)
    ap.add_argument("--adapter-dir", type=Path, action="append", default=[],
                    help="Path to a LoRA adapter directory (may repeat)")
    ap.add_argument("--tarball", type=Path, action="append", default=[],
                    help="Path to a .tar.gz to inspect for Windows-uid issues (may repeat)")
    ap.add_argument("--base-model", type=str, action="append", default=[],
                    help="HF model id to probe for gating (may repeat)")
    ap.add_argument("--no-hf-probe", action="store_true", help="Skip HF gating probe")
    args = ap.parse_args()

    rep = Report()
    if not args.script.exists():
        rep.add("FATAL", "script", f"{args.script}: file not found")
        return rep.emit()

    scan_script(args.script, rep)
    for ad in args.adapter_dir:
        if not ad.exists():
            rep.add("WARN", "adapter", f"{ad}: directory not found")
            continue
        scan_adapter(ad, rep)
        scan_tokenizer(ad, rep)
    for tb in args.tarball:
        if not tb.exists():
            rep.add("WARN", "tarball", f"{tb}: file not found")
            continue
        scan_tarball(tb, rep)
    if not args.no_hf_probe:
        for mid in args.base_model:
            probe_hf(mid, rep)

    return rep.emit()


if __name__ == "__main__":
    sys.exit(main())
