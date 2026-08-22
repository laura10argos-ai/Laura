---
name: sl-competitor-analysis
description: Actively research YouTube competitors in a creator's niche using web search, then synthesize findings into a complete Competitor Intelligence Sheet with proven outlier video ideas. This skill performs real searches — it doesn't just tell the user what to do, it does the research and surfaces the patterns. Use whenever someone says "I need to analyze my competitors", "research YouTube channels in my niche", "what's working on YouTube in [topic]", "find me competitors", "competitor research", or is on Day 2 of Month 1 in the Sandy Lee AI Content System. Always requires a confirmed niche or topic before starting. Output is a Competitor Intelligence Sheet with channels, outliers, patterns, gaps, and 10 proven video ideas remixed for the user's voice.
---

# Competitor Analysis (Automated Research Edition)

This skill DOES the research. It uses web search to find real YouTube creators in the user's niche, surfaces outliers, identifies patterns, and produces an Intelligence Sheet with proven video ideas.

The user provides their niche. Claude does the search, analysis, and synthesis.

**Requires:** Confirmed niche (from Personal Brand Blueprint) or a clear topic statement
**Time:** 15-30 minutes (depending on depth)
**Output:** Competitor Intelligence Sheet with channels, outlier patterns, content gaps, and 10 ready-to-film video ideas

---

## Open with the most important insight

Tell them this BEFORE starting the research:

> The biggest mistake creators make: they study only the big channels in their niche.
>
> Big channels show you what's saturated. The real gold is in **small channels with outlier hits** — a channel with 5K subscribers and a video at 100K views means a proven topic with low competition. Those are the videos to make first.
>
> So I'm going to study big AND small. The small creators are where I'll find your first 10 video ideas.

This reframe matters. Lead with it every time.

---

## How to actually run this skill

### Step 1: Confirm the niche (and sharpen if needed)

Before any searching, confirm:
- What's the niche? (Specific topic area)
- Who's the ICA / dream viewer?
- What 3-5 keywords would the dream viewer search?

If the niche is too broad ("AI" or "personal finance"), ask 1-2 sharpening questions before proceeding. Vague niche = vague research.

### Step 2: Run the search waves

Use web_search to find creators in 3 waves:

**Wave 1 — Small creator hunt (priority)**

Run 4-6 searches with this pattern:
- `"[niche keyword]" YouTube channel under 10K subscribers`
- `"[long-tail keyword from ICA's search behavior]" YouTube`
- `[niche] YouTube creators 2025`
- `best [niche] YouTube channels small`
- `[specific subtopic] YouTube tutorial`

Look in results for:
- Channel names with smaller subscriber counts but viral video performance
- Reddit threads, Twitter/X posts where people share niche YouTubers
- Listicle articles ("best YouTubers for X")
- YouTube search result pages

**Wave 2 — Mid-tier creators**

Run 2-3 searches:
- `[niche] YouTube channels 10K-250K subscribers`
- `fast growing [niche] creators YouTube`
- `[niche] creators to watch 2025`

**Wave 3 — Big creator landscape**

Run 1-2 searches:
- `top [niche] YouTube channels`
- `biggest [niche] YouTubers`

### Step 3: Deepen on the most interesting channels

Once you have a list of 15-25 candidates, use web_fetch to look closer at the most promising ones. Especially:
- Channels mentioned in multiple sources (signal of relevance)
- Small channels with one obvious outlier hit
- Channels with thumbnails or titles that match clear patterns

For each channel investigation, note:
- Channel name + estimated size
- 1-3 of their highest-view videos (with titles)
- Apparent format (tutorial, vlog, list, commentary)
- Apparent thumbnail style
- Hook style if visible from titles

### Step 4: Calculate outlier signals

For any channel where you have view-count data on multiple videos:

> **Outlier Score = Video Views ÷ Channel Average Views × 100**

Channel average = recent videos minus their top 1-2 anomalies.

Outlier scores:
- 200+ = strong signal (worth noting)
- 500+ = viral outlier (definitely note)
- 1000+ = breakout (study this video specifically)

If exact view counts aren't accessible, eyeball it: "This channel typically gets 5K views, this video has 80K — that's a clear outlier." Don't get hung up on perfect math. Look for obvious anomalies.

### Step 5: Surface patterns

After gathering data on 20-40 channels, look across the dataset for:

**Format patterns**
- What dominates? (Tutorial / story / list / commentary / vlog)
- What's the average video length in this niche?

**Thumbnail patterns**
- Do outliers share a visual style? (Face + text / no face / before-after)
- Common color palettes?

**Title patterns**
- Recurring formats? ("How I X in Y minutes" / "5 things..." / "I tried...")
- First-3-words analysis on outliers

**Topic patterns**
- Which subtopics show up across multiple channels?
- Which subtopics are NOT being covered well? (Gaps)

### Step 6: Generate the 10 outlier video ideas

This is the payoff section. Take the strongest outlier topics from the research and remix them into ideas the user can actually film.

Rules:
- Never copy a title verbatim — remix into the user's voice using their Blueprint
- Mix 2-3 format types across the 10 ideas
- Each idea must be specific enough to film (not "AI tools" but "5 AI Tools That Cut My Editing Time in Half")
- Bias toward topics with high search demand AND low big-creator coverage

---

## Required tools

This skill REQUIRES web access. Use:
- **web_search** — for finding channels, listicles, niche communities
- **web_fetch** — for digging deeper on specific channel pages or articles when needed

If web search is unavailable, fall back to manual research mode and tell the user explicitly: "I can't access the web right now, so this will be a guided manual research session instead." Don't fake research with general knowledge.

---

## Output — Competitor Intelligence Sheet

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPETITOR INTELLIGENCE SHEET — [Niche]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHANNELS RESEARCHED: [number]
TIME WINDOW: Recent uploads through [date]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE TOP 10 OUTLIER VIDEO IDEAS (your starting bank):

1. [Specific title — remixed for your voice]
   Inspired by: [Channel] — [original video title] — [outlier signal]

2. [Specific title]
   Inspired by: [Channel] — [original] — [signal]

[... continue for all 10]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PATTERNS OBSERVED (the "rules" of this niche):

• [Pattern — e.g. "Outliers in this niche use face + text thumbnails with a colored accent"]
• [Pattern — e.g. "How I + specific outcome dominates the title format"]
• [Pattern — e.g. "Best performers are 8-12 min long form, not Shorts"]
• [Pattern]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONTENT GAPS (underserved topics — your differentiation opportunity):

• [Gap — what's missing or poorly covered]
• [Gap]
• [Gap]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHANNELS TO WATCH WEEKLY:

Small (priority):
• [Channel] — [subs] — outlier specialist, watch next 3 uploads
• [Channel] — [subs] — fastest growing in your tier

Mid:
• [Channel] — [subs] — what's working at the next level
• [Channel] — [subs] — recent breakout

Big (for landscape):
• [Channel] — [subs] — format reference
• [Channel] — [subs] — topic reference

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YOUR UNFAIR ADVANTAGE VS THIS LANDSCAPE:

[2-3 sentences: based on the patterns and gaps, what can YOU bring
that the current creators in this niche aren't? Pull from the user's
Blueprint to make this specific.]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FIRST VIDEO PICK:

Recommended: Idea #[N] from above

Why: [Reason — usually a mix of "highest-confidence outlier signal" +
"matches your unfair advantage" + "low competition from big creators"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEXT STEPS:
→ Save this sheet permanently (you'll reference it for months)
→ Watch the small "channels to watch" weekly for new outliers
→ Move to packaging (Day 6 in the program)
```

---

## Rules for running this skill

- **Search waves before synthesis.** Don't try to generate the Intelligence Sheet from general knowledge. Always run real searches first.
- **Small creators are the priority.** This is the most counterintuitive insight in the skill. Make sure they end up in the final list.
- **Don't fake outlier scores.** If exact view counts aren't accessible, say so. Use language like "appears to be an outlier based on visible signals" rather than fabricating precise numbers.
- **Remix titles, never copy.** Every video idea must be in the user's voice from their Blueprint. Direct copying defeats the point of competitor research.
- **The First Video Pick is mandatory.** This is the bridge from research to action. Don't skip it.
- **Be honest about what you found.** If a niche has very few clear outliers, say so. Don't manufacture insights to fill the template.
- **Pull from their Blueprint when remixing.** If their voice is "no-fluff and direct," the remixed titles should reflect that. If their ICA is solopreneurs, remixed titles should speak to solopreneurs.
- **The Intelligence Sheet feeds directly into Packaging (Day 6).** That's where their first video gets packaged from one of these top 10 ideas. Make sure the ideas are actually filmable.

---

## What this skill does NOT do

- Doesn't replace YouTube Studio analytics for the user's own channel (that's a different skill area)
- Doesn't pull live subscriber counts in real-time (uses what's surfaced via web search)
- Doesn't do brand or visual analysis (that's sl-brand-kit)
- Doesn't write scripts (that's the Script Writer agent in Slee Studio)
- Doesn't replace ongoing competitor watching — it's a Day 2 starting point. The user should still watch their "Channels to Watch" list weekly going forward.
