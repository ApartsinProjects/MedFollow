# MTSamples Top-5 Realism Check: Closed-Set Coverage Analysis

Manually annotated on 2025-01-15 reference date. Source: 
`Data/external/mtsamples/mtsamples_top5_gold.json`.

## Headline finding

Of 14 follow-up-style items identified across the 5 notes, only 5 (36%) map to one of the paper's 28 closed-set action types. The remaining items fall outside the synthetic-corpus ontology: medication changes, generic follow-up appointments without a specified procedure, conditional instructions ('if symptoms persist...'), patient self-care behaviors, and vague timing.

This is a direct empirical confirmation of the limitation declared in Section 5.1 of the manuscript: 'Medication changes, conditional follow-up ("return if symptoms worsen"), patient self-care behavior, and instructions with ambiguous executor are not yet represented.'

## Coverage breakdown by category

| Category | Count | Notes |
|---|---:|---|
| `generic_followup` | 3 | Generic follow-up appointment with no specific procedure |
| `med_change` | 3 | Medication start / stop / titration |
| `in_set` | 2 | Maps cleanly to a closed-set action with an explicit time |
| `no_time` | 2 | Closed-set action recommended but no scheduled time given ("may benefit from MRI") |
| `conditional` | 1 | Closed-set action gated on a condition ("x-ray if symptoms persist") |
| `referral` | 1 | Referral to specialist outside the closed set |
| `self_care` | 1 | Patient self-care or activity instruction |
| `vague` | 1 | Vague timing without a specific date phrase |

## Per-note summary

| # | Note | Items | In-set | Dominant gap |
|---:|---|---:|---:|---|
| 1 | Note 1: Leg Pain & Bone Pain (SOAP/Progress, score 20) | 4 | 2 | med_change |
| 2 | Note 2: Asperger Disorder (SOAP/Progress, score 20) | 5 | 0 | generic_followup |
| 3 | Note 3: CT Neck - 1 (Orthopedic, score 19) | 2 | 2 | (none, all in-set) |
| 4 | Note 4: Cartilage Loose Body Removal (Orthopedic, score 14) | 2 | 1 | self_care |
| 5 | Note 5: Cineangiography - 1 (Surgery, score 14) | 1 | 0 | vague |

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