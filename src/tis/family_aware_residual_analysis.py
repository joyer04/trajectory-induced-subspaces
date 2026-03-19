from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

import pandas as pd


TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9\-]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Family-aware residual regime analysis")
    parser.add_argument(
        "--residual-summary",
        default="outputs/static_dynamic_bridge_100_minilm/residual_summary.csv",
        help="Residual summary CSV",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/static_dynamic_bridge_100_minilm",
        help="Directory for family-aware outputs",
    )
    parser.add_argument(
        "--examples-per-group",
        type=int,
        default=4,
        help="Number of exemplar transitions per family/outcome/cluster",
    )
    parser.add_argument(
        "--top-terms",
        type=int,
        default=6,
        help="Number of top terms per family/outcome/cluster",
    )
    return parser.parse_args()


def total_variation_distance(p: list[float], q: list[float]) -> float:
    return 0.5 * sum(abs(a - b) for a, b in zip(p, q))


def js_divergence(p: list[float], q: list[float]) -> float:
    def _kl(a: list[float], b: list[float]) -> float:
        total = 0.0
        for x, y in zip(a, b):
            if x > 0 and y > 0:
                total += x * math.log(x / y, 2)
        return total

    m = [(a + b) / 2.0 for a, b in zip(p, q)]
    return 0.5 * _kl(p, m) + 0.5 * _kl(q, m)


def top_terms(texts: list[str], top_k: int) -> str:
    counts: dict[str, int] = {}
    for text in texts:
        for token in TOKEN_PATTERN.findall(text.lower()):
            counts[token] = counts.get(token, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:top_k]
    return ", ".join(term for term, _ in ranked)


def main() -> None:
    args = parse_args()
    frame = pd.read_csv(args.residual_summary)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    frame["transition_text"] = frame["from_step_text"].fillna("") + "  ==>  " + frame["to_step_text"].fillna("")

    distribution_rows: list[dict] = []
    shift_rows: list[dict] = []
    exemplar_rows: list[dict] = []
    profile_rows: list[dict] = []

    for task_family, family_frame in frame.groupby("task_family"):
        cluster_ids = sorted(int(value) for value in family_frame["residual_cluster"].unique())
        dist_map: dict[str, list[float]] = {}

        for outcome, outcome_frame in family_frame.groupby("outcome"):
            counts = outcome_frame["residual_cluster"].value_counts().to_dict()
            total = len(outcome_frame)
            proportions = [counts.get(cluster_id, 0) / total for cluster_id in cluster_ids]
            dist_map[outcome] = proportions

            for cluster_id in cluster_ids:
                subset = outcome_frame[outcome_frame["residual_cluster"] == cluster_id].copy()
                proportion = counts.get(cluster_id, 0) / total
                exemplar_subset = subset.sort_values(
                    ["residual_norm", "static_projection_norm"],
                    ascending=[False, True],
                ).head(args.examples_per_group)
                terms = top_terms(subset["transition_text"].tolist(), args.top_terms) if not subset.empty else ""

                distribution_rows.append(
                    {
                        "task_family": task_family,
                        "outcome": outcome,
                        "residual_cluster": cluster_id,
                        "count": int(counts.get(cluster_id, 0)),
                        "proportion": proportion,
                        "top_terms": terms,
                    }
                )

                for _, row in exemplar_subset.iterrows():
                    exemplar_rows.append(
                        {
                            "task_family": task_family,
                            "outcome": outcome,
                            "residual_cluster": cluster_id,
                            "trace_id": row["trace_id"],
                            "residual_norm": row["residual_norm"],
                            "static_projection_norm": row["static_projection_norm"],
                            "transition_text": row["transition_text"],
                        }
                    )

        correct = dist_map.get("correct", [0.0] * len(cluster_ids))
        incorrect = dist_map.get("incorrect", [0.0] * len(cluster_ids))
        profile_rows.append(
            {
                "task_family": task_family,
                "total_variation_distance": total_variation_distance(correct, incorrect),
                "js_divergence": js_divergence(correct, incorrect),
            }
        )

        for cluster_id, correct_prop, incorrect_prop in zip(cluster_ids, correct, incorrect):
            shift_rows.append(
                {
                    "task_family": task_family,
                    "residual_cluster": cluster_id,
                    "correct_proportion": correct_prop,
                    "incorrect_proportion": incorrect_prop,
                    "incorrect_minus_correct": incorrect_prop - correct_prop,
                }
            )

    pd.DataFrame(distribution_rows).to_csv(output_dir / "family_residual_distribution.csv", index=False)
    pd.DataFrame(shift_rows).sort_values(
        ["task_family", "incorrect_minus_correct"],
        ascending=[True, False],
    ).to_csv(output_dir / "family_residual_shift.csv", index=False)
    pd.DataFrame(exemplar_rows).to_csv(output_dir / "family_residual_exemplars.csv", index=False)
    pd.DataFrame(profile_rows).sort_values(
        "total_variation_distance",
        ascending=False,
    ).to_csv(output_dir / "family_residual_profile_divergence.csv", index=False)


if __name__ == "__main__":
    main()
