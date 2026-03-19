from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build JSON payloads for the exploratory dashboard")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--output", default="outputs/dashboard/dashboard_data.json")
    return parser.parse_args()


def _clean_value(value):
    if pd.isna(value):
        return None
    return value


def frame_records(path: Path) -> list[dict]:
    records = pd.read_csv(path).to_dict(orient="records")
    return [{key: _clean_value(value) for key, value in record.items()} for record in records]


def main() -> None:
    args = parse_args()
    root = Path(args.project_root)

    temp_analysis = json.loads((root / "data/processed_temperatures_scored_minilm/analysis_summary.json").read_text())
    repeated_analysis = json.loads((root / "data/processed_repeated_8x5_scored_minilm/analysis_summary.json").read_text())

    payload = {
        "overview": {
            "temperature_run": {
                "trace_count": temp_analysis["trace_count"],
                "step_count": temp_analysis["step_count"],
                "delta_count": temp_analysis["delta_count"],
            },
            "repeated_8x5_run": {
                "trace_count": repeated_analysis["trace_count"],
                "step_count": repeated_analysis["step_count"],
                "delta_count": repeated_analysis["delta_count"],
            },
            "embedding_model": temp_analysis["embedding_model"],
        },
        "finding_scores": frame_records(root / "outputs/finding_evidence_scores.csv"),
        "alignment_summary": frame_records(root / "outputs/static_dynamic_bridge_temperature_minilm/alignment_group_summary.csv"),
        "residual_summary": frame_records(root / "outputs/static_dynamic_bridge_temperature_minilm/residual_group_summary.csv"),
        "phase_path_divergence": frame_records(root / "outputs/static_dynamic_bridge_temperature_minilm/phase_path_divergence.csv"),
        "phase_path_dominant": frame_records(root / "outputs/static_dynamic_bridge_temperature_minilm/phase_path_dominant.csv"),
        "step_phase_failure_divergence": frame_records(root / "outputs/static_dynamic_bridge_temperature_minilm/step_phase_failure_divergence.csv"),
        "phase_predictability": frame_records(root / "outputs/static_dynamic_bridge_temperature_minilm/phase_predictability_summary.csv"),
        "late_cluster_predictability": frame_records(root / "outputs/static_dynamic_bridge_temperature_minilm/late_cluster_predictability.csv"),
        "temperature_family_margin": frame_records(root / "outputs/static_dynamic_bridge_temperature_minilm/temperature_family_margin.csv"),
        "prompt_recurrence_significance": frame_records(root / "outputs/static_dynamic_bridge_repeated_8x5_minilm/prompt_recurrence_significance.csv"),
        "prompt_stability_overall": frame_records(root / "outputs/static_dynamic_bridge_repeated_8x5_minilm/prompt_stability_overall.csv"),
        "exploratory_note_path": "outputs/exploratory_research_note.md",
    }

    output_path = root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(payload, indent=2, allow_nan=False)
    output_path.write_text(json_text, encoding="utf-8")
    js_path = output_path.with_suffix(".js")
    js_path.write_text(f"window.DASHBOARD_DATA = {json_text};\n", encoding="utf-8")


if __name__ == "__main__":
    main()
