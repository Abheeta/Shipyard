"""End-to-end sanity check against the in-process app (no server needed).

    python -m scripts.smoke
"""
from __future__ import annotations

import sys

from shipyard.corpus import corpus
from shipyard.search import Query, run
from shipyard.state import init_db, patch_state, today_ids
from shipyard import llm


def main() -> int:
    init_db()
    corpus.load()
    print(f"corpus: {len(corpus)} items, {len(corpus.cluster_names)} clusters")
    assert len(corpus) > 0

    # semantic search
    for q in ["crochet gauge", "chicken curry recipe", "diabetes blood sugar", "beyonce"]:
        r = run(Query(q=q, source="both", limit=3))
        top = corpus.rows_at(r.positions)
        print(f"\nq={q!r}  ({r.total} candidates)")
        for t in top:
            print(f"  [{t['source']}] @{t['creator']:<20} {(t['summary'] or t['caption'])[:70]}")

    # filters compose
    r = run(Query(source="saved", time_preset="this_year", actionable="actionable", limit=5))
    print(f"\nsaved + this_year + actionable: {r.total}")

    # cluster filter
    if corpus.cluster_names:
        cid = next(iter(corpus.cluster_names))
        r = run(Query(cluster_id=cid, limit=3))
        print(f"cluster {cid} ({corpus.cluster_names[cid]!r}): {r.total} items")

    # loop: schedule -> today -> resolve
    sample_id = corpus.df.iloc[0]["id"]
    patch_state(sample_id, user_note="try this", scheduled_at=__import__("datetime").date.today())
    assert sample_id in today_ids(), "scheduled item not in today"
    patch_state(sample_id, status="resolved")
    assert sample_id not in today_ids(), "resolved item still in today"
    print("\nloop: schedule -> today -> resolve  OK")

    # Q&A (fallback mode when LLM off)
    ans, used = llm.answer_question("what have I saved about crochet", corpus.rows_at(run(Query(q="crochet", limit=5)).positions))
    print(f"\nask (used_llm={used}): {ans[:120]}…")

    print("\nSMOKE OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
