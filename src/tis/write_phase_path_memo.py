from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a memo for phase-wise regime paths")
    parser.add_argument(
        "--bridge-dir",
        default="outputs/static_dynamic_bridge_temperature_minilm",
        help="Bridge output directory",
    )
    parser.add_argument(
        "--output",
        default="notes/phase_path_memo.md",
        help="Markdown output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bridge_dir = Path(args.bridge_dir)

    path_divergence = pd.read_csv(bridge_dir / "phase_path_divergence.csv")
    dominant = pd.read_csv(bridge_dir / "phase_path_dominant.csv")
    transitions = pd.read_csv(bridge_dir / "phase_transition_summary.csv")

    strongest = path_divergence.sort_values("path_js_divergence", ascending=False).head(10)
    lines: list[str] = []
    lines.append("# Phase Path Memo")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "Assess whether correct and incorrect traces occupy different early-to-middle-to-late residual regime paths."
    )
    lines.append("")
    lines.append("## Family path divergence")
    lines.append("")
    for _, row in strongest.iterrows():
        lines.append(
            f"- `{row['task_family']}`: "
            f"correct_path={row['correct_dominant_path']}, "
            f"incorrect_path={row['incorrect_dominant_path']}, "
            f"same_path={bool(row['same_dominant_path'])}, "
            f"path_js={row['path_js_divergence']:.3f}"
        )
    lines.append("")
    lines.append("## Dominant paths")
    lines.append("")
    for _, row in dominant.sort_values(["task_family", "outcome"]).iterrows():
        lines.append(
            f"- `{row['task_family']}` / `{row['outcome']}`: "
            f"path={row['dominant_phase_path']}, count={int(row['dominant_phase_path_count'])}"
        )
    lines.append("")
    lines.append("## Dominant transitions")
    lines.append("")
    top_transitions = (
        transitions.groupby(["task_family", "outcome", "transition"])
        .first()
        .reset_index()
        .sort_values(["task_family", "outcome", "transition"])
    )
    for _, row in top_transitions.iterrows():
        lines.append(
            f"- `{row['task_family']}` / `{row['outcome']}` / `{row['transition']}`: "
            f"{row['transition_path']} (count={int(row['count'])})"
        )
    lines.append("")
    lines.append("## Reading")
    lines.append("")
    lines.append(
        "If dominant paths diverge early, then failure may be selected near the start of reasoning. "
        "If paths only diverge in the late transition, then the regime difference is more about answer commitment than initial decomposition."
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
