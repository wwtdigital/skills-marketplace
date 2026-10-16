---
name: wwtdigital-time-codes
description: >
  Builds and maintains each person's own directory of WWT time codes (project numbers, Sales P&L,
  GSE Indirect and Administration codes for Kronos/MyTime). Codes come from the topics of their
  private Slack channels and the Digital Time Entry page. Use when someone asks what code to bill or
  charge time to, needs codes for a timesheet week, names a client, pursuit or #channel and wants
  its code, asks where interviews, training, PTO, R&D, practice dev, AI initiative or sales support
  time goes, or says "set up my time codes" or "refresh my time codes". When a code is unknown or
  sources conflict, it drafts a question to the ops team in #d-time-entry. Not for entering or
  approving time in Kronos/MyTime, nudging teammates about timecards (wwtdigital-mytime-nudge), or
  expense reports.
metadata:
  owner: scott.cullum@wwt.com
  category: ops
  status: draft
  connectors: [slack, notion]
  version: 0.1.3
---

# Time Codes

WWT Digital posts each channel's charge codes in its Slack channel **topic**, and sometimes in its **purpose**. This skill gives each person a private, searchable "My Time Codes" page in their claude.ai artifacts. The page has click-to-copy codes for every channel they're in, plus the standing admin and indirect codes, and the skill uses it to answer "what do I bill this to?"

Every person has their own copy. Nothing is shared unless the owner shares the page.

## Before you start

| Need | Used for | If it isn't connected |
|---|---|---|
| **Slack** connector | channel topics, activity, #d-time-entry, ops questions | Stop and say: "This skill needs the Slack connector. Connect Slack in your connector settings, then ask again." |
| **Notion** connector | the Digital Time Entry page (standing codes) | Carry on without standing codes. Tell the person to connect Notion to get admin, indirect and regional sales codes. |
| **Artifacts** (claude.ai) | the person's "My Time Codes" page | Answer in chat and write the data to a JSON file instead. Say the page needs claude.ai with artifacts enabled. |

**Who is "you".** Call `slack_read_user_profile` with no `user_id` and `response_format: "detailed"` to get the signed-in user's name and ID; the concise format leaves out the ID. Use that ID wherever this file says `<ME>`. Never use another person's ID or open another person's page.

**Workspace.** Take the workspace from **channel** permalinks returned by `slack_search_channels`, usually `wwt.slack.com`. Message permalinks show `wwt.enterprise.slack.com` for the same workspace. Channels on any other domain are Slack Connect channels with clients or vendors, so skip them.

## Where the data lives

The data lives in a private Artifact titled **"My Time Codes"**. Its data is a JSON block in the page, inside `<script type="application/json" id="bill-codes-data">`. Find the page with `Artifact` (`action: "list"`, `scope: "mine"`), then `read` it. If there's none, run **Setup**.

`scripts/build_page.py` does the mechanical parts. Run it with `python3` (macOS has no `python` command). If Python isn't available, do the same steps yourself by following `references/build-without-python.md`, which also says how to check without setting off an installer:

- `extract <page.html> <data.json>` pulls the JSON out of a saved page, so you don't read 50KB of HTML.
- `build <data.json> <out.html>` puts the JSON into `references/page-template.html`, escapes it, and checks the result.

The full schema is in `references/data-schema.md`. In short:

- **`rows`**: one entry per code-and-task pair in a channel, typed `project`, `sales_pl` or `indirect`.
- **`standing`**: non-client codes from the Time Entry page.
- **`notices`**: team-wide rule changes that override channel topics.
- **`no_code_channels`**: channels that were scanned and had no code.
- **`open_questions`**: questions this person has asked the ops team.

## Team defaults (WWT Digital)

These are the same for everyone on the team:

- **Time Entry page (Notion):** https://app.notion.com/p/381b0eeb3b2280d3871bdf288052ae7e. This is the canonical list of regional Sales P&Ls, `10004590` GSE Indirect tasks, `10023126` Solutions Strategy, and Administration tasks.
- **#d-time-entry** (`C0321TBF0P5`): where people ask for codes. The time-entry admins (Brandi Gallagher-Taylor `U68QGJ6S2`, Staci Powell `U02M9FU5J3F`, Kenzie McAllister `U0B94600X1Q`) answer in threads. The ops group handle is `<!subteam^S0BECPY6SET>`.

If the person can't open the Notion page or the channel, they're probably on another team. Build the page from their own channels only and say that's what you did.

## Setup (first run)

1. Identify the person, then build the data by following `references/refresh.md`, steps 1–6.
2. Run `python3 scripts/build_page.py build data.json my-time-codes.html`, or the fallback in `references/build-without-python.md`. If it reports an error, fix the data and run it again. Don't hand-edit the template.
3. Publish the page with the Artifact tool, using `icon: "clock"` and a one-line description. It's private by default.
4. Report back: channels scanned, channels with codes, the notices that affect this person, and any conflicts found. Offer once to pin the page.

## Lookup ("what do I bill X to?")

1. Read the page and `extract` the data.
2. **Check `notices` first.** If a notice covers the code or the kind of work, apply it and say so. Notices are newer than channel topics.
3. **Non-client work** (interviews, training, all-hands, PTO, R&D, practice dev, partner meetings, general sales support, AI initiatives): answer from `standing` after applying any notice, and include the task (`10004590/06 Internal Initiatives`, `Administration/1.2 Training Education`). For general sales support, ask which region if it isn't obvious.
4. **Client work:** match on channel name, client name, label or code. Try short forms and hyphenated names (`acme`, `ac`, `acme-corp`). A client can have both a delivery channel and a pursuit channel, so pick the one that matches the work.
   - **Even when a topic has a code**, search #d-time-entry for the client or channel name over the last six months. If an admin gave a different code there, the admin's answer wins: give it and mention the topic code. Topics go stale and admins correct them in threads.
   - If the topic's only code carries an older year or phase label, or the person says it doesn't work in MyTime, say it may be stale and offer to check, instead of handing it over.
5. **Nothing found:** check in this order.
   - Search channels live, since the channel may be newer than the last refresh.
   - Search #d-time-entry for the client and read the thread for an admin's answer. Answers older than six months may be stale.
   - Still nothing: say so and offer to ask the ops team. Don't guess from a similar client.
6. **Answer briefly.** Give the code in backticks, the task if one is posted, the label and the source.
   - **Kronos format:** if the channel posts a full Kronos string (`kronos` on the row), give it verbatim. Otherwise use `code/task`, e.g. `100XXXXX/1001-Project Cost Collection`. If no task is posted, take it from another row or `standing` entry for the same code, and say where it came from. If there's no task anywhere, give the bare code and say the Kronos picker lists the valid tasks. **Never invent a task.**
   - **Picking the type:** project codes are for delivery work. Sales P&L codes are for pursuit, presales and new-biz work.
   - **Conflicts:** if sources disagree, use the newest one and mention the other. If the conflict changes which code to use and nothing settles it, offer to ask the ops team.
7. **When to check live:** if the data is more than 30 days old, a row looks off, or the person says a code is wrong, read the channel's topic and purpose live. Offer a full refresh, but don't run one to answer a single question.

## Codes for a timesheet week

1. Find what the person worked on with `slack_search_public_and_private`:
   - `filters: "from:<@<ME>> after:YYYY-MM-DD before:YYYY-MM-DD"`. **Both dates are exclusive**, so Mon Oct 5 – Fri Oct 9 is `after:2026-10-04 before:2026-10-10`.
   - `channel_types: "private_channel"`, `only_my_channels: true`, `include_context: false`, `response_format: "concise"`.

   Page through the results and count messages per channel.
2. Join those channels to `rows`:
   - A channel in `no_code_channels` has no code.
   - A channel in neither list was never scanned, so check it live.
   - A Slack Connect channel maps to its WWT twin channel if there's an obvious one.
3. Answer with two short tables, busiest channel first:
   - **Channels with codes:** the channel, message count, code(s), and what each code is. Apply `notices`. When a channel has both a project code and a Sales P&L code, pick one from what the messages were about and say why.
   - **Channels with no code:** suggest a `standing` code for clearly internal channels, labeled as a suggestion. Otherwise leave the call to the person.
4. If anything is unknown or conflicting, offer **one** combined question to the ops team.
5. Caveats: this covers private channels only, not DMs, public channels or meetings. Message count isn't hours. Flag non-billable-looking channels instead of dropping them.

## Asking the ops team

Follow `references/ops-questions.md`. In short:

1. Check that nobody has already asked the same question.
2. Draft one short, specific message tagging `<!subteam^S0BECPY6SET>`.
3. **Show the draft and get a yes before posting**, because the message goes out under the person's name. If they'd rather send it themselves, save it with `slack_send_message_draft`.
4. Post it in #d-time-entry and record it in `open_questions`.
5. Check the thread on the next lookup or refresh.

## Refresh

Follow `references/refresh.md` to:

- find the person's channels with activity search plus name sweeps (Slack has no "list my channels" call),
- extract codes using the rules in `references/extraction-rules.md`,
- rebuild the standing codes and notices,
- apply any answered ops questions,
- diff against the last version and republish to the same URL.

## Verify before you report

Before saying a setup or refresh is done:

- `build_page.py build` exits cleanly, or every check in the fallback passes. It checks that the JSON parses, the template has exactly one placeholder, and every row has a channel, code and type.
- The published page is the same URL as before (refresh) or a new private page (setup).
- `channels_scanned` is plausible. For someone on Digital, it's usually over 100. A very small number means paging stopped early, so rerun the sweep.
- Every notice that names a code shows its flag on at least one row, or the report says the code isn't in this person's channels.

Before answering a lookup, confirm the code came from a source you can name (a channel, the Time Entry page, or an admin's thread reply), and cite that source in the answer.

## Ground rules

- **Slack writes:** the only messages this skill sends are ops questions in #d-time-entry, and only after the person approves the wording. Never post anywhere else, react, edit or delete messages, or change channel topics.
- **Privacy:** each person's page is their own. Never read or write anyone else's.
- **Kronos/MyTime:** this skill never enters or approves time there. It only tells the person what to enter.
- **Old and new codes:** topics roll forward to new phases and years. When a channel lists an old code and a new one, keep both and give the newer one first.
