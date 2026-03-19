from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import adjusted_rand_score

from tis.spatial_semantomics import SpatialSemantomicsConfig, run_spatial_semantomics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare Spatial Semantomics outputs across embedding models")
    parser.add_argument("--input", default="data/spatial_semantomics_corpus_200.json")
    parser.add_argument("--output-dir", default="outputs/spatial_semantomics_model_compare")
    parser.add_argument(
        "--models",
        nargs="+",
        default=[
            "sentence-transformers/all-MiniLM-L6-v2",
            "sentence-transformers/all-mpnet-base-v2",
            "BAAI/bge-small-en-v1.5",
        ],
    )
    parser.add_argument("--clusters", type=int, default=5)
    parser.add_argument("--axes", type=int, default=5)
    return parser.parse_args()


def sanitize_model_name(model_name: str) -> str:
    return model_name.replace("/", "__").replace(":", "_")


def main() -> None:
    args = parse_args()
    texts = json.loads(Path(args.input).read_text(encoding="utf-8"))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cluster_assignments: dict[str, list[int]] = {}
    variance_rows: list[dict] = []

    for model_name in args.models:
        model_dir = output_dir / sanitize_model_name(model_name)
        config = SpatialSemantomicsConfig(
            embedding_model=model_name,
            n_clusters=args.clusters,
            n_axes=args.axes,
            enable_visualization=False,
            enable_llm_interpretation=False,
        )
        results = run_spatial_semantomics(texts=texts, output_dir=model_dir, config=config)
        cluster_assignments[model_name] = [int(value) for value in results["clusters"]]
        variance_frame = results["axis_results"]["explained_variance"].copy()
        variance_frame["model"] = model_name
        variance_rows.extend(variance_frame.to_dict(orient="records"))

    comparison_rows: list[dict] = []
    model_names = list(cluster_assignments)
    for i, left_model in enumerate(model_names):
        for right_model in model_names[i + 1 :]:
            ari = adjusted_rand_score(cluster_assignments[left_model], cluster_assignments[right_model])
            comparison_rows.append(
                {
                    "left_model": left_model,
                    "right_model": right_model,
                    "adjusted_rand_index": ari,
                }
            )

    pd.DataFrame(comparison_rows).to_csv(output_dir / "cluster_agreement.csv", index=False)
    pd.DataFrame(variance_rows).to_csv(output_dir / "axis_variance_comparison.csv", index=False)


if __name__ == "__main__":
    main()
