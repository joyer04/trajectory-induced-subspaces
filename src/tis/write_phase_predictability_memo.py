from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a memo for phase-path predictability")
    parser.add_argument(
        "--bridge-dir",
        default="outputs/static_dynamic_bridge_temperature_minilm",
        help="Bridge output directory",
    )
    parser.add_argument(
        "--output",
        default="notes/phase_predictability_memo.md",
        help="Markdown output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bridge_dir = Path(args.bridge_dir)
    predictability = pd.read_csv(bridge_dir / "phase_predictability_summary.csv")
    late = pd.read_csv(bridge_dir / "late_cluster_predictability.csv")

    lines: list[str] = []
    lines.append("# Phase Predictability Memo")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append("Estimate how early regime information predicts later paths and final outcome.")
    lines.append("")
    lines.append("## Outcome predictability")
    lines.append("")
    for _, row in predictability.sort_values(["task_family", "feature_set"]).iterrows():
        lines.append(
            f"- `{row['task_family']}` / `{row['feature_set']}`: "
            f"accuracy={row['cv_accuracy']:.3f}, balanced_accuracy={row['cv_balanced_accuracy']:.3f}"
        )
    lines.append("")
    lines.append("## Late-cluster rule accuracy")
    lines.append("")
    for _, row in late.sort_values(["task_family", "feature_set"]).iterrows():
        lines.append(
            f"- `{row['task_family']}` / `{row['feature_set']}`: "
            f"late_cluster_accuracy={row['late_cluster_rule_accuracy']:.3f}"
        )
    lines.append("")
    lines.append("## Reading")
    lines.append("")
    lines.append(
        "If early-only features already predict outcome well, the regime is being selected near the start of reasoning. "
        "If early-middle is much stronger than early-only, the decisive branching happens during the transition to the middle phase."
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
