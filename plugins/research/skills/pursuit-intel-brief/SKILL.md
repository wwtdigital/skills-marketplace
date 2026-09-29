---
name: pursuit-intel-brief
description: Build a supplemental intelligence brief for a WWT Digital pursuit. Reads the pursuit's Slack channel and posted files, the Notion 9-box and Intelligence tab, the SharePoint client folder (RFP, appendix, working deck, Q&A doc), sizes the deal against comparable past Digital SOWs, checks every credential claim against wwt.com, and researches the client and their project from public sources. Produces a published brief page that contains only what is NEW relative to what the team already has, plus corrections to the team's own material and where to go deeper or lighter. Use this whenever someone asks to "look at the pursuit channel," "get up to speed on the [client] RFP," "do deep research on [client/project]," "what's new for the team," "size this proposal," "check our credentials," "cross-check the deck," or asks for a pursuit briefing, deal review prep, or Q&A prep for an RFP. Trigger even if they only name the client or channel. Not for writing the proposal itself, the SOW, or the estimate.
metadata:
  owner: scott.cullum@wwt.com
  category: research
  status: beta
  connectors: [slack, notion, microsoft-365]
  version: 1.1.0
---

# Pursuit Intel Brief

The team on a pursuit already has a 9-box, an Intelligence tab, a working deck and a Slack channel full of context. They do not need a summary of it. They need the things they don't have: facts from outside that change the approach, contradictions inside their own material, the real size of the deal against what WWT has actually sold, and whether the credentials they're about to put on a slide will survive a Google search by the client.

Everything in the brief passes one test: **would a team member learn something, or change something, from reading this line?** If not, cut it.

## Inputs

You need one of: a pursuit channel name, a client name, or a Notion opportunity link. Find the rest from there.

Before anything else, fetch the **internal reference page** in Notion: https://app.notion.com/p/3eab0eeb3b2281778130eb1dd9beb266. It holds what this public skill can't: the comparables table and run rates, the GP floor and deal-review triggers, channel IDs, SharePoint paths, prior pursuits worth pulling, and the wwt.com credential status. `references/sources.md` and `references/sizing.md` have the method and connector tips that don't change. If Notion isn't connected, say so, work from search, and note in the brief that the page wasn't read.

Tools this skill leans on: Slack (read channel, threads, search), Notion (fetch), Microsoft 365 (SharePoint folder + file reads), WebSearch / web_fetch, and subagents for parallel outside research. If a connector isn't connected, say which one and what it would have covered, then proceed with the rest. Never try to fetch SharePoint or Slack files through the browser with the user's credentials.

## Before you start

A full run takes 10–15 minutes and dozens of tool calls. Three habits keep it from going wrong:

- **Tell the user the run will take a while**, then send a one-line progress note at each phase boundary. Long silent runs read as stalled.
- **Checkpoint each phase to disk** in the scratchpad (`01-team-material.md`, `02-outside-research.md`, `03-sizing.md`, `04-credentials.md`). If the session is cut off, or a connector drops mid-run, resume from the last checkpoint instead of re-reading everything. Write the checkpoint as soon as the phase ends, not at the end of the run.
- **Surface a missing connector or permission once, then move on.** If SharePoint, Notion or Slack isn't attached or a file won't open, record it in the checkpoint and the Sources section. Don't retry the same dead end, and never work around it through a browser with the user's credentials.

Stay inside the ask. The brief informs the team; it doesn't edit their deck, their pursuit pages in Notion, or this skill's files, and it doesn't draft proposal content unless asked. The one exception is the internal reference page, where new comparables and corrected locations belong. If you find something that should change in a team document, say so in "Corrections" and let the owner make the edit.

## Workflow

Run phases 1–3 in parallel where you can. Phase 4 needs 1–3 done. Phase 5 is the write-up. Phase 6 is a verification pass before anything is published.

### 1. Read what the team already has

Read, in full, before forming any view:

- The pursuit channel, newest to oldest, plus every thread with replies. Note the timeline, who owns what, open asks, and any files posted.
- The Notion opportunity page: all tabs. The 9-box holds the team's thesis, buyer map, scope boundaries, red flags and pricing. The Intelligence tab (if present) holds research, a do-not-say list and open questions. The change log tells you what version the team is on.
- Any context file the team is loading into Claude (`*-project-context.md`). Note its date; these go stale fast and drift from Notion.
- The SharePoint client folder: the RFP itself, the client's appendix or strategy deck, the working response deck, the Q&A question bank, brainstorm and agenda docs, any audit or research docs.

Read the RFP and the client's appendix with particular care. Two things matter most: the **proposal guidelines** (required sections, page limit, format, submission method) because teams often work for weeks without them, and the **client's own words** for their goals, narratives and named vendors, because the proposal should quote them back.

Not every pursuit has all of this. Some are at RFI stage with no RFP yet, some have no Notion 9-box, some keep the strategy in SharePoint markdown files instead. Work with what exists, say what's missing, and adapt section 2 of the brief to whatever solicitation the client actually issued.

While reading, keep a running list of **internal contradictions**: numbers that differ between Notion and the deck, claims one document prohibits and another asserts, corrections that landed in one place and not another. These are the highest-value findings in the brief because nobody on the team is positioned to see them.

Check the team's **status claims** against the client's own documents too. "We won the RFI" or "we're shortlisted" is worth testing: an RFI may say it isn't a scored procurement, an interview window may have passed with no interview recorded, a decision date may have slipped. If the evidence doesn't support the claim, that's the first line of the brief.

### 2. Research the client and the project from outside

Spawn two subagents in parallel (they take 5–10 minutes each), each told to cite a URL for every fact and to flag anything uncertain or conflicting:

- **The project**: what's being built or bought, cost, funding, timeline, status, the design and build team, named technology partners and procurement signals, comparable projects and their vendor choices, risks and recent news (last 6 months).
- **The organization**: ownership, leadership with current titles (verify against the org's own roster page), the technology/IT leadership specifically, current vendors and partners, recent hires and departures, capital projects, controversies, and a stakeholder map for a technology pursuit.

The research is only useful where it goes beyond Notion. Give the subagents what the team already knows so they don't repeat it, and ask them to lead with incumbents, embedded partner staff, owner's-side delivery firms (project managers, owner's reps, builders), sponsors who already hold the lanes WWT wants (AI, security, connectivity), and vendor relationships the team hasn't named. Those are where the surprises live.

Ask each subagent to check its own output before reporting: every fact has a URL, titles are verified against the organization's own roster, and anything it couldn't confirm is labeled. Keep to two or three research agents at once; more tends to duplicate work and cut transcripts short.

### 3. Size the deal against what WWT has actually sold

Search the Digital SOW approval channel (and the relevant pursuit channels) for the closest comparable engagements. For each, capture fee, contract type, duration, GP%, team shape (roles and FTE), and what happened (won, cut, renegotiated). Start from the reference page's table, then search for anything newer or closer. `references/sizing.md` has what to capture, the run-rate method and the structuring patterns. Add any comparable that isn't on the reference page yet as a row there, with the post date, so the next run starts warmer. Nothing internal goes into this skill's own files: they're public.

Then compute a per-week run rate from the comparables and multiply by the working deck's timeline. Compare that to the Notion estimate and the deck's own numbers. Note the GP floor, the deal-review triggers, and any pattern of client pushback. This is the section the first deal review will actually use.

If there's no timeline yet (common at RFI stage), assume one, say so in the brief, and label the resulting range as an assumption. A labeled estimate is more useful to the team than no number.

### 4. Cross-check credentials against wwt.com

For every named case study, partner, or "we did X" claim in the working deck, search `site:wwt.com <client>` and fetch the page. Record what the public site says, in its own words, next to what the deck says. Three verdicts: **supported**, **overstated** (public site supports a weaker version), **not public** (nothing on the site; needs written clearance). The client's evaluators will do this search. Doing it first is cheap.

Check WWT's own boilerplate too: headcount, partner-of-the-year counts, rankings. Decks copy these from old versions, and they drift. The reference page has the figures as of its review date; recheck wwt.com if that's more than a quarter old, and update the page.

Also check the internal record: a context file or Notion note saying "we did not do that work" outranks a deck slide that says we did.

### 5. Write the brief

Publish it as a private Artifact page. If there's no Artifact tool, write the HTML file to the scratchpad and hand it over instead. Use `assets/brief-template.html` for the styling and section scaffold, and follow this structure:

1. **How to use this** — 4–6 bullets. What holds up in the team's intel, and the handful of things that should change how they work this week.
2. **What the RFP actually asks for** (or RFI, or brief — whatever the client issued) — proposal guidelines as a table, the client's own narrative list, what the appendix reveals that Notion doesn't capture (with a "So what" on each).
3. **How we've sized comparable work** — the comparables table and what it means for this number.
4. **What's new from outside research** — ranked items, each with `So what:` stating what it changes.
5. **Where to go deeper or lighter** — a table: topic, Deeper/Lighter, why.
6. **Corrections to our own material** — the internal contradictions, highest severity first. Say which document is wrong and what to change.
7. **Credentials checked against wwt.com** — claim, what the site says, verdict.
8. **Anything visual** — renderings, site plans, charts posted to the channel, read for what they imply. Mark inferences as yours.
9. **Q&A / meeting priorities** — the 4–5 questions to protect in the next client contact, tied to the new findings.
10. **Sources** — internal (what you read, what you couldn't) and external URLs.

Drop any section that has nothing new in it. Do not add a stadium/company overview section; the team has it.

### 6. Verify before publishing

Read the draft once as a skeptical reviewer would. The mistakes that slip through in this kind of brief are quiet ones: a number with no source, a verdict chip that contradicts its evidence, a "new" finding that's already in Notion, a landmine the brief itself steps on. Check:

- Every dollar figure, date and title traces to a source you read this run (or is labeled as an assumption).
- Every "new" item is absent from the team's material. If it's already there, cut it or move it to "Corrections" if the team has it wrong.
- Every correction names the document and says what to change.
- Nothing in the brief breaks the team's do-not-say list.
- Section numbers in cross-references match the final headings.

Fix what you find, then publish.

### 7. Tell the user what changed, briefly

Lead with the two or three findings that alter the approach. Name anything you got wrong earlier if a later source corrected you. List what you couldn't open. Don't paste the URL; the card carries it. Mention that the page is private until they share it.

## Writing rules

- **Every number gets a source.** If you can't source it, say so instead of rounding to something plausible.
- **Tier every claim**: client's own words / public source / our synthesis / inference. Mark inferences as yours ("my read," "I inferred"), especially on visuals.
- **Name the document that's wrong.** "Notion says X, the deck says Y, wwt.com says Z; use Z" is more useful than "there's a discrepancy."
- **Respect the landmines.** If the team keeps a do-not-say list, honor it in the brief and flag any team material that breaks it.
- **Own your corrections.** If a later source shows you were wrong earlier in the session, say "I was wrong earlier" in the brief and in the chat.
- **Short "So what" lines.** One or two sentences on what the finding changes: a slide, a question, a boundary, a price.
- **Keep the page a supplement.** The team's Notion is the record. The brief points at it, corrects it, and adds to it.

## Refreshing an existing brief

When asked to update a brief later in the pursuit, republish to the same URL. Re-read the channel since the last run, check whether the Notion version bumped, re-read the deck if it changed, and move anything the team has since fixed out of "Corrections." Keep "What's new" limited to what is new since the last version, and say the date range.

## References

- Internal reference page (Notion): https://app.notion.com/p/3eab0eeb3b2281778130eb1dd9beb266. Comparables, rules, locations, credential status. Team-editable.
- `references/sources.md` — connector quirks, file limits, wwt.com search patterns.
- `references/sizing.md` — what to capture per comparable, run-rate math, structuring patterns.
- `references/sports-venues.md` — checks specific to stadium, team and league pursuits (venue tech pattern, incumbents to look for, benchmark venues, landmine themes).
- `assets/brief-template.html` — the page scaffold and CSS.
