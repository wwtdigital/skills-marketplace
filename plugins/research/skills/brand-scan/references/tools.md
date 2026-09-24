# brandscanner tools

Notes on the `brandscanner` MCP server as bundled in `plugins/research/.mcp.json`. In an
installed plugin the tools register under `plugin:research:brandscanner`. Names below are the
tool names without any client prefix. Everything here was read from the tool schemas and a
read-only look at the data on 2026-09-24; timings are estimates.

## Read-only (safe to call any time)

| Tool | Input | Returns |
| --- | --- | --- |
| `list_brands` | none | every scanned brand: `slug`, `brand_name`, core/research/overall scores, `last_scanned`, `scan_count`; a `rankings` list with percentiles; `rubric_hashes` and a `rubric_mix_warning` when brands were scored under different rubric versions |
| `get_scorecard` | `brand_name` | `status: found` or not; the full `scorecard` (shape below), `version`, `history[]` of scan ids and scores, `deltas` vs the previous scan, `benchmarks[]` per category |
| `brand_benchmarks` | `brand_name` | `category_percentiles[]`, `subtheme_percentiles[]` (with `quartile`), `deltas`, `cohort_rank`, `cohort_size`, rubric warning |
| `cohort_summary` | none | mean/median/std/min/max for core, research and overall across the cohort |
| `scan_status` | optional `brand_name` | per brand: `last_scan_started`, `last_scan_finished`, `status` (`success`, `failed`, `running`, `timeout`), `tools_succeeded[]`, `tools_failed[]`, `scan_id` |

The cohort is described by the server as quick-service restaurants. A brand from another
sector still gets percentiles against it; say so when presenting.

## Run lifecycle (writes records)

| Tool | Input | Notes |
| --- | --- | --- |
| `resolve_brand` | `brand_name` | website URL, iOS/Android app IDs, ticker, social handles, subreddits, competitors. Calls external lookups. |
| `start_scan_run` | `brand_name` | returns `run_id`; makes the run visible in `scan_status` |
| `finish_scan_run` | `run_id`, `status` (`ok`/`failed`), optional `scan_id`, `tools_succeeded[]`, `tools_failed[]`, `error_details {stage, message}` | always call it, even after a failure |
| `close_stale_scan_runs` | `max_age_minutes` (default 60) | marks orphaned `running` rows as `timeout`; for runs that crashed before `finish_scan_run` |
| `save_scorecard` | `scorecard_json` (string), `merge` (default true) | creates a timestamped snapshot; returns the `scan_id`; `persist_failed` means the DB write failed and a checkpoint was kept |
| `resume_scorecard_save` | `brand_slug` | replays a `persist_failed` checkpoint; `no_checkpoint` if none |
| `apply_overrides` | `brand_name` | re-applies admin sub-theme overrides to the latest scorecard and saves a new version; described as "after `score_research`, before the final `save_scorecard`" |
| `score_research` | `brand_name`, optional `financials`, `app_reviews`, `tech_stack` (objects), `web_research_text` | scores six research dimensions 0-10: financial health, market sentiment, tech intelligence, brand reputation, company intelligence, competitive position. Pass this run's tool results or the first three score as flat 5.0 stubs. |

## Evidence scans (hit external systems)

| Tool | Input | Returns |
| --- | --- | --- |
| `scan_security` | `url` | security headers (CSP, HSTS, X-Frame-Options, ...), TLS version and cert, cookie flags, dead links, redirect issues, privacy/ToS URLs. Feeds rubric Q46 and Q48. |
| `detect_tech_stack` | `url` | CMS, frameworks, CDN, analytics, tag managers, payment providers, monitoring, chat widgets, hosting signals, each with confidence |
| `check_dns_auth` | `domain` | SPF, DKIM (common selectors), DMARC presence and policy. Feeds Q43. |
| `analyze_app_reviews` | `app_name`, optional `ios_app_id`, `android_app_id` | ratings, counts, version, recent review text per platform, cross-platform summary and platform gap. Scrapes Google Play. |
| `track_app_version` | `app_name`, optional `ios_app_id` | current iOS version, release date, days since update; appends a snapshot so cadence accrues across runs |
| `fetch_public_financials` | `company_name`, optional `ticker` | market cap, price, revenue, margins, employees, sector, analyst view; `status: private` when unlisted; can be `rate_limited` |
| `search_breach_db` | `domain` | breach history and credential exposure counts from public OSINT sources. Retired from scoring in 2026-08; still sensitive data. |

## Follow-ups

| Tool | Notes |
| --- | --- |
| `map_solutions` | `brand_name`, `threshold` (default 6.0): WWT capabilities and seller talking points for sub-themes under the threshold. Reads the saved scorecard; run after `get_scorecard`, only when asked. |
| `mark_app_scan_baseline` | belongs to a separate app-evaluation workflow, not this skill. Leave it alone. |

## Scorecard JSON shape

`save_scorecard` takes a JSON string. Mirror what `get_scorecard` returns in `scorecard`;
with `merge: true` you can leave out categories you did not re-assess. Top-level keys seen:

```
brand_name, website_url, ios_app_id, android_app_id, ticker, exchange, industry,
parent_company, scan_date (ISO 8601), core_score, research_score, overall_score,
categories[]        {id, name, score, sub_themes[] {id, name, score, na_reason?,
                      questions[] {question_id, score, evidence, provenance, confidence_level}}}
research_dimensions[] {id, name, score, sub_scores{}, summary, evidence[], sources[], data_source}
metadata            {tool_results {<tool_name>: <raw tool output>}, rubric_hash, quality{}}
signals, channel_breakdown, provisional
```

`provenance` values seen: `mcp_tool`, `browser_judged`, `model_prior`. `data_source` values
seen: `tool_data`, `web_research`, `partial`, `stub_no_data`. Anything `model_prior` or
`stub_no_data` is a placeholder, not a finding.

The six core categories (conversion effectiveness, ordering convenience, usability, brand
loyalty, performance, security) are scored from a 44-question rubric. Only a few questions are
answered by the tools above; the rest come from crawls, Lighthouse and accessibility checks in
the full monthly pipeline, which this server does not expose. Whether `save_scorecard` accepts
a scorecard with no `categories` at all has not been tested.
