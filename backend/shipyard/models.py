"""API request/response schemas and shared enums."""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel


class Source(str, Enum):
    saved = "saved"
    liked = "liked"


class Intent(str, Enum):
    try_it = "try"
    learn = "learn"
    do_later = "do_later"
    remember = "remember"


class Status(str, Enum):
    saved = "saved"
    scheduled = "scheduled"
    resolved = "resolved"


# Canonical column order for corpus.parquet. The ingest + index scripts and the
# in-memory loader all agree on this list.
CORPUS_COLUMNS = [
    "id",
    "source",
    "url",
    "caption",
    "title",
    "creator",
    "creator_name",
    "timestamp",
    "saved_date",
    "year",
    "hashtags",
    "summary",
    "tags",
    "cluster_id",
    "is_ad",
    "is_actionable",
]


class ItemState(BaseModel):
    user_note: Optional[str] = None
    user_intent: Optional[Intent] = None
    scheduled_at: Optional[date] = None
    status: Status = Status.saved
    resolved_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Item(BaseModel):
    id: str
    source: Source
    url: str
    caption: str
    title: str = ""
    creator: str = ""
    creator_name: str = ""
    timestamp: int
    saved_date: Optional[date] = None
    year: Optional[int] = None
    hashtags: list[str] = []
    summary: str = ""
    tags: list[str] = []
    cluster_id: int = -1
    cluster_name: str = ""
    is_ad: bool = False
    is_actionable: bool = True
    # merged mutable state
    state: ItemState = ItemState()
    score: Optional[float] = None


class ItemPatch(BaseModel):
    user_note: Optional[str] = None
    user_intent: Optional[Intent] = None
    scheduled_at: Optional[date] = None
    status: Optional[Status] = None
    # convenience: "promote a liked item into saved"
    promote_to_saved: Optional[bool] = None


class SearchResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[Item]


class Cluster(BaseModel):
    cluster_id: int
    name: str
    size: int


class CreatorFacet(BaseModel):
    creator: str
    creator_name: str
    count: int


class Facets(BaseModel):
    total_items: int
    saved_count: int
    liked_count: int
    unique_creators: int = 0
    unique_creators_saved: int = 0
    clusters: list[Cluster]
    top_creators_saved: list[CreatorFacet]
    top_creators_liked: list[CreatorFacet]
    top_creators_combined: list[CreatorFacet]
    like_save_gap: list[dict[str, Any]] = []
    year_counts: dict[str, int]
    cluster_split: dict[str, dict[str, int]] = {}
    age_buckets: dict[str, int] = {}
    backlog: dict[str, Any]
    llm_enabled: bool


class AskRequest(BaseModel):
    question: str
    source: Literal["saved", "liked", "both"] = "both"
    k: int = 10


class AskCitation(BaseModel):
    id: str
    creator: str
    url: str
    summary: str
    source: Source


class AskResponse(BaseModel):
    answer: str
    citations: list[AskCitation]
    used_llm: bool
