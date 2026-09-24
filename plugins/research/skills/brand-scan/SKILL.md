---
name: brand-scan
description: "Run or read a brandscanner assessment of a company's digital presence: security posture, tech stack, app-store reviews, public financials, email-auth records, benchmarks against the scanned cohort, and the resulting scorecard, using the brandscanner MCP server bundled with the research plugin. Use when someone says \"scan this brand\", \"run brandscanner on <company>\", \"what's <company>'s scorecard\", \"how does <company> compare to its cohort\", \"pull the tech stack for <company>\", or \"prep a digital assessment of a prospect\". Not for general desk research without the tool, for writing the pitch deck or proposal that follows, or for anything about WWT's own internal systems."
metadata:
  owner: scott.cullum@wwt.com
  category: research
  status: draft
  connectors: [brandscanner]
  version: 0.1.0
---

# Brand scan

Runs, refreshes or reads a brandscanner assessment of one company ("brand"): evidence scans of
its website, email domain and mobile apps, public financials, six research dimensions scored
0-10, and a saved scorecard with version history and percentiles against the cohort of
brands already scanned (currently quick-service restaurants). For sellers, strategists and
researchers preparing a digital assessment. Output is a short readout in chat, backed by the
scorecard saved in brandscanner. Per-tool notes and the scorecard JSON shape are in
`references/tools.md`.

## Inputs

- The company name, from the person. Never infer or pick one.
- Which parts they want: a read of what exists, a full run, or specific scans (see step 4).
- Optional: website URL, app-store IDs or ticker if the person knows them (`resolve_brand`
  usually finds them).

## Steps

1. **Connector check.** The `brandscanner` server connects when the research plugin is
   installed, but it needs a one-time sign-in. If tools like `list_brands` and `get_scorecard`
   aren't available, brandscanner isn't connected: tell the person to run `/mcp` in Claude Code
   (or accept the sign-in prompt in the Claude app), sign in, and ask again. Then stop.
2. **Read before you scan.** Reads are cheap; scans are slow and hit external services.
   Call `get_scorecard` for the brand (and `brand_benchmarks` if they asked about the cohort).
   - If a scorecard exists, show the person its `scan_date`, scores and `history_count`, and
     ask whether the existing one answers their question before starting a new run. A read-only
     request ("what's the scorecard", "how does it compare") ends here, at step 9.
   - If `status` is not `found`, the brand is new: say so and go on.
   - Call `scan_status` for the brand. A run that is still `running` with no finish time long
     after it started is an orphan; `close_stale_scan_runs` (default 60 minutes) marks it
     `timeout`. If a previous `save_scorecard` ended in `persist_failed`, call
     `resume_scorecard_save` with the brand slug (from `list_brands`) instead of re-scanning;
     `no_checkpoint` means there is nothing pending.
3. **Confirm the target, then resolve it.** Scans touch the company's live systems, so before
   the first one restate the company and get a yes. Then `resolve_brand` with the name; it
   returns website URL, iOS/Android app IDs, ticker, social handles and competitors. If the
   result looks like a different company (wrong domain, wrong sector), stop and ask.
4. **Agree the scope.** If the person didn't say, ask which of these they want, with rough
   timings (estimates, not measured):
   - Website: `scan_security` (headers, TLS, cookies, dead links, policy pages) and
     `detect_tech_stack` (frameworks, CMS, CDN, analytics, payments), well under a minute each.
   - Email domain: `check_dns_auth` (SPF, DKIM, DMARC), seconds.
   - Apps: `analyze_app_reviews` (ratings and recent reviews, both stores) and
     `track_app_version` (iOS version and release cadence), a minute or two; they scrape the
     stores.
   - Financials: `fetch_public_financials` (market cap, revenue, margins); seconds, returns
     `status: private` for private companies and can be rate-limited.
   - Breach history: `search_breach_db`; optional, no longer feeds a scored question.
   A full run is usually 5-15 minutes end to end. Default to everything except breach history.
5. **Open the run.** `start_scan_run` with the brand name; keep the `run_id`. Everything from
   here to step 8 belongs to that run.
6. **Run the scans** from step 4 with the URL, domain and IDs from `resolve_brand`. Keep two
   lists as you go, `tools_succeeded` and `tools_failed` (with the reason, e.g.
   `fetch_public_financials (rate_limited)`). A failure in one scan does not stop the others.
7. **Score and save.**
   - `score_research` with the brand name **and** this run's `fetch_public_financials`,
     `analyze_app_reviews` and `detect_tech_stack` results passed as `financials`,
     `app_reviews` and `tech_stack`. Omitting them scores those dimensions as flat 5.0 stubs.
     Pass any web research the person supplied as `web_research_text`.
   - `apply_overrides` for the brand, so analyst overrides survive the re-scan (its description
     asks for it after scoring and before the final save).
   - `save_scorecard` with `scorecard_json` built as `references/tools.md` describes and
     `merge` left `true`, so categories this run did not assess keep their previous scores.
     Keep the returned `scan_id`. If it returns `persist_failed`, the result is checkpointed:
     tell the person, and note that `resume_scorecard_save` replays it later.
8. **Close the run.** `finish_scan_run` with the `run_id`: on success `status: ok`, the
   `scan_id`, and the two tool lists; on failure `status: failed` with `error_details`
   `{stage, message}`. Always close it, including after a failure, or it shows as stale.
9. **Verify and present.** Call `get_scorecard` again and check: `scan_date` is today (for a
   fresh run), the `metadata.tool_results` keys match the scans that ran, and every section the
   person asked for is present with a non-stub value. Then present, in this order: overall,
   core and research scores with deltas from the previous scan; the category benchmarks
   (score, percentile, cohort average) from `brand_benchmarks`, plus the cohort rank; the
   research dimensions with their evidence; and a plain list of scans that failed or returned
   nothing, with the reason. Repeat any `rubric_mix_warning` the server returns, and say when a
   brand is outside the cohort's sector, since percentiles then compare unlike things.
   If the person asks where WWT could help, `map_solutions` maps low-scoring sub-themes to WWT
   capabilities; offer it, don't run it by default.

## Output

A chat readout of the scorecard as in step 9: numbers first, evidence second, gaps last, with
the `scan_id` and `scan_date` so the result can be found again. No file unless asked; if the
person wants a document, hand the verified numbers to a presentation skill rather than
retyping them.

## Guardrails

- Confirm the company before the first scan, and never scan one the person hasn't named.
- Never present partial output as a complete assessment. The core category scores come from
  the full monthly pipeline (crawls, Lighthouse, accessibility checks) that this server does
  not expose; a run from here refreshes the evidence tools and research dimensions and, with
  `merge: true`, carries the rest forward. Say which is which.
- Scorecards can include third-party breach data and scraped reviews. Keep them internal
  unless the person says otherwise, and don't paste raw breach records into shared channels.
- Don't invent scores. A dimension marked `stub` or `model_prior` is a placeholder; call it
  that.
- Always pair `start_scan_run` with `finish_scan_run`; never call `close_stale_scan_runs`
  while a run you know about is still in progress.

## Examples

**User says:** "Run brandscanner on <brand> and tell me where they're weak."
**Claude does:** Checks the tools are available, reads any existing scorecard and asks whether
a fresh run is wanted; confirms the company, resolves it, agrees the scope, opens a run, runs
the scans, scores, saves, closes the run, re-reads the scorecard and presents the lowest
percentile categories with their evidence and the list of scans that didn't return data.

**User says:** "How does <brand> compare to its cohort?"
**Claude does:** Calls `get_scorecard` and `brand_benchmarks` only; presents rank, category
percentiles and cohort averages with the scan date, repeats the rubric-mix warning if present,
and offers a re-scan if the scorecard is old. No scans run.

**Should NOT trigger:** "Write a two-paragraph company overview of <brand> for the intro
slide." That's desk research and deck writing; use a research or presentation skill without
brandscanner.
