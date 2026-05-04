from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch
from torch import nn
from torch.nn import functional as F

from tis.embedding import embed_texts
from tis.hallucination_diff.dataset import build_sample_frame, load_qa_pairs
from tis.hallucination_diff.family_subspace import (
    extract_pair_metadata,
    fit_family_subspaces,
    group_cv_multiclass,
    principal_angle_frame,
    projection_fingerprint_frame,
    residualize_by_base,
    transfer_frame,
)
from tis.hallucination_diff.paired_delta import build_paired_delta_matrix
from tis.io_utils import ensure_dir, records_to_parquet, write_json


class ProjectionHead(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return F.normalize(self.net(inputs), dim=-1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Contrastive family projection audit over paired deltas.")
    parser.add_argument("--dataset", required=True, help="Path to JSON list of question/answer pairs")
    parser.add_argument(
        "--output-dir",
        default="outputs/hallucination_diff/family_contrastive_projection",
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
    parser.add_argument("--epochs", type=int, default=300, help="Contrastive training epochs")
    parser.add_argument("--learning-rate", type=float, default=1e-3, help="Optimizer learning rate")
    parser.add_argument("--weight-decay", type=float, default=1e-4, help="Optimizer weight decay")
    parser.add_argument("--temperature", type=float, default=0.15, help="SupCon temperature")
    parser.add_argument("--hidden-dim", type=int, default=128, help="Projection head hidden dimension")
    parser.add_argument("--output-dim", type=int, default=32, help="Projection head output dimension")
    parser.add_argument("--variance-threshold", type=float, default=0.9, help="Intrinsic rank threshold")
    parser.add_argument("--max-subspace-dim", type=int, default=6, help="Family basis comparison dimension cap")
    parser.add_argument("--device", default="cpu", help="Training device")
    return parser.parse_args()


def _supervised_contrastive_loss(
    embeddings: torch.Tensor,
    family_ids: torch.Tensor,
    base_ids: torch.Tensor,
    temperature: float,
) -> torch.Tensor:
    similarity = embeddings @ embeddings.T / temperature
    similarity = similarity - torch.max(similarity, dim=1, keepdim=True).values
    logits_mask = ~torch.eye(len(embeddings), dtype=torch.bool, device=embeddings.device)
    same_family = family_ids[:, None] == family_ids[None, :]
    different_base = base_ids[:, None] != base_ids[None, :]
    positive_mask = same_family & different_base & logits_mask

    exp_logits = torch.exp(similarity) * logits_mask
    log_prob = similarity - torch.log(exp_logits.sum(dim=1, keepdim=True) + 1e-12)

    positive_count = positive_mask.sum(dim=1)
    valid = positive_count > 0
    if not torch.any(valid):
        raise ValueError("No valid positive pairs were found for supervised contrastive training.")

    mean_log_prob_pos = (positive_mask.float() * log_prob).sum(dim=1) / positive_count.clamp(min=1)
    loss = -mean_log_prob_pos[valid].mean()
    return loss


def _plot_training_curve(history: list[float], output_path: Path) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    plt.figure(figsize=(8, 5))
    plt.plot(np.arange(1, len(history) + 1), history, color="#4c72b0", linewidth=2)
    plt.xlabel("Epoch")
    plt.ylabel("SupCon loss")
    plt.title("Contrastive Training Curve")
    plt.tight_layout()
    plt.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close()


def _plot_projection_margin(
    baseline_frame: pd.DataFrame,
    contrastive_frame: pd.DataFrame,
    output_path: Path,
) -> None:
    sns.set_theme(style="whitegrid", context="talk")
    combined = pd.concat(
        [
            baseline_frame.assign(space="baseline"),
            contrastive_frame.assign(space="contrastive"),
        ],
        ignore_index=True,
    )
    plt.figure(figsize=(10, 6))
    sns.boxplot(
        data=combined,
        x="space",
        y="projection_margin",
        hue="space",
        palette={"baseline": "#9ecae1", "contrastive": "#3182bd"},
        legend=False,
    )
    sns.stripplot(
        data=combined,
        x="space",
        y="projection_margin",
        color="black",
        size=3,
        alpha=0.45,
    )
    plt.xlabel("")
    plt.ylabel("Own minus best-other projection energy")
    plt.title("Projection Margin Before vs After Contrastive Training")
    plt.tight_layout()
    plt.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close()


def _run_subspace_metrics(
    features: np.ndarray,
    pair_frame: pd.DataFrame,
    variance_threshold: float,
    max_subspace_dim: int,
) -> dict[str, object]:
    families = pair_frame["error_family"].astype(str).tolist()
    base_ids = pair_frame["base_id"].astype(str).tolist()

    subspaces, family_summary = fit_family_subspaces(
        features,
        families,
        variance_threshold=variance_threshold,
        max_subspace_dim=max_subspace_dim,
    )
    principal_angles = principal_angle_frame(subspaces)
    transfer = transfer_frame(features, families, subspaces)
    fingerprint = projection_fingerprint_frame(features, families, subspaces)
    projection_features = fingerprint[[column for column in fingerprint.columns if column.startswith("proj_")]].to_numpy()

    embedding_probe = group_cv_multiclass(features, families, base_ids)
    projection_probe = group_cv_multiclass(projection_features, families, base_ids)
    within_transfer = transfer.loc[transfer["source_family"] == transfer["target_family"], "transfer_r2"]
    cross_transfer = transfer.loc[transfer["source_family"] != transfer["target_family"], "transfer_r2"]
    off_diag_angles = principal_angles.loc[
        principal_angles["family_left"] != principal_angles["family_right"],
        "mean_principal_angle_deg",
    ]

    return {
        "family_summary": family_summary,
        "principal_angles": principal_angles,
        "transfer": transfer,
        "fingerprint": fingerprint,
        "embedding_probe": embedding_probe,
        "projection_probe": projection_probe,
        "mean_rank_at_threshold": float(family_summary["rank_at_threshold"].mean()),
        "mean_effective_rank": float(family_summary["effective_rank"].mean()),
        "mean_within_transfer_r2": float(within_transfer.mean()),
        "mean_cross_transfer_r2": float(cross_transfer.mean()),
        "mean_projection_margin": float(fingerprint["projection_margin"].mean()),
        "mean_own_projection_energy": float(fingerprint["own_family_projection_energy"].mean()),
        "mean_best_other_projection_energy": float(fingerprint["best_other_projection_energy"].mean()),
        "mean_off_diagonal_angle_deg": float(off_diag_angles.mean()),
    }


def _write_metric_bundle(output_dir: Path, prefix: str, bundle: dict[str, object]) -> None:
    family_summary = bundle["family_summary"]
    principal_angles = bundle["principal_angles"]
    transfer = bundle["transfer"]
    fingerprint = bundle["fingerprint"]
    assert isinstance(family_summary, pd.DataFrame)
    assert isinstance(principal_angles, pd.DataFrame)
    assert isinstance(transfer, pd.DataFrame)
    assert isinstance(fingerprint, pd.DataFrame)

    family_summary.to_csv(output_dir / f"{prefix}_family_rank_summary.csv", index=False)
    principal_angles.to_csv(output_dir / f"{prefix}_family_principal_angles.csv", index=False)
    transfer.to_csv(output_dir / f"{prefix}_family_transfer_r2.csv", index=False)
    fingerprint.to_csv(output_dir / f"{prefix}_projection_fingerprint.csv", index=False)


def main() -> None:
    args = parse_args()
    output_dir = ensure_dir(args.output_dir)

    qa_pairs = load_qa_pairs(args.dataset)
    sample_frame = build_sample_frame(qa_pairs)
    embeddings = embed_texts(sample_frame[args.text_field].tolist(), model_name=args.embedding_model)

    paired = build_paired_delta_matrix(sample_frame, embeddings)
    pair_frame = extract_pair_metadata(paired.pair_frame)
    residual_delta = residualize_by_base(paired.delta_matrix, pair_frame["base_id"].tolist())
    baseline_features = residual_delta if args.delta_mode == "residual" else paired.delta_matrix
    records_to_parquet(output_dir / "delta_pair_index.parquet", pair_frame.to_dict(orient="records"))

    family_codes = pd.Categorical(pair_frame["error_family"])
    base_codes = pd.Categorical(pair_frame["base_id"])

    tensor_inputs = torch.tensor(baseline_features, dtype=torch.float32, device=args.device)
    family_ids = torch.tensor(family_codes.codes, dtype=torch.long, device=args.device)
    base_ids = torch.tensor(base_codes.codes, dtype=torch.long, device=args.device)

    model = ProjectionHead(
        input_dim=baseline_features.shape[1],
        hidden_dim=args.hidden_dim,
        output_dim=args.output_dim,
    ).to(args.device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)

    history: list[float] = []
    model.train()
    for _ in range(args.epochs):
        optimizer.zero_grad(set_to_none=True)
        projected = model(tensor_inputs)
        loss = _supervised_contrastive_loss(projected, family_ids, base_ids, args.temperature)
        loss.backward()
        optimizer.step()
        history.append(float(loss.item()))

    model.eval()
    with torch.no_grad():
        contrastive_features = model(tensor_inputs).cpu().numpy().astype(np.float32)

    np.save(output_dir / "baseline_delta_embeddings.npy", baseline_features)
    np.save(output_dir / "contrastive_delta_embeddings.npy", contrastive_features)
    torch.save(model.state_dict(), output_dir / "contrastive_projection_head.pt")

    baseline_bundle = _run_subspace_metrics(
        baseline_features,
        pair_frame,
        variance_threshold=args.variance_threshold,
        max_subspace_dim=args.max_subspace_dim,
    )
    contrastive_bundle = _run_subspace_metrics(
        contrastive_features,
        pair_frame,
        variance_threshold=args.variance_threshold,
        max_subspace_dim=args.max_subspace_dim,
    )

    _write_metric_bundle(output_dir, "baseline", baseline_bundle)
    _write_metric_bundle(output_dir, "contrastive", contrastive_bundle)
    _plot_training_curve(history, output_dir / "contrastive_training_curve.png")
    _plot_projection_margin(
        baseline_bundle["fingerprint"],
        contrastive_bundle["fingerprint"],
        output_dir / "projection_margin_comparison.png",
    )

    comparison = {
        "dataset": args.dataset,
        "embedding_model": args.embedding_model,
        "text_field": args.text_field,
        "delta_mode": args.delta_mode,
        "pair_count": int(len(pair_frame)),
        "family_count": int(pair_frame["error_family"].nunique()),
        "base_count": int(pair_frame["base_id"].nunique()),
        "epochs": int(args.epochs),
        "learning_rate": float(args.learning_rate),
        "weight_decay": float(args.weight_decay),
        "temperature": float(args.temperature),
        "hidden_dim": int(args.hidden_dim),
        "output_dim": int(args.output_dim),
        "baseline_embedding_probe_accuracy": baseline_bundle["embedding_probe"]["accuracy"],
        "baseline_embedding_probe_macro_f1": baseline_bundle["embedding_probe"]["macro_f1"],
        "baseline_projection_probe_accuracy": baseline_bundle["projection_probe"]["accuracy"],
        "baseline_projection_probe_macro_f1": baseline_bundle["projection_probe"]["macro_f1"],
        "contrastive_embedding_probe_accuracy": contrastive_bundle["embedding_probe"]["accuracy"],
        "contrastive_embedding_probe_macro_f1": contrastive_bundle["embedding_probe"]["macro_f1"],
        "contrastive_projection_probe_accuracy": contrastive_bundle["projection_probe"]["accuracy"],
        "contrastive_projection_probe_macro_f1": contrastive_bundle["projection_probe"]["macro_f1"],
        "baseline_mean_projection_margin": baseline_bundle["mean_projection_margin"],
        "contrastive_mean_projection_margin": contrastive_bundle["mean_projection_margin"],
        "baseline_mean_within_transfer_r2": baseline_bundle["mean_within_transfer_r2"],
        "contrastive_mean_within_transfer_r2": contrastive_bundle["mean_within_transfer_r2"],
        "baseline_mean_cross_transfer_r2": baseline_bundle["mean_cross_transfer_r2"],
        "contrastive_mean_cross_transfer_r2": contrastive_bundle["mean_cross_transfer_r2"],
        "baseline_mean_off_diagonal_angle_deg": baseline_bundle["mean_off_diagonal_angle_deg"],
        "contrastive_mean_off_diagonal_angle_deg": contrastive_bundle["mean_off_diagonal_angle_deg"],
        "final_training_loss": float(history[-1]),
    }
    write_json(output_dir / "summary.json", comparison)


if __name__ == "__main__":
    main()
