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
    # Synthetic corpus
    ("data/synthetic_clinical_notes_2000.csv",         ROOT / "Data" / "synthetic_clinical_notes_2000.csv"),

    # Per-system per-split metrics + consolidated canonical file
    ("results/biobert_seen_metrics.json",              ROOT / "newrepo" / "artifacts" / "metrics" / "biobert_seen_metrics.json"),
    ("results/biobert_oov_metrics.json",               ROOT / "newrepo" / "artifacts" / "metrics" / "biobert_oov_metrics.json"),
    ("results/llama_seen_metrics.json",                ROOT / "newrepo" / "artifacts" / "metrics" / "llama_seen_metrics.json"),
    ("results/llama_oov_metrics.json",                 ROOT / "newrepo" / "artifacts" / "metrics" / "llama_oov_metrics.json"),
    ("results/gpt_seen_metrics.json",                  ROOT / "newrepo" / "artifacts" / "metrics" / "gpt_seen_metrics.json"),
    ("results/gpt_oov_metrics.json",                   ROOT / "newrepo" / "artifacts" / "metrics" / "gpt_oov_metrics.json"),
    ("results/results_seen_oov_with_ci.json",          ROOT / "Results" / "results_seen_oov_with_ci.json"),

    # Analysis scripts that reproduce figures and tables in the manuscript
    ("scripts/consolidate_seen_oov_metrics.py",        ROOT / "Paper" / "scripts" / "consolidate_seen_oov_metrics.py"),
    ("scripts/make_seen_oov_figures.py",               ROOT / "Paper" / "scripts" / "make_seen_oov_figures.py"),
    ("scripts/make_round2_figures.py",                 ROOT / "Paper" / "scripts" / "make_round2_figures.py"),
    ("scripts/make_round4_figures.py",                 ROOT / "Paper" / "scripts" / "make_round4_figures.py"),
    ("scripts/make_vocab_distributions.py",            ROOT / "Paper" / "scripts" / "make_vocab_distributions.py"),

    # Editable vector source of the pipeline figure
    ("figures/pipeline.svg",                           ROOT / "Paper" / "figures" / "pipeline.svg"),

    # Supplementary figure: stress-factor coverage (moved out of body to free a figure slot)
    ("figures/stress_factor_coverage.png",             ROOT / "Paper" / "figures" / "stress_factor_coverage.png"),

    # MTSamples top-20 realism check (gold annotations + coverage report)
    ("realism_check/mtsamples_top20_gold.json",        ROOT / "Data" / "external" / "mtsamples" / "mtsamples_top20_gold.json"),
    ("realism_check/mtsamples_top20_coverage.md",      ROOT / "Data" / "external" / "mtsamples" / "mtsamples_top20_coverage.md"),
]

README = """# Supplementary Materials

Companion package for the manuscript:

> *Reliable Extraction of Clinical Follow-Up Instructions:
> A Hybrid Neural-Symbolic Pipeline.*
> M. Laufer, Y. Aperstein, A. Apartsin.
> Submitted to *Journal of Biomedical Informatics*.

Code repository: https://github.com/michallaufer/Clinical-Follow-up-Extraction

## Contents

### data/
- **synthetic_clinical_notes_2000.csv** -- The 2,000-note synthetic
  outpatient corpus described in Section 3.2. Each row contains
  `note_text`, `visit_date`, `specialty`, `topic`, `plan_variant`,
  `num_actions`, `actions_gt` (JSON list of gold spans with canonical
  TestSpecification labels, TimeSpecification phrases, normalized
  period_date, and character offsets), style-feature fields, and
  validation-flag fields. License: CC BY 4.0.

### results/
- **biobert_{seen,oov}_metrics.json**,
  **llama_{seen,oov}_metrics.json**,
  **gpt_{seen,oov}_metrics.json** -- Per-system, per-split metric
  files containing the point estimates and the note-level bootstrap
  distributions used to populate Table 2 of the manuscript.
- **results_seen_oov_with_ci.json** -- Consolidated canonical file
  with point estimates and 95% confidence intervals for all three
  systems on both the seen-test and OOV-test splits, plus
  methodology metadata. This is the strict-JSON file used to drive
  Table 2, Figure 4, and Figure 5.

### scripts/
- **consolidate_seen_oov_metrics.py** -- Builds the consolidated
  `results_seen_oov_with_ci.json` from the six per-system per-split
  metric files. Reproduces every number in Table 2.
- **make_seen_oov_figures.py** -- Regenerates Figure 4 (Seen vs OOV
  F1 comparison) and Figure 5 (Time-offset MAE by model and split)
  from the consolidated metrics file.
- **make_round2_figures.py** -- Regenerates Figure 2 (dataset
  composition) from the released CSV.
- **make_vocab_distributions.py** -- Regenerates Figure 3
  (vocabulary distributions) from the released CSV.
- **make_round4_figures.py** -- Regenerates the supplementary
  stress-factor-coverage figure from the released CSV.

### figures/
- **pipeline.svg** -- Editable vector source of Figure 1 (system
  overview). The DOCX manuscript embeds this same SVG.
- **stress_factor_coverage.png** -- Supplementary figure showing the
  per-stress-factor proportions in the corpus (moved out of the body
  to satisfy the journal's figure-count cap).

### realism_check/
- **mtsamples_top20_gold.json** -- Manual ground-truth annotations
  for the top 20 highest-scoring real transcribed outpatient notes
  from the MTSamples corpus (Apache-2.0). Each note carries a list
  of follow-up items with `action_verbatim`, `period_text`,
  `period_date`, character offsets, an `in_closed_set` flag, and a
  `coverage_note` tag. Cited in Section 5.1 of the manuscript.
- **mtsamples_top20_coverage.md** -- Per-category coverage breakdown
  showing the 40% closed-set coverage finding and a per-note table.

## Reproducibility

The scripts assume the directory layout in this zip; run them from
the zip root after extraction. The trained BioBERT joint checkpoint
and LLaMA-3 LoRA adapter used in evaluation are not redistributed
here owing to size; they are available from the corresponding
author on reasonable request. Re-running `consolidate_seen_oov_metrics.py`
followed by `make_seen_oov_figures.py` reproduces every number in
the manuscript Table 2 and Figures 4-5 from the released per-system
metric files alone.

## License

- Synthetic dataset (data/): CC BY 4.0.
- MTSamples top-20 annotations (realism_check/): Apache-2.0 (inherits
  from the MTSamples upstream).
- Code (scripts/): MIT.
- Pipeline figure (figures/pipeline.svg): CC BY 4.0.
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
