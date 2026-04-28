from __future__ import annotations

import argparse
import json
from pathlib import Path

from tis.spatial_semantomics import SpatialSemantomicsConfig, run_spatial_semantomics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Spatial Semantomics experiment")
    parser.add_argument(
        "--input",
        default="data/spatial_semantomics_texts.json",
        help="Path to a JSON list of texts",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/spatial_semantomics",
        help="Directory for plots and tables",
    )
    parser.add_argument(
        "--embedding-model",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="SentenceTransformer model name",
    )
    parser.add_argument(
        "--ollama-model",
        default="llama3.2:latest",
        help="Local Ollama model for interpretation",
    )
    parser.add_argument(
        "--clusters",
        type=int,
        default=3,
        help="Number of semantic domain clusters",
    )
    parser.add_argument(
        "--axes",
        type=int,
        default=5,
        help="Number of semantic axes to discover",
    )
    parser.add_argument(
        "--neighbors",
        type=int,
        default=10,
        help="k for the semantic kNN graph",
    )
    parser.add_argument(
        "--disable-visualization",
        action="store_true",
        help="Skip UMAP figure generation",
    )
    parser.add_argument(
        "--disable-llm-interpretation",
        action="store_true",
        help="Skip Ollama-based cluster and axis labeling",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    texts = json.loads(Path(args.input).read_text(encoding="utf-8"))
    config = SpatialSemantomicsConfig(
        embedding_model=args.embedding_model,
        n_neighbors=args.neighbors,
        n_axes=args.axes,
        n_clusters=args.clusters,
        ollama_model=args.ollama_model,
        enable_visualization=not args.disable_visualization,
        enable_llm_interpretation=not args.disable_llm_interpretation,
    )
    run_spatial_semantomics(texts=texts, output_dir=args.output_dir, config=config)


if __name__ == "__main__":
    main()
