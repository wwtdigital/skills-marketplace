---
name: "wwtdigital-onboarding"
description: "Answer WWTDigital new-hire and early-tenure onboarding questions — IT/equipment setup, tool access, benefits/payroll/time entry, PTO, expense reports, team structure, culture/ways-of-working, the 30/60/90-day plan, Digital-specific acronyms, team-specific reference by discipline, and learning & development — from the live Onboarding articles in Notion and their SharePoint sources. Use this whenever someone asks an onboarding-style question about WWTDigital (or \"WWT Digital\"), such as \"how do I get my laptop\", \"when's my first paycheck\", \"how do I submit an expense report\", \"what should I expect on day one\", \"what does SSA/DPM/NERF mean\", \"what does my team use for X\", or \"where do I find the onboarding checklist\" (even without saying \"onboarding\"). Also use to check what's covered before writing new onboarding content, or to audit articles for staleness. Not for a specific person's onboarding board, client-specific onboarding, or ops/pursuit terminology."
metadata:
  owner: staci.powell@wwt.com
  category: ops
  status: beta
  connectors: [notion]
  version: 1.0.0
---

## What this does

Answers new-hire and early-tenure questions about WWTDigital onboarding — IT/equipment setup, tool access, benefits/payroll/time entry, PTO, expense reports, team structure, culture/ways-of-working, the 30/60/90-day plan, Digital-specific acronyms/vocabulary, discipline/team-specific reference, and learning & development — by pulling live from the Digital Engagement Wiki's Onboarding articles in Notion, the separate Disciplines database for team-specific content, and the SharePoint pages those articles source from.

The content lives in Notion and SharePoint, not in this skill. Facts like phone numbers, deadlines, time codes, and team/org names can and do change (each article tracks its own Last Reviewed date), so always fetch live rather than relying on anything memorized from a previous run of this skill.

## How to answer a question

1. Search Notion for the question, scoped to onboarding content: use `notion-ai-search` (or `notion-search` if ai_search isn't available for this user) with `page_url` set to the wiki hub URL below, so results stay inside onboarding content rather than pulling in the rest of the Digital Engagement Wiki.
2. Fetch the matched article page(s) in full with `notion-fetch` — don't answer from search snippets alone.
3. If the question is purely a term/acronym lookup (e.g. "what does SSA mean", "what's a DPM", "what is a NERF"), check the Digital Terms & Acronyms glossary article first — it's built for exactly this and is faster than searching the narrative articles. For general company-wide terms not specific to Digital, point to WWT Terms on United instead (linked from the glossary) rather than guessing.
4. If the question is specific to a particular discipline/team rather than general onboarding (team-specific tools, processes, or resources), use the Discipline-specific reference section below instead of guessing from the general articles.
5. Check the article's `Status` property. If it's "Needs Update" or "Draft" rather than "Published", say so in your answer and suggest confirming with Staci Powell (BizOps) rather than presenting it as current.
6. Answer from the article's content first. If the question needs more detail than the Notion summary gives, open the SharePoint page in its "Source" callout too (Glean search with an `o365sharepoint` app filter, or fetch the URL directly) rather than guessing at what's on it.
7. Cite both the Notion article and the SharePoint source link you used (the glossary article and discipline pages are Notion-only — no SharePoint source to cite there).
8. Before replying, check that every fact in your answer (numbers, deadlines, contacts, codes) appears in a page you fetched in this conversation. Drop or flag anything that doesn't.
9. If nothing in the Onboarding category or Disciplines database answers the question, don't guess — say so plainly and point to the Global Service Desk / ServiceNow ticket portal for IT-flavored questions, or suggest asking Staci Powell or the person's manager. Never guess on pay, benefits, or policy specifics.

## Discipline-specific reference (ask which team, then fetch live)

Beyond the six general onboarding articles below, WWTDigital maintains a separate "Disciplines" database in Notion — one page per team, maintained directly by that discipline's own leads. Use this for anything team-specific that the general onboarding articles don't cover, so an answer always reflects whatever the discipline lead has published, not something hardcoded here.

- Disciplines database: https://app.notion.com/p/3acb0eeb3b2280b3bbaeebe946f225ca
- Known discipline pages (as of September 2026 — query the database directly rather than assuming this list is complete, since leads can add new ones): Digital Operations, Product, COE, CSD, DPMD, Design Studio, Tech
- Welcome & Team Overview also links out to this database directly, for anyone browsing Notion rather than asking this skill.

If the person's discipline/team isn't already clear from context, ask before answering — don't guess which page applies. Once you know the team, fetch that page live (never reuse cached content from a previous run) and answer from it. If a discipline doesn't have a page yet, or its page doesn't cover the question, say so plainly and fall back to the general onboarding articles or suggest asking Staci Powell / the person's manager.

## What this is NOT for

- A specific new hire's personal Trello onboarding board or checklist. That board is built per-hire by BizOps and the hiring manager — it's not general reference content, and this skill has no way to know what's on any one person's board. Say so rather than guessing.
- Anything outside the Onboarding category of the Articles database or the Disciplines database (e.g. Governance, Pipeline/Process, SSA Best Practices, client-specific onboarding checklists). This skill is scoped to general WWTDigital onboarding and discipline reference — for those other topics, search Notion normally without assuming this skill's structure applies.
- Ops/pursuit-specific jargon (deal-stage terms, pursuit financial definitions like T&M/FFP/CIF, etc.). The glossary and team-overview content here are deliberately scoped to general new-hire vocabulary, not operations-specific terminology.

## Known structure (starting points — verify current content by fetching; don't rely on this table alone, it will drift)

- Wiki hub: "🎓 Onboarding & Training" — https://app.notion.com/p/3a9b0eeb3b22810eaee5db73d27270f2
- Articles database (filter Category = Onboarding): https://app.notion.com/p/3a9b0eeb3b2281df9d77e07dceced717

| Article | Notion URL | Covers | SharePoint source |
|---|---|---|---|
| Welcome & Team Overview | https://app.notion.com/p/3a9b0eeb3b228144b1fbfce30864ae17 | SC&E's business units, where WWTDigital sits and who leads it, functional groups including Digital Intake and Center of Excellence and Digital Product Management & Alliances, THE PATH values, Digital's own Culture & Ways of Working (AI-First Mindset, Radical Transparency, Client-Obsessed, Cross-Functional Collaboration, Continuous Learning, Excellence in Execution), plus a link out to the Disciplines database for team-specific pages | wwt.sharepoint.com/sites/WWTDigitalOnboarding/SitePages/Who-Are-We-.aspx and .../Meet-the-team.aspx |
| Day 1 & First Week Checklist | https://app.notion.com/p/3a9b0eeb3b2281e7816ff544c6ae1977 | Day 1 tasks, an hour-by-hour "What to Expect on Day One" timeline, the benefits effective-date rule (first of month following start date), Global Service Desk numbers by region, ServiceNow ticket portal, requesting a monitor/keyboard/mouse via Amazon Business, expense reports (pointer to Time Entry article), first-week required trainings (WWT You, SC&E Overview, Wonder Week), and a Your First 30/60/90 Days plan | wwt.sharepoint.com/sites/WWTDigitalOnboarding/SitePages/New-employee-training.aspx |
| Tools & Systems | https://app.notion.com/p/3a9b0eeb3b228181bbb1db528adc8493 | What each tool is for (Slack, Trello, SharePoint, Notion, Teams, Lattice, Glean, ServiceNow, WWTYou, design resource sites), how to request access via ServiceNow, plus a "Getting Started — Orientation Videos & Guides" section with the MyTime tutorial video, a SharePoint how-to KB article, Digital's Slack Tips doc, and Notion Training | wwt.sharepoint.com/sites/WWTDigitalOnboarding/SitePages/YourFirstDay.aspx |
| Time Entry, PTO & Payroll | https://app.notion.com/p/3a9b0eeb3b2281c2b554cd8d033ed9bd | MyTime, Monday 9 AM timecard deadline, admin vs. billable time codes, onboarding-week codes, PTO request process, payday/pay-cycle info, MyTime troubleshooting tips (idle time, approval delegation, project-code wildcard search, carrying over prior-period activities), when a historical correction needs an ITTA ticket vs. a manager fix, corporate credit card ordering, expense report submission (WWT Expenses App, receipt deadlines, reimbursement windows), #d-time-entry / #d-work-status Slack channels, payroll contact | wwt.sharepoint.com/sites/WWTDigitalOnboarding/SitePages/TimeX.aspx |
| Continuous Learning & Professional Development | https://app.notion.com/p/3a9b0eeb3b2281d3a6bcfa15ffbf1ad3 | Udemy for Business, 90-day performance review, Management Foundations, the New Leader Program (for anyone newly promoted or hired into a people-manager role), SC&E Training, the IML framework, THE PATH Way new-hire event | wwt.sharepoint.com/sites/WWTDigitalOnboarding/SitePages/Professional-Development-Opportunities.aspx |
| Digital Terms & Acronyms | https://app.notion.com/p/3d5b0eeb3b22813b892bc9e45d6c79b7 | Digital-specific vocabulary and acronyms — team/role terms (SC&E, CSD, SSA, DPM, DPD, BizOps, Digital Intake and Center of Excellence, ESG), tools (MyTime, WWT You, Empower, ServiceNow, Glean, NERF, Vantage), time/money/codes (SFTC, WWTHC, GP, SOW, ITTA), and programs/events (THE PATH, THE PATH Way, IML, Wonder Week, QBR). Links out to WWT Terms on United for general, company-wide terms — the two are meant to be used together. Notion-original content; no SharePoint source. | — |

## Known gaps (confirmed as of September 2026 — check again, this list will go stale)

Dress code and remote-work policy are not covered in these six articles. There's no buddy/mentor program at the general Digital level — some individual teams informally pair new hires with a buddy, others don't, so don't assume one exists or point someone to it; if asked, say it varies by team and suggest checking with their manager. There's no orientation video for Notion itself yet (MyTime, SharePoint, and Slack have one each) — though Tools & Systems now links out to the Notion Training page for a 101 recording. The glossary's WWTHC entry flags its literal expansion as unconfirmed. Discipline pages vary in completeness since each is owned by that team's leads, not BizOps — don't assume a discipline page is exhaustive just because it exists. If asked about any of these, say so plainly, check whether the answer lives elsewhere in Notion or SharePoint before assuming it's missing entirely, and suggest to the user that this looks like a gap worth flagging to Staci Powell (for general onboarding content) or the discipline lead (for team-specific content).

## Escalation defaults

- IT/access issues: Global Service Desk (numbers are in the Day 1 & First Week Checklist article — fetch it for current numbers rather than reusing old ones) or the ServiceNow ticket portal.
- Hardware (monitor/keyboard/mouse): the Order Accessories request in ServiceNow, fulfilled via Amazon Business — see the Day 1 & First Week Checklist article for the current link and funding amounts. Don't say BizOps orders these directly; that changed.
- Payroll issues: the Payroll SharePoint site or Payroll@wwt.com (confirm current contact via the Time Entry, PTO & Payroll article).
- Time entry questions: the #d-time-entry Slack channel; ad-hoc time-off notices go in #d-work-status. Timecard historical corrections older than 6 weeks (or missing a PTO/leave code) need an IT Time & Attendance (ITTA) ticket rather than a manager fix — see the Time Entry, PTO & Payroll article for the current threshold.
- Expense reports: the WWT Expenses App for US employees (see Time Entry, PTO & Payroll for the process and deadlines) or the Travel & Expense SharePoint site; non-US employees use different country-specific tools/forms.
- Discipline/team-specific questions: the relevant discipline's page in the Disciplines database (see above), or that discipline's lead if the page doesn't cover it.
- New people managers: point to the New Leader Program (see Continuous Learning & Professional Development) rather than guessing at manager-specific onboarding.
- Anything else unmatched: Staci Powell (BizOps) or the person's manager — never guess on policy, pay, or benefits specifics.

## Maintenance

This skill is retrieval logic only — it has no onboarding content baked into it beyond the structural map above. To update an actual answer, edit the Notion article or discipline page (that's the system of record, tracked with its own Owner/Status/Last Reviewed fields for onboarding articles); don't patch facts into this file, since anything hardcoded here will silently drift out of sync with Notion.

