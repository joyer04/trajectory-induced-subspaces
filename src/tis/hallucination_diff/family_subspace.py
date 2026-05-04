from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.linalg import subspace_angles
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GroupKFold, cross_val_predict


@dataclass(frozen=True)
class FamilySubspace:
    family: str
    mean_vector: np.ndarray
    basis: np.ndarray
    explained_variance_ratio: np.ndarray
    effective_rank: int
    rank_at_threshold: int
    sample_count: int


def extract_pair_metadata(pair_frame: pd.DataFrame) -> pd.DataFrame:
    frame = pair_frame.copy()
    families = frame["error_family"].astype(str).tolist()
    frame["base_id"] = [
        pair_id[: -(len(family) + 1)] if pair_id.endswith(f"_{family}") else pair_id
        for pair_id, family in zip(frame["pair_id"].astype(str).tolist(), families)
    ]
    return frame


def residualize_by_base(features: np.ndarray, base_ids: list[str]) -> np.ndarray:
    residual = features.copy()
    frame = pd.DataFrame({"base_id": base_ids})
    for _, indices in frame.groupby("base_id").groups.items():
        base_index = np.asarray(list(indices), dtype=int)
        residual[base_index] = residual[base_index] - residual[base_index].mean(axis=0, keepdims=True)
    return residual


def rank_at_threshold(explained_variance_ratio: np.ndarray, variance_threshold: float) -> int:
    cumulative = np.cumsum(explained_variance_ratio)
    return int(np.searchsorted(cumulative, variance_threshold, side="left") + 1)


def fit_family_subspaces(
    features: np.ndarray,
    families: list[str],
    variance_threshold: float,
    max_subspace_dim: int,
) -> tuple[list[FamilySubspace], pd.DataFrame]:
    family_frame = pd.DataFrame({"error_family": families})
    results: list[FamilySubspace] = []
    rows: list[dict[str, object]] = []

    for family, indices in family_frame.groupby("error_family").groups.items():
        family_index = np.asarray(list(indices), dtype=int)
        family_vectors = features[family_index]
        family_mean = family_vectors.mean(axis=0)
        centered = family_vectors - family_mean

        max_components = min(len(family_vectors), family_vectors.shape[1])
        pca = PCA(n_components=max_components, random_state=7)
        pca.fit(centered)
        full_ratio = pca.explained_variance_ratio_
        threshold_rank = rank_at_threshold(full_ratio, variance_threshold)
        effective_rank = min(threshold_rank, max_subspace_dim, max_components)
        basis = pca.components_[:effective_rank].T

        results.append(
            FamilySubspace(
                family=str(family),
                mean_vector=family_mean.astype(np.float32),
                basis=basis.astype(np.float32),
                explained_variance_ratio=full_ratio.astype(np.float32),
                effective_rank=int(effective_rank),
                rank_at_threshold=int(threshold_rank),
                sample_count=int(len(family_vectors)),
            )
        )
        rows.append(
            {
                "error_family": str(family),
                "pair_count": int(len(family_vectors)),
                "effective_rank": int(effective_rank),
                "rank_at_threshold": int(threshold_rank),
                "variance_explained_by_effective_rank": float(np.sum(full_ratio[:effective_rank])),
                "variance_explained_top1": float(full_ratio[0]) if len(full_ratio) >= 1 else float("nan"),
                "variance_explained_top2": float(np.sum(full_ratio[:2])) if len(full_ratio) >= 2 else float("nan"),
                "variance_explained_top3": float(np.sum(full_ratio[:3])) if len(full_ratio) >= 3 else float("nan"),
            }
        )

    return results, pd.DataFrame(rows).sort_values("error_family").reset_index(drop=True)


def basis_projection_r2(centered_vectors: np.ndarray, basis: np.ndarray) -> float:
    if centered_vectors.size == 0:
        return float("nan")
    projected = centered_vectors @ basis @ basis.T
    residual = centered_vectors - projected
    total_ss = float(np.sum(centered_vectors**2))
    if total_ss == 0.0:
        return 1.0
    residual_ss = float(np.sum(residual**2))
    return float(1.0 - (residual_ss / total_ss))


def principal_angle_frame(subspaces: list[FamilySubspace]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for left in subspaces:
        for right in subspaces:
            shared_dim = min(left.effective_rank, right.effective_rank)
            if shared_dim == 0:
                angle_values = np.asarray([np.nan], dtype=np.float32)
            else:
                angle_values = np.rad2deg(
                    subspace_angles(left.basis[:, :shared_dim], right.basis[:, :shared_dim])
                ).astype(np.float32)
            rows.append(
                {
                    "family_left": left.family,
                    "family_right": right.family,
                    "shared_dim": int(shared_dim),
                    "mean_principal_angle_deg": float(np.nanmean(angle_values)),
                    "max_principal_angle_deg": float(np.nanmax(angle_values)),
                }
            )
    return pd.DataFrame(rows)


def transfer_frame(
    features: np.ndarray,
    families: list[str],
    subspaces: list[FamilySubspace],
) -> pd.DataFrame:
    family_frame = pd.DataFrame({"error_family": families})
    centered_lookup: dict[str, np.ndarray] = {}
    for subspace in subspaces:
        indices = np.asarray(list(family_frame.groupby("error_family").groups[subspace.family]), dtype=int)
        centered_lookup[subspace.family] = features[indices] - features[indices].mean(axis=0, keepdims=True)

    rows: list[dict[str, object]] = []
    for source in subspaces:
        source_vectors = centered_lookup[source.family]
        for target in subspaces:
            r2 = basis_projection_r2(source_vectors, target.basis)
            rows.append(
                {
                    "source_family": source.family,
                    "target_family": target.family,
                    "transfer_r2": r2,
                }
            )
    return pd.DataFrame(rows)


def projection_fingerprint_frame(
    features: np.ndarray,
    families: list[str],
    subspaces: list[FamilySubspace],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    family_order = [item.family for item in subspaces]
    for row_index, vector in enumerate(features):
        current_family = families[row_index]
        energy_by_family: dict[str, float] = {}
        for target in subspaces:
            centered = vector - target.mean_vector
            total_energy = float(np.sum(centered**2))
            if total_energy == 0.0:
                projection_energy = 1.0
            else:
                projected = centered @ target.basis @ target.basis.T
                projection_energy = float(np.sum(projected**2) / total_energy)
            energy_by_family[target.family] = projection_energy

        own_energy = energy_by_family[current_family]
        other_energies = [energy_by_family[name] for name in family_order if name != current_family]
        best_other = max(other_energies) if other_energies else float("nan")
        row = {
            "row_index": int(row_index),
            "error_family": current_family,
            "own_family_projection_energy": own_energy,
            "best_other_projection_energy": float(best_other),
            "projection_margin": float(own_energy - best_other),
        }
        for target_family in family_order:
            row[f"proj_{target_family}"] = energy_by_family[target_family]
        rows.append(row)
    return pd.DataFrame(rows)


def group_cv_multiclass(features: np.ndarray, labels: list[str], groups: list[str]) -> dict[str, float]:
    y = np.asarray(labels)
    group_values = np.asarray(groups)
    splitter = GroupKFold(n_splits=len(set(groups)))
    model = LogisticRegression(max_iter=4000)
    preds = cross_val_predict(model, features, y, cv=splitter, groups=group_values)
    return {
        "accuracy": float(accuracy_score(y, preds)),
        "macro_f1": float(f1_score(y, preds, average="macro")),
    }
