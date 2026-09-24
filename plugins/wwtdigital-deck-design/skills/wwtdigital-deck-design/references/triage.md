# Triage: turning document prose into slides

**Read this before building anything from a document.** The system's rules make a slide
correct. They cannot make a deck the right length, and length is where the worst failure
happened: a 91-slide RFP response where 52 slides were under 10% coverage, 37 headlines were
repeats and nine were titled "(cont.)".

Nothing in the spec book demonstrates cutting. Every recipe shows a composition that already
fits. This file shows the harder move, using the real slides from that deck.

---

## The move, stated once

For each block of source prose, write **one sentence** naming what it has to land. Then pick
the recipe that lands that sentence. The prose that does not serve the sentence goes to an
appendix document, not to another slide.

If you cannot write the sentence, the block does not need a slide. That is the most common
answer and the hardest one to accept.

**Cutting is allowed.** It is the job. An RFP response is a document that also needs a deck,
not a document that needs to become a deck.

---

## Example 1: six slides to one

**What shipped:** slides 25 to 30, "Prime Contractor & Subcontractor Disclosure (RFP 7.1)",
three distinct slides run twice. Two of the six carried a headline and a single line of
grey disclaimer. The other four carried two cards.

**The sentence:** *WWT is the prime, delivers in house by default, and discloses the one
open decision.*

**The slide:** recipe 05, two-panel compare. Headline left, the two scenarios as the two
panels, the disclosure line as the lede. **One slide.**

The rest of RFP 7.1's language is contractual and belongs in the written response. A
procurement officer reads the contract; nobody reads a contract off a projector.

| Before | After |
|---|---|
| 6 slides, 2 of them near-empty, 3 duplicated | 1 slide, recipe 05 |
| headline repeated 6 times | headline appears once |
| the open decision buried on slide 26 | the open decision is the slide |

---

## Example 2: two slides to zero

**What shipped:** slides 2 and 3, "A Partner That Extends The Counter Line" and the same
headline again with "(cont.)". Between them: a date, a name, an email, an RE line and four
paragraphs of cover letter. Slide 3 held a mailing address.

**The sentence:** there isn't one. A cover letter has no job on a screen.

**The slide:** none. The letter is the first page of the written response.

If the deck genuinely needs to open on the argument rather than the cover, use recipe 03 and
say the argument: *82% of executives are increasing AI investment, only 23% are seeing the
value.* One statement, one gradient panel, one photograph. That is what a cover letter is
trying to do and fails at.

---

## Example 3: five slides to one, plus an appendix

**What shipped:** slides 13 to 17, "Our Team (1 of 4)" through "(4 of 4)", plus a
"(1 of 4) (cont.)" that collided with its own numbering. Each held a three-column table with
two rows and roughly 600px of blank canvas beneath.

**The sentence:** *These five named people are accountable, and each has done this before at
a comparable brand.*

**The slide:** recipe 09, card row. Five cards, name and role and one proof clause each.
**One slide.** The full biographies, the client lists and the certifications go to an
appendix document the client can read at their own pace.

The tell that this was pagination rather than design: the numbering. "1 of 4" is a page
number. A deck does not have page numbers, it has an argument.

---

## Example 4: six slides to one

**What shipped:** slides 19 to 24, "Technology Partnerships & Certifications", six times.
Slide 22 carried the headline and the words "Lorem ipsum".

**The sentence:** *We hold current, named partnerships with the platforms your stack runs
on.*

**The slide:** one logo wall. The partner marks at a normalised optical height in a single
row set, the certifications as a short chip row beneath, one source line. Recipe 09 or a
custom assembly from the slots.

A logo wall is one slide by nature. Six slides of logos reads as padding, which is what it
was.

---

## Example 5: when the answer is a different medium

**What shipped:** slides 85 to 90, six "Where Every Requirement Lives" compliance matrices
and two "Every Placeholder, Owned And Dated" trackers. Dense three-column tables at 14 to
17px line pitch, well below the 20px floor, in a deck that would be projected.

**The sentence:** *Every RFP requirement maps to a numbered section of our response.*

**The slide:** one. A summary count and the mapping method, on recipe 13 or a single table
at legal type size, six rows maximum.

The matrices themselves are a spreadsheet. They exist so somebody can check a box against a
row, which is a task nobody performs from a slide. Ship them as an XLSX appendix and the
deck gets its one honest slide.

---

## The arithmetic on that deck

| | Shipped | After triage |
|---|---|---|
| Prime contractor disclosure | 6 | 1 |
| Cover letter | 2 | 0 |
| Team | 5 | 1 |
| Partnerships | 6 | 1 |
| Compliance matrices and trackers | 8 | 1 |
| Everything else | 64 | ~18 |
| **Total** | **91** | **~22** |

Twenty-two slides, each above the coverage floor, each carrying something to read, with
photography on at least one in five and a background device on every light ground. That deck
passes. The 91-slide version could not be made to pass by fixing pixels, because its problem
was never pixels.

---

## What to say when someone pushes back

They will, because the source document feels like the deliverable and cutting feels like
losing content. Three answers that hold up:

**The content is not lost, it moved.** The written response carries the contractual
language, the biographies and the matrices. Nothing was deleted; it was put where it gets
read.

**A slide nobody can read is not coverage, it is a liability.** Fourteen percent of the lines
in that deck were tighter than any step in the type ladder. Projected in a room they are
texture. Claiming a requirement is addressed on a slide where the requirement is illegible is
worse than not having the slide.

**A repeated headline tells the reader you ran out of ideas.** Six slides titled
"Technology Partnerships & Certifications" reads as padding to a procurement panel that reads
decks for a living. The judgment being made in that room is partly about whether you can
think clearly, and deck length is evidence.
