"""Compute Wilson 95% CIs on proportion metrics and bootstrap CIs on F1
metrics for all three systems, and emit:

  - Paper/figures/model_comparison_with_ci.png  (grouped bar chart with CIs)
  - Paper/figures/date_error_with_dispersion.png (MAE with reference lines)
  - Console table that can be pasted into the manuscript

Counts are reconstructed from the released metrics files in Results/. We
treat each prediction outcome as a Bernoulli draw (TP=1, FP=0 for
precision; TP=1, FN=0 for recall) and resample with replacement to
estimate F1 sampling variability. This is the standard "instance-level
bootstrap" used when raw predictions are not available but TP/FP/FN
counts are.

Run from the repository root:
    /c/Python314/python Paper/scripts/compute_confidence_intervals.py
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

Z95 = 1.959963984540054  # two-sided 95% normal critical value
RNG = np.random.default_rng(42)
N_BOOT = 10_000


def wilson(k: int, n: int, z: float = Z95) -> tuple[float, float, float]:
    """Wilson score interval for a binomial proportion. Returns (point, lo, hi)."""
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return p, max(0.0, centre - half), min(1.0, centre + half)


def bootstrap_f1(tp: int, fp: int, fn: int, n_boot: int = N_BOOT) -> tuple[float, float, float]:
    """Instance-level bootstrap on reconstructed outcome arrays.

    We construct a virtual array of (predicted, gold) outcomes:
      - tp 'positive-positive' instances
      - fp 'positive-negative' instances (predicted but not in gold)
      - fn 'negative-positive' instances (gold but not predicted)
    and resample these (tp+fp+fn) outcomes with replacement, recomputing
    F1 each time. The 2.5/97.5 percentiles give a 95% CI.
    """
    n = tp + fp + fn
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    # Encode: 0 = TP, 1 = FP, 2 = FN
    arr = np.concatenate(
        [np.zeros(tp, dtype=np.int8), np.ones(fp, dtype=np.int8), np.full(fn, 2, dtype=np.int8)]
    )
    f1s = np.empty(n_boot, dtype=np.float64)
    for i in range(n_boot):
        sample = RNG.choice(arr, size=n, replace=True)
        s_tp = int((sample == 0).sum())
        s_fp = int((sample == 1).sum())
        s_fn = int((sample == 2).sum())
        denom = 2 * s_tp + s_fp + s_fn
        f1s[i] = (2 * s_tp / denom) if denom else float("nan")
    point = (2 * tp) / (2 * tp + fp + fn)
    lo, hi = np.nanpercentile(f1s, [2.5, 97.5])
    return point, float(lo), float(hi)


@dataclass
class ModelCounts:
    name: str
    # span counts (gold-aligned exact-offset)
    act_tp: int; act_fp: int; act_fn: int
    time_tp: int; time_fp: int; time_fn: int
    # linked pair counts (= action-date in this benchmark since action match implies date eligibility)
    pair_tp: int; pair_fp: int; pair_fn: int
    # date-on-matched
    date_correct: int; date_matched: int
    # date error
    mae_days: float


def main() -> None:
    # Counts reconstructed from Results/{biobert,chatgpt,llama}_metrics.json.
    # See companion notes in the file header for derivation.
    biobert = ModelCounts(
        name="BioBERT hybrid",
        act_tp=196, act_fp=2, act_fn=0,
        time_tp=196, time_fp=1, time_fn=0,
        pair_tp=193, pair_fp=5, pair_fn=3,
        date_correct=193, date_matched=196,
        mae_days=0.531,
    )
    chatgpt = ModelCounts(
        name="ChatGPT zero-shot",
        act_tp=192, act_fp=4, act_fn=4,
        time_tp=162, time_fp=32, time_fn=34,
        pair_tp=162, pair_fp=34, pair_fn=34,
        date_correct=162, date_matched=192,
        mae_days=5.068,
    )
    llama = ModelCounts(
        name="LLaMA-3 8B (LoRA)",
        act_tp=196, act_fp=0, act_fn=0,
        time_tp=160, time_fp=36, time_fn=36,
        pair_tp=158, pair_fp=38, pair_fn=38,
        date_correct=158, date_matched=196,
        mae_days=10.878,
    )
    models = [biobert, chatgpt, llama]

    # Print the table
    print(f"{'Model':22s} {'Metric':22s} {'point':>8s} {'95% CI':>22s}  {'method':10s}")
    print("-" * 90)

    metric_rows = {}
    for m in models:
        rows = {}

        # Action span F1 (bootstrap)
        f, lo, hi = bootstrap_f1(m.act_tp, m.act_fp, m.act_fn)
        rows["Action span F1"] = (f, lo, hi, "bootstrap")
        # Time span F1
        f, lo, hi = bootstrap_f1(m.time_tp, m.time_fp, m.time_fn)
        rows["Time span F1"] = (f, lo, hi, "bootstrap")
        # Linked-pair F1 == action-date F1 in this benchmark
        f, lo, hi = bootstrap_f1(m.pair_tp, m.pair_fp, m.pair_fn)
        rows["Action-date F1"] = (f, lo, hi, "bootstrap")
        # Exact date accuracy on matched (Wilson)
        p, lo, hi = wilson(m.date_correct, m.date_matched)
        rows["Date exact acc."] = (p, lo, hi, "Wilson")
        # Action span precision / recall (Wilson) for transparency
        p, lo, hi = wilson(m.act_tp, m.act_tp + m.act_fp)
        rows["  Action precision"] = (p, lo, hi, "Wilson")
        p, lo, hi = wilson(m.act_tp, m.act_tp + m.act_fn)
        rows["  Action recall"] = (p, lo, hi, "Wilson")
        p, lo, hi = wilson(m.pair_tp, m.pair_tp + m.pair_fp)
        rows["  Action-date precision"] = (p, lo, hi, "Wilson")
        p, lo, hi = wilson(m.pair_tp, m.pair_tp + m.pair_fn)
        rows["  Action-date recall"] = (p, lo, hi, "Wilson")

        for metric, (point, lo, hi, method) in rows.items():
            ci_str = f"[{lo:.3f}, {hi:.3f}]"
            print(f"{m.name:22s} {metric:22s} {point:8.4f} {ci_str:>22s}  {method:10s}")
        print()
        metric_rows[m.name] = rows

    # ---------- Comparison figure with CIs ----------
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    metrics_to_plot = ["Action span F1", "Time span F1", "Action-date F1", "Date exact acc."]
    palette = {"BioBERT hybrid": "#08519c", "ChatGPT zero-shot": "#fd8d3c", "LLaMA-3 8B (LoRA)": "#74c476"}
    n_models = len(models)
    width = 0.26
    x = np.arange(len(metrics_to_plot))
    for i, m in enumerate(models):
        rows = metric_rows[m.name]
        ys = [rows[k][0] for k in metrics_to_plot]
        los = [rows[k][1] for k in metrics_to_plot]
        his = [rows[k][2] for k in metrics_to_plot]
        yerr = np.array([[y - lo for y, lo in zip(ys, los)], [hi - y for y, hi in zip(ys, his)]])
        offset = (i - (n_models - 1) / 2) * width
        bars = ax.bar(x + offset, ys, width, color=palette[m.name], label=m.name, edgecolor="white")
        ax.errorbar(x + offset, ys, yerr=yerr, fmt="none", color="#333333", capsize=3, linewidth=1)
        for xi, y in zip(x + offset, ys):
            ax.text(xi, min(y + 0.02, 1.02), f"{y:.3f}", ha="center", fontsize=8, color="#333333")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_to_plot, fontsize=9)
    ax.set_ylim(0.0, 1.08)
    ax.set_ylabel("Score (with 95% CI)")
    ax.set_title("Held-out performance with 95% confidence intervals (n=198 notes, 196 actions)")
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "model_comparison_with_ci.png", dpi=180)
    plt.close(fig)

    # ---------- Date error figure ----------
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    names = [m.name for m in models]
    maes = [m.mae_days for m in models]
    colors = [palette[n] for n in names]
    bars = ax.bar(names, maes, color=colors, edgecolor="white")
    for bar, val in zip(bars, maes):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.2, f"{val:.2f}", ha="center", fontsize=10)
    ax.set_ylabel("Mean absolute date error (days)")
    ax.set_title("Calendar error on matched actions")
    ax.spines[["top", "right"]].set_visible(False)
    ax.axhline(1.0, color="#999", linestyle="--", linewidth=0.8)
    ax.text(2.3, 1.2, "1 day", fontsize=8, color="#666")
    ax.axhline(7.0, color="#999", linestyle="--", linewidth=0.8)
    ax.text(2.3, 7.2, "1 week", fontsize=8, color="#666")
    fig.tight_layout()
    fig.savefig(OUT / "date_error_with_dispersion.png", dpi=180)
    plt.close(fig)

    print(f"Wrote {OUT/'model_comparison_with_ci.png'}")
    print(f"Wrote {OUT/'date_error_with_dispersion.png'}")


if __name__ == "__main__":
    main()
