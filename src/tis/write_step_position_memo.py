from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a memo for step-position-aware regime analysis")
    parser.add_argument(
        "--bridge-dir",
        default="outputs/static_dynamic_bridge_temperature_minilm",
        help="Bridge output directory",
    )
    parser.add_argument(
        "--output",
        default="notes/step_position_regime_memo.md",
        help="Markdown output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bridge_dir = Path(args.bridge_dir)

    phase_summary = pd.read_csv(bridge_dir / "step_phase_summary.csv")
    phase_divergence = pd.read_csv(bridge_dir / "step_phase_failure_divergence.csv")
    prompt_phase = pd.read_csv(bridge_dir / "prompt_phase_regime_summary.csv")

    strongest = phase_divergence.sort_values(["js_divergence", "tv_distance"], ascending=False).head(10)
    phase_order = {"early": 0, "middle": 1, "late": 2}
    phase_means = (
        phase_summary.groupby("phase")[["static_projection_norm", "residual_norm"]]
        .mean()
        .reset_index()
        .sort_values("phase", key=lambda s: s.map(phase_order))
    )
    concentrated = prompt_phase.sort_values(["dominant_cluster_share", "phase_entropy"], ascending=[False, True]).head(10)

    lines: list[str] = []
    lines.append("# Step Position Regime Memo")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "Assess whether residual geometry changes across early, middle, and late reasoning transitions."
    )
    lines.append("")
    lines.append("## Global phase means")
    lines.append("")
    for _, row in phase_means.iterrows():
        lines.append(
            f"- `{row['phase']}`: "
            f"mean_static_projection={row['static_projection_norm']:.3f}, "
            f"mean_residual_norm={row['residual_norm']:.3f}"
        )
    lines.append("")
    lines.append("## Strongest failure-regime divergences by phase")
    lines.append("")
    for _, row in strongest.iterrows():
        lines.append(
            f"- `{row['task_family']}` / `{row['phase']}`: "
            f"js={row['js_divergence']:.3f}, tv={row['tv_distance']:.3f}, "
            f"correct_mode={int(row['correct_mode_cluster'])}, incorrect_mode={int(row['incorrect_mode_cluster'])}, "
            f"same_mode={bool(row['same_mode_cluster'])}"
        )
    lines.append("")
    lines.append("## Most concentrated prompt-phase regimes")
    lines.append("")
    for _, row in concentrated.iterrows():
        lines.append(
            f"- `{row['prompt_id']}` / `{row['task_family']}` / `{row['phase']}` / `{row['outcome']}`: "
            f"cluster={int(row['dominant_cluster'])}, share={row['dominant_cluster_share']:.3f}, "
            f"entropy={row['phase_entropy']:.3f}"
        )
    lines.append("")
    lines.append("## Reading")
    lines.append("")
    lines.append(
        "If late-phase divergences dominate, then residual geometry may be tied to convergence and answer commitment. "
        "If early-phase divergences dominate, then the regime is being selected near the start of reasoning."
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
