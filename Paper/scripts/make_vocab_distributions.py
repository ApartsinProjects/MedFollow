"""Generate a single 2-panel figure that merges what were previously
two separate figures (action ontology + temporal-phrase distribution).

Reduces total figure count from 8 to 6 to fit JBI's <=8 figures+tables cap.

Writes:
  - Paper/figures/vocabulary_distributions.png

Run from the repository root:
    /c/Python314/python Paper/scripts/make_vocab_distributions.py
"""
from __future__ import annotations

import collections
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "Data" / "synthetic_clinical_notes_2000.csv"
OUT = ROOT / "Paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    df = pd.read_csv(DATA)

    # Action ontology
    actions = []
    for s in df["actions_gt"]:
        for it in json.loads(s):
            actions.append(it["action"])
    act_counts = collections.Counter(actions)
    act_top = act_counts.most_common(15)

    # Temporal phrases
    phrases = []
    for s in df["actions_gt"]:
        for it in json.loads(s):
            phrases.append(it["period_text"].strip().lower())
    phrase_counts = collections.Counter(phrases)
    phr_top = phrase_counts.most_common(15)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.4))

    # Left panel: actions
    labels = [k for k, _ in act_top][::-1]
    values = [v for _, v in act_top][::-1]
    ax1.barh(labels, values, color="#08519c", edgecolor="white")
    ax1.set_xlabel("Mention count")
    ax1.set_title(f"(a) Top 15 follow-up actions ({len(act_counts)} total in closed set)", fontsize=10)
    ax1.spines[["top", "right"]].set_visible(False)
    for i, v in enumerate(values):
        ax1.text(v + 1, i, str(v), va="center", fontsize=8, color="#333333")

    # Right panel: temporal phrases
    labels = [k for k, _ in phr_top][::-1]
    values = [v for _, v in phr_top][::-1]
    ax2.barh(labels, values, color="#2c7fb8", edgecolor="white")
    ax2.set_xlabel("Mention count")
    ax2.set_title(f"(b) Top 15 temporal expressions ({len(phrase_counts)} surface forms total)", fontsize=10)
    ax2.spines[["top", "right"]].set_visible(False)
    for i, v in enumerate(values):
        ax2.text(v + 0.2, i, str(v), va="center", fontsize=8, color="#333333")

    fig.tight_layout()
    fig.savefig(OUT / "vocabulary_distributions.png", dpi=180)
    plt.close(fig)
    print(f"Wrote {OUT/'vocabulary_distributions.png'}")
    print(f"  actions: {len(act_counts)} types, {sum(act_counts.values())} mentions")
    print(f"  phrases: {len(phrase_counts)} surface forms, {sum(phrase_counts.values())} mentions")


if __name__ == "__main__":
    main()
