from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


def unit_normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0.0, 1.0, norms)
    return vectors / norms


def run_pca(vectors: np.ndarray, n_components: int = 8) -> dict:
    if len(vectors) == 0:
        return {"explained_variance_ratio": [], "components": []}

    n_components = min(n_components, vectors.shape[0], vectors.shape[1])
    model = PCA(n_components=n_components)
    model.fit(vectors)
    return {
        "explained_variance_ratio": model.explained_variance_ratio_.tolist(),
        "components": model.components_.tolist(),
    }


def cluster_directions(vectors: np.ndarray, n_clusters: int = 5, random_state: int = 7) -> dict:
    if len(vectors) == 0:
        return {"labels": [], "centroids": []}

    normalized = unit_normalize(vectors)
    n_clusters = min(n_clusters, len(normalized))
    model = KMeans(n_clusters=n_clusters, n_init=10, random_state=random_state)
    labels = model.fit_predict(normalized)
    return {
        "labels": labels.tolist(),
        "centroids": model.cluster_centers_.tolist(),
    }


def summarize_by_task(delta_index: list[dict], labels: list[int]) -> dict:
    summary: dict[str, dict[str, int]] = {}
    for row, label in zip(delta_index, labels):
        task_family = row["task_family"]
        task_summary = summary.setdefault(task_family, {})
        cluster_key = f"cluster_{label}"
        task_summary[cluster_key] = task_summary.get(cluster_key, 0) + 1
    return summary
