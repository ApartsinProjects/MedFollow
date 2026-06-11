# Cover Letter

**To:** Editor-in-Chief, *Journal of Biomedical Informatics*
**From:** Yehudit Aperstein (corresponding author), Afeka College of Engineering, Tel Aviv, Israel. Email: apersteiny@afeka.ac.il
**Date:** [insert at submission]
**Re:** Submission of *Reliable Extraction of Clinical Follow-Up Instructions: A Hybrid Neural-Symbolic Pipeline* as an Original Research article.

---

Dear Editor,

We are pleased to submit our manuscript *Reliable Extraction of Clinical Follow-Up Instructions: A Hybrid Neural-Symbolic Pipeline* for consideration as an Original Research article in the *Journal of Biomedical Informatics*. The work has not been published previously and is not under consideration at any other journal.

**Why the problem matters.** Outpatient clinical notes routinely carry follow-up instructions (*"MRI brain in two weeks"*, *"RTC 3 mo"*, *"Holter in 6 weeks"*) that determine the next tests, referrals, and care-coordination steps. Failure to act on these instructions has been documented as a patient-safety issue in ambulatory care (Callen et al., 2012, *J. Gen. Intern. Med.*), with recommended actions sometimes going unaddressed across care transitions. Reliable extraction of structured (action, date) pairs from the free-text plan is therefore a prerequisite for downstream EHR scheduling, automated care-coordination audit, structured-field validation, and outpatient-quality measurement; the integrity of every downstream use is bounded by the integrity of the upstream extraction.

**Why the problem is difficult and remains unsolved.** The task is not standard named-entity recognition. A clinically useful extraction must simultaneously (i) recognise the action span (a procedure, test, consult, or referral), (ii) recognise the temporal expression that schedules it, (iii) *link* the correct time to the correct action when notes contain multiple actions and historical-context distractors, and (iv) *normalize* relative phrases (`3 mos`, `q6mo`, "within five weeks") to an absolute calendar date against the visit-date anchor. Each subtask is tractable in isolation; their composition is not. Recent end-to-end generative extractors illustrate the gap concretely: zero-shot GPT-4o-mini and a LoRA-fine-tuned LLaMA-3 8B both *name* the clinical action well (TestSpecification F1 0.93-0.99) but their full-pair reconstruction collapses to Pair F1 **0.51-0.57** because linking and calendar arithmetic are implicit in decoding and not exposed to inspection. Fine-tuning a generative model on the in-distribution training set does not close the gap, and the obvious post-hoc remediation, applying a deterministic normalizer to the LLM's output, also fails: feeding the LoRA model's emitted `period_text` through the rule grammar collapses Pair F1 from 0.564 to **0.000** on seen-test and from 0.562 to **0.000** on OOV-test (Section 4.2), because the fine-tuned model emits absolute ISO dates directly and never produces a parseable temporal phrase. The composition fails silently, that is, a wrong end-to-end date is unauditable without re-running the decoder, which is precisely the failure mode a safety-relevant clinical application cannot afford.

**Our approach and what it delivers.** We propose a hybrid neural-symbolic pipeline that explicitly decomposes the four subtasks and exposes each component for inspection. A shared BioBERT encoder feeds two task heads: a BIO tagger that recognises TestSpecification and TimeSpecification spans, and a biaffine relation extractor that links each action span to its time span (or to a learned "none" option). Entities are canonicalized through a closed 28-action ontology, and the linked time phrase is mapped to an integer day offset by a deterministic rule grammar; the neural model never performs calendar arithmetic. On a 2,000-note synthetic outpatient corpus with controlled stress-factor coverage and an action-disjoint OOV split, the pipeline reaches Test-Time Pair F1 of **0.997 [0.990, 1.000]** (seen-test, n=259) and **0.986 [0.972, 0.997]** (OOV-test, n=259) with **0.00-day mean absolute date error** in both splits; the 95% confidence intervals do not overlap with either generative baseline on either split. Any wrong end-to-end pair traces to a specific entity span, a specific link, or a specific normalization, so failure modes are inspectable rather than implicit. A first-pass realism check on forty transcribed MTSamples outpatient notes (Section 5.1) bounds external readiness honestly: 31% (28 of 91) of real follow-up items map to the synthetic ontology, and on the in-scope subset (15 evaluable items) the model scores Pair F1 = **0.118** (1 TP, 1 FP, 14 FN), cleanly separating a coverage gap (ontology design) from a textual-generalization gap (synthetic-only training) and motivating the concrete next-version program described in Section 5.1.

**Data, code, and reproducibility.** The synthetic corpus, training and inference code, per-system metric files, the per-note LLaMA prediction dumps used for the Table 3 quantitative error profile and the Section 4.2 ablation, the MTSamples top-40 gold annotations and per-item coverage breakdown referenced in Section 5.1, and the source files for every manuscript figure are publicly released under permissive licences at https://github.com/ApartsinProjects/MedFollow. The inference pipeline reproduces end-to-end from the released data and supplied checkpoints in approximately ten minutes on a single rented RTX 4090. A DOI-bearing Zenodo deposit including the fine-tuned BioBERT weights (~440 MB) and the LLaMA-3 LoRA adapter (~158 MB) will be created at acceptance and cited in the final version.

**Conflicts of interest.** None to declare.

**Funding.** This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

We thank you in advance for considering this manuscript. We will be happy to address any questions you or the reviewers may have, and we welcome feedback that would strengthen the paper toward publication.

Sincerely,

Yehudit Aperstein, on behalf of the authors
Afeka College of Engineering, Tel Aviv, Israel
apersteiny@afeka.ac.il
