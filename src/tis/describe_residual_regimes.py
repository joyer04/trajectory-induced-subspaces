from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Describe residual geometric regimes with exemplars")
    parser.add_argument(
        "--residual-summary",
        default="outputs/static_dynamic_bridge_100_minilm/residual_summary.csv",
        help="Residual summary CSV from analyze_residual_structure.py",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/static_dynamic_bridge_100_minilm",
        help="Directory for residual regime summaries",
    )
    parser.add_argument(
        "--examples-per-cluster",
        type=int,
        default=5,
        help="Number of exemplar deltas to keep per residual cluster",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(args.residual_summary)
    frame["transition_text"] = (
        frame["from_step_text"].fillna("")
        + "  ==>  "
        + frame["to_step_text"].fillna("")
    )

    composition = (
        frame.groupby(["task_family", "outcome", "residual_cluster"])
        .size()
        .reset_index(name="count")
    )
    composition["group_total"] = composition.groupby(["task_family", "outcome"])["count"].transform("sum")
    composition["proportion"] = composition["count"] / composition["group_total"]
    composition = composition.sort_values(
        ["task_family", "outcome", "proportion", "count"],
        ascending=[True, True, False, False],
    )
    composition.to_csv(output_dir / "residual_regime_composition.csv", index=False)

    pivot = composition.pivot_table(
        index=["task_family", "outcome"],
        columns="residual_cluster",
        values="proportion",
        fill_value=0.0,
    ).reset_index()
    pivot.to_csv(output_dir / "residual_regime_profile_matrix.csv", index=False)

    exemplar_rows: list[dict] = []
    for cluster_id, cluster_frame in frame.groupby("residual_cluster"):
        ranked = cluster_frame.sort_values(
            ["residual_norm", "static_projection_norm"],
            ascending=[False, True],
        ).head(args.examples_per_cluster)
        for _, row in ranked.iterrows():
            exemplar_rows.append(
                {
                    "residual_cluster": cluster_id,
                    "task_family": row["task_family"],
                    "outcome": row["outcome"],
                    "trace_id": row["trace_id"],
                    "residual_norm": row["residual_norm"],
                    "static_projection_norm": row["static_projection_norm"],
                    "transition_text": row["transition_text"],
                }
            )
    pd.DataFrame(exemplar_rows).to_csv(output_dir / "residual_cluster_exemplars.csv", index=False)

    comparison_rows: list[dict] = []
    for task_family, family_frame in composition.groupby("task_family"):
        correct = family_frame[family_frame["outcome"] == "correct"].set_index("residual_cluster")
        incorrect = family_frame[family_frame["outcome"] == "incorrect"].set_index("residual_cluster")
        clusters = sorted(set(correct.index).union(set(incorrect.index)))
        for cluster_id in clusters:
            correct_prop = float(correct.loc[cluster_id, "proportion"]) if cluster_id in correct.index else 0.0
            incorrect_prop = float(incorrect.loc[cluster_id, "proportion"]) if cluster_id in incorrect.index else 0.0
            comparison_rows.append(
                {
                    "task_family": task_family,
                    "residual_cluster": cluster_id,
                    "correct_proportion": correct_prop,
                    "incorrect_proportion": incorrect_prop,
                    "incorrect_minus_correct": incorrect_prop - correct_prop,
                }
            )
    pd.DataFrame(comparison_rows).sort_values(
        ["task_family", "incorrect_minus_correct"],
        ascending=[True, False],
    ).to_csv(output_dir / "residual_regime_differences.csv", index=False)


if __name__ == "__main__":
    main()
