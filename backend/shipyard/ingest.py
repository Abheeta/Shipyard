"""Parse Instagram data-export JSON into a normalized corpus DataFrame.

The export shape (per item):
    {
      "timestamp": <unix int>,
      "label_values": [
        {"label": "URL", "value": "...", "href": "..."},
        {"label": "Caption", "value": "..."},        # sometimes absent
        {"label": "Title", "value": "..."},
        {"title": "Hashtags", "dict": [ {"dict": [{"label":"Name","value":"..."}]} ]},
        {"title": "Owner", "dict": [ {"dict": [
            {"label":"URL","value":"..."},
            {"label":"Name","value":"..."},
            {"label":"Username","value":"..."}]} ]},
        {"title": "Brand partner", "dict": [...]},    # non-empty => sponsored
      ],
      "fbid": "..."
    }
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def _labelled(label_values: list[dict], label: str) -> str:
    for lv in label_values:
        if lv.get("label") == label:
            return (lv.get("value") or "").strip()
    return ""


def _section(label_values: list[dict], title: str) -> list:
    for lv in label_values:
        if lv.get("title") == title:
            return lv.get("dict") or []
    return []


def _hashtags(label_values: list[dict]) -> list[str]:
    out: list[str] = []
    for entry in _section(label_values, "Hashtags"):
        for kv in entry.get("dict", []):
            if kv.get("label") == "Name" and kv.get("value"):
                out.append(kv["value"].strip().lstrip("#"))
    return out


def _owner(label_values: list[dict]) -> tuple[str, str]:
    for entry in _section(label_values, "Owner"):
        kvs = {kv.get("label"): (kv.get("value") or "") for kv in entry.get("dict", [])}
        return kvs.get("Username", "").strip(), kvs.get("Name", "").strip()
    return "", ""


def _is_sponsored(label_values: list[dict], caption: str) -> bool:
    if _section(label_values, "Brand partner"):
        return True
    low = caption.lower()
    markers = ("#ad", "#sponsored", "sponsored post", "paid partnership", "dm to order",
              "dm to get", "link in bio to shop", "use my code", "giveaway")
    return any(m in low for m in markers)


def _item_id(fbid: str, url: str, source: str) -> str:
    if fbid:
        return f"{source}:{fbid}"
    h = hashlib.sha1(f"{source}|{url}".encode()).hexdigest()[:16]
    return f"{source}:{h}"


def parse_export(path: Path, source: str) -> list[dict]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    rows: list[dict] = []
    for it in raw:
        lv = it.get("label_values", [])
        url = _labelled(lv, "URL")
        if not url:
            continue
        caption = _labelled(lv, "Caption")
        title = _labelled(lv, "Title")
        creator, creator_name = _owner(lv)
        ts = int(it.get("timestamp") or 0)
        d = datetime.fromtimestamp(ts, tz=timezone.utc).date() if ts else None
        rows.append(
            {
                "id": _item_id(str(it.get("fbid") or ""), url, source),
                "source": source,
                "url": url,
                "caption": caption,
                "title": title,
                "creator": creator,
                "creator_name": creator_name or creator,
                "timestamp": ts,
                "saved_date": d,
                "year": d.year if d else None,
                "hashtags": _hashtags(lv),
                "is_ad": _is_sponsored(lv, caption),
            }
        )
    return rows


def build_corpus(saved_path: Path, liked_path: Path) -> pd.DataFrame:
    rows: list[dict] = []
    if Path(saved_path).exists():
        rows += parse_export(saved_path, "saved")
    if Path(liked_path).exists():
        rows += parse_export(liked_path, "liked")
    if not rows:
        raise FileNotFoundError(
            f"No export data found at {saved_path} or {liked_path}"
        )

    df = pd.DataFrame(rows)
    # de-dup within a source on url (keep earliest save/like)
    df = df.sort_values("timestamp").drop_duplicates(["source", "url"], keep="first")

    # enrichment columns — filled by build_index; defaulted here so the schema
    # is stable even if the index step is skipped.
    df["summary"] = ""
    df["tags"] = [[] for _ in range(len(df))]
    df["cluster_id"] = -1
    df["is_actionable"] = True

    return df.reset_index(drop=True)


def embed_text(row: pd.Series) -> str:
    """Text handed to the embedding model for one item."""
    parts = [row.get("caption") or "", row.get("title") or ""]
    tags = row.get("hashtags") or []
    if len(tags):
        parts.append(" ".join(tags))
    name = row.get("creator_name") or ""
    if name:
        parts.append(f"by {name}")
    return "  ".join(p for p in parts if p).strip()
