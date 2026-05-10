"""Score MTSamples notes for follow-up-instruction richness and emit the
top-N candidates as a CSV ready for manual annotation against the
MedFollow schema (action span, time span, period_date).

Scoring rationale (per note):
  +3  explicit "(in|within|after) N (day|week|month|wk|mo|d)s?" pattern
  +3  explicit "follow[ -]?up in N <unit>" pattern
  +2  clinical shorthand temporal form (q6mo, x2w, RTC 3mo, etc.)
  +2  imperative scheduling verb near a temporal phrase (schedule|order|
       plan|will obtain|return) within +/-30 chars of a temporal token
  +1  any other temporal-expression match (broad regex)
  +1  belongs to a high-density specialty (Discharge Summary, SOAP/Progress,
       Emergency Room, General Medicine, Office Notes, Consult-H&P, Orthopedic)
  -2  past-tense markers ("had a follow-up", "previously scheduled",
       "last <unit>", "<unit> ago")
  -1  pure radiology/pathology report (specialty contains "Radiology" or
       "Pathology")

Outputs:
  Data/external/mtsamples/mtsamples_top100_followup.csv  (note_id, specialty,
       sample_name, score, n_actions_estimate, n_temporal_matches,
       transcription)
  Data/external/mtsamples/mtsamples_followup_scores.csv  (full-corpus scores
       for transparency / future re-ranking)

Run from the repository root:
    /c/Python314/python Paper/scripts/rank_mtsamples_followup.py
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "Data" / "external" / "mtsamples" / "mtsamples.csv"
OUT_DIR = ROOT / "Data" / "external" / "mtsamples"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------- regex patterns ----------
RE_FUTURE_NUM = re.compile(
    r"(?i)\b(?:in|within|after|over\s+the\s+next)\s+"
    r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"fifteen|twenty|thirty)\s+"
    r"(?:day|week|month|wk|mo|hr|d)s?\b"
)
RE_FOLLOWUP_IN = re.compile(
    r"(?i)\b(?:follow[\s-]?up|f/u|return|RTC|come\s+back|reassess|recheck|review)"
    r"\s+(?:in|after|within)\s+"
    r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s*-?\s*"
    r"(?:day|week|month|wk|mo|hr|d)s?\b"
)
RE_SHORTHAND = re.compile(
    r"(?i)(?:^|[\s,;:.])(?:q\d+\s*(?:mo|wk|w|d|hr|h)|x\s*\d+\s*(?:w|d|m|wk|mo)|"
    r"RTC\s*\d+\s*(?:mo|wk|d|w|hr|h)|\d+\s*mos?\b|\d+\s*wks?\b)"
)
RE_TEMP_BROAD = re.compile(
    r"(?i)\b(?:in|within|after|over)\s+(?:\d+|one|two|three|four|five|six|seven|"
    r"eight|nine|ten)\s*-?\s*(?:day|week|month|year|wk|mo|hr)s?\b"
)
RE_SCHED_VERB = re.compile(
    r"(?i)\b(?:schedule[ds]?|scheduling|order(?:ed|s)?|plan(?:ned|s|ning)?|"
    r"will\s+(?:obtain|order|schedule|return|see|reassess|recheck|repeat)|"
    r"recommend(?:ed|s|ation)?|advise[ds]?|next\s+(?:appointment|visit|follow))\b"
)
RE_PAST = re.compile(
    r"(?i)\b(?:had\s+(?:a\s+)?follow|previously\s+(?:scheduled|seen|had)|"
    r"last\s+(?:visit|year|month|week|appointment)|"
    r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+"
    r"(?:days?|weeks?|months?|years?)\s+ago|"
    r"history\s+of\s+|H/O\b)"
)

HIGH_DENSITY_SPECIALTIES = {
    "discharge summary",
    "soap / chart / progress notes",
    "emergency room reports",
    "general medicine",
    "office notes",
    "consult - history and phy.",
    "orthopedic",
}
LOW_VALUE_SPECIALTIES = {
    "radiology",
    "pathology",
}


def score_note(row: pd.Series) -> dict:
    text = str(row.get("transcription", "") or "")
    spec = str(row.get("medical_specialty", "") or "").strip().lower()
    score = 0
    components: dict[str, int] = {}

    # primary signals
    n_future_num = len(RE_FUTURE_NUM.findall(text))
    n_followup_in = len(RE_FOLLOWUP_IN.findall(text))
    n_shorthand = len(RE_SHORTHAND.findall(text))
    n_temp_broad = len(RE_TEMP_BROAD.findall(text))
    n_sched = len(RE_SCHED_VERB.findall(text))
    n_past = len(RE_PAST.findall(text))

    # imperative verb within 40 chars of a temporal expression
    n_sched_near_time = 0
    for m in RE_TEMP_BROAD.finditer(text):
        window = text[max(0, m.start() - 40): m.end() + 40]
        if RE_SCHED_VERB.search(window):
            n_sched_near_time += 1

    score += 3 * n_future_num
    score += 3 * n_followup_in
    score += 2 * n_shorthand
    score += 2 * n_sched_near_time
    score += 1 * n_temp_broad
    score -= 2 * n_past

    components = {
        "future_num": n_future_num,
        "followup_in": n_followup_in,
        "shorthand": n_shorthand,
        "sched_near_time": n_sched_near_time,
        "temp_broad": n_temp_broad,
        "sched_verb_total": n_sched,
        "past_markers": n_past,
    }

    # specialty bonus / penalty
    if spec in HIGH_DENSITY_SPECIALTIES:
        score += 1
        components["spec_bonus"] = 1
    elif any(low in spec for low in LOW_VALUE_SPECIALTIES):
        score -= 1
        components["spec_bonus"] = -1
    else:
        components["spec_bonus"] = 0

    components["score"] = score
    components["n_chars"] = len(text)
    components["n_actions_estimate"] = n_future_num + n_followup_in + n_shorthand
    components["n_temporal_matches"] = n_future_num + n_followup_in + n_shorthand + n_temp_broad

    return components


def main() -> None:
    df = pd.read_csv(SRC)
    df = df.rename(columns={"Unnamed: 0": "note_id"})
    df["note_id"] = df["note_id"].astype(int)

    scores = df.apply(score_note, axis=1, result_type="expand")
    out = pd.concat([df, scores], axis=1)

    # Drop non-clinical filler (very short notes, no transcription, etc.)
    out = out[out["n_chars"] >= 200].copy()

    # Save full scoring table
    full_out = OUT_DIR / "mtsamples_followup_scores.csv"
    out_full = out[[
        "note_id", "medical_specialty", "sample_name", "score",
        "future_num", "followup_in", "shorthand", "sched_near_time",
        "temp_broad", "past_markers", "spec_bonus",
        "n_chars", "n_actions_estimate", "n_temporal_matches",
    ]].sort_values("score", ascending=False)
    out_full.to_csv(full_out, index=False)

    # MTSamples cross-tags many notes with multiple specialties, so the same
    # transcription appears under several specialty labels. Dedupe by the
    # transcription text before picking the top 100. We keep the highest-
    # scoring duplicate (which, since score depends on text + specialty bonus,
    # will favour the high-density specialty assignment when applicable).
    out = (
        out.sort_values("score", ascending=False)
        .drop_duplicates(subset=["transcription"], keep="first")
        .copy()
    )
    print(f"After dedup by transcription: {len(out)} unique notes")
    top100 = out.head(100).copy()

    cols = [
        "note_id", "medical_specialty", "sample_name", "score",
        "n_actions_estimate", "n_temporal_matches", "future_num",
        "followup_in", "shorthand", "past_markers", "transcription",
    ]
    top100_out = OUT_DIR / "mtsamples_top100_followup.csv"
    top100[cols].to_csv(top100_out, index=False)

    # Console summary
    print(f"Wrote {full_out} ({len(out_full)} rows)")
    print(f"Wrote {top100_out} (100 rows)")
    print()
    print("--- top-100 score distribution ---")
    print(top100["score"].describe().round(2))
    print()
    print("--- top-100 by specialty ---")
    print(top100["medical_specialty"].value_counts())
    print()
    print("--- example (rank 1) ---")
    r = top100.iloc[0]
    print(f"  specialty: {r['medical_specialty'].strip()}")
    print(f"  sample_name: {r['sample_name'].strip()}")
    print(f"  score: {r['score']} (future_num={r['future_num']}, followup_in={r['followup_in']}, shorthand={r['shorthand']}, sched_near={r['sched_near_time']})")
    # show 280-char snippet around first temporal match
    text = str(r['transcription'])
    m = RE_TEMP_BROAD.search(text) or RE_FOLLOWUP_IN.search(text) or RE_SHORTHAND.search(text)
    if m:
        s = max(0, m.start() - 80)
        e = min(len(text), m.end() + 200)
        print(f"  context: ...{text[s:e]!r}...")


if __name__ == "__main__":
    main()
