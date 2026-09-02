# Shipyard --- What a RAG System Over This Data Can Actually Tell You

## Status

Companion to `shipyard_retrieval_frontend.md`. That doc is the
mechanism (embeddings, clustering, search). This doc is the payoff ---
a catalog of specific, non-obvious insights that become possible once
saved + liked content (embeddings, clusters, timestamps, owners) exist
in one retrievable index. Organized by what kind of system produces
them, cheapest first.

Each entry notes what it needs and roughly when it's realistic to build
it: **D1** (fits the one-day build), **D2** (needs the app running for
a while first --- resolved-item history, repeat usage), or **later**
(needs more data, more infra, or is a bigger feature than a day allows).

## A. Aggregation Insights (no RAG needed --- just counting, cheap)

These come from grouping/counting over metadata you already have. They
don't need embeddings, but they're much more legible once clustering
gives you a `topic` to group by instead of raw hashtags.

1. **Topic distribution.** What do you actually save/like about, by
   volume? Not what you'd guess --- what the data says. **[D1]**
2. **Creator concentration.** "You've saved from 340 different
   creators, but 55% of your saves come from your top 12." Useful for
   the creator filter itself, and a genuinely surprising number to most
   people. **[D1]**
3. **Save-rate vs. like-rate by topic.** Liked posts outnumber saved
   ~3.4:1 overall, but that ratio isn't uniform --- some topics you like
   constantly and almost never save (low commitment), others you save
   almost every time you engage (high intent). This is the single best
   argument for keeping Saved and Liked as separate signals rather than
   merging them. **[D1]**
4. **Time-of-year patterns.** Does a topic spike seasonally --- more
   recipe saves in Nov/Dec, more fitness content in January? Just a
   month-bucketed count per cluster. **[D1]**
5. **Content age / backlog decay.** "Your oldest unresolved saved item
   is from [date], X months ago." A blunt, honest number that makes the
   core hypothesis ("saves rot") concrete using your own data on day
   one, before any resolving has happened. **[D1]**
6. **Caption coverage.** What % of items have a substantive caption vs.
   near-empty? This sets an honest ceiling on how good AI understanding
   *can* be with caption-only extraction --- worth knowing before
   promising extraction quality. **[D1]**

## B. Embedding-Only Insights (needs vectors, not generation)

7. **Near-duplicate save detection.** Cosine similarity surfaces cases
   where you saved multiple near-identical pieces of content (three
   different "here's why your knee hurts" explainers, four variations
   of the same stretch routine). Each individual save looks unremarkable;
   the cluster of near-duplicates is a strong, legible signal of
   unresolved need --- "you clearly want an answer to this, you just
   haven't gotten one yet." **[D1]**
8. **Cross-source overlap.** Same or near-identical content appearing
   in both Saved and Liked (you liked it once, then later actually
   saved a similar one) --- a concrete example of interest turning into
   intent, which is literally the product's core loop, visible in
   historical data before you've built anything. **[D1]**
9. **"More like this."** Given one item, nearest neighbors across the
   whole corpus, mixing sources. Cheap, and doubles as a sanity check
   that the embedding space is doing something sensible. **[D1]**

## C. Retrieval + Generation Insights (real RAG: retrieve top-k, LLM synthesizes)

10. **Natural-language Q&A over your own archive.** "What have I saved
    about improving grip strength?" → retrieves relevant items, answers
    with citations back to the specific posts. This is the flagship RAG
    feature and the most demoable one. **[D1 if time allows, else D2]**
11. **Cross-item synthesis on a theme.** Rather than just listing
    matches, have the model reconcile them: "you have three saved
    explainers on pain types that each emphasize something different ---
    here's the throughline." Turns a pile of separately-saved content
    into one coherent answer, which is a step past retrieval into
    actual "understanding over folders" (a stated product principle).
    **[D2]**
12. **Auto-generated digest.** Periodic ("this week you leaned heavily
    into pasta recipes and crochet gauge questions") summary grouped by
    theme, generated from recent saves/likes. Good retention hook, not
    a day-one build. **[later]**
13. **Contradiction/gap detection.** Model flags when retrieved items
    on the same topic disagree (two saved sources give conflicting
    advice) --- turns passive hoarding into something closer to research.
    Interesting but needs careful prompting to not hallucinate
    disagreement that isn't there. **[later]**

## D. Signal-Driven Insights (needs saved + liked + eventual resolve history together)

14. **Like → Save gap, by creator.** Creators you engage with (like)
    constantly but have never once saved from --- passive interest that
    never converts to intent. A legitimate "you might want to actually
    save something from this person" nudge, grounded in your own
    behavior, not a generic recommendation algorithm. **[D1, since it's
    just a join over two existing files]**
15. **Follow-through rate by creator.** Once resolve history exists: of
    items saved from creator X, what fraction actually got resolved?
    Distinguishes creators whose content you genuinely use from ones
    you hoard from out of habit. **[D2 --- needs resolved-item history to
    exist first]**
16. **Follow-through rate by topic.** Same idea, by cluster instead of
    creator --- "you resolve short bodyweight workouts at a much higher
    rate than long gym sessions," which is a more useful fact about
    your actual capacity than anything you'd self-report. **[D2]**
17. **Resurfacing priority beyond FIFO.** Rank unresolved items by
    similarity to recently *resolved* ones instead of just "oldest
    first" --- if you keep resolving lower-body workouts and ignoring
    yoga saves, resurface accordingly. A real, if small, personalization
    step once there's resolve history to learn from. **[D2]**
18. **Anniversary resurfacing.** "This time last year you saved a
    Diwali recipe" --- calendar-relevant resurfacing using timestamp +
    topic, no waiting on resolve history, works from day one on the
    existing export. **[D1]**

## E. Data-Quality / Corpus-Hygiene Insights

19. **Sponsored/ad content detection.** A meaningful slice of both
    files is ads ("*This is a sponsored post*", "DM to get link",
    giveaway posts). An LLM pass (or even a cheap keyword/pattern
    filter first) can flag these so they don't pollute topic clusters
    or get treated as genuine saved intent. Worth doing before
    clustering, not after. **[D1, do this early --- it improves
    everything downstream]**
20. **Actionable vs. informational split.** Not everything saved is
    something to *do* --- some of it is just "things to know" (news
    commentary, general facts) rather than "things to do" (a recipe, a
    routine, a technique). Since the whole product thesis is about
    closing the gap between saving and *doing*, a classifier that
    separates these is arguably more valuable than topic tagging: it
    tells you which fraction of the backlog the "resolve" concept even
    applies to. **[D1 as a rough LLM pass over cluster representatives,
    refine later]**

## What I'd Actually Prioritize for Day One

If you can only build a handful of these before the demo, in order:

1. **#5 (backlog decay)** and **#1 (topic distribution)** --- cheapest,
   most immediately legible, and directly support the core hypothesis
   pitch.
2. **#20 (actionable vs. informational split)** --- do this as an early
   pass; it's cheap and makes every other insight and the library itself
   more honest (no point resurfacing a news post as if it were a
   to-do).
3. **#7 (near-duplicate detection)** --- the single most "wow, it found
   that" moment for the least engineering, since it falls straight out
   of embeddings you're computing anyway.
4. **#14 (like → save gap by creator)** --- costs nothing beyond a join,
   and it's the clearest illustration that Saved and Liked being
   separate signals was the right call.
5. **#10 (Q&A over your archive)** if there's time left after the
   library/filters work in the companion doc --- it's the best demo
   moment but it's also the most replaceable by #1/#5/#7/#14 if the day
   gets tight, since those are cheaper and still land.

Everything under **D2** and **later** is a legitimate roadmap, not a
day-one gap --- they need behavioral history (resolves) this export
can't provide yet.
