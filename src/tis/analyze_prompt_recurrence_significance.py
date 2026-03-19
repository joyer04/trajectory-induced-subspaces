from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assess statistical support for prompt-level recurrence")
    parser.add_argument(
        "--bridge-dir",
        default="outputs/static_dynamic_bridge_repeated_4x5_minilm",
        help="Bridge output directory with prompt stability files",
    )
    parser.add_argument("--bootstrap-iters", type=int, default=2000)
    parser.add_argument("--permutations", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=7)
    return parser.parse_args()


def compute_margin(pairwise: pd.DataFrame, labels: dict[str, str]) -> float:
    frame = pairwise.copy()
    frame["left_label"] = frame["left_trace_id"].map(labels)
    frame["right_label"] = frame["right_trace_id"].map(labels)
    within = frame[frame["left_label"] == frame["right_label"]]["js_divergence"]
    between = frame[frame["left_label"] != frame["right_label"]]["js_divergence"]
    if within.empty or between.empty:
        return float("nan")
    return float(between.mean() - within.mean())


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator, iterations: int) -> tuple[float, float]:
    if len(values) == 0:
        return float("nan"), float("nan")
    samples = []
    for _ in range(iterations):
        draw = rng.choice(values, size=len(values), replace=True)
        samples.append(float(draw.mean()))
    lower, upper = np.percentile(samples, [2.5, 97.5])
    return float(lower), float(upper)


def main() -> None:
    args = parse_args()
    rng = np.random.default_rng(args.seed)
    bridge_dir = Path(args.bridge_dir)

    profiles = pd.read_csv(bridge_dir / "prompt_level_regime_profiles.csv")
    pairwise = pd.read_csv(bridge_dir / "prompt_level_pairwise_distances.csv")
    prompt_stability = pd.read_csv(bridge_dir / "prompt_stability_summary.csv")

    rows: list[dict] = []
    for (task_family, outcome), profile_group in profiles.groupby(["task_family", "outcome"]):
        prompt_ids = sorted(profile_group["prompt_id"].unique())
        if len(prompt_ids) < 2:
            continue

        trace_ids = set(profile_group["trace_id"])
        group_pairwise = pairwise[
            pairwise["left_trace_id"].isin(trace_ids) & pairwise["right_trace_id"].isin(trace_ids)
        ].copy()
        labels = dict(zip(profile_group["trace_id"], profile_group["prompt_id"]))
        prompt_values = prompt_stability[
            (prompt_stability["task_family"] == task_family) & (prompt_stability["outcome"] == outcome)
        ]["js_margin"].dropna().to_numpy()
        if len(prompt_values) == 0:
            continue
        observed_prompt_margin = float(prompt_values.mean())
        ci_low, ci_high = bootstrap_ci(prompt_values, rng, args.bootstrap_iters)
        observed_pairwise_margin = compute_margin(group_pairwise, labels)

        permuted_margins = []
        shuffled_labels = profile_group["prompt_id"].to_numpy().copy()
        trace_order = profile_group["trace_id"].tolist()
        for _ in range(args.permutations):
            rng.shuffle(shuffled_labels)
            perm_labels = dict(zip(trace_order, shuffled_labels))
            permuted_margins.append(compute_margin(group_pairwise, perm_labels))

        permuted = np.asarray([value for value in permuted_margins if not np.isnan(value)], dtype=float)
        if len(permuted) == 0:
            continue

        p_value = float((1 + np.sum(permuted >= observed_pairwise_margin)) / (len(permuted) + 1))
        null_mean = float(permuted.mean())
        null_std = float(permuted.std(ddof=0))
        z_score = float((observed_pairwise_margin - null_mean) / null_std) if null_std > 0 else float("nan")

        rows.append(
            {
                "task_family": task_family,
                "outcome": outcome,
                "n_prompts": int(len(prompt_ids)),
                "n_traces": int(len(profile_group)),
                "observed_prompt_margin": observed_prompt_margin,
                "observed_pairwise_margin": observed_pairwise_margin,
                "bootstrap_ci_low": ci_low,
                "bootstrap_ci_high": ci_high,
                "positive_prompt_share": float(np.mean(prompt_values > 0)),
                "permutation_null_mean": null_mean,
                "permutation_null_std": null_std,
                "permutation_p_value": p_value,
                "permutation_z_score": z_score,
            }
        )

    summary = pd.DataFrame(rows).sort_values(["permutation_p_value", "observed_pairwise_margin"], ascending=[True, False])
    summary.to_csv(bridge_dir / "prompt_recurrence_significance.csv", index=False)


if __name__ == "__main__":
    main()
