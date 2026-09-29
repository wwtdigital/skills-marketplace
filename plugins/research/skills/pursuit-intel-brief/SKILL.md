---
name: pursuit-intel-brief
description: "Build a supplemental intelligence brief for a WWT Digital pursuit at any stage: RFP, RFI, or no solicitation yet. Reads the pursuit's Slack channel, Notion space and SharePoint folder (RFP or RFI, working deck, Q&A doc), sizes the deal against comparable past Digital SOWs, checks every claim in our material against wwt.com and the internal record, and researches the client from public sources. Produces a published brief with only what is NEW, the positioning angles the findings support, corrections to the team's own material, and the claims that will blow up if the client checks them. Use whenever someone asks to \"look at the pursuit channel,\" \"get up to speed on [client],\" \"do deep research on [client/project],\" \"what's new for the team,\" \"size this proposal,\" \"check our credentials,\" \"cross-check the deck,\" \"what's our angle,\" or asks for a pursuit briefing, deal review prep, or Q&A prep. Trigger even if they only name the client or channel. Not for writing the proposal itself, the SOW, or the estimate."
metadata:
  owner: scott.cullum@wwt.com
  category: research
  status: beta
  connectors: [slack, notion, microsoft-365]
  version: 1.2.0
---

# Pursuit Intel Brief

The team on a pursuit already has a Notion space, a working deck and a Slack channel full of context. They do not need a summary of it. They need the things they don't have: facts from outside that change the approach, the positioning angles those facts open up, contradictions inside their own material, the real size of the deal against what WWT has actually sold, and whether the claims they're about to put on a slide will survive a Google search by the client. The brief is an accelerator for research and positioning, and a check that nothing in our material blows up on contact.

Everything in the brief passes one test: **would a team member learn something, or change something, from reading this line?** If not, cut it.

## Inputs

You need one of: a pursuit channel name, a client name, or a Notion opportunity link. Find the rest from there.

Before anything else, fetch the **internal reference page** in Notion: https://app.notion.com/p/3eab0eeb3b2281778130eb1dd9beb266. It holds what this public skill can't: the comparables table and run rates, the GP floor and deal-review triggers, channel IDs, SharePoint paths, prior pursuits worth pulling, and the wwt.com credential status. `references/sources.md` and `references/sizing.md` have the method and connector tips that don't change. If Notion isn't connected, say so, work from search, and note in the brief that the page wasn't read.

Tools this skill leans on: Slack (read channel, threads, search), Notion (fetch), Microsoft 365 (SharePoint folder + file reads), WebSearch / web_fetch, and subagents for parallel outside research. Everything runs on the user's own connectors and credentials.

**Check the connectors before reading anything.** Make one cheap call on each (search Slack channels for the client name, `notion-search` for it, `sharepoint_folder_search` for it). If a connector isn't connected, or a call fails with an authorization error, or comes back empty in a way that looks like an expired session, stop and ask the user to connect it or sign in again (claude.ai connector settings, or `/mcp` in Claude Code), then retry. Do not quietly proceed without it: say what it would have covered and ask whether to continue without it. Only go on with reduced scope if the user says so. Never try to reach SharePoint or Slack through the browser with the user's credentials.

## Before you start

A full run takes 10–15 minutes and dozens of tool calls. Three habits keep it from going wrong:

- **Tell the user the run will take a while**, then send a one-line progress note at each phase boundary. Long silent runs read as stalled.
- **Checkpoint each phase to disk** in the scratchpad (`01-team-material.md`, `02-outside-research.md`, `03-sizing.md`, `04-credentials.md`). If the session is cut off, or a connector drops mid-run, resume from the last checkpoint instead of re-reading everything. Write the checkpoint as soon as the phase ends, not at the end of the run.
- **Surface a missing connector or permission once, then move on.** If SharePoint, Notion or Slack isn't attached or a file won't open, record it in the checkpoint and the Sources section. Don't retry the same dead end, and never work around it through a browser with the user's credentials.

Stay inside the ask. The brief informs the team; it doesn't edit their deck, their pursuit pages in Notion, or this skill's files, and it doesn't draft proposal content unless asked. The one exception is the internal reference page, where new comparables and corrected locations belong.

**Work at whatever stage the pursuit is in.** RFP: read the RFP and any appendix closely; the proposal guidelines and the client's own words matter most. RFI: read the RFI; note whether it says it is scored (most say it isn't) and test any "we're shortlisted" claims against it. No solicitation yet: the brief becomes a research and positioning accelerator: what the client is likely buying, who is already inside the account, what angle WWT would take, what would trigger a formal ask, and what to do this week. Section 2 of the brief adapts to whichever of the three you find. If you find something that should change in a team document, say so in "Corrections" and let the owner make the edit.

## Workflow

Run phases 1–3 in parallel where you can. Phase 4 needs 1–3 done. Phase 5 is the write-up. Phase 6 is a verification pass before anything is published.

### 1. Read what the team already has

Read, in full, before forming any view:

- The pursuit channel, newest to oldest, plus every thread with replies. Note the timeline, who owns what, open asks, and any files posted.
- The pursuit's Notion space: every tab and child page. Teams organize these differently; look for the thesis, buyer map, scope boundaries, red flags, pricing, research, any do-not-say list and any open-questions list. A version or change log tells you what the team is on. Some pursuits have no Notion page yet; say so and move on.
- Any context file the team is loading into Claude (`*-project-context.md`). Note its date; these go stale fast and drift from Notion.
- The SharePoint client folder: the RFP itself, the client's appendix or strategy deck, the working response deck, the Q&A question bank, brainstorm and agenda docs, any audit or research docs.

Read the RFP and the client's appendix with particular care. Two things matter most: the **proposal guidelines** (required sections, page limit, format, submission method) because teams often work for weeks without them, and the **client's own words** for their goals, narratives and named vendors, because the proposal should quote them back.

Not every pursuit has all of this. Some are at RFI stage, some have nothing from the client yet, some have no Notion page, some keep the strategy in SharePoint files. Work with what exists, say what's missing, and adapt section 2 of the brief to whatever the client actually issued, if anything.

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

### 4. Hunt the slop grenades: check every claim against wwt.com and the internal record

A slop grenade is a claim in our own material that detonates when the client checks it: an overstated credential, a number with no source, a stale fact, a name we aren't cleared to use, a benchmark that circulates internally and isn't true. Finding them before the client does is the highest-value thing this skill does after outside research.

For every named case study, partner, or "we did X" claim in the working deck, search `site:wwt.com <client>` and fetch the page. Record what the public site says, in its own words, next to what the deck says. Three verdicts: **supported**, **overstated** (public site supports a weaker version), **not public** (nothing on the site; needs written clearance). The client's evaluators will do this search. Doing it first is cheap.

Check WWT's own boilerplate too: headcount, partner-of-the-year counts, rankings. Decks copy these from old versions, and they drift. The reference page has the figures as of its review date; recheck wwt.com if that's more than a quarter old, and update the page.

Also check the internal record: a context file or Notion note saying "we did not do that work" outranks a deck slide that says we did. Then sweep the rest of the team's material for unsourced numbers, dates that have moved, and anything on the team's own do-not-say list that has crept back into a slide.

### 5. Write the brief

Publish it as a private Artifact page. If there's no Artifact tool, write the HTML file to the scratchpad and hand it over instead. Use `assets/brief-template.html` for the styling and section scaffold, and follow this structure:

1. **How to use this** — 4–6 bullets. What holds up in the team's intel, the two or three angles worth taking, and the handful of things that should change how they work this week.
2. **What the client actually asked for** — RFP: proposal guidelines as a table, the client's own narrative list, what the appendix reveals that the Notion space doesn't capture (with a "So what" on each). RFI: the same, plus whether it is scored and what the next step really is. Nothing yet: what we think they will buy and why, from the outside evidence.
3. **How we've sized comparable work** — the comparables table and what it means for this number.
4. **What's new from outside research** — ranked items, each with `So what:` stating what it changes.
5. **Positioning angles** — three to five angles the new findings support that the team's win themes don't already cover. For each: the evidence, what it lets us say to the client, and what we'd have to be able to deliver for it to hold. This is where the brief earns its keep as an accelerator; don't repeat the team's existing themes back to them.
6. **Where to go deeper or lighter** — a table: topic, Deeper/Lighter, why.
7. **Corrections to our own material** — the internal contradictions, highest severity first. Say which document is wrong and what to change.
8. **Slop grenades: what blows up on contact** — claim, where it appears, what the source actually says, verdict (supported / overstated / not public / unsourced / stale), and the one-line fix.
9. **Anything visual** — renderings, site plans, charts posted to the channel, read for what they imply. Mark inferences as yours.
10. **Q&A / meeting priorities** — the 4–5 questions to protect in the next client contact, tied to the new findings. If there is no client contact scheduled, make this "what to do this week."
11. **Sources** — internal (what you read, what you couldn't) and external URLs.

Drop any section that has nothing new in it. Do not add a stadium/company overview section; the team has it.

### 6. Verify before publishing

Read the draft once as a skeptical reviewer would. The mistakes that slip through in this kind of brief are quiet ones: a number with no source, a verdict chip that contradicts its evidence, a "new" finding that's already in Notion, a landmine the brief itself steps on. Check:

- Every dollar figure, date and title traces to a source you read this run (or is labeled as an assumption).
- Every "new" item is absent from the team's material. If it's already there, cut it or move it to "Corrections" if the team has it wrong.
- Every positioning angle rests on a finding in the brief, not on a hunch, and says what we'd have to deliver.
- The brief carries no slop grenades of its own: no number without a source, no name without a URL or an internal record, no benchmark repeated from memory.
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

When asked to update a brief later in the pursuit, republish to the same URL. Re-read the channel since the last run, check whether the Notion space changed, re-read the deck if it changed, and move anything the team has since fixed out of "Corrections." Keep "What's new" limited to what is new since the last version, and say the date range.

## References

- Internal reference page (Notion): https://app.notion.com/p/3eab0eeb3b2281778130eb1dd9beb266. Comparables, rules, locations, credential status. Team-editable.
- `references/sources.md` — connector quirks, file limits, wwt.com search patterns.
- `references/sizing.md` — what to capture per comparable, run-rate math, structuring patterns.
- `references/sports-venues.md` — checks specific to stadium, team and league pursuits (venue tech pattern, incumbents to look for, benchmark venues, landmine themes).
- `assets/brief-template.html` — the page scaffold and CSS.
