from __future__ import annotations

from typing import Sequence

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - handled at runtime
    SentenceTransformer = None  # type: ignore[assignment]


def load_embedder(model_name: str) -> SentenceTransformer:
    if SentenceTransformer is None:
        raise ImportError("sentence-transformers is not installed")
    return SentenceTransformer(model_name)


def embed_with_hashing(texts: Sequence[str], normalize: bool = True) -> np.ndarray:
    vectorizer = HashingVectorizer(
        n_features=384,
        alternate_sign=False,
        norm="l2" if normalize else None,
        ngram_range=(1, 2),
    )
    matrix = vectorizer.transform(list(texts))
    return matrix.astype(np.float32).toarray()


def embed_texts(
    texts: Sequence[str],
    model_name: str,
    normalize: bool = True,
    batch_size: int = 32,
) -> np.ndarray:
    if model_name == "local-hashing":
        return embed_with_hashing(texts, normalize=normalize)

    model = load_embedder(model_name)
    try:
        vectors = model.encode(
            list(texts),
            batch_size=batch_size,
            normalize_embeddings=normalize,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return np.asarray(vectors, dtype=np.float32)
    except Exception as exc:
        if "local-hashing" in model_name:
            raise
        raise RuntimeError(
            f"Failed to load embedding model '{model_name}'. "
            "Use --embedding-model local-hashing for a fully offline baseline."
        ) from exc
