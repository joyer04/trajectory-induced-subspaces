from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate robustness-map figures for current geometry findings")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--output-dir", default="outputs/robustness_maps")
    return parser.parse_args()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def save(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches="tight")
    plt.close()


def heatmap_figure(frame: pd.DataFrame, title: str, path: Path, cmap: str, center: float | None = None, fmt: str = ".3f") -> None:
    plt.figure(figsize=(9, 4.8))
    ax = sns.heatmap(frame, annot=True, cmap=cmap, center=center, fmt=fmt, linewidths=0.5, cbar=True)
    ax.set_title(title, fontsize=14, pad=12)
    ax.set_xlabel("")
    ax.set_ylabel("")
    save(path)


def main() -> None:
    args = parse_args()
    root = Path(args.project_root)
    outdir = ensure_dir(root / args.output_dir)

    sns.set_theme(style="whitegrid")

    sig = pd.read_csv(root / "outputs/static_dynamic_bridge_repeated_8x5_minilm/prompt_recurrence_significance.csv")
    sig_pivot = sig.pivot(index="task_family", columns="outcome", values="observed_pairwise_margin").fillna(0.0)
    heatmap_figure(
        sig_pivot,
        "Prompt Recurrence Margin by Family and Outcome (8x5 repeated run)",
        outdir / "prompt_recurrence_margin_heatmap.png",
        cmap="mako",
        center=0.0,
    )

    sig_pivot_p = sig.pivot(index="task_family", columns="outcome", values="permutation_p_value").fillna(1.0)
    heatmap_figure(
        sig_pivot_p,
        "Prompt Recurrence Permutation P-Value by Family and Outcome",
        outdir / "prompt_recurrence_pvalue_heatmap.png",
        cmap="rocket_r",
        center=None,
    )

    phase_div = pd.read_csv(root / "outputs/static_dynamic_bridge_temperature_minilm/step_phase_failure_divergence.csv")
    phase_pivot = phase_div.pivot(index="task_family", columns="phase", values="js_divergence").fillna(0.0)
    heatmap_figure(
        phase_pivot,
        "Failure-Regime JS Divergence by Family and Phase",
        outdir / "phase_divergence_heatmap.png",
        cmap="crest",
        center=0.0,
    )

    phase_predict = pd.read_csv(root / "outputs/static_dynamic_bridge_temperature_minilm/phase_predictability_summary.csv")
    predict_pivot = phase_predict.pivot(index="task_family", columns="feature_set", values="cv_balanced_accuracy").fillna(0.0)
    heatmap_figure(
        predict_pivot,
        "Outcome Predictability from Phase Features",
        outdir / "phase_predictability_heatmap.png",
        cmap="flare",
        center=0.5,
    )

    temp_margin = pd.read_csv(root / "outputs/static_dynamic_bridge_temperature_minilm/temperature_family_margin.csv")
    temp_pivot = temp_margin.set_index("task_family")[["temperature_margin", "same_temp_js", "cross_temp_js"]]
    heatmap_figure(
        temp_pivot,
        "Temperature Sensitivity by Family",
        outdir / "temperature_sensitivity_heatmap.png",
        cmap="vlag",
        center=0.0,
    )

    scores = pd.read_csv(root / "outputs/finding_evidence_scores.csv").set_index("finding_id")[
        ["evidence_score", "sample_component", "effect_component", "consistency_component"]
    ]
    heatmap_figure(
        scores,
        "Heuristic Evidence Map for Current Findings",
        outdir / "finding_score_heatmap.png",
        cmap="YlOrBr",
        center=None,
        fmt=".2f",
    )


if __name__ == "__main__":
    main()
