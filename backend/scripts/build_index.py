"""Build the static index from the raw exports.

    python -m scripts.build_index

Produces (in INDEX_DIR):
    corpus.parquet    one row per item, incl. summary/tags/cluster_id/flags
    embeddings.npy    (N, dim) float32, L2-normalized, row-aligned with corpus
    clusters.json     {cluster_id: {name, size}}
    facets.json       precomputed creator/topic/year/backlog facets + dup groups

Re-runnable any time; never touches state.sqlite.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone

import numpy as np

from shipyard import clustering
from shipyard.config import settings
from shipyard.embeddings import fit_embed
from shipyard.ingest import build_corpus, embed_text
from shipyard.llm import enrich_items, name_cluster
from shipyard.models import CORPUS_COLUMNS


def _facets(df) -> dict:
    def top_creators(sub, n=15):
        g = (
            sub.groupby("creator")
            .agg(count=("id", "size"), creator_name=("creator_name", "first"))
            .sort_values("count", ascending=False)
            .head(n)
            .reset_index()
        )
        return [
            {"creator": r.creator, "creator_name": r.creator_name, "count": int(r.count)}
            for r in g.itertuples()
        ]

    saved = df[df.source == "saved"]
    liked = df[df.source == "liked"]

    oldest = df["timestamp"].replace(0, np.nan).min()
    oldest_dt = datetime.fromtimestamp(oldest, tz=timezone.utc) if oldest == oldest else None
    age_days = (datetime.now(timezone.utc) - oldest_dt).days if oldest_dt else None

    clusters = (
        df[df.cluster_id >= 0]
        .groupby("cluster_id")
        .size()
        .sort_values(ascending=False)
    )
    # per-cluster saved vs liked split — powers topic distribution + save/like ratio
    cluster_split = {}
    for cid, grp in df[df.cluster_id >= 0].groupby("cluster_id"):
        s = int((grp.source == "saved").sum())
        cluster_split[int(cid)] = {"saved": s, "liked": int(len(grp) - s)}

    # like -> save gap: creators liked a lot, never saved from
    liked_by = liked.groupby("creator").size()
    saved_creators = set(saved["creator"])
    gap = [
        {"creator": c, "likes": int(n)}
        for c, n in liked_by.sort_values(ascending=False).items()
        if n >= 5 and c and c not in saved_creators
    ][:12]

    # age histogram of saved items (backlog decay)
    now = datetime.now(timezone.utc).timestamp()
    age_months = ((now - saved["timestamp"].replace(0, np.nan)) / 2_592_000).dropna()
    buckets = {"0–1 mo": 0, "1–3 mo": 0, "3–6 mo": 0, "6–12 mo": 0, "12 mo+": 0}
    for m in age_months:
        key = ("0–1 mo" if m < 1 else "1–3 mo" if m < 3 else "3–6 mo" if m < 6
               else "6–12 mo" if m < 12 else "12 mo+")
        buckets[key] += 1

    substantive = int((df["caption"].str.len() > 80).sum())

    return {
        "total_items": len(df),
        "saved_count": len(saved),
        "liked_count": len(liked),
        "unique_creators": int(df["creator"].nunique()),
        "unique_creators_saved": int(saved["creator"].nunique()),
        "top_creators_saved": top_creators(saved),
        "top_creators_liked": top_creators(liked),
        "top_creators_combined": top_creators(df),
        "like_save_gap": gap,
        "year_counts": {
            str(int(k)): int(v)
            for k, v in df["year"].dropna().astype(int).value_counts().sort_index().items()
        },
        "cluster_sizes": {int(k): int(v) for k, v in clusters.items()},
        "cluster_split": cluster_split,
        "noise_count": int((df.cluster_id == -1).sum()),
        "age_buckets": buckets,
        "backlog": {
            "oldest_item_date": oldest_dt.date().isoformat() if oldest_dt else None,
            "oldest_item_age_days": age_days,
            "saved_total": len(saved),
            "substantive_caption_share": round(substantive / len(df), 3),
            "ad_share": round(float(df["is_ad"].mean()), 3),
            "actionable_share": round(float(df["is_actionable"].mean()), 3),
        },
        "llm_enabled": settings.llm_enabled,
    }


def main() -> None:
    t0 = time.time()
    settings.index_path.mkdir(parents=True, exist_ok=True)
    print(f"LLM provider: {settings.llm_provider} (enabled={settings.llm_enabled})")

    print("1/6  parsing exports…")
    df = build_corpus(settings.saved_file, settings.liked_file)
    print(f"     {len(df)} items ({(df.source=='saved').sum()} saved / {(df.source=='liked').sum()} liked)")

    print(f"2/6  embedding ({settings.embed_backend})…")
    texts = [embed_text(r) for _, r in df.iterrows()]
    emb = fit_embed(texts)
    print(f"     {emb.shape}")

    print(f"3/6  clustering ({settings.cluster_method})…")
    labels = clustering.cluster(emb)
    # A cluster holding a big share of the corpus is the algorithm's dumping
    # ground for vague captions, not a topic — send it back to "ungrouped".
    max_share = int(len(df) * settings.cluster_max_share)
    for cid in {int(x) for x in labels if x != -1}:
        if (labels == cid).sum() > max_share:
            print(f"     dropping oversized cluster {cid} ({(labels == cid).sum()} items) -> ungrouped")
            labels[labels == cid] = -1
    labels = clustering._compact(labels)
    df["cluster_id"] = labels
    n_clusters = len({int(x) for x in labels if x != -1})
    print(f"     {n_clusters} clusters, {(labels == -1).sum()} ungrouped")

    print("4/6  naming clusters…")
    reps = clustering.representative_indices(emb, labels, per_cluster=10)
    cluster_meta: dict[str, dict] = {}
    for cid, idxs in reps.items():
        caps = [df.iloc[i]["caption"] or df.iloc[i]["title"] for i in idxs]
        caps = [c for c in caps if c][:8]
        name = name_cluster(cid, caps)
        cluster_meta[str(cid)] = {"name": name, "size": int((labels == cid).sum())}
        print(f"     [{cid:>2}] {name}  ({cluster_meta[str(cid)]['size']})")

    print("5/6  enriching items (summary / tags / actionable)…")
    order = df[df.source == "saved"].index.tolist() + df[df.source == "liked"].index.tolist()
    cap = settings.llm_max_enrich_items or len(order)
    llm_targets = order[:cap] if settings.llm_enabled else []
    heuristic_targets = [i for i in df.index if i not in set(llm_targets)]

    for label, targets in (("llm", llm_targets), ("heuristic", heuristic_targets)):
        if not targets:
            continue
        payload = [
            {
                "caption": df.at[i, "caption"],
                "title": df.at[i, "title"],
                "hashtags": list(df.at[i, "hashtags"]),
                "creator": df.at[i, "creator"],
                "creator_name": df.at[i, "creator_name"],
            }
            for i in targets
        ]
        # force heuristic path by temporarily hiding the key
        if label == "heuristic" and settings.llm_enabled:
            saved_key = settings.anthropic_api_key
            settings.anthropic_api_key = ""
            res = enrich_items(payload)
            settings.anthropic_api_key = saved_key
        else:
            res = enrich_items(payload)
        for i, r in zip(targets, res):
            df.at[i, "summary"] = r["summary"]
            df.at[i, "tags"] = r["tags"]
            df.at[i, "is_actionable"] = r["is_actionable"]
        print(f"     {label}: {len(targets)} items")

    print("6/6  facets + near-duplicates…")
    facets = _facets(df)
    dup_groups = clustering.near_duplicate_groups(emb, threshold=0.95)
    facets["near_duplicate_groups"] = [
        [df.iloc[i]["id"] for i in g] for g in sorted(dup_groups, key=len, reverse=True)[:50]
    ]
    facets["near_duplicate_item_count"] = sum(len(g) for g in dup_groups)
    print(f"     {len(dup_groups)} duplicate groups covering {facets['near_duplicate_item_count']} items")

    df = df[CORPUS_COLUMNS]
    df.to_parquet(settings.corpus_file, index=False)
    np.save(settings.embeddings_file, emb)
    settings.clusters_file.write_text(json.dumps(cluster_meta, indent=2, ensure_ascii=False), encoding="utf-8")
    settings.facets_file.write_text(json.dumps(facets, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\ndone in {time.time()-t0:.1f}s -> {settings.index_path}")


if __name__ == "__main__":
    main()
