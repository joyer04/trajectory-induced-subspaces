from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a memo for prompt recurrence significance analysis")
    parser.add_argument(
        "--bridge-dir",
        default="outputs/static_dynamic_bridge_repeated_4x5_minilm",
        help="Bridge output directory",
    )
    parser.add_argument(
        "--output",
        default="notes/prompt_recurrence_significance_memo.md",
        help="Markdown output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bridge_dir = Path(args.bridge_dir)
    summary = pd.read_csv(bridge_dir / "prompt_recurrence_significance.csv")

    strongest = summary.sort_values(["permutation_p_value", "observed_pairwise_margin"], ascending=[True, False]).head(5)
    weakest = summary.sort_values("observed_pairwise_margin", ascending=True).head(5)

    lines: list[str] = []
    lines.append("# Prompt Recurrence Significance Memo")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "Test whether prompt-level recurrence margins remain above a shuffled-label baseline within each family/outcome group."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for _, row in summary.iterrows():
        lines.append(
            f"- `{row['task_family']}` / `{row['outcome']}`: "
            f"prompt_mean_margin={row['observed_prompt_margin']:.3f}, "
            f"pairwise_margin={row['observed_pairwise_margin']:.3f}, "
            f"CI=[{row['bootstrap_ci_low']:.3f}, {row['bootstrap_ci_high']:.3f}], "
            f"positive_prompt_share={row['positive_prompt_share']:.3f}, "
            f"perm_p={row['permutation_p_value']:.3f}, "
            f"z={row['permutation_z_score']:.3f}"
        )
    lines.append("")
    lines.append("## Strongest support")
    lines.append("")
    for _, row in strongest.iterrows():
        lines.append(
            f"- `{row['task_family']}` / `{row['outcome']}`: "
            f"pairwise_margin={row['observed_pairwise_margin']:.3f}, perm_p={row['permutation_p_value']:.3f}"
        )
    lines.append("")
    lines.append("## Weakest support")
    lines.append("")
    for _, row in weakest.iterrows():
        lines.append(
            f"- `{row['task_family']}` / `{row['outcome']}`: "
            f"pairwise_margin={row['observed_pairwise_margin']:.3f}, perm_p={row['permutation_p_value']:.3f}"
        )
    lines.append("")
    lines.append("## Reading")
    lines.append("")
    lines.append(
        "The bootstrap interval tracks the mean prompt-level margin, while the permutation test compares the observed pairwise margin against shuffled prompt labels. "
        "Positive margins with low permutation p-values indicate that same-prompt residual profiles are tighter than expected under random prompt reassignment. "
        "Negative margins or wide confidence intervals indicate unstable or multi-regime prompts."
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
