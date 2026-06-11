# Cover Letter

**To:** Editor-in-Chief, *Journal of Biomedical Informatics*
**From:** Yehudit Aperstein (corresponding author), Afeka College of Engineering, Tel Aviv, Israel. Email: apersteiny@afeka.ac.il
**Date:** [insert at submission]
**Re:** Submission of *Reliable Extraction of Clinical Follow-Up Instructions: A Hybrid Neural-Symbolic Pipeline* as an Original Research article.

---

Dear Editor,

We are pleased to submit our manuscript *Reliable Extraction of Clinical Follow-Up Instructions: A Hybrid Neural-Symbolic Pipeline* for consideration as an Original Research article in the *Journal of Biomedical Informatics*. The work has not been published previously and is not under consideration at any other journal.

**Why this fits JBI.** This is a methods paper on a concrete clinical-informatics problem: turning the free-text follow-up plans in outpatient notes (e.g., *"MRI brain in two weeks"*) into the structured (action, date) records that EHR systems, scheduling auditors, and care-coordination tools need downstream. It sits within JBI's focus on methodology that improves health-information systems, rather than within a general-purpose NLP venue.

**Why the problem matters.** When a clinician writes a follow-up instruction in a note, that instruction has to reach the scheduling system, the chart-audit pipeline, and the patient's care plan. Failure to act on follow-up instructions is a recognized patient-safety issue in ambulatory care, with recommended actions sometimes going unaddressed across care transitions. Reliable structured extraction of these instructions is the upstream foundation on which every downstream tool depends; if the extraction is unreliable, downstream automation cannot be trusted.

**Why the problem is difficult and remains unsolved.** Although it looks like a straightforward extraction task, getting it right means doing four things at once: identifying the clinical action being scheduled, identifying the timing phrase that schedules it, linking the right time to the right action when a note mentions several actions and historical events, and converting a relative phrase such as "in six weeks" into an actual calendar date. Recent large language models can name the clinical action almost perfectly, but they handle the linking and the date arithmetic poorly. Crucially, their mistakes are buried inside the model's free-text output, so a wrong date cannot easily be traced back to a specific failing step. Fine-tuning the generative model on examples drawn from the same setting does not close the gap. The obvious workaround of running a calendar-arithmetic helper on top of the language model's output does not work either, because the fine-tuned model writes absolute dates directly rather than the phrases the helper is designed to parse. The net effect is a system that often extracts the right action attached to the wrong date in ways the user cannot inspect, which is precisely the failure mode a safety-relevant clinical application cannot afford.

**Our approach and what it delivers.** We separate the task into a learning component and a calculation component. The learning component reads the note and identifies the clinical action, the timing phrase, and which timing phrase belongs to which action. The calculation component is a small deterministic rule-based piece that converts the identified timing phrase into an absolute calendar date using the visit date as the anchor; the learning component is never asked to do calendar arithmetic. Because each component has a single responsibility, an extraction error can be traced to a specific step: a missed span, a wrong link, or a wrong date conversion. On a controlled outpatient benchmark we built and release with the paper, the hybrid pipeline produces complete and correct (action, date) records nearly perfectly, while two reasonable generative baselines extract the action well but mis-recover the date in roughly half the cases. A first-pass check on real transcribed clinical notes gives an honest bound on external readiness: most real follow-up types fall outside our current action list, and even within the supported types the model trained on our synthetic notes has not yet fully generalized to real-text vocabulary. We treat both as upstream signals for the next-version program rather than as evidence of deployment readiness.

**Data, code, and reproducibility.** The synthetic corpus, training and inference code, per-system metric files, the per-note LLaMA prediction dumps used for the Table 3 quantitative error profile and the Section 4.2 ablation, the MTSamples top-40 gold annotations and per-item coverage breakdown referenced in Section 5.1, and the source files for every manuscript figure are publicly released under permissive licences at https://github.com/ApartsinProjects/MedFollow. The inference pipeline reproduces end-to-end from the released data and supplied checkpoints in approximately ten minutes on a single rented RTX 4090. A DOI-bearing Zenodo deposit including the fine-tuned BioBERT weights (~440 MB) and the LLaMA-3 LoRA adapter (~158 MB) will be created at acceptance and cited in the final version.

**Conflicts of interest.** None to declare.

**Funding.** This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

We thank you in advance for considering this manuscript. We will be happy to address any questions you or the reviewers may have, and we welcome feedback that would strengthen the paper toward publication.

Sincerely,

Yehudit Aperstein, on behalf of the authors
Afeka College of Engineering, Tel Aviv, Israel
apersteiny@afeka.ac.il
