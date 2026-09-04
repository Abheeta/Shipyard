"""Topic clustering + near-duplicate detection over the corpus embeddings.

Automatic in the sense that no item is ever hand-tagged:
  * hdbscan  — discovers the cluster count from density; leaves genuine
               one-offs as noise (cluster_id = -1).
  * kmeans   — fixed partition; K auto-picked by a silhouette sweep when
               KMEANS_K = 0.
"""
from __future__ import annotations

import numpy as np

from .config import settings


def cluster(embeddings: np.ndarray) -> np.ndarray:
    method = settings.cluster_method.lower()
    if method == "kmeans":
        return _kmeans(embeddings)
    return _hdbscan(embeddings)


def _hdbscan(embeddings: np.ndarray) -> np.ndarray:
    from sklearn.cluster import HDBSCAN

    model = HDBSCAN(
        min_cluster_size=settings.hdbscan_min_cluster_size,
        metric="euclidean",  # vectors are L2-normalized => monotonic with cosine
        n_jobs=-1,
    )
    labels = model.fit_predict(embeddings)
    return _compact(labels)


def _kmeans(embeddings: np.ndarray) -> np.ndarray:
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    k = settings.kmeans_k
    if k and k > 0:
        return KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(embeddings)

    lo, hi = settings.kmeans_k_min, settings.kmeans_k_max
    sample = embeddings
    if len(embeddings) > 4000:
        idx = np.random.RandomState(42).choice(len(embeddings), 4000, replace=False)
        sample = embeddings[idx]

    best_k, best_score = lo, -1.0
    for cand in range(lo, hi + 1, 2):
        labels = KMeans(n_clusters=cand, n_init=5, random_state=42).fit_predict(sample)
        score = silhouette_score(sample, labels)
        if score > best_score:
            best_k, best_score = cand, score
    print(f"  kmeans auto-K = {best_k} (silhouette {best_score:.3f})")
    return KMeans(n_clusters=best_k, n_init=10, random_state=42).fit_predict(embeddings)


def _compact(labels: np.ndarray) -> np.ndarray:
    """Renumber cluster ids to 0..n-1, keeping -1 (noise) as -1."""
    out = labels.copy()
    uniq = sorted(u for u in set(labels.tolist()) if u != -1)
    remap = {old: new for new, old in enumerate(uniq)}
    for i, v in enumerate(labels):
        out[i] = -1 if v == -1 else remap[v]
    return out


def representative_indices(embeddings: np.ndarray, labels: np.ndarray, per_cluster: int = 10) -> dict[int, list[int]]:
    """Indices closest to each cluster centroid — used for LLM naming."""
    reps: dict[int, list[int]] = {}
    for c in sorted(set(labels.tolist())):
        if c == -1:
            continue
        members = np.where(labels == c)[0]
        centroid = embeddings[members].mean(axis=0)
        order = members[np.argsort(-(embeddings[members] @ centroid))]
        reps[c] = order[:per_cluster].tolist()
    return reps


def near_duplicate_groups(embeddings: np.ndarray, threshold: float = 0.95, block: int = 1024) -> list[list[int]]:
    """Union-find over pairs with cosine similarity >= threshold. Block-wise so
    the full N×N matrix is never materialized."""
    n = len(embeddings)
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    for start in range(0, n, block):
        end = min(start + block, n)
        sims = embeddings[start:end] @ embeddings.T  # (block, n)
        for r in range(end - start):
            i = start + r
            hits = np.where(sims[r, i + 1 :] >= threshold)[0]
            for j in hits:
                union(i, i + 1 + int(j))

    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return [sorted(g) for g in groups.values() if len(g) > 1]
