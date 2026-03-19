from __future__ import annotations

import argparse
import json
from itertools import islice
from pathlib import Path


DOMAIN_TERMS = {
    "biology": [
        "gene expression",
        "single-cell sequencing",
        "protein folding",
        "cancer immunotherapy",
        "genomic mutation",
        "cell signaling",
        "drug target",
        "immune checkpoint",
        "transcriptomic profiling",
        "pathway analysis",
    ],
    "finance": [
        "equity volatility",
        "bond yield curve",
        "portfolio optimization",
        "credit risk",
        "options pricing",
        "macro market signal",
        "asset allocation",
        "rate forecasting",
        "liquidity stress",
        "derivatives exposure",
    ],
    "machine_learning": [
        "transformer training",
        "representation learning",
        "reinforcement learning",
        "vision segmentation",
        "model distillation",
        "federated learning",
        "language modeling",
        "embedding alignment",
        "self-supervised learning",
        "neural architecture search",
    ],
    "physics": [
        "quantum state estimation",
        "particle collision analysis",
        "fluid turbulence modeling",
        "thermodynamic simulation",
        "phase transition detection",
        "wave propagation study",
        "plasma stability analysis",
        "gravitational lensing",
        "materials diffusion model",
        "spectral density estimation",
    ],
    "software": [
        "distributed system tracing",
        "compiler optimization",
        "database indexing",
        "API rate limiting",
        "container orchestration",
        "fault tolerant architecture",
        "latency profiling",
        "event stream processing",
        "schema migration",
        "observability pipeline",
    ],
}

MODIFIERS = [
    "benchmark",
    "simulation",
    "analysis",
    "prediction",
    "forecasting",
    "optimization",
    "modeling",
    "detection",
    "classification",
    "inference",
]

CONTEXTS = [
    "workflow",
    "pipeline",
    "system",
    "framework",
    "dataset",
    "study",
    "platform",
    "experiment",
    "architecture",
    "application",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a larger deterministic Spatial Semantomics corpus")
    parser.add_argument("--size", type=int, default=200, help="Approximate number of phrases to generate")
    parser.add_argument(
        "--output",
        default="data/spatial_semantomics_corpus_200.json",
        help="Output JSON path",
    )
    return parser.parse_args()


def build_corpus(size: int) -> list[str]:
    phrases: list[str] = []
    seen: set[str] = set()

    for domain, terms in DOMAIN_TERMS.items():
        for term in terms:
            for modifier in MODIFIERS:
                phrase = f"{term} {modifier}"
                if phrase not in seen:
                    phrases.append(phrase)
                    seen.add(phrase)
                if len(phrases) >= size:
                    return phrases
            for context in CONTEXTS:
                phrase = f"{term} {context}"
                if phrase not in seen:
                    phrases.append(phrase)
                    seen.add(phrase)
                if len(phrases) >= size:
                    return phrases
            phrase = f"{domain} {term}"
            if phrase not in seen:
                phrases.append(phrase)
                seen.add(phrase)
            if len(phrases) >= size:
                return phrases

    return list(islice(phrases, size))


def main() -> None:
    args = parse_args()
    phrases = build_corpus(args.size)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(phrases, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
