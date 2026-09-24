# Prompting the WWTDigital Design System

How to ask for a deck and get one back that survives review. Every item here came out of a real
build that went wrong.

Two audiences. **Part 1** is for someone who has never used this. **Parts 2 to 5** are for people
building decks most weeks. Skip ahead if that is you.

Versions and thresholds live in `SKILL.md`, where the code checks them on every run. A copy here
would be wrong within a month.

---

## Part 1 · Your first deck

### Install and check, once

Install the `wwtdigital-deck-design` plugin (`/plugin install wwtdigital-deck-design@wwtdigital`), make
sure Aptos is on the machine (see the plugin README), then run two things
before asking for anything.

```bash
sh setup/run.sh doctor.py                            # what this machine can enforce
sh setup/run.sh teardown.py -o WWT-teardown.html     # the system, rendered. Open it
```

(If it says SETUP NEEDED, run `sh setup/setup.sh` once; Claude will offer to do it for you.
On Windows use `setup\run.ps1` and `setup\setup.ps1`.)

The doctor answers ENFORCED, PARTIAL or DOCUMENTATION. ENFORCED means the validator runs and measures
your deck. PARTIAL means only the fast static lint runs, leaving contrast, rendered measure, widows,
ink coverage, photography share and architecture diversity unchecked. DOCUMENTATION
means nothing runs and you have a stylesheet.

**If it says anything but ENFORCED, say so when you hand the deck over.** The lint covers a
fraction of the rules, and the difference is most of the quality bar.

The teardown writes one page carrying every colour as a swatch with its measured contrast ratio,
the type ladder at true size in real Aptos, the mesh at its real opacity, and the four things this
system does not have, named as gaps. Open it. Two decks came back wrong from builders who had the
skill installed and had never opened the system. Both failed in ways a table of hex values cannot
prevent, because a table is what a reader skims.

### The shape of a good first ask

You are not writing a prompt. You are briefing a designer. Give it:

- **Who is in the room and what you need them to do afterwards.** Not "an executive audience".
  "The CIO and two of her directors, and I need them to approve a six-week assessment."
- **The source material, attached.** Not a description of it. Attach the deck, the notes, the
  transcript, the RFP.
- **How long.** Under thirty slides unless there is a reason. Over forty fails outright.
- **PPTX or HTML,** because that changes the font story and the licence position. See Part 3.
- **What imagery you want.** This one matters more than it should. See Part 2.

A first ask that works:

> Build a WWTDigital deck from the attached discovery notes. Audience is the CIO and two
> directors at a regional grocery chain; I need them to approve a six-week AI readiness
> assessment. Twelve to fifteen slides. Final deliverable is a PPTX they can forward. Use
> photography wherever it earns its place, I want to land near 40% of slides. Plan it first and
> show me the plan before you build anything.

### Expect to be asked questions

Above eight slides the skill writes a plan before it builds: one line per slide saying what that
slide has to land, its role, its recipe and its source material. If it cannot write that sentence
for a slide, the slide has no job and should not exist. Let it. Reading the plan takes thirty
seconds, and it is where a wrong deck gets caught cheaply.

---

## Part 2 · The five prompts that change the output most

### 1. Ask for imagery explicitly, and say why

**This is the single highest-value instruction you can add.** Left alone, the default lands too
few images. A text-heavy deck is the most common way this system produces something correct and
lifeless.

The system's own numbers: 30% of slides is the floor and 40% the target. A slide counts as
carrying photography when its imagery sums to 15% of the canvas, card images included. Nineteen
approved frames ship with the skill.

What went wrong before this was written down: one deck came back at 27%, another at 14%. Asked
for without saying what it was for, imagery arrived as thumbnails pushed into the top right corner,
related to nothing and forming no background. That is worse than no image, because it reads as a
mistake rather than an omission.

So say what the imagery is *for*:

> Use photography wherever it earns its place, aiming near 40% of slides. Images should either
> relate to specific content, anchor a card, or form a real background. No floating thumbnails.
> A band or an image at the top or bottom of a page runs to that edge and both sides.

### 2. Ask for the measurement, not the reassurance

"Does this look right?" gets you an opinion. Every defect this system has shipped passed visual
review first: a headline at 1.16:1 contrast, a logo wrong on all four axes, twenty-one widows, an
entire deck set in a substituted typeface, a cover wedge painted across a light slide under all of
its text. All of them looked fine in a screenshot.

> Run the validator and paste the output. I want to see the FAIL and WARN lines, not a summary.

And when a PPTX ships:

> Run verify_pptx.py against the HTML and paste it. Tell me plainly which gate ran and which
> did not.

### 3. Never ask it to open the built file

After inlining, a deck is several megabytes of base64 and a spec book is sixteen. Reading one
burns your usage limit for no benefit, and it is the actual cause of the "hit token limits"
reports.

The scripts exist so nothing has to read it. If you want to know what is in a built deck, ask for
the lint, the validator or a rendered screenshot.

> Check it with the scripts. Do not open the built file.

### 4. One deck per session

Start a new conversation for each deck. A build makes many tool calls and produces a lot of
intermediate output, and a session that has already built one deck carries all of it. Nothing
breaks. You pay for it, and you get a vaguer collaborator.

### 5. Say whether your fix is a one-off or a correction to the system

When you override something, you are doing one of two things and they have opposite consequences.
A client-specific or context-specific change should be made and then left alone, so say it is a
one-off and nothing in the system moves. A change that means the system itself is wrong should be
named as one, and it becomes a rule, a threshold or a retirement that every future deck inherits.

Getting this wrong in either direction is expensive. A one-off committed as a correction teaches
the system a client's preference. A real correction left as a one-off means you fix the same thing
every deck.

> This is a one-off for this client, do not change the system.

> This is wrong in the system. The blue gradient rule was never intended as an element. Remove it
> from the stylesheet, the gallery and both reference decks.

---

## Part 3 · Telling it what you are actually shipping

Say the format in the first message, because three things change with it.

**PPTX.** The exporter embeds Aptos automatically, no manual step. But font embedding is a Windows
PowerPoint feature. PowerPoint for Mac, Keynote, Google Slides and LibreOffice ignore it outright,
and that was measured rather than assumed: with Aptos hidden from the operating system, a correctly
embedded deck rendered end to end in a fallback face. Two answers are durable: Aptos installed on
the machine opening it, which Microsoft 365 provides, or a PDF. Ask which before you promise
anything.

**HTML.** Aptos is proprietary to Microsoft. A 365 subscription grants use of the font, not the
right to self-host it as a webfont or inline it into something handed to a client. Internal
tooling is fine. An HTML deck leaving WWT is a different act, so confirm the licence position
first. PPTX and PDF embedding is the normal and permitted route.

**A deck someone else will edit.** Say so. It changes how much ships as live text rather than
baked artwork. Four CSS features have no PowerPoint equivalent and ship as pictures either way.

---

## Part 4 · Which model, and why

Verified against Anthropic's documentation in September 2026. The lineup moves; the reasoning
underneath it moves slower, so that is written out below the table.

| | Best for | Context | Default effort |
|---|---|---|---|
| **Claude Opus 5.5** | Long-running agentic work. **Start here.** | 1M | `medium` |
| **Claude Fable 5.1** | Demanding reasoning and long-horizon work | 1M | `high` |
| **Claude Sonnet 5** | The best balance of speed and intelligence | 1M | `high` |
| **Claude Haiku 4.5** | Fastest, near-frontier. Not for deck builds | 200K | not supported |

Set the model and the effort level from the menu next to the send button, or `/model` in Claude
Code. You can change either mid-conversation and it applies from the next response.

### What to use for what

**Building a deck: Opus 5.5 at `xhigh` effort.** This is the workhorse and the setting matters.
Anthropic's guidance for complex coding and agentic tasks on Opus 4.7 or newer is to try extra high
first, and a deck build is exactly that shape: dozens of tool calls, a validator that has to be
re-run until it is clean, and a long stretch of work where the thread cannot be dropped. Opus 5.5
defaults to `medium`, a level lower than Opus 5 did, so a build left on the default runs leaner than
you want.

**Narrative, planning and critique: Opus 5.5 at `high`, or Fable 5.1 for a hard pitch.** Writing
the story and deciding what each slide has to land is reasoning work, not agentic work. It does not
need `xhigh`.

**Fable 5.1 when Opus 5.5 at higher effort still falls short.** That is Anthropic's own framing
and it is the right threshold. It is also the slowest and the most expensive, so reach for it when
the thinking is hard rather than as a default.

**Sonnet 5 for iteration on a deck that already exists.** Fixing four slides, changing copy,
re-exporting. Fast, a fifth of the cost of Fable, and holds the 1M context you need for the system.

**Not Haiku 4.5 for a build.** 200K context and no effort setting. Fine for a quick question.

### Effort costs usage

Higher effort spends more tokens, so you reach your usage limit sooner. That is the real trade,
and it is the same lever as the token problem in Part 2. Running low, `xhigh` for the build and
`medium` for the conversation around it beats a whole session pinned to `max`. Reserve `max` for
correctness-critical work you are willing to wait for.

### How to re-derive this when the lineup changes

Three properties make a model right for this work.

1. **A large context window.** The design system is substantial, a plan plus source material adds
   up, and a validator run returns real output. 1M is comfortable. 200K runs out.
2. **It holds a long agentic thread.** A build is a sequence of dependent tool calls where step
   twelve depends on step three. That is what "long-horizon agentic" names, and what effort levels
   above `high` are built for.
3. **It re-runs a failing gate instead of declaring victory.** The most useful behaviour in this
   whole workflow is a model that reads a FAIL, fixes it, and runs the validator again without
   being told. Lower effort produces fewer and terser tool calls, which is exactly the wrong
   instinct here.

Whatever the model names are when you read this, pick the one whose documentation describes
long-horizon agentic coding work, run it a level above its default, and keep a cheaper fast model
for iteration.

---

## Part 5 · When it comes back wrong

**Check the rule before you assume the slide is wrong.** More rules in this system have turned out
wrong than slides have. The uppercase cap outlawed the eyebrow. The one-headline rule outlawed the
two recipes that lead with a stat. The crop list was missing a crop the source uses. A rule required
a lockup on dividers when the source puts the bug there, and passed a wrong divider for three
revisions.

So when a validator finding disagrees with a slide you believe in, say so and ask it to check the
rule against the Figma source first. Then decide which one moves.

**A clean run is not always a clean deck.** If a gate could not run, it should say so as a failure
and not as a silence. That is enforced now, but ask anyway: *which checks actually ran?*

**"It looks fine" is not a verification.** Ask for the number. Contrast sampled from the rendered
backdrop, not inferred from the CSS. Photography share measured, not estimated. Line breaks
compared between the HTML and the PPTX.

**If a deck comes back thin, that is a defect.** An empty page is a defect in the same way an
overfull one is, and it is the more common one. A 91-slide deck once returned zero failures with 12%
of slides carrying a photograph, a median content coverage of 8%, "Lorem ipsum" on one slide and no
live text anywhere in the file. Say "this is too thin" and it will be taken as a real finding.

---

## The short version

Run the doctor. Open the teardown. Brief it like a designer, not a search engine. Ask for imagery
on purpose. Name the output format. Build on Opus 5.5 at `xhigh`. Never open the built file. Ask
for the measurement. And say whether your override is a one-off or a correction.
