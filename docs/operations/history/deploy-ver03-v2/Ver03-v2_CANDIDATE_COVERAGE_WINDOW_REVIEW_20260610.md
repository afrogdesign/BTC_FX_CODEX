# BTCFX Ver03-v2 Candidate Coverage / Window Alignment Review

## Purpose

Execute the selected human review outcome `REPORT_NEEDS_COVERAGE_REVIEW`.

Review candidate coverage and OHLCV window alignment using existing generated artifacts.

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

Human-selected branch: `REPORT_NEEDS_COVERAGE_REVIEW`

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

## OHLCV Window Alignment

- OHLCV row count: `499`
- OHLCV timestamp min/max JST:
  - min: `2026-06-04T22:45:00+09:00`
  - max: `2026-06-10T03:15:00+09:00`
- candidate timestamp min/max JST from outcome rows:
  - min: `2026-06-08T20:05:01.033760+09:00`
  - max: `2026-06-10T03:05:00.119594+09:00`
- number of candidate timestamps inside OHLCV window: `88`
- number before OHLCV window: `0`
- number after OHLCV window: `0`
- candidate timestamps inside OHLCV window percentage: `100.0%`
- latest-window OHLCV is enough for currently observed outcome rows: yes
- historical backfill caveat: not needed for the currently observed outcome rows, but still a future concern for older or rolled-back candidates.

## Outcome Bucket Review

- outcome row count: `88`
- outcome counts:
  - `entry_reached`: 1
  - `pending`: 12
  - `sl_first`: 39
  - `timeout`: 1
  - `tp1_first`: 35
- candidate_type counts:
  - `active_counter_scalp`: 22
  - `active_limit_retest`: 64
  - `active_market_small`: 2
- active_primary_action counts:
  - `ACTIVE_LIMIT_RETEST`: 6
  - `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP`: 66
  - `NO_ACTION`: 16
- side counts:
  - `long`: 47
  - `short`: 41
- entry_mode counts:
  - `limit_zone_mid`: 64
  - `market`: 2
  - `market_conditional`: 22
- candidate_status counts:
  - `candidate`: 66
  - `conditional`: 22
- candidate_type x outcome matrix:
  - `active_counter_scalp`: `pending=3`, `sl_first=10`, `tp1_first=9`
  - `active_limit_retest`: `entry_reached=1`, `pending=9`, `sl_first=29`, `timeout=1`, `tp1_first=24`
  - `active_market_small`: `tp1_first=2`
- non-`no_ohlcv` rows exist: yes
- NO_ACTION rows appear and should be interpreted as guidance / gatekeeping, not trade signals.
- ACTIVE_* rows are still only practical guidance, not automatic order candidates.

## Pending Bucket Review

- pending count: `12`
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
- pending breakdown by candidate_status:
  - `candidate`: 9
  - `conditional`: 3
- visible sample rows:
  - recent rows from `2026-06-09T14:05:00.982536+09:00` through `2026-06-10T03:05:00.119594+09:00` remain pending
  - these rows show blank `entry_reached_time`, `first_exit_time`, `first_exit_reason`, `mfe_r`, and `mae_r`
- likely interpretation:
  - unresolved recent windows
  - entry not yet resolved
  - candidate design / timeout horizon
  - insufficient resolution for some candidate paths
- unknowns remain about whether each pending row is due to window length, design, or unresolved state; the inspection does not resolve those individually.

## Candidate CSV Comparison

- candidate CSV row count: `88`
- candidate CSV timestamp range:
  - min: `2026-06-08T20:05:01.033760+09:00`
  - max: `2026-06-10T03:05:00.119594+09:00`
- candidate CSV count distributions:
  - candidate_type: `active_counter_scalp=22`, `active_limit_retest=64`, `active_market_small=2`
  - active_primary_action: `ACTIVE_LIMIT_RETEST=6`, `ACTIVE_LIMIT_RETEST+ACTIVE_COUNTER_SCALP=66`, `NO_ACTION=16`
  - side: `long=47`, `short=41`
  - entry_mode: `limit_zone_mid=64`, `market=2`, `market_conditional=22`
  - candidate_status: `candidate=66`, `conditional=22`
- outcome row count matches candidate CSV row count: yes
- gap requiring review: pending rows are concentrated in the newer tail of the candidate set, which suggests a timing / resolution issue rather than a count mismatch.

## Report Caveat Visibility

- pending caveat visible: yes
- no_ohlcv caveat visible: yes
- FORMAL_GO caveat visible: yes
- report-only caveat visible: yes
- the report communicates coverage caveats adequately: yes
- no wording change is required before wiring design based on this review alone.

## Coverage Decision

Decision: `COVERAGE_NEEDS_PENDING_REASON_REVIEW`

Rationale:

- OHLCV coverage reaches every observed outcome row, so window coverage is not the primary blocker.
- The `pending` bucket is still material and concentrated in recent rows.
- The next useful step is to explain pending reasons more precisely before any wiring boundary design.
- This is the conservative choice because the current data is strong enough for review but not yet precise enough for wiring design.

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

Suggested next work ID: `BTCFX-20260610-086`

Goal: docs-only pending reason classification review.

Do not recommend daily-sync implementation, deployment, runtime integration, or automatic trading unless explicitly approved after this review.
