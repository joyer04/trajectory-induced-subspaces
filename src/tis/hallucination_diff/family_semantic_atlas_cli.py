from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.sparse.csgraph import minimum_spanning_tree
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import StandardScaler

try:
    import umap
except ImportError:  # pragma: no cover
    umap = None  # type: ignore[assignment]

from tis.embedding import embed_texts
from tis.hallucination_diff.dataset import build_sample_frame, load_qa_pairs
from tis.hallucination_diff.family_subspace import (
    extract_pair_metadata,
    fit_family_subspaces,
    projection_fingerprint_frame,
    residualize_by_base,
)
from tis.hallucination_diff.paired_delta import build_paired_delta_matrix
from tis.io_utils import ensure_dir, records_to_parquet, write_json


BASE_PALETTE = [
    "#1b9e77",
    "#d95f02",
    "#7570b3",
    "#e7298a",
    "#66a61e",
    "#e6ab02",
    "#a6761d",
    "#1f78b4",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a projection-based semantic atlas over paired deltas.")
    parser.add_argument("--dataset", required=True, help="Path to JSON list of question/answer pairs")
    parser.add_argument(
        "--output-dir",
        default="outputs/hallucination_diff/family_semantic_atlas",
        help="Directory for atlas outputs",
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
        help="Which text field to embed",
    )
    parser.add_argument(
        "--delta-mode",
        choices=["raw", "residual"],
        default="residual",
        help="Whether to use raw paired deltas or base-residual deltas",
    )
    parser.add_argument(
        "--variance-threshold",
        type=float,
        default=0.9,
        help="Explained variance target used to define family bases",
    )
    parser.add_argument(
        "--max-subspace-dim",
        type=int,
        default=6,
        help="Upper bound for family basis dimension used in projection fingerprints",
    )
    return parser.parse_args()


def _project_pca_2d(features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    pca = PCA(n_components=2, random_state=7)
    coords = pca.fit_transform(features)
    return coords.astype(np.float32), pca.explained_variance_ratio_.astype(np.float32)


def _project_umap_2d(features: np.ndarray) -> tuple[np.ndarray, bool]:
    if umap is None or len(features) < 4:
        coords, _ = _project_pca_2d(features)
        return coords, False
    reducer = umap.UMAP(
        n_components=2,
        random_state=7,
        min_dist=0.2,
        n_neighbors=min(10, len(features) - 1),
        metric="euclidean",
    )
    coords = reducer.fit_transform(features)
    return coords.astype(np.float32), True


def _atlas_sample_frame(
    pair_frame: pd.DataFrame,
    fingerprint: pd.DataFrame,
    pca_coords: np.ndarray,
    umap_coords: np.ndarray,
) -> pd.DataFrame:
    frame = pair_frame.copy().reset_index(drop=True)
    frame["atlas_pca1"] = pca_coords[:, 0]
    frame["atlas_pca2"] = pca_coords[:, 1]
    frame["atlas_umap1"] = umap_coords[:, 0]
    frame["atlas_umap2"] = umap_coords[:, 1]
    frame["own_family_projection_energy"] = fingerprint["own_family_projection_energy"].to_numpy()
    frame["best_other_projection_energy"] = fingerprint["best_other_projection_energy"].to_numpy()
    frame["projection_margin"] = fingerprint["projection_margin"].to_numpy()
    proj_columns = [column for column in fingerprint.columns if column.startswith("proj_")]
    for column in proj_columns:
        frame[column] = fingerprint[column].to_numpy()
    return frame


def _atlas_centroid_frame(sample_frame: pd.DataFrame) -> pd.DataFrame:
    proj_columns = [column for column in sample_frame.columns if column.startswith("proj_")]
    rows: list[dict[str, object]] = []
    for family, group in sample_frame.groupby("error_family", sort=True):
        row: dict[str, object] = {
            "error_family": family,
            "pair_count": int(len(group)),
            "atlas_pca1": float(group["atlas_pca1"].mean()),
            "atlas_pca2": float(group["atlas_pca2"].mean()),
            "atlas_umap1": float(group["atlas_umap1"].mean()),
            "atlas_umap2": float(group["atlas_umap2"].mean()),
            "mean_projection_margin": float(group["projection_margin"].mean()),
            "mean_own_family_projection_energy": float(group["own_family_projection_energy"].mean()),
            "mean_best_other_projection_energy": float(group["best_other_projection_energy"].mean()),
        }
        for column in proj_columns:
            row[column] = float(group[column].mean())
        rows.append(row)
    return pd.DataFrame(rows).sort_values("error_family").reset_index(drop=True)


def _centroid_navigation_frame(centroids: pd.DataFrame) -> pd.DataFrame:
    proj_columns = [column for column in centroids.columns if column.startswith("proj_")]
    rows: list[dict[str, object]] = []
    for _, source in centroids.iterrows():
        source_vector = source[proj_columns].to_numpy(dtype=np.float32)
        for _, target in centroids.iterrows():
            target_vector = target[proj_columns].to_numpy(dtype=np.float32)
            cosine = float(np.dot(source_vector, target_vector) / ((np.linalg.norm(source_vector) * np.linalg.norm(target_vector)) + 1e-12))
            row: dict[str, object] = {
                "source_family": str(source["error_family"]),
                "target_family": str(target["error_family"]),
                "proj_space_distance": float(np.linalg.norm(target_vector - source_vector)),
                "proj_space_cosine_similarity": cosine,
                "atlas_pca_dx": float(target["atlas_pca1"] - source["atlas_pca1"]),
                "atlas_pca_dy": float(target["atlas_pca2"] - source["atlas_pca2"]),
                "atlas_pca_distance": float(
                    np.linalg.norm(
                        [
                            target["atlas_pca1"] - source["atlas_pca1"],
                            target["atlas_pca2"] - source["atlas_pca2"],
                        ]
                    )
                ),
                "atlas_umap_dx": float(target["atlas_umap1"] - source["atlas_umap1"]),
                "atlas_umap_dy": float(target["atlas_umap2"] - source["atlas_umap2"]),
                "atlas_umap_distance": float(
                    np.linalg.norm(
                        [
                            target["atlas_umap1"] - source["atlas_umap1"],
                            target["atlas_umap2"] - source["atlas_umap2"],
                        ]
                    )
                ),
            }
            for column in proj_columns:
                row[f"delta_{column}"] = float(target[column] - source[column])
            rows.append(row)
    return pd.DataFrame(rows)


def _mst_edge_frame(centroids: pd.DataFrame) -> pd.DataFrame:
    proj_columns = [column for column in centroids.columns if column.startswith("proj_")]
    feature_matrix = centroids[proj_columns].to_numpy(dtype=np.float32)
    distance_matrix = pairwise_distances(feature_matrix, metric="euclidean")
    mst = minimum_spanning_tree(distance_matrix).toarray()
    rows: list[dict[str, object]] = []
    families = centroids["error_family"].astype(str).tolist()
    for source_index in range(len(families)):
        for target_index in range(len(families)):
            weight = float(mst[source_index, target_index] + mst[target_index, source_index])
            if weight <= 0.0:
                continue
            source = centroids.iloc[source_index]
            target = centroids.iloc[target_index]
            rows.append(
                {
                    "source_family": families[source_index],
                    "target_family": families[target_index],
                    "proj_space_distance": weight,
                    "atlas_pca_x0": float(source["atlas_pca1"]),
                    "atlas_pca_y0": float(source["atlas_pca2"]),
                    "atlas_pca_x1": float(target["atlas_pca1"]),
                    "atlas_pca_y1": float(target["atlas_pca2"]),
                    "atlas_umap_x0": float(source["atlas_umap1"]),
                    "atlas_umap_y0": float(source["atlas_umap2"]),
                    "atlas_umap_x1": float(target["atlas_umap1"]),
                    "atlas_umap_y1": float(target["atlas_umap2"]),
                }
            )
    return pd.DataFrame(rows)


def _plot_atlas_samples(
    sample_frame: pd.DataFrame,
    centroids: pd.DataFrame,
    x_col: str,
    y_col: str,
    output_path: Path,
    title: str,
) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    families = sorted(sample_frame["error_family"].astype(str).unique().tolist())
    palette = {family: BASE_PALETTE[index % len(BASE_PALETTE)] for index, family in enumerate(families)}
    plt.figure(figsize=(10, 8))
    ax = sns.scatterplot(
        data=sample_frame,
        x=x_col,
        y=y_col,
        hue="error_family",
        palette=palette,
        s=70,
        alpha=0.72,
        edgecolor="white",
        linewidth=0.6,
    )
    sns.scatterplot(
        data=centroids,
        x=x_col,
        y=y_col,
        hue="error_family",
        palette=palette,
        s=260,
        marker="X",
        legend=False,
        edgecolor="black",
        linewidth=1.0,
        ax=ax,
    )
    for _, row in centroids.iterrows():
        ax.text(
            float(row[x_col]),
            float(row[y_col]),
            str(row["error_family"]),
            fontsize=10,
            ha="center",
            va="bottom",
        )
    ax.set_title(title)
    ax.set_xlabel(x_col.replace("_", " ").title())
    ax.set_ylabel(y_col.replace("_", " ").title())
    plt.tight_layout()
    plt.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close()


def _plot_centroid_graph(
    centroids: pd.DataFrame,
    mst_edges: pd.DataFrame,
    x_col: str,
    y_col: str,
    output_path: Path,
    title: str,
) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    families = sorted(centroids["error_family"].astype(str).unique().tolist())
    palette = {family: BASE_PALETTE[index % len(BASE_PALETTE)] for index, family in enumerate(families)}
    plt.figure(figsize=(10, 8))
    ax = plt.gca()
    for _, edge in mst_edges.iterrows():
        ax.plot(
            [float(edge[f"{x_col}_x0"]), float(edge[f"{x_col}_x1"])],
            [float(edge[f"{y_col}_y0"]), float(edge[f"{y_col}_y1"])],
            color="#6b7280",
            linewidth=2.2,
            alpha=0.9,
            zorder=1,
        )
    sns.scatterplot(
        data=centroids,
        x=x_col,
        y=y_col,
        hue="error_family",
        palette=palette,
        s=320,
        marker="X",
        edgecolor="black",
        linewidth=1.0,
        ax=ax,
    )
    for _, row in centroids.iterrows():
        ax.text(
            float(row[x_col]),
            float(row[y_col]),
            str(row["error_family"]),
            fontsize=11,
            ha="center",
            va="bottom",
        )
    ax.set_title(title)
    ax.set_xlabel(x_col.replace("_", " ").title())
    ax.set_ylabel(y_col.replace("_", " ").title())
    plt.tight_layout()
    plt.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close()


def _summary_payload(
    args: argparse.Namespace,
    pair_frame: pd.DataFrame,
    fingerprint: pd.DataFrame,
    centroids: pd.DataFrame,
    navigation: pd.DataFrame,
    pca_variance_ratio: np.ndarray,
    used_umap: bool,
) -> dict[str, object]:
    non_self = navigation.loc[navigation["source_family"] != navigation["target_family"]].copy()
    nearest = non_self.sort_values("proj_space_distance", ascending=True).iloc[0].to_dict()
    farthest = non_self.sort_values("proj_space_distance", ascending=False).iloc[0].to_dict()
    return {
        "dataset": args.dataset,
        "embedding_model": args.embedding_model,
        "text_field": args.text_field,
        "delta_mode": args.delta_mode,
        "pair_count": int(len(pair_frame)),
        "family_count": int(pair_frame["error_family"].nunique()),
        "base_count": int(pair_frame["base_id"].nunique()),
        "variance_threshold": float(args.variance_threshold),
        "max_subspace_dim": int(args.max_subspace_dim),
        "atlas_feature_dim": int(len([column for column in centroids.columns if column.startswith("proj_")])),
        "mean_projection_margin": float(fingerprint["projection_margin"].mean()),
        "mean_own_family_projection_energy": float(fingerprint["own_family_projection_energy"].mean()),
        "mean_best_other_projection_energy": float(fingerprint["best_other_projection_energy"].mean()),
        "pca_variance_explained_pc1": float(pca_variance_ratio[0]),
        "pca_variance_explained_pc2": float(pca_variance_ratio[1]),
        "used_umap_for_2d": bool(used_umap),
        "nearest_family_pair_in_proj_space": nearest,
        "farthest_family_pair_in_proj_space": farthest,
    }


def main() -> None:
    args = parse_args()
    output_dir = ensure_dir(args.output_dir)

    qa_pairs = load_qa_pairs(args.dataset)
    sample_frame = build_sample_frame(qa_pairs)
    embeddings = embed_texts(sample_frame[args.text_field].tolist(), model_name=args.embedding_model)

    paired = build_paired_delta_matrix(sample_frame, embeddings)
    pair_frame = extract_pair_metadata(paired.pair_frame)
    residual_delta = residualize_by_base(paired.delta_matrix, pair_frame["base_id"].tolist())
    delta_matrix = residual_delta if args.delta_mode == "residual" else paired.delta_matrix

    families = pair_frame["error_family"].astype(str).tolist()
    subspaces, _ = fit_family_subspaces(
        delta_matrix,
        families,
        variance_threshold=args.variance_threshold,
        max_subspace_dim=args.max_subspace_dim,
    )
    fingerprint = projection_fingerprint_frame(delta_matrix, families, subspaces)
    projection_columns = [column for column in fingerprint.columns if column.startswith("proj_")]
    projection_matrix = fingerprint[projection_columns].to_numpy(dtype=np.float32)
    scaled_projection = StandardScaler().fit_transform(projection_matrix).astype(np.float32)

    pca_coords, pca_variance_ratio = _project_pca_2d(scaled_projection)
    umap_coords, used_umap = _project_umap_2d(scaled_projection)

    atlas_samples = _atlas_sample_frame(pair_frame, fingerprint, pca_coords, umap_coords)
    centroids = _atlas_centroid_frame(atlas_samples)
    navigation = _centroid_navigation_frame(centroids)
    mst_edges = _mst_edge_frame(centroids)

    records_to_parquet(output_dir / "delta_pair_index.parquet", pair_frame.to_dict(orient="records"))
    atlas_samples.to_csv(output_dir / "atlas_sample_coordinates.csv", index=False)
    centroids.to_csv(output_dir / "atlas_family_centroids.csv", index=False)
    navigation.to_csv(output_dir / "atlas_family_navigation.csv", index=False)
    mst_edges.to_csv(output_dir / "atlas_centroid_mst_edges.csv", index=False)

    _plot_atlas_samples(
        atlas_samples,
        centroids,
        "atlas_pca1",
        "atlas_pca2",
        output_dir / "atlas_projection_pca2d.png",
        "Projection Atlas in PCA Coordinates",
    )
    _plot_atlas_samples(
        atlas_samples,
        centroids,
        "atlas_umap1",
        "atlas_umap2",
        output_dir / "atlas_projection_umap2d.png",
        "Projection Atlas in UMAP Coordinates" if used_umap else "Projection Atlas in PCA Coordinates",
    )
    _plot_centroid_graph(
        centroids,
        mst_edges.rename(
            columns={
                "atlas_pca_x0": "atlas_pca1_x0",
                "atlas_pca_y0": "atlas_pca2_y0",
                "atlas_pca_x1": "atlas_pca1_x1",
                "atlas_pca_y1": "atlas_pca2_y1",
                "atlas_umap_x0": "atlas_umap1_x0",
                "atlas_umap_y0": "atlas_umap2_y0",
                "atlas_umap_x1": "atlas_umap1_x1",
                "atlas_umap_y1": "atlas_umap2_y1",
            }
        ),
        "atlas_pca1",
        "atlas_pca2",
        output_dir / "atlas_centroid_graph_pca2d.png",
        "Family Atlas Graph (PCA Coordinates)",
    )
    _plot_centroid_graph(
        centroids,
        mst_edges.rename(
            columns={
                "atlas_pca_x0": "atlas_pca1_x0",
                "atlas_pca_y0": "atlas_pca2_y0",
                "atlas_pca_x1": "atlas_pca1_x1",
                "atlas_pca_y1": "atlas_pca2_y1",
                "atlas_umap_x0": "atlas_umap1_x0",
                "atlas_umap_y0": "atlas_umap2_y0",
                "atlas_umap_x1": "atlas_umap1_x1",
                "atlas_umap_y1": "atlas_umap2_y1",
            }
        ),
        "atlas_umap1",
        "atlas_umap2",
        output_dir / "atlas_centroid_graph_umap2d.png",
        "Family Atlas Graph (UMAP Coordinates)" if used_umap else "Family Atlas Graph (PCA Coordinates)",
    )

    summary = _summary_payload(
        args=args,
        pair_frame=pair_frame,
        fingerprint=fingerprint,
        centroids=centroids,
        navigation=navigation,
        pca_variance_ratio=pca_variance_ratio,
        used_umap=used_umap,
    )
    write_json(output_dir / "summary.json", summary)


if __name__ == "__main__":
    main()
