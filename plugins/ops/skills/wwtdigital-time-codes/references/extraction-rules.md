# Extraction rules

Read each channel's Topic and Purpose the way someone filling in a timesheet would. These rules cover the conventions WWT Digital channels use.

## Code types

**Project**
- 8 digits starting `100`, next to a project name: `100XXXXX - Acme Omni-channel Rebuild`.

**Sales P&L**, in either of two forms:
- An 8-digit `100…` code labeled `WWTHC`, `GES`, `SLED`, `MSO`, `CSP`, `Commercial`, `Sales`, `Presales`/`Pre-sales`, or `- PL`.
- A 5–6 digit code next to those same words: `110691 GES Big Rivers`, `96624 GES House`, `128059 GES Gateway`.

**Indirect**
- `10004590 GSE Indirect`, always with a task 01–06.
- `10035304` and `10034890` (internal AI initiatives).
- `10023126` Solutions Strategy.
- `35933 Internship`.
- Text codes like `Administration - WWTHC/1.2-Training Education`. Store these as `code: "Administration"`, with the task, as type `indirect`.

## Common Sales P&Ls

Use this table to label a bare code. Don't treat it as complete.

| Code | Name |
|---|---|
| 10000009 | Federal House |
| 10000028 | SLED Midwest |
| 10000031 | SLED House |
| 10000090 | Commercial East |
| 10000095 | Comm Central House |
| 10000098 | Commercial West |
| 10000099 | MSO Media + Gaming |
| 10000191 | GES North Texas/OK |
| 10011269 | GES TOLA House |
| 10011272 | GES SoCal Utilities |
| 10028184 | SLED NYC |
| 10028185 | SLED Florida |
| 10028189 | GES Healthcare |
| 10028191 | GES Retail & Hospitality (retail team disbanded Sept 2026; see notices) |
| 10028192 | GES Energy & Utilities |
| 10028195 | GES Domestic Financials |
| 10028199 | GES Insurance |
| 10034671 | GES Oklahoma |

## Tasks and labels

**Full Kronos strings**
- Some topics post the exact Kronos entry, like `100XXXXX-ACME CC CMS 100XXXXX |$DS/1001-Project Cost Collection`. Store it verbatim in the row's optional `kronos` field, so lookups can hand it over as-is.

**Tasks**
- A task follows its code after `/`, `Task:` or `Task NN`, as in `1001 Project Cost Collection`. Store it in `task` exactly as written.
- A task name with no number, like "(Project Cost Collection)", is also stored as written.
- A task never gets its own row, but the same code with different tasks gets one row per task.

**Labels**
- Use the words next to the code, kept short.
- If a bare code is in the table above, use the table's name.
- Otherwise use `(unlabeled)`.

## Skip

- Anything that only looks like a code: phone numbers, Slack or Notion IDs, URLs, passwords, dates, email aliases.
- Channels on another workspace domain (Slack Connect).
- Channels with no code. Put them in `no_code_channels` instead of making rows.

## Old and new codes

Topics roll forward to new phases and years (for example, `10034836 NEW 2026 Feature Dev` alongside `10028356 Loyalty Implementation 2025`). Keep both rows, and give the newer one first when answering.
