from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a memo for robustness-map figures")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--output", default="notes/robustness_map_memo.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.project_root)

    sig = pd.read_csv(root / "outputs/static_dynamic_bridge_repeated_8x5_minilm/prompt_recurrence_significance.csv")
    phase_div = pd.read_csv(root / "outputs/static_dynamic_bridge_temperature_minilm/step_phase_failure_divergence.csv")
    temp_margin = pd.read_csv(root / "outputs/static_dynamic_bridge_temperature_minilm/temperature_family_margin.csv")
    scores = pd.read_csv(root / "outputs/finding_evidence_scores.csv").sort_values("evidence_score", ascending=False)

    lines: list[str] = []
    lines.append("# Robustness Map Memo")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "Compress the current state of the project into a small number of scanning figures that show where each finding is strong or weak."
    )
    lines.append("")
    lines.append("## Strongest prompt-recurrence buckets")
    lines.append("")
    for _, row in sig.sort_values(["permutation_p_value", "observed_pairwise_margin"], ascending=[True, False]).head(6).iterrows():
        lines.append(
            f"- `{row['task_family']}` / `{row['outcome']}`: margin={row['observed_pairwise_margin']:.3f}, p={row['permutation_p_value']:.3f}"
        )
    lines.append("")
    lines.append("## Strongest phase divergences")
    lines.append("")
    for _, row in phase_div.sort_values("js_divergence", ascending=False).head(6).iterrows():
        lines.append(
            f"- `{row['task_family']}` / `{row['phase']}`: js={row['js_divergence']:.3f}, same_mode={bool(row['same_mode_cluster'])}"
        )
    lines.append("")
    lines.append("## Temperature sensitivity")
    lines.append("")
    for _, row in temp_margin.sort_values("temperature_margin", ascending=False).iterrows():
        lines.append(
            f"- `{row['task_family']}`: temperature_margin={row['temperature_margin']:.3f}"
        )
    lines.append("")
    lines.append("## Current evidence scores")
    lines.append("")
    for _, row in scores.iterrows():
        lines.append(
            f"- `{row['finding_id']}`: score={row['evidence_score']:.1f} ({row['finding']})"
        )
    lines.append("")
    lines.append("## Reading")
    lines.append("")
    lines.append(
        "The robustness maps are not a new theory. They are a scanning layer that tells us where the current theory seems strongest, where it still looks local, and where the next data collection should focus."
    )

    output_path = root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
