# Shipyard --- One-Day Build PRD

## Status

**Derived from `shipyard_prd_week3.md`.** That PRD assumed a one-week
build window and a fitness-specific wedge. This version assumes roughly
one day, and drops the fitness restriction --- the loop is tested on
whatever content is actually in your saved posts (crochet, recipes,
workouts, whatever). Almost everything in Week Three's "Nice to have"
and several "Must have" items are cut. The goal is not a smaller
version of the same product --- it is the smallest possible thing that
still tests the core hypothesis:

> **People do not primarily need another place to save content. They
> need help turning useful saved content into action.**

If you only have a day, you are not building a product. You are
building a demo of one loop, run on real data, that you can show
someone and say "this is what it would feel like."

## 1. What Changes Because It's One Day, Not One Week

| Week Three assumed | Day One drops it because |
|---|---|
| Instagram share-to-app capture | No time to build/test a share extension or deep link handler |
| Live AI extraction from video/caption per item | Fine for a handful of items, too slow to rely on for a demo of the full library |
| Multi-user accounts | Irrelevant for a solo validation demo |
| Push notifications for resurfacing | Replace with in-app "today" view, checked manually |
| Semantic natural-language search | Replace with basic tag/keyword filter |
| "Plan my week" | Cut entirely |
| Metrics/funnel tracking | Cut; you're the only user, you already know what happened |
| Fitness-only content wedge | Cut; the loop is content-agnostic --- import whatever's actually in the export |

The one thing that does **not** get cut: the loop itself.

> **Capture → Understand → Intent → Schedule → Resurface → Resolve**

Everything else exists only to make that loop feel real for a handful
of items.

## 2. The Big Scope Shortcut: Use `saved_posts.json`

You already have a real Instagram "Saved" export sitting in this repo
(`saved_posts.json`, ~2,800 items, full JSON with URL, caption, owner,
timestamp per post). That changes the smartest use of one day:

**Do not build live Instagram capture.** Instead, treat the export as
the seed data. "Capture" becomes: import N items from this JSON file
into the app (a script, not a UI flow). This gets you a populated,
realistic library in minutes instead of you manually pasting links all
day.

Two consequences:

- Pick ~30--50 items rather than all ~2,800 --- enough to feel like a
  real library, small enough to import and eyeball in minutes. A random
  or recency-based sample is fine now that there's no content-type
  filter to apply; diversity of topic (crochet, recipes, workouts,
  whatever shows up) is actually a better demo of "content-agnostic"
  than a filtered one would be.
- "Understand" now runs on **caption text only** (no video, no
  transcription) --- the export has no media, just URL + caption +
  owner. Say this explicitly to yourself: extraction quality is bounded
  by whatever the caption says. That's fine for validating the loop; it
  is not fine to promise as a real capture experience later.

If you'd rather actually test manual paste-a-link capture (closer to
the real product), that's a legitimate alternate choice for the day ---
but not both. Pick one before you start building.

## 3. Minimal Product Definition

> **Import saved posts → AI structures each one → you optionally add
> intent/date → items show in a library → items scheduled for today
> show on a "today" screen → you mark them resolved.**

That's the whole app. No accounts, no notifications, no folders, no
search beyond a text filter.

## 4. Data Model (trimmed)

Single object, no separate tables needed:

```
SavedItem {
  id
  source_url
  caption            // raw text from the export
  creator            // owner username, if present
  tags               // AI-generated, array of strings
  summary            // one-line AI-generated description
  user_note          // optional free text, why saved
  user_intent        // optional: try | learn | do_later | remember
  scheduled_at        // optional date
  status              // saved | scheduled | resolved
  resolved_at
}
```

Drop `structured_attributes` (sets/reps/exercises extraction) unless
the caption plainly contains them --- don't build a parser for it in a
day, let the AI extraction prompt just skip the field when absent.

## 5. Build Order (time-boxed for one day, ~8 working hours)

**Hour 0--0.5 --- Decide capture source.** Confirm: importing from
`saved_posts.json` (recommended) vs. manual paste. If using the export,
sample ~30--50 items rather than filtering by topic.

**Hour 0.5--1.5 --- Understand.** Script or endpoint that takes a
caption + URL, calls an LLM, returns `{summary, tags[]}`. Test on 3--5
real captions from the export first, before running it over the whole
seed set. Never invent details not in the caption.

**Hour 1.5--2 --- Import.** Run the extraction over your chosen seed
items, write results into local storage / a flat JSON file / a
lightweight DB (SQLite is enough). This is your seeded library.

**Hour 2--4 --- Library UI.** A single page: list of items (thumbnail
optional --- you likely don't have images, just show creator + summary
+ tags), item detail view, a text filter box. This is the largest
single chunk of work; protect the time for it.

**Hour 4--5 --- Intent + Schedule.** On item detail: optional note
field, optional intent picker, optional date picker. Writing these
updates `status` to `scheduled` when a date is set.

**Hour 5--5.5 --- Resurface.** A second view/tab: "Today" --- items
where `scheduled_at` is today (or overdue). No push notifications; you
open the tab.

**Hour 5.5--6 --- Resolve.** A button on an item: mark
`resolved`/`status = resolved`, sets `resolved_at`. Resolved items stay
visible in the library, maybe visually distinct (strikethrough,
checkmark).

**Hour 6--7 --- Walk the loop end to end** with real data. Fix what's
broken. This is not optional --- an untested demo is not a demo.

**Remaining time --- polish or cut further**, in this priority order if
you're behind: (1) make sure resolve/schedule work reliably over
looking nice, (2) library filter, (3) visual polish. Do not spend
remaining time on anything not in this list.

## 6. Explicitly Out of Scope for Day One

Everything already cut in Week Three's "Explicitly Out of Scope," plus:

- Live Instagram capture / share extension
- Video/audio transcription of any kind
- Multi-user auth
- Push/email notifications
- Semantic search
- Weekly planning
- Any metrics dashboard beyond eyeballing your own data
- Content-type-specific structured extraction (exercise sets/reps,
  recipe ingredients, etc.) beyond what's plainly in the caption --- tags
  and a summary are enough for day one, regardless of topic

## 7. What "Done" Looks Like

You can, live, in front of someone:

1. Show a library of real saved posts --- any topic, not just fitness ---
   each with an AI summary and tags, pulled from your actual Instagram
   saves.
2. Open one, add a note ("try this Thursday") and a date.
3. Switch to "Today," see an item you scheduled for today.
4. Mark it resolved, see it reflected in the library.

If that sequence works without you narrating around a broken step, the
day succeeded. Everything else is bonus.
