# EVIDENCE_ACCURACY_RESUME

## Purpose

runtime pull handoff path を閉じ、MCP-primary repo を current source of truth として evidence / intraperiod / win-rate diagnostics を再開する。

## Current source of truth

- MCP-primary repo is the current source of truth
- old runtime pull is not needed
- no old runtime repo access was performed in this task

## Evidence baseline

- dashboard parity: `dashboard_parity_complete`
- checkpoint push: reported successful
- evidence phase: current
- automatic trading: not started
- profitability improvement: not complete

## Existing accepted tooling

- `build-active-plan-intraperiod-outcomes`
- `build-active-plan-intraperiod-review`
- `build-active-plan-intraperiod-review --stdout-json`
- `active_plan_intraperiod_review.v1`
- `intraperiod_review_stdout_json`
- `operator_status_diagnostic`
- `safe_config_schema_audit`
- `operator_triage_summary`
- `manual_action_checklist_surface`

## Available intraperiod reports

| Date | Path | Status | Notes |
|---|---|---|---|
| 2026-06-24 | `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260624.md` | available | not deeply analyzed in this task |
| 2026-06-25 | `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260625.md` | available | not deeply analyzed in this task |
| 2026-06-26 | `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260626.md` | available | not deeply analyzed in this task |
| 2026-06-27 | `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260627.md` | available | not deeply analyzed in this task |
| 2026-06-28 | `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260628.md` | available | not deeply analyzed in this task |
| 2026-06-29 | `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260629.md` | available | not deeply analyzed in this task |
| 2026-06-30 | `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260630.md` | available | not deeply analyzed in this task |

## Diagnostic dimensions

- entry reached
- TP / SL sequence
- timeout
- MFE / MAE
- false positives
- missed opportunities
- bad entry timing
- fakeout
- same-bar TP1+TP2 without SL classified as `tp2_first`
- expectancy / win-rate

この task は resume / planning only であり、metric computation はしない。

## What to avoid

- no trading logic change
- no auto order
- no private/account/order endpoint
- no notification sending
- no runtime action
- no generated file commit
- no profitability claim without evidence
- no broad repo exploration

## Next recommended task

- `BTCFX-20260630-INTRAPERIOD-WINRATE-DIAGNOSTIC-PASS`
- Goal: perform a focused diagnostic pass over available intraperiod outcome reports to identify what metrics and tests are needed next, without changing trading logic.
- Mode: `NORMAL_CODEX`

## Stop / human-check triggers

- missing or inconsistent evidence files
- need to change trading rules
- need to touch private/account/order endpoints
- need to run live/runtime actions
- need to send notifications
- need to claim profitability
- need to expand beyond listed evidence files
