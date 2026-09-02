# Shipyard --- Product Requirements Document

## Status

**Working PRD --- Week Three MVP.** This captures the current product
hypothesis after the Week Two research and today's discussion. It is
deliberately narrow because the build window is one week.

## 1. Executive Summary

Shipyard is exploring the gap between **discovering useful content
online and actually doing something with it**.

People discover workouts, recipes, mobility routines, nutrition ideas,
tutorials, and other useful content on social platforms. They save these
items because they intend to use them later. Saving is easy; the failure
happens afterward. The item gets buried, the user forgets why they saved
it, they cannot find it, they have to rewatch it, or they never decide
when to act.

The current hypothesis is:

> **People do not primarily need another place to save content. They
> need help turning useful saved content into action.**

The initial wedge is **fitness content saved from Instagram**. A user
shares an Instagram link to Shipyard. Shipyard understands and
structures the content, automatically categorizes it, captures an
optional note about why the user saved it, makes it searchable, lets the
user schedule it, resurfaces it at the right time, and lets the user
mark it resolved.

The core loop is:

> **Discover → Save → Understand → Remember → Act → Resolve → Discover
> again**

The key metric is not how many things users save. It is:

> **How many saved intentions does Shipyard help users actually
> resolve?**

Instagram is the initial input channel, not the fundamental product
boundary. The MVP does **not** include Instagram Graph API discovery.

## 2. Shipyard Context

Shipyard is in Week Two. The immediate goal is validation: speak with at
least forty users by the end of the week, put up a simple
landing/waitlist page, and decide whether the problem is painful enough
to justify a Week Three build.

This is an experiment, not a commitment to building a complete fitness
platform.

The central research question is:

> **What painful behavior is happening often enough that people will
> change their behavior or pay to solve it?**

The product should not be justified merely by "Instagram saved posts are
badly organized." The deeper hypothesis is the gap between **saving**
and **action**.

## 3. Research Background

Prior Reddit research surfaced repeated examples of people saving large
quantities of workout and recipe content and later struggling to
retrieve or use those saves.

Original discussion:

https://www.reddit.com/r/PKMS/comments/1ke1c41/how_do_you_all_save_videosposts_of_workouts/

Other relevant discussions:

https://www.reddit.com/r/PKMS/comments/1mj6pgv/i_was_drowning_in_saved_workout_videos_across/

https://www.reddit.com/r/microsaas/comments/1pgd1v6/building_an_app_that_organizes_workouts_from/

https://www.reddit.com/r/apps/comments/1ph16t8/i_built_an_app_that_turns_ig_tiktok_workout_reels/

https://www.reddit.com/r/iosapps/comments/1pnz6gc/turn_your_saved_workout_video_reels_into_trackable_workout_routines/

https://www.reddit.com/r/SideProject/comments/1t6m0nf/i_built_an_app_to_stop_losing_instagram_workouts_in_my_saved_folder/

https://www.reddit.com/r/sideprojects/comments/1vdqg4x/i_built_an_app_that_turns_tiktok_recipes_into/

https://www.reddit.com/r/cookingforbeginners/comments/1vqgvcb/i_have_hundreds_of_saved_recipe_videos_and_ive/

https://www.reddit.com/r/mealprep/comments/1l81aeo/how_do_you_organise_and_save_your_recipes/

https://www.reddit.com/r/Notion/comments/190aoyl/i_built_a_better_way_to_organize_tiktoks_to/

The recurring pattern is not that saving itself is difficult. The more
interesting failure points are finding the item, remembering why it was
saved, extracting useful information, deciding when to use it, and
following through.

Fitness and cooking are particularly interesting because the saved
content often corresponds to a repeated real-world action: doing a
workout or cooking a recipe.

## 4. Problem Statement

A user discovers useful content on Instagram and saves it because they
intend to use it later.

Later, the saved item can be difficult to act on:

-   It cannot be found.
-   It is found but the user no longer remembers why they saved it.
-   The user has to rewatch the whole video.
-   The user manually extracts exercises, sets, reps, ingredients, or
    instructions.
-   The user never decides when to use it.
-   It becomes part of a large backlog and is forgotten.
-   The user searches for the same information again.
-   The user stores the same idea elsewhere.

User-facing problem statement:

> **"I save useful things because I want to do them later, but my saved
> folder doesn't help me actually do them."**

## 5. Target User

The primary user is a digitally active, self-improvement-oriented person
who regularly discovers and saves fitness content on Instagram.

Examples include gym-goers, calisthenics users, runners, yoga/Pilates
users, people following fitness creators, and people who regularly save
workout demonstrations or routines.

The important behavior is repeated saving of useful fitness content with
an intention to use it later.

Home cooks who save recipes from social media are a strong secondary
segment, but cooking should not expand the Week Three scope unless
research strongly supports it.

## 6. Product Thesis

### Core thesis

> **Turn the things I save online into things I can actually use.**

### Fitness version

> **Save a workout Reel. Actually use it.**

A user discovers a workout, shares it, and Shipyard understands it,
organizes it, remembers why the user saved it, helps them retrieve it,
resurfaces it, and lets them resolve it.

### Deeper thesis

A save is often an implicit intention:

-   "I want to try this."
-   "I want to learn this."
-   "I want to add this to my routine."
-   "I want to remember this."
-   "I want to do this Thursday."

Shipyard should capture enough of that intent to help the user act.

## 7. Product Principles

**Zero organization work.** Users should not drag and drop items into
folders.

**Content understanding over folders.** A saved item should have
multiple dimensions rather than one rigid category.

**User intent is first-class data.** AI can understand what the content
contains; only the user can reliably explain why they saved it.

**Resurface instead of bury.** The app should bring useful saved items
back to attention at appropriate times.

**Measure action, not saves.** Saving is an input. Resolution is an
outcome.

**Keep scope narrow.** Every Week Three feature must support the action
hypothesis.

## 8. Core User Journey

### Discover

The user discovers useful fitness content on Instagram.

### Share

The user shares the Instagram URL to Shipyard. This should require
almost no manual work.

### Understand

Shipyard creates a structured representation.

Example:

> Twenty-five-minute lower-body workout. Strength training · Lower body
> · Glutes · Dumbbells · Intermediate.

If exercises and sets/reps are explicitly present, Shipyard extracts
them. It must not invent missing information.

### Capture intent

Shipyard asks:

> **Why are you saving this?**

Possible quick choices:

> Try it · Add to workout · Learn it · Do later · Just remember · Add a
> note

The user can write:

> "Try this Thursday after work."

### Organize automatically

Shipyard creates searchable metadata without requiring user-maintained
folders.

Possible fitness tags include strength training, mobility, stretching,
calisthenics, conditioning, agility/sports preparation, yoga/Pilates,
recovery, and nutrition/education.

These are tags, not mutually exclusive folders.

### Retrieve

The user can browse or search their saved library.

Useful queries include:

> "Show me lower-body workouts."

> "What did I save for mobility?"

> "Show me beginner workouts I can do at home."

> "What did I save because I wanted to improve my pull-ups?"

Retrieval should use both content metadata and user intent.

### Schedule

The user can assign an item to a date.

Example:

> "Do this Thursday."

### Resurface

At the appropriate time:

> **You wanted to try this today.**

The reminder should point directly to the saved item.

### Act

The user opens the structured content and performs the workout.

### Resolve

The user marks it as done/resolved. The item stays in history.

## 9. The Intent Layer

Each saved item can contain both structured intent and free-form notes.

Possible intents:

-   try
-   learn
-   add to routine
-   cook
-   buy
-   remember
-   do later

Examples:

> "Try this Thursday after work."

> "Use this before my next leg workout."

> "Cook this sometime this month."

The note is optional. Making it mandatory would recreate the friction
Shipyard is trying to remove.

## 10. The Resolved Layer

Every saved item should have an intention lifecycle:

> **Saved → Scheduled → Resolved**

The resolved state is important because it creates an outcome metric.

A future dashboard could show:

> Saved: twenty-three\
> Scheduled: six\
> Resolved: eight

The strongest qualitative signal would be:

> **"I actually did the workout because Shipyard reminded me."**

For different content types, the UI can use action-specific language
such as Done or Cooked, while the underlying state remains `resolved`.

## 11. Information Architecture

Core object: `SavedItem`

Suggested fields:

-   id
-   source_url
-   source_platform
-   source_title
-   creator
-   thumbnail/media reference
-   raw_content
-   content_type
-   extracted_content
-   tags
-   structured_attributes
-   user_note
-   user_intent
-   scheduled_at
-   status
-   created_at
-   resolved_at

### Structured workout fields

-   title
-   duration
-   difficulty
-   training type
-   goal
-   body parts
-   muscle groups
-   equipment
-   exercises
-   sets
-   reps
-   rest
-   context

The system must never fabricate missing workout information.

## 12. Search and Retrieval

Search should cover:

-   extracted content
-   tags
-   workout fields
-   creator
-   user note
-   user intent
-   status
-   scheduled date

The desired experience is natural retrieval rather than folder
navigation.

Examples:

> "What leg workouts have I saved?"

> "Show me a quick workout."

> "What did I save for shoulder mobility?"

> "Which workouts have I not done yet?"

Basic search/filter is enough for the MVP. Semantic search is useful
only if it can be added without destabilizing the core flow.

## 13. Discovery Without External Discovery APIs

Shipyard does not need to discover new content for the discovery loop.

The user's own saved library becomes the discovery pool.

The app can rediscover things the user previously found valuable:

> "You saved this three weeks ago. Still want to try it?"

> "You have four saved lower-body workouts. Want to pick one for this
> week?"

> "You wanted to try this today."

This makes the loop:

> **Discover → Save → Understand → Remember → Act → Resolve → Discover
> again**

The key insight is:

> **Shipyard can rediscover the user's own discoveries.**

## 14. Weekly Planning

A useful extension is:

> **Build my week**

Shipyard proposes a simple schedule using workouts the user has already
saved.

Example:

> Monday --- Lower body\
> Tuesday --- Mobility\
> Wednesday --- Upper body\
> Thursday --- Rest\
> Friday --- Calisthenics

The plan should preferentially use saved content rather than generating
an entirely new workout.

For the one-week MVP, manual assignment to days is enough. "Plan my
week" is optional if time remains.

Do not build a sophisticated AI personal trainer, recovery engine,
progressive-overload system, or medical advisor.

## 15. Fitness and Cooking

Fitness should be the initial wedge.

Cooking is a strong adjacent use case because the same architecture
applies:

> Instagram Reel → structured recipe → tags → intent → schedule → cook →
> resolve

Possible recipe fields include title, ingredients, quantities,
instructions, meal type, cuisine, cooking time, difficulty, protein,
dietary attributes, user note, planned date, and resolution state.

Cooking should remain outside the one-week build unless research
strongly supports it.

## 16. MVP Scope

### Must have

**Capture:** Instagram URL/share input.

**Understand:** reliable content extraction and AI-generated structured
representation.

**Organize:** automatic tags and metadata.

**Intent:** optional quick intent and free-form note.

**Library:** saved item list, item detail view, and search/filter.

**Schedule:** assign an item to a date.

**Resurface:** simple reminder or in-app resurfacing.

**Resolve:** mark an item done/resolved and retain it in history.

**Measure:** track import, intent, scheduling, resurfacing, opening, and
resolution.

### Nice to have

-   simple "Plan my week"
-   natural-language search
-   action dashboard
-   recurring resurfacing of unresolved items
-   richer workout extraction
-   history view

## 17. Explicitly Out of Scope

-   Instagram Graph API discovery
-   live "top workout" search
-   YouTube integration
-   TikTok integration
-   arbitrary web ingestion
-   universal save-anything functionality
-   social features
-   public profiles
-   full fitness tracking
-   progressive-overload algorithms
-   medical advice
-   injury diagnosis
-   supplement recommendations
-   sophisticated AI coaching
-   complex nutrition recommendations
-   complex meal planning
-   large manually designed taxonomy
-   advanced recommendation algorithms

The architecture can remain extensible, but implementation should stay
narrow.

## 18. Metrics

### North-star experiment metric

> **Resolution rate = resolved saved items / imported saved items**

This is an experiment metric, not yet a final business KPI.

### Supporting metrics

**Capture rate:** users who successfully import real saved content.

**Intent rate:** imported items with an intention/note.

**Scheduling rate:** items scheduled.

**Return rate:** users returning after importing.

**Resurfacing engagement:** opens following resurfacing.

**Resolution rate:** imported items that become resolved.

**Time to resolution:** capture to resolution.

**Repeat behavior:** users who import and resolve multiple items.

**Retention:** continued use after initial novelty.

## 19. Validation Questions

The Week Two research should determine:

-   Do users regularly save fitness content?
-   Do they struggle to use those saves later?
-   Do they care about remembering why they saved something?
-   Does automatic structuring reduce friction?
-   Do users schedule saved content?
-   Do they return when saved content is resurfaced?
-   Do saved items become resolved actions?
-   Does Shipyard solve something their existing save system does not?
-   Do users want to keep using it?
-   Is the action loop valuable enough to plausibly pay for?

The strongest validation signal is behavioral:

> **Users import real content, add intentions, return, act, and mark
> items resolved.**

## 20. Research Interview Direction

Focus on real behavior rather than "Would you use this?"

Ask:

> Tell me about the last useful workout video you saved.

> Why did you save it?

> Have you actually used it?

> When did you use it?

> How did you find it again?

> What did you have to do before you could start?

> Did you have to rewatch it?

> Did you rewrite the workout somewhere?

> Have you forgotten why you saved something?

> Have you given up on finding something you saved?

> What do you currently use to organize saved content?

> If you could add one thing to a saved item, what would you want to
> remember?

> Would you want reminders about things you previously said you wanted
> to do?

> What would make that reminder useful rather than annoying?

The most important behavioral question remains:

> **What is the last saved workout you actually used?**

## 21. Positioning

Do not position Shipyard as:

> "A better Instagram Saved folder."

Do not initially position it as:

> "An AI fitness app."

The stronger positioning is:

> **Turn the things you save into things you actually do.**

Fitness version:

> **Save a workout Reel. Actually use it.**

The differentiation is:

> **Capture → Understand → Remember why → Resurface → Act → Resolve**

rather than:

> **Save → Store**

## 22. Landing Page Hypothesis

### Headline

> **Turn workout videos into workouts you actually do.**

### Supporting copy

> Found a great workout on Instagram? Share it with Shipyard. We'll
> understand it, organize it, remember why you saved it, and help you
> actually use it.

### CTA

> **Join the waitlist**

Keep the landing page simple and avoid overpromising unvalidated
features.

## 23. Key Product Risks

**Problem severity:** People may complain about saved content but not
care enough to adopt another app. Test actual behavior.

**Organization vs. value:** Automatic tagging may be a nice feature
rather than a product. Test whether users return for action.

**Reminder fatigue:** Start with explicit intent and scheduling rather
than constant notifications.

**AI accuracy:** Incorrect extraction destroys trust. Never invent
missing workout details.

**Existing competition:** Workout organizers already exist.
Differentiation must come from the personal intent and action loop.

**Scope explosion:** Planning, tracking, coaching, nutrition, recovery,
and medical advice can turn this into a full fitness platform. Keep the
MVP centered on saved content becoming actionable.

## 24. One-Week Build Order

**Phase 1 --- Capture:** Instagram URL/share input.

**Phase 2 --- Understand:** turn the submitted link into a structured
content object.

**Phase 3 --- Organize:** generate tags and metadata.

**Phase 4 --- Intent:** capture an optional note/action.

**Phase 5 --- Library:** show saved items and search/filter.

**Phase 6 --- Schedule:** assign an item to a date.

**Phase 7 --- Resurface:** surface scheduled items at the right time.

**Phase 8 --- Resolve:** mark an item done.

**Phase 9 --- Measure:** track the full funnel.

**Phase 10 --- Optional:** add "Plan my week" using saved workouts.

## 25. Minimal Product

If time is extremely constrained:

> **Share Instagram Reel → AI structures it → user optionally adds
> intent → item can be scheduled → Shipyard resurfaces it → user marks
> it resolved.**

That alone tests the central hypothesis.

## 26. Long-Term Direction

If the fitness wedge works, Shipyard can extend to other "save now, act
later" content.

Possible future sources include Instagram, TikTok, YouTube, Reddit,
websites, and other apps.

Possible future content types include workouts, recipes, learning
resources, travel ideas, products, tutorials, projects, and places to
visit.

But the underlying model remains:

> **Content → Intent → Time → Action → Resolution**

The broader thesis becomes:

> **Your saved content is a list of things you once thought were worth
> doing. Shipyard helps you actually do them.**

## 27. Final Product Definition

For the one-week experiment:

> **Shipyard is a personal action layer for the useful things people
> save from Instagram.**

The user discovers a workout, shares it, Shipyard understands it,
automatically organizes it, remembers why the user wanted it, helps the
user find it again, resurfaces it when appropriate, and lets the user
mark it resolved.

The product is not trying to make saving easier. Saving is already easy.

It is trying to close the gap between:

> **"I should save this."**

and:

> **"I actually did it."**

The core hypothesis for Week Three is:

> **Shipyard can increase the percentage of useful things people save
> that they actually act on.**
