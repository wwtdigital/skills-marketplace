# Humanizer pattern catalog

Every pattern the humanizer checks, by tier, with before/after examples.
The "Before:" lines deliberately contain the patterns they illustrate.

## Tier 1: Hard Bans

These are out. Every time. No exceptions.

### Em Dashes
The single most reliable AI tell. Replace with a comma, a period, or split into two sentences. That's it.

```
Before: The problem — and this is the part nobody talks about — is systemic.
After:  The problem, which nobody talks about, is systemic.

Before: We hit a wall — the timeline collapsed.
After:  We hit a wall. The timeline collapsed.
```

### Claude-isms and AI Tells
Phrases that teammates, clients, and executives have learned to recognize. Seeing one of these in a document is now enough to make people distrust the whole thing.

Never use:
- "Here's the kicker"
- "Here's the thing"
- "Here's where it gets interesting"
- "Here's what most people miss"
- "What I'd flag honestly"
- "One honest flag"
- "That's the floor, not the ceiling"
- "Let's dive in" / "Let's unpack this" / "Let's break this down"
- "Let's explore"
- "It's worth noting" / "It bears mentioning" / "Notably" / "Importantly"
- "Delve" (in any form)
- "Certainly" (as filler)
- "Imagine a world where..."
- "Think of it as..." / "It's like a..."
- "In conclusion" / "To sum up" / "In summary"

### Negative Parallelism
The "It's not X, it's Y" pattern. Occasionally effective; used constantly by AI. If you see it at all, cut it.

```
Before: It's not bold. It's backwards.
After:  It's a backwards choice.

Before: This isn't a process problem. It's a culture problem.
After:  The process isn't broken. The culture is.
```

### Bold-First Bullets
Every bullet starting with a bolded keyword followed by a colon. Nobody writes lists this way by hand.

```
Before:
- **Speed:** The interface loads in under 200ms.
- **Security:** All data is encrypted at rest.
- **Usability:** Users rated the experience 4.8/5.

After:
The interface loads in under 200ms, all data is encrypted at rest,
and users rated the experience 4.8/5.
```

### Signposting Openers
Announcing what you're about to do instead of doing it.

```
Before: Let's dive into how this works. Here's what you need to know.
After:  [Just start explaining how it works.]
```

### Sycophantic Tone
Chatbot residue. Cut everything in this category.

```
Before: Great question! You're absolutely right. I hope this helps!
        Let me know if you'd like me to expand on any section.
After:  [Just answer the question.]
```

---

## Tier 2: Frequency Violations

These patterns are fine once. Annoying twice. An obvious tell three times or more. Flag them when they appear multiple times in the same piece.

### Rule of Three (Tricolon)
One tricolon is elegant. Three back-to-back tricolons are a recognition failure.

```
Flagged: "innovation, inspiration, and industry insights"
         "workflows, decisions, and interactions"
         "fast, reliable, and scalable"
         [All three in the same paragraph]

Fix: Break the pattern. Use two items, or four, or just one strong one.
```

### Rhetorical Questions Answered Immediately
The model asks a question no one asked, then answers it for drama.

```
Flagged: The result? Devastating.
         The worst part? Nobody saw it coming.

Fix: "The result was devastating." Say it. Don't perform it.
```

### Short Punchy Fragments as Standalone Paragraphs
Effective once. Exhausting as a pattern.

```
Flagged: "He published this. Openly. In a book. As a priest."
         "Platforms do."
         [Used repeatedly across the same piece]

Fix: One or two fragments for emphasis is fine. After that, write full sentences.
```

### Anaphora (Repeated Sentence Openers)
Starting three or more consecutive sentences with the same word or phrase.

```
Flagged:
They assume users will pay.
They assume developers will build.
They assume ecosystems will emerge.
They assume markets will follow.

Fix: Combine, vary, or restructure. Two is rhythm. Four is a tic.
```

### Historical Analogy Stacking
Rapid-fire list of historical companies or moments to build false authority.

```
Flagged: "Apple didn't build Uber. Facebook didn't build Spotify.
          Stripe didn't build Shopify. AWS didn't build Airbnb."

Fix: Pick the one analogy that actually serves the argument. Drop the rest.
```

### False Ranges
"From X to Y" where X and Y aren't on any real scale.

```
Flagged: "from innovation to cultural transformation"
         "from the Big Bang to the cosmic web"

Fix: List the things plainly. "X, Y, and Z" beats a fake spectrum every time.
```

---

## Tier 3: Voice Problems

These patterns don't necessarily announce AI. They make writing feel corporate, inflated, or generic. Fix them when the goal is direct, grounded, human writing.

### Significance Inflation
Puffing up ordinary facts with fake importance.

**Words to watch:** pivotal, testament, underscores, highlights, reflects broader, marks a moment, sets the stage for, transformative, enduring legacy, key turning point

```
Before: This marks a pivotal moment in the evolution of regional design,
        underscoring our commitment to innovation.
After:  This is the first time we've shipped a design system across
        all three product lines.
```

### Promotional Language
Writing that sounds like a press release or tourism brochure.

**Words to watch:** nestled, breathtaking, vibrant, boasts, renowned, groundbreaking, must-visit, stunning, rich cultural heritage

```
Before: Nestled within our groundbreaking design ecosystem, this component
        boasts remarkable versatility.
After:  This component works across eight different layout contexts.
```

### Vague Attributions
Invoking unnamed experts and imaginary sources.

**Words to watch:** experts argue, observers have cited, industry reports suggest, several sources, many have noted

```
Before: Experts argue that this approach has significant drawbacks.
After:  Name the expert, or cut the attribution entirely.
```

### Copula Avoidance
Replacing "is" and "are" with pompous alternatives.

**Words to watch:** serves as, stands as, marks, represents, functions as

```
Before: This component serves as the foundation of the design system.
After:  This component is the foundation of the design system.
```

### AI Vocabulary Words
Words that appear in post-2023 text at a frequency no human matches.

**Cut or replace:** delve, leverage (as a verb), utilize, robust, streamline, harness, paradigm, synergy, ecosystem (when used loosely), tapestry, landscape (abstract), interplay, intricate/intricacies, foster, garner, showcase, pivotal, vital, crucial, enhance, align with

```
Before: We need to leverage robust frameworks to streamline our workflows
        and harness the full potential of the ecosystem.
After:  We need better systems so the work moves faster.
```

### Grandiose Stakes Inflation
Everything is the most important thing that has ever happened.

```
Before: This will fundamentally reshape how we think about everything.
        It defines the next era of computing.
After:  This changes how the team handles approvals. That's worth paying
        attention to.
```

### Superficial "-ing" Analyses
Tacking a present participle onto the end of a sentence to fake depth.

```
Before: The new interface launched in Q2, reflecting broader trends
        in enterprise UX and highlighting our commitment to accessibility.
After:  The new interface launched in Q2.
        [If there's a real point about trends or accessibility, make it.]
```

### Formulaic Challenges Sections
Acknowledge-and-immediately-dismiss. AI's version of intellectual honesty.

```
Before: Despite its challenges, the initiative continues to thrive.
After:  [Either describe the challenges specifically, or don't mention them.]
```

### Excessive Hedging
Over-qualifying to the point of saying nothing.

```
Before: It could potentially possibly be argued that this might have
        some effect on outcomes.
After:  This likely affects outcomes. (Or: We don't know yet.)
```

### Generic Positive Conclusions
Vague uplift as a substitute for an actual ending.

```
Before: The future looks bright. Exciting times lie ahead as we continue
        our journey toward excellence.
After:  [End on the last real point you made. That's the conclusion.]
```

### Overly Formal Word Choices
Simple words replaced with Latinate alternatives.

| Replace | With |
|---|---|
| utilize | use |
| facilitate | help / enable |
| leverage (verb) | use |
| endeavor | try |
| commence | start |
| obtain | get |
| subsequently | then |
| prior to | before |
| in order to | to |
| regarding | about |
| provide assistance | help |
| ascertain | find out |

### Missing Contractions in Casual Writing
Formal expanded forms in conversational contexts. A subtle but reliable tell.

```
Before: We do not recommend skipping this step. It is easy to overlook.
After:  We don't recommend skipping this step. It's easy to overlook.
```

*Don't force contractions in formal writing. Match the register.*

### Filler Phrases
Verbal throat-clearing that adds length without adding anything.

```
Cut entirely: "It is important to note that..."
              "It is worth mentioning that..."
              "It should be noted that..."
              "Due to the fact that..." → "Because"
              "In order to..." → "To"
              "At this point in time..." → "Now"
              "Has the ability to..." → "Can"
```

---
