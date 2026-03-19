from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write an exploratory GitHub/blog-style research note")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root",
    )
    parser.add_argument(
        "--output",
        default="outputs/exploratory_research_note.md",
        help="Markdown output path",
    )
    return parser.parse_args()


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def main() -> None:
    args = parse_args()
    root = Path(args.project_root)

    finding_scores = pd.read_csv(root / "outputs/finding_evidence_scores.csv").sort_values("evidence_score", ascending=False)
    temp_analysis = json.loads((root / "data/processed_temperatures_scored_minilm/analysis_summary.json").read_text())
    repeated_8_analysis = json.loads((root / "data/processed_repeated_8x5_scored_minilm/analysis_summary.json").read_text())

    alignment = pd.read_csv(root / "outputs/static_dynamic_bridge_temperature_minilm/alignment_group_summary.csv")
    residual = pd.read_csv(root / "outputs/static_dynamic_bridge_temperature_minilm/residual_group_summary.csv")
    phase_paths = pd.read_csv(root / "outputs/static_dynamic_bridge_temperature_minilm/phase_path_divergence.csv")
    phase_predict = pd.read_csv(root / "outputs/static_dynamic_bridge_temperature_minilm/phase_predictability_summary.csv")
    temp_margin = pd.read_csv(root / "outputs/static_dynamic_bridge_temperature_minilm/temperature_family_margin.csv")
    sig_8 = pd.read_csv(root / "outputs/static_dynamic_bridge_repeated_8x5_minilm/prompt_recurrence_significance.csv")

    mean_alignment = float(alignment["best_abs_alignment"].mean())
    mean_residual = float(alignment["residual_energy"].mean())
    top_scores = finding_scores.head(4)
    top_paths = phase_paths.sort_values("path_js_divergence", ascending=False).head(5)
    top_sig = sig_8.sort_values(["permutation_p_value", "observed_pairwise_margin"], ascending=[True, False]).head(6)

    lines: list[str] = []
    lines.append("# Trajectory-Induced Subspaces: Exploratory Research Note")
    lines.append("")
    lines.append("This is not a paper draft. It is a working research note for the current state of the project.")
    lines.append("")
    lines.append("The core question is simple:")
    lines.append("")
    lines.append("> Does LLM reasoning mostly follow pre-existing semantic axes, or does the trajectory itself induce local residual structure?")
    lines.append("")
    lines.append("## Current Dataset Footprint")
    lines.append("")
    lines.append(
        f"- Temperature-conditioned run: `{temp_analysis['trace_count']}` traces, `{temp_analysis['step_count']}` steps, `{temp_analysis['delta_count']}` deltas"
    )
    lines.append(
        f"- Repeated 8x5 run: `{repeated_8_analysis['trace_count']}` traces, `{repeated_8_analysis['step_count']}` steps, `{repeated_8_analysis['delta_count']}` deltas"
    )
    lines.append("- Embedding backbone: `sentence-transformers/all-MiniLM-L6-v2`")
    lines.append("- Reasoning models: local Ollama-served models for generation and judging")
    lines.append("")
    lines.append("## The Short Version")
    lines.append("")
    lines.append(
        f"- Static top axes are weak explanatory variables for actual reasoning motion. Mean best-axis alignment is only `{fmt(mean_alignment)}`, while mean residual energy stays around `{fmt(mean_residual)}`."
    )
    lines.append(
        "- Repeated same-prompt runs are often more similar to each other than different prompts from the same family, so the residual geometry is not just noise."
    )
    lines.append(
        "- The geometry is not universal. It depends strongly on task family, outcome, and even phase of the reasoning trace."
    )
    lines.append(
        "- Temperature changes outcome mix, but it does not appear to be the dominant source of residual regime structure."
    )
    lines.append("")
    lines.append("## Evidence Scoreboard")
    lines.append("")
    lines.append("These are heuristic evidence scores, not probabilities.")
    lines.append("")
    for _, row in top_scores.iterrows():
        lines.append(
            f"- `{row['finding_id']}` `{row['evidence_score']:.1f}/100`: {row['finding']}"
        )
    lines.append("")
    lines.append("## What Looks Strong")
    lines.append("")
    lines.append("### 1. Static semantic manifold is not enough")
    lines.append("")
    lines.append(
        f"The average alignment to the best static axis remains low (`{fmt(mean_alignment)}`), while residual norms stay very high across families. "
        "That is the cleanest and most stable finding in the project right now."
    )
    lines.append("")
    lines.append("### 2. Residual structure is phase-specific")
    lines.append("")
    for _, row in top_paths.iterrows():
        lines.append(
            f"- `{row['task_family']}`: correct `{row['correct_dominant_path']}` vs incorrect `{row['incorrect_dominant_path']}` "
            f"(path JS `{fmt(row['path_js_divergence'])}`)"
        )
    lines.append("")
    lines.append(
        "This is important because it suggests failures are not just 'further away' from the manifold. "
        "They often follow different path topologies through phase space."
    )
    lines.append("")
    lines.append("### 3. Repeated prompts still matter when prompt support is widened")
    lines.append("")
    for _, row in top_sig.iterrows():
        lines.append(
            f"- `{row['task_family']}` / `{row['outcome']}`: pairwise margin `{fmt(row['observed_pairwise_margin'])}`, "
            f"`p={row['permutation_p_value']:.3f}`, prompts `{int(row['n_prompts'])}`"
        )
    lines.append("")
    lines.append(
        "This is the main reason I am comfortable saying that at least part of the residual geometry is genuinely prompt-recurrent."
    )
    lines.append("")
    lines.append("## Where The Story Gets More Interesting")
    lines.append("")
    lines.append("### Arithmetic")
    lines.append("")
    lines.append(
        "Arithmetic is not just 'harder'. Its divergence often appears early or in the middle phase. "
        "That makes it look more like an early regime-selection problem than a late answer-commitment problem."
    )
    lines.append("")
    lines.append("### Temporal Ordering")
    lines.append("")
    lines.append(
        "Temporal tasks often look more path-sensitive late in the trace. "
        "That suggests the failure may emerge when the model commits to an ordering rather than when it first decomposes the problem."
    )
    lines.append("")
    lines.append("### Causal Micro World")
    lines.append("")
    lines.append(
        "Causal tasks are surprisingly structured. Early-phase signals already carry useful information about later path and outcome."
    )
    lines.append("")
    lines.append("## Temperature: Important, But Not The Main Character")
    lines.append("")
    for _, row in temp_margin.sort_values("temperature_margin", ascending=False).iterrows():
        lines.append(
            f"- `{row['task_family']}`: same-temp JS `{fmt(row['same_temp_js'])}` vs cross-temp JS `{fmt(row['cross_temp_js'])}` "
            f"(margin `{fmt(row['temperature_margin'])}`)"
        )
    lines.append("")
    lines.append(
        "The margins are mostly small. Temperature does move the correct/incorrect ratio, but it is not the main driver of the residual regime structure."
    )
    lines.append("")
    lines.append("## A Useful Mental Model")
    lines.append("")
    lines.append(
        "Right now the project looks less like 'the model walks along a single semantic gradient' and more like this:"
    )
    lines.append("")
    lines.append("1. The prompt family constrains a coarse region of semantic space.")
    lines.append("2. The reasoning trajectory enters a local regime.")
    lines.append("3. Different outcomes correspond to different phase paths through that regime.")
    lines.append("4. Static axes explain some background organization, but not the actual motion.")
    lines.append("")
    lines.append("## What Still Looks Unsettled")
    lines.append("")
    lines.append("- Prompt recurrence is real, but not equally strong in every family/outcome bucket.")
    lines.append("- Some groups still have weak or unstable significance when prompt support grows.")
    lines.append("- The current cluster labels are useful for orientation, but they are still exploratory rather than definitive.")
    lines.append("")
    lines.append("## What I Would Do Next")
    lines.append("")
    lines.append("- Build a robustness map that shows each finding by family, outcome, temperature, and phase in one place.")
    lines.append("- Test whether early-phase regime features can predict final outcome on held-out prompts rather than held-out traces only.")
    lines.append("- Compare multiple embedding backbones on the full repeated datasets, not just the static text corpus.")
    lines.append("- Add a small interactive notebook or dashboard view for phase paths and regime transitions.")
    lines.append("")
    lines.append("## Files Worth Opening")
    lines.append("")
    lines.append(f"- [Evidence scores]({(root / 'outputs/finding_evidence_scores.csv').as_posix()})")
    lines.append(f"- [Temperature bridge outputs]({(root / 'outputs/static_dynamic_bridge_temperature_minilm').as_posix()})")
    lines.append(f"- [Repeated 8x5 bridge outputs]({(root / 'outputs/static_dynamic_bridge_repeated_8x5_minilm').as_posix()})")
    lines.append(f"- [Phase path memo]({(root / 'notes/phase_path_memo.md').as_posix()})")
    lines.append(f"- [Prompt recurrence significance memo]({(root / 'notes/prompt_recurrence_significance_repeated_8x5_memo.md').as_posix()})")
    lines.append("")
    lines.append("## Bottom Line")
    lines.append("")
    lines.append(
        "The exploratory picture is getting sharper. The strongest reading so far is that reasoning is not well described as simple static-axis following. "
        "It looks more like family-specific, phase-specific local geometry, with some regimes recurring across repeated runs and others remaining unstable."
    )

    output_path = root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
