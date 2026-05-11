# MedFollow

**Reliable Follow-Up Action and Date Extraction from Clinical Notes: A Hybrid Neural-Symbolic Approach**

Michal Laufer<sup>a</sup>, Yehudit Aperstein<sup>b,*</sup>, Alexander Apartsin<sup>c</sup>

<sup>a</sup>Bar-Ilan University, Ramat Gan, Israel  
<sup>b</sup>Afeka College of Engineering, Tel Aviv, Israel  
<sup>c</sup>Holon Institute of Technology, Holon, Israel  
<sup>*</sup>Corresponding author: [apersteiny@afeka.ac.il](mailto:apersteiny@afeka.ac.il)

> Submitted to *Journal of Biomedical Informatics* (Elsevier).

| Read | Download |
|---|---|
| [Manuscript (HTML)](https://apartsinprojects.github.io/MedFollow/Paper/) | [Manuscript (.docx)](Paper/MedFollow_JBI_submission.docx) |
| [JBI submission notes](Paper/jbi_submission_notes.md) | [Supplementary materials (.zip)](Paper/MedFollow_supplementary.zip) |
| [Cover letter](Paper/cover_letter.md) | [Audit report](Paper/audit_report.md) |

---

## What this is

A hybrid neural-symbolic system that extracts structured `(action, date)` pairs from outpatient clinical notes. A shared BioBERT encoder feeds a BIO action/time tagging head and a biaffine action-time linker; a deterministic `dateparser`-based normalizer converts the linked time phrase into an absolute ISO date anchored on the visit date. By design, the neural model is never asked to perform calendar arithmetic.

```text
Input note + visit_date
        |
        v
  BioBERT encoder (sliding windows, 512/128)
        |
        v
  Head A: BIO action/time spans     -->     Head B: biaffine action-time linker (with NONE option)
                                                            |
                                                            v
                                              Deterministic date normalizer
                                                            |
                                                            v
                                              {action, period_text, period_date}
```

## Headline result

On a 2,000-note synthetic outpatient corpus (198-note held-out split, 196 gold actions):

| Model | Action F1 [95% CI] | Time F1 [95% CI] | Action-Date F1 [95% CI] | Date MAE (days) |
|---|---|---|---|---|
| **BioBERT hybrid (proposed)** | **0.995 [0.987, 1.000]** | **0.997 [0.992, 1.000]** | **0.980 [0.964, 0.992]** | **0.53** |
| ChatGPT zero-shot (gpt-4o-mini) | 0.980 [0.964, 0.992] | 0.831 [0.790, 0.868] | 0.827 [0.783, 0.864] | 5.07 |
| LLaMA-3 8B fine-tuned (LoRA) | 1.000 [1.000, 1.000] | 0.816 [0.772, 0.854] | 0.806 [0.762, 0.847] | 10.88 |

The hybrid pipeline's CIs for time F1, action-date F1, and date accuracy do not overlap with either generative baseline (significant at p<0.05). The largest gap is on calendar arithmetic (0.53 vs 5-11 days MAE), supporting the design hypothesis that semantic extraction and date arithmetic should be separated. See Section 4 of the manuscript for the full results table and Section 5 for discussion.

## Repository layout

```
MedFollow/
|-- Paper/
|   |-- index.html                           rendered manuscript (KaTeX math, GitHub Pages source)
|   |-- MedFollow_JBI_submission.docx        camera-ready Word version (JBI single-column)
|   |-- MedFollow_supplementary.zip          supplementary materials bundle
|   |-- cover_letter.md                      cover letter to JBI Editor
|   |-- jbi_submission_notes.md              JBI Guide-for-Authors compliance notes
|   |-- anticipated_reviewer_concerns.md     internal prep doc (10 likely concerns + responses)
|   |-- audit_report.md                      automated DOCX audit (24 PASS / 0 ISSUES)
|   |-- references.bib                       BibTeX
|   |-- figures/                             6 manuscript figures (1 SVG, 5 PNG)
|   |-- scripts/                             every script that produces a figure or metric
|   `-- templates/cnf-word-template.docx     Elsevier generic single-column Word template
|-- Code/
|   |-- llm_project_..._submit.ipynb         training, baseline inference, evaluation notebook
|   `-- requirements.txt
|-- Data/
|   |-- synthetic_clinical_notes_2000.csv    the released synthetic corpus
|   `-- external/mtsamples/                  MTSamples (Apache-2.0) for realism-check work
|-- Results/
|   |-- biobert_metrics.json                 per-system aggregated metrics
|   |-- chatgpt_metrics.json
|   |-- llama_metrics.json
|   `-- results_with_ci.json                 consolidated point estimates + 95% CIs
|-- Visuals/                                 earlier figures (kept for provenance)
|-- models/
|   `-- MODELS.md                            external-checkpoint manifest
|-- Slides/                                  course presentations (first / interim / final)
|-- index.html                               redirect to Paper/
`-- README.md                                this file
```

## Reproducing the metrics from the released artifacts

Without the trained model checkpoints (which live on Google Drive, see `models/MODELS.md`), you can already:

1. **Reproduce every confidence interval in the paper** from the released metric files:
   ```bash
   python Paper/scripts/compute_confidence_intervals.py
   ```
   Wilson score intervals on proportion metrics; 10,000-replicate instance-level bootstrap on F1 metrics with seed 42.

2. **Regenerate every figure** from the released CSV and metric files:
   ```bash
   python Paper/scripts/make_round2_figures.py        # Figure 2 (composition)
   python Paper/scripts/make_vocab_distributions.py   # Figure 3 (vocab)
   python Paper/scripts/make_round4_figures.py        # Figure 4 (stress factors)
   ```
   Figures 5 and 6 are produced by the same `compute_confidence_intervals.py` script.

3. **Audit the manuscript DOCX** against JBI requirements:
   ```bash
   python Paper/scripts/audit_docx.py
   ```

## Running training and inference end-to-end

Currently a single notebook (`Code/llm_project_..._submit.ipynb`) covering data generation, BioBERT training, baseline inference, and evaluation. Restoring this to a runnable state requires:

- The fine-tuned BioBERT checkpoint (`biobert_finetuned_2k.pth`, ~440 MB) and tokenizer dir,
- The LLaMA-3 LoRA adapter (`Llama3_Clinical_Action_Extraction_LoRA/`, ~150 MB),
- An OpenAI API key for the ChatGPT baseline (`gpt-4o-mini`).

See [`models/MODELS.md`](models/MODELS.md) for download instructions.

Refactoring the notebook into discrete entry-point scripts (`generate_data.py`, `train_biobert.py`, `run_baselines.py`, `evaluate.py`, `make_figures.py`) and persisting raw per-note predictions are the highest-priority reproducibility improvements; both are in progress.

## Real-EHR realism work (in progress)

For the planned external-validation appendix, we have downloaded the MTSamples corpus (4,999 transcribed clinical notes, Apache-2.0) and ranked it for follow-up-instruction richness. The top-100 candidate notes for manual annotation are at [`Data/external/mtsamples/mtsamples_top100_followup.csv`](Data/external/mtsamples/mtsamples_top100_followup.csv); a first pass annotation of the top 20 (mapping verbatim follow-up text to the paper's 28-action closed set) is at [`Data/external/mtsamples/mtsamples_top20_gold.json`](Data/external/mtsamples/mtsamples_top20_gold.json), with a coverage analysis at [`Data/external/mtsamples/mtsamples_top20_coverage.md`](Data/external/mtsamples/mtsamples_top20_coverage.md). Initial finding: closed-set coverage on the top 20 real notes is 40% (19/48 follow-up items map to the closed set), confirming the limitation declared in Section 5.1 of the manuscript that the synthetic ontology underrepresents medication changes, generic follow-up appointments, specialist referrals outside the consult set, and patient self-care behavior.

A larger-scale Tier-B evaluation on MIMIC-IV-Note discharge summaries is planned subject to PhysioNet credentialing; see [`Paper/real_ehr_sources.md`](Paper/real_ehr_sources.md) for the three-tier roadmap.

## Ethics and data

The released corpus is fully synthetic and contains no protected health information; no IRB approval is required for the present experiments. MTSamples is a publicly redistributed (Apache-2.0) collection of transcribed clinician sample notes; it is not real EHR documentation. Any extension to identifiable clinical data will require institutional governance, a data-use agreement, and IRB approval.

## License

- Synthetic dataset (`Data/synthetic_clinical_notes_2000.csv`): CC BY 4.0.
- Code: MIT (see `LICENSE`).
- Manuscript text and figures: CC BY 4.0.

## Citation

```bibtex
@article{medfollow_2026,
  author  = {Michal Laufer and Yehudit Aperstein and Alexander Apartsin},
  title   = {Reliable Follow-Up Action and Date Extraction from Clinical Notes: A Hybrid Neural-Symbolic Approach},
  journal = {Journal of Biomedical Informatics},
  year    = {2026},
  note    = {Submitted}
}
```
