from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a prompt-level recurrence memo")
    parser.add_argument(
        "--bridge-dir",
        default="outputs/static_dynamic_bridge_100_minilm",
        help="Bridge output directory",
    )
    parser.add_argument(
        "--output",
        default="notes/prompt_recurrence_memo.md",
        help="Markdown output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bridge_dir = Path(args.bridge_dir)

    global_summary = pd.read_csv(bridge_dir / "prompt_level_distance_summary.csv")
    family_summary = pd.read_csv(bridge_dir / "prompt_level_family_distance_summary.csv")
    same_prompt_summary = pd.read_csv(bridge_dir / "prompt_level_same_prompt_summary.csv")
    nn_summary = pd.read_csv(bridge_dir / "prompt_level_nearest_neighbor_summary.csv")

    lines: list[str] = []
    lines.append("# Prompt Recurrence Memo")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "Assess whether different prompts within the same task family converge toward similar residual-regime profiles."
    )
    lines.append("")
    lines.append("## Global distance summary")
    lines.append("")
    for _, row in global_summary.iterrows():
        lines.append(
            f"- same_prompt={bool(row['same_prompt'])}, same_family={bool(row['same_family'])}, same_outcome={bool(row['same_outcome'])}: "
            f"mean_js={row['js_divergence']:.3f}, mean_tv={row['tv_distance']:.3f}"
        )
    lines.append("")
    lines.append("## Same-prompt vs different-prompt inside family")
    lines.append("")
    for _, row in same_prompt_summary.iterrows():
        lines.append(
            f"- `{row['task_family']}` / same_prompt={bool(row['same_prompt'])}, same_outcome={bool(row['same_outcome'])}: "
            f"mean_js={row['js_divergence']:.3f}, mean_tv={row['tv_distance']:.3f}"
        )
    lines.append("")
    lines.append("## Family-level recurrence")
    lines.append("")
    for _, row in family_summary.iterrows():
        lines.append(
            f"- `{row['task_family']}` / same_outcome={bool(row['same_outcome'])}: "
            f"mean_js={row['js_divergence']:.3f}, mean_tv={row['tv_distance']:.3f}"
        )
    lines.append("")
    lines.append("## Nearest-neighbor purity")
    lines.append("")
    for _, row in nn_summary.iterrows():
        lines.append(
            f"- `{row['task_family']}`: "
            f"same_family_nn={row['same_family_nn']:.3f}, "
            f"same_outcome_nn={row['same_outcome_nn']:.3f}, "
            f"nn_js={row['nn_js_divergence']:.3f}"
        )
    lines.append("")
    lines.append("## Reading")
    lines.append("")
    lines.append(
        "If same-family prompt pairs are consistently closer than cross-family pairs, "
        "and nearest-neighbor purity stays above chance, then residual regimes are not just artifacts of one prompt."
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
