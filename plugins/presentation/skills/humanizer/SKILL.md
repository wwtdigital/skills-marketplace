---
name: humanizer
description: |
  Remove AI writing patterns from text: hard bans (em dashes, Claude-isms,
  negative parallelism, bold-first bullets), frequency violations (rule of
  three, rhetorical questions, repeated punchy fragments) and voice problems
  (corporate jargon, inflated stakes, sycophantic tone, vague attributions),
  through a tiered audit: hard ban pass, frequency check, voice calibration,
  self-critique, final. Use when someone asks for it directly: "humanize this",
  "make it sound less like AI", "de-AI this", "does this read as AI?", "make
  this sound like a person wrote it", "clean up the AI tells", or when someone
  asks for a final pass on text before it goes to a real person. Not for
  flagging AI writing in a document without changing it (a separate skill),
  for brand or visual style, or for writing new content from scratch.
license: MIT
metadata:
  owner: toby.gerber@wwt.com
  category: presentation
  status: beta
  connectors: []
  version: 4.1.0
---

# Humanizer v4.0

Good writing sounds like a person wrote it. That's the whole job.

This skill removes bad patterns and replaces them with something better. Sterile, pattern-free writing that has no voice is still obviously AI. The goal is writing that reads like it came from a real human who thinks clearly, speaks plainly, and has something to say.

Use this skill on any piece of writing: emails, strategy docs, presentations, Slack messages, reports, proposals. If it came out of an AI and needs to go to a real person, run it through here first.

---

## The Three-Tier System

Not all problems are equal. This skill uses three tiers:

**Tier 1: Hard Bans.** These never belong in any piece of writing. Remove every instance, no exceptions.

**Tier 2: Frequency Violations.** These patterns aren't always wrong. One tricolon in a piece is fine. Three is a tell. Flag when the same pattern appears more than once or twice in the same document.

**Tier 3: Voice Problems.** Patterns that make writing feel corporate, inflated, or generic. Fix based on context and intended audience.

---


The full pattern catalog, with before/after examples for every pattern in all three tiers, is in
[references/patterns.md](references/patterns.md). Read it before the first pass.

---

## Voice Calibration

When you have a writing sample from the person, use it.

Read the sample before touching the text. Pay attention to:
- Sentence length (short? long? mixed?)
- Word choice level (casual? technical? somewhere between?)
- How they handle transitions (connectors, or just move to the next point?)
- Punctuation habits
- Any recurring phrases or verbal tics

Then match that in the rewrite. Don't stop at removing AI patterns. Replace them with patterns from the sample.

If no sample is provided, default to: direct, plain-spoken, warm but not soft. Write like a person who knows what they're talking about and doesn't need to perform it.

---

## The Process

Run this in order. Don't skip steps.

**1. Hard ban pass**
Find and remove every Tier 1 violation. No exceptions. Em dashes, Claude-isms, negative parallelism, bold-first bullets, signposting, sycophantic residue.

**2. Frequency audit**
Scan for Tier 2 patterns. Flag any that appear more than once. Fix the repetition: keep one if it's earning its place, cut or rewrite the rest.

**3. Voice pass**
Work through Tier 3. Deflate significance inflation. Cut AI vocabulary. Replace formal words with plain ones. Make sure the register matches the audience.

**4. Read it out loud (mentally)**
Does it sound like a person talking? If any sentence makes you pause because it sounds assembled rather than written, rewrite it.

**5. Self-audit and verify**
Ask: "What still makes this obviously AI-generated?" Answer honestly. Then fix those things.
Then check the rewrite against the Quick Reference hard-ban list at the end of this file, one
item at a time. Zero hits is the bar before you present anything. (The "Before:" examples in
the pattern catalog are the one place those patterns are allowed to appear.)

**6. Final version**
Present the cleaned output. If changes were significant, note what categories you found. Skip the line-by-line changelog, just the main things: "Heavy on significance inflation, three em dashes, two instances of negative parallelism."

---

## Output Format

1. **Final rewrite** (this is the main output)
2. **Brief audit note**: one short paragraph on what you found and fixed
3. Skip the draft-then-critique cycle unless the piece is long or complex enough to warrant it

---

## One Rule Above All Others

Any of these patterns used once might be fine. The problem is repetition. AI writes in patterns because it's predicting the next token, not making choices. Humans break patterns. They vary. They surprise. They contradict themselves and then correct. They end sentences abruptly.

When something reads like it was assembled rather than written, that's the problem to solve. The pattern list is just a map to find it faster.

---

## Quick Reference: The Hard Ban List

Never use these. Not once.

- Em dashes (—)
- "Here's the kicker" / "Here's the thing" / "Here's where it gets interesting"
- "What I'd flag honestly" / "One honest flag"
- "That's the floor, not the ceiling"
- "Let's dive in" / "Let's unpack" / "Let's break this down" / "Let's explore"
- "It's worth noting" / "Importantly" / "Notably"
- "Delve" (any form)
- "Imagine a world where..."
- "Think of it as..." (patronizing analogy)
- "In conclusion" / "To sum up" / "In summary"
- Negative parallelism ("It's not X, it's Y")
- Bold-first bullets (every item starts **Bold Keyword:** ...)
- Sycophantic openers ("Great question!", "Of course!", "Certainly!")
- Chatbot closers ("I hope this helps!", "Let me know if you'd like me to expand...")


---

Adapted from [humanizer](https://github.com/blader/humanizer) by Siqi Chen (MIT). See `LICENSE`.
