# Refresh (also used by Setup)

Slack has no "list all my channels" call. The refresh finds the person's channels two ways and then parses each channel's topic and purpose.

Connector facts that shape the steps:

- `slack_search_channels` needs at least one keyword. Keywords match the **name and purpose only**, not the topic, so searching "charge" or for a code number misses most channels.
- It returns 20 results per page. Follow `cursor` until "End of results". Use `response_format: "detailed"`, because `concise` leaves out Topic and Purpose.
- Private channels only appear if the person is a member, so a private sweep is already limited to them.
- Message search stops after about 8 pages (roughly 160 messages) but still says "End of results". That's why the activity sweep runs in weekly windows.

## Steps

**Cheaper model for steps 1–4.** These steps are most of the cost, and they're mechanical. If you can start a subagent and choose its model (in Claude Code, the Agent tool with `model: "haiku"`), hand steps 1–4 to one on Haiku:

- Give it the person's Slack ID (`<ME>`), their workspace domain, the full path to this file and to `extraction-rules.md`, and the activity-sweep start date.
- Tell it the job is read-only: search and read, never post, react or change anything.
- Have it return only JSON: `channels_scanned`, `rows` and `no_code_channels`, in the shapes in `data-schema.md`. No raw search results.

Then carry on from step 5 yourself. Spot-check three rows against their channels' live topics. If they don't match, or `channels_scanned` fails the check in "Verify before you report", run steps 1–4 yourself. If you can't choose a subagent's model, or the subagent can't reach Slack, just run every step yourself.

### 1. Activity sweep

This is the most reliable way to find the channels someone actually uses.

- Run `slack_search_public_and_private` with:
  - `channel_types: "private_channel"`
  - `only_my_channels: true`
  - `include_context: false`
  - `response_format: "concise"`
  - `limit: 20`
- Search **in weekly windows** going back about 90 days, using `filters: "from:<@<ME>> after:<day before week start> before:<day after week end>"`. Run the windows in parallel.
- Collect the distinct channel names.

### 2. Name sweeps

- Run `slack_search_channels` with `channel_types: "private_channel"`, `response_format: "detailed"` and `limit: 20` for each token below. Page to the end, in parallel.
  - Start with `d`, `digital`, `client`, `pursuit`, `aine`, `ai`, `wwt` and `team`.
  - Add distinctive prefixes and words from the activity-sweep channel names (a client short name like `acme`, a project nickname).
- Look up any activity-sweep channel that's still missing by searching for a word from its name.

### 3. Dedupe

Dedupe by channel ID. Drop any channel whose permalink isn't on the person's workspace domain.

### 4. Extract codes

Extract codes from each Topic and Purpose using `extraction-rules.md`.

### 5. Standing codes and notices

**Standing codes.** Fetch the Time Entry page with `notion-fetch` and rebuild `standing` from it. Keep the page's groups:
- Regional Sales P&L (task: Cost collect)
- GSE Indirect 01–06
- Solutions Strategy
- Administration: 1.1, 1.15, 1.2, 1.22, 1.7, 2.1 Holiday, 2.2 PTO, and the other 2.x leave types it lists

Also add `10035304` (general AI internal initiatives) and `10034890` (AINE initiative only), as long as #d-time-entry still says so.

**Notices.**
- Read the #d-time-entry pins first, with `filters: "in:<#C0321TBF0P5> has:pin"`.
- Then skim Brandi's messages, using `filters: "in:<#C0321TBF0P5> from:<@U68QGJ6S2> after:<date>"`. For `<date>`, use the last refresh, or 12 months ago on setup.
- Most of her messages are one-off replies in threads. Look for channel-wide guidance: "<!here>", "going forward", "please use X instead of Y", "for everyone".
- Turn each piece of guidance into a `notice`. Give it a short `flag`, plus `codes` and/or `channels`.

These three notices were current as of October 2026. Confirm them and carry them forward:

| Date | Rule | Flag | Applies to |
|---|---|---|---|
| 2026-09-04 | Retail sales team disbanded. Pursuit time that used to go to `10028191` now goes to the regional P&L. | "retail team disbanded, use regional P&L" | codes `["10028191"]` |
| 2026-02-11 | General AI work goes to `10035304`. `10034890` is only for the AINE initiative. | "AINE initiative only" | codes `["10034890"]` |
| 2026-09-21 | AINE bootcamp: facilitating goes to `10034890`, attending goes to Administration / 1.2 Training. | "bootcamp: facilitating only" | the bootcamp channel(s) |

**Conflicts.** When sources disagree, the newest dated source wins, and the conflict goes in the report. For example, the Notion page lists interviews as Admin 1.15, but a February 2026 thread says 1.23.

### 6. Open questions

Read the thread of each `open` question and apply any answers. See `ops-questions.md`, step 6.

### 7. Diff

Skip this step on setup.

Compare against the current data and report:
- new channels that have codes
- codes added or removed
- changed labels
- new notices
- answered questions

When a channel has gone missing, say whether it was archived or simply not found.

### 8. Build and republish

1. `read` the artifact, which saves the page locally. If the page was published in an earlier conversation, the Artifact tool may require you to read the whole saved file before it allows a republish. Read it through, then continue.
2. Run `python3 scripts/build_page.py extract <page.html> data.json` to get the current data, or follow `build-without-python.md` if Python isn't available.
3. Write the new data and run `python3 scripts/build_page.py build data.json my-time-codes.html` (or the fallback).
4. Publish with `url` set to the page's URL, so the link stays the same.

### 9. Report

In a few lines, give the counts, the diff, and anything ambiguous. Offer to ask the ops team about the ambiguous items in one message.
