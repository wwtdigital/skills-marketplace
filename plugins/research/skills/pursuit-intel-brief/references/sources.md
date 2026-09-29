# Where pursuit material lives

Channel IDs, SharePoint paths, prior pursuits worth pulling, the wwt.com public/not-public list
and the current boilerplate figures are on the internal reference page in Notion (linked from
SKILL.md). This file has the connector tips that don't change. If Notion isn't connected, find
each location by search and ask the user for anything a search doesn't turn up.

## Slack

- The pursuit channel: `slack_search_channels` with the client name, including private channels.
- The Digital SOW approval channel is the best source for sizing. Posts follow a template: Scope,
  Docs, Estimate Recap (Total | GP | Timing | Staffing), Key Takeaways, Reviews/Approvals. Search
  it by client or offering keyword with `in:<#channel>`.
- The deal review channel holds the current approval rules and recaps; the general channel has
  win/loss posts.
- `slack_read_channel` returns newest first and truncates long channels to a file; read the whole file.
- Read every thread that has replies. Staffing thoughts, links and corrections hide in threads.
- The Slack connector returns file *titles* only. To read a posted file, find the same file on
  SharePoint or ask the user to upload it.
- Pursuit-channel topics often carry a pre-sales billing code. It's expected, not an error, and it
  never goes in the brief.

## Notion

- Each pursuit is one tabbed opportunity page in the Digital pipeline database (the reference page
  says where). Find it with `notion-search` on the client name. Tabs usually include Links to
  Tools, 9-Box, Pursuit, Project Dashboard, and sometimes Intelligence and Relevant Links.
- Page properties carry confidence, estimated revenue, pursuit status, close date and pipeline ID.
  Compare these to the CRM and the deck; they drift.
- The 9-box has a version and a change log at the top. The Intelligence tab may have a
  "Corrections" note with its own version. Anything dated before those corrections is suspect.
- `notion-fetch` on a big page saves to a file; extract the text and read it in chunks. Don't skip tabs.
- Child pages (context dumps, benchmark dossiers, handoff notes) sit at the bottom of the page.
  Fetch them.

## SharePoint (Microsoft 365 connector)

- Find the client folder with `sharepoint_folder_search` on the client name, then `read_resource`
  on the folder URI to list contents. The reference page has the folder layout.
- Typical contents: the RFP PDF, the client's appendix or strategy deck, a WIP deck folder, a Q&A
  doc, brainstorm docs, internal agendas, audit docs, prior-pursuit decks copied in for reference.
- `read_resource` on a PDF or pptx returns extracted text; for long decks use `startPage`/`endPage`.
- Adjacent pursuits for the same client may have their own site or folder. Search the client name
  and look past the first result.

## CRM

Opportunity links appear in the pursuit request post. Note stage, %, close date and owner; compare
with Notion.

## wwt.com credential checks

- `WebSearch` with `site:wwt.com <client or program name>`, then fetch the page. Sponsorship pages
  live at `/corporate/sponsorships/<name>`; case studies at `/case-study/<slug>`; news at `/news/<slug>`.
- Start from the reference page's public/not-public list, then re-verify anything the deck leans
  on. Don't assume a reference is public because a deck uses it.
- Internal referenceability outranks the deck: if a context file or Notion note records that
  someone confirmed "WWT did not do that work," treat it as binding until the account team clears
  otherwise.
- Boilerplate (partner-of-the-year count, headcount, rankings): the reference page has the figures
  as of its review date. If that date is more than a quarter old, recheck the latest wwt.com press
  release and update the page.

## Known file limits (front-load these)

- **Office files over ~100MB won't open** through `read_resource`. Submitted decks are often
  150–300MB. Look for the PDF export first, then a draft or copy pptx in the same folder, which is
  usually smaller.
- **PDF text extraction sometimes fails** on design-heavy exports. Fall back to the source pptx or
  the draft, and note in Sources which version you read.
- **Images over ~5MB won't load.** Renderings folders are usually over. Ask the user to upload one
  or two if the visuals matter.
- **Large Notion pages and long Slack channels save to a file.** Read the whole file in chunks.
- **Folders referenced inside strategy docs** often live in someone's OneDrive, not the client
  folder. Try `sharepoint_search` on the folder name before giving up.

## Connector gaps

- Slack files: titles only. Ask for uploads.
- Browser tools can't sign in to SharePoint or Slack for the user, and must not enter credentials.
  Use the Microsoft 365 connector; if it isn't connected, say so and ask the user to connect it.
- Meeting notes and Teams transcripts sometimes exist as Notion child pages or `.docx` in
  SharePoint; they're the best record of what leadership actually said.
