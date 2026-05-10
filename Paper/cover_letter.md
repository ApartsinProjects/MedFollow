# Cover Letter

**To:** Editor-in-Chief, *Journal of Biomedical Informatics*
**From:** Yehudit Aperstein (corresponding author), Afeka College of Engineering, Tel Aviv, Israel. Email: apersteiny@afeka.ac.il
**Date:** [insert at submission]
**Re:** Submission of *Reliable Follow-Up Action and Date Extraction from Clinical Notes: A Hybrid Neural-Symbolic Approach* as an Original Research article.

---

Dear Editor,

We are pleased to submit our manuscript *Reliable Follow-Up Action and Date Extraction from Clinical Notes: A Hybrid Neural-Symbolic Approach* for consideration as an Original Research article in the *Journal of Biomedical Informatics*. The work has not been published previously and is not under consideration at another journal.

**Why JBI.** The manuscript fits squarely within JBI's scope as a methodology paper that addresses a concrete clinical-informatics problem: extracting structured action-date pairs (e.g., "MRI brain in two weeks" → `{MRI Brain, 2026-01-24}`) from outpatient note text. Reliable extraction of these pairs is a prerequisite for downstream EHR scheduling, care-coordination audit, and structured-field validation, and the problem is acutely sensitive to the date-arithmetic failure modes that current end-to-end LLM extractors exhibit.

**Contribution.** We propose a hybrid neural-symbolic system that delegates calendar arithmetic to a deterministic temporal-expression normalizer while retaining a learned BioBERT encoder with joint BIO action/time tagging and biaffine action-time linking. On a 2,000-note synthetic outpatient corpus we release with the paper, the system reaches end-to-end action-date F1 of 0.980 (95% CI [0.964, 0.992]) and 0.53-day mean absolute date error, against 0.806-0.827 F1 and 5-11 day MAE for two reasonable generative baselines (zero-shot GPT-4o-mini and a LoRA-fine-tuned LLaMA-3 8B). The 95% confidence intervals on the headline metrics do not overlap. To the best of our knowledge this is the first explicit comparative evaluation of a decomposed-versus-end-to-end architecture for action-date extraction with a designed stress-factor corpus.

**Honest scope statement.** We want to be explicit about the principal limitation: the present evaluation is conducted on a controlled synthetic corpus that we constructed to enable exact-offset metrics and stress-factor coverage that would be impractical with real EHR notes. The paper does not claim real-world clinical-deployment readiness, and the Discussion (Section 5) and Limitations (Section 5.1) describe the next-version program that includes external evaluation on a clinician-annotated real-note sample and the full ablation set required before such claims could be made. We believe the current results justify publication on three grounds: (i) the controlled benchmark cleanly isolates the calendar-arithmetic failure mode of generative extraction and demonstrates that a neural-symbolic decomposition removes it; (ii) the proposed system, the corpus, and the analysis scripts are released openly so the community can extend the work; and (iii) the methodological argument (separate ambiguous-semantic interpretation from well-defined symbolic transformation, audit each independently) is generalizable beyond the specific benchmark.

**Compliance with the Guide for Authors.** We confirm the manuscript conforms to JBI's structural and editorial requirements:

- **Body shape:** Introduction / Related Work / Methods / Results / Discussion / Conclusion, with 4,734 body words (cap 6,000).
- **Abstract:** 295 words, structured as Objective / Methods / Results / Conclusion (cap 300).
- **Statement of Significance** with the four mandated sub-headings (Problem or Issue; What is Already Known; What this Paper Adds; Who would benefit) is included at the end of the Introduction.
- **Figures and tables:** 6 figures and 2 tables, total 8 (at the cap).
- **References** in Elsevier numbered Vancouver format with LTWA-abbreviated journal names and live `https://doi.org/` URLs.
- **Required declarations** (CRediT authorship contribution, Declaration of competing interest, Funding, Ethics, Data and code availability, Generative AI use disclosure, Acknowledgements) are all present after the Conclusion. Generative AI was used in drafting and copy-editing the manuscript and as the synthetic-data generator (OpenAI `gpt-4o-mini`); both uses are disclosed using Elsevier's mandated wording, with model name and version recorded in Methods.
- **Ethics:** The dataset is fully synthetic and contains no protected health information; no IRB approval is required.
- **Data and code availability:** the synthetic corpus, training and inference code, per-system metric files (including a consolidated `results_with_ci.json`), figure-generation scripts, and the rendered manuscript are publicly released at https://github.com/ApartsinProjects/MedFollow. A DOI-bearing Zenodo deposit will be created at acceptance.

**Suggested reviewers** (the editor may, of course, select differently):
- [Suggested reviewer 1, name + email + affiliation]
- [Suggested reviewer 2, name + email + affiliation]
- [Suggested reviewer 3, name + email + affiliation]

Plausible candidates given the topic span (clinical NLP, temporal extraction, span-pair relation modeling, LLM-based clinical extraction) include authors of cited works on cTAKES, the THYME / Clinical TempEval line of temporal extraction, BERT-based clinical models, and recent LLM clinical extraction benchmarks. We will provide concrete names in the Editorial Manager submission form.

**Conflicts of interest.** None to declare.

**Funding.** This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors. *(To be confirmed before submission.)*

We thank you in advance for considering this manuscript for *Journal of Biomedical Informatics*. We will be happy to address any questions you or the reviewers may have, and we welcome feedback that would strengthen the paper toward publication.

Sincerely,

Yehudit Aperstein, on behalf of the authors
Afeka College of Engineering, Tel Aviv, Israel
apersteiny@afeka.ac.il
