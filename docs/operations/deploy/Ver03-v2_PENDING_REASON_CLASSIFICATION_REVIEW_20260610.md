# BTCFX Ver03-v2 Pending Reason Classification Review

## Purpose

Execute the selected coverage decision `COVERAGE_NEEDS_PENDING_REASON_REVIEW`.

Classify the 12 pending intraperiod outcomes using existing generated artifacts only.

This is docs-only inspection.

This is not wiring design.

This is not daily-sync/runtime/deploy/trading integration.

## Inputs Reviewed

- OHLCV CSV: `logs/csv/active_plan_intraperiod_ohlcv.csv`
- Outcome CSV: `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`
- Candidate CSV: `logs/csv/active_plan_paper_candidates.csv`
- Markdown report: `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md`

Lineage:

- 080 controlled public fetch
- 081 controlled builder run
- 082 controlled report generation
- 083 report quality / coverage review
- 084 human checklist
- 085 candidate coverage/window review

Selected branch: `COVERAGE_NEEDS_PENDING_REASON_REVIEW`

## Commands Executed

Exact read-only inspection commands:

```bash
cd /Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor
git status --short --branch --untracked-files=all
test -f logs/csv/active_plan_intraperiod_ohlcv.csv
test -f logs/csv/active_plan_candidate_intraperiod_outcomes.csv
test -f logs/csv/active_plan_paper_candidates.csv
test -f 運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md
```

No generator command was run.

No new fetch, builder rerun, or report rerun occurred.

## Pending Set Summary

- pending count: `12`
- resolved count: `76`
- OHLCV max timestamp: `2026-06-10T03:15:00+09:00`
- pending age-hours min/max/avg to OHLCV max:
  - min: `0.17`
  - max: `13.17`
  - avg: `5.67`
- resolved age-hours min/max/avg to OHLCV max:
  - min: `0.17`
  - max: `31.17`
  - avg: `16.97`
- pending breakdown by candidate_type:
  - `active_counter_scalp`: 3
  - `active_limit_retest`: 9
- pending breakdown by active_primary_action:
  - `ACTIVE_LIMIT_RETEST`: 2
  - `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP`: 10
- pending breakdown by side:
  - `long`: 6
  - `short`: 6
- pending breakdown by entry_mode:
  - `limit_zone_mid`: 9
  - `market_conditional`: 3

## Candidate CSV Comparison

- candidate CSV row count: `88`
- candidate CSV timestamp range:
  - min: `2026-06-08T20:05:01.033760+09:00`
  - max: `2026-06-10T03:05:00.119594+09:00`
- candidate CSV count distributions:
  - candidate_type:
    - `active_counter_scalp`: `22`
    - `active_limit_retest`: `64`
    - `active_market_small`: `2`
  - active_primary_action:
    - `ACTIVE_LIMIT_RETEST`: `6`
    - `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP`: `66`
    - `NO_ACTION`: `16`
  - side:
    - `long`: `47`
    - `short`: `41`
  - entry_mode:
    - `limit_zone_mid`: `64`
    - `market`: `2`
    - `market_conditional`: `22`
  - candidate_status:
    - `candidate`: `66`
    - `conditional`: `22`
- outcome row count matches candidate CSV row count: `88`
- candidate coverage gap requiring review: none at the window level; the unresolved bucket is about pending outcome resolution, not missing rows

## Pending Row Context

All 12 pending rows are listed below using existing generated fields only.

| candidate_id | timestamp_jst | candidate_type | active_primary_action | side | entry_mode | candidate_status | bars_after_candidate | entry-touch check | draft pending reason | notes |
|---|---|---|---|---|---|---|---:|---|---|---|
| `20260609_050500:active_limit_retest:short` | `2026-06-09T14:05:00.982536+09:00` | `active_limit_retest` | `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP` | `short` | `limit_zone_mid` | `candidate` | 53 | `False` | `PENDING_ENTRY_NOT_TOUCHED_BY_SIMPLE_RANGE_CHECK` |  |
| `20260609_070501:active_limit_retest:short` | `2026-06-09T16:05:01.148805+09:00` | `active_limit_retest` | `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP` | `short` | `limit_zone_mid` | `candidate` | 45 | `False` | `PENDING_RECENT_UNRESOLVED_WINDOW` |  |
| `20260609_080501:active_limit_retest:long` | `2026-06-09T17:05:01.058143+09:00` | `active_limit_retest` | `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP` | `long` | `limit_zone_mid` | `candidate` | 41 | `False` | `PENDING_RECENT_UNRESOLVED_WINDOW` |  |
| `20260609_080501:active_counter_scalp:long` | `2026-06-09T17:05:01.058143+09:00` | `active_counter_scalp` | `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP` | `long` | `market_conditional` | `conditional` | 41 | `False` | `PENDING_RECENT_UNRESOLVED_WINDOW` |  |
| `20260609_080501:active_limit_retest:short` | `2026-06-09T17:05:01.058143+09:00` | `active_limit_retest` | `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP` | `short` | `limit_zone_mid` | `candidate` | 41 | `False` | `PENDING_RECENT_UNRESOLVED_WINDOW` |  |
| `20260609_130501:active_limit_retest:short` | `2026-06-09T22:05:01.147889+09:00` | `active_limit_retest` | `ACTIVE_LIMIT_RETEST` | `short` | `limit_zone_mid` | `candidate` | 21 | `False` | `PENDING_RECENT_UNRESOLVED_WINDOW` |  |
| `20260609_140500:active_limit_retest:short` | `2026-06-09T23:05:00.524496+09:00` | `active_limit_retest` | `ACTIVE_LIMIT_RETEST` | `short` | `limit_zone_mid` | `candidate` | 17 | `False` | `PENDING_RECENT_UNRESOLVED_WINDOW` |  |
| `20260609_170500:active_limit_retest:long` | `2026-06-10T02:05:00.970467+09:00` | `active_limit_retest` | `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP` | `long` | `limit_zone_mid` | `candidate` | 5 | `False` | `PENDING_RECENT_UNRESOLVED_WINDOW` |  |
| `20260609_170500:active_counter_scalp:long` | `2026-06-10T02:05:00.970467+09:00` | `active_counter_scalp` | `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP` | `long` | `market_conditional` | `conditional` | 5 | `False` | `PENDING_RECENT_UNRESOLVED_WINDOW` |  |
| `20260609_170500:active_limit_retest:short` | `2026-06-10T02:05:00.970467+09:00` | `active_limit_retest` | `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP` | `short` | `limit_zone_mid` | `candidate` | 5 | `False` | `PENDING_RECENT_UNRESOLVED_WINDOW` |  |
| `20260609_180500:active_limit_retest:long` | `2026-06-10T03:05:00.119594+09:00` | `active_limit_retest` | `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP` | `long` | `limit_zone_mid` | `candidate` | 1 | `False` | `PENDING_RECENT_UNRESOLVED_WINDOW` |  |
| `20260609_180500:active_counter_scalp:long` | `2026-06-10T03:05:00.119594+09:00` | `active_counter_scalp` | `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP` | `long` | `market_conditional` | `conditional` | 1 | `False` | `PENDING_RECENT_UNRESOLVED_WINDOW` |  |

## Draft Pending Reason Categories

These categories are diagnostic and heuristic, not evaluator logic.

- `PENDING_RECENT_UNRESOLVED_WINDOW`: `11`
- `PENDING_ENTRY_NOT_TOUCHED_BY_SIMPLE_RANGE_CHECK`: `1`
- `PENDING_TOUCHED_BUT_EXIT_OR_TIMEOUT_UNRESOLVED`: `0`
- `PENDING_NO_POST_CANDIDATE_BARS`: `0`
- `PENDING_REASON_UNKNOWN`: `0`

## Report Caveat Visibility

- The generated report clearly shows `pending`, `no_ohlcv`, `report-only`, and `FORMAL_GO` context words.
- The report title and first conclusion identify BTCFX Ver03-v2 Active Plan intraperiod report-only diagnostics.
- The report is readable enough for human review, but it still treats `pending` as an unresolved diagnostic bucket rather than an explicit evaluator reason field.
- The report does not hide the unresolved bucket, so the caveat is visible before any wiring decision.

## Interpretation

- Pending appears mainly due to recent unresolved windows.
- Entry-not-touched is a material minor category for one older short setup.
- No pending row suggests insufficient OHLCV coverage; all 88 outcome rows fall within the observed OHLCV window.
- The report does not appear to have a wording defect, but it should still be clearer about heuristic pending classification.
- This does not block wiring boundary design, but it does warrant a caveat that pending is unresolved and heuristic.

## Pending Decision

Decision: `PENDING_ACCEPT_WITH_CAVEAT_FOR_WIRING_BOUNDARY_DESIGN`

Rationale:

- The pending set is understandable enough to proceed to docs-only wiring boundary design.
- The caveat is that the pending categories are heuristic, not explicit evaluator fields.
- This is still not an implementation task.

## What Was Not Run

- no new external fetch
- no builder rerun
- no report regeneration
- no daily-sync
- no report hub generation
- no deploy
- no runtime
- no `main.py`
- no `run_cycle`
- no API keys
- no private/account/order endpoints
- no live trading
- no automatic orders
- no `paper_positions.csv` integration
- no evaluator semantic changes
- no trading logic changes
- no archive/cleanup

## Generated Output Policy

- Generated CSV/report outputs remain local and uncommitted.
- Do not stage or commit generated CSVs or generated reports.
- Leave existing generated report dirtiness untouched.

## Next Recommended Task

Suggested next work ID: `BTCFX-20260610-087`

Goal: docs-only design of the future wiring boundary.

Do not recommend daily-sync implementation, deployment, runtime integration, or automatic trading unless explicitly approved after this review.
