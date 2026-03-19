from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a memo for temperature-conditioned prompt stability")
    parser.add_argument(
        "--bridge-dir",
        default="outputs/static_dynamic_bridge_temperature_minilm",
        help="Bridge output directory",
    )
    parser.add_argument(
        "--output",
        default="notes/temperature_stability_memo.md",
        help="Markdown output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bridge_dir = Path(args.bridge_dir)

    summary = pd.read_csv(bridge_dir / "temperature_pairwise_summary.csv")
    family_margin = pd.read_csv(bridge_dir / "temperature_family_margin.csv")
    outcome_mix = pd.read_csv(bridge_dir / "temperature_outcome_mix.csv")

    strongest = family_margin.sort_values("temperature_margin", ascending=False).head(5)
    weakest = family_margin.sort_values("temperature_margin", ascending=True).head(5)

    outcome_digest = (
        outcome_mix.groupby(["temperature_tag", "outcome"])["share"]
        .mean()
        .reset_index()
        .sort_values(["temperature_tag", "outcome"])
    )

    lines: list[str] = []
    lines.append("# Temperature Stability Memo")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "Measure how much prompt-level residual recurrence survives when generation temperature changes."
    )
    lines.append("")
    lines.append("## Global pairwise summary")
    lines.append("")
    for _, row in summary.iterrows():
        lines.append(
            f"- same_prompt={bool(row['same_prompt'])}, same_family={bool(row['same_family'])}, "
            f"same_outcome={bool(row['same_outcome'])}, same_temperature={bool(row['same_temperature'])}: "
            f"mean_js={row['js_divergence']:.3f}, mean_tv={row['tv_distance']:.3f}"
        )
    lines.append("")
    lines.append("## Family temperature margins")
    lines.append("")
    for _, row in strongest.iterrows():
        lines.append(
            f"- `{row['task_family']}`: same_temp_js={row['same_temp_js']:.3f}, "
            f"cross_temp_js={row['cross_temp_js']:.3f}, margin={row['temperature_margin']:.3f}"
        )
    lines.append("")
    lines.append("## Weakest temperature margins")
    lines.append("")
    for _, row in weakest.iterrows():
        lines.append(
            f"- `{row['task_family']}`: same_temp_js={row['same_temp_js']:.3f}, "
            f"cross_temp_js={row['cross_temp_js']:.3f}, margin={row['temperature_margin']:.3f}"
        )
    lines.append("")
    lines.append("## Outcome mix by temperature")
    lines.append("")
    for _, row in outcome_digest.iterrows():
        lines.append(
            f"- temp={row['temperature_tag']}, outcome={row['outcome']}: mean_share={row['share']:.3f}"
        )
    lines.append("")
    lines.append("## Reading")
    lines.append("")
    lines.append(
        "A positive temperature margin means same-prompt traces are more similar when sampled at the same temperature than when pooled across temperatures. "
        "If this margin is large, some of the residual regime signal is temperature-sensitive rather than fully prompt-intrinsic."
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
