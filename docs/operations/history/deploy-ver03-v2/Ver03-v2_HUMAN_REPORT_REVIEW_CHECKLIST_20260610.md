# BTCFX Ver03-v2 Human Report Review Checklist

## Purpose

Provide a human-facing checklist for reviewing the generated exchange-auto-public intraperiod report.

This is a review aid only.

This is not a trading decision.

This is not FORMAL_GO.

This is not daily-sync, runtime, deploy, or trading integration.

## Report Under Review

- Generated report path: `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260610.md`
- Outcome CSV lineage: `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`
- OHLCV lineage: `logs/csv/active_plan_intraperiod_ohlcv.csv`
- Source: `exchange-auto-public`

Lineage tasks:

- BTCFX-20260610-080 controlled public fetch
- BTCFX-20260610-081 controlled builder run
- BTCFX-20260610-082 controlled report generation
- BTCFX-20260610-083 report quality / coverage review

## Known Aggregate Facts to Verify Manually

- OHLCV row count: `499`
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
- non-`no_ohlcv` rows exist
- pending bucket remains and must be reviewed as a caveat

## Human Review Checklist

- [ ] The report title clearly identifies BTCFX Ver03-v2 and Active Plan intraperiod evaluation.
- [ ] The first conclusion clearly says report-only diagnostics.
- [ ] The report does not imply FORMAL_GO.
- [ ] The report does not imply auto-trading permission.
- [ ] The aggregate counts match the known facts.
- [ ] `pending` rows are visible and not hidden.
- [ ] `sl_first` and `tp1_first` balance is understandable.
- [ ] MFE / MAE / R information is readable enough for human review.
- [ ] Representative examples are useful.
- [ ] `NO_ACTION` rows are not misleadingly treated as trade signals.
- [ ] `ACTIVE_*` rows are not described as automatic order candidates.
- [ ] The report makes it clear this is path-validation evidence, not trading-performance proof.
- [ ] The report is useful enough to review before any wiring decision.
- [ ] Any confusing wording is noted before integration.

## Candidate Coverage Questions

- Are 499 latest-window OHLCV rows enough for current candidate coverage?
- Do candidate timestamps fall within the OHLCV range sufficiently?
- Are `pending` rows caused by recent/unresolved windows, missing data, or candidate design?
- Are `active_limit_retest`, `active_counter_scalp`, and `active_market_small` represented clearly?
- Are long/short results both visible enough?
- Is there any candidate type with obviously weak or misleading coverage?

## Interpretation Guardrails

- `tp1_first` does not automatically mean good strategy.
- `sl_first` does not automatically mean bad strategy without context.
- `pending` rows are unresolved, not failures.
- `NO_ACTION` should not be treated as a trade candidate.
- Active Plan is practical guidance, not formal order permission.
- No automatic trading decision can be made from this report alone.
- No integration should happen until human review is complete.

## Review Outcomes

- `REPORT_ACCEPT_FOR_WIRING_DESIGN`: report is clear enough to design a future wiring boundary; still no implementation in this task.
- `REPORT_NEEDS_WORDING_FIX`: report wording/structure should be adjusted before wiring design.
- `REPORT_NEEDS_COVERAGE_REVIEW`: candidate coverage/window alignment needs deeper review.
- `REPORT_HOLD`: do not proceed; keep manual diagnostics only.

## Next Boundary Recommendation

Recommended default after this checklist: human selects one of the review outcomes above.

If the human selects `REPORT_ACCEPT_FOR_WIRING_DESIGN`, the next task may be docs-only wiring boundary design.

If wording or coverage issues are found, the next task should fix/review those first.

Do not recommend daily-sync implementation directly in this task.

Do not recommend deployment or automatic trading.

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

Generated CSV/report outputs remain local and uncommitted.

Do not stage or commit generated CSVs or generated reports.

Leave existing generated report dirtiness untouched.
