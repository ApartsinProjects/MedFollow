"""Assemble the JBI supplementary-materials package as a single zip
suitable for upload at submission time.

Per Elsevier Guide for Authors: "Submit all supplementary materials at
the same time as your manuscript ... These files will not be checked,
formatted or typeset."

Contents:
  README_supplementary.md  -- describes every file in the bundle
  data/synthetic_clinical_notes_2000.csv  -- the released corpus
  results/biobert_metrics.json
  results/chatgpt_metrics.json
  results/llama_metrics.json
  results/results_with_ci.json  -- consolidated point estimates + CIs
  scripts/compute_confidence_intervals.py
  scripts/make_round2_figures.py
  scripts/make_round4_figures.py
  scripts/make_vocab_distributions.py
  figures/pipeline.svg  -- editable vector source of Figure 1

Output:
  Paper/MedFollow_supplementary.zip
"""
from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Paper" / "MedFollow_supplementary.zip"

FILES = [
    # (zip path, source path)
    ("data/synthetic_clinical_notes_2000.csv", ROOT / "Data" / "synthetic_clinical_notes_2000.csv"),
    ("results/biobert_metrics.json",            ROOT / "Results" / "biobert_metrics.json"),
    ("results/chatgpt_metrics.json",            ROOT / "Results" / "chatgpt_metrics.json"),
    ("results/llama_metrics.json",              ROOT / "Results" / "llama_metrics.json"),
    ("results/results_with_ci.json",            ROOT / "Results" / "results_with_ci.json"),
    ("scripts/compute_confidence_intervals.py", ROOT / "Paper" / "scripts" / "compute_confidence_intervals.py"),
    ("scripts/make_round2_figures.py",          ROOT / "Paper" / "scripts" / "make_round2_figures.py"),
    ("scripts/make_round4_figures.py",          ROOT / "Paper" / "scripts" / "make_round4_figures.py"),
    ("scripts/make_vocab_distributions.py",     ROOT / "Paper" / "scripts" / "make_vocab_distributions.py"),
    ("figures/pipeline.svg",                    ROOT / "Paper" / "figures" / "pipeline.svg"),
]

README = """# MedFollow Supplementary Materials

Companion package for the manuscript:

> *Reliable Follow-Up Action and Date Extraction from Clinical Notes:
> A Hybrid Neural-Symbolic Approach.*
> M. Laufer, Y. Aperstein, A. Apartsin.
> Submitted to *Journal of Biomedical Informatics*.

Public repository: https://github.com/ApartsinProjects/MedFollow

## Contents

### data/
- **synthetic_clinical_notes_2000.csv** -- The 2,000-note synthetic
  outpatient corpus described in Section 3.2. Each row contains
  `note_text`, `visit_date`, `specialty`, `topic`, `plan_variant`,
  `num_actions`, `actions_gt` (JSON list of gold action/time spans
  with normalized dates), `style_features` (JSON list of the ten
  style-feature axes), and validation-flag fields. License: CC BY 4.0.

### results/
- **biobert_metrics.json**, **chatgpt_metrics.json**,
  **llama_metrics.json** -- Per-system aggregated held-out metrics
  (precision, recall, F1, exact date accuracy, MAE) on the 198-note
  test split.
- **results_with_ci.json** -- Consolidated point estimates and 95%
  confidence intervals for all three systems and all five metrics,
  plus reconstructed (TP, FP, FN) counts and CI methodology metadata.
  This is the strict-JSON file used to populate Table 2 and Section 4.

### scripts/
- **compute_confidence_intervals.py** -- Reproduces every CI in the
  manuscript from the per-system metric files. Wilson score intervals
  on proportion metrics; 10,000-replicate instance-level bootstrap on
  F1 metrics with random seed 42. Run with Python 3.11+; depends on
  numpy and matplotlib.
- **make_round2_figures.py** -- Regenerates Figure 2 (dataset
  composition) from the released CSV.
- **make_vocab_distributions.py** -- Regenerates Figure 3
  (vocabulary distributions) from the released CSV.
- **make_round4_figures.py** -- Regenerates Figure 4 (stress-factor
  coverage) from the released CSV.

Figures 5 and 6 (model comparison with CIs; date error) are produced
by the same `compute_confidence_intervals.py` script.

### figures/
- **pipeline.svg** -- Editable vector source of Figure 1 (system
  overview). The DOCX manuscript embeds this same SVG; reviewers who
  prefer a rasterized version can render it via Inkscape, librsvg,
  or any SVG viewer.

## Reproducibility notes

- All scripts assume the repository layout (`scripts/` referencing
  `data/`, `results/`, `figures/` siblings); they are intended to be
  run after extracting the zip with the directory structure preserved.
- The training notebook used to produce the per-system metrics is
  available in the public repository at
  `Code/llm_project_follow_up_instruction_extraction_2k_dataset_submit.ipynb`.
- Trained model checkpoints (BioBERT fine-tuned weights, LLaMA-3
  LoRA adapter) are not included in this zip; see `models/MODELS.md`
  in the public repository for download instructions.

## License

- Synthetic dataset: CC BY 4.0.
- Code (scripts): MIT.
- Figures (SVG source): CC BY 4.0.
"""


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    # Verify all source files exist
    missing = [src for _, src in FILES if not src.exists()]
    if missing:
        print("ERROR: missing source files:")
        for m in missing:
            print(f"  - {m}")
        return

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        # Write README first
        z.writestr("README_supplementary.md", README)
        # Write each file
        for zip_path, src in FILES:
            z.write(src, arcname=zip_path)

    size = OUT.stat().st_size
    print(f"Wrote {OUT.relative_to(ROOT)} ({size:,} bytes, {size / 1024 / 1024:.2f} MB)")
    with zipfile.ZipFile(OUT) as z:
        print(f"\nContents ({len(z.namelist())} files):")
        for n in sorted(z.namelist()):
            info = z.getinfo(n)
            print(f"  {info.file_size:>9,}  {n}")


if __name__ == "__main__":
    main()
