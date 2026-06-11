# Cover Letter

**To:** Editor-in-Chief, *Journal of Biomedical Informatics*
**From:** Yehudit Aperstein (corresponding author), Afeka College of Engineering, Tel Aviv, Israel. Email: apersteiny@afeka.ac.il
**Date:** [insert at submission]
**Re:** Submission of *Reliable Extraction of Clinical Follow-Up Instructions: A Hybrid Neural-Symbolic Pipeline* as an Original Research article.

---

Dear Editor,

We are pleased to submit our manuscript *Reliable Extraction of Clinical Follow-Up Instructions: A Hybrid Neural-Symbolic Pipeline* for consideration as an Original Research article in the *Journal of Biomedical Informatics*. The work has not been published previously and is not under consideration at any other journal.

**Why JBI.** The manuscript sits squarely in JBI's scope as a methodology paper on a concrete clinical-informatics problem: extracting structured (action, date) pairs (e.g., *"MRI brain in two weeks" -> {MRI Brain, 2026-01-24}*) from outpatient note text. Reliable extraction of these pairs is a prerequisite for downstream EHR scheduling, care-coordination audit, and structured-field validation, and the problem is acutely sensitive to the date-arithmetic failure modes that current end-to-end LLM extractors exhibit. Failure to follow up on instructions of this kind has been documented as a patient-safety issue in ambulatory care (Callen et al., 2012, J. Gen. Intern. Med.).

**Core contribution.** We propose a hybrid neural-symbolic system that delegates calendar arithmetic to a deterministic temporal-expression normalizer while retaining a learned BioBERT encoder with a joint BIO action/time tagging head and a biaffine action-time linker. On a 2,000-note synthetic outpatient corpus we release with the paper, the system reaches Test-Time Pair F1 of **0.997 [0.990, 1.000]** on a 259-note seen-test split and **0.986 [0.972, 0.997]** on a 259-note action-disjoint OOV-test split, with **0.00-day mean absolute date error** in both splits. The two generative baselines (zero-shot GPT-4o-mini and LoRA-fine-tuned LLaMA-3 8B) reach high TestSpecification F1 (0.93-0.99) but their Pair F1 stays at **0.51-0.57** with day-to-month-scale arithmetic errors. The 95% confidence intervals on the headline metrics do not overlap between the hybrid pipeline and either baseline on either split. To the best of our knowledge this is the first explicit comparative evaluation of a decomposed-versus-end-to-end architecture for clinical action-date extraction with a designed stress-factor corpus and a strict set-level correctness criterion.

**Two findings worth flagging for reviewers.**

1. A **date-normalization ablation** (Section 4.2) addresses the natural alternative architecture: *can the symbolic normalizer be applied to a generative model's output as a drop-in date-arithmetic component?* Feeding the LoRA model's emitted `period_text` strings through the same rule grammar collapses Pair F1 from 0.564 to **0.000** on seen-test and from 0.562 to **0.000** on OOV-test, because the fine-tuned model emits absolute ISO dates directly and never produces a `period_text` intermediate the rule grammar can parse. This is a stronger statement than the original architectural argument: the symbolic normalizer is coupled to the structured BIO tagger output by design and is not a separable swappable component.

2. A **realism check on real transcribed notes** (Section 5.1) is the principal external-validity signal in the current version. Forty MTSamples transcribed outpatient notes were manually annotated against the closed 28-action ontology; **31% (28 of 91)** of identified follow-up items fell inside the ontology, with the remaining 69% in categories the synthetic corpus does not represent (medication titration 25%, generic specialist follow-up 21%, recurring schedules, conditional/self-care instructions). On the in-ontology subset (15 evaluable items), the hybrid pipeline scored Pair F1 = **0.118** (1 TP, 1 FP, 14 FN), an approximately eight-fold drop from the synthetic OOV-test split (0.986). The two findings together separate a coverage gap (ontology design) from a textual-generalization gap (synthetic-only training) and give an honest empirical bound on real-world readiness rather than a hand-waved limitations paragraph.

**Compliance with the Guide for Authors.** We confirm the manuscript conforms to JBI's structural and editorial requirements:

- **Body shape:** Introduction / Related Work / Methods / Results / Discussion / Conclusion, with **5,941 body words** (cap 6,000).
- **Abstract:** **191 words / 1,385 characters**, structured as Objective / Methods / Results / Conclusion (caps 300 / 1,500).
- **Statement of Significance** with the four mandated sub-headings (Problem or Issue; What is Already Known; What this Paper Adds; Who would benefit) is included at the end of the Introduction.
- **Figures and tables:** 5 figures and 3 tables, total **8 (at the cap)**. No vertical rules in tables; figures are embedded at the cited locations.
- **References:** 25 references in Elsevier numbered Vancouver format with LTWA-abbreviated journal names. Every entry was verified resolvable against Crossref / OpenAlex / arXiv (DOI present for journal articles; ACL Anthology or OpenReview link for conference papers without DOIs).
- **Required declarations** (CRediT authorship contribution, Declaration of competing interest, Funding, Ethics, Data and code availability, Generative AI use disclosure, Acknowledgements) are all present after the Conclusion. Generative AI was used in drafting and copy-editing the manuscript and as the synthetic-data generator (OpenAI `gpt-4o-mini`); both uses are disclosed using Elsevier's mandated wording, with model name and version recorded in the Methods section.
- **Ethics:** The dataset is fully synthetic and contains no protected health information; no IRB approval is required for the present experiments.

**Data, code, and reproducibility.** The synthetic corpus, training and inference code, per-system metric files, the per-note LLaMA prediction dumps used for the Table 3 quantitative error profile and the Section 4.2 ablation, the MTSamples top-40 gold annotations and per-item coverage breakdown referenced in Section 5.1, and the source files for every manuscript figure are publicly released under permissive licences at https://github.com/ApartsinProjects/MedFollow. The inference pipeline reproduces end-to-end from the released data and supplied checkpoints in approximately ten minutes on a single rented RTX 4090. A DOI-bearing Zenodo deposit including the fine-tuned BioBERT weights (~440 MB) and the LLaMA-3 LoRA adapter (~158 MB) will be created at acceptance and cited in the final version.

**Conflicts of interest.** None to declare.

**Funding.** This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

We thank you in advance for considering this manuscript. We will be happy to address any questions you or the reviewers may have, and we welcome feedback that would strengthen the paper toward publication.

Sincerely,

Yehudit Aperstein, on behalf of the authors
Afeka College of Engineering, Tel Aviv, Israel
apersteiny@afeka.ac.il
