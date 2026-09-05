"""Retrieval: metadata pre-filter -> cosine rerank -> MMR diversification.

All in-process against the in-memory corpus. No vector DB.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from dataclasses import dataclass, field

import numpy as np

from . import state
from .corpus import corpus
from .embeddings import embed_one

CURRENT_YEAR = datetime.now(timezone.utc).year


@dataclass
class Query:
    q: str | None = None
    source: str = "both"          # saved | liked | both
    time_preset: str | None = None  # this_year | last_year | older | all
    year_from: int | None = None
    year_to: int | None = None
    creator: str | None = None
    cluster_id: int | None = None
    tags: tuple[str, ...] = ()      # AND match against item.tags
    include_ads: bool = True
    actionable: str = "all"       # all | actionable | info
    status: str | None = None     # saved | scheduled | resolved
    intent: str | None = None     # try | learn | do_later | remember — user-set only, no default
    sort: str = "relevance"       # relevance | recent | oldest
    offset: int = 0
    limit: int = 40
    mmr: bool = True


@dataclass
class Result:
    total: int
    positions: list[int]
    scores: dict[int, float] = field(default_factory=dict)


def _year_mask(df, qy: Query) -> np.ndarray:
    years = df["year"].to_numpy()
    if qy.time_preset == "this_year":
        return years == CURRENT_YEAR
    if qy.time_preset == "last_year":
        return years == CURRENT_YEAR - 1
    if qy.time_preset == "older":
        return years < CURRENT_YEAR - 1
    m = np.ones(len(df), dtype=bool)
    if qy.year_from is not None:
        m &= years >= qy.year_from
    if qy.year_to is not None:
        m &= years <= qy.year_to
    return m


def _prefilter(qy: Query) -> np.ndarray:
    df = corpus.df
    m = np.ones(len(df), dtype=bool)

    if qy.source in ("saved", "liked"):
        src = df["source"].to_numpy()
        if qy.source == "saved":
            promoted = state.promoted_ids()
            ids = df["id"].to_numpy()
            m &= (src == "saved") | np.isin(ids, list(promoted))
        else:
            m &= src == "liked"

    m &= _year_mask(df, qy)

    if qy.creator:
        m &= df["creator"].to_numpy() == qy.creator
    if qy.cluster_id is not None:
        m &= df["cluster_id"].to_numpy() == qy.cluster_id
    if qy.tags:
        wanted = {t.lower() for t in qy.tags}
        tag_col = df["tags"].to_numpy()
        keep = np.array(
            [wanted.issubset({t.lower() for t in (row if row is not None else [])}) for row in tag_col],
            dtype=bool,
        )
        m &= keep
    if not qy.include_ads:
        m &= ~df["is_ad"].to_numpy().astype(bool)
    if qy.actionable == "actionable":
        m &= df["is_actionable"].to_numpy().astype(bool)
    elif qy.actionable == "info":
        m &= ~df["is_actionable"].to_numpy().astype(bool)

    if qy.status or qy.intent:
        ids = df["id"].to_numpy()
        states = state.get_states(ids[m].tolist())
        if qy.status:
            want = qy.status
            keep = np.array(
                [states.get(i, {}).get("status", "saved") == want for i in ids],
                dtype=bool,
            )
            m &= keep
        if qy.intent:
            want_intent = qy.intent
            keep = np.array(
                [states.get(i, {}).get("user_intent") == want_intent for i in ids],
                dtype=bool,
            )
            m &= keep

    return m


def _mmr(query_vec: np.ndarray, cand_pos: np.ndarray, sims: np.ndarray, k: int, lam: float = 0.7) -> list[int]:
    selected: list[int] = []
    remaining = list(range(len(cand_pos)))
    vecs = corpus.embeddings[cand_pos]
    while remaining and len(selected) < k:
        if not selected:
            best = int(np.argmax(sims[remaining]))
            selected.append(remaining.pop(best))
            continue
        sel_vecs = vecs[selected]
        best_i, best_score = None, -1e9
        for idx in remaining:
            div = float(np.max(vecs[idx] @ sel_vecs.T))
            score = lam * sims[idx] - (1 - lam) * div
            if score > best_score:
                best_i, best_score = idx, score
        selected.append(best_i)
        remaining.remove(best_i)
    return selected


def run(qy: Query) -> Result:
    mask = _prefilter(qy)
    positions = np.where(mask)[0]
    if len(positions) == 0:
        return Result(total=0, positions=[])

    use_semantic = bool(qy.q and qy.q.strip()) and qy.sort == "relevance"

    if use_semantic:
        qvec = embed_one(qy.q.strip())
        sims = (corpus.embeddings[positions] @ qvec) * corpus.text_weight[positions]
        order = np.argsort(-sims)
        # substring safety net for very short / literal queries
        if len(qy.q.strip()) <= 3 or sims.max() < 0.15:
            ql = qy.q.strip().lower()
            hay = (corpus.df["caption"].str.lower() + " " + corpus.df["creator"].str.lower()).to_numpy()
            sub = np.array([ql in (hay[p] or "") for p in positions])
            order = np.concatenate([np.where(sub)[0], np.where(~sub)[0][np.argsort(-sims[~sub])]])

        top = order[: max(qy.offset + qy.limit, 200)]
        if qy.mmr and len(top) > qy.limit:
            reranked = _mmr(qvec, positions[top], sims[top], k=min(len(top), qy.offset + qy.limit))
            top = top[reranked]
        page = top[qy.offset : qy.offset + qy.limit]
        pos_list = positions[page].tolist()
        scores = {int(positions[i]): float(sims[i]) for i in top}
        return Result(total=len(positions), positions=pos_list, scores=scores)

    # non-semantic: order by time
    ts = corpus.df["timestamp"].to_numpy()[positions]
    order = np.argsort(ts if qy.sort == "oldest" else -ts)
    page = order[qy.offset : qy.offset + qy.limit]
    return Result(total=len(positions), positions=positions[page].tolist())


def top_creators(qy: Query, offset: int = 0, limit: int = 30) -> tuple[list[dict], int]:
    """Creators ranked within the current filter selection (topic/tags/source/
    etc.) — powers "who posts about this" discovery, as opposed to the
    static global top-creator facets computed once at index build time.
    Paginated: returns (page, total_distinct_creators)."""
    mask = _prefilter(qy)
    df = corpus.df[mask]
    df = df[df["creator"].astype(bool)]
    if qy.q:
        needle = qy.q.strip().lower()
        df = df[
            df["creator"].str.lower().str.contains(needle, regex=False)
            | df["creator_name"].fillna("").str.lower().str.contains(needle, regex=False)
        ]
    if df.empty:
        return [], 0
    g = (
        df.groupby("creator")
        .agg(
            count=("id", "size"),
            creator_name=("creator_name", "first"),
            saved_count=("source", lambda s: int((s == "saved").sum())),
            liked_count=("source", lambda s: int((s == "liked").sum())),
        )
        .sort_values("count", ascending=False)
        .reset_index()
    )
    total = len(g)
    page = g.iloc[offset : offset + limit]
    rows = [
        {
            "creator": r.creator,
            "creator_name": r.creator_name,
            "count": int(r.count),
            "saved_count": r.saved_count,
            "liked_count": r.liked_count,
        }
        for r in page.itertuples()
    ]
    return rows, total


def more_like(item_id: str, k: int = 12) -> list[int]:
    p = corpus.pos(item_id)
    if p is None:
        return []
    sims = corpus.embeddings @ corpus.embeddings[p]
    order = np.argsort(-sims)
    return [int(i) for i in order if int(i) != p][:k]
