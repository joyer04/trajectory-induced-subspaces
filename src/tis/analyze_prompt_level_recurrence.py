from __future__ import annotations

import argparse
import math
from itertools import combinations
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze prompt-level recurrence of residual regimes")
    parser.add_argument(
        "--residual-summary",
        default="outputs/static_dynamic_bridge_100_minilm/residual_summary.csv",
        help="Residual summary CSV",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/static_dynamic_bridge_100_minilm",
        help="Directory for prompt-level recurrence outputs",
    )
    return parser.parse_args()


def js_divergence(p: list[float], q: list[float]) -> float:
    def _kl(a: list[float], b: list[float]) -> float:
        total = 0.0
        for x, y in zip(a, b):
            if x > 0 and y > 0:
                total += x * math.log(x / y, 2)
        return total

    m = [(a + b) / 2.0 for a, b in zip(p, q)]
    return 0.5 * _kl(p, m) + 0.5 * _kl(q, m)


def total_variation_distance(p: list[float], q: list[float]) -> float:
    return 0.5 * sum(abs(a - b) for a, b in zip(p, q))


def build_trace_profiles(frame: pd.DataFrame) -> pd.DataFrame:
    cluster_ids = sorted(int(value) for value in frame["residual_cluster"].unique())
    rows: list[dict] = []

    grouped = frame.groupby(["trace_id", "prompt_id", "task_family", "outcome"])
    for (trace_id, prompt_id, task_family, outcome), group in grouped:
        counts = group["residual_cluster"].value_counts().to_dict()
        total = len(group)
        row = {
            "trace_id": trace_id,
            "prompt_id": prompt_id,
            "task_family": task_family,
            "outcome": outcome,
            "trial_id": group["trial_id"].iloc[0] if "trial_id" in group.columns else "",
            "n_deltas": total,
        }
        for cluster_id in cluster_ids:
            row[f"cluster_{cluster_id}"] = counts.get(cluster_id, 0) / total
        rows.append(row)

    return pd.DataFrame(rows), cluster_ids


def pairwise_prompt_distances(profiles: pd.DataFrame, cluster_ids: list[int]) -> pd.DataFrame:
    rows: list[dict] = []
    cluster_columns = [f"cluster_{cluster_id}" for cluster_id in cluster_ids]

    for left_idx, right_idx in combinations(range(len(profiles)), 2):
        left = profiles.iloc[left_idx]
        right = profiles.iloc[right_idx]
        p = [float(left[col]) for col in cluster_columns]
        q = [float(right[col]) for col in cluster_columns]
        rows.append(
            {
                "left_trace_id": left["trace_id"],
                "right_trace_id": right["trace_id"],
                "left_prompt_id": left["prompt_id"],
                "right_prompt_id": right["prompt_id"],
                "left_family": left["task_family"],
                "right_family": right["task_family"],
                "left_outcome": left["outcome"],
                "right_outcome": right["outcome"],
                "same_prompt": bool(left["prompt_id"] == right["prompt_id"]),
                "same_family": bool(left["task_family"] == right["task_family"]),
                "same_outcome": bool(left["outcome"] == right["outcome"]),
                "js_divergence": js_divergence(p, q),
                "tv_distance": total_variation_distance(p, q),
            }
        )

    return pd.DataFrame(rows)


def nearest_neighbor_purity(pairwise: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    all_trace_ids = sorted(set(pairwise["left_trace_id"]).union(set(pairwise["right_trace_id"])))

    for trace_id in all_trace_ids:
        left_rows = pairwise[pairwise["left_trace_id"] == trace_id].copy()
        left_rows = left_rows.rename(
            columns={
                "right_trace_id": "neighbor_trace_id",
                "right_family": "neighbor_family",
                "right_outcome": "neighbor_outcome",
            }
        )
        right_rows = pairwise[pairwise["right_trace_id"] == trace_id].copy()
        right_rows = right_rows.rename(
            columns={
                "left_trace_id": "neighbor_trace_id",
                "left_family": "neighbor_family",
                "left_outcome": "neighbor_outcome",
            }
        )
        merged = pd.concat(
            [
                left_rows[["js_divergence", "tv_distance", "neighbor_trace_id", "neighbor_family", "neighbor_outcome", "left_family", "left_outcome"]],
                right_rows[["js_divergence", "tv_distance", "neighbor_trace_id", "neighbor_family", "neighbor_outcome", "right_family", "right_outcome"]].rename(
                    columns={"right_family": "left_family", "right_outcome": "left_outcome"}
                ),
            ],
            ignore_index=True,
        )
        nearest = merged.sort_values("js_divergence").iloc[0]
        rows.append(
            {
                "trace_id": trace_id,
                "task_family": nearest["left_family"],
                "outcome": nearest["left_outcome"],
                "neighbor_trace_id": nearest["neighbor_trace_id"],
                "neighbor_family": nearest["neighbor_family"],
                "neighbor_outcome": nearest["neighbor_outcome"],
                "same_family_nn": bool(nearest["left_family"] == nearest["neighbor_family"]),
                "same_outcome_nn": bool(nearest["left_outcome"] == nearest["neighbor_outcome"]),
                "nn_js_divergence": float(nearest["js_divergence"]),
                "nn_tv_distance": float(nearest["tv_distance"]),
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(args.residual_summary)
    profiles, cluster_ids = build_trace_profiles(frame)
    profiles.to_csv(output_dir / "prompt_level_regime_profiles.csv", index=False)

    pairwise = pairwise_prompt_distances(profiles, cluster_ids)
    pairwise.to_csv(output_dir / "prompt_level_pairwise_distances.csv", index=False)

    grouped = (
        pairwise.groupby(["same_prompt", "same_family", "same_outcome"])[["js_divergence", "tv_distance"]]
        .mean()
        .reset_index()
    )
    grouped.to_csv(output_dir / "prompt_level_distance_summary.csv", index=False)

    same_prompt_summary = (
        pairwise[pairwise["same_family"]]
        .groupby(["left_family", "same_prompt", "same_outcome"])[["js_divergence", "tv_distance"]]
        .mean()
        .reset_index()
        .rename(columns={"left_family": "task_family"})
    )
    same_prompt_summary.to_csv(output_dir / "prompt_level_same_prompt_summary.csv", index=False)

    family_grouped = (
        pairwise[pairwise["same_family"]]
        .groupby(["left_family", "same_outcome"])[["js_divergence", "tv_distance"]]
        .mean()
        .reset_index()
        .rename(columns={"left_family": "task_family"})
    )
    family_grouped.to_csv(output_dir / "prompt_level_family_distance_summary.csv", index=False)

    nn = nearest_neighbor_purity(pairwise)
    nn.to_csv(output_dir / "prompt_level_nearest_neighbors.csv", index=False)
    nn.groupby(["task_family"])[["same_family_nn", "same_outcome_nn", "nn_js_divergence", "nn_tv_distance"]].mean().reset_index().to_csv(
        output_dir / "prompt_level_nearest_neighbor_summary.csv",
        index=False,
    )


if __name__ == "__main__":
    main()
