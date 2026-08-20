# SHIPYARD — FULL CHAT HANDOFF

## Purpose

This document is a faithful working handoff of the Shipyard discussion in this chat. It preserves the user's questions, the assistant's recommendations, the evolving hypotheses, the Reddit research discussed, the interview strategy, and the current decision point.

---

# 1. Starting point: Reddit research

## User request

The user provided this Reddit thread:

https://www.reddit.com/r/PKMS/comments/1ke1c41/how_do_you_all_save_videosposts_of_workouts/

and asked:

> find similar reddit threads related to saving instagram workout and recipe videos, sort by latest to older

## Research direction

The assistant searched for related Reddit discussions around:
- saving workout videos
- saving Instagram/TikTok recipes
- organizing saved Reels/posts
- PKM / Notion workflows
- “digital hoarding”
- turning saved content into usable information

The main pattern identified was:

> People generally do not have a problem with the act of saving content. They have a problem with retrieving it later, remembering why they saved it, and actually turning the saved content into action.

---

# 2. Reddit threads identified

The following threads were discussed as especially relevant.

## Very high relevance

### r/PKMS — original thread

“How do you all save videos/posts of workouts?”

https://www.reddit.com/r/PKMS/comments/1ke1c41/how_do_you_all_save_videosposts_of_workouts/

This was the user's original reference.

---

### r/PKMS — saved workout videos

“I was drowning in saved workout videos across TikTok & IG. So I built my own system to actually use them.”

https://www.reddit.com/r/PKMS/comments/1mj6pgv/i_was_drowning_in_saved_workout_videos_across/

Key pattern discussed:
- user follows fitness creators
- saves many workout videos
- has difficulty finding the right one at the gym
- described scrolling for 10–15 minutes
- sometimes skips the workout
- workaround involved importing videos, tagging them, and assigning them to a calendar

This was considered one of the strongest workout-specific signals.

---

### r/microsaas — workout organizer

“Building an app that organizes workouts from Instagram/TikTok/YouTube — would anyone actually use this?”

https://www.reddit.com/r/microsaas/comments/1pgd1v6/building_an_app_that_organizes_workouts_from/

Proposed workflow:
- paste/share workout link
- extract exercises
- extract reps/sets/equipment
- turn into a usable workout

Important observation:
This independently resembles the user's current hypothesis, which is evidence that the problem is real enough for multiple builders to notice.

But it also means the category is already competitive.

---

### r/apps — workout Reel organizer

https://www.reddit.com/r/apps/comments/1ph16t8/i_built_an_app_that_turns_ig_tiktok_workout_reels/

---

### r/iosapps — workout Reel organizer

https://www.reddit.com/r/iosapps/comments/1ph1i55/i_built_an_app_that_turns_igtiktok_workout_reels/

---

### r/iosapps — trackable workout routines

https://www.reddit.com/r/iosapps/comments/1pnz6gc/turn_your_saved_workout_video_reels_into_trackable_workout_routines/

These discussions were used as evidence that the product category is already emerging:
- save workout links
- extract structure
- follow workouts
- track completion

Therefore, simply building “AI organizes my Instagram workout saves” may not be enough differentiation.

---

### r/apps — 100+ workout Reels

“After saving 100+ workout reels, I finally built the workout organizer I needed.”

https://www.reddit.com/r/apps/comments/1pvt95a/after_saving_100_workout_reels_i_finally_built/

Key pattern:
- saves spread across Instagram, TikTok, Notes, screenshots, bookmarks
- remembers the content but not the exact workout details
- switches between apps at the gym
- wants structured workout information

Important implication:
The problem is broader than Instagram's Saved UI.

---

### r/SideProject — losing Instagram workouts

“I built an app to stop losing Instagram workouts in my saved folder.”

https://www.reddit.com/r/SideProject/comments/1t6m0nf/i_built_an_app_to_stop_losing_instagram_workouts/

Interesting progression:
- began as a simple list of Instagram links
- expanded toward tracking weights
- expanded toward generating workouts

This suggested that a narrow save problem can become a broader fitness workflow.

---

### r/sideprojects — TikTok recipes

“I built an app that turns TikTok recipes into saved recipes.”

https://www.reddit.com/r/sideprojects/comments/1vdqg4x/i_built_an_app_that_turns_tiktok_recipes_into/

The product described:
- recipe extraction
- pantry tracking
- expiry reminders
- shopping lists
- meal planning

This was evidence that the same underlying pattern exists in recipes:

> save → structure → action

---

### r/cookingforbeginners — hundreds of recipe videos

“I have hundreds of saved recipe videos and I’ve cooked maybe three.”

https://www.reddit.com/r/cookingforbeginners/comments/1vqgvcb/i_have_hundreds_of_saved_recipe_videos_and_ive/

Key pattern:
- recipes saved on Instagram/TikTok/etc.
- large backlog
- very few actually cooked
- recipes actually used tended to be rewritten as normal ingredients + steps
- following a video live was cumbersome

This became an especially strong example of:

> unstructured content → executable object

---

# 3. Other Reddit threads discussed

These were also surfaced during research:

### r/Notion — organizing TikToks

https://www.reddit.com/r/Notion/comments/190aoyl/i_built_a_better_way_to_organize_tiktoks_to/

The discussion involved people saving large quantities of:
- recipes
- gym routines
- healing techniques
- video editing hacks
- design courses
- other “learn/use later” content

One important conceptual takeaway:

> Saved content becomes a “future self” wishlist.

---

### r/mealprep — organizing recipes from social media

https://www.reddit.com/r/mealprep/comments/1l81aeo/how_do_you_organise_and_save_your_recipes/

Discussed:
- Instagram recipe saves
- screenshots
- Notes
- Notion
- dedicated recipe apps
- difficulty finding recipes again

---

### r/Notion — online hoarding

https://www.reddit.com/r/Notion/comments/1owfggm/how_do_you_handle_your_online_hoarding/

Relevant because it reflects the broader information-hoarding behavior.

---

### r/OrganizationPorn — digital recipes

https://www.reddit.com/r/OrganizationPorn/comments/1nl3cce/what_is_everyone_doing_with_their_digital_recipes/

---

### r/Cooking — recipe app/import

https://www.reddit.com/r/Cooking/comments/1i5mdrf/looking_for_an_app_to_import_and_save_recipes/

---

### r/Cooking — tracking recipes from different sources

https://www.reddit.com/r/Cooking/comments/1i16isa/how_do_you_keep_track_of_recipes_from_various/

---

### r/Notion — Instagram embeds

https://www.reddit.com/r/Notion/comments/s60qwu/how_can_i_embed_instagram_reels_posts_form_notion/

---

# 4. First major insight: saving is not the real problem

The assistant framed the problem as:

> “People don't really have a saving problem — Instagram/TikTok already solve that. They have a retrieval + context + action problem.”

The conceptual pipeline is:

**Discovery → Save → Retrieval → Interpretation → Preparation → Action**

Possible failure points:

1. Can't find the saved content.
2. Finds it but doesn't remember why it was saved.
3. Has to rewatch the video to understand it.
4. Has to manually extract information.
5. Doesn't know what to do with it.
6. Doesn't actually act.

This led to the idea that the product should perhaps not be a better bookmark manager.

Instead:

> **Turn something I found online into something I can actually use.**

---

# 5. Who has the problem?

The assistant described the likely user as:

> A digitally active, self-improvement-oriented person in their 20s–30s who consumes a lot of short-form content and uses social media as a discovery engine for things they want to do in real life.

Potential segments identified:

## A. Fitness enthusiast

- gym-goer
- runner
- yoga/Pilates user
- follows fitness creators
- saves workout demonstrations
- saves routines
- wants to use them later

Pain:
> “I know I saved that workout. Where the hell is it?”

Or:

> “I found it, but now I have to pause/rewind and extract the workout myself.”

---

## B. Home cook

- follows food creators
- saves many recipes
- wants to cook later
- uses Instagram/TikTok/YouTube as a recipe discovery source

Pain:
> “What was that recipe I saved?”

Or:

> “I have to watch the whole Reel while cooking.”

---

## C. Digital hoarder

Saves:
- recipes
- workouts
- travel
- products
- business ideas
- tutorials
- productivity
- design
- health
- etc.

Pain:
> “I know I saved this somewhere.”

---

## D. Aspirational self-improver

Saves things because they represent the person they want to become:

- workouts
- recipes
- books
- travel
- learning
- productivity systems
- lifestyle ideas

Saved content becomes a wishlist for Future Self.

---

## E. Content creator

Saves:
- hooks
- visual inspiration
- competitor references
- editing techniques
- sounds
- ideas
- trends

Their problem is not consumption but:

> content saved as research → future content creation

---

# 6. What changed recently in 2025–2026?

The assistant argued that the timing is important because several trends converged.

## 1. Social media is increasingly a discovery/search layer

People use Instagram/TikTok to answer:
- what workout should I do?
- what should I cook?
- where should I travel?
- what product should I buy?
- how do I do this?

Social content is increasingly functional rather than purely entertainment.

---

## 2. Content volume is enormous

Short-form content volume keeps increasing.

The user is exposed to a practically infinite supply of things that might be useful.

Therefore:

> discovery → save → discovery → save

causes a compounding backlog.

---

## 3. Algorithms improve discovery but make retrieval harder

The better recommendations get, the more useful things users encounter and save.

But feeds are ephemeral.

Instagram knows:

> user saved this Reel

The user knows:

> I saved this because I want a 20-minute shoulder workout on Tuesdays.

That intent/context distinction is important.

---

## 4. AI changed the economics

Previously:

save → manually categorize → manually name → manually transcribe → manually organize

That is too much work.

AI can now potentially:

- watch/transcribe
- identify topic
- extract useful information
- generate tags
- summarize
- create structure
- support semantic search

This enables:

> share Reel → AI understands it → structured object

---

## 5. AI makes execution possible

Example:

### Workout Reel

AI could turn it into:

- Goal: Glutes
- Difficulty: Beginner
- Duration: 25 min
- Hip thrust — 3×10
- Bulgarian split squat — 3×8
- Cable kickback — 3×12

Instead of simply:

> saved Reel

It becomes:

> usable workout

Likewise:

### Recipe Reel

Could become:

- ingredients
- quantities
- instructions
- shopping list

This is a stronger value proposition than “better folders.”

---

# 7. The product levels identified

The assistant distinguished three versions of the idea.

## Product A — Search my Instagram saves

> “Find the Reel I saved.”

Pros:
- obvious problem
- simple

Cons:
- feels like fixing a platform UX issue
- Instagram could build it
- may not be enough to make users switch

---

## Product B — Save useful content from anywhere

> “One personal library for Instagram/TikTok/YouTube.”

More interesting.

But this category is increasingly crowded.

---

## Product C — Turn content into something usable

> “I found this. Make it actionable.”

Examples:

- workout Reel → workout
- recipe Reel → recipe
- travel Reel → itinerary item
- product Reel → wishlist item
- learning video → lesson/notes

This was identified as the strongest product thesis.

---

# 8. Fitness vs recipes

The assistant considered both.

## Recipes

Pros:
- standardized structure
- easy transformation
- clear action
- ingredients + instructions + shopping list

Cons:
- category already has many dedicated products
- recipe import/extraction is increasingly commoditized

Examples discussed:
- ReciMe
- ReelMeal
- Recipe One
- Cookpad import workflows

Therefore recipes were not recommended as the obvious first wedge unless interviews uncovered an unmet need.

---

## Fitness

Pros:
- workout structure is more complex
- exercises, sets, reps, rest, equipment, muscle groups, difficulty
- can evolve into planning and tracking
- repeated usage
- potentially stronger recurring engagement

Potential pipeline:

**Reel → structured workout → library → plans → execution → tracking**

But the assistant explicitly warned:

> There are already workout organizer competitors.

Therefore the user's interviews need to discover what those products miss.

---

# 9. The important distinction for Instagram

The user initially wanted to focus heavily on Instagram because there is “impeccable content” there and Instagram does not provide a good search engine for saved content.

The assistant's recommendation:

Do not make:

> Instagram

the fundamental product boundary.

Instead make:

> **Instagram an initial input channel.**

The deeper behavior is:

> encounter useful content somewhere → save it for future action → struggle to turn it into action

The product can eventually support:
- Instagram
- TikTok
- YouTube
- Reddit
- WhatsApp
- websites

---

# 10. Shipyard context

The user explained:

- This is for a project called Shipyard.
- They are in Week 2.
- They need to speak to at least 40 users by the end of the week.
- Today was Wednesday when this was discussed.
- They need a landing page or waitlist page.
- They need to determine whether the problem is worth solving.
- Week 3 is when they are supposed to start building.
- They do not have unlimited time/headspace.

The assistant advised:

> Do not spend the remaining time endlessly researching or polishing a product.

Instead:

1. Define hypotheses.
2. Make a deliberately simple landing page.
3. Prepare interviews.
4. Recruit users.
5. Conduct interviews.
6. Let evidence determine the product.

---

# 11. The immediate two-hour plan

The assistant suggested:

## First 20 minutes

Write one hypothesis:

> “People who regularly save fitness content from Instagram/TikTok/YouTube struggle to retrieve and actually use those saves later.”

Then three competing hypotheses:

> “The real problem is finding a specific saved workout.”

> “The real problem is converting a video into a usable workout.”

> “The real problem is deciding what workout to do.”

This prevents confirmation bias.

---

## Next 20 minutes

Make a very simple landing page.

Suggested copy:

### Headline

> **Turn workout videos into workouts you can actually follow.**

### Subtext

> Found a great workout on Instagram, TikTok or YouTube? Share it with us. We'll turn the video into a structured workout you can save, search and use at the gym.

### CTA

> **Join the waitlist**

No need for a polished brand.

---

## Next 30 minutes

Prepare interview script.

Important questions:

> “Tell me about the last workout video you saved.”

> “Where did you find it?”

> “Why did you save it?”

> “When did you actually use it?”

> “Can you show me how you found it again?”

> “What happened before you could actually start the workout?”

> “How many workout videos do you think you have saved?”

> “Where else do you save workouts?”

> “Have you ever sent one to yourself on WhatsApp, Notes, Telegram, screenshots, etc.?”

> “If Instagram suddenly made Saved posts perfectly searchable, would that actually solve your problem?”

---

## Remaining 50 minutes

Recruit people.

Suggested message:

> “Hey! I'm researching how people save and use workout videos from Instagram/TikTok/YouTube. I'm not selling anything — I'm trying to understand the problem. Could I ask you a few questions for fifteen minutes sometime this week?”

Goal:
- not forty interviews immediately
- get first 3 conversations scheduled

---

# 12. Interview philosophy

The assistant repeatedly emphasized:

> **Do not ask “Would you use this?”**

Instead:

> **Ask about the last real incident.**

For example:

Bad:
> “Would you use an app that organizes Instagram saves?”

Good:
> “Tell me about the last workout Reel you saved.”

Then:

> “When did you use it?”

> “How did you find it?”

> “What did you have to do?”

> “What was annoying?”

The goal is to observe behavior, not collect compliments.

---

# 13. Critical interview question

The assistant emphasized this one particularly strongly:

> **“What’s the last workout video you saved that you actually used?”**

Then:

- How long between save and use?
- Where was it saved?
- How did they retrieve it?
- What did they have to do before starting?
- Did they rewrite it?
- Did they use another app?

This gives the funnel:

**Discovery → Save → Retrieval → Interpretation → Preparation → Action**

The largest drop-off is likely the real product opportunity.

---

# 14. Suggested interview sample

Instead of 40 identical users, the assistant suggested:

### ~15 fitness users

Workout-specific questions.

### ~15 saved-content / recipe users

Test the broader save → retrieval → action problem.

### ~10 exploratory users

Ask about:
- productivity
- technical workflows
- geeky problems
- B2B information-heavy work

This is important because the user was unsure whether a completely different problem might be more interesting.

---

# 15. Other product directions the user might enjoy

The user asked whether, based on prior interactions, they might be better suited to building something else.

The assistant's observation:

The user seems drawn to:

> **messy information → operationally useful information**

Potential directions:

## A. Personal information → action

The Instagram idea in broader form.

## B. Geeky/analytical tools

Examples:
- research tools
- data investigation
- reconciliation
- inconsistency detection
- “what changed?” systems
- tools that compare multiple information sources

## C. Narrow B2B workflow

A tiny product where:

> upload → process → identify anomalies → produce output

The assistant specifically suggested exploring problems where people repeatedly:

- search
- compare
- organize
- reconcile
- copy
- check

---

# 16. Founder/product-fit insight

The assistant's current hypothesis about the user's product taste:

> The user may not be most interested in “productivity” itself.

The stronger pattern is:

> **taking something messy and making it operationally useful.**

Possible sweet spot:

> **making complicated information systems feel ridiculously simple**

This could apply to:
- personal information
- fitness content
- research
- technical data
- B2B workflows

---

# 17. Recommended ranking

At one point the assistant ranked the directions:

1. Geeky/analytical tool — strongest personal-fit curiosity
2. Personal information → action — current Instagram/fitness direction
3. Narrow B2B workflow — potentially strong but may require more access/headspace

But the assistant also emphasized:

> For Shipyard, don't necessarily choose the thing you'd enjoy building for five years. Choose the thing where you can discover a painful problem fast.

Therefore the recommendation was to continue interviewing rather than decide immediately.

---

# 18. Current strongest product thesis

If forced to choose today:

> **Fitness enthusiasts who discover workouts through short-form video and want to turn those videos into a searchable personal workout library.**

Input:

> Share from Instagram/TikTok/YouTube

Output:

> Structured workout

Potential evolution:

> Workout library → plans → execution → tracking

But this is explicitly a **hypothesis**, not a validated conclusion.

---

# 19. Landing page hypothesis

The assistant proposed:

## Headline

> **Turn workout videos into workouts you can actually follow.**

## Subtext

> Found a great workout on Instagram, TikTok or YouTube? Share it with us. We’ll turn the video into a structured workout you can save, search and use at the gym.

## CTA

> **Join the waitlist**

The landing page is a test, not proof.

---

# 20. Validation criteria

## Strong signals

- User has lots of saved content.
- User has a recent concrete failure.
- User uses ugly workarounds.
- Problem occurs weekly or more.
- Problem wastes meaningful time.
- User has tried another solution.
- User has paid for adjacent software.
- User asks when they can try the prototype.
- User describes the desired solution without prompting.

## Weak / kill signals

- They save but don't intend to use.
- Current system works.
- Perfect native search would completely solve it.
- They cannot remember a recent painful incident.
- Problem happens rarely.
- They don't care enough to change behavior.
- Real pain is something else.
- Competitors already solve it and users are satisfied.

---

# 21. The key conceptual model

The assistant ultimately recommended thinking about the opportunity as:

> **Social media has become the discovery layer, but there is still no great personal execution layer.**

Social platforms:
- discovery
- inspiration
- recommendations

Potential product:
- understanding
- structuring
- retrieval
- execution

The key transformation:

> **unstructured social content → structured personal knowledge → real-world action**

This is stronger than:

> “Instagram saves are hard to organize.”

---

# 22. Google Forms discussion

The user asked for the interview questions in PDFs or Google Forms.

Three PDFs were created:

1. `shipyard_user_interviews_fitness.pdf`
2. `shipyard_user_interviews_saved_content.pdf`
3. `shipyard_user_interviews_exploratory.pdf`

The PDFs contain:
- Fitness deep-dive
- Saved-content discovery
- Exploratory/geeky/B2B questions

The user then asked whether ChatGPT could create a Google Form.

The assistant explained that a Google Forms/Google Workspace connector would be needed to create it directly in the user's Google account.

The assistant checked available plugins/connectors and found no Google Forms connector available.

Google Forms API exists:
https://developers.google.com/workspace/forms/api/guides/create-form-quiz

But no direct connector was available in this chat.

---

# 23. Interview form structure discussed

A proposed Google-Forms-ready structure was:

## Section 1 — Participant profile
- Age range
- Occupation/role
- Workout frequency
- Platforms used
- Platforms saved from

## Section 2 — Actual behavior

> “Tell me about the last useful piece of content you saved.”

Then:
- where found
- what it was
- why saved
- where saved
- whether used
- how retrieved

## Section 3 — Retrieval

- volume of useful saves
- organization method
- failure to find
- time to find
- workaround
- use of screenshots/WhatsApp/Notes/Notion/etc.

## Section 4 — Critical diagnostic

> “If Instagram/TikTok suddenly gave you perfect search across all your saved content, would that completely solve the problem?”

Options:
- Yes
- Mostly
- Somewhat
- No
- I don't really have this problem

Then:

> “What's still missing?”

## Section 5 — Fitness branch

Only for fitness users:
- workout types
- last workout actually used
- retrieval
- pausing/rewinding
- extracting sets/reps
- separate fitness app
- desired structured workout
- trust in AI-generated workout

## Section 6 — Alternatives

- existing apps
- what works
- what doesn't
- paid products
- switching trigger

## Section 7 — Open discovery

> “What's something else in your life/work that you repeatedly have to search, organize, compare, copy, reconcile, or keep track of that you hate doing?”

Then:

> “Tell me about the last time you had to do it.”

---

# 24. Files created in the chat

Earlier PDFs:

- `shipyard_user_interviews_fitness.pdf`
- `shipyard_user_interviews_saved_content.pdf`
- `shipyard_user_interviews_exploratory.pdf`

A broader handoff ZIP was also created:

`shipyard_handoff.zip`

It contained:
- README
- research brief
- Reddit evidence
- interview guide
- validation framework
- source index
- interview PDFs

Then a Markdown handoff ZIP was created:

`shipyard_handoff_markdown.zip`

The current request is for the entire chat in Markdown, which is this document.

---

# 25. Current state / what Claude should do next

Do not assume the final product is:

> “Instagram workout organizer.”

The current state is:

**Hypothesis under validation.**

Claude should help the user:

1. Conduct the 40 interviews.
2. Capture actual behavior.
3. Cluster pain points.
4. Identify the highest-frequency/highest-pain workflow.
5. Compare fitness vs broader saved-content vs geeky/B2B opportunities.
6. Look for existing workarounds and willingness to pay.
7. Decide the smallest product to build in Week 3.
8. Avoid premature feature development.

The most important question is:

> **What painful behavior is happening often enough that people will change their behavior or pay to solve it?**

Not:

> “Is an Instagram save organizer a cool idea?”

---

# 26. One-sentence handoff

The entire current Shipyard thesis can be summarized as:

> **The user is investigating whether there is a valuable product opportunity at the boundary between social-media discovery and real-world action, initially using saved fitness content as a wedge, but they explicitly want the research to remain open to a better productivity, geeky, analytical, or B2B problem.**
