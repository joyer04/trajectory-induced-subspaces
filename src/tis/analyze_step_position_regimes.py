from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze residual regimes by reasoning-step position")
    parser.add_argument(
        "--bridge-dir",
        default="outputs/static_dynamic_bridge_temperature_minilm",
        help="Bridge output directory containing residual_summary.csv",
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


def phase_from_ratio(value: float) -> str:
    if value <= 1 / 3:
        return "early"
    if value <= 2 / 3:
        return "middle"
    return "late"


def cluster_profile(frame: pd.DataFrame, cluster_ids: list[int]) -> list[float]:
    counts = frame["residual_cluster"].value_counts(normalize=True).to_dict()
    return [float(counts.get(cluster_id, 0.0)) for cluster_id in cluster_ids]


def main() -> None:
    args = parse_args()
    bridge_dir = Path(args.bridge_dir)
    residual = pd.read_csv(bridge_dir / "residual_summary.csv")

    trace_lengths = (
        residual.groupby("trace_id")["to_step_position"]
        .max()
        .rename("max_to_step_position")
        .reset_index()
    )
    frame = residual.merge(trace_lengths, on="trace_id", how="left")
    frame["position_ratio"] = frame["to_step_position"] / frame["max_to_step_position"].clip(lower=1)
    frame["phase"] = frame["position_ratio"].apply(phase_from_ratio)
    frame.to_csv(bridge_dir / "residual_summary_with_phase.csv", index=False)

    phase_summary = (
        frame.groupby(["task_family", "outcome", "phase"])[["static_projection_norm", "residual_norm"]]
        .mean()
        .reset_index()
    )
    phase_summary.to_csv(bridge_dir / "step_phase_summary.csv", index=False)

    cluster_counts = (
        frame.groupby(["task_family", "outcome", "phase", "residual_cluster"])
        .size()
        .reset_index(name="count")
    )
    cluster_counts.to_csv(bridge_dir / "step_phase_cluster_counts.csv", index=False)

    cluster_ids = sorted(int(value) for value in frame["residual_cluster"].unique())
    divergence_rows: list[dict] = []
    for (task_family, phase), group in frame.groupby(["task_family", "phase"]):
        correct = group[group["outcome"] == "correct"]
        incorrect = group[group["outcome"] == "incorrect"]
        if correct.empty or incorrect.empty:
            continue
        p = cluster_profile(correct, cluster_ids)
        q = cluster_profile(incorrect, cluster_ids)
        divergence_rows.append(
            {
                "task_family": task_family,
                "phase": phase,
                "correct_count": int(len(correct)),
                "incorrect_count": int(len(incorrect)),
                "correct_mode_cluster": int(correct["residual_cluster"].mode().iloc[0]),
                "incorrect_mode_cluster": int(incorrect["residual_cluster"].mode().iloc[0]),
                "same_mode_cluster": bool(int(correct["residual_cluster"].mode().iloc[0]) == int(incorrect["residual_cluster"].mode().iloc[0])),
                "js_divergence": js_divergence(p, q),
                "tv_distance": total_variation_distance(p, q),
                "correct_residual_norm_mean": float(correct["residual_norm"].mean()),
                "incorrect_residual_norm_mean": float(incorrect["residual_norm"].mean()),
                "residual_norm_gap": float(incorrect["residual_norm"].mean() - correct["residual_norm"].mean()),
            }
        )
    pd.DataFrame(divergence_rows).sort_values(["js_divergence", "tv_distance"], ascending=False).to_csv(
        bridge_dir / "step_phase_failure_divergence.csv",
        index=False,
    )

    prompt_phase_rows: list[dict] = []
    for (prompt_id, outcome, phase), group in frame.groupby(["prompt_id", "outcome", "phase"]):
        counts = group["residual_cluster"].value_counts(normalize=True)
        prompt_phase_rows.append(
            {
                "prompt_id": prompt_id,
                "task_family": str(group["task_family"].iloc[0]),
                "outcome": outcome,
                "phase": phase,
                "n_deltas": int(len(group)),
                "phase_entropy": float(-sum(v * math.log(v, 2) for v in counts if v > 0)),
                "dominant_cluster": int(counts.idxmax()),
                "dominant_cluster_share": float(counts.max()),
            }
        )
    pd.DataFrame(prompt_phase_rows).sort_values(["task_family", "prompt_id", "phase", "outcome"]).to_csv(
        bridge_dir / "prompt_phase_regime_summary.csv",
        index=False,
    )


if __name__ == "__main__":
    main()
