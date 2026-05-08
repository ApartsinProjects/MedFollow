from __future__ import annotations

import ast
import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="paper")
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.titlesize": 13,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "figure.dpi": 180,
        "savefig.dpi": 300,
    }
)


def load_metrics(name: str) -> dict:
    text = (ROOT / "Results" / name).read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except Exception:
        pass
    try:
        return ast.literal_eval(text)
    except Exception:
        metrics = {}
        for raw in text.replace("{", "").replace("}", "").splitlines():
            if ":" not in raw:
                continue
            key, value = raw.split(":", 1)
            key = key.strip().strip("\"'")
            value = value.strip().rstrip(",")
            try:
                metrics[key] = float(value)
            except ValueError:
                continue
        return metrics


def parse_actions(value: str) -> list[dict]:
    if not value or value == "[]":
        return []
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return []


def classify_time_phrase(text: str) -> str:
    low = text.lower()
    if any(token in low for token in ["wk", "wks", "mo", "mos", "f/u", "~"]):
        return "shorthand"
    if any(token in low for token in ["about", "approximately", "approx", "within", "over the next"]):
        return "approximate"
    if "-" in low or " to " in low:
        return "range"
    if any(word in low for word in ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"]):
        return "word numeral"
    return "standard"


def make_dataset_composition(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.7), gridspec_kw={"width_ratios": [1.4, 1]})

    specialty_counts = df["specialty"].value_counts().sort_index()
    sns.barplot(x=specialty_counts.values, y=specialty_counts.index, ax=axes[0], color="#0a6f82")
    axes[0].set_title("Specialty coverage")
    axes[0].set_xlabel("Notes")
    axes[0].set_ylabel("")
    for i, value in enumerate(specialty_counts.values):
        axes[0].text(value + 5, i, str(value), va="center", fontsize=9)

    action_counts = df["num_actions"].astype(int).value_counts().sort_index()
    sns.barplot(x=action_counts.index.astype(str), y=action_counts.values, ax=axes[1], color="#ca6702")
    axes[1].set_title("Scheduled actions per note")
    axes[1].set_xlabel("Gold actions")
    axes[1].set_ylabel("Notes")
    for i, value in enumerate(action_counts.values):
        axes[1].text(i, value + 12, str(value), ha="center", fontsize=9)

    fig.suptitle("Synthetic corpus composition (N=2,000)", fontsize=14, fontweight="bold", y=1.04)
    fig.tight_layout()
    fig.savefig(OUT / "dataset_composition.png", bbox_inches="tight")
    plt.close(fig)


def make_time_phrase_distribution(df: pd.DataFrame) -> None:
    actions = []
    for raw in df["actions_gt"]:
        actions.extend(parse_actions(raw))

    phrase_types = Counter(classify_time_phrase(a.get("period_text", "")) for a in actions)
    units = Counter()
    for action in actions:
        low = action.get("period_text", "").lower()
        if any(x in low for x in ["day", "days"]):
            units["days"] += 1
        elif any(x in low for x in ["wk", "wks", "week", "weeks"]):
            units["weeks"] += 1
        elif any(x in low for x in ["mo", "mos", "month", "months"]):
            units["months"] += 1
        else:
            units["other"] += 1

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.7))

    unit_series = pd.Series(units).sort_values(ascending=False)
    sns.barplot(x=unit_series.index, y=unit_series.values, ax=axes[0], color="#005f73")
    axes[0].set_title("Temporal unit distribution")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Action-time labels")
    for i, value in enumerate(unit_series.values):
        axes[0].text(i, value + 8, str(value), ha="center", fontsize=9)

    phrase_series = pd.Series(phrase_types).sort_values(ascending=False)
    sns.barplot(x=phrase_series.values, y=phrase_series.index, ax=axes[1], color="#9b2226")
    axes[1].set_title("Surface-form categories")
    axes[1].set_xlabel("Action-time labels")
    axes[1].set_ylabel("")
    for i, value in enumerate(phrase_series.values):
        axes[1].text(value + 8, i, str(value), va="center", fontsize=9)

    fig.suptitle("Variation in gold temporal expressions", fontsize=14, fontweight="bold", y=1.04)
    fig.tight_layout()
    fig.savefig(OUT / "temporal_phrase_distribution.png", bbox_inches="tight")
    plt.close(fig)


def make_performance_summary() -> None:
    biobert = load_metrics("biobert_metrics.json")
    chatgpt = load_metrics("chatgpt_metrics.json")
    llama = load_metrics("llama_metrics.json")

    rows = [
        {
            "Model": "BioBERT hybrid",
            "Action F1": biobert["ner_span_ACT_f1"],
            "Time/Date F1": biobert["ner_span_TIME_f1"],
            "Action-Date F1": biobert["action_date_f1"],
            "Date MAE": biobert["period_date_abs_err_days_mae_on_matched_actions"],
        },
        {
            "Model": "ChatGPT zero-shot",
            "Action F1": chatgpt["ner_span_ACT_f1"],
            "Time/Date F1": chatgpt["ner_span_TIME_f1"],
            "Action-Date F1": chatgpt["action_date_f1"],
            "Date MAE": chatgpt["period_date_abs_err_days_mae_on_matched_actions"],
        },
        {
            "Model": "LLaMA fine-tuned",
            "Action F1": llama["STRICT_action_f1"],
            "Time/Date F1": llama["STRICT_date_only_f1"],
            "Action-Date F1": llama["STRICT_action_date_f1"],
            "Date MAE": llama["period_date_abs_err_days_mae_on_matched_actions"],
        },
    ]
    perf = pd.DataFrame(rows)
    long = perf.melt(id_vars="Model", value_vars=["Action F1", "Time/Date F1", "Action-Date F1"], var_name="Metric", value_name="F1")

    fig, axes = plt.subplots(1, 2, figsize=(11, 3.9), gridspec_kw={"width_ratios": [1.45, 1]})
    palette = ["#005f73", "#ee9b00", "#9b2226"]

    sns.barplot(data=long, x="Metric", y="F1", hue="Model", ax=axes[0], palette=palette)
    axes[0].set_ylim(0.75, 1.02)
    axes[0].set_title("Strict extraction performance")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("F1")
    axes[0].legend(loc="lower left", frameon=True)
    for container in axes[0].containers:
        axes[0].bar_label(container, fmt="%.3f", padding=2, fontsize=8)

    sns.barplot(data=perf, x="Model", y="Date MAE", ax=axes[1], palette=palette)
    axes[1].set_title("Date arithmetic error")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Mean absolute error (days)")
    axes[1].tick_params(axis="x", rotation=18)
    for container in axes[1].containers:
        axes[1].bar_label(container, fmt="%.2f", padding=2, fontsize=8)

    fig.suptitle("Hybrid span-link extraction vs direct generative extraction", fontsize=14, fontweight="bold", y=1.04)
    fig.tight_layout()
    fig.savefig(OUT / "performance_summary.png", bbox_inches="tight")
    plt.close(fig)


def make_pipeline_svg() -> None:
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="250" viewBox="0 0 1120 250">
  <style>
    .box{fill:#f7fbfc;stroke:#0a6f82;stroke-width:2;rx:10}
    .head{font:700 18px Arial,sans-serif;fill:#17313b}
    .body{font:14px Arial,sans-serif;fill:#40515a}
    .arrow{stroke:#9b2226;stroke-width:3;fill:none;marker-end:url(#arrow)}
  </style>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#9b2226"/>
    </marker>
  </defs>
  <rect x="18" y="50" width="160" height="110" class="box"/>
  <text x="38" y="86" class="head">Clinical note</text>
  <text x="38" y="115" class="body">note_text</text>
  <text x="38" y="137" class="body">visit_date</text>
  <path d="M185 105 H240" class="arrow"/>
  <rect x="248" y="50" width="170" height="110" class="box"/>
  <text x="270" y="86" class="head">BioBERT</text>
  <text x="270" y="115" class="body">sliding windows</text>
  <text x="270" y="137" class="body">shared encoder</text>
  <path d="M425 105 H480" class="arrow"/>
  <rect x="488" y="25" width="178" height="86" class="box"/>
  <text x="512" y="60" class="head">Head A</text>
  <text x="512" y="88" class="body">BIO action/time spans</text>
  <rect x="488" y="138" width="178" height="86" class="box"/>
  <text x="512" y="173" class="head">Head B</text>
  <text x="512" y="201" class="body">action-time linking</text>
  <path d="M674 68 H730" class="arrow"/>
  <path d="M674 181 H730" class="arrow"/>
  <rect x="738" y="50" width="170" height="110" class="box"/>
  <text x="760" y="86" class="head">Date normalizer</text>
  <text x="760" y="115" class="body">relative base = visit</text>
  <text x="760" y="137" class="body">ISO period_date</text>
  <path d="M915 105 H970" class="arrow"/>
  <rect x="978" y="50" width="124" height="110" class="box"/>
  <text x="1002" y="86" class="head">JSON</text>
  <text x="1002" y="115" class="body">action</text>
  <text x="1002" y="137" class="body">period_date</text>
</svg>
"""
    (OUT / "pipeline.svg").write_text(svg, encoding="utf-8")


def main() -> None:
    df = pd.read_csv(ROOT / "Data" / "synthetic_clinical_notes_2000.csv")
    make_dataset_composition(df)
    make_time_phrase_distribution(df)
    make_performance_summary()
    make_pipeline_svg()
    print(f"Wrote paper figures to {OUT}")


if __name__ == "__main__":
    main()
