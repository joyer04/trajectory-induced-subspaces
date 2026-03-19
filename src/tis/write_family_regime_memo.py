from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a family-aware residual regime memo")
    parser.add_argument(
        "--bridge-dir",
        default="outputs/static_dynamic_bridge_100_minilm",
        help="Bridge output directory",
    )
    parser.add_argument(
        "--output",
        default="notes/family_regime_memo.md",
        help="Markdown output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bridge_dir = Path(args.bridge_dir)
    divergence = pd.read_csv(bridge_dir / "family_residual_profile_divergence.csv")
    shifts = pd.read_csv(bridge_dir / "family_residual_shift.csv")
    exemplars = pd.read_csv(bridge_dir / "family_residual_exemplars.csv")

    lines: list[str] = []
    lines.append("# Family Regime Memo")
    lines.append("")
    lines.append("## Goal")
    lines.append("")
    lines.append(
        "Characterize residual regimes inside each task family and compare how correct and incorrect traces distribute across them."
    )
    lines.append("")
    lines.append("## Family divergence")
    lines.append("")
    for _, row in divergence.iterrows():
        lines.append(
            f"- `{row['task_family']}`: TV distance={row['total_variation_distance']:.3f}, "
            f"JS divergence={row['js_divergence']:.3f}"
        )
    lines.append("")
    lines.append("## Dominant incorrect-shifted regimes")
    lines.append("")

    for task_family, family_rows in shifts.groupby("task_family"):
        top_rows = family_rows.sort_values("incorrect_minus_correct", ascending=False).head(2)
        lines.append(f"- `{task_family}`:")
        for _, row in top_rows.iterrows():
            cluster_id = int(row["residual_cluster"])
            lines.append(
                f"  cluster {cluster_id}: incorrect_minus_correct={row['incorrect_minus_correct']:.3f}, "
                f"correct={row['correct_proportion']:.3f}, incorrect={row['incorrect_proportion']:.3f}"
            )
            subset = exemplars[
                (exemplars["task_family"] == task_family)
                & (exemplars["residual_cluster"] == cluster_id)
                & (exemplars["outcome"] == "incorrect")
            ].head(2)
            for _, ex in subset.iterrows():
                lines.append(f"  exemplar: {ex['transition_text']}")
    lines.append("")
    lines.append("## Reading")
    lines.append("")
    lines.append(
        "If family-level profile divergence remains non-trivial, then failure is better described as a family-specific residual regime shift than as global off-axis noise."
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
