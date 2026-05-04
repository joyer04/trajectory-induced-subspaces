from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from tis.embedding import embed_texts
from tis.hallucination_diff.dataset import build_sample_frame, load_qa_pairs
from tis.hallucination_diff.paired_delta import build_paired_delta_matrix
from tis.hallucination_diff.family_subspace import (
    extract_pair_metadata,
    fit_family_subspaces,
    principal_angle_frame,
    residualize_by_base,
    transfer_frame,
)
from tis.io_utils import ensure_dir, records_to_parquet, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit family-specific subspace structure over paired deltas.")
    parser.add_argument("--dataset", required=True, help="Path to JSON list of question/answer pairs")
    parser.add_argument(
        "--output-dir",
        default="outputs/hallucination_diff/family_subspace_audit",
        help="Directory for audit outputs",
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
        help="Whether to audit raw paired deltas or base-residual deltas",
    )
    parser.add_argument(
        "--variance-threshold",
        type=float,
        default=0.9,
        help="Explained variance target used to define intrinsic rank",
    )
    parser.add_argument(
        "--max-subspace-dim",
        type=int,
        default=6,
        help="Upper bound for family basis dimension used in comparisons",
    )
    return parser.parse_args()


def _plot_rank_bar(family_summary: pd.DataFrame, output_path: Path) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    frame = family_summary.copy()
    plt.figure(figsize=(9, 6))
    ax = sns.barplot(data=frame, x="error_family", y="rank_at_threshold", color="#4c72b0")
    ax.set_title("Family Intrinsic Rank")
    ax.set_xlabel("")
    ax.set_ylabel("Components for 90% variance")
    plt.tight_layout()
    plt.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close()


def _plot_heatmap(matrix: pd.DataFrame, title: str, output_path: Path, fmt: str = ".2f") -> None:
    sns.set_theme(style="whitegrid", context="talk")
    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix, annot=True, fmt=fmt, cmap="viridis", square=True, cbar=True)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close()


def main() -> None:
    args = parse_args()
    output_dir = ensure_dir(args.output_dir)

    qa_pairs = load_qa_pairs(args.dataset)
    sample_frame = build_sample_frame(qa_pairs)
    embeddings = embed_texts(sample_frame[args.text_field].tolist(), model_name=args.embedding_model)

    paired = build_paired_delta_matrix(sample_frame, embeddings)
    pair_frame = _extract_pair_metadata(paired.pair_frame)
    residual_delta = _residualize_by_base(paired.delta_matrix, pair_frame["base_id"].tolist())
    delta_matrix = residual_delta if args.delta_mode == "residual" else paired.delta_matrix

    pair_frame[f"{args.delta_mode}_delta_norm"] = np.linalg.norm(delta_matrix, axis=1)
    records_to_parquet(output_dir / "delta_pair_index.parquet", pair_frame.to_dict(orient="records"))

    families = pair_frame["error_family"].astype(str).tolist()
    subspaces, family_summary = _fit_family_subspaces(
        delta_matrix,
        families,
        variance_threshold=args.variance_threshold,
        max_subspace_dim=args.max_subspace_dim,
    )
    principal_angles = _principal_angle_frame(subspaces)
    transfer = _transfer_frame(delta_matrix, families, subspaces)

    principal_angle_matrix = principal_angles.pivot(
        index="family_left",
        columns="family_right",
        values="mean_principal_angle_deg",
    )
    transfer_matrix = transfer.pivot(
        index="source_family",
        columns="target_family",
        values="transfer_r2",
    )

    family_summary.to_csv(output_dir / "family_rank_summary.csv", index=False)
    principal_angles.to_csv(output_dir / "family_principal_angles.csv", index=False)
    transfer.to_csv(output_dir / "family_transfer_r2.csv", index=False)
    principal_angle_matrix.to_csv(output_dir / "family_principal_angle_matrix.csv")
    transfer_matrix.to_csv(output_dir / "family_transfer_r2_matrix.csv")

    _plot_rank_bar(family_summary, output_dir / "family_intrinsic_rank.png")
    _plot_heatmap(
        principal_angle_matrix,
        "Family Mean Principal Angle (deg)",
        output_dir / "family_principal_angle_heatmap.png",
    )
    _plot_heatmap(
        transfer_matrix,
        "Cross-Family Subspace Transfer R2",
        output_dir / "family_transfer_r2_heatmap.png",
    )

    within_transfer = transfer.loc[transfer["source_family"] == transfer["target_family"], "transfer_r2"]
    cross_transfer = transfer.loc[transfer["source_family"] != transfer["target_family"], "transfer_r2"]

    summary = {
        "dataset": args.dataset,
        "embedding_model": args.embedding_model,
        "text_field": args.text_field,
        "delta_mode": args.delta_mode,
        "pair_count": int(len(pair_frame)),
        "family_count": int(pair_frame["error_family"].nunique()),
        "base_count": int(pair_frame["base_id"].nunique()),
        "variance_threshold": float(args.variance_threshold),
        "max_subspace_dim": int(args.max_subspace_dim),
        "mean_rank_at_threshold": float(family_summary["rank_at_threshold"].mean()),
        "mean_effective_rank": float(family_summary["effective_rank"].mean()),
        "mean_within_family_transfer_r2": float(within_transfer.mean()),
        "mean_cross_family_transfer_r2": float(cross_transfer.mean()),
        "mean_off_diagonal_principal_angle_deg": float(
            principal_angles.loc[
                principal_angles["family_left"] != principal_angles["family_right"],
                "mean_principal_angle_deg",
            ].mean()
        ),
    }
    write_json(output_dir / "summary.json", summary)


if __name__ == "__main__":
    main()
