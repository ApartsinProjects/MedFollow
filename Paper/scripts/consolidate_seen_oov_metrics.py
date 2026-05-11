"""Consolidate the six per-system per-split metric JSONs from Michal's
Drive artifacts into a single canonical Results/results_seen_oov_with_ci.json
that drives every number cited in the manuscript.

Source files (read-only, under newrepo/):
  newrepo/artifacts/metrics/{biobert,llama,gpt}_{seen,oov}_metrics.json

Output:
  Results/results_seen_oov_with_ci.json   (consolidated; canonical)
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "newrepo" / "artifacts" / "metrics"
DST = ROOT / "Results" / "results_seen_oov_with_ci.json"

CANON = {
    "biobert": "BioBERT structured pipeline",
    "llama": "LLaMA-3 8B LoRA",
    "gpt": "GPT-4o-mini zero-shot",
}


def _safe_ci(ci_dict, key):
    """Look up a metric's CI under several possible names."""
    if key in ci_dict:
        v = ci_dict[key]
        return [round(v["ci_lower"], 4), round(v["ci_upper"], 4)]
    return [None, None]


def main() -> None:
    out = {
        "evaluation": {
            "methodology": {
                "split_design": "Action-disjoint Seen/OOV split with 28 canonical action types "
                                "partitioned by numpy shuffle (seed 123) into 18 train types, "
                                "4 OOV-validation types, and 6 OOV-test types. A separate seen-test "
                                "set is drawn from notes whose action types are in the training set.",
                "note_partition": {
                    "train": 901, "seen_val": 100, "oov_val": 178,
                    "seen_test": 259, "oov_test": 259,
                },
                "bootstrap": "Note-level resampling, 1,000 iterations, seed 123",
                "random_seed": 123,
                "metric_definitions": {
                    "action_f1": "Set-level F1 on canonical TestSpecification labels.",
                    "offset_f1": "Set-level F1 on normalized TimeSpecification day-offsets.",
                    "pair_f1":   "Set-level F1 on complete (TestSpecification, days_offset) pairs (end-to-end).",
                    "mae_days":  "Mean absolute error in days on matched TestSpecification entities."
                }
            },
            "systems": {}
        }
    }

    for sys_key in ["biobert", "llama", "gpt"]:
        sys_entry = {"canonical_name": CANON[sys_key]}
        for split_key in ["seen", "oov"]:
            f = SRC / f"{sys_key}_{split_key}_metrics.json"
            m = json.load(open(f))
            point = m["point"]
            ci = m.get("ci", {})
            ci_mae = ci.get("period_date_abs_err_days_mae_on_matched_actions", {})
            sys_entry[f"{split_key}_test"] = {
                "n_notes": point.get("n_eval"),
                "n_matched_actions": point.get("n_matched_actions_for_date"),
                "action_f1": {"point": round(point["action_f1"], 4),
                              "ci95":  _safe_ci(ci, "action_f1")},
                "offset_f1": {"point": round(point["offset_f1"], 4),
                              "ci95":  _safe_ci(ci, "offset_f1")},
                "pair_f1":   {"point": round(point["pair_f1"], 4),
                              "ci95":  _safe_ci(ci, "pair_f1")},
                "mae_days":  {"point": round(point["period_date_abs_err_days_mae_on_matched_actions"], 2),
                              "ci95":  [round(ci_mae.get("ci_lower", 0), 2),
                                        round(ci_mae.get("ci_upper", 0), 2)]
                                       if ci_mae else [None, None]}
            }
        out["evaluation"]["systems"][sys_key] = sys_entry

    DST.parent.mkdir(parents=True, exist_ok=True)
    with open(DST, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {DST.relative_to(ROOT)}")
    print()

    # Print headline table (the new Table 2 in the manuscript)
    hdr = f'{"Model":<28} {"Split":<6} {"Action F1 [95% CI]":<24} {"Offset F1 [95% CI]":<24} {"Pair F1 [95% CI]":<24} {"MAE [95% CI]":<18}'
    print(hdr)
    print("-" * len(hdr))
    for sys_key in ["biobert", "llama", "gpt"]:
        e = out["evaluation"]["systems"][sys_key]
        for sp in ["seen_test", "oov_test"]:
            d = e[sp]
            af = f'{d["action_f1"]["point"]:.3f} [{d["action_f1"]["ci95"][0]:.3f}, {d["action_f1"]["ci95"][1]:.3f}]'
            of = f'{d["offset_f1"]["point"]:.3f} [{d["offset_f1"]["ci95"][0]:.3f}, {d["offset_f1"]["ci95"][1]:.3f}]'
            pf = f'{d["pair_f1"]["point"]:.3f} [{d["pair_f1"]["ci95"][0]:.3f}, {d["pair_f1"]["ci95"][1]:.3f}]'
            mae_lo = d["mae_days"]["ci95"][0]
            mae_hi = d["mae_days"]["ci95"][1]
            mae = f'{d["mae_days"]["point"]:.2f} [{mae_lo:.2f}, {mae_hi:.2f}]' if mae_lo is not None else f'{d["mae_days"]["point"]:.2f}'
            print(f'{e["canonical_name"]:<28} {sp[:4]:<6} {af:<24} {of:<24} {pf:<24} {mae:<18}')


if __name__ == "__main__":
    main()
