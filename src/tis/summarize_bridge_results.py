from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize bridge alignment by task family and outcome")
    parser.add_argument(
        "--input",
        default="outputs/static_dynamic_bridge_50_minilm/alignment_summary.csv",
        help="Bridge alignment summary CSV",
    )
    parser.add_argument(
        "--output",
        default="outputs/static_dynamic_bridge_50_minilm/family_outcome_comparison.csv",
        help="Output CSV for family-level comparisons",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = pd.read_csv(args.input)

    grouped = (
        frame.groupby(["task_family", "outcome"])[["best_abs_alignment", "residual_energy"]]
        .agg(["mean", "median", "count"])
        .reset_index()
    )
    grouped.columns = [
        "task_family",
        "outcome",
        "best_abs_alignment_mean",
        "best_abs_alignment_median",
        "count",
        "residual_energy_mean",
        "residual_energy_median",
        "residual_count",
    ]
    grouped = grouped.drop(columns=["residual_count"])

    correct = grouped[grouped["outcome"] == "correct"].copy()
    incorrect = grouped[grouped["outcome"] == "incorrect"].copy()

    merged = correct.merge(
        incorrect,
        on="task_family",
        suffixes=("_correct", "_incorrect"),
        how="outer",
    )
    merged["alignment_mean_diff_incorrect_minus_correct"] = (
        merged["best_abs_alignment_mean_incorrect"] - merged["best_abs_alignment_mean_correct"]
    )
    merged["residual_mean_diff_incorrect_minus_correct"] = (
        merged["residual_energy_mean_incorrect"] - merged["residual_energy_mean_correct"]
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
