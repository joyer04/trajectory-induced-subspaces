from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze prompt-level residual regime stability")
    parser.add_argument(
        "--bridge-dir",
        default="outputs/static_dynamic_bridge_repeated_4x5_minilm",
        help="Bridge output directory with prompt-level recurrence files",
    )
    return parser.parse_args()


def entropy(values: list[float]) -> float:
    total = 0.0
    for value in values:
        if value > 0:
            total -= value * math.log(value, 2)
    return total


def mean_or_nan(series: pd.Series) -> float:
    if series.empty:
        return float("nan")
    return float(series.mean())


def main() -> None:
    args = parse_args()
    bridge_dir = Path(args.bridge_dir)

    profiles = pd.read_csv(bridge_dir / "prompt_level_regime_profiles.csv")
    pairwise = pd.read_csv(bridge_dir / "prompt_level_pairwise_distances.csv")
    cluster_columns = sorted(col for col in profiles.columns if col.startswith("cluster_"))

    prompt_rows: list[dict] = []
    outcome_rows: list[dict] = []

    for prompt_id, prompt_frame in profiles.groupby("prompt_id"):
        task_family = str(prompt_frame["task_family"].iloc[0])
        outcome_counts = prompt_frame["outcome"].value_counts(normalize=True).sort_index()
        prompt_outcome_entropy = entropy(outcome_counts.tolist())
        dominant_outcome = str(prompt_frame["outcome"].mode().iloc[0])
        dominant_outcome_share = float(prompt_frame["outcome"].value_counts(normalize=True).max())

        outcome_rows.append(
            {
                "prompt_id": prompt_id,
                "task_family": task_family,
                "n_trials": int(len(prompt_frame)),
                "outcome_entropy": prompt_outcome_entropy,
                "dominant_outcome": dominant_outcome,
                "dominant_outcome_share": dominant_outcome_share,
            }
        )

        for outcome, profile_group in prompt_frame.groupby("outcome"):
            trace_ids = set(profile_group["trace_id"])
            within = pairwise[
                pairwise["left_trace_id"].isin(trace_ids) & pairwise["right_trace_id"].isin(trace_ids)
            ]
            between = pairwise[
                (
                    pairwise["left_prompt_id"].eq(prompt_id)
                    | pairwise["right_prompt_id"].eq(prompt_id)
                )
                & pairwise["same_family"]
                & pairwise["same_outcome"]
                & ~pairwise["same_prompt"]
            ]

            centroid = profile_group[cluster_columns].mean()
            dominant_cluster = str(centroid.idxmax()).replace("cluster_", "")
            dominant_share = float(centroid.max())

            within_js = mean_or_nan(within["js_divergence"])
            between_js = mean_or_nan(between["js_divergence"])
            within_tv = mean_or_nan(within["tv_distance"])
            between_tv = mean_or_nan(between["tv_distance"])

            prompt_rows.append(
                {
                    "prompt_id": prompt_id,
                    "task_family": task_family,
                    "outcome": outcome,
                    "n_trials": int(len(profile_group)),
                    "within_prompt_js": within_js,
                    "between_prompt_js": between_js,
                    "js_margin": float(between_js - within_js) if not np.isnan(between_js) and not np.isnan(within_js) else float("nan"),
                    "js_ratio": float(within_js / between_js) if not np.isnan(between_js) and between_js > 0 and not np.isnan(within_js) else float("nan"),
                    "within_prompt_tv": within_tv,
                    "between_prompt_tv": between_tv,
                    "tv_margin": float(between_tv - within_tv) if not np.isnan(between_tv) and not np.isnan(within_tv) else float("nan"),
                    "tv_ratio": float(within_tv / between_tv) if not np.isnan(between_tv) and between_tv > 0 and not np.isnan(within_tv) else float("nan"),
                    "centroid_entropy": entropy(centroid.tolist()),
                    "dominant_cluster": dominant_cluster,
                    "dominant_cluster_share": dominant_share,
                }
            )

    prompt_summary = pd.DataFrame(prompt_rows).sort_values(["task_family", "prompt_id", "outcome"])
    prompt_summary.to_csv(bridge_dir / "prompt_stability_summary.csv", index=False)

    outcome_summary = pd.DataFrame(outcome_rows).sort_values(["task_family", "prompt_id"])
    outcome_summary.to_csv(bridge_dir / "prompt_outcome_consistency.csv", index=False)

    family_summary = (
        prompt_summary.groupby(["task_family", "outcome"])[
            ["within_prompt_js", "between_prompt_js", "js_margin", "js_ratio", "centroid_entropy", "dominant_cluster_share"]
        ]
        .mean()
        .reset_index()
    )
    family_summary.to_csv(bridge_dir / "family_prompt_stability_summary.csv", index=False)

    overall = pd.DataFrame(
        [
            {
                "mean_within_prompt_js": float(prompt_summary["within_prompt_js"].mean()),
                "mean_between_prompt_js": float(prompt_summary["between_prompt_js"].mean()),
                "mean_js_margin": float(prompt_summary["js_margin"].mean()),
                "mean_js_ratio": float(prompt_summary["js_ratio"].mean()),
                "mean_centroid_entropy": float(prompt_summary["centroid_entropy"].mean()),
                "mean_dominant_cluster_share": float(prompt_summary["dominant_cluster_share"].mean()),
                "mean_dominant_outcome_share": float(outcome_summary["dominant_outcome_share"].mean()),
            }
        ]
    )
    overall.to_csv(bridge_dir / "prompt_stability_overall.csv", index=False)


if __name__ == "__main__":
    main()
