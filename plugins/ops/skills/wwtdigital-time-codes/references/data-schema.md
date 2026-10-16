# Data schema

The page stores its data as JSON inside `<script type="application/json" id="bill-codes-data">`. `scripts/build_page.py` reads and writes it (`build-without-python.md` covers doing that without Python).

```json
{
  "owner": "Jane Doe", "slack_user_id": "U0XXXXXXX", "workspace": "wwt.slack.com",
  "generated": "2026-10-15", "channels_scanned": 233,
  "sources": { "time_entry_channel": "C0321TBF0P5",
               "time_entry_page": "https://app.notion.com/p/381b0eeb3b2280d3871bdf288052ae7e" },
  "notices": [ { "date": "2026-09-04", "text": "…", "source": "<permalink>", "flag": "retail team disbanded, use regional P&L",
                 "codes": ["10028191"], "channels": [] } ],
  "standing": [ { "group": "GSE Indirect – Corp Strategy", "code": "10004590", "task": "06",
                  "label": "Internal Initiatives", "use_for": "Non-client initiatives, coaching, mentoring, all hands" } ],
  "references": [ { "label": "Time Entry page (Notion)", "url": "…" } ],
  "no_code_channels": [ "d-tech-managers" ],
  "open_questions": [ { "date": "2026-10-15", "topic": "Acme pursuit", "question": "…",
                        "permalink": "<message link>", "status": "open" } ],
  "rows": [ { "channel": "d-client-acme", "channel_id": "G0XXXXXXXXX", "code": "100XXXXX",
              "code_type": "project", "task": "", "label": "Acme Omni-channel Rebuild", "found_in": "topic" } ]
}
```

## Fields

**`rows`**
- One entry per code-and-task pair. A channel that lists `10004590` with tasks 01, 02 and 03 gets three rows.
- `code_type` is one of `project`, `sales_pl` or `indirect`.
- `found_in` is one of `topic`, `purpose`, `topic+purpose`, or `#d-time-entry` (for an ops answer).
- `code` can be text, such as `Administration`. The page shows a copy button only for numeric codes.
- `kronos` is optional. It holds the exact Kronos string when the topic posts one.

**`no_code_channels`**
- Channels that were scanned and had no code.
- A channel in neither `rows` nor this list was never scanned.
- If this list is much shorter than `channels_scanned` minus the channels with codes, it was only partly filled. Treat a missing channel as unknown and check it live.

**`notices`**
- Team-wide rule changes that override channel topics.
- `flag` is a short label that the page shows on matching rows.
- A notice matches rows through `codes` (every row with that code) or `channels` (only those channels). Use `channels` when the rule changes one channel's code but not the code everywhere.
- A `channels` entry can be a pattern with `*`, like `aine-*bootcamp*`, so the notice also covers channels created after it. Use a pattern whenever the rule is about a kind of channel, not one channel.
- `codes` and `channels` can both be empty for a rule about a kind of work (training, events, interviews). Lookup still applies it; the page just shows no row flag.

**`open_questions`**
- Questions this person has posted to the ops team.
- `status` is `open` or `answered`.
- The page lists the open ones with a link to the thread.
