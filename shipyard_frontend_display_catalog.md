# Shipyard --- Frontend Display Catalog

## Status

Companion to `shipyard_retrieval_frontend.md` and `shipyard_rag_insights.md`.

- `shipyard_retrieval_frontend.md` = the mechanism (embeddings, filters,
  the four core views, the loop).
- `shipyard_rag_insights.md` = the catalog of *insights* the data can
  yield.
- **This doc** = the catalog of *display surfaces* --- concretely, every
  screen, panel, card region, chart, and widget that can be rendered
  from the two exports plus the derived index, and exactly which field
  feeds each one. It is the "what goes on the glass" reference so the
  build isn't improvising UI while also wiring data.

Tags carried over: **[D1]** fits the one-day build, **[D2]** needs the
app running a while (resolve history), **[later]** bigger than a day.

---

## 1. Ground Truth --- What the Two Files Actually Contain

Measured from the real exports in this repo, not the PRD estimates.
Some earlier assumptions were off; the frontend should be planned
against these numbers.

| Fact | Liked (`liked_posts (1).json`) | Saved (`saved_posts.json`) |
|---|---|---|
| Items | **9,392** | **858** (not ~2,800) |
| Like : Save volume ratio | **~10.9 : 1** (not 3.4:1) | --- |
| Date range (of the save/like action) | 2025-08-25 → 2026-08-25 | 2025-08-26 → 2026-08-25 |
| Caption present | 96% (306 empty) | 96% (28 empty) |
| Substantive caption (>80 chars) | 72% | **87%** |
| Avg caption length | 384 chars | 555 chars |
| Owner/creator attributed | 100% | 100% |
| Unique creators | **5,886** | 697 |
| Content type | 62% Reels, 38% posts | 68% Reels, 32% posts |
| `Title` field | present but **empty on effectively every item** | same |
| `Hashtags` (structured) | present, **junk-dominated** (`fyp`, `explore`, `viral`, `trending`) | present, **more useful** (`recipe`, `healthy`, `pasta`, `protein`, `phonics`) |
| Explicit `Brand partner` flag | 22 items | 3 items |
| Ad-pattern captions (keyword scan) | ~299 (~3%) | ~39 (~4.5%) |

Cross-file relationships (these power the discovery surfaces):

- **422 creators** appear in *both* Saved and Liked.
- **170 creators** were liked **≥5 times** and **never saved from** ---
  the like→save gap is large and real (top offenders: `lifeofpujaa` 43,
  `brut.india` 40, `knowyourmeme` 34, `hindustantimes` 25 --- i.e.
  news/meme/celebrity accounts you watch but never act on).
- **370 items share an exact URL** across Saved and Liked --- concrete
  "interest became intent" pairs, visible on day one.

### Corrections that change the UI

1. **Creator concentration is the opposite of what the insights doc
   guessed.** Top 10 creators are only ~5--6% of items; the average
   creator has ~1.6 likes. The surprising, displayable fact is
   *fragmentation* --- "9,392 likes spread across 5,886 creators; you
   have no favourites, you have a feed." The "top creators" rail still
   works but frame it as a long-tail histogram, not an 80/20.
2. **Raw hashtags are not a usable topic axis.** Don't render them as
   filter chips or on cards as-is. Topic = the clustering pass only.
   Hashtags can still show in the detail panel as raw metadata.
3. **`Title` is always empty** --- drop it from every layout.
4. **Everything is "in the past" relative to today (2026-09).** The
   oldest item is ~13 months old. The backlog-decay number is real and
   large on day one; the "Today" view will be empty until the user
   schedules something (design the empty state deliberately, see §6).
5. **Saved captions are meaningfully richer than Liked** (555 vs 384
   chars, 87% vs 72% substantive) --- AI summaries of Saved items will be
   higher quality; lean the demo on Saved.

---

## 2. Display Surface Map

Seven surfaces. The first four are the core loop (mostly in the
companion doc, itemised here for field-level completeness). The last
three are the "discovery engine" --- everything that makes the archive
feel like it understands itself.

```
  CORE LOOP                          DISCOVERY ENGINE
  1. Library (grid + filter bar)     5. Insights dashboard
  2. Item detail panel               6. Discovery feed (nudges / dupes / more-like-this)
  3. Today / resurface view          7. Ask-your-archive (RAG Q&A)
  4. Resolve state (cross-cutting)
```

---

## 3. Core Loop Surfaces --- Field-Level Detail

### 3.1 Library card (`ItemCard`)

What can be shown on each card, in priority order (top 4 fit a compact
card; the rest are detail-panel only):

| Region | Source | Notes |
|---|---|---|
| Creator handle | `owner` | 100% coverage; links out to `instagram.com/<owner>` |
| AI summary (1 line) | derived `summary` | the headline of the card; falls back to first ~90 chars of caption if extraction skipped |
| Topic chip | derived `cluster_name` | one per card, colour-coded by cluster |
| Source badge | `source` (`saved`/`liked`) | visually distinct; Liked cards are lighter-weight |
| AI tags (2--3) | derived `tags[]` | not raw hashtags |
| Content-type icon | parsed from `url` (`/reel/` vs `/p/`) | reel vs image post |
| Age / "saved N months ago" | `timestamp` | relative; this is the backlog-decay signal at the item level |
| Intent pill | `user_intent` | only if set: `try` / `learn` / `do later` / `remember` |
| Status ribbon | `status` | `scheduled` → date badge; `resolved` → check + strikethrough treatment |
| Actionable/informational tag | derived `item_kind` | "to-do" vs "to-know" (RAG #20) --- small muted label |
| Ad flag | derived `is_promotional` | tiny "sponsored" marker; or hidden behind a filter toggle |
| Near-duplicate indicator | derived `dup_group_id` | "3 similar saves" badge → opens the cluster (RAG #7) |

### 3.2 Item detail panel (`ItemDetailPanel`)

Everything the card omits, plus the mutation controls.

**Read region (all items):**
- Full caption (raw text, preserved line breaks)
- AI summary + full AI tag list
- Creator: handle, display name (`owner.Name` where present), external
  link (`owner.URL` --- linktree etc., present on many)
- Original post link (opens Instagram)
- Save/like timestamp, absolute + relative, labelled "you saved this
  on..." (not "posted on" --- the export has no post date)
- Content type, source
- Raw hashtags (collapsed "metadata" disclosure --- honesty, not a
  feature)
- "More like this" strip: 4--6 nearest neighbours across the whole
  corpus, mixed source (RAG #9)
- If part of a near-dup group: "You saved N near-identical things"
  expandable list (RAG #7)
- If this exact URL is in both Saved and Liked: "You liked this on
  [date], then saved it on [date]" --- the interest→intent line (RAG #8)

**Mutation region (Saved items only, per companion doc's open decision):**
- `user_note` free text ("why I saved this")
- `user_intent` picker: try / learn / do later / remember
- `scheduled_at` date picker → flips `status` to `scheduled`
- Resolve button → `status = resolved`, stamps `resolved_at`
- Un-resolve (undo)

**For Liked items:** read-only + a single **"Save this"** button that
promotes it into the Saved set (source flip + default `saved` status).

### 3.3 Today / resurface view (`TodayView`)

- Query: `status != resolved AND scheduled_at <= today`.
- Same `ItemCard`, no filter bar.
- Sections: **Overdue** (scheduled before today) / **Today** / (opt.)
  **This week**.
- Per card here: emphasise the `user_note` and `user_intent` (that's
  what the user needs to see to act), de-emphasise creator/tags.
- **Empty state is the default state on day one** --- see §6.
- Stretch, no resolve history needed: an "It's been a while" shelf
  under the empty Today view --- 3--5 oldest unresolved Saved items
  (`ORDER BY timestamp ASC LIMIT 5`). Turns the empty screen into the
  backlog-decay pitch (RAG #5).
- Stretch: **Anniversary shelf** --- items saved ~12 months ago this
  week (`timestamp` within ±3 days of one year back). Works from the
  export alone (RAG #18); the data supports it (items from 2025-09
  exist).

### 3.4 Resolve state (cross-cutting)

Wherever an item renders, `status = resolved` gets a consistent
treatment: check icon, reduced opacity, strikethrough on the summary,
`resolved_at` shown. Resolved items stay in the Library (filterable
in/out), never in Today.

---

## 4. Insights Dashboard (Surface 5)

A single scrollable page of read-only widgets. Everything here is
computed once at import (or on resolve) and served from memory ---
"presentation of data the backend already has," per the companion doc.
Each widget below maps to a numbered insight in `shipyard_rag_insights.md`.

### 4.1 Day-one widgets (no RAG, no resolve history --- all [D1])

| # | Widget | Visual | Data |
|---|---|---|---|
| Header | **Corpus summary tiles** | 4--5 stat tiles | "9,392 liked · 858 saved · 5,886 creators · 13-month backlog · 96% captioned" |
| RAG #5 | **Backlog decay** | Big number + one-line | "Your oldest unresolved save is from Aug 2025 --- 13 months ago." Below: histogram of Saved items by age bucket (0--1mo, 1--3, 3--6, 6--12, 12+). |
| RAG #1 | **Topic distribution** | Horizontal bar chart | Item count per cluster, Saved vs Liked as stacked/paired bars. The "what you actually save about" reveal. |
| RAG #3 | **Save-rate vs like-rate by topic** | Slope chart or paired bars | Per cluster: liked count vs saved count, sorted by ratio. Surfaces "high intent" topics (save almost every time) vs "low commitment" (like constantly, never save). The core argument for keeping the two signals separate. |
| RAG #2 | **Creator distribution** | Long-tail curve + "top 15" list | Frame the fragmentation (avg 1.6 likes/creator). Toggle: rank by Saved / Liked / Combined. Click a creator → filters Library. |
| RAG #4 | **Time-of-year pattern** | Small-multiples line/area, one sparkline per top cluster | Month-bucketed count per cluster. Callouts where a cluster spikes (e.g. the July 2026 liked surge --- 1,580 items). |
| RAG #6 | **Caption coverage** | Donut + one sentence | "72% of liked / 87% of saved items have a substantive caption --- that's the ceiling on AI understanding." An honesty widget. |
| RAG #14 | **Like→Save gap by creator** | Ranked list | 170 creators liked ≥5x, never saved from. "You've watched `brut.india` 40 times and never saved anything." Each row: creator, like count, "see posts" / "these are all informational" note. |
| RAG #20 | **Actionable vs informational split** | Single stacked bar + per-cluster breakdown | "X% of your saved backlog is stuff to *do*; the rest is stuff to *know*." Defines how much of the library "resolve" even applies to. |
| RAG #8 | **Interest → intent pairs** | Count + sample list | "370 posts you liked, then later saved." Small gallery of before/after date pairs. The product's core loop, visible in historical data. |
| RAG #7 | **Near-duplicate clusters** | Grid of dup-groups | Each group: representative summary + "you saved this N times" + the members. "You clearly want an answer to this and haven't gotten one." |
| RAG #19 | **Sponsored/ad slice** | Small tile | "~3% of saves look promotional" + toggle to review/exclude them. |

### 4.2 Needs the app running a while ([D2] --- design the slots now, leave them empty/"coming soon")

| # | Widget | Data it waits on |
|---|---|---|
| RAG #15 | **Follow-through rate by creator** | resolved-item history |
| RAG #16 | **Follow-through rate by topic** | "you resolve short workouts at 3x the rate of long ones" |
| RAG #11 | **Cross-item synthesis panel** | LLM reconciles 3+ saves on one theme into one answer |
| RAG #17 | **Resurfacing priority (beyond FIFO)** | rank unresolved by similarity to recently *resolved* |

### 4.3 [later]

RAG #12 auto-digest, RAG #13 contradiction/gap detection --- list as
roadmap, don't build slots.

---

## 5. Discovery Feed (Surface 6)

A single "for you, from your own archive" view --- a vertical feed of
generated cards, each backed by one of the embedding/aggregation
passes. This is the "discovery engine" made visible: no new data, just
the index surfaced proactively instead of only on search.

Card types in the feed:

1. **"Answer this already" card** --- a near-dup group (RAG #7).
   "You've saved 3 explainers on knee pain. Want the throughline?" →
   opens synthesis (D2) or just the 3 items (D1).
2. **"You keep watching, never saving" card** --- a like→save-gap
   creator (RAG #14). "43 likes from `lifeofpujaa`, 0 saves." Action:
   dismiss / "save one".
3. **"This became a thing" card** --- an interest→intent URL pair
   (RAG #8).
4. **"Buried" card** --- an old unresolved Saved item resurfaced
   (RAG #5 / FIFO). One per feed refresh.
5. **"This time last year" card** --- anniversary resurfacing
   (RAG #18).
6. **"More like the one you just opened" card** --- populated after any
   detail-panel view (RAG #9).
7. **Topic spike card** --- "You leaned hard into recipes in
   January" (RAG #4), generated from month buckets.

Each card: a headline, 1--3 item thumbnails/summaries, one primary
action (open / save / schedule / dismiss), and a "why am I seeing
this" line naming the signal. Dismissals are the only state it writes.

Feed composition on day one is deterministic (round-robin the card
types over available material), not ranked --- ranking is a [D2]
concern once dismiss data exists.

---

## 6. Ask-Your-Archive (Surface 7) --- RAG Q&A

RAG #10, the flagship demo, **[D1 if time allows, else D2]**.

- A single text box + answer area. Optionally reachable from the
  Library search box ("ask a question instead" affordance).
- Input: natural-language question ("what have I saved about grip
  strength?").
- Output display:
  - **Answer** --- 2--4 sentences, LLM synthesis over retrieved top-k.
  - **Citations** --- inline `[1] [2]` linking to the specific items,
    rendered as `ItemCard`s below the answer.
  - **"Retrieved from" strip** --- the k items the answer used, so the
    user can see the sources even for parts not cited.
  - **Source mix note** --- "answered from 4 saved + 2 liked items."
  - **Confidence / coverage caveat** when retrieval is thin ("only
    found 1 related item --- this may be incomplete").
- Suggested-question chips seeded from cluster names ("What have I
  saved about `<top cluster>`?") so the empty state is demoable.
- [D2] upgrade: **cross-item synthesis mode** (RAG #11) --- explicitly
  reconcile disagreeing sources rather than just answer.

---

## 7. New Components (beyond `shipyard_retrieval_frontend.md` §5)

The companion doc already defines `FilterBar`, `ResultsGrid`,
`ItemCard`, `ItemDetailPanel`, `TodayView`, `CreatorRail`,
`TopicChips`. This doc adds:

- `StatTileRow` --- the corpus-summary tiles (reused: dashboard header,
  Today empty state).
- `InsightCard` --- generic titled container: headline + chart slot +
  caption. Every dashboard widget is one of these.
- `BarChart` / `SlopeChart` / `Sparkline` / `LongTailCurve` / `Donut`
  --- minimal chart primitives (one small lib, or hand-rolled SVG; data
  volumes are tiny post-aggregation).
- `DupGroupCard` --- representative + member list + count.
- `GapCreatorRow` --- creator, like count, action.
- `DiscoveryFeed` + `FeedCard` (with a `variant` per §5 card type).
- `AnniversaryShelf` / `BuriedShelf` --- oldest/anniversary item
  strips (reuse `ItemCard`).
- `AskBox` + `AnswerBlock` (answer + citation cards + retrieved strip).
- `ResolvedTreatment` --- shared style wrapper, not a component per se.

---

## 8. Empty / Loading / Honesty States

The data guarantees several screens are empty or degraded on day one.
Design them, don't let them look broken.

| Screen | Day-one reality | Deliberate state |
|---|---|---|
| Today | Nothing scheduled yet | "Nothing scheduled. Here's what's been sitting longest:" + `BuriedShelf` + `AnniversaryShelf` |
| Resolved filter | Zero resolved items | "You haven't resolved anything yet --- that's the point." + link to Today |
| Follow-through widgets | No resolve history | Greyed slot: "Unlocks after you resolve a few items" |
| Ask-your-archive, thin retrieval | Some topics have 1--2 items | Show the caveat line, still answer |
| Item with empty caption (306 liked / 28 saved) | No text to summarise | Card shows "No caption --- can't summarise" instead of a fake summary; still browsable by creator/topic |
| AI summary skipped/failed | --- | Fall back to truncated raw caption, visibly (italic, "raw caption") |

Honesty widgets to keep visible, not hide: caption coverage (#6), ad
slice (#19), actionable/informational split (#20). They make the
library's claims believable.

---

## 9. What The Data Cannot Show (don't design these)

- **Thumbnails / any media.** `media: []` on every item. Cards are
  text-first: creator + summary + tags. A generated colour block or
  topic icon is the only "image."
- **Post date, view/like/comment counts, audio track.** Not in the
  export. Only the user's save/like timestamp exists.
- **Why the user saved something.** No note in the export --- that's
  `user_note`, created in-app.
- **Full-text of the video/reel.** Caption only. Extraction quality is
  capped at what the caption says (surface this via #6).
- **Real resolve/follow-through behaviour** until the app is used ---
  every [D2] widget.
- **Reliable topic from hashtags.** Junk-dominated; topic must come
  from clustering.

---

## 10. Build Priority (display work only)

On top of the companion doc's time-box. If the day runs long, cut from
the bottom.

1. **`ItemCard` + `ItemDetailPanel` full field set** (§3.1--3.2) ---
   this is the loop; protect it.
2. **Today view + its empty state** (§3.3, §8) --- the empty state is
   not optional, it carries the pitch.
3. **Dashboard: tiles + backlog decay (#5) + topic distribution (#1)**
   --- cheapest, most legible, directly support the hypothesis.
4. **Dashboard: like→save gap (#14) + near-dup groups (#7)** --- best
   "it found that" moments per unit of engineering; both fall out of
   data already computed.
5. **Dashboard: save-rate vs like-rate (#3) + actionable/informational
   (#20) + interest→intent pairs (#8)**.
6. **Discovery feed (§5)** --- high demo value, but it's a composition
   of things 3--5 already produce; build it only if they're done.
7. **Ask-your-archive (§6)** --- best single demo moment, most
   replaceable by 3--5 if time is tight.
8. **Time-of-year (#4), caption coverage (#6), ad slice (#19)** ---
   polish widgets, first to cut.

Do not cut: `ItemCard`/`ItemDetailPanel` fields, Today + its empty
state, backlog-decay, topic distribution. Those are the demo.
