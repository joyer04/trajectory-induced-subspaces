from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from tis.analysis import cluster_directions, run_pca, summarize_by_task
from tis.embedding import embed_texts
from tis.io_utils import ensure_dir, read_jsonl, records_to_parquet, write_json
from tis.trajectories import build_delta_vectors, flatten_steps


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Baseline trajectory-induced subspace pipeline")
    parser.add_argument(
        "--traces",
        default="data/raw/traces.jsonl",
        help="Path to reasoning traces JSONL",
    )
    parser.add_argument(
        "--output-dir",
        default="data/processed",
        help="Directory for processed outputs",
    )
    parser.add_argument(
        "--embedding-model",
        default="intfloat/e5-small-v2",
        help="Sentence-transformers model name",
    )
    parser.add_argument(
        "--clusters",
        type=int,
        default=5,
        help="Number of direction clusters",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    traces = read_jsonl(args.traces)
    step_texts, step_index = flatten_steps(traces)
    if not step_texts:
        raise ValueError("No reasoning steps found in the traces file.")

    output_dir = ensure_dir(args.output_dir)

    embeddings = embed_texts(step_texts, model_name=args.embedding_model)
    np.save(output_dir / "step_embeddings.npy", embeddings)
    records_to_parquet(output_dir / "trajectory_index.parquet", step_index)

    delta_vectors, delta_index = build_delta_vectors(embeddings, step_index)
    np.save(output_dir / "delta_vectors.npy", delta_vectors)
    records_to_parquet(output_dir / "delta_index.parquet", delta_index)

    pca_summary = run_pca(delta_vectors)
    clustering = cluster_directions(delta_vectors, n_clusters=args.clusters)
    task_cluster_summary = summarize_by_task(delta_index, clustering["labels"])

    summary = {
        "trace_count": len(traces),
        "step_count": len(step_texts),
        "delta_count": int(len(delta_vectors)),
        "embedding_model": args.embedding_model,
        "pca_explained_variance_ratio": pca_summary["explained_variance_ratio"],
        "task_cluster_summary": task_cluster_summary,
    }
    write_json(output_dir / "analysis_summary.json", summary)


if __name__ == "__main__":
    main()
