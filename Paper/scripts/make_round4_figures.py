"""Round 4 figures: temporal-phrase distribution and stress-factor coverage.

Reads ``Data/synthetic_clinical_notes_2000.csv`` and writes:
  - Paper/figures/temporal_phrase_distribution.png  (top-N period_text bars)
  - Paper/figures/stress_factor_coverage.png        (proportion of notes per
                                                     stress factor)

Run from the repository root:
    /c/Python314/python Paper/scripts/make_round4_figures.py
"""
from __future__ import annotations

import collections
import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "Data" / "synthetic_clinical_notes_2000.csv"
OUT = ROOT / "Paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)


SHORTHAND_RE = re.compile(r"(?i)\b(\d+\s*mos|q\d+\s*(?:mo|wk|w|d|h)|x\s*\d+\s*(?:w|d|m)|rtc\s*\d+\s*\w+)\b")
HISTORY_RE = re.compile(r"(?i)(history|hx|past medical history|\bago\b|previous|prior|last (?:year|month|week))")


def normalize_phrase(p: str) -> str:
    return p.strip().lower()


def main() -> None:
    df = pd.read_csv(DATA)

    # ---------- Temporal phrase distribution ----------
    phrases: list[str] = []
    for s in df["actions_gt"]:
        for it in json.loads(s):
            phrases.append(normalize_phrase(it["period_text"]))
    counts = collections.Counter(phrases)
    top = counts.most_common(20)
    labels = [k for k, _ in top][::-1]
    values = [v for _, v in top][::-1]

    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    ax.barh(labels, values, color="#2c7fb8", edgecolor="white")
    ax.set_xlabel("Mention count across the corpus")
    ax.set_title(f"Most frequent temporal expressions (top 20 of {len(counts)} surface forms)")
    ax.spines[["top", "right"]].set_visible(False)
    for i, v in enumerate(values):
        ax.text(v + 1, i, str(v), va="center", fontsize=8, color="#333333")
    fig.tight_layout()
    fig.savefig(OUT / "temporal_phrase_distribution.png", dpi=180)
    plt.close(fig)

    # ---------- Stress factor coverage ----------
    n = len(df)
    multi_action = (df["num_actions"] >= 2).sum()
    zero_action = (df["num_actions"] == 0).sum()
    shorthand = df["note_text"].apply(lambda t: bool(SHORTHAND_RE.search(t))).sum()
    history = df["note_text"].apply(lambda t: bool(HISTORY_RE.search(t))).sum()
    flagged = (df["span_error"] != "").sum() if df["span_error"].dtype == object else (df["span_error"].notna() & (df["span_error"] != "")).sum()

    # Plan variant coverage
    plan_a = (df["plan_variant"] == "A").sum()
    plan_b = (df["plan_variant"] == "B").sum()
    plan_e = (df["plan_variant"] == "E").sum()

    factors = [
        ("Multi-action notes (≥2 actions)", multi_action),
        ("Zero-action notes", zero_action),
        ("Notes containing shorthand temporal forms", shorthand),
        ("Notes containing historical-time mentions", history),
        ("Plan variant A (canonical)", plan_a),
        ("Plan variant B (numbered list)", plan_b),
        ("Plan variant E (run-on)", plan_e),
        ("Notes with validation-flag annotations", flagged),
    ]
    labels = [k for k, _ in factors][::-1]
    values = [v for _, v in factors][::-1]
    pct = [100 * v / n for v in values]

    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    bars = ax.barh(labels, pct, color="#6a51a3", edgecolor="white")
    for bar, val, count in zip(bars, pct, values):
        ax.text(val + 0.5, bar.get_y() + bar.get_height() / 2, f"{val:4.1f}% (n={count})", va="center", fontsize=8, color="#333333")
    ax.set_xlabel("Share of corpus (%)")
    ax.set_xlim(0, max(pct) * 1.25)
    ax.set_title("Stress-factor coverage in the 2,000-note corpus")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "stress_factor_coverage.png", dpi=180)
    plt.close(fig)

    print(f"Wrote {OUT/'temporal_phrase_distribution.png'} ({len(counts)} unique surface forms)")
    print(f"Wrote {OUT/'stress_factor_coverage.png'}")
    print(f"Top phrase: {top[0]}; rarest in top-20: {top[-1]}")


if __name__ == "__main__":
    main()
