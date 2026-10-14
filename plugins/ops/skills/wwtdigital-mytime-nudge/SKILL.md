---
name: wwtdigital-mytime-nudge
description: >
  Turn WWT payroll's MyTime manager email ("Action Required – Complete Your MyTime Manager Pay
  Period Review") into Slack nudges: a DM from the manager to each teammate flagged for idle
  time, a missed punch or an unexcused absence, plus a summary to the manager of who was nudged
  and whose timecards are waiting on their own approval. Sets up an hourly Monday to Wednesday
  scheduled check, or runs once on demand. Use when a people manager says "set up MyTime nudges
  for my team", "nudge everyone flagged in today's MyTime email", "ping everyone in the pay
  period review email", "chase my team about their timecards" or "automate my MyTime
  reminders". Needs Slack and Microsoft 365 (Outlook). Not for filling in your own timesheet or
  reconstructing a Kronos or MyTime week, payroll or time-entry policy questions (use
  wwtdigital-onboarding), or approving timecards in MyTime itself.
metadata:
  owner: scott.cullum@wwt.com
  category: ops
  status: draft
  connectors: [slack, microsoft-365]
  version: 0.1.0
---

# WWTDigital MyTime Nudge

WWT payroll emails people managers "Action Required – Complete Your MyTime Manager Pay Period
Review" from `MyTime_Manager_Action@wwt.com`, usually Monday around 11am ET, Tuesday around
7:45am ET (before the Tuesday lockout) and Wednesday around 1pm ET. Its body is an HTML table
of flagged employees. This skill reads that email, DMs each flagged teammate in Slack (from the
manager) about the fixes that are theirs to make, and sends the manager a summary in their Slack
self-DM, including the timecards waiting on the manager's own approval.

Two modes:

- **Setup** ("set up MyTime nudges for my team"): ask a few questions, then create a scheduled
  task that checks for the email every hour.
- **Run** ("nudge everyone flagged in today's MyTime email", or a scheduled run): process any
  new email once.

## Before anything else: check the connectors

This skill needs **Slack** (to find and message people) and **Microsoft 365** (to read Outlook).
Look for their tools: Slack's `slack_search_users` and `slack_send_message`; Microsoft 365's
`outlook_email_search`. If either isn't connected, name the one that's missing and stop. Don't
guess at the email or at people. Tell the person:

- In the Claude app: open **Connectors** in settings, find Slack or Microsoft 365, choose
  **Connect** and sign in with their WWT account, then ask again.
- In Claude Code: run `/mcp` to see whether it's listed and signed in.
- If it isn't offered at all, the workspace admin controls which connectors are available.

Setup also needs the scheduled-task tools (`create_scheduled_task`, or `create_trigger` where
that is its name). If they aren't available, say scheduled nudges only work in the Claude
desktop app or Cowork, offer a one-off run instead, and stop.

## Mode A: Setup

1. **Ask the manager** (use AskUserQuestion when it's available, all three in one call):
   - **Send mode**: send DMs directly (default) / create Slack drafts for me to review and send
     / summary to me only (message nobody else).
   - **Which flags count** (multi-select): idle time, missed punches, unexcused absence (all on
     by default); hours warning (off by default).
   - **Polling window**: hourly, Monday to Wednesday, 7am to 5pm in their time zone (default),
     or a window they name.
2. **Look up the manager.** Their email from Microsoft 365 (`get_me`) or their Slack profile
   (`slack_read_user_profile` with no user, which returns their own). Their time zone from the
   Slack profile (`tz`, an IANA name like `America/Chicago`); if it's missing, ask. Note their
   own Slack user ID too; it's where the self-DM summaries go.
3. **Build the run prompt.** Read [references/run-prompt.md](references/run-prompt.md) and fill
   every `{{PLACEHOLDER}}`:
   - `{{MANAGER_NAME}}`, `{{MANAGER_EMAIL}}`, `{{MANAGER_SLACK_ID}}`, `{{TIMEZONE}}`
   - `{{SEND_MODE}}`: `send`, `draft` or `summary-only`
   - `{{FLAGS}}`: the chosen flags, comma-separated, from `idle-time`, `missed-punches`,
     `unexcused-absence`, `hours-warning`
   - `{{CUTOFF}}`: the current time as ISO 8601 with offset, e.g. `2026-10-14T09:12:00-05:00`
   The filled prompt must stand on its own. Scheduled runs may not load this plugin, so never
   shorten it to "use this skill".
4. **Create the scheduled task** with the scheduled-task tool: name it
   `wwtdigital-mytime-nudge`, give it the filled prompt, and use cron
   `CRON_TZ=<their tz> 0 7-17 * * 1-3` (adjust the hours or days if they chose another window).
5. **Verify.** List the scheduled tasks and confirm the new one is there with the right cron
   expression, and that its prompt has no `{{` left in it and contains the manager's email and
   the cutoff. If anything is wrong, fix it with the update tool before reporting.
6. **Tell the manager**, in plain words:
   - Automatic approval is turned off for the org, so they'll be asked to approve each run that
     sends messages. Runs that find no email finish on their own and don't need them.
   - Anything already in their inbox before now (including this week's email, if it has
     arrived) won't be processed. If they want it handled, they can say "nudge everyone
     flagged in today's MyTime email" once.
   - How to stop it: delete the `wwtdigital-mytime-nudge` scheduled task.

## Mode B: Run

For a one-off run in conversation, read [references/run-prompt.md](references/run-prompt.md)
and follow it as written, with these values instead of the placeholders:

- Manager: the person you're talking to (look them up as in Setup step 2).
- Send mode: `send`, flags: `idle-time, missed-punches, unexcused-absence`, unless they say
  otherwise.
- Cutoff: none. The 36-hour window and the duplicate checks still apply.
- Because they're here: after parsing, show them the planned DMs (who, and for what) and the
  approval list, and send only after they say yes. A scheduled run skips this question; its
  per-run approval is the confirmation.

The run prompt covers the whole workflow: find the email, skip ones already done, parse the
table, decide whose action each flag is, match people in Slack, send the DMs, post the summary,
tag the email, and verify. The rules that matter most:

- "Needs Approval" is the **manager's** action. Never message an employee about it.
- Match people in Slack by exact name and confirm with their `@wwt.com` email. Never guess;
  anyone without exactly one confirmed match is listed as "couldn't find in Slack".
- The summary's first line is exactly `MyTime nudges sent (data extraction <timestamp>)`. It's
  the duplicate key the next run checks.

## Testing

[references/sample-email.html](references/sample-email.html) is an anonymized sample with fake
names and IDs, and the expected result is in a comment at its end. To dry-run the parser, read
it in place of the Outlook email with send mode `summary-only` and show the summary in chat
instead of posting it. Never send test DMs to real people.

## Guardrails

- Message only people listed in the email, and only about their own row. Never mention other
  people, employee IDs, hours totals or anything else from the table.
- Never reply to or forward the payroll email, never post in channels, never approve or edit
  anything in MyTime, and take no actions beyond the ones in the run prompt.
- No em dashes in any message.

## Examples

**User says:** "Set up MyTime nudges for my team."
**Claude does:** checks Slack, Microsoft 365 and the scheduled-task tools, asks the three
questions, looks up the manager's email and `America/Chicago` time zone, fills the run prompt
with a cutoff of now, creates `wwtdigital-mytime-nudge` on `CRON_TZ=America/Chicago 0 7-17 * * 1-3`,
confirms it's listed, and explains approvals and that this week's email won't be processed.

**User says:** "Ping everyone flagged in today's MyTime pay period review email."
**Claude does:** finds this morning's email, sees no `MyTime-Nudged` category and no matching
summary, parses three rows, plans one idle-time DM and one unexcused-absence DM, holds the
"Needs Approval" row for the manager, skips the hours-warning row, asks to send, sends, posts the
summary to the manager's self-DM and tags the email.
