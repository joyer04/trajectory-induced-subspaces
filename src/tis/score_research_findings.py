from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score current research findings with heuristic evidence scores")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root path",
    )
    return parser.parse_args()


def clip01(value: float) -> float:
    return max(0.0, min(1.0, value))


def sample_score(count: float, target: float) -> float:
    return clip01(math.log1p(count) / math.log1p(target))


def main() -> None:
    args = parse_args()
    root = Path(args.project_root)

    temp_bridge = root / "outputs/static_dynamic_bridge_temperature_minilm"
    repeated_4 = root / "outputs/static_dynamic_bridge_repeated_4x5_minilm"
    repeated_8 = root / "outputs/static_dynamic_bridge_repeated_8x5_minilm"

    temp_analysis = json.loads((root / "data/processed_temperatures_scored_minilm/analysis_summary.json").read_text())
    repeated_8_analysis = json.loads((root / "data/processed_repeated_8x5_scored_minilm/analysis_summary.json").read_text())

    alignment = pd.read_csv(temp_bridge / "alignment_group_summary.csv")
    residual = pd.read_csv(temp_bridge / "residual_group_summary.csv")
    merged = alignment.merge(residual, on=["task_family", "outcome"])

    static_effect = clip01(((merged["residual_norm_mean"].mean() - merged["best_abs_alignment"].mean()) - 0.60) / 0.25)
    static_consistency = float(
        ((merged["residual_norm_mean"] > 0.95) & (merged["best_abs_alignment"] < 0.25)).mean()
    )
    static_sample = sample_score(temp_analysis["delta_count"], 1000)
    static_score = 100 * (0.4 * static_effect + 0.3 * static_consistency + 0.3 * static_sample)

    sig_4 = pd.read_csv(repeated_4 / "prompt_recurrence_significance.csv")
    sig_8 = pd.read_csv(repeated_8 / "prompt_recurrence_significance.csv")
    sig_t = pd.read_csv(temp_bridge / "prompt_recurrence_significance.csv")
    all_sig = pd.concat(
        [
            sig_4.assign(dataset="repeated_4x5"),
            sig_8.assign(dataset="repeated_8x5"),
            sig_t.assign(dataset="temperature_4x5"),
        ],
        ignore_index=True,
    )
    recurrent_significant = float((all_sig["permutation_p_value"] < 0.05).mean())
    recurrent_effect = clip01(all_sig["observed_pairwise_margin"].mean() / 0.35)
    recurrent_support = sample_score(all_sig["n_prompts"].mean() * all_sig["n_traces"].mean(), 160)
    recurrent_score = 100 * (0.4 * recurrent_significant + 0.35 * recurrent_effect + 0.25 * recurrent_support)

    temp_margin = pd.read_csv(temp_bridge / "temperature_family_margin.csv")
    temp_sig_fraction = float((sig_t["permutation_p_value"] < 0.05).mean())
    temp_small_margin = clip01(1.0 - (temp_margin["temperature_margin"].abs().mean() / 0.05))
    temp_support = sample_score(temp_analysis["trace_count"], 300)
    temperature_score = 100 * (0.4 * temp_small_margin + 0.35 * temp_sig_fraction + 0.25 * temp_support)

    phase_div = pd.read_csv(temp_bridge / "phase_path_divergence.csv")
    step_div = pd.read_csv(temp_bridge / "step_phase_failure_divergence.csv")
    phase_effect = clip01(phase_div["path_js_divergence"].mean() / 0.60)
    phase_diverse = float((phase_div["same_dominant_path"] == False).mean())
    step_peak = clip01(step_div["js_divergence"].max() / 0.40)
    phase_sample = sample_score(temp_analysis["trace_count"], 300)
    phase_score = 100 * (0.35 * phase_effect + 0.25 * phase_diverse + 0.20 * step_peak + 0.20 * phase_sample)

    findings = pd.DataFrame(
        [
            {
                "finding_id": "F1",
                "finding": "Static semantic axes under-explain dynamic reasoning transitions",
                "evidence_score": round(static_score, 1),
                "sample_component": round(static_sample, 3),
                "effect_component": round(static_effect, 3),
                "consistency_component": round(static_consistency, 3),
                "notes": "High residual norms and low best-axis alignments persist across task/outcome groups.",
            },
            {
                "finding_id": "F2",
                "finding": "Some residual geometry is prompt-recurrent rather than pure sampling noise",
                "evidence_score": round(recurrent_score, 1),
                "sample_component": round(recurrent_support, 3),
                "effect_component": round(recurrent_effect, 3),
                "consistency_component": round(recurrent_significant, 3),
                "notes": "Repeated-prompt significance survives across 4x5, 8x5, and temperature-conditioned runs.",
            },
            {
                "finding_id": "F3",
                "finding": "Family/outcome structure matters more than temperature for residual recurrence",
                "evidence_score": round(temperature_score, 1),
                "sample_component": round(temp_support, 3),
                "effect_component": round(temp_small_margin, 3),
                "consistency_component": round(temp_sig_fraction, 3),
                "notes": "Temperature margins are small while recurrence remains strong in the temperature-conditioned dataset.",
            },
            {
                "finding_id": "F4",
                "finding": "Residual regimes are phase-specific and path-specific, not uniform over a trace",
                "evidence_score": round(phase_score, 1),
                "sample_component": round(phase_sample, 3),
                "effect_component": round(phase_effect, 3),
                "consistency_component": round(phase_diverse, 3),
                "notes": "Different families diverge in different phases and often follow different dominant regime paths.",
            },
        ]
    )
    findings.to_csv(root / "outputs/finding_evidence_scores.csv", index=False)

    payload = {
        "scoring_note": (
            "Evidence scores are heuristic 0-100 summaries, not posterior probabilities. "
            "They combine sample size, effect size, and consistency/reproducibility components."
        ),
        "datasets_used": {
            "temperature_trace_count": temp_analysis["trace_count"],
            "temperature_delta_count": temp_analysis["delta_count"],
            "repeated_8x5_trace_count": repeated_8_analysis["trace_count"],
            "repeated_8x5_delta_count": repeated_8_analysis["delta_count"],
            "significance_tables": [
                str(repeated_4 / "prompt_recurrence_significance.csv"),
                str(repeated_8 / "prompt_recurrence_significance.csv"),
                str(temp_bridge / "prompt_recurrence_significance.csv"),
            ],
        },
    }
    (root / "outputs/finding_evidence_scores.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
