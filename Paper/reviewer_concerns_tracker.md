# JBI R1 — Reviewer Concern Tracker

Working document for the revision. One row per distinct concern, each with a
stable ID so the response letter, the manuscript changes, and the experiment
log can all reference the same identifier.

Status legend: `OPEN` (not started) / `WIP` (in progress) / `DONE` (change
landed in manuscript) / `PARTIAL` (addressed but not fully resolvable in this
round) / `REBUT` (we argue against making the change).

Source: [`reviewer_comments_r1.md`](reviewer_comments_r1.md)

---

## Editor-level consensus

| ID | Concern | Severity | Status |
|---|---|---|---|
| **ED-1** | Both reviewers agree the evaluation lacks rigor because it relies on synthetic data. This is the decision-driving concern. | **Critical** | OPEN |

---

## Reviewer 1

| ID | Concern | Severity | Status |
|---|---|---|---|
| **R1-1** | Near-perfect BioBERT performance (0.986 / 0.997 Pair F1) is "a red flag that undermines the results". Suspects the model is learning GPT-4o-mini's generation regularities, not the clinical phenomenon. Notes that real temporal/relation clinical extraction has human IAA far below these numbers. | **Critical** | OPEN |
| **R1-2** | Unexplained why fine-tuned LLaMA-3 is so far below BioBERT; reviewer's intuition is a fine-tuned LLaMA should be "reasonable". Implies the baseline may be under-optimized or mis-configured. | **Major** | OPEN |
| **R1-3** | Contribution is corpus + comparative analysis, not a new IE approach; and the corpus's value depends entirely on its realism, which the limited MTSamples comparison does not demonstrate. | **Major** | OPEN |
| **R1-4** | Real-world IE performance is needed to understand the relationship between synthetic-corpus performance and real-world performance. | **Critical** | OPEN |
| **R1-5** | The language of the synthetic corpus should be explicitly stated (i.e., English). | **Minor** | OPEN |
| **R1-6** | §3.3 architecture is very similar to preceding publications; where the architecture is drawn from existing work the relevant paper must be cited. Span representation specifically resembles existing BERT-based work. | **Major** | OPEN |

**Reviewer 1 positives to preserve:** §2 Related Work is well done and clearly differentiates the work; §2.7 correctly frames the corpus as controlled evaluation rather than deployment evidence; §3.5 evaluation metrics are appropriate.

---

## Reviewer 3

| ID | Concern | Severity | Status |
|---|---|---|---|
| **R3-1a** | LLM baselines are minimally optimized: no in-context examples, no tool use, no constrained decoding. The large gap may reflect unoptimized prompts / output schema / post-processing rather than an architectural truth. | **Critical** | OPEN |
| **R3-1b** | The claim that linking and arithmetic fail because they are "implicit in generation" is a hypothesis, not established: **no ablation isolates linking failures from arithmetic failures within the generative baselines**. | **Critical** | OPEN |
| **R3-2** | MTSamples is a realism check, not external validation; MTSamples also differs from operational EHR notes. No end-to-end performance on any independent real-text dataset. Claims about scheduling auditors / clinical reliability / generalizability must be stated more cautiously. | **Critical** | OPEN |
| **R3-3** | Methodological novelty is incremental. Must more clearly distinguish from prior work on (a) clinical recommendation extraction, (b) event-time linking, (c) joint entity-relation extraction, (d) temporal normalization. Requests stronger conventional baselines (rule-only pipeline; encoder-choice ablation) and additional ablations. | **Major** | OPEN |
| **R3-4** | Task excludes clinically important follow-up types (conditional follow-up, medication titration). ~60-69% of real items fall outside the closed set. This bears directly on clinical-applicability claims and must be **more prominent in the main text**, not only in Limitations, with a clearer account of how the ontology would be extended. | **Major** | OPEN |
| **R3-5** | Table 3 qualitative labels ("high", "moderate", "low", "rare") are uninterpretable without counts/denominators. Requests number and percentage per error type, broken down by model and by split. | **Major** | PARTIAL — the LLaMA-3 column was quantified in the current repo version (counts from 319 seen + 293 OOV predictions), but BioBERT and GPT-4o-mini columns remain qualitative. |
| **R3-m1** | Figure 2 has overlapping graphical elements; reformat for clarity. | **Minor** | DONE — legend moved below the plot in a single horizontal row (Figure 4 given the same treatment); both regenerated and embedded in the DOCX. |
| **R3-m2** | Avoid "trustworthy" / "reliable" in abstract and conclusion unless supported by real-world external validation. | **Minor** | OPEN — note the manuscript **title** itself begins "Reliable Extraction of..."; a title change may be warranted. |

---

## Cross-cutting themes (what actually has to change)

1. **Synthetic-only evaluation is the decision driver** (ED-1, R1-1, R1-3, R1-4, R3-2). No amount of prose hedging fixes this; it needs either real-text end-to-end numbers or a fundamentally reframed claim.
2. **Baseline fairness** (R1-2, R3-1a). The LLM comparison must be re-run with few-shot prompting, a constrained output schema, and ideally tool use, or the comparative claim must be withdrawn.
3. **Missing ablations** (R3-1b, R3-3). Specifically: isolate linking error from arithmetic error inside the generative baselines; add a rule-only baseline; add an encoder-choice ablation.
4. **Framing and language** (R3-2, R3-4, R3-m2). Move the coverage limitation into the main text; strip reliability language from title/abstract/conclusion.
5. **Attribution** (R1-6). Cite the specific prior work the span representation and architecture derive from.
6. **Small fixes** (R1-5, R3-m1, R3-5). Corpus language, figure overlap, Table 3 counts.

---

## Assets already in the repo that bear on these concerns

| Asset | Bears on |
|---|---|
| `Results/llama_pernote_seen.jsonl`, `Results/llama_pernote_oov.jsonl` (per-note LLaMA predictions, 319 + 293) | R3-5 (Table 3 counts), R3-1b (can separate link vs arithmetic error post hoc) |
| `Results/llama_date_norm_ablation.json` (§4.2 ablation) | R3-1b (partially — shows the normalizer cannot be retrofitted, but does not yet decompose link vs arithmetic error) |
| `Results/mtsamples_realism_summary.json`, `mtsamples_realism_predictions.json` | R1-4, R3-2 (currently the only real-text signal: Pair F1 = 0.118 on 15 in-scope items) |
| `Data/external/mtsamples/mtsamples_top40_gold.json`, `mtsamples_top40_coverage.md` | R3-4 (coverage breakdown that must move into the main text) |
| `Paper/figures/dataset_composition.png`, `seen_oov_f1_comparison.png` (regenerated) | R3-m1 (already fixed) |
