# Real Clinical Notes for MedFollow Realism Evaluation

Survey of corpora suitable for assembling a small (~50-200) test set of real outpatient clinical notes to evaluate the MedFollow follow-up-instruction extraction model (BioBERT + biaffine + dateparser), previously trained and tested only on synthetic notes.

Target text characteristics: outpatient progress notes, visit notes, or hospital discharge summaries containing plausible follow-up text such as "MRI in 2 weeks", "RTC 3 mo", "schedule colonoscopy". Pure radiology or pathology reports are de-prioritized because they rarely include scheduling instructions.

---

## Tier 1: Publicly downloadable, no access barrier

### 1.1 MTSamples (mtsamples.com)

- **What it is:** A public collection of transcribed medical sample reports across ~40 specialties, intended originally as training material for medical transcriptionists.
- **Volume:** ~5,000 documents (the most-cited Kaggle/HF mirror has 4,999 rows). The site itself reports "5,043 medical transcription samples in 40 specialties."
- **Outpatient relevance:** Highly relevant. Has dedicated specialty sections including "Office Notes," "General Medicine," "Discharge Summary," "Consult - History and Phy.", "SOAP / Chart / Progress Notes." These commonly end with "Follow up in 2 weeks", "Return in 1 month", "Schedule colonoscopy", "RTC PRN" lines.
- **Expected follow-up density:** High in Office Notes, Discharge Summary, SOAP / Progress Notes. Estimate ~50-80% of office notes contain a future-dated follow-up instruction; ~70-90% of discharge summaries contain a "follow up with..." section.
- **License:** The most widely redistributed Kaggle/HF mirrors are tagged Apache-2.0 / CC0 / public-domain. The mtsamples.com site itself does not display an explicit machine-readable license; the standard practice in the literature has been to treat the texts as freely usable for research (the documents are not real PHI, they are training samples). The HuggingFace mirror `harishnair04/mtsamples` is published under Apache-2.0.
- **Are these REAL clinical notes?** Important caveat: MTSamples are sample/template reports prepared for transcription training. They are written by real clinicians in real clinical style and contain realistic phrasing, but they are not actual encounter records from real patients. For a "realism check" they are dramatically more realistic than purely templated synthetic data, but they are not authentic EHR.
- **Time-to-data:** Minutes. Available immediately via:
  - HuggingFace: https://hf.co/datasets/harishnair04/mtsamples (4,999 rows, Apache-2.0)
  - Kaggle: https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions
  - Source site: https://www.mtsamples.com/site/pages/browse.asp?Type=87-Office+Notes
- **Recommendation:** Yes, primary candidate for fast realism appendix. Filter to specialty in {Office Notes, General Medicine, SOAP / Chart / Progress Notes, Discharge Summary, Consult - History and Phy.}.

### 1.2 i2b2 / n2c2 challenge datasets (DBMI Harvard Portal)

- **What it is:** Annotated clinical-NLP shared-task corpora hosted at https://portal.dbmi.hms.harvard.edu/projects/n2c2-nlp/. "Freely available" but each user must register on the portal and sign a Data Use Agreement (DUA); it is not anonymous download.
- **Access steps:** Create DBMI Portal account; submit project description; sign DUA; await approval (typically days to a couple of weeks). PI/affiliation strongly preferred.
- **License:** Per-dataset DUA. Generally permits research and publication of derived results; redistribution prohibited.
- **Most relevant subsets for follow-up extraction:**
  - **2014 i2b2/UTHealth Track 2 (Heart Disease Risk Factors):** 1,304 longitudinal records from 296 diabetic patients spanning months/years. Real progress-note style, longitudinal. Contains follow-up phrasing routinely. Strong match.
  - **2008 Obesity Challenge:** 1,237 discharge summaries (obesity/diabetes patients). Discharge summaries contain follow-up sections.
  - **2010 Relations / Concepts:** Discharge summaries plus progress notes from Partners + Beth Israel + UPMC; follow-up instructions appear.
  - **2022 N2C2 Track 3 Progress Note Understanding (Assessment-and-Plan):** Daily progress notes with explicit Plan sections; very relevant for follow-up extraction.
- **Less relevant for follow-up:** 2006 Smoking, 2009 Medications (focused on drug attributes), 2011 Coreference, 2012 Temporal Relations (time-focused but the schema is different from MedFollow's action+time scheme so it is more useful as a comparison than as a drop-in test set).
- **Volume usable:** A few hundred to ~1,000 notes per challenge.
- **Time-to-data:** Days to a few weeks for DUA approval.
- **Recommendation:** Best mid-tier option. The 2014 longitudinal corpus and the 2022 Plan-section corpus are the strongest matches. Lower legal/access burden than MIMIC.

### 1.3 Open-i / Indiana University Chest X-ray Collection

- **What it is:** ~7,470 chest X-ray images and 3,955 paired radiology reports from Indiana University, exposed via the NLM Open-i image search.
- **License:** CC BY-NC-ND 4.0 (per multiple secondary sources; the Open-i FAQ also restricts use).
- **Outpatient/follow-up relevance:** Low. Reports are radiology reports with Comparison, Indication, Findings, Impression sections. The Impression section occasionally contains a recommendation ("recommend follow-up CT in 3 months"), but most reports do not. As you noted, pure radiology reports are not the target.
- **Time-to-data:** Minutes (direct download from openi.nlm.nih.gov or HF mirror `ykumards/open-i`).
- **Recommendation:** Skip for primary set. Could yield ~20-40 items as supplementary "radiology recommendation" examples if you want a separate sub-evaluation, but they will not exercise the typical MedFollow scheduling-instruction pattern.

### 1.4 Synthea (NOT real notes, but flagged for completeness)

- **What it is:** Synthetic patient records with synthetic notes generated from realistic clinical templates (https://synthetichealth.github.io/synthea/).
- **Status:** Synthetic. Does NOT meet the "real notes" requirement. The user already has synthetic data; Synthea would not provide an independent realism check.
- **Recommendation:** Skip.

### 1.5 MedNLI / MedQA / emrQA (too short or off-task)

- **MedNLI:** Single-sentence pairs from MIMIC for natural-language inference. Too short and too out-of-task for MedFollow.
- **MedQA:** USMLE-style multiple-choice questions. Not clinical notes.
- **emrQA:** QA pairs auto-generated over i2b2 notes. The underlying notes are i2b2; if you obtain i2b2 you already have the notes. emrQA itself does not add new note text.
- **Recommendation:** Skip all three for this purpose.

### 1.6 HuggingFace clinical-text datasets (search results)

The HF Hub does not appear to host any large, real, non-PhysioNet outpatient clinical-note dataset in the open. Searches for `clinical notes`, `discharge summary`, `outpatient progress note` returned essentially only mirrors of MTSamples (`harishnair04/mtsamples`, `bhargavi909/mt_Samples`, `NickyNicky/medical_mtsamples`, `metaboulie/MTSamples-openai-embedded`) and synthetic / Asclepius-style derivatives. Notable items:

  - `harishnair04/mtsamples`, best maintained MTSamples mirror, 4,999 rows, Apache-2.0.
  - `mitclinicalml/clinical-ie`, small CASI-derived snippet sets used in Agrawal et al. (2022) "Large Language Models are Few-Shot Clinical Information Extractors". Contains snippets, not full visit notes.
  - `AGBonnet/augmented-clinical-notes`, synthetic-augmented; not real.
  - `ykumards/open-i`, Indiana CXR mirror.

  No openly-redistributed large real outpatient EHR exists on HF: this matches the field's status quo (real EHR text is gated behind PhysioNet/i2b2 because of HIPAA).

### 1.7 ACI-Bench (ambient clinical conversations)

- **What it is:** 207 doctor-patient conversation transcripts paired with the doctor's clinical visit note, intended for ambient-AI scribing benchmarks. Created via professional medical scribes simulating realistic encounters.
- **Status:** Simulated/role-played but written by real clinicians/scribes in fully realistic visit-note format.
- **Outpatient/follow-up relevance:** Medium-to-high. Visit notes have Plan sections; many include follow-up scheduling text.
- **License:** Open (CC BY 4.0); code at https://github.com/wyim/aci-bench, paper at https://www.nature.com/articles/s41597-023-02487-3.
- **Volume usable:** ~200 visit notes.
- **Time-to-data:** Minutes.
- **Recommendation:** Strong supplemental source, especially because visit notes are much closer to outpatient progress notes than discharge summaries are. Worth treating as a parallel "tier-A" source alongside MTSamples.

---

## Tier 2: Credentialed access (PhysioNet), free but DUA + training

All PhysioNet datasets share a common access path:

  1. Create PhysioNet account (free).
  2. Complete CITI Program "Data or Specimens Only Research" course (~6-8 hours self-paced, free; affiliate as "Massachusetts Institute of Technology Affiliates" if not already CITI-affiliated). Upload completion report.
  3. Complete the Credentialing application on your PhysioNet profile (PI / supervisor / affiliation / project description).
  4. Sign the per-dataset DUA in the Files section of the project.
  5. Wait for review (typically 24-72 hours after all three steps complete; can take up to ~2 weeks if the application is incomplete or needs follow-up).

**Common license:** PhysioNet Credentialed Health Data License 1.5.0:
  - Research and education only; **commercial use disallowed**.
  - No re-identification attempts; no sharing access with anyone else; no redistribution.
  - Publication of aggregate / derived results is permitted; code associated with publications must be released to a public repo.

### 2.1 MIMIC-IV-Note v2.2, strongest single source

- **Link:** https://physionet.org/content/mimic-iv-note/2.2/
- **Volume:** **331,794 deidentified discharge summaries** from 145,915 patients at Beth Israel Deaconess Medical Center (Boston), plus 2,321,355 radiology reports.
- **Outpatient/follow-up relevance:** Very high for the discharge-summary table. Discharge summaries include a structured "Discharge Instructions" section with patient-facing instructions, AND a separate "Followup Instructions" section that explicitly lists follow-up appointments, e.g.:
  - "Follow-up with Dr. ___ in 2 weeks"
  - "Cardiology follow-up appointment in 4-6 weeks"
  - "Repeat CBC in 1 week"
- **Expected follow-up density:** Effectively 100% of discharge summaries contain a Followup Instructions section by design. Multiple instructions per note are common (median 2-4).
- **De-identification:** HIPAA Safe Harbor; PHI replaced with `___` placeholders. Dates are date-shifted (year is jittered, but intervals between events are preserved), so MedFollow's relative-time extraction will still work; absolute dates obviously will not.
- **Cohort caveat:** Discharge summaries, not outpatient progress notes. They are a strong proxy because the Followup Instructions section is exactly the kind of free text MedFollow targets. If the user explicitly wants outpatient visit notes, MIMIC alone will not satisfy that, but the Followup Instructions text style is essentially identical to what an outpatient progress note Plan section contains.
- **Time-to-data:** ~3-7 days end to end if doing CITI training from scratch (training is the bottleneck); 24-48 hr if already credentialed.
- **Commercial / publication:** Publication of derived results is permitted and standard; commercial use disallowed.
- **Recommendation:** Primary source for the peer-review-quality realism evaluation. Sample ~200 discharge summaries, extract the "Discharge Instructions" + "Followup Instructions" sections, and annotate.

### 2.2 MIMIC-III v1.4 (Notes table)

- **Link:** https://physionet.org/content/mimiciii/1.4/
- **Volume:** ~2 million notes across multiple categories (NOTEEVENTS table). Categories include "Discharge summary", "Physician", "Nursing", "Echo", "Radiology". Discharge summaries are again the most relevant.
- **Status:** Older but still widely used; the discharge summaries are very similar to MIMIC-IV-Note. Same access model (CITI + DUA).
- **Recommendation:** Use only if MIMIC-IV-Note is unavailable, or if you specifically want comparability with prior work that used MIMIC-III. Otherwise prefer MIMIC-IV-Note.

### 2.3 MIMIC-CXR reports

- **Link:** https://physionet.org/content/mimic-cxr/2.0.0/
- **Volume:** ~377k chest-X-ray reports.
- **Relevance:** Low for MedFollow. Radiology reports rarely contain scheduled follow-up. Skip.

### 2.4 eICU Collaborative Research Database

- **Link:** https://physionet.org/content/eicu-crd/2.0/
- **Volume:** ICU stays from 200+ US hospitals. The text-note content is sparse compared to MIMIC.
- **Relevance:** Low. ICU notes; outpatient follow-up rare.
- **Recommendation:** Skip.

### 2.5 MIMIC-IV-Ext-BHC (Hospital Course Summarization)

- **Link:** https://physionet.org/content/labelled-notes-hospital-course/1.2.0/
- **Relevance:** Pre-extracted "Brief Hospital Course" sections from MIMIC-IV-Note. Not specifically follow-up text, but useful as a starting point if you want to limit raw download size. Same DUA path.

---

## Tier 3: Patient-facing / forum corpora (fallback only)

### 3.1 r/AskDocs (MedRedQA)

- **What it is:** ~51,000 cleaned patient-question / verified-clinician-response pairs from the r/AskDocs subreddit. Built into the **MedRedQA** corpus (Nguyen et al., IJCNLP 2023) and the related **MedRedFlag** subset (1,100+ items focused on misconception redirection).
- **Source code:** https://github.com/ju-resplande/askD; paper https://aclanthology.org/2023.ijcnlp-main.42.pdf
- **Outpatient/follow-up relevance:** Mixed. Some clinician responses include phrasing like "you should follow up with your PCP in 2 weeks", but these are advice-to-the-public, not EHR-style instructions. Vocabulary, abbreviations, and structure differ significantly from real progress-note Plan sections.
- **Status:** REAL clinician text but NOT EHR. MedFollow's BioBERT + biaffine + dateparser pipeline was tuned for EHR-style abbreviations ("RTC 3 mo", "f/u 2 wks") that do not appear naturally on Reddit.
- **License:** Reddit data is governed by Reddit's API terms (recently restrictive); MedRedQA itself is a research-use academic corpus.
- **Time-to-data:** Same-day for the academic corpus.
- **Recommendation:** Fallback only. Useful if Tier 1 + Tier 2 cannot be obtained, or as a separate "out-of-distribution: patient forum" auxiliary evaluation in the paper.

### 3.2 PMC Open Access case reports

- **What it is:** Subset of PubMed Central full-text articles, including case reports (https://pmc.ncbi.nlm.nih.gov/tools/openftlist/). Subset has CC-BY / CC0 licenses for the commercial-use grouping.
- **Relevance:** Low. Case reports describe patient courses but are written for publication, not as EHR notes. They occasionally state "the patient was discharged with follow-up scheduled in 6 weeks" but vocabulary and density differ from real EHR.
- **Recommendation:** Possibly useful as a tertiary external-validity source, but not recommended as primary.

---

## Annotation protocol (recommended)

Mirror the existing MedFollow synthetic schema so the realism evaluation is metric-comparable.

### Schema

Per follow-up mention in a note, capture:

| Field | Type | Description |
|------|------|-------------|
| `action_span` | char span | Surface text of the clinical action (e.g., "MRI brain", "RTC", "schedule colonoscopy", "labs"). |
| `time_span` | char span | Surface text of the time expression (e.g., "in 2 weeks", "3 mo", "next Tuesday"). May be NULL if action is mentioned without timing. |
| `period_date_norm` | normalized | Output of dateparser (or your existing normalizer) on `time_span`. ISO-8601 if absolute, ISO-8601 duration (`P14D`, `P3M`) if relative. |
| `is_future_scheduled` | bool | Yes if it is a future scheduled item (the MedFollow target). No for retrospective references ("MRI 2 weeks ago showed..."), conditional ("if symptoms recur, MRI"), patient-history mentions. |
| `link_action_to_time` | binary edge | Biaffine link between the action and time spans. |

Also capture a per-note coarse label: `has_any_followup` (bool) for an easy precision/recall sanity check.

### Tooling recommendation

Use **Label Studio** (open source, https://labelstud.io/). Reasons:

  - Best-supported NER + relation annotation in a modern UI; configurable via XML labeling spec.
  - Free, self-hostable via `pip install label-studio` (no Docker required, runs on Windows/PowerShell).
  - Can import a CSV/JSONL of notes; exports JSON-MIN that includes character-offset spans and labeled relations; trivial to convert to BIO/CoNLL or to MedFollow's existing format.
  - Active learning + model-in-the-loop available out of the box if a second annotation pass is needed.

Alternatives:

  - **doccano**, simpler UI; relation annotation supported in recent versions; lighter setup. Pick this if Label Studio's config XML is too heavy for a 50-200-note job.
  - **brat**, classic in clinical NLP and historically the i2b2/n2c2 default. Annotation files (.ann sidecars) are easy to diff. Trade-off: requires Python 2 / Apache + has a dated UI; not ideal for Windows.

For 50-200 notes by a single annotator, **Label Studio** or **doccano** will both work; pick whichever the annotator is comfortable with. If you anticipate publishing the annotated corpus alongside the paper, brat .ann format remains the most portable for reviewers.

### Inter-annotator agreement

For a JBI submission's realism appendix, ideally have a second annotator label a 20% subsample and report Cohen's kappa or token-level F1 between annotators. Both Label Studio and doccano support multiple annotators per item natively.

---

## Three-tier action plan

### Tier A, fastest path to ~50 real-style notes (1-2 days)

For an appendix labelled "Realism check on non-synthetic clinical text".

1. Download MTSamples mirror today: `pip install datasets; datasets.load_dataset("harishnair04/mtsamples")` (Apache-2.0). 4,999 rows.
2. Filter to specialty in {"Office Notes", "General Medicine", "SOAP / Chart / Progress Notes", "Discharge Summary", "Consult - History and Phy."}. Expected ~600-900 surviving notes.
3. Sample 50 stratified by specialty.
4. Optionally add 10-20 ACI-Bench visit notes (https://github.com/wyim/aci-bench, CC BY 4.0) for genuine visit-note style.
5. Annotate with Label Studio using schema above (~4-8 hours of annotation time at ~5-10 min/note).
6. In the paper, characterize honestly: "MTSamples are clinician-written sample reports rather than authentic EHR; they constitute a stylistic realism check that complements but does not replace true EHR evaluation."

**Expected deliverable:** A 50-note appendix table with per-note action/time-span counts and MedFollow extraction F1, run as-is (zero-shot from the synthetic-trained model).

### Tier B, peer-review-quality ~200 real-EHR sample (2-4 weeks)

For a section in the main paper titled e.g. "Evaluation on real EHR discharge instructions".

1. Today: create PhysioNet account. Begin CITI "Data or Specimens Only Research" course (allow 1-2 evenings).
2. Days 2-3: complete CITI; upload completion certificate to PhysioNet.
3. Days 3-5: submit Credentialing application (PI, affiliation, project description: "Evaluate a follow-up-instruction extraction model on de-identified discharge summaries"). Await approval (typically 24-72 hr after all materials are in).
4. Days 5-10: sign the MIMIC-IV-Note v2.2 DUA; download via wget (~3 GB compressed).
5. Days 7-14: programmatically extract the "Discharge Instructions" + "Followup Instructions" sections from 200 randomly sampled discharge summaries (sampling stratified by service). Both section headers are reliably present and easy to regex.
6. Annotate 200 in Label Studio over ~2-4 days (annotator time ~15-30 hours total at ~5-9 min/note for these short sections).
7. Hold out a 20% inter-annotator subsample if a second annotator is available.
8. Report MedFollow zero-shot F1 (action span, time span, link, normalized date) on this set, plus density statistics.

**Critical license note for the JBI submission:** MIMIC-IV-Note's DUA permits publication of derived results and aggregate examples but **forbids inclusion of verbatim notes in the paper**. Use only paraphrased or synthetic-but-MIMIC-style examples in figures; cite individual notes by `note_id` only. This is the standard approach in JBI papers using MIMIC.

**Expected deliverable:** A primary results table comparing MedFollow performance on synthetic vs real EHR text, suitable for peer review.

### Tier C, institutional partnership for true outpatient notes (3-12 months)

For a follow-up paper or for generalization claims to outpatient settings (which neither MTSamples nor MIMIC discharge summaries fully support).

1. Identify a clinical NLP / informatics group at a partner institution (typical candidates: Mayo Clinic NLP group, Stanford CIBO, UCSF DSI, Vanderbilt DBMI, Pittsburgh DBMI, Columbia DBMI, NYU CAI). Many have public collaboration intake forms.
2. Draft a collaboration proposal: scope (50-500 outpatient progress notes; PCP / specialty clinic; de-identified), data flow (analysis on their servers, models exported, no raw text leaves), IRB plan.
3. Their IRB / privacy review: typically 2-6 months for a non-interventional reuse-of-existing-EHR-text project. Often expedited if no PHI export is requested.
4. Execute Data Use Agreement between institutions.
5. Run MedFollow inside their environment (Docker container or notebook). Annotation by their clinical team or by you with VPN access.
6. Author a joint paper or include the partner as co-authors.

**Estimated timeline:** 3-12 months. **Cost:** zero-to-modest (some institutions charge nominal data-prep fees). **Outcome:** the only path to real outpatient (not discharge) notes for follow-up extraction. Worth pursuing in parallel with Tier B but not blocking the JBI submission.

---

## Summary recommendation

For the current JBI submission, do **Tier A immediately** (MTSamples + ACI-Bench) for a quick realism appendix, and **start Tier B today in parallel** (PhysioNet credentialing has a multi-day-to-week latency but minimal effort). Tier C is a future-work item.

If only one tier is feasible, do Tier B: MIMIC-IV-Note discharge summaries with their explicit "Followup Instructions" section are the single best match for MedFollow's task and are the most defensible source for a peer-review claim about real-EHR generalization.

---

## References (URLs only)

- MTSamples site: https://www.mtsamples.com/
- MTSamples on HuggingFace: https://hf.co/datasets/harishnair04/mtsamples
- MTSamples on Kaggle: https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions
- n2c2 / i2b2 portal: https://portal.dbmi.hms.harvard.edu/projects/n2c2-nlp/
- n2c2 2014 challenge: https://portal.dbmi.hms.harvard.edu/projects/n2c2-2014/
- Open-i: https://openi.nlm.nih.gov/
- PhysioNet credentialing: https://physionet.org/about/citi-course/ and https://physionet.org/news/post/395/
- PhysioNet Credentialed Health Data License 1.5.0: https://physionet.org/about/licenses/physionet-credentialed-health-data-license-150/
- MIMIC-IV-Note v2.2: https://physionet.org/content/mimic-iv-note/2.2/
- MIMIC-III v1.4: https://physionet.org/content/mimiciii/1.4/
- MIMIC-CXR: https://physionet.org/content/mimic-cxr/2.0.0/
- eICU: https://physionet.org/content/eicu-crd/2.0/
- ACI-Bench paper: https://www.nature.com/articles/s41597-023-02487-3
- ACI-Bench code: https://github.com/wyim/aci-bench
- MedRedQA / r/AskDocs corpus: https://aclanthology.org/2023.ijcnlp-main.42.pdf and https://github.com/ju-resplande/askD
- Label Studio: https://labelstud.io/
- doccano: https://github.com/doccano/doccano
- brat: https://brat.nlplab.org/
