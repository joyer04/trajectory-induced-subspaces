from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a memo for prompt-level stability analysis")
    parser.add_argument(
        "--bridge-dir",
        default="outputs/static_dynamic_bridge_repeated_4x5_minilm",
        help="Bridge output directory with prompt stability CSVs",
    )
    parser.add_argument(
        "--output",
        default="notes/prompt_stability_memo.md",
        help="Markdown output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bridge_dir = Path(args.bridge_dir)

    overall = pd.read_csv(bridge_dir / "prompt_stability_overall.csv").iloc[0]
    family = pd.read_csv(bridge_dir / "family_prompt_stability_summary.csv")
    prompts = pd.read_csv(bridge_dir / "prompt_stability_summary.csv")
    consistency = pd.read_csv(bridge_dir / "prompt_outcome_consistency.csv")

    strongest = prompts.sort_values("js_margin", ascending=False).head(5)
    weakest = prompts.sort_values("js_margin", ascending=True).head(5)
    unstable_outcomes = consistency.sort_values(["dominant_outcome_share", "outcome_entropy"], ascending=[True, False]).head(5)

    lines: list[str] = []
    lines.append("# Prompt Stability Memo")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "Assess whether residual regimes are stable at the prompt level, not just at the family level."
    )
    lines.append("")
    lines.append("## Overall")
    lines.append("")
    lines.append(
        f"- mean within-prompt JS: {overall['mean_within_prompt_js']:.3f}"
    )
    lines.append(
        f"- mean same-family between-prompt JS: {overall['mean_between_prompt_js']:.3f}"
    )
    lines.append(
        f"- mean JS margin (between - within): {overall['mean_js_margin']:.3f}"
    )
    lines.append(
        f"- mean JS ratio (within / between): {overall['mean_js_ratio']:.3f}"
    )
    lines.append(
        f"- mean centroid entropy: {overall['mean_centroid_entropy']:.3f}"
    )
    lines.append(
        f"- mean dominant residual-cluster share: {overall['mean_dominant_cluster_share']:.3f}"
    )
    lines.append(
        f"- mean dominant outcome share: {overall['mean_dominant_outcome_share']:.3f}"
    )
    lines.append("")
    lines.append("## Family summary")
    lines.append("")
    for _, row in family.sort_values("js_margin", ascending=False).iterrows():
        lines.append(
            f"- `{row['task_family']}` / `{row['outcome']}`: "
            f"within_js={row['within_prompt_js']:.3f}, "
            f"between_js={row['between_prompt_js']:.3f}, "
            f"margin={row['js_margin']:.3f}, "
            f"ratio={row['js_ratio']:.3f}, "
            f"cluster_share={row['dominant_cluster_share']:.3f}"
        )
    lines.append("")
    lines.append("## Strongest prompt-level recurrence")
    lines.append("")
    for _, row in strongest.iterrows():
        lines.append(
            f"- `{row['prompt_id']}` / `{row['task_family']}` / `{row['outcome']}`: "
            f"margin={row['js_margin']:.3f}, ratio={row['js_ratio']:.3f}, "
            f"entropy={row['centroid_entropy']:.3f}, dominant_cluster={row['dominant_cluster']}"
        )
    lines.append("")
    lines.append("## Weakest prompt-level recurrence")
    lines.append("")
    for _, row in weakest.iterrows():
        lines.append(
            f"- `{row['prompt_id']}` / `{row['task_family']}` / `{row['outcome']}`: "
            f"margin={row['js_margin']:.3f}, ratio={row['js_ratio']:.3f}, "
            f"entropy={row['centroid_entropy']:.3f}, dominant_cluster={row['dominant_cluster']}"
        )
    lines.append("")
    lines.append("## Outcome consistency")
    lines.append("")
    for _, row in unstable_outcomes.iterrows():
        lines.append(
            f"- `{row['prompt_id']}` / `{row['task_family']}`: "
            f"dominant_outcome={row['dominant_outcome']}, "
            f"share={row['dominant_outcome_share']:.3f}, "
            f"entropy={row['outcome_entropy']:.3f}"
        )
    lines.append("")
    lines.append("## Reading")
    lines.append("")
    lines.append(
        "A positive JS margin means same-prompt trials are closer to each other than to different prompts in the same family and outcome. "
        "A lower JS ratio means tighter prompt-level recurrence. "
        "High centroid entropy means the prompt spreads across several residual regimes even when it recurs."
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
