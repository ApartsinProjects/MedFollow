"""Generate dataset-composition and action-ontology figures for the manuscript.

Reads ``Data/synthetic_clinical_notes_2000.csv`` and writes:
  - Paper/figures/dataset_composition.png  (specialty x action count grid)
  - Paper/figures/action_ontology.png      (top-N action vocabulary bars)

Run from the repository root:
    /c/Python314/python Paper/scripts/make_round2_figures.py
"""
from __future__ import annotations

import collections
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "Data" / "synthetic_clinical_notes_2000.csv"
OUT = ROOT / "Paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    df = pd.read_csv(DATA)

    # ---------- Figure: dataset composition (specialty x action count) ----------
    ct = pd.crosstab(df["specialty"], df["num_actions"])
    ct = ct.reindex(sorted(ct.index))
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    bottoms = np.zeros(len(ct))
    palette = ["#a6cee3", "#1f78b4", "#08306b"]
    for i, col in enumerate(ct.columns):
        ax.barh(
            ct.index,
            ct[col],
            left=bottoms,
            color=palette[i % len(palette)],
            edgecolor="white",
            label=f"{col}-action notes",
        )
        bottoms += ct[col].values
    ax.set_xlabel("Number of notes")
    ax.set_title("Dataset composition by specialty and follow-up action count (n = 2,000)")
    # Legend BELOW the plot, in one horizontal row, so it never overlaps the
    # longest bar (the original "lower right" inside-the-plot placement sat on
    # top of the data for the largest specialty).
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16),
              frameon=False, fontsize=9, ncol=len(ct.columns))
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.22)
    fig.savefig(OUT / "dataset_composition.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # ---------- Figure: action ontology (top-N vocabulary) ----------
    actions = []
    for s in df["actions_gt"]:
        for it in json.loads(s):
            actions.append(it["action"])
    counts = collections.Counter(actions)
    top = counts.most_common(20)
    labels = [k for k, _ in top][::-1]
    values = [v for _, v in top][::-1]

    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    ax.barh(labels, values, color="#08519c", edgecolor="white")
    ax.set_xlabel("Mention count across the corpus")
    ax.set_title(f"Most frequent follow-up actions (top 20 of {len(counts)} closed-set types)")
    ax.spines[["top", "right"]].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#999999")
    for i, v in enumerate(values):
        ax.text(v + 1, i, str(v), va="center", fontsize=8, color="#333333")
    fig.tight_layout()
    fig.savefig(OUT / "action_ontology.png", dpi=180)
    plt.close(fig)

    print(f"Wrote {OUT/'dataset_composition.png'}")
    print(f"Wrote {OUT/'action_ontology.png'}")
    print(f"Total distinct actions: {len(counts)}")
    print(f"Total action mentions: {sum(counts.values())}")


if __name__ == "__main__":
    main()
