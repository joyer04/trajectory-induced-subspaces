from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd


PHASES = ["early", "middle", "late"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze phase-wise residual regime paths")
    parser.add_argument(
        "--bridge-dir",
        default="outputs/static_dynamic_bridge_temperature_minilm",
        help="Bridge output directory containing residual_summary_with_phase.csv",
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


def normalized_counts(series: pd.Series, keys: list[str]) -> list[float]:
    counts = series.value_counts(normalize=True).to_dict()
    return [float(counts.get(key, 0.0)) for key in keys]


def dominant_cluster(group: pd.DataFrame) -> int:
    counts = group["residual_cluster"].value_counts()
    return int(counts.index[0])


def main() -> None:
    args = parse_args()
    bridge_dir = Path(args.bridge_dir)
    frame = pd.read_csv(bridge_dir / "residual_summary_with_phase.csv")

    trace_rows: list[dict] = []
    transition_rows: list[dict] = []

    for trace_id, trace_frame in frame.groupby("trace_id"):
        meta = trace_frame.iloc[0]
        phase_clusters: dict[str, str] = {}
        phase_shares: dict[str, float] = {}
        for phase in PHASES:
            phase_frame = trace_frame[trace_frame["phase"] == phase]
            if phase_frame.empty:
                phase_clusters[phase] = "NA"
                phase_shares[phase] = float("nan")
                continue
            counts = phase_frame["residual_cluster"].value_counts(normalize=True)
            phase_clusters[phase] = str(int(counts.index[0]))
            phase_shares[phase] = float(counts.iloc[0])

        path = "->".join(phase_clusters[phase] for phase in PHASES)
        trace_rows.append(
            {
                "trace_id": trace_id,
                "prompt_id": meta["prompt_id"],
                "task_family": meta["task_family"],
                "outcome": meta["outcome"],
                "temperature_tag": meta.get("temperature_tag", ""),
                "early_cluster": phase_clusters["early"],
                "middle_cluster": phase_clusters["middle"],
                "late_cluster": phase_clusters["late"],
                "early_share": phase_shares["early"],
                "middle_share": phase_shares["middle"],
                "late_share": phase_shares["late"],
                "phase_path": path,
            }
        )

        for left, right in zip(PHASES[:-1], PHASES[1:]):
            if phase_clusters[left] == "NA" or phase_clusters[right] == "NA":
                continue
            transition_rows.append(
                {
                    "trace_id": trace_id,
                    "prompt_id": meta["prompt_id"],
                    "task_family": meta["task_family"],
                    "outcome": meta["outcome"],
                    "temperature_tag": meta.get("temperature_tag", ""),
                    "transition": f"{left}_to_{right}",
                    "from_cluster": phase_clusters[left],
                    "to_cluster": phase_clusters[right],
                    "transition_path": f"{phase_clusters[left]}->{phase_clusters[right]}",
                }
            )

    trace_paths = pd.DataFrame(trace_rows)
    trace_paths.to_csv(bridge_dir / "trace_phase_paths.csv", index=False)

    transitions = pd.DataFrame(transition_rows)
    transitions.to_csv(bridge_dir / "trace_phase_transitions.csv", index=False)

    path_summary = (
        trace_paths.groupby(["task_family", "outcome", "phase_path"])
        .size()
        .reset_index(name="count")
        .sort_values(["task_family", "outcome", "count"], ascending=[True, True, False])
    )
    path_summary.to_csv(bridge_dir / "phase_path_summary.csv", index=False)

    dominant_paths = (
        path_summary.groupby(["task_family", "outcome"])
        .first()
        .reset_index()
        .rename(columns={"phase_path": "dominant_phase_path", "count": "dominant_phase_path_count"})
    )
    dominant_paths.to_csv(bridge_dir / "phase_path_dominant.csv", index=False)

    divergence_rows: list[dict] = []
    for task_family, family_frame in trace_paths.groupby("task_family"):
        correct = family_frame[family_frame["outcome"] == "correct"]
        incorrect = family_frame[family_frame["outcome"] == "incorrect"]
        if correct.empty or incorrect.empty:
            continue
        path_keys = sorted(set(correct["phase_path"]).union(set(incorrect["phase_path"])))
        js = js_divergence(
            normalized_counts(correct["phase_path"], path_keys),
            normalized_counts(incorrect["phase_path"], path_keys),
        )
        divergence_rows.append(
            {
                "task_family": task_family,
                "correct_dominant_path": correct["phase_path"].mode().iloc[0],
                "incorrect_dominant_path": incorrect["phase_path"].mode().iloc[0],
                "same_dominant_path": bool(correct["phase_path"].mode().iloc[0] == incorrect["phase_path"].mode().iloc[0]),
                "path_js_divergence": js,
            }
        )
    pd.DataFrame(divergence_rows).sort_values("path_js_divergence", ascending=False).to_csv(
        bridge_dir / "phase_path_divergence.csv",
        index=False,
    )

    transition_summary = (
        transitions.groupby(["task_family", "outcome", "transition", "transition_path"])
        .size()
        .reset_index(name="count")
        .sort_values(["task_family", "outcome", "transition", "count"], ascending=[True, True, True, False])
    )
    transition_summary.to_csv(bridge_dir / "phase_transition_summary.csv", index=False)


if __name__ == "__main__":
    main()
