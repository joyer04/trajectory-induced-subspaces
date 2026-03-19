from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze residual structure after static-axis projection")
    parser.add_argument("--delta-vectors", default="data/processed_balanced_50_scored_minilm/delta_vectors.npy")
    parser.add_argument("--delta-index", default="data/processed_balanced_50_scored_minilm/delta_index.parquet")
    parser.add_argument("--axis-vectors", default="outputs/spatial_semantomics_tis_steps_50_fast/axis_vectors.npy")
    parser.add_argument("--output-dir", default="outputs/static_dynamic_bridge_50_minilm")
    parser.add_argument("--clusters", type=int, default=5)
    parser.add_argument("--pca-components", type=int, default=8)
    return parser.parse_args()


def row_normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0.0, 1.0, norms)
    return matrix / norms


def orthonormal_basis(axis_vectors: np.ndarray) -> np.ndarray:
    q, _ = np.linalg.qr(axis_vectors.T)
    return q


def project_residuals(vectors: np.ndarray, basis: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    coefficients = vectors @ basis
    reconstructed = coefficients @ basis.T
    residuals = vectors - reconstructed
    return coefficients, residuals


def run_pca(matrix: np.ndarray, n_components: int) -> tuple[np.ndarray, np.ndarray]:
    n_components = min(n_components, matrix.shape[0], matrix.shape[1])
    pca = PCA(n_components=n_components, random_state=7)
    coords = pca.fit_transform(matrix)
    return coords, pca.explained_variance_ratio_


def main() -> None:
    args = parse_args()
    delta_vectors = np.load(args.delta_vectors)
    delta_index = pd.read_parquet(args.delta_index)
    axis_vectors = np.load(args.axis_vectors)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    basis = orthonormal_basis(axis_vectors)
    basis = row_normalize(basis.T).T

    normalized_deltas = row_normalize(delta_vectors)
    static_coefficients, residuals = project_residuals(normalized_deltas, basis)
    residual_norms = np.linalg.norm(residuals, axis=1)
    residual_unit = row_normalize(residuals)

    residual_coords, explained = run_pca(residual_unit, args.pca_components)
    kmeans = KMeans(n_clusters=min(args.clusters, len(residual_unit)), random_state=7, n_init=10)
    residual_clusters = kmeans.fit_predict(residual_unit)

    summary = delta_index.copy()
    summary["static_projection_norm"] = np.linalg.norm(static_coefficients, axis=1)
    summary["residual_norm"] = residual_norms
    summary["residual_cluster"] = residual_clusters
    for idx in range(residual_coords.shape[1]):
        summary[f"residual_pc_{idx + 1}"] = residual_coords[:, idx]

    summary.to_csv(output_dir / "residual_summary.csv", index=False)
    np.save(output_dir / "residual_vectors.npy", residuals)
    pd.DataFrame(
        {
            "component": [f"residual_pc_{idx + 1}" for idx in range(len(explained))],
            "explained_variance_ratio": explained,
        }
    ).to_csv(output_dir / "residual_pca_variance.csv", index=False)

    group_summary = (
        summary.groupby(["task_family", "outcome"])[["static_projection_norm", "residual_norm"]]
        .agg(["mean", "median", "count"])
        .reset_index()
    )
    group_summary.columns = [
        "task_family",
        "outcome",
        "static_projection_norm_mean",
        "static_projection_norm_median",
        "count",
        "residual_norm_mean",
        "residual_norm_median",
        "residual_count",
    ]
    group_summary = group_summary.drop(columns=["residual_count"])
    group_summary.to_csv(output_dir / "residual_group_summary.csv", index=False)

    cluster_counts = (
        summary.groupby(["task_family", "outcome", "residual_cluster"])
        .size()
        .reset_index(name="count")
        .sort_values(["task_family", "outcome", "residual_cluster"])
    )
    cluster_counts.to_csv(output_dir / "residual_cluster_counts.csv", index=False)

    failure_rows: list[dict] = []
    for task_family, family_frame in summary.groupby("task_family"):
        correct = family_frame[family_frame["outcome"] == "correct"]
        incorrect = family_frame[family_frame["outcome"] == "incorrect"]
        if correct.empty or incorrect.empty:
            continue

        correct_mean = correct["residual_norm"].mean()
        incorrect_mean = incorrect["residual_norm"].mean()
        correct_proj = correct["static_projection_norm"].mean()
        incorrect_proj = incorrect["static_projection_norm"].mean()

        correct_cluster_mode = int(correct["residual_cluster"].mode().iloc[0])
        incorrect_cluster_mode = int(incorrect["residual_cluster"].mode().iloc[0])

        failure_rows.append(
            {
                "task_family": task_family,
                "correct_count": int(len(correct)),
                "incorrect_count": int(len(incorrect)),
                "correct_residual_norm_mean": float(correct_mean),
                "incorrect_residual_norm_mean": float(incorrect_mean),
                "incorrect_minus_correct_residual_norm": float(incorrect_mean - correct_mean),
                "correct_static_projection_mean": float(correct_proj),
                "incorrect_static_projection_mean": float(incorrect_proj),
                "incorrect_minus_correct_static_projection": float(incorrect_proj - correct_proj),
                "correct_residual_cluster_mode": correct_cluster_mode,
                "incorrect_residual_cluster_mode": incorrect_cluster_mode,
                "same_mode_cluster": bool(correct_cluster_mode == incorrect_cluster_mode),
            }
        )

    pd.DataFrame(failure_rows).to_csv(output_dir / "failure_regime_summary.csv", index=False)


if __name__ == "__main__":
    main()
