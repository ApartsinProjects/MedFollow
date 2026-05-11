# MTSamples Top-20 Realism Check: Closed-Set Coverage Analysis

Manually annotated on 2025-01-15 reference date. Source: 
`Data/external/mtsamples/mtsamples_top20_gold.json`.

## Headline finding

Of 48 follow-up-style items identified across the 20 notes, only 19 (40%) map to one of the paper's 28 closed-set action types. The remaining items fall outside the synthetic-corpus ontology: medication changes, generic follow-up appointments without a specified procedure, conditional instructions ('if symptoms persist...'), patient self-care behaviors, specialist referrals outside the consult set, and vague or absent timing.

This is a direct empirical confirmation of the limitation declared in Section 5.1 of the manuscript: 'Medication changes, conditional follow-up ("return if symptoms worsen"), patient self-care behavior, and instructions with ambiguous executor are not yet represented.'

## Coverage breakdown by category

| Category | Count | Notes |
|---|---:|---|
| `in_set` | 12 | Maps cleanly to a closed-set action with an explicit time |
| `med_change` | 12 | Medication start / stop / titration |
| `generic_followup` | 8 | Generic follow-up appointment with no specific procedure |
| `no_time` | 6 | Closed-set action recommended but no scheduled time given ("may benefit from MRI") |
| `referral` | 4 | Referral to specialist outside the closed set |
| `vague` | 3 | Vague timing without a specific date phrase |
| `self_care` | 2 | Patient self-care or activity instruction |
| `conditional` | 1 | Closed-set action gated on a condition ("x-ray if symptoms persist") |

## Per-note summary

| # | Note | Items | In-set | Dominant gap |
|---:|---|---:|---:|---|
| 1 | Note 1: Leg Pain & Bone Pain (SOAP/Progress, score 20) | 4 | 2 | med_change |
| 2 | Note 2: Asperger Disorder (SOAP/Progress, score 20) | 5 | 0 | med_change |
| 3 | Note 3: CT Neck - 1 (Orthopedic, score 19) | 2 | 2 | (none, all in-set) |
| 4 | Note 4: Cartilage Loose Body Removal (Orthopedic, score 14) | 2 | 1 | self_care |
| 5 | Note 5: Cineangiography - 1 (Surgery, score 14) | 1 | 0 | vague |
| 6 | Note 6: Tailor Bunionectomy with Screw Fixation (Orthopedic, score 13) | 1 | 0 | vague |
| 7 | Note 7: Ortho - Letter - 1 (Orthopedic, score 13) | 3 | 2 | generic_followup |
| 8 | Note 8: Elbow Manipulation (Orthopedic, score 12) | 2 | 2 | (none, all in-set) |
| 9 | Note 9: Premature retina and vitreous (Office Notes, score 12) | 1 | 0 | generic_followup |
| 10 | Note 10: Delayed ORIF (Orthopedic, score 12) | 1 | 1 | (none, all in-set) |
| 11 | Note 11: Posttransplant Lymphoproliferative Disorder (SOAP, score 11) | 2 | 1 | med_change |
| 12 | Note 12: Pneumonia & COPD - Discharge Summary (Discharge, score 11) | 3 | 1 | med_change |
| 13 | Note 13: Hyperthyroidism Following Pregnancy (General Medicine, score 10) | 3 | 1 | med_change |
| 14 | Note 14: Angiography & Catheterization - 1 (Surgery, score 10) | 3 | 0 | med_change |
| 15 | Note 15: Kidney Transplant - Followup (Nephrology, score 10) | 4 | 1 | med_change |
| 16 | Note 16: Selective Coronary Angiography & Angioplasty (Cardiovascular, score 10) | 0 | 0 | (none, all in-set) |
| 17 | Note 17: Long-Arm Cast (Orthopedic, score 10) | 1 | 1 | (none, all in-set) |
| 18 | Note 18: Myoclonic Epilepsy (Office Notes, score 10) | 2 | 1 | med_change |
| 19 | Note 19: Gen Med Progress Note - 9 (SOAP, score 9) | 4 | 1 | med_change |
| 20 | Note 20: Gen Med Progress Note - 2 (SOAP, score 9) | 4 | 2 | med_change |

## Implications for the JBI submission

- **Coverage gap is real and large.** The paper's hypothesis that real EHR text contains types of follow-up not present in the synthetic ontology is borne out on the very first 5 notes. A clinician-annotated real-note evaluation in revision should report two metrics:
  1. *Closed-set recall* (over items the model could in principle predict).
  2. *Total recall* (counting OOV items as missed), which is the clinically relevant number.

- **Schema extension priorities** (in order of frequency in this 5-note sample):
  1. Generic follow-up appointment (no specific procedure linked) - most common.
  2. Medication change / titration - common in chronic-disease follow-up.
  3. Conditional follow-up ("if X then Y") - scoping rule needed in the linker.
  4. Self-care instructions with a date - may be in-scope for scheduling auditors.
  5. Specialist referrals outside the consult set (psychology, dermatology, etc.).

- **MTSamples is anonymized**: no visit_date is present in the headers. For a real eval we either need an MTSamples-derived corpus that injects synthetic visit dates, or a switch to MIMIC-IV-Note which records `charttime` per discharge summary.