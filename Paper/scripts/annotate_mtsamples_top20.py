"""Manually annotate the top 20 MTSamples notes for follow-up items,
aligned with the paper's 28-action closed-set taxonomy and the
synthetic-corpus schema (action / period_text / period_date / char
offsets).

This is the realism-check sample. Goal: reveal how well the paper's
action ontology covers real outpatient follow-up text, and produce
gold annotations in the same JSON shape as the synthetic corpus so
the same eval scripts can run on this set.

Output:
  Data/external/mtsamples/mtsamples_top20_gold.json
    - Per-note: note_id, specialty, sample_name, transcription,
      visit_date_assumed, follow_up_items (list with action,
      period_text, period_date, char offsets, in_closed_set flag,
      coverage_note).
  Data/external/mtsamples/mtsamples_top20_coverage.md
    - Markdown report on closed-set coverage gaps.

Approach:
  - The paper's closed set has 28 action types (CT Scan, X-Ray, MRI,
    MRI Brain, Cardiac MRI, Echocardiogram, Holter Monitor, Sleep
    Study, Abdominal Ultrasound, Blood Test, Lipid Panel, Urinalysis,
    Stool Antigen Test, Breath Test, EMG, EEG, Stress Test, Pulmonary
    Function Test, Endoscopy, Colonoscopy, Joint Injection,
    Vaccination, Cardiology / Neurology / GI / Orthopedic Consult,
    Physical Therapy, Annual Physical).
  - For each annotated item we record both the canonical closed-set
    label (when applicable) and the verbatim string that appears in
    the note. We mark coverage gaps explicitly: medication change,
    generic follow-up appointment, conditional instruction, patient
    self-care, vague-no-time, and recommendation-no-schedule.
  - Visit date is not in MTSamples (notes are anonymized templates).
    We use a reference date of 2025-01-15 throughout so dateparser
    can produce comparable normalized dates; the in-set evaluation
    of date arithmetic on real notes will need a real EHR visit-date
    column anyway.

Run:
    /c/Python314/python Paper/scripts/annotate_mtsamples_top5.py
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import dateparser
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "Data" / "external" / "mtsamples" / "mtsamples_top100_followup.csv"
OUT_JSON = ROOT / "Data" / "external" / "mtsamples" / "mtsamples_top20_gold.json"
OUT_MD = ROOT / "Data" / "external" / "mtsamples" / "mtsamples_top20_coverage.md"

REFERENCE_VISIT_DATE = "2025-01-15"  # placeholder anchor (MTSamples notes are anonymized)


@dataclass
class GoldItem:
    action_canonical: str | None      # one of 28 closed-set labels, or None if OOV
    action_verbatim: str               # exact substring in note
    period_text: str                   # exact substring in note
    period_date: str | None            # ISO from dateparser(period_text, RELATIVE_BASE=visit_date)
    in_closed_set: bool
    coverage_note: str                 # "in_set" | "med_change" | "generic_followup" | "conditional" | "self_care" | "no_time" | "vague" | "referral"


def find_offsets(text: str, needle: str) -> tuple[int, int]:
    """Return (start, end) char offsets of the first exact occurrence."""
    i = text.find(needle)
    if i < 0:
        raise ValueError(f"Not found in text: {needle!r}")
    return i, i + len(needle)


def normalize_date(period_text: str, visit_date: str) -> str | None:
    base = dateparser.parse(visit_date)
    if base is None:
        return None
    d = dateparser.parse(period_text, settings={"RELATIVE_BASE": base, "PREFER_DATES_FROM": "future"})
    return d.strftime("%Y-%m-%d") if d else None


# -------------------------------------------------------------------
# Manual annotations (one block per note). The list contains EVERY
# follow-up-style item I identified, including the OOV ones, so the
# coverage report is honest about what closed-set evaluation misses.
# -------------------------------------------------------------------
MANUAL = {
    "Note 1: Leg Pain & Bone Pain (SOAP/Progress, score 20)": {
        "items": [
            {
                "action_canonical": "Annual Physical",
                "action_verbatim": "diabetic checkup",
                "period_text": "in one month",
                "in_closed_set": True,
                "coverage_note": "in_set",  # diabetic checkup loosely maps to Annual Physical
            },
            {
                "action_canonical": "X-Ray",
                "action_verbatim": "x-ray of back, hip, and legs",
                "period_text": "at that time",
                "in_closed_set": True,
                "coverage_note": "conditional",  # "if symptoms are not gone"
            },
            {
                "action_canonical": None,
                "action_verbatim": "follow up",
                "period_text": "in one month",
                "in_closed_set": False,
                "coverage_note": "generic_followup",
            },
            {
                "action_canonical": None,
                "action_verbatim": "Crestor",
                "period_text": "in one month",
                "in_closed_set": False,
                "coverage_note": "med_change",  # conditional med substitution
            },
        ],
    },

    "Note 2: Asperger Disorder (SOAP/Progress, score 20)": {
        "items": [
            {
                "action_canonical": None,
                "action_verbatim": "Decrease Abilify from 7.5 mg to 5 mg",
                "period_text": None,   # immediate, no scheduled future time
                "in_closed_set": False,
                "coverage_note": "med_change",
            },
            {
                "action_canonical": None,
                "action_verbatim": "Luvox 25 mg tablet one-half",
                "period_text": "in one week",
                "in_closed_set": False,
                "coverage_note": "med_change",  # conditional titration
            },
            {
                "action_canonical": None,
                "action_verbatim": "Parents will call me",
                "period_text": "in two weeks",
                "in_closed_set": False,
                "coverage_note": "generic_followup",
            },
            {
                "action_canonical": None,
                "action_verbatim": "medication review",
                "period_text": "in four weeks",
                "in_closed_set": False,
                "coverage_note": "generic_followup",
            },
            {
                "action_canonical": None,
                "action_verbatim": "referral to psychologists",
                "period_text": None,
                "in_closed_set": False,
                "coverage_note": "referral",
            },
        ],
    },

    "Note 3: CT Neck - 1 (Orthopedic, score 19)": {
        "items": [
            {
                "action_canonical": "MRI",
                "action_verbatim": "MRI examination",
                "period_text": None,                      # no scheduled time
                "in_closed_set": True,
                "coverage_note": "no_time",               # "would be of benefit"
            },
            {
                "action_canonical": "MRI",
                "action_verbatim": "MRI",
                "period_text": None,
                "in_closed_set": True,
                "coverage_note": "no_time",               # "may be of benefit"
            },
        ],
    },

    "Note 4: Cartilage Loose Body Removal (Orthopedic, score 14)": {
        "items": [
            {
                "action_canonical": "Orthopedic Consult",
                "action_verbatim": "follow up",
                "period_text": "in 10 days",
                "in_closed_set": True,
                "coverage_note": "in_set",   # post-op ortho followup
            },
            {
                "action_canonical": None,
                "action_verbatim": "may wet the wound",
                "period_text": "in 5 days",
                "in_closed_set": False,
                "coverage_note": "self_care",
            },
        ],
    },

    "Note 5: Cineangiography - 1 (Surgery, score 14)": {
        "items": [
            {
                "action_canonical": None,
                "action_verbatim": "close followup as an outpatient",
                "period_text": None,
                "in_closed_set": False,
                "coverage_note": "vague",
            },
        ],
    },

    "Note 6: Tailor Bunionectomy with Screw Fixation (Orthopedic, score 13)": {
        "items": [
            {
                "action_canonical": None,
                "action_verbatim": "follow up with Dr. A",
                "period_text": None,
                "in_closed_set": False,
                "coverage_note": "vague",
            },
        ],
    },

    "Note 7: Ortho - Letter - 1 (Orthopedic, score 13)": {
        "items": [
            {
                "action_canonical": "EMG",
                "action_verbatim": "EMG study",
                "period_text": "in two week's time",
                "in_closed_set": True,
                "coverage_note": "in_set",
            },
            {
                "action_canonical": "Joint Injection",
                "action_verbatim": "trigger point injections",
                "period_text": "in two weeks' time",
                "in_closed_set": True,
                "coverage_note": "in_set",
            },
            {
                "action_canonical": None,
                "action_verbatim": "following him",
                "period_text": "in two weeks' time",
                "in_closed_set": False,
                "coverage_note": "generic_followup",
            },
        ],
    },

    "Note 8: Elbow Manipulation (Orthopedic, score 12)": {
        "items": [
            {
                "action_canonical": "Physical Therapy",
                "action_verbatim": "physical therapy and Dynasplint",
                "period_text": "in 3 days",
                "in_closed_set": True,
                "coverage_note": "in_set",
            },
            {
                "action_canonical": "Orthopedic Consult",
                "action_verbatim": "follow up",
                "period_text": "in 1 week's time",
                "in_closed_set": True,
                "coverage_note": "in_set",
            },
        ],
    },

    "Note 9: Premature retina and vitreous (Office Notes, score 12)": {
        "items": [
            {
                "action_canonical": None,
                "action_verbatim": "Recheck",
                "period_text": "in two weeks",
                "in_closed_set": False,
                "coverage_note": "generic_followup",
            },
        ],
    },

    "Note 10: Delayed ORIF (Orthopedic, score 12)": {
        "items": [
            {
                "action_canonical": "Orthopedic Consult",
                "action_verbatim": "follow up",
                "period_text": "in 2 days",
                "in_closed_set": True,
                "coverage_note": "in_set",
            },
        ],
    },

    "Note 11: Posttransplant Lymphoproliferative Disorder (SOAP, score 11)": {
        "items": [
            {
                "action_canonical": "Blood Test",
                "action_verbatim": "CBC, CMP, and LDH",
                "period_text": None,
                "in_closed_set": True,
                "coverage_note": "no_time",
            },
            {
                "action_canonical": None,
                "action_verbatim": "prednisone",
                "period_text": None,
                "in_closed_set": False,
                "coverage_note": "med_change",
            },
        ],
    },

    "Note 12: Pneumonia & COPD - Discharge Summary (Discharge, score 11)": {
        "items": [
            {
                "action_canonical": None,
                "action_verbatim": "Clindamycin 300 mg p.o. q.i.d.",
                "period_text": "x2 weeks",
                "in_closed_set": False,
                "coverage_note": "med_change",
            },
            {
                "action_canonical": "X-Ray",
                "action_verbatim": "chest x-ray PA and lateral",
                "period_text": "after 2 weeks of treatment",
                "in_closed_set": True,
                "coverage_note": "in_set",
            },
            {
                "action_canonical": None,
                "action_verbatim": "speech therapy evaluation",
                "period_text": None,
                "in_closed_set": False,
                "coverage_note": "referral",
            },
        ],
    },

    "Note 13: Hyperthyroidism Following Pregnancy (General Medicine, score 10)": {
        "items": [
            {
                "action_canonical": "Blood Test",
                "action_verbatim": "thyroid function tests",
                "period_text": "in six weeks",
                "in_closed_set": True,
                "coverage_note": "in_set",
            },
            {
                "action_canonical": None,
                "action_verbatim": "follow up",
                "period_text": "in 6 weeks",
                "in_closed_set": False,
                "coverage_note": "referral",
            },
            {
                "action_canonical": None,
                "action_verbatim": "citalopram 10 mg",
                "period_text": None,
                "in_closed_set": False,
                "coverage_note": "med_change",
            },
        ],
    },

    "Note 14: Angiography & Catheterization - 1 (Surgery, score 10)": {
        "items": [
            {
                "action_canonical": None,
                "action_verbatim": "aspirin lifelong",
                "period_text": None,
                "in_closed_set": False,
                "coverage_note": "med_change",
            },
            {
                "action_canonical": None,
                "action_verbatim": "Plavix for at least 12 months",
                "period_text": None,
                "in_closed_set": False,
                "coverage_note": "med_change",
            },
            {
                "action_canonical": None,
                "action_verbatim": "smoking cessation",
                "period_text": None,
                "in_closed_set": False,
                "coverage_note": "self_care",
            },
        ],
    },

    "Note 15: Kidney Transplant - Followup (Nephrology, score 10)": {
        "items": [
            {
                "action_canonical": "Urinalysis",
                "action_verbatim": "send urine for decoy cells",
                "period_text": "on his next visit",
                "in_closed_set": True,
                "coverage_note": "vague",
            },
            {
                "action_canonical": None,
                "action_verbatim": "see transplant",
                "period_text": "in two weeks",
                "in_closed_set": False,
                "coverage_note": "referral",
            },
            {
                "action_canonical": None,
                "action_verbatim": "and me",
                "period_text": "in four weeks",
                "in_closed_set": False,
                "coverage_note": "generic_followup",
            },
            {
                "action_canonical": None,
                "action_verbatim": "fish oil b.i.d.",
                "period_text": None,
                "in_closed_set": False,
                "coverage_note": "med_change",
            },
        ],
    },

    "Note 16: Selective Coronary Angiography & Angioplasty (Cardiovascular, score 10)": {
        "items": [],   # Tail and full text show only procedural narrative; no scheduled follow-up actions identified
    },

    "Note 17: Long-Arm Cast (Orthopedic, score 10)": {
        "items": [
            {
                "action_canonical": "Orthopedic Consult",
                "action_verbatim": "She will return",
                "period_text": "in 3 weeks",
                "in_closed_set": True,
                "coverage_note": "in_set",
            },
        ],
    },

    "Note 18: Myoclonic Epilepsy (Office Notes, score 10)": {
        "items": [
            {
                "action_canonical": None,
                "action_verbatim": "Keppra 500 mg b.i.d.",
                "period_text": None,
                "in_closed_set": False,
                "coverage_note": "med_change",
            },
            {
                "action_canonical": "Neurology Consult",
                "action_verbatim": "see in followup",
                "period_text": "in three months",
                "in_closed_set": True,
                "coverage_note": "in_set",
            },
        ],
    },

    "Note 19: Gen Med Progress Note - 9 (SOAP, score 9)": {
        "items": [
            {
                "action_canonical": "Blood Test",
                "action_verbatim": "CBC and a metabolic panel",
                "period_text": "in the morning",
                "in_closed_set": True,
                "coverage_note": "in_set",
            },
            {
                "action_canonical": None,
                "action_verbatim": "venous Doppler of the left leg",
                "period_text": None,
                "in_closed_set": False,
                "coverage_note": "no_time",
            },
            {
                "action_canonical": None,
                "action_verbatim": "Detrol 0.4 mg one daily",
                "period_text": None,
                "in_closed_set": False,
                "coverage_note": "med_change",
            },
            {
                "action_canonical": None,
                "action_verbatim": "see her back",
                "period_text": "in two weeks",
                "in_closed_set": False,
                "coverage_note": "generic_followup",
            },
        ],
    },

    "Note 20: Gen Med Progress Note - 2 (SOAP, score 9)": {
        "items": [
            {
                "action_canonical": "Blood Test",
                "action_verbatim": "BMP, lipid, liver profile, CPK, and CBC",
                "period_text": None,
                "in_closed_set": True,
                "coverage_note": "no_time",
            },
            {
                "action_canonical": "Lipid Panel",
                "action_verbatim": "lipid",
                "period_text": None,
                "in_closed_set": True,
                "coverage_note": "no_time",
            },
            {
                "action_canonical": None,
                "action_verbatim": "Increase his Altace to 5 mg day",
                "period_text": None,
                "in_closed_set": False,
                "coverage_note": "med_change",
            },
            {
                "action_canonical": None,
                "action_verbatim": "see him back",
                "period_text": "in three months",
                "in_closed_set": False,
                "coverage_note": "generic_followup",
            },
        ],
    },
}


def main() -> None:
    df = pd.read_csv(SRC).head(len(MANUAL)).reset_index(drop=True)

    out: list[dict] = []
    coverage_counts: dict[str, int] = {}
    in_set_count = 0
    total_items = 0

    for i, key in enumerate(MANUAL.keys()):
        row = df.iloc[i]
        text = str(row["transcription"])
        items: list[dict] = []
        for raw in MANUAL[key]["items"]:
            total_items += 1
            coverage_counts[raw["coverage_note"]] = coverage_counts.get(raw["coverage_note"], 0) + 1
            if raw["in_closed_set"]:
                in_set_count += 1

            try:
                a_s, a_e = find_offsets(text, raw["action_verbatim"])
            except ValueError as e:
                print(f"WARN [{key}]: {e}")
                a_s, a_e = -1, -1

            if raw["period_text"]:
                try:
                    t_s, t_e = find_offsets(text, raw["period_text"])
                except ValueError as e:
                    print(f"WARN [{key}]: {e}")
                    t_s, t_e = -1, -1
                pdate = normalize_date(raw["period_text"], REFERENCE_VISIT_DATE)
            else:
                t_s, t_e = -1, -1
                pdate = None

            items.append({
                "action": raw["action_canonical"],
                "action_verbatim": raw["action_verbatim"],
                "period_text": raw["period_text"],
                "period_date": pdate,
                "action_char_start": a_s,
                "action_char_end": a_e,
                "time_char_start": t_s,
                "time_char_end": t_e,
                "in_closed_set": raw["in_closed_set"],
                "coverage_note": raw["coverage_note"],
            })

        out.append({
            "note_id": int(row["note_id"]),
            "specialty": str(row["medical_specialty"]).strip(),
            "sample_name": str(row["sample_name"]).strip(),
            "visit_date_assumed": REFERENCE_VISIT_DATE,
            "transcription": text,
            "follow_up_items": items,
        })

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)} ({len(out)} notes, {total_items} items)")

    # ---------- Coverage Markdown report ----------
    md = []
    md.append(f"# MTSamples Top-{len(MANUAL)} Realism Check: Closed-Set Coverage Analysis")
    md.append("")
    md.append(f"Manually annotated on {REFERENCE_VISIT_DATE} reference date. Source: ")
    md.append(f"`Data/external/mtsamples/mtsamples_top{len(MANUAL)}_gold.json`.")
    md.append("")
    md.append("## Headline finding")
    md.append("")
    md.append(f"Of {total_items} follow-up-style items identified across the {len(MANUAL)} notes, "
              f"only {in_set_count} ({100 * in_set_count / total_items:.0f}%) "
              "map to one of the paper's 28 closed-set action types. The remaining items "
              "fall outside the synthetic-corpus ontology: medication changes, generic "
              "follow-up appointments without a specified procedure, conditional "
              "instructions ('if symptoms persist...'), patient self-care behaviors, "
              "specialist referrals outside the consult set, and vague or absent timing.")
    md.append("")
    md.append("This is a direct empirical confirmation of the limitation declared in "
              "Section 5.1 of the manuscript: 'Medication changes, conditional follow-up "
              "(\"return if symptoms worsen\"), patient self-care behavior, and instructions "
              "with ambiguous executor are not yet represented.'")
    md.append("")
    md.append("## Coverage breakdown by category")
    md.append("")
    md.append("| Category | Count | Notes |")
    md.append("|---|---:|---|")
    descriptions = {
        "in_set": "Maps cleanly to a closed-set action with an explicit time",
        "no_time": "Closed-set action recommended but no scheduled time given (\"may benefit from MRI\")",
        "conditional": "Closed-set action gated on a condition (\"x-ray if symptoms persist\")",
        "generic_followup": "Generic follow-up appointment with no specific procedure",
        "med_change": "Medication start / stop / titration",
        "self_care": "Patient self-care or activity instruction",
        "vague": "Vague timing without a specific date phrase",
        "referral": "Referral to specialist outside the closed set",
    }
    for cat, n in sorted(coverage_counts.items(), key=lambda x: -x[1]):
        md.append(f"| `{cat}` | {n} | {descriptions.get(cat, '')} |")
    md.append("")
    md.append("## Per-note summary")
    md.append("")
    md.append("| # | Note | Items | In-set | Dominant gap |")
    md.append("|---:|---|---:|---:|---|")
    for i, key in enumerate(MANUAL.keys(), 1):
        items = MANUAL[key]["items"]
        n_items = len(items)
        n_in = sum(1 for it in items if it["in_closed_set"])
        gaps = [it["coverage_note"] for it in items if not it["in_closed_set"]]
        # most common gap
        if gaps:
            gap_str = max(set(gaps), key=gaps.count)
        elif n_in == n_items:
            gap_str = "(none, all in-set)"
        else:
            gap_str = ""
        md.append(f"| {i} | {key} | {n_items} | {n_in} | {gap_str} |")
    md.append("")
    md.append("## Implications for the JBI submission")
    md.append("")
    md.append("- **Coverage gap is real and large.** The paper's hypothesis that real EHR text contains"
              " types of follow-up not present in the synthetic ontology is borne out on the very first 5"
              " notes. A clinician-annotated real-note evaluation in revision should report two metrics:")
    md.append("  1. *Closed-set recall* (over items the model could in principle predict).")
    md.append("  2. *Total recall* (counting OOV items as missed), which is the clinically relevant number.")
    md.append("")
    md.append("- **Schema extension priorities** (in order of frequency in this 5-note sample):")
    md.append("  1. Generic follow-up appointment (no specific procedure linked) - most common.")
    md.append("  2. Medication change / titration - common in chronic-disease follow-up.")
    md.append("  3. Conditional follow-up (\"if X then Y\") - scoping rule needed in the linker.")
    md.append("  4. Self-care instructions with a date - may be in-scope for scheduling auditors.")
    md.append("  5. Specialist referrals outside the consult set (psychology, dermatology, etc.).")
    md.append("")
    md.append("- **MTSamples is anonymized**: no visit_date is present in the headers. For a real eval"
              " we either need an MTSamples-derived corpus that injects synthetic visit dates, or a"
              " switch to MIMIC-IV-Note which records `charttime` per discharge summary.")

    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    print()
    print(f"Closed-set coverage on top-{len(MANUAL)} sample: {in_set_count}/{total_items} = {100 * in_set_count / total_items:.0f}%")


if __name__ == "__main__":
    main()
