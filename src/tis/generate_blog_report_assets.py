from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate blog-report figures and markdown")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--docs-dir", default="docs")
    return parser.parse_args()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_figure(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches="tight")
    plt.close()


def main() -> None:
    args = parse_args()
    root = Path(args.project_root)
    docs_dir = ensure_dir(root / args.docs_dir)
    assets_dir = ensure_dir(docs_dir / "assets")

    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.facecolor"] = "#fffdf8"
    plt.rcParams["axes.facecolor"] = "#fffdf8"
    plt.rcParams["savefig.facecolor"] = "#fffdf8"

    finding_scores = pd.read_csv(root / "outputs/finding_evidence_scores.csv").sort_values("evidence_score")
    alignment = pd.read_csv(root / "outputs/static_dynamic_bridge_temperature_minilm/alignment_group_summary.csv")
    phase_div = pd.read_csv(root / "outputs/static_dynamic_bridge_temperature_minilm/phase_path_divergence.csv").sort_values("path_js_divergence")
    prompt_sig = pd.read_csv(root / "outputs/static_dynamic_bridge_repeated_8x5_minilm/prompt_recurrence_significance.csv").sort_values("observed_pairwise_margin")
    temp_margin = pd.read_csv(root / "outputs/static_dynamic_bridge_temperature_minilm/temperature_family_margin.csv").sort_values("temperature_margin")
    phase_pred = pd.read_csv(root / "outputs/static_dynamic_bridge_temperature_minilm/phase_predictability_summary.csv")
    temp_analysis = json.loads((root / "data/processed_temperatures_scored_minilm/analysis_summary.json").read_text())
    repeated_analysis = json.loads((root / "data/processed_repeated_8x5_scored_minilm/analysis_summary.json").read_text())

    fig1 = assets_dir / "evidence_scores.png"
    plt.figure(figsize=(10, 4.8))
    ax = sns.barplot(data=finding_scores, x="evidence_score", y="finding_id", hue="finding_id", dodge=False, palette="flare", legend=False)
    ax.set_title("Heuristic Evidence Scores for Current Findings", fontsize=15, pad=12)
    ax.set_xlabel("Evidence score (0-100)")
    ax.set_ylabel("")
    for idx, row in finding_scores.reset_index(drop=True).iterrows():
        ax.text(row["evidence_score"] + 1.0, idx, f"{row['finding_id']}  {row['evidence_score']:.1f}", va="center", fontsize=11)
    save_figure(fig1)

    fig2 = assets_dir / "static_vs_residual.png"
    plt.figure(figsize=(10, 5.2))
    melted = alignment.melt(
        id_vars=["task_family", "outcome"],
        value_vars=["best_abs_alignment", "residual_energy"],
        var_name="metric",
        value_name="value",
    )
    ax = sns.barplot(data=melted, x="task_family", y="value", hue="metric", palette=["#c4542d", "#2f6f8f"])
    ax.set_title("Static Axis Alignment Stays Small While Residual Energy Stays High", fontsize=15, pad=12)
    ax.set_xlabel("")
    ax.set_ylabel("Mean value")
    ax.tick_params(axis="x", rotation=20)
    save_figure(fig2)

    fig3 = assets_dir / "phase_path_divergence.png"
    plt.figure(figsize=(10, 5))
    ax = sns.barplot(data=phase_div, x="path_js_divergence", y="task_family", hue="task_family", dodge=False, palette="crest", legend=False)
    ax.set_title("Correct vs Incorrect Phase-Path Divergence by Family", fontsize=15, pad=12)
    ax.set_xlabel("JS divergence over dominant phase paths")
    ax.set_ylabel("")
    for idx, row in phase_div.reset_index(drop=True).iterrows():
        ax.text(row["path_js_divergence"] + 0.01, idx, f"{row['correct_dominant_path']} | {row['incorrect_dominant_path']}", va="center", fontsize=9)
    save_figure(fig3)

    fig4 = assets_dir / "prompt_recurrence_significance.png"
    plt.figure(figsize=(11, 6))
    prompt_sig["label"] = prompt_sig["task_family"] + " / " + prompt_sig["outcome"]
    ax = sns.scatterplot(
        data=prompt_sig,
        x="observed_pairwise_margin",
        y="label",
        size="n_prompts",
        hue="permutation_p_value",
        palette="mako_r",
        sizes=(70, 240),
    )
    ax.set_title("Prompt-Recurrent Residual Structure Survives Wider Prompt Support", fontsize=15, pad=12)
    ax.set_xlabel("Observed pairwise margin")
    ax.set_ylabel("")
    ax.axvline(0.0, color="#555", linestyle="--", linewidth=1)
    save_figure(fig4)

    fig5 = assets_dir / "temperature_margin.png"
    plt.figure(figsize=(10, 4.8))
    ax = sns.barplot(data=temp_margin, x="temperature_margin", y="task_family", hue="task_family", dodge=False, palette="rocket", legend=False)
    ax.set_title("Temperature Changes Outcome Mix More Than Residual Geometry", fontsize=15, pad=12)
    ax.set_xlabel("Cross-temp JS minus same-temp JS")
    ax.set_ylabel("")
    ax.axvline(0.0, color="#555", linestyle="--", linewidth=1)
    save_figure(fig5)

    fig6 = assets_dir / "phase_predictability.png"
    plt.figure(figsize=(11, 5.5))
    ax = sns.barplot(
        data=phase_pred,
        x="task_family",
        y="cv_balanced_accuracy",
        hue="feature_set",
        palette=["#d0894f", "#58798a", "#465d4f"],
    )
    ax.set_title("When Outcome Becomes Predictable Depends on the Family", fontsize=15, pad=12)
    ax.set_xlabel("")
    ax.set_ylabel("Cross-validated balanced accuracy")
    ax.tick_params(axis="x", rotation=20)
    save_figure(fig6)

    report_path = docs_dir / "research_blog_report.md"
    report = f"""# Trajectory-Induced Subspaces: An Exploratory Research Report

*This repository is a personal learning project and an open exploratory workbench. The goal of this report is not to present a polished final theory, but to make the current experiments, figures, and partial conclusions legible.*

## What this project is trying to understand

The central question is:

> Does LLM reasoning mostly follow static semantic structure, or does the trajectory itself induce local residual geometry?

The project started from a simple intuition: a reasoning trace may not just *select* an axis that is already sitting inside embedding space. It may instead *create* a local subspace as the trace unfolds.

At this point, the project has accumulated two main experimental views:

- a **static manifold view** through Spatial Semantomics
- a **dynamic trajectory view** through trajectory deltas and residual-regime analysis

The current datasets used in this report are:

- temperature-conditioned run: **{temp_analysis["trace_count"]} traces / {temp_analysis["step_count"]} steps / {temp_analysis["delta_count"]} deltas**
- repeated 8x5 run: **{repeated_analysis["trace_count"]} traces / {repeated_analysis["step_count"]} steps / {repeated_analysis["delta_count"]} deltas**

## 1. A quick scoreboard

The first question was not “what is true?” but “which of the current findings have started to look durable?”

![Evidence score summary](./assets/evidence_scores.png)

The strongest findings so far are:

- static semantic axes do **not** explain most dynamic reasoning movement
- residual regimes look **phase-specific** and often **path-specific**
- family and outcome structure seem to matter more than temperature

Prompt recurrence is real too, but it is more uneven across families, so it still feels more exploratory than the other findings.

## 2. Static structure is real, but it is not enough

One of the cleanest plots in the project is the gap between static-axis alignment and residual energy.

![Static vs residual geometry](./assets/static_vs_residual.png)

If reasoning were mostly “axis following,” I would expect much higher best-axis alignment and much lower residual energy. Instead, the residual stays very large across families and outcomes.

That does **not** mean static structure is irrelevant. It means static structure looks more like a background organization of semantic space than a sufficient explanation of the actual reasoning motion.

## 3. The interesting part is not just that failures differ, but *how* they differ

Once the trace is cut into phases, the geometry becomes more legible. Instead of asking “is incorrect reasoning noisier?”, a better question becomes:

> Do correct and incorrect traces move through different residual-regime paths?

![Phase-path divergence by family](./assets/phase_path_divergence.png)

This is where the project started to feel less like a generic embedding experiment and more like a geometry-of-reasoning experiment:

- **Arithmetic** often diverges early or in the middle.
- **Temporal ordering** looks more late-path-sensitive.
- **Causal micro world** often seems to pick a regime quite early.
- **Commonsense** is trickier: the dominant path can match while the full path distribution still diverges.

That last point matters. Sometimes the mode path is the same, but the distribution over paths is still different enough to show a meaningful divergence.

## 4. Some of the residual geometry really does recur at the prompt level

One obvious alternative explanation is that the residual structure is just sampling noise. Repeated prompt runs were the first serious attempt to pressure-test that.

![Prompt recurrence significance](./assets/prompt_recurrence_significance.png)

The broad pattern is:

- several family/outcome groups keep positive same-prompt margins even as prompt support grows
- `symbolic_logic`, `temporal_ordering (incorrect)`, `arithmetic (correct)`, and `causal_micro_world (correct)` remain relatively strong
- `commonsense` and some incorrect groups are noisier and less stable

So the honest reading is not “all residual structure is prompt-recurrent.”  
It is:

> some residual regimes are reproducible enough that shuffled baselines stop looking plausible, but the strength of this recurrence is family-dependent.

## 5. Temperature matters, but it is not the main organizing variable

I expected temperature to maybe wash out the recurrence story. It did not.

![Temperature sensitivity](./assets/temperature_margin.png)

Temperature does change the **correct/incorrect mix**, but the residual-regime structure is usually not dramatically more similar at the same temperature than across temperatures. In other words:

- temperature affects behavior
- but the geometry still seems more constrained by **family**, **outcome**, and **phase**

That is one reason the project now leans more strongly toward the phrase *trajectory-induced local structure* rather than a simpler “sampling artifact” explanation.

## 6. Different families seem to decide at different times

The next question was timing:

> When does the reasoning path become informative about the eventual outcome?

![Phase predictability](./assets/phase_predictability.png)

The answer is not uniform:

- **Causal micro world** is often informative already from early-phase information.
- **Arithmetic** seems to need the early-to-middle transition to become more legible.
- **Temporal ordering** becomes more predictable when the path is seen more fully.
- **Symbolic logic** remains relatively subtle in this framing.

This is important because it suggests that “failure” is not a single kind of event. For some families it looks like **early regime selection**. For others it looks closer to **late commitment**.

## 7. Current working mental model

Right now the project feels best summarized by this sequence:

1. The prompt family places the model in a broad semantic neighborhood.
2. The reasoning trace enters a local residual regime.
3. Phase-to-phase movement creates a path through that regime.
4. Correct and incorrect outcomes often correspond to different regime paths.
5. Static semantic axes still matter, but they do not explain the motion by themselves.

This is still exploratory. But it is already more specific than “reasoning is geometric.”

## What feels strongest right now

- **Static semantic manifold alone is not enough.**
- **Residual geometry is real and often family-specific.**
- **Some residual regimes recur under repeated prompting.**
- **Phase structure matters a lot.**
- **Temperature is secondary to family/outcome/phase structure.**

## What still feels unsettled

- some families, especially parts of commonsense, still look unstable
- current residual clusters are useful but still exploratory
- the project has more evidence for “not static-axis-only” than for a final universal alternative model

## Where I would push next

- build a robustness map over family × outcome × phase × temperature
- compare the full repeated datasets across multiple embedding backbones
- turn phase paths into a more explicit transition-graph or Sankey-style view
- test whether early-phase features predict held-out prompts, not just held-out traces

## Where to browse next

- exploratory note: [outputs/exploratory_research_note.md](../outputs/exploratory_research_note.md)
- dashboard: [outputs/dashboard/index.html](../outputs/dashboard/index.html)
- evidence scores: [outputs/finding_evidence_scores.csv](../outputs/finding_evidence_scores.csv)

The project is still evolving, but at this point the main exploratory conclusion is fairly stable:

> reasoning does not look well described as simple static-axis following; it looks more like family-specific, phase-sensitive local geometry.
"""

    report_path.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
