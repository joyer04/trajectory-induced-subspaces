from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze temperature sensitivity of prompt-level residual regimes")
    parser.add_argument(
        "--bridge-dir",
        default="outputs/static_dynamic_bridge_temperature_minilm",
        help="Bridge output directory containing residual summary",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bridge_dir = Path(args.bridge_dir)
    residual = pd.read_csv(bridge_dir / "residual_summary.csv")
    pairwise = pd.read_csv(bridge_dir / "prompt_level_pairwise_distances.csv")

    trace_meta = residual[["trace_id", "prompt_id", "task_family", "outcome", "temperature", "temperature_tag"]].drop_duplicates()
    pairwise = pairwise.merge(
        trace_meta.rename(
            columns={
                "trace_id": "left_trace_id",
                "temperature": "left_temperature",
                "temperature_tag": "left_temperature_tag",
            }
        ),
        on="left_trace_id",
        how="left",
    )
    pairwise = pairwise.merge(
        trace_meta.rename(
            columns={
                "trace_id": "right_trace_id",
                "temperature": "right_temperature",
                "temperature_tag": "right_temperature_tag",
            }
        ),
        on="right_trace_id",
        how="left",
    )
    pairwise["same_temperature"] = pairwise["left_temperature_tag"] == pairwise["right_temperature_tag"]

    summary = (
        pairwise.groupby(["same_prompt", "same_family", "same_outcome", "same_temperature"])[["js_divergence", "tv_distance"]]
        .mean()
        .reset_index()
    )
    summary.to_csv(bridge_dir / "temperature_pairwise_summary.csv", index=False)

    same_prompt_same_outcome = pairwise[
        pairwise["same_prompt"] & pairwise["same_family"] & pairwise["same_outcome"]
    ]
    temperature_effect = (
        same_prompt_same_outcome.groupby(["left_family", "same_temperature"])[["js_divergence", "tv_distance"]]
        .mean()
        .reset_index()
        .rename(columns={"left_family": "task_family"})
    )
    temperature_effect.to_csv(bridge_dir / "temperature_same_prompt_summary.csv", index=False)

    family_rows: list[dict] = []
    for task_family, group in same_prompt_same_outcome.groupby("left_family"):
        same_temp = group[group["same_temperature"]]["js_divergence"]
        cross_temp = group[~group["same_temperature"]]["js_divergence"]
        if same_temp.empty or cross_temp.empty:
            continue
        family_rows.append(
            {
                "task_family": task_family,
                "same_temp_js": float(same_temp.mean()),
                "cross_temp_js": float(cross_temp.mean()),
                "temperature_margin": float(cross_temp.mean() - same_temp.mean()),
                "same_temp_tv": float(group[group["same_temperature"]]["tv_distance"].mean()),
                "cross_temp_tv": float(group[~group["same_temperature"]]["tv_distance"].mean()),
            }
        )
    pd.DataFrame(family_rows).sort_values("temperature_margin", ascending=False).to_csv(
        bridge_dir / "temperature_family_margin.csv",
        index=False,
    )

    outcome_stability = (
        trace_meta.groupby(["prompt_id", "temperature_tag"])["outcome"]
        .value_counts(normalize=True)
        .rename("share")
        .reset_index()
    )
    outcome_stability.to_csv(bridge_dir / "temperature_outcome_mix.csv", index=False)


if __name__ == "__main__":
    main()
