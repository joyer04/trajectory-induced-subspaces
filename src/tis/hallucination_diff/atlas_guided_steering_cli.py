from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from tis.embedding import embed_texts
from tis.hallucination_diff.dataset import build_sample_frame, load_qa_pairs
from tis.hallucination_diff.family_subspace import (
    extract_pair_metadata,
    fit_family_subspaces,
    projection_fingerprint_frame,
    residualize_by_base,
)
from tis.hallucination_diff.paired_delta import build_paired_delta_matrix
from tis.io_utils import ensure_dir, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Steer paired deltas using a local or global semantic atlas.")
    parser.add_argument("--dataset", required=True, help="Path to JSON list of question/answer pairs")
    parser.add_argument(
        "--output-dir",
        default="outputs/hallucination_diff/atlas_guided_steering",
        help="Directory for outputs",
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
        "--scope",
        choices=["knn_local", "topic_local", "global"],
        default="knn_local",
        help="How to define atlas neighborhoods for steering",
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
    parser.add_argument("--neighbors", type=int, default=15, help="Neighborhood size for local atlas selection")
    parser.add_argument(
        "--steer-scale",
        type=float,
        default=0.75,
        help="Scale applied to the target minus source anchor vector",
    )
    return parser.parse_args()


def _fit_reference_model(features: np.ndarray, labels: list[str]) -> LogisticRegression:
    model = LogisticRegression(max_iter=4000)
    model.fit(features, np.asarray(labels))
    return model


def _family_metrics(labels: list[str], preds: np.ndarray) -> dict[str, float]:
    y = np.asarray(labels)
    return {
        "accuracy": float(accuracy_score(y, preds)),
        "macro_f1": float(f1_score(y, preds, average="macro")),
    }


def _build_neighbor_index(atlas_features: np.ndarray) -> NearestNeighbors:
    model = NearestNeighbors(
        n_neighbors=min(len(atlas_features), max(2, len(atlas_features))),
        metric="euclidean",
    )
    model.fit(atlas_features)
    return model


def _candidate_indices(
    row_index: int,
    pair_frame: pd.DataFrame,
    atlas_features: np.ndarray,
    nn_model: NearestNeighbors,
    scope: str,
    neighbors: int,
) -> np.ndarray:
    if scope == "global":
        return np.delete(np.arange(len(pair_frame), dtype=int), row_index)

    current = pair_frame.iloc[row_index]
    base_id = str(current["base_id"])
    topic = str(current["topic"]) if "topic" in current else ""

    if scope == "topic_local":
        mask = (pair_frame["topic"].astype(str) == topic) & (pair_frame["base_id"].astype(str) != base_id)
        matches = np.where(mask.to_numpy())[0]
        if len(matches) >= max(4, neighbors):
            return matches.astype(int)

    distances, indices = nn_model.kneighbors(atlas_features[row_index : row_index + 1], return_distance=True)
    flat = indices[0].astype(int)
    filtered = [idx for idx in flat if idx != row_index and str(pair_frame.iloc[idx]["base_id"]) != base_id]
    if len(filtered) >= neighbors:
        return np.asarray(filtered[:neighbors], dtype=int)
    return np.asarray(filtered, dtype=int)


def _mean_anchor(delta_matrix: np.ndarray, indices: np.ndarray, fallback: np.ndarray) -> np.ndarray:
    if len(indices) == 0:
        return fallback.copy()
    return delta_matrix[indices].mean(axis=0)


def _build_steering_frame(
    pair_frame: pd.DataFrame,
    delta_matrix: np.ndarray,
    atlas_features: np.ndarray,
    scope: str,
    neighbors: int,
    steer_scale: float,
) -> tuple[np.ndarray, pd.DataFrame]:
    nn_model = _build_neighbor_index(atlas_features)
    edited = delta_matrix.copy()
    global_same_family: dict[str, np.ndarray] = {}
    global_other_family: dict[str, np.ndarray] = {}

    families = sorted(pair_frame["error_family"].astype(str).unique().tolist())
    for family in families:
        same_indices = np.where(pair_frame["error_family"].astype(str).to_numpy() == family)[0]
        other_indices = np.where(pair_frame["error_family"].astype(str).to_numpy() != family)[0]
        global_same_family[family] = delta_matrix[same_indices].mean(axis=0)
        global_other_family[family] = delta_matrix[other_indices].mean(axis=0)

    rows: list[dict[str, object]] = []
    for row_index in range(len(pair_frame)):
        family = str(pair_frame.iloc[row_index]["error_family"])
        candidate_idx = _candidate_indices(
            row_index=row_index,
            pair_frame=pair_frame,
            atlas_features=atlas_features,
            nn_model=nn_model,
            scope=scope,
            neighbors=neighbors,
        )

        same_local = np.asarray(
            [idx for idx in candidate_idx if str(pair_frame.iloc[idx]["error_family"]) == family],
            dtype=int,
        )
        other_local = np.asarray(
            [idx for idx in candidate_idx if str(pair_frame.iloc[idx]["error_family"]) != family],
            dtype=int,
        )

        source_anchor = _mean_anchor(delta_matrix, same_local, global_same_family[family])
        target_anchor = _mean_anchor(delta_matrix, other_local, global_other_family[family])
        steering_direction = target_anchor - source_anchor
        edited[row_index] = delta_matrix[row_index] + (steer_scale * steering_direction)

        rows.append(
            {
                "row_index": int(row_index),
                "pair_id": str(pair_frame.iloc[row_index]["pair_id"]),
                "base_id": str(pair_frame.iloc[row_index]["base_id"]),
                "topic": str(pair_frame.iloc[row_index]["topic"]),
                "error_family": family,
                "scope": scope,
                "neighbor_pool_size": int(len(candidate_idx)),
                "same_family_neighbor_count": int(len(same_local)),
                "other_family_neighbor_count": int(len(other_local)),
                "source_anchor_norm": float(np.linalg.norm(source_anchor)),
                "target_anchor_norm": float(np.linalg.norm(target_anchor)),
                "steering_direction_norm": float(np.linalg.norm(steering_direction)),
                "delta_norm_before": float(np.linalg.norm(delta_matrix[row_index])),
                "delta_norm_after": float(np.linalg.norm(edited[row_index])),
                "cosine_before_after": float(
                    np.dot(delta_matrix[row_index], edited[row_index])
                    / ((np.linalg.norm(delta_matrix[row_index]) * np.linalg.norm(edited[row_index])) + 1e-12)
                ),
            }
        )
    return edited.astype(np.float32), pd.DataFrame(rows)


def _per_family_probability_frame(
    pair_frame: pd.DataFrame,
    baseline_probs: np.ndarray,
    steered_probs: np.ndarray,
    classes: np.ndarray,
) -> pd.DataFrame:
    class_to_index = {name: idx for idx, name in enumerate(classes.tolist())}
    rows: list[dict[str, object]] = []
    for family, group in pair_frame.groupby("error_family", sort=True):
        family_index = class_to_index[str(family)]
        idx = group.index.to_numpy(dtype=int)
        baseline_family_prob = baseline_probs[idx, family_index]
        steered_family_prob = steered_probs[idx, family_index]
        baseline_best_other = np.max(np.delete(baseline_probs[idx], family_index, axis=1), axis=1)
        steered_best_other = np.max(np.delete(steered_probs[idx], family_index, axis=1), axis=1)
        rows.append(
            {
                "error_family": str(family),
                "sample_count": int(len(idx)),
                "baseline_own_probability_mean": float(baseline_family_prob.mean()),
                "steered_own_probability_mean": float(steered_family_prob.mean()),
                "own_probability_delta": float(steered_family_prob.mean() - baseline_family_prob.mean()),
                "baseline_best_other_probability_mean": float(baseline_best_other.mean()),
                "steered_best_other_probability_mean": float(steered_best_other.mean()),
                "best_other_probability_delta": float(steered_best_other.mean() - baseline_best_other.mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("error_family").reset_index(drop=True)


def _raw_sample_metadata(dataset_path: str) -> pd.DataFrame:
    payload = json.loads(Path(dataset_path).read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    for row in payload:
        sample_id = str(row.get("sample_id", ""))
        base_id = str(row.get("base_id", ""))
        if not base_id and "_" in sample_id:
            parts = sample_id.split("_")
            if len(parts) >= 3:
                base_id = parts[1]
        rows.append(
            {
                "sample_id": sample_id,
                "base_id": base_id,
                "topic": str(row.get("topic", "")),
            }
        )
    return pd.DataFrame(rows).drop_duplicates(subset=["sample_id"])


def main() -> None:
    args = parse_args()
    output_dir = ensure_dir(args.output_dir)

    qa_pairs = load_qa_pairs(args.dataset)
    sample_frame = build_sample_frame(qa_pairs)
    sample_frame = sample_frame.merge(_raw_sample_metadata(args.dataset), on="sample_id", how="left")
    embeddings = embed_texts(sample_frame[args.text_field].tolist(), model_name=args.embedding_model)

    paired = build_paired_delta_matrix(sample_frame, embeddings)
    pair_frame = extract_pair_metadata(paired.pair_frame)
    topic_lookup = (
        sample_frame[["base_id", "topic"]]
        .drop_duplicates(subset=["base_id"])
        .assign(base_id=lambda frame: frame["base_id"].astype(str))
    )
    pair_frame = pair_frame.merge(topic_lookup, on="base_id", how="left")

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
    atlas_features = StandardScaler().fit_transform(
        fingerprint[projection_columns].to_numpy(dtype=np.float32)
    ).astype(np.float32)

    reference_model = _fit_reference_model(delta_matrix, families)
    baseline_preds = reference_model.predict(delta_matrix)
    baseline_probs = reference_model.predict_proba(delta_matrix)
    baseline_metrics = _family_metrics(families, baseline_preds)

    edited_delta, steering_frame = _build_steering_frame(
        pair_frame=pair_frame,
        delta_matrix=delta_matrix,
        atlas_features=atlas_features,
        scope=args.scope,
        neighbors=args.neighbors,
        steer_scale=args.steer_scale,
    )
    steered_preds = reference_model.predict(edited_delta)
    steered_probs = reference_model.predict_proba(edited_delta)
    steered_metrics = _family_metrics(families, steered_preds)

    class_names = reference_model.classes_
    own_prob_index = np.asarray([np.where(class_names == family)[0][0] for family in families], dtype=int)
    baseline_own_prob = baseline_probs[np.arange(len(families)), own_prob_index]
    steered_own_prob = steered_probs[np.arange(len(families)), own_prob_index]

    steering_frame["baseline_prediction"] = baseline_preds
    steering_frame["steered_prediction"] = steered_preds
    steering_frame["prediction_changed"] = baseline_preds != steered_preds
    steering_frame["baseline_own_probability"] = baseline_own_prob
    steering_frame["steered_own_probability"] = steered_own_prob
    steering_frame["own_probability_delta"] = steered_own_prob - baseline_own_prob

    family_probability = _per_family_probability_frame(pair_frame, baseline_probs, steered_probs, class_names)

    steering_frame.to_csv(output_dir / "atlas_guided_steering_samples.csv", index=False)
    family_probability.to_csv(output_dir / "atlas_guided_steering_family_summary.csv", index=False)

    summary = {
        "dataset": args.dataset,
        "embedding_model": args.embedding_model,
        "text_field": args.text_field,
        "delta_mode": args.delta_mode,
        "scope": args.scope,
        "neighbors": int(args.neighbors),
        "steer_scale": float(args.steer_scale),
        "pair_count": int(len(pair_frame)),
        "family_count": int(pair_frame["error_family"].nunique()),
        "baseline_accuracy": baseline_metrics["accuracy"],
        "baseline_macro_f1": baseline_metrics["macro_f1"],
        "steered_accuracy": steered_metrics["accuracy"],
        "steered_macro_f1": steered_metrics["macro_f1"],
        "accuracy_delta": float(steered_metrics["accuracy"] - baseline_metrics["accuracy"]),
        "macro_f1_delta": float(steered_metrics["macro_f1"] - baseline_metrics["macro_f1"]),
        "mean_own_probability_delta": float(np.mean(steered_own_prob - baseline_own_prob)),
        "mean_prediction_changed_fraction": float(np.mean(steering_frame["prediction_changed"].to_numpy(dtype=bool))),
        "mean_same_family_neighbor_count": float(steering_frame["same_family_neighbor_count"].mean()),
        "mean_other_family_neighbor_count": float(steering_frame["other_family_neighbor_count"].mean()),
        "mean_cosine_before_after": float(steering_frame["cosine_before_after"].mean()),
        "best_family_reduction": family_probability.sort_values("own_probability_delta").iloc[0].to_dict(),
        "worst_family_reduction": family_probability.sort_values("own_probability_delta").iloc[-1].to_dict(),
    }
    write_json(output_dir / "summary.json", summary)


if __name__ == "__main__":
    main()
