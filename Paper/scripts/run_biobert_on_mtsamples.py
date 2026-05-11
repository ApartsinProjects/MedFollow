"""Run the trained BioBERT structured pipeline on MTSamples real-text
notes and score predictions against the 20-note manual gold.

Reproduces Tier-A experiment #1 from the porting plan.

Steps:
  1. Load BioBertNerLinker model from
     models/biobert_joint_seen_oov/biobert_joint_seen_oov/pytorch_model.bin
  2. Run sliding-window BIO tagging over the top-20 MTSamples notes
  3. Decode TestSpecification and TimeSpecification character spans
  4. Apply ontology canonicalization (from newrepo/src/ontology.py)
  5. Apply rule-based temporal normalization (from newrepo/src/time_utils.py)
  6. Heuristic linker: pair each TestSpecification with the nearest
     TimeSpecification span within 200 characters (the trained
     biaffine linker would need a more involved integration; the
     heuristic is sufficient for a first-pass real-text result)
  7. Compare against Data/external/mtsamples/mtsamples_top20_gold.json
     and report set-level F1 over the in-closed-set gold subset

Writes:
  Results/mtsamples_realism_predictions.json   (per-note predictions)
  Results/mtsamples_realism_summary.json       (aggregated metrics)
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from transformers import AutoTokenizer, BertConfig, BertModel

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "models" / "biobert_joint_seen_oov" / "biobert_joint_seen_oov"
GOLD_PATH = ROOT / "Data" / "external" / "mtsamples" / "mtsamples_top20_gold.json"
NEWREPO_SRC = ROOT / "newrepo" / "src"
OUT_PRED = ROOT / "Results" / "mtsamples_realism_predictions.json"
OUT_SUMMARY = ROOT / "Results" / "mtsamples_realism_summary.json"

# Bring in the canonical ontology + time grammar from newrepo (read-only)
sys.path.insert(0, str(NEWREPO_SRC.parent))
from src.ontology import ACTION_ONTOLOGY, normalize_action  # noqa: E402
from src.time_utils import time_text_to_days_offset  # noqa: E402

# ---------- Constants (must match training-time configuration) ----------
TAG2ID = {"O": 0, "B-TEST": 1, "I-TEST": 2, "B-TIME": 3, "I-TIME": 4}
ID2TAG = {v: k for k, v in TAG2ID.items()}
MAX_LEN = 512
DOC_STRIDE = 128
LINK_RADIUS = 200  # characters; heuristic linker

# ---------- Model architecture (NER head only; we skip the linker for
# the real-text experiment and use a nearest-neighbour heuristic) ----------
class BioBertNer(nn.Module):
    def __init__(self, config: BertConfig, num_tags: int):
        super().__init__()
        # Build encoder from config only (no remote weight download); our
        # state_dict will overwrite all weights below anyway.
        self.encoder = BertModel(config)
        self.ner_head = nn.Linear(config.hidden_size, num_tags)

    def forward(self, input_ids, attention_mask):
        h = self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        return self.ner_head(h)


def load_model(device: str):
    cfg = json.load(open(MODEL_DIR / "model_config.json"))
    print(f"  base config: {cfg['base_name']}  num_tags={cfg['num_tags']}")
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
    # Inline BertConfig for dmis-lab/biobert-base-cased-v1.1 (standard
    # BERT-base hyperparameters). Avoids any HuggingFace remote fetch.
    config = BertConfig(
        vocab_size=28996,
        hidden_size=768,
        num_hidden_layers=12,
        num_attention_heads=12,
        intermediate_size=3072,
        max_position_embeddings=512,
        type_vocab_size=2,
        pad_token_id=0,
    )
    model = BioBertNer(config, cfg["num_tags"]).to(device)
    sd_full = torch.load(MODEL_DIR / "pytorch_model.bin", map_location=device, weights_only=False)
    sd_ner_only = {k: v for k, v in sd_full.items() if k.startswith("encoder.") or k.startswith("ner_head.")}
    missing, unexpected = model.load_state_dict(sd_ner_only, strict=False)
    print(f"  loaded {len(sd_ner_only)} tensors; missing={len(missing)} unexpected={len(unexpected)}")
    model.eval()
    return model, tokenizer


# ---------- Sliding-window NER ----------
@torch.no_grad()
def predict_spans(model: BioBertNer, tokenizer, text: str, device: str):
    enc = tokenizer(
        text, return_offsets_mapping=True, truncation=True,
        max_length=MAX_LEN, stride=DOC_STRIDE, padding="max_length",
        return_overflowing_tokens=True, return_tensors="pt",
    )
    input_ids = enc["input_ids"].to(device)
    attn = enc["attention_mask"].to(device)
    offsets = enc["offset_mapping"].cpu().numpy()

    logits = model(input_ids, attn)
    preds = logits.argmax(-1).cpu().numpy()  # [n_windows, max_len]

    # Decode per-window BIO into char spans, then merge across windows
    seen = set()
    test_spans = []
    time_spans = []
    for win_i in range(preds.shape[0]):
        offs = offsets[win_i]
        tags = preds[win_i]
        cur = None
        cur_kind = None
        for i, ((s, e), tid) in enumerate(zip(offs, tags)):
            if s == 0 and e == 0:
                # special token or padding
                if cur is not None:
                    cs = offs[cur[0]][0]; ce = offs[cur[1]][1]
                    txt = text[cs:ce].strip()
                    if txt:
                        key = (cs, ce, cur_kind)
                        if key not in seen:
                            seen.add(key)
                            (test_spans if cur_kind == "TEST" else time_spans).append((int(cs), int(ce), txt))
                cur = None; cur_kind = None
                continue
            tag = ID2TAG[int(tid)]
            if tag in ("B-TEST", "B-TIME"):
                if cur is not None:
                    cs = offs[cur[0]][0]; ce = offs[cur[1]][1]
                    txt = text[cs:ce].strip()
                    if txt:
                        key = (cs, ce, cur_kind)
                        if key not in seen:
                            seen.add(key)
                            (test_spans if cur_kind == "TEST" else time_spans).append((int(cs), int(ce), txt))
                cur = [i, i]
                cur_kind = "TEST" if tag == "B-TEST" else "TIME"
            elif tag in ("I-TEST", "I-TIME") and cur is not None and cur_kind == tag.split("-")[1]:
                cur[1] = i
            else:
                if cur is not None:
                    cs = offs[cur[0]][0]; ce = offs[cur[1]][1]
                    txt = text[cs:ce].strip()
                    if txt:
                        key = (cs, ce, cur_kind)
                        if key not in seen:
                            seen.add(key)
                            (test_spans if cur_kind == "TEST" else time_spans).append((int(cs), int(ce), txt))
                cur = None; cur_kind = None
        # flush
        if cur is not None:
            cs = offs[cur[0]][0]; ce = offs[cur[1]][1]
            txt = text[cs:ce].strip()
            if txt:
                key = (cs, ce, cur_kind)
                if key not in seen:
                    seen.add(key)
                    (test_spans if cur_kind == "TEST" else time_spans).append((int(cs), int(ce), txt))

    return test_spans, time_spans


def link_heuristic(test_spans, time_spans, radius: int = LINK_RADIUS):
    """For each TEST span, find the nearest TIME span within `radius` characters.
    Returns list of (test_span, time_span_or_None) pairs."""
    pairs = []
    used = set()
    for ts in test_spans:
        ts_cs, ts_ce, _ = ts
        best = None
        best_d = None
        for j, tm in enumerate(time_spans):
            if j in used: continue
            tm_cs, tm_ce, _ = tm
            d = min(abs(ts_cs - tm_ce), abs(tm_cs - ts_ce))
            if d > radius: continue
            if best_d is None or d < best_d:
                best = j; best_d = d
        if best is not None:
            used.add(best)
            pairs.append((ts, time_spans[best]))
        else:
            pairs.append((ts, None))
    return pairs


def build_predictions(test_spans, time_spans):
    """Build a list of {action, days_offset} dicts after ontology + temporal normalization."""
    pairs = link_heuristic(test_spans, time_spans)
    out = []
    for ts, tm in pairs:
        ts_cs, ts_ce, ts_txt = ts
        canonical = normalize_action(ts_txt)
        if canonical not in ACTION_ONTOLOGY:
            continue
        if tm is None:
            continue
        tm_cs, tm_ce, tm_txt = tm
        days = time_text_to_days_offset(tm_txt)
        if days is None:
            continue
        out.append({"action": canonical, "days_offset": int(days),
                    "test_span": [ts_cs, ts_ce, ts_txt],
                    "time_span": [tm_cs, tm_ce, tm_txt]})
    return out


def evaluate_against_gold(predictions: list, gold_items: list):
    """Compute set-level F1 over (action, days_offset) pairs and the
    sub-metrics (action-only, offset-only). Restricts gold to items
    where in_closed_set is True (the model cannot predict OOV items by
    construction).
    """
    gold_filtered = []
    for g in gold_items:
        if not g.get("in_closed_set"): continue
        if g.get("action") is None: continue
        # Build a gold (canonical_action, days_offset) tuple
        canon = normalize_action(g["action"])
        if canon not in ACTION_ONTOLOGY:
            continue
        period_text = g.get("period_text")
        days = time_text_to_days_offset(period_text) if period_text else None
        if days is None:
            # no scheduled time -> excluded from pair F1 but counted for action-only
            gold_filtered.append({"action": canon, "days_offset": None})
        else:
            gold_filtered.append({"action": canon, "days_offset": int(days)})
    return gold_filtered


def main() -> None:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    if device == "cpu":
        print("WARNING: no CUDA available; this will be slow.")

    print("Loading model...")
    model, tokenizer = load_model(device)

    gold = json.load(open(GOLD_PATH))
    print(f"Loaded {len(gold)} MTSamples notes from gold.")

    per_note = []
    agg_act_tp = agg_act_fp = agg_act_fn = 0
    agg_pair_tp = agg_pair_fp = agg_pair_fn = 0
    for i, note in enumerate(gold, 1):
        text = note["transcription"]
        gold_items = note["follow_up_items"]
        test_spans, time_spans = predict_spans(model, tokenizer, text, device)
        preds = build_predictions(test_spans, time_spans)
        gold_norm = evaluate_against_gold(preds, gold_items)

        # action-only F1 over canonical labels
        pred_acts = {p["action"] for p in preds}
        gold_acts = {g["action"] for g in gold_norm}
        a_tp = len(pred_acts & gold_acts)
        a_fp = len(pred_acts - gold_acts)
        a_fn = len(gold_acts - pred_acts)
        agg_act_tp += a_tp; agg_act_fp += a_fp; agg_act_fn += a_fn

        # pair F1 over (canonical, days_offset); skip gold items where days_offset is None
        pred_pairs = {(p["action"], p["days_offset"]) for p in preds}
        gold_pairs = {(g["action"], g["days_offset"]) for g in gold_norm if g["days_offset"] is not None}
        p_tp = len(pred_pairs & gold_pairs)
        p_fp = len(pred_pairs - gold_pairs)
        p_fn = len(gold_pairs - pred_pairs)
        agg_pair_tp += p_tp; agg_pair_fp += p_fp; agg_pair_fn += p_fn

        per_note.append({
            "note_id": note["note_id"],
            "sample_name": note["sample_name"],
            "n_test_spans": len(test_spans),
            "n_time_spans": len(time_spans),
            "predictions": preds,
            "gold_in_set": gold_norm,
            "action_tp": a_tp, "action_fp": a_fp, "action_fn": a_fn,
            "pair_tp": p_tp, "pair_fp": p_fp, "pair_fn": p_fn,
        })
        print(f"  [{i:2d}/{len(gold)}] {note['sample_name'][:30]:<30}  "
              f"TEST={len(test_spans):2d} TIME={len(time_spans):2d}  "
              f"preds={len(preds):2d}  goldA={len(gold_acts):2d} goldP={len(gold_pairs):2d}  "
              f"act_tp/fp/fn={a_tp}/{a_fp}/{a_fn}  pair_tp/fp/fn={p_tp}/{p_fp}/{p_fn}")

    def f1(tp, fp, fn):
        p = tp / (tp + fp) if (tp + fp) else 0
        r = tp / (tp + fn) if (tp + fn) else 0
        return p, r, (2*p*r/(p+r) if (p+r) else 0)

    a_p, a_r, a_f = f1(agg_act_tp, agg_act_fp, agg_act_fn)
    p_p, p_r, p_f = f1(agg_pair_tp, agg_pair_fp, agg_pair_fn)
    summary = {
        "n_notes": len(gold),
        "linker": "heuristic_nearest_neighbour",
        "link_radius_chars": LINK_RADIUS,
        "action_only_f1": {
            "tp": agg_act_tp, "fp": agg_act_fp, "fn": agg_act_fn,
            "precision": round(a_p, 4), "recall": round(a_r, 4), "f1": round(a_f, 4),
        },
        "test_time_pair_f1": {
            "tp": agg_pair_tp, "fp": agg_pair_fp, "fn": agg_pair_fn,
            "precision": round(p_p, 4), "recall": round(p_r, 4), "f1": round(p_f, 4),
        }
    }

    OUT_PRED.write_text(json.dumps(per_note, indent=2), encoding="utf-8")
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print()
    print(f"Wrote {OUT_PRED.relative_to(ROOT)}")
    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print()
    print("=== SUMMARY ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
