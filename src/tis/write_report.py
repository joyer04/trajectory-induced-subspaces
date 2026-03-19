from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a short markdown report from processed outputs")
    parser.add_argument(
        "--processed-dir",
        default="data/processed",
        help="Directory containing analysis_summary.json and parquet outputs",
    )
    parser.add_argument(
        "--output",
        default="outputs/baseline_report.md",
        help="Markdown output path",
    )
    return parser.parse_args()


def format_cluster_summary(summary: dict) -> list[str]:
    lines: list[str] = []
    for task_family, clusters in summary.items():
        parts = ", ".join(f"{name}={count}" for name, count in sorted(clusters.items()))
        lines.append(f"- `{task_family}`: {parts}")
    return lines


def main() -> None:
    args = parse_args()
    processed_dir = Path(args.processed_dir)
    summary_path = processed_dir / "analysis_summary.json"
    delta_index_path = processed_dir / "delta_index.parquet"
    if not summary_path.exists():
        raise FileNotFoundError(f"Missing summary file: {summary_path}")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    report_lines = [
        "# Baseline Report",
        "",
        "## Summary",
        "",
        f"- Traces: {summary['trace_count']}",
        f"- Steps: {summary['step_count']}",
        f"- Deltas: {summary['delta_count']}",
        f"- Embedding model: `{summary['embedding_model']}`",
        "",
        "## PCA Explained Variance",
        "",
        ", ".join(f"{value:.4f}" for value in summary["pca_explained_variance_ratio"]) or "No PCA output",
        "",
        "## Task Cluster Summary",
        "",
        *format_cluster_summary(summary["task_cluster_summary"]),
    ]

    if delta_index_path.exists():
        delta_index = pd.read_parquet(delta_index_path)
        report_lines.extend(
            [
                "",
                "## Outcome Counts",
                "",
                *[
                    f"- `{outcome}`: {count}"
                    for outcome, count in delta_index["outcome"].value_counts().to_dict().items()
                ],
            ]
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
