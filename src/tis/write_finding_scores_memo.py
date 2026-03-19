from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a memo for heuristic finding evidence scores")
    parser.add_argument(
        "--scores",
        default="outputs/finding_evidence_scores.csv",
        help="CSV file with heuristic evidence scores",
    )
    parser.add_argument(
        "--output",
        default="notes/finding_scores_memo.md",
        help="Markdown output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scores = pd.read_csv(args.scores).sort_values("evidence_score", ascending=False)

    lines: list[str] = []
    lines.append("# Finding Scores Memo")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "These are heuristic evidence scores from 0 to 100. They are not p-values or posterior probabilities. "
        "They summarize sample size, effect size, and consistency across runs."
    )
    lines.append("")
    lines.append("## Scores")
    lines.append("")
    for _, row in scores.iterrows():
        lines.append(
            f"- `{row['finding_id']}` score={row['evidence_score']:.1f}: {row['finding']} "
            f"(sample={row['sample_component']:.3f}, effect={row['effect_component']:.3f}, consistency={row['consistency_component']:.3f})"
        )
        lines.append(f"  note: {row['notes']}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
