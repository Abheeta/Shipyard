"""HTTP surface. Thin — all logic lives in search / state / llm / corpus."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException, Query as Q

from . import llm, state
from .corpus import corpus
from .models import (
    AskCitation,
    AskRequest,
    AskResponse,
    Facets,
    Item,
    ItemPatch,
    SearchResponse,
)
from .search import Query, more_like, run

router = APIRouter(prefix="/api")


def _hydrate(pos_list: list[int], scores: dict[int, float] | None = None) -> list[Item]:
    rows = corpus.rows_at(pos_list)
    ids = [r["id"] for r in rows]
    states = state.get_states(ids)
    out: list[Item] = []
    for r, p in zip(rows, pos_list):
        st = states.get(r["id"], {"status": "saved"})
        r["state"] = {
            "user_note": st.get("user_note"),
            "user_intent": st.get("user_intent"),
            "scheduled_at": st.get("scheduled_at"),
            "status": st.get("status", "saved"),
            "resolved_at": st.get("resolved_at"),
            "updated_at": st.get("updated_at"),
        }
        if scores and p in scores:
            r["score"] = round(scores[p], 4)
        out.append(Item(**r))
    return out


@router.get("/health")
def health() -> dict:
    return {"ok": True, "items": len(corpus), "llm": corpus.facets.get("llm_enabled", False)}


@router.get("/search", response_model=SearchResponse)
def search(
    q: str | None = None,
    source: str = "both",
    time_preset: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    creator: str | None = None,
    cluster_id: int | None = None,
    tags: list[str] = Q([]),
    include_ads: bool = True,
    actionable: str = "all",
    status: str | None = None,
    sort: str = "relevance",
    offset: int = 0,
    limit: int = Q(40, le=120),
) -> SearchResponse:
    res = run(
        Query(
            q=q, source=source, time_preset=time_preset, year_from=year_from,
            year_to=year_to, creator=creator, cluster_id=cluster_id,
            tags=tuple(tags), include_ads=include_ads, actionable=actionable,
            status=status, sort=sort, offset=offset, limit=limit,
        )
    )
    return SearchResponse(
        total=res.total, offset=offset, limit=limit,
        items=_hydrate(res.positions, res.scores),
    )


@router.get("/items/{item_id}", response_model=Item)
def get_item(item_id: str) -> Item:
    if corpus.pos(item_id) is None:
        raise HTTPException(404, "item not found")
    return _hydrate([corpus.pos(item_id)])[0]


@router.get("/items/{item_id}/similar", response_model=SearchResponse)
def similar(item_id: str, limit: int = Q(12, le=50)) -> SearchResponse:
    if corpus.pos(item_id) is None:
        raise HTTPException(404, "item not found")
    pos_list = more_like(item_id, k=limit)
    return SearchResponse(total=len(pos_list), offset=0, limit=limit, items=_hydrate(pos_list))


@router.patch("/items/{item_id}", response_model=Item)
def patch_item(item_id: str, patch: ItemPatch) -> Item:
    if corpus.pos(item_id) is None:
        raise HTTPException(404, "item not found")
    fields = patch.model_dump(exclude_unset=True)
    unset = {k for k in ("user_note", "user_intent", "scheduled_at") if k in fields and fields[k] is None}

    if fields.get("promote_to_saved"):
        state.promote(item_id)

    state.patch_state(
        item_id,
        user_note=fields.get("user_note"),
        user_intent=fields.get("user_intent").value if hasattr(fields.get("user_intent"), "value") else fields.get("user_intent"),
        scheduled_at=fields.get("scheduled_at"),
        status=fields.get("status").value if hasattr(fields.get("status"), "value") else fields.get("status"),
        _unset=unset,
    )
    return _hydrate([corpus.pos(item_id)])[0]


@router.get("/today", response_model=SearchResponse)
def today(on: date | None = None) -> SearchResponse:
    ids = state.today_ids(on)
    pos_list = [corpus.pos(i) for i in ids if corpus.pos(i) is not None]
    return SearchResponse(total=len(pos_list), offset=0, limit=len(pos_list), items=_hydrate(pos_list))


@router.get("/facets", response_model=Facets)
def facets() -> Facets:
    f = corpus.facets
    sizes = f.get("cluster_sizes", {})
    return Facets(
        total_items=f.get("total_items", len(corpus)),
        saved_count=f.get("saved_count", 0),
        liked_count=f.get("liked_count", 0),
        unique_creators=f.get("unique_creators", 0),
        unique_creators_saved=f.get("unique_creators_saved", 0),
        clusters=sorted(
            [
                {"cluster_id": cid, "name": name,
                 "size": sizes.get(str(cid)) or sizes.get(cid, 0)}
                for cid, name in corpus.cluster_names.items()
            ],
            key=lambda c: -c["size"],
        ),
        top_creators_saved=f.get("top_creators_saved", []),
        top_creators_liked=f.get("top_creators_liked", []),
        top_creators_combined=f.get("top_creators_combined", []),
        top_tags=f.get("top_tags", []),
        like_save_gap=f.get("like_save_gap", []),
        year_counts=f.get("year_counts", {}),
        cluster_split={str(k): v for k, v in f.get("cluster_split", {}).items()},
        age_buckets=f.get("age_buckets", {}),
        backlog={
            **f.get("backlog", {}),
            "state_counts": state.counts(),
            "near_duplicate_item_count": f.get("near_duplicate_item_count", 0),
            "near_duplicate_groups": f.get("near_duplicate_groups", [])[:12],
        },
        llm_enabled=f.get("llm_enabled", False),
    )


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    res = run(Query(q=req.question, source=req.source, limit=max(req.k, 1), mmr=True))
    items = corpus.rows_at(res.positions)
    answer, used = llm.answer_question(req.question, items)
    cites = [
        AskCitation(
            id=it["id"], creator=it.get("creator", ""), url=it.get("url", ""),
            summary=it.get("summary") or (it.get("caption") or "")[:120],
            source=it["source"],
        )
        for it in items
    ]
    return AskResponse(answer=answer, citations=cites, used_llm=used)
