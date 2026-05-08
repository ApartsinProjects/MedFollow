# Publication Audit: Follow-Up Instruction Extraction

## Project Classification

Likely paper type: clinical NLP methods paper with a dataset/evaluation component.

The current repository implements a reliability-first extraction pipeline for outpatient follow-up instructions. The technical core is a joint BioBERT model that detects action and time spans, links actions to their corresponding times, and delegates calendar arithmetic to deterministic date normalization anchored on the visit date.

## Strongest Defensible Thesis

The strongest current thesis is not "LLMs solve clinical follow-up extraction." A more defensible thesis is:

> For structured follow-up instruction extraction from clinical notes, a hybrid architecture that separates semantic extraction from deterministic temporal normalization can outperform direct generative extraction on synthetic but stress-varied notes, especially for action-date correctness and date arithmetic reliability.

This thesis is promising, but it is not yet top-journal ready because the current evidence is synthetic-only and lacks external validation, uncertainty estimates, ablations, and a clean reproducibility package.

## Current Evidence Inventory

Repository artifacts:

- Dataset: `Data/synthetic_clinical_notes_2000.csv`
- Main notebook: `Code/llm_project_follow_up_instruction_extraction_2k_dataset_submit.ipynb`
- Requirements: `Code/requirements.txt`
- Metrics: `Results/biobert_metrics.json`, `Results/chatgpt_metrics.json`, `Results/llama_metrics.json`
- Figures: `Visuals/*.png`
- Presentations: `Slides/*.pptx`, `Slides/*.pdf`

Dataset summary:

- Total notes: 2,000
- Specialties: Orthopedic 379, Cardiovascular/Pulmonary 391, Gastroenterology 394, Neurology 414, General Medicine 422
- Action counts: 0 actions 497, 1 action 978, 2 actions 525
- Mean actions per note: 1.014
- Note length: 436 to 1,834 characters, median 1,193 characters
- API errors: 0
- Span errors recorded: 26

Reported held-out results:

| Model | Action F1 | Time/Date F1 | Action-Date F1 | Date Exact Accuracy | Date MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| BioBERT hybrid pipeline | 0.9949 | 0.9975 | 0.9797 | 0.9847 | 0.53 days |
| ChatGPT zero-shot | 0.9796 | 0.8308 | 0.8265 | 0.8438 | 5.07 days |
| LLaMA fine-tuned | 1.0000 | 0.8163 | 0.8061 | 0.8061 | 10.88 days |

## Claim-to-Evidence Map

| Candidate claim | Current support | Publication risk |
| --- | --- | --- |
| The task can be decomposed into action span detection, time span detection, action-time linking, and date normalization. | README and notebook architecture define this decomposition. | Low. This is a methods framing claim. |
| Hybrid extraction plus deterministic date normalization improves action-date reliability over direct generative JSON extraction. | Metrics show BioBERT action-date F1 0.9797 vs ChatGPT 0.8265 and LLaMA 0.8061 on the same synthetic split. | Medium. Needs protocol clarity, seeds, confidence intervals, exact baseline prompts/settings, and strict JSON metric reproducibility. |
| Deterministic normalization reduces date arithmetic errors. | Date MAE is much lower for BioBERT pipeline: 0.53 vs 5.07 and 10.88 days. | Medium-high. Needs ablation: learned extractor with and without deterministic normalizer, plus error categories. |
| The dataset covers multiple specialties and note styles. | Synthetic data includes 5 specialties, style features, plan variants, shorthand, distractors, and 0/1/2 action cases. | Medium. Needs a dataset card, generation protocol, validation against real-note style, and leakage controls. |
| The method is robust to real clinical notes. | Not supported by current repository. | Fatal if claimed. Needs de-identified institutional data, public benchmark adaptation, or expert-labeled shadow evaluation. |
| The system is deployable in care coordination workflows. | Not supported beyond prototype framing. | Fatal if claimed. Needs clinical validation, workflow integration, calibration, monitoring, and safety governance. |

## Highest-Risk Gaps

1. Synthetic-only evaluation.
   A top journal reviewer will likely treat current results as proof-of-concept unless there is external validation or a carefully designed realism study.

2. Missing reproducibility structure.
   The main notebook combines data generation, model training, LLM baselines, evaluation, and plotting. This is hard to audit and rerun.

3. Weak baseline documentation.
   The repository has metric files, but it does not yet preserve baseline prompts, generation parameters, model versions, train/test split IDs, or raw predictions.

4. No statistical uncertainty.
   Results are point estimates on one split. A serious paper needs seeds, bootstrap confidence intervals, or repeated splits.

5. No ablation study.
   The core scientific claim depends on the value of joint linking and deterministic date normalization, but the current repo does not isolate those contributions.

6. Metrics files are not fully publication-grade artifacts.
   Some result files appear to use Python literal formatting rather than strict JSON. This will complicate automated auditing.

7. Current paper identity is underspecified.
   The project can become a methods paper, dataset paper, or benchmark paper, but a top-tier submission needs one primary identity.

## Highest-Value Next Experiments

Minimum convincing experiment set:

1. Reproducible split manifest.
   Save train/validation/test note IDs and all random seeds.

2. Rule-normalization ablation.
   Compare span/link extraction with deterministic date normalization against at least one variant that asks a model to produce normalized dates directly.

3. Linking ablation.
   Compare the biaffine linker against nearest-time, same-sentence, and action-order baselines.

4. Synthetic stress slices.
   Report performance by specialty, note length, number of actions, shorthand time expressions, history distractors, proximity traps, and list-swapping traps.

5. External realism evaluation.
   Add one of:
   - A small de-identified clinician-labeled note set, if available.
   - A public clinical-note-derived temporal extraction benchmark adapted to action-date extraction.
   - A blinded clinician realism/annotation study over synthetic notes if real data cannot be used.

6. Uncertainty and error analysis.
   Add bootstrap 95% confidence intervals and a manually reviewed error taxonomy.

## Recommended Paper Framing

Working title:

> Reliable Extraction of Follow-Up Actions and Timelines from Clinical Notes via Joint Span-Link Modeling and Deterministic Date Normalization

Primary contribution:

1. A task formulation for extracting follow-up actions linked to executable dates from clinical notes.
2. A hybrid neural-symbolic architecture that separates span/link understanding from date arithmetic.
3. A synthetic stress-test corpus with controlled distractors, shorthand temporal expressions, and multi-action cases.
4. A comparative evaluation against direct generative extraction baselines.

Non-contributions to state explicitly:

- The work does not claim clinical deployment readiness.
- The work does not establish real-world generalization without further validation.
- The synthetic dataset is a controlled evaluation scaffold, not a substitute for prospective clinical data.

## Target Manuscript Package

Recommended repo additions:

- `Paper/manuscript.md` or `Paper/main.tex`
- `Paper/figures/`
- `Paper/tables/`
- `Paper/references.bib`
- `experiments/`
- `splits/`
- `predictions/`
- `results/metrics_strict_json/`
- `docs/dataset_card.md`
- `docs/model_card.md`

## Next Concrete Actions

1. Refactor the notebook into scripts:
   - data generation
   - split creation
   - model training
   - baseline inference
   - evaluation
   - figure/table generation

2. Normalize all result files to strict JSON and preserve raw model predictions.

3. Build `Paper/manuscript.md` with a skeleton: Introduction, Related Work, Task Definition, Dataset, Method, Experiments, Results, Error Analysis, Limitations, Ethics, Reproducibility.

4. Run the ablation/stress-slice plan before drafting strong claims.

5. Start literature positioning around clinical information extraction, temporal expression normalization, relation extraction, instruction-following LLM extraction, and synthetic clinical data evaluation.

## What the Repo Still Cannot Claim

The current repository cannot yet claim real-clinical-note robustness, clinical deployment readiness, superiority over all LLM approaches, or general temporal reasoning capability. It can claim a promising synthetic proof-of-concept showing that a decomposed hybrid pipeline substantially improves action-date extraction and date arithmetic reliability over the included direct generative baselines.
