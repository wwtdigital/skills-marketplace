# Ops

Skills for running projects and teams: status reporting, staffing, risk tracking, SOW and estimate support.

Install:

```
/plugin install ops@wwtdigital
```

## Skills

Each subfolder of `skills/` is one skill. See the [contribution guide](../../CONTRIBUTING.md) to add one.

| Skill | What it does |
| --- | --- |
| `wwtdigital-onboarding` | Answers new-hire onboarding questions from the live Notion onboarding wiki, with sources (from Staci Powell). Needs the Notion connector |
| `wwtdigital-mytime-nudge` | Turns MyTime timecard emails (pay period review, missed punch alerts, past idle time notices) into Slack nudges for the teammates who need to act, plus a summary of what needs your approval or a historical correction, on an hourly schedule or on demand. Draft. Needs Slack and Microsoft 365 |
| `wwtdigital-mytime-time-off-digest` | Collapses MyTime's time-off request emails into one self-DM each weekday: each new request once, cancellations, late submissions that need manual approval, and who else is out the same days. Never approves anything. Draft. Needs Slack and Microsoft 365 |
| `wwtdigital-time-codes` | Builds your own "My Time Codes" page from your private Slack channel topics and the Digital Time Entry page; answers "what do I bill this to?", maps a week of Slack activity to codes, and, when a code is unknown, drafts a question for the channel's lead or #d-time-entry without tagging ops. Draft. Needs Slack; Notion adds the standing codes |

## Owners

Listed in [`CODEOWNERS`](../../.github/CODEOWNERS). Owners review every change to this plugin.
