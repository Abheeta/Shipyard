"""Pluggable embedding backend.

Selected by EMBED_BACKEND:
  * tfidf                 — scikit-learn TF-IDF + TruncatedSVD (LSA). No native
                            deps beyond sklearn; must be *fitted* on the corpus
                            at build time (the fitted pipeline is persisted to
                            the index dir). Good lexical-semantic baseline for
                            short captions. DEFAULT for local dev.
  * fastembed             — ONNX runtime, no torch. Smallest footprint; best for
                            Linux hosts (Render). Needs a current VC++ runtime
                            on Windows.
  * sentence-transformers — torch-based. Most portable where torch loads.

Pretrained backends (fastembed / sentence-transformers) ignore fit(); tfidf
requires it. build_index calls fit_embed(); the API calls embed() (loads the
persisted pipeline for tfidf).
"""
from __future__ import annotations

import pickle

import numpy as np

from .config import settings

_backend = None


def _l2(vecs: np.ndarray) -> np.ndarray:
    vecs = np.asarray(vecs, dtype=np.float32)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vecs / norms


class _TfidfLSA:
    def __init__(self) -> None:
        self.pipe = None
        self.dim = settings.tfidf_components

    def _build_pipe(self):
        from sklearn.decomposition import TruncatedSVD
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.pipeline import make_pipeline

        return make_pipeline(
            TfidfVectorizer(
                analyzer="word",
                ngram_range=(1, 2),
                min_df=2,
                max_features=settings.tfidf_max_features,
                sublinear_tf=True,
                stop_words="english",
            ),
            TruncatedSVD(n_components=settings.tfidf_components, random_state=42),
        )

    def fit(self, texts: list[str]) -> np.ndarray:
        self.pipe = self._build_pipe()
        vecs = self.pipe.fit_transform([t or " " for t in texts])
        # shrink the persisted pipeline: SVD components dominate the file size
        svd = self.pipe.steps[-1][1]
        svd.components_ = svd.components_.astype(np.float32)
        if hasattr(svd, "explained_variance_"):
            svd.explained_variance_ = svd.explained_variance_.astype(np.float32)
        settings.embed_model_file.parent.mkdir(parents=True, exist_ok=True)
        with open(settings.embed_model_file, "wb") as f:
            pickle.dump(self.pipe, f, protocol=pickle.HIGHEST_PROTOCOL)
        return _l2(vecs)

    def _ensure_loaded(self) -> None:
        if self.pipe is None:
            if not settings.embed_model_file.exists():
                raise FileNotFoundError(
                    f"{settings.embed_model_file} missing — run scripts.build_index"
                )
            with open(settings.embed_model_file, "rb") as f:
                self.pipe = pickle.load(f)

    def encode(self, texts: list[str]) -> np.ndarray:
        self._ensure_loaded()
        return _l2(self.pipe.transform([t or " " for t in texts]))


class _FastEmbed:
    dim = 384

    def __init__(self) -> None:
        from fastembed import TextEmbedding

        self.model = TextEmbedding(model_name=settings.embed_model)

    def fit(self, texts: list[str]) -> np.ndarray:
        return self.encode(texts)

    def encode(self, texts: list[str]) -> np.ndarray:
        return _l2(np.array(list(self.model.embed(texts, batch_size=settings.embed_batch))))


class _SentenceTransformers:
    def __init__(self) -> None:
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(settings.embed_model)
        self.dim = self.model.get_sentence_embedding_dimension()

    def fit(self, texts: list[str]) -> np.ndarray:
        return self.encode(texts)

    def encode(self, texts: list[str]) -> np.ndarray:
        return _l2(
            self.model.encode(
                texts, batch_size=min(settings.embed_batch, 64),
                normalize_embeddings=True, show_progress_bar=len(texts) > 2000,
            )
        )


def _get_backend():
    global _backend
    if _backend is None:
        name = settings.embed_backend.lower()
        if name == "fastembed":
            _backend = _FastEmbed()
        elif name == "sentence-transformers":
            _backend = _SentenceTransformers()
        else:
            _backend = _TfidfLSA()
    return _backend


def fit_embed(texts: list[str]) -> np.ndarray:
    """Fit (if needed) and embed the whole corpus. Used by build_index."""
    if not texts:
        return np.zeros((0, 1), dtype=np.float32)
    return _get_backend().fit(texts)


def embed(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, 1), dtype=np.float32)
    return _get_backend().encode(texts)


def embed_one(text: str) -> np.ndarray:
    return embed([text])[0]
