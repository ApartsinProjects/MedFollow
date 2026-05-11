"""Generate the seen-vs-OOV comparison figures for the manuscript from
the consolidated Results/results_seen_oov_with_ci.json artifact.

Writes:
  Paper/figures/seen_oov_f1_comparison.png  (3-panel: Action / Offset / Pair F1 by model x split)
  Paper/figures/seen_oov_mae.png            (MAE by model x split, log-y because BioBERT = 0)

Run from the repository root:
    /c/Python314/python Paper/scripts/make_seen_oov_figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "Results" / "results_seen_oov_with_ci.json"
OUT = ROOT / "Paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)


SYSTEM_ORDER = ["biobert", "llama", "gpt"]
SHORT_NAME = {
    "biobert": "BioBERT pipeline",
    "llama": "LLaMA-3 8B LoRA",
    "gpt": "GPT-4o-mini zero-shot",
}
COLOUR = {
    "biobert": "#08519c",
    "llama":   "#fd8d3c",
    "gpt":     "#74c476",
}


def main() -> None:
    data = json.load(open(SRC))["evaluation"]["systems"]

    # ---------- Figure 1: 3-panel F1 comparison ----------
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 4.5), sharey=True)
    metric_titles = [
        ("action_f1", "(a) TestSpecification F1"),
        ("offset_f1", "(b) TimeSpecification offset F1"),
        ("pair_f1",   "(c) Test-Time pair F1 (end-to-end)"),
    ]
    width = 0.36
    x = np.arange(2)   # seen, oov
    for ax, (metric, title) in zip(axes, metric_titles):
        for i, sys_key in enumerate(SYSTEM_ORDER):
            pts = []
            err_lo = []
            err_hi = []
            for split_key in ["seen_test", "oov_test"]:
                d = data[sys_key][split_key][metric]
                p = d["point"]
                lo, hi = d["ci95"]
                pts.append(p)
                err_lo.append(p - lo)
                err_hi.append(hi - p)
            offset = (i - (len(SYSTEM_ORDER) - 1) / 2) * width
            bars = ax.bar(x + offset, pts, width, color=COLOUR[sys_key],
                          edgecolor="white", label=SHORT_NAME[sys_key] if ax is axes[0] else None)
            yerr = np.array([err_lo, err_hi])
            ax.errorbar(x + offset, pts, yerr=yerr, fmt="none",
                        color="#333333", capsize=3, linewidth=1)
            for xi, p in zip(x + offset, pts):
                ax.text(xi, min(p + 0.025, 1.04), f"{p:.3f}",
                        ha="center", fontsize=8, color="#333333")
        ax.set_title(title, fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(["Seen-test (n=259)", "OOV-test (n=259)"], fontsize=10)
        ax.set_ylim(0.0, 1.12)
        ax.spines[["top", "right"]].set_visible(False)
        if ax is axes[0]:
            ax.set_ylabel("F1 (with 95% CI)")
    axes[0].legend(loc="lower left", frameon=False, fontsize=9)
    fig.suptitle("Held-out performance with 95% confidence intervals", fontsize=12, y=1.01)
    fig.tight_layout()
    fig.savefig(OUT / "seen_oov_f1_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT/'seen_oov_f1_comparison.png'}")

    # ---------- Figure 2: MAE comparison (linear scale; BioBERT shows as zero) ----------
    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    width = 0.36
    x = np.arange(2)
    for i, sys_key in enumerate(SYSTEM_ORDER):
        pts = []
        err_lo = []
        err_hi = []
        for split_key in ["seen_test", "oov_test"]:
            d = data[sys_key][split_key]["mae_days"]
            p = d["point"]
            lo, hi = d["ci95"]
            pts.append(p)
            err_lo.append(p - lo if lo is not None else 0)
            err_hi.append(hi - p if hi is not None else 0)
        offset = (i - (len(SYSTEM_ORDER) - 1) / 2) * width
        ax.bar(x + offset, pts, width, color=COLOUR[sys_key], edgecolor="white", label=SHORT_NAME[sys_key])
        yerr = np.array([err_lo, err_hi])
        ax.errorbar(x + offset, pts, yerr=yerr, fmt="none",
                    color="#333333", capsize=3, linewidth=1)
        for xi, p in zip(x + offset, pts):
            ax.text(xi, p + 0.6, f"{p:.2f}", ha="center", fontsize=9, color="#333333")
    ax.set_xticks(x)
    ax.set_xticklabels(["Seen-test (n=259)", "OOV-test (n=259)"], fontsize=10)
    ax.set_ylabel("Mean absolute date error (days, 95% CI)")
    ax.set_title("Calendar error by model and split")
    ax.spines[["top", "right"]].set_visible(False)
    ax.axhline(1.0, color="#999", linestyle="--", linewidth=0.8)
    ax.text(1.65, 1.4, "1 day", fontsize=8, color="#666")
    ax.axhline(7.0, color="#999", linestyle="--", linewidth=0.8)
    ax.text(1.65, 7.4, "1 week", fontsize=8, color="#666")
    ax.axhline(30.0, color="#999", linestyle="--", linewidth=0.8)
    ax.text(1.65, 30.4, "1 month", fontsize=8, color="#666")
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.set_ylim(0, 40)
    fig.tight_layout()
    fig.savefig(OUT / "seen_oov_mae.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT/'seen_oov_mae.png'}")


if __name__ == "__main__":
    main()
