# Shipyard --- Retrieval Architecture & Frontend Plan (Day One)

## Status

Follows `shipyard_prd_day1.md`. That doc set the loop; this one details
the retrieval layer (embeddings, clustering, filters) and the frontend
that exposes it, now that there are **two** real datasets to work with:

- `saved_posts.json` --- ~2,800 items, your saved-with-intent library.
- `liked_posts (1).json` --- ~9,392 items, everything you've liked.

## 1. Product Distinction: Saved vs. Liked

These are not the same signal and the app should not treat them
identically.

- **Saved** = you meant to come back to this. This is the library that
  gets the full loop --- note, intent, schedule, resurface, resolve.
- **Liked** = passive interest, lower commitment, ~3.4x the volume.
  Liked items are **not** schedulable/resolvable in Day One --- they're
  browsable and searchable context, and they're the main input to a few
  of the insights in the companion doc (who you engage with a lot but
  never actually save from, etc).

Both are part of one searchable corpus, distinguished by a `source`
field. This is what makes "top liked creator" vs. "top saved creator"
a meaningful, different filter rather than a redundant one.

## 2. Retrieval Architecture (recap + what changes at 12k items)

Combined corpus is ~12,200 items. Still small enough that none of this
needs real infrastructure:

- **Embeddings:** local model (e.g. `all-MiniLM-L6-v2` via
  `sentence-transformers`), one vector per item from `caption` (+
  hashtags where present). No API calls, no rate limits, embeds the
  full 12k in a few minutes on CPU.
- **Storage:** one flat matrix (numpy `.npy`, ~12,200 × 384 floats ≈
  18MB) plus a parallel metadata array/JSON (id, source, owner,
  timestamp, caption, hashtags, cluster_id). No database required for
  the corpus itself.
- **Search:** brute-force cosine similarity, in-memory, sub-100ms at
  this size. Query text gets embedded at request time, dotted against
  the matrix, top-k returned.
- **Clustering:** k-means over the same matrix (~25--35 clusters
  across both sources combined, since topic diversity is now larger
  with liked posts included), LLM names each cluster from a handful of
  representative captions (~30 LLM calls total, not 12,200).
- **User-added state** (note, intent, scheduled_at, status,
  resolved_at) lives in a small separate JSON/SQLite file keyed by item
  id --- this is the only thing that's actually mutable at runtime. The
  corpus + embeddings + clusters are a static index built once at
  import time.

## 3. Filters

All filters operate as pre-filters on the metadata array before (or in
combination with) the semantic search step. None require new backend
infrastructure --- they're array filters over data already in memory.

### Time

- **Presets:** This year (2026) · Last year (2025) · Older · All time.
- **Custom range:** simple two-date picker for anything more specific.
- Powered directly by each item's `timestamp` (the save/like
  timestamp, not post date --- worth a small label in the UI so it's not
  misread as "posted in 2025").

### Creator

- Ranked list, top N (say top 15) creators by count, **computed
  separately for Saved and Liked** --- "top saved creator" and "top
  liked creator" are genuinely different lists and both are useful (one
  shows intent, one shows attention).
- UI: a small ranked chip/list panel (creator name + count), click to
  filter the main view to that creator. A toggle switches the ranking
  between Saved-count / Liked-count / Combined.
- Computed once at import time (group-by on `owner.username` per
  source), cached --- not recomputed per request.

### Source

- Simple three-way toggle: Saved / Liked / Both. Default: Both, since
  the corpus is meant to feel unified; this is what narrows it back
  down when it matters.

### Topic (cluster)

- Chip row of the ~25--35 auto-named clusters, click to filter. This
  is the "zero organization work" payoff --- it exists because of the
  clustering pass, not hand-tagging.

### Search

- Free-text box, semantic (embeds the query, cosine against the
  filtered subset --- filters apply first, search reranks within them).
  Falls back to substring match on caption/owner if the query embeds to
  nothing useful (e.g. very short queries) --- cheap safety net, not a
  real hybrid ranker.

Filters compose with each other and with search: e.g. Source=Saved +
Time=Last year + Topic=Crochet + query "gauge" is just successive
array narrowing, then a cosine rerank.

## 4. Frontend Layout

Single page app, four views:

```
┌─────────────────────────────────────────────────────────┐
│  [ Search box                              ]  [Today] [Insights?]│
│  Time: [This year][Last year][Older][All]                │
│  Source: [Saved][Liked][Both]     Topic: (chip)(chip)...  │
│  Top creators: (name·count)(name·count)... [saved|liked ▾]│
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ owner     │ │ owner     │ │ owner     │ │ owner     │     │
│  │ summary…  │ │ summary…  │ │ summary…  │ │ summary…  │     │
│  │ #tag #tag │ │ #tag #tag │ │ #tag #tag │ │ #tag #tag │     │
│  │ [Saved]   │ │ [Liked]   │ │ [Saved]   │ │ [Saved]   │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│  (grid continues, virtualized/paginated)                  │
└─────────────────────────────────────────────────────────┘
```

- **Library (default view):** the filter bar + grid above. This is
  most of the day's UI budget.
- **Item detail:** click a card → side panel or modal. Full caption,
  summary, tags, link to the original post. If `source = saved`: note
  field, intent picker, date picker, resolve button. If
  `source = liked`: read-only, plus a "Save this" button that promotes
  it into the saved set (nice small bridge between the two, cheap to
  build since it's just a source flip + default state).
- **Today:** items where `scheduled_at` is today or earlier and not
  resolved. Same card component, different query, no filter bar needed.
- **Insights (stretch, only if time remains):** a static-ish page
  rendering the top few things from the companion insights doc --- top
  creators chart, topic distribution, saved-vs-liked gap. This is the
  first thing to cut if the day runs long; it's presentation of data
  the backend already computed for filters, not new work, so it's cheap
  *if* there's time, and skippable if there isn't.

## 5. Components (for whatever framework you pick --- React assumed)

- `FilterBar` --- owns filter state (time preset/range, source, topic,
  creator, query), fires a single combined query on change.
- `ResultsGrid` --- renders `ItemCard[]` from the current query result,
  paginated or virtualized (12k items means don't render them all at
  once even filtered).
- `ItemCard` --- owner, truncated summary, tags, source badge.
- `ItemDetailPanel` --- full item + mutation controls (note/intent/date/
  resolve), conditional on source.
- `TodayView` --- reuses `ResultsGrid`/`ItemCard`, different data
  source.
- `CreatorRail` / `TopicChips` --- small presentational components fed
  by the precomputed facet lists.

## 6. Backend Endpoints (minimal)

- `GET /search?q=&source=&time=&topic=&creator=` → ranked item list.
  All filtering + reranking happens in-process against the in-memory
  index.
- `GET /items/:id` → full item.
- `PATCH /items/:id` → update note/intent/scheduled_at/status (writes
  to the small mutable state store, not the corpus).
- `GET /facets` → precomputed top creators (saved & liked, separately),
  cluster list with names/counts. Computed once at startup, served from
  memory.
- `GET /today` → items with `scheduled_at <= today AND status != resolved`.

No auth, no pagination cursors needed at this scale --- offset/limit is
fine.

## 7. Updated Time-Box

This adds real work on top of `shipyard_prd_day1.md`'s estimate. Budget
honestly, ~9--10 hours now, and know what to cut first if it runs long:

| Block | Time | Notes |
|---|---|---|
| Ingest both JSON files, normalize to one schema + `source` field | 0.5h | |
| Embed full ~12k corpus (local model) | 0.5h | mostly wait time |
| Cluster + LLM-name clusters | 0.75h | ~30 LLM calls |
| Facet precompute (top creators per source) | 0.25h | simple groupby |
| Backend endpoints (`/search`, `/items`, `/facets`, `/today`) | 1.5h | |
| Frontend: filter bar + results grid | 2h | largest single chunk |
| Frontend: item detail panel + mutations | 1h | |
| Frontend: Today view | 0.5h | reuses grid |
| End-to-end pass with real data, fix breakage | 1h | not optional |
| Insights view (stretch) | remaining time | cut first if behind |

**If behind schedule, cut in this order:** Insights view → Topic chips
(clusters) → Creator ranking toggle (saved/liked/combined, just default
to combined) → custom date range (keep only the presets). Do not cut:
search, source filter, item detail mutations, Today view --- those are
the loop.

## 8. Open Decision

Liked items currently only get a "Save this" promotion action, nothing
else. If you'd rather liked items be fully first-class (schedulable,
resolvable) that's a one-line scope change (drop the `source`
conditional in `ItemDetailPanel`), but it dilutes the "saved = you
meant to do this" signal that a few of the insights in the companion
doc depend on. Recommend keeping the distinction unless there's a
specific reason not to.
