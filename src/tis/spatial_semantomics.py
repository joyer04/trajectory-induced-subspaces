from __future__ import annotations

import json
import pickle
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import urllib.request

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import seaborn as sns
import umap
from sklearn.cluster import SpectralClustering
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sentence_transformers import SentenceTransformer


DEFAULT_CLUSTER_SYSTEM = (
    "You are summarizing a semantic cluster. "
    "Return a short noun phrase label only."
)

DEFAULT_AXIS_SYSTEM = (
    "You are describing a semantic dimension between two poles. "
    "Return a short phrase only."
)

TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9\\-]+")


@dataclass
class SpatialSemantomicsConfig:
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    n_neighbors: int = 10
    n_axes: int = 5
    n_clusters: int = 3
    random_state: int = 7
    ollama_model: str = "llama3.2:latest"
    ollama_host: str = "http://127.0.0.1:11434"
    enable_visualization: bool = True
    enable_llm_interpretation: bool = True


def compute_embeddings(texts: list[str], model_name: str) -> np.ndarray:
    model = SentenceTransformer(model_name)
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return np.asarray(vectors, dtype=np.float32)


def build_knn_graph(X: np.ndarray, texts: list[str], k: int = 10) -> nx.Graph:
    n_neighbors = min(k + 1, len(texts))
    neighbors = NearestNeighbors(n_neighbors=n_neighbors, metric="cosine")
    neighbors.fit(X)
    distances, indices = neighbors.kneighbors(X)

    graph = nx.Graph()
    for idx, text in enumerate(texts):
        graph.add_node(idx, text=text)

    for src_idx in range(len(texts)):
        for rank in range(1, n_neighbors):
            dst_idx = int(indices[src_idx, rank])
            cosine_distance = float(distances[src_idx, rank])
            similarity = 1.0 - cosine_distance
            graph.add_edge(src_idx, dst_idx, distance=cosine_distance, similarity=similarity)

    return graph


def discover_axes(X: np.ndarray, n_axes: int = 5, method: str = "pca") -> dict[str, Any]:
    if method != "pca":
        raise ValueError("Only PCA is implemented in the baseline pipeline.")

    n_components = min(n_axes, X.shape[0], X.shape[1])
    pca = PCA(n_components=n_components, random_state=7)
    coordinates = pca.fit_transform(X)
    axes = pca.components_

    axis_frame = pd.DataFrame(
        coordinates,
        columns=[f"axis_{idx + 1}" for idx in range(n_components)],
    )
    explained = pd.DataFrame(
        {
            "axis_id": [f"axis_{idx + 1}" for idx in range(n_components)],
            "explained_variance_ratio": pca.explained_variance_ratio_,
        }
    )

    return {
        "axis_vectors": axes,
        "axis_coordinates": axis_frame,
        "explained_variance": explained,
        "model": pca,
    }


def segment_domains(axis_coordinates: pd.DataFrame, n_clusters: int = 3, method: str = "spectral") -> np.ndarray:
    if method != "spectral":
        raise ValueError("Only spectral clustering is implemented in the baseline pipeline.")

    affinity = cosine_similarity(axis_coordinates.to_numpy())
    affinity = np.nan_to_num(affinity, nan=0.0, posinf=0.0, neginf=0.0)
    affinity = np.clip((affinity + 1.0) / 2.0, 0.0, 1.0)
    np.fill_diagonal(affinity, 1.0)
    clustering = SpectralClustering(
        n_clusters=min(n_clusters, len(axis_coordinates)),
        affinity="precomputed",
        assign_labels="kmeans",
        random_state=7,
    )
    return clustering.fit_predict(affinity)


def _fit_umap(X: np.ndarray, n_neighbors: int, random_state: int) -> np.ndarray:
    reducer = umap.UMAP(
        n_neighbors=min(n_neighbors, max(2, len(X) - 1)),
        metric="cosine",
        min_dist=0.2,
        random_state=random_state,
    )
    return reducer.fit_transform(X)


def visualize_space(
    texts: list[str],
    embeddings: np.ndarray,
    axis_coordinates: pd.DataFrame,
    clusters: np.ndarray,
    output_dir: str | Path,
    n_neighbors: int = 10,
    random_state: int = 7,
) -> dict[str, str]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    umap_coords = _fit_umap(embeddings, n_neighbors=n_neighbors, random_state=random_state)
    plot_frame = pd.DataFrame(
        {
            "x": umap_coords[:, 0],
            "y": umap_coords[:, 1],
            "text": texts,
            "cluster": clusters.astype(str),
        }
    )

    cluster_plot_path = output_dir / "umap_clusters.png"
    plt.figure(figsize=(10, 8))
    ax = sns.scatterplot(data=plot_frame, x="x", y="y", hue="cluster", palette="tab10", s=90)
    for _, row in plot_frame.iterrows():
        ax.text(row["x"] + 0.02, row["y"] + 0.02, row["text"], fontsize=8, alpha=0.9)
    ax.set_title("Spatial Semantomics: UMAP Cluster Map")
    plt.tight_layout()
    plt.savefig(cluster_plot_path, dpi=200)
    plt.close()

    axis_plot_paths: dict[str, str] = {}
    for axis_id in axis_coordinates.columns:
        axis_plot_path = output_dir / f"{axis_id}_gradient.png"
        plt.figure(figsize=(10, 8))
        ax = sns.scatterplot(
            x=plot_frame["x"],
            y=plot_frame["y"],
            hue=axis_coordinates[axis_id],
            palette="coolwarm",
            s=90,
        )
        for idx, text in enumerate(texts):
            ax.text(plot_frame.loc[idx, "x"] + 0.02, plot_frame.loc[idx, "y"] + 0.02, text, fontsize=8, alpha=0.9)
        ax.set_title(f"Gradient Plot: {axis_id}")
        plt.tight_layout()
        plt.savefig(axis_plot_path, dpi=200)
        plt.close()
        axis_plot_paths[axis_id] = str(axis_plot_path)

    return {
        "cluster_plot": str(cluster_plot_path),
        "axis_plots": axis_plot_paths,
    }


def _ask_ollama(host: str, model: str, system: str, prompt: str) -> str:
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0},
    }
    request = urllib.request.Request(
        f"{host}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body["response"].strip()


def interpret_clusters(
    texts: list[str],
    clusters: np.ndarray,
    ollama_model: str,
    ollama_host: str,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    cluster_ids = sorted(set(int(cluster_id) for cluster_id in clusters))
    for cluster_id in cluster_ids:
        cluster_texts = [text for text, label in zip(texts, clusters) if int(label) == cluster_id]
        prompt = (
            "These phrases appear together in embedding space:\n"
            + "\n".join(f"- {text}" for text in cluster_texts)
            + "\n\nWhat semantic theme connects them?"
        )
        label = _ask_ollama(ollama_host, ollama_model, DEFAULT_CLUSTER_SYSTEM, prompt)
        rows.append(
            {
                "cluster_id": cluster_id,
                "semantic_label": label,
                "size": len(cluster_texts),
                "texts": cluster_texts,
            }
        )
    return pd.DataFrame(rows)


def statistical_cluster_terms(texts: list[str], clusters: np.ndarray, top_k: int = 5) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    cluster_ids = sorted(set(int(cluster_id) for cluster_id in clusters))

    for cluster_id in cluster_ids:
        token_counts: dict[str, int] = {}
        cluster_texts = [text for text, label in zip(texts, clusters) if int(label) == cluster_id]
        for text in cluster_texts:
            for token in TOKEN_PATTERN.findall(text.lower()):
                token_counts[token] = token_counts.get(token, 0) + 1
        top_terms = sorted(token_counts.items(), key=lambda item: (-item[1], item[0]))[:top_k]
        rows.append(
            {
                "cluster_id": cluster_id,
                "top_terms": ", ".join(term for term, _ in top_terms),
            }
        )
    return pd.DataFrame(rows)


def interpret_axes(
    texts: list[str],
    axis_coordinates: pd.DataFrame,
    ollama_model: str,
    ollama_host: str,
    top_k: int = 10,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for axis_id in axis_coordinates.columns:
        ranked = axis_coordinates[axis_id].sort_values()
        negative_texts = [texts[idx] for idx in ranked.index[:top_k]]
        positive_texts = [texts[idx] for idx in ranked.index[-top_k:]]
        prompt = (
            "The following texts lie on opposite ends of a semantic axis.\n\n"
            "Positive side:\n"
            + "\n".join(f"- {text}" for text in positive_texts)
            + "\n\nNegative side:\n"
            + "\n".join(f"- {text}" for text in negative_texts)
            + "\n\nDescribe the semantic dimension separating them."
        )
        interpretation = _ask_ollama(ollama_host, ollama_model, DEFAULT_AXIS_SYSTEM, prompt)
        rows.append(
            {
                "axis_id": axis_id,
                "interpretation": interpretation,
                "positive_texts": positive_texts,
                "negative_texts": negative_texts,
            }
        )
    return pd.DataFrame(rows)


def statistical_axis_terms(texts: list[str], axis_coordinates: pd.DataFrame, top_k: int = 5) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for axis_id in axis_coordinates.columns:
        ranked = axis_coordinates[axis_id].sort_values()
        negative_texts = [texts[idx] for idx in ranked.index[:top_k]]
        positive_texts = [texts[idx] for idx in ranked.index[-top_k:]]
        rows.append(
            {
                "axis_id": axis_id,
                "positive_terms": ", ".join(positive_texts),
                "negative_terms": ", ".join(negative_texts),
            }
        )
    return pd.DataFrame(rows)


def run_spatial_semantomics(
    texts: list[str],
    output_dir: str | Path,
    config: SpatialSemantomicsConfig | None = None,
) -> dict[str, Any]:
    config = config or SpatialSemantomicsConfig()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    embeddings = compute_embeddings(texts, config.embedding_model)
    graph = build_knn_graph(embeddings, texts, k=config.n_neighbors)
    axis_results = discover_axes(embeddings, n_axes=config.n_axes, method="pca")
    clusters = segment_domains(axis_results["axis_coordinates"], n_clusters=config.n_clusters, method="spectral")
    plot_paths = {}
    if config.enable_visualization:
        plot_paths = visualize_space(
            texts=texts,
            embeddings=embeddings,
            axis_coordinates=axis_results["axis_coordinates"],
            clusters=clusters,
            output_dir=output_dir,
            n_neighbors=config.n_neighbors,
            random_state=config.random_state,
        )

    if config.enable_llm_interpretation:
        cluster_table = interpret_clusters(texts, clusters, config.ollama_model, config.ollama_host)
        axis_table = interpret_axes(texts, axis_results["axis_coordinates"], config.ollama_model, config.ollama_host)
    else:
        cluster_table = pd.DataFrame(
            {
                "cluster_id": sorted(set(int(cluster_id) for cluster_id in clusters)),
                "semantic_label": ["llm_disabled"] * len(set(int(cluster_id) for cluster_id in clusters)),
            }
        )
        axis_table = pd.DataFrame(
            {
                "axis_id": list(axis_results["axis_coordinates"].columns),
                "interpretation": ["llm_disabled"] * len(axis_results["axis_coordinates"].columns),
            }
        )
    cluster_stats = statistical_cluster_terms(texts, clusters)
    axis_stats = statistical_axis_terms(texts, axis_results["axis_coordinates"])

    text_frame = pd.DataFrame(
        {
            "text": texts,
            "cluster_id": clusters,
        }
    ).join(axis_results["axis_coordinates"])
    text_frame.to_csv(output_dir / "text_assignments.csv", index=False)
    cluster_table.to_csv(output_dir / "cluster_labels.csv", index=False)
    axis_table.to_csv(output_dir / "axis_labels.csv", index=False)
    cluster_table.merge(cluster_stats, on="cluster_id", how="left").to_csv(
        output_dir / "cluster_labels_combined.csv",
        index=False,
    )
    axis_table.merge(axis_stats, on="axis_id", how="left").to_csv(
        output_dir / "axis_labels_combined.csv",
        index=False,
    )
    axis_results["explained_variance"].to_csv(output_dir / "axis_variance.csv", index=False)
    np.save(output_dir / "axis_vectors.npy", axis_results["axis_vectors"])
    with (output_dir / "semantic_knn_graph.gpickle").open("wb") as handle:
        pickle.dump(graph, handle)
    np.save(output_dir / "embeddings.npy", embeddings)

    return {
        "embeddings": embeddings,
        "graph": graph,
        "axis_results": axis_results,
        "clusters": clusters,
        "cluster_table": cluster_table,
        "axis_table": axis_table,
        "plot_paths": plot_paths,
    }
