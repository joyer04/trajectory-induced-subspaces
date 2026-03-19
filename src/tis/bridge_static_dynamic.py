from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare static semantic axes with dynamic trajectory deltas")
    parser.add_argument("--delta-vectors", default="data/processed_balanced_scored/delta_vectors.npy")
    parser.add_argument("--delta-index", default="data/processed_balanced_scored/delta_index.parquet")
    parser.add_argument("--axis-vectors", default="outputs/spatial_semantomics_tis_steps/axis_vectors.npy")
    parser.add_argument("--output", default="outputs/static_dynamic_bridge/alignment_summary.csv")
    return parser.parse_args()


def unit_normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0.0, 1.0, norms)
    return matrix / norms


def main() -> None:
    args = parse_args()
    delta_vectors = np.load(args.delta_vectors)
    delta_index = pd.read_parquet(args.delta_index)
    axis_vectors = np.load(args.axis_vectors)
    axis_columns = [f"axis_{idx + 1}" for idx in range(axis_vectors.shape[0])]
    static_axis_basis = unit_normalize(axis_vectors)
    normalized_deltas = unit_normalize(delta_vectors)

    rows: list[dict] = []
    for idx, delta in enumerate(normalized_deltas):
        alignments = static_axis_basis @ delta
        abs_alignments = np.abs(alignments)
        best_axis_idx = int(abs_alignments.argmax())
        residual = float(np.sqrt(max(0.0, 1.0 - abs_alignments[best_axis_idx] ** 2)))
        rows.append(
            {
                "trace_id": delta_index.loc[idx, "trace_id"],
                "task_family": delta_index.loc[idx, "task_family"],
                "outcome": delta_index.loc[idx, "outcome"],
                "best_static_axis": axis_columns[best_axis_idx],
                "best_alignment": float(alignments[best_axis_idx]),
                "best_abs_alignment": float(abs_alignments[best_axis_idx]),
                "residual_energy": residual,
            }
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(output_path, index=False)
    frame.groupby(["task_family", "outcome"])[["best_abs_alignment", "residual_energy"]].mean().reset_index().to_csv(
        output_path.parent / "alignment_group_summary.csv",
        index=False,
    )


if __name__ == "__main__":
    main()
