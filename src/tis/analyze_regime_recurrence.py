from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze recurrence of residual regimes within task families")
    parser.add_argument(
        "--residual-summary",
        default="outputs/static_dynamic_bridge_100_minilm/residual_summary.csv",
        help="Residual summary CSV",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/static_dynamic_bridge_100_minilm",
        help="Directory for recurrence outputs",
    )
    return parser.parse_args()


def normalized_entropy(proportions: list[float]) -> float:
    import math

    positive = [p for p in proportions if p > 0]
    if len(positive) <= 1:
        return 0.0
    entropy = -sum(p * math.log(p, 2) for p in positive)
    max_entropy = math.log(len(proportions), 2) if len(proportions) > 1 else 1.0
    return entropy / max_entropy if max_entropy > 0 else 0.0


def main() -> None:
    args = parse_args()
    frame = pd.read_csv(args.residual_summary)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for (task_family, outcome), group in frame.groupby(["task_family", "outcome"]):
        cluster_counts = group["residual_cluster"].value_counts().sort_index()
        proportions = (cluster_counts / cluster_counts.sum()).tolist()
        dominant_cluster = int(cluster_counts.idxmax())
        dominant_share = float(cluster_counts.max() / cluster_counts.sum())
        rows.append(
            {
                "task_family": task_family,
                "outcome": outcome,
                "n_deltas": int(cluster_counts.sum()),
                "n_active_clusters": int((cluster_counts > 0).sum()),
                "dominant_cluster": dominant_cluster,
                "dominant_share": dominant_share,
                "normalized_entropy": normalized_entropy(proportions),
            }
        )

    summary = pd.DataFrame(rows).sort_values(["task_family", "outcome"])
    summary.to_csv(output_dir / "residual_regime_recurrence.csv", index=False)

    paired_rows: list[dict] = []
    for task_family, family in summary.groupby("task_family"):
        correct = family[family["outcome"] == "correct"]
        incorrect = family[family["outcome"] == "incorrect"]
        if correct.empty or incorrect.empty:
            continue
        c = correct.iloc[0]
        i = incorrect.iloc[0]
        paired_rows.append(
            {
                "task_family": task_family,
                "correct_dominant_cluster": int(c["dominant_cluster"]),
                "incorrect_dominant_cluster": int(i["dominant_cluster"]),
                "same_dominant_cluster": bool(int(c["dominant_cluster"]) == int(i["dominant_cluster"])),
                "correct_dominant_share": float(c["dominant_share"]),
                "incorrect_dominant_share": float(i["dominant_share"]),
                "correct_entropy": float(c["normalized_entropy"]),
                "incorrect_entropy": float(i["normalized_entropy"]),
                "incorrect_minus_correct_entropy": float(i["normalized_entropy"] - c["normalized_entropy"]),
            }
        )
    pd.DataFrame(paired_rows).to_csv(output_dir / "residual_regime_recurrence_paired.csv", index=False)


if __name__ == "__main__":
    main()
