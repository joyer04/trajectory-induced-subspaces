from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

try:
    import umap
except ImportError:  # pragma: no cover
    umap = None  # type: ignore[assignment]

from tis.embedding import embed_texts
from tis.hallucination_diff.dataset import build_sample_frame, load_qa_pairs
from tis.hallucination_diff.paired_delta import build_paired_delta_matrix
from tis.io_utils import ensure_dir, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create 3D PCA visualizations of family delta vectors.")
    parser.add_argument("--dataset", required=True, help="Path to JSON list of question/answer pairs")
    parser.add_argument(
        "--output-dir",
        default="outputs/hallucination_diff/family_delta_3d",
        help="Directory for generated figures and tables",
    )
    parser.add_argument(
        "--embedding-model",
        default="sentence-transformers/all-mpnet-base-v2",
        help="Sentence embedding model name",
    )
    parser.add_argument(
        "--text-field",
        choices=["combined_text", "answer_text"],
        default="answer_text",
        help="Which text field to embed before building paired deltas",
    )
    parser.add_argument(
        "--title-prefix",
        default="Family delta",
        help="Figure title prefix",
    )
    return parser.parse_args()


def _extract_pair_metadata(pair_frame: pd.DataFrame) -> pd.DataFrame:
    frame = pair_frame.copy()
    families = frame["error_family"].astype(str).tolist()
    frame["base_id"] = [
        pair_id[: -(len(family) + 1)] if pair_id.endswith(f"_{family}") else pair_id
        for pair_id, family in zip(frame["pair_id"].astype(str).tolist(), families)
    ]
    return frame


def _residualize_by_base(features: np.ndarray, base_ids: list[str]) -> np.ndarray:
    residual = features.copy()
    frame = pd.DataFrame({"base_id": base_ids})
    for _, indices in frame.groupby("base_id").groups.items():
        base_index = np.asarray(list(indices), dtype=int)
        residual[base_index] = residual[base_index] - residual[base_index].mean(axis=0, keepdims=True)
    return residual


def _project_pca_3d(features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    projector = PCA(n_components=3, random_state=7)
    coords = projector.fit_transform(features)
    return coords, projector.explained_variance_ratio_


def _project_pca_2d(features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    projector = PCA(n_components=2, random_state=7)
    coords = projector.fit_transform(features)
    return coords, projector.explained_variance_ratio_


def _project_umap_2d(features: np.ndarray) -> tuple[np.ndarray, bool]:
    if umap is None or len(features) < 4:
        coords, _ = _project_pca_2d(features)
        return coords, False
    reducer = umap.UMAP(
        n_components=2,
        random_state=7,
        min_dist=0.2,
        n_neighbors=min(10, len(features) - 1),
    )
    scaled = StandardScaler().fit_transform(features)
    coords = reducer.fit_transform(scaled)
    return coords, True


def _coordinate_frame(
    pair_frame: pd.DataFrame,
    coords: np.ndarray,
    prefix: str,
) -> pd.DataFrame:
    frame = pair_frame.copy()
    frame[f"{prefix}_pc1"] = coords[:, 0]
    frame[f"{prefix}_pc2"] = coords[:, 1]
    frame[f"{prefix}_pc3"] = coords[:, 2]
    return frame


def _coordinate_frame_2d(
    pair_frame: pd.DataFrame,
    coords: np.ndarray,
    prefix: str,
) -> pd.DataFrame:
    frame = pair_frame.copy()
    frame[f"{prefix}_pc1"] = coords[:, 0]
    frame[f"{prefix}_pc2"] = coords[:, 1]
    return frame


def _centroid_frame(coordinate_frame: pd.DataFrame, prefix: str) -> pd.DataFrame:
    columns = [f"{prefix}_pc1", f"{prefix}_pc2", f"{prefix}_pc3"]
    return (
        coordinate_frame.groupby("error_family", sort=True)[columns]
        .mean()
        .reset_index()
        .rename(
            columns={
                f"{prefix}_pc1": "pc1",
                f"{prefix}_pc2": "pc2",
                f"{prefix}_pc3": "pc3",
            }
        )
    )


def _centroid_frame_2d(coordinate_frame: pd.DataFrame, prefix: str) -> pd.DataFrame:
    columns = [f"{prefix}_pc1", f"{prefix}_pc2"]
    return (
        coordinate_frame.groupby("error_family", sort=True)[columns]
        .mean()
        .reset_index()
        .rename(
            columns={
                f"{prefix}_pc1": "pc1",
                f"{prefix}_pc2": "pc2",
            }
        )
    )


def _axis_label(axis_name: str, variance_ratio: np.ndarray, axis_index: int) -> str:
    return f"{axis_name} ({variance_ratio[axis_index] * 100:.1f}% var.)"


def _plot_2d(
    coordinate_frame: pd.DataFrame,
    centroid_frame: pd.DataFrame,
    prefix: str,
    title: str,
    output_path: Path,
    method_label: str,
) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    families = sorted(coordinate_frame["error_family"].unique())
    palette = dict(zip(families, sns.color_palette("tab10", n_colors=len(families))))

    plt.figure(figsize=(10, 8))
    ax = sns.scatterplot(
        data=coordinate_frame,
        x=f"{prefix}_pc1",
        y=f"{prefix}_pc2",
        hue="error_family",
        palette=palette,
        s=80,
        alpha=0.78,
        edgecolor="white",
        linewidth=0.4,
    )
    for _, row in centroid_frame.iterrows():
        family = str(row["error_family"])
        ax.scatter(
            row["pc1"],
            row["pc2"],
            s=220,
            color=palette[family],
            marker="X",
            edgecolor="black",
            linewidth=1.2,
            zorder=5,
        )
        ax.text(row["pc1"], row["pc2"], f" {family}", fontsize=10)

    ax.set_title(title)
    ax.set_xlabel(f"{method_label} 1")
    ax.set_ylabel(f"{method_label} 2")
    plt.tight_layout()
    plt.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close()


def _plot_3d(
    coordinate_frame: pd.DataFrame,
    centroid_frame: pd.DataFrame,
    variance_ratio: np.ndarray,
    prefix: str,
    title: str,
    output_path: Path,
) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    families = sorted(coordinate_frame["error_family"].unique())
    palette = dict(zip(families, sns.color_palette("tab10", n_colors=len(families))))

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection="3d")

    for family in families:
        subset = coordinate_frame[coordinate_frame["error_family"] == family]
        ax.scatter(
            subset[f"{prefix}_pc1"],
            subset[f"{prefix}_pc2"],
            subset[f"{prefix}_pc3"],
            s=55,
            alpha=0.72,
            color=palette[family],
            label=family,
            edgecolor="white",
            linewidth=0.4,
        )

    for _, row in centroid_frame.iterrows():
        family = str(row["error_family"])
        ax.scatter(
            row["pc1"],
            row["pc2"],
            row["pc3"],
            s=230,
            color=palette[family],
            marker="X",
            edgecolor="black",
            linewidth=1.2,
        )
        ax.text(row["pc1"], row["pc2"], row["pc3"], f" {family}", fontsize=9)

    ax.set_title(title, pad=20)
    ax.set_xlabel(_axis_label("PC1", variance_ratio, 0), labelpad=12)
    ax.set_ylabel(_axis_label("PC2", variance_ratio, 1), labelpad=12)
    ax.set_zlabel(_axis_label("PC3", variance_ratio, 2), labelpad=12)
    ax.view_init(elev=23, azim=42)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False, title="Error family")
    fig.tight_layout()
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    output_dir = ensure_dir(args.output_dir)

    qa_pairs = load_qa_pairs(args.dataset)
    sample_frame = build_sample_frame(qa_pairs)
    embeddings = embed_texts(sample_frame[args.text_field].tolist(), model_name=args.embedding_model)

    paired = build_paired_delta_matrix(sample_frame, embeddings)
    pair_frame = _extract_pair_metadata(paired.pair_frame)
    residual_delta = _residualize_by_base(paired.delta_matrix, pair_frame["base_id"].tolist())

    raw_coords, raw_variance = _project_pca_3d(paired.delta_matrix)
    residual_coords, residual_variance = _project_pca_3d(residual_delta)
    raw_umap_coords, raw_used_umap = _project_umap_2d(paired.delta_matrix)
    residual_umap_coords, residual_used_umap = _project_umap_2d(residual_delta)

    raw_frame = _coordinate_frame(pair_frame, raw_coords, "raw")
    residual_frame = _coordinate_frame(pair_frame, residual_coords, "residual")
    raw_umap_frame = _coordinate_frame_2d(pair_frame, raw_umap_coords, "raw_umap")
    residual_umap_frame = _coordinate_frame_2d(pair_frame, residual_umap_coords, "residual_umap")
    raw_centroids = _centroid_frame(raw_frame, "raw")
    residual_centroids = _centroid_frame(residual_frame, "residual")
    raw_umap_centroids = _centroid_frame_2d(raw_umap_frame, "raw_umap")
    residual_umap_centroids = _centroid_frame_2d(residual_umap_frame, "residual_umap")

    raw_frame.to_csv(output_dir / "family_delta_pca3d.csv", index=False)
    residual_frame.to_csv(output_dir / "family_delta_residual_pca3d.csv", index=False)
    raw_umap_frame.to_csv(output_dir / "family_delta_umap2d.csv", index=False)
    residual_umap_frame.to_csv(output_dir / "family_delta_residual_umap2d.csv", index=False)
    raw_centroids.to_csv(output_dir / "family_centroids_pca3d.csv", index=False)
    residual_centroids.to_csv(output_dir / "family_residual_centroids_pca3d.csv", index=False)
    raw_umap_centroids.to_csv(output_dir / "family_centroids_umap2d.csv", index=False)
    residual_umap_centroids.to_csv(output_dir / "family_residual_centroids_umap2d.csv", index=False)

    _plot_3d(
        raw_frame,
        raw_centroids,
        raw_variance,
        "raw",
        f"{args.title_prefix}: raw paired deltas",
        output_dir / "family_delta_pca3d.png",
    )
    _plot_3d(
        residual_frame,
        residual_centroids,
        residual_variance,
        "residual",
        f"{args.title_prefix}: base-residual paired deltas",
        output_dir / "family_delta_residual_pca3d.png",
    )
    _plot_2d(
        raw_umap_frame,
        raw_umap_centroids,
        "raw_umap",
        f"{args.title_prefix}: raw paired deltas",
        output_dir / "family_delta_umap2d.png",
        "UMAP" if raw_used_umap else "PCA",
    )
    _plot_2d(
        residual_umap_frame,
        residual_umap_centroids,
        "residual_umap",
        f"{args.title_prefix}: base-residual paired deltas",
        output_dir / "family_delta_residual_umap2d.png",
        "UMAP" if residual_used_umap else "PCA",
    )

    summary = {
        "dataset": args.dataset,
        "embedding_model": args.embedding_model,
        "text_field": args.text_field,
        "pair_count": int(len(pair_frame)),
        "base_count": int(pair_frame["base_id"].nunique()),
        "family_count": int(pair_frame["error_family"].nunique()),
        "raw_pca3_explained_variance_ratio": [float(value) for value in raw_variance],
        "raw_pca3_total_explained_variance": float(np.sum(raw_variance)),
        "residual_pca3_explained_variance_ratio": [float(value) for value in residual_variance],
        "residual_pca3_total_explained_variance": float(np.sum(residual_variance)),
        "raw_umap2d_used_umap": bool(raw_used_umap),
        "residual_umap2d_used_umap": bool(residual_used_umap),
        "outputs": {
            "raw_figure": str(output_dir / "family_delta_pca3d.png"),
            "residual_figure": str(output_dir / "family_delta_residual_pca3d.png"),
            "raw_umap_figure": str(output_dir / "family_delta_umap2d.png"),
            "residual_umap_figure": str(output_dir / "family_delta_residual_umap2d.png"),
            "raw_coordinates": str(output_dir / "family_delta_pca3d.csv"),
            "residual_coordinates": str(output_dir / "family_delta_residual_pca3d.csv"),
            "raw_umap_coordinates": str(output_dir / "family_delta_umap2d.csv"),
            "residual_umap_coordinates": str(output_dir / "family_delta_residual_umap2d.csv"),
        },
    }
    write_json(output_dir / "summary.json", summary)


if __name__ == "__main__":
    main()
