# BTCFX Ver03-v2 Wiring Boundary Design

## Purpose

Define the docs-only wiring boundary for Ver03-v2 exchange-auto-public intraperiod diagnostics after the pending-outcome review.

This document does not implement wiring.

This document does not authorize execution, daily-sync, deploy, runtime, or trading work.

## Scope

This boundary covers the future path for:

- public 15m OHLCV fetch-to-local diagnostic artifact
- intraperiod outcome builder input/output
- Markdown report generation
- report-only daily-sync / report hub integration boundary
- human review gates before any runtime/deploy/trading work

## Preserved Decisions

- `PENDING_ACCEPT_WITH_CAVEAT_FOR_WIRING_BOUNDARY_DESIGN`
- pending categories are heuristic, not evaluator fields
- `ACTIVE_*` guidance is not `FORMAL_GO`
- no Active Plan candidates become automatic orders
- no `paper_positions.csv` integration yet
- generated CSV/report outputs remain local/uncommitted unless a later approved task changes policy

## Approved Future Boundary

The approved future boundary is a staged, review-gated diagnostic flow only:

1. Public 15m OHLCV is fetched into a local diagnostic CSV artifact.
2. The existing intraperiod outcome builder consumes that CSV and writes outcome rows locally.
3. The report builder consumes the outcome CSV and writes a Markdown review artifact locally.
4. Report-only daily-sync or report hub integration may reference the generated report, but only as a reporting surface, not as a runtime or trading trigger.
5. Human review must approve the evidence before any runtime, deploy, or trading work is discussed.

## Allowed Future Implementation Boundary

The smallest future implementation step that is safe after this docs-only design is:

- a standalone public 15m OHLCV fetch-to-local diagnostic command
- writing only `logs/csv/active_plan_intraperiod_ohlcv.csv`
- using public exchange market data only
- requiring no API keys
- not touching `main.py`, `run_cycle`, deploy/runtime config, trading logic, evaluator semantics, or `paper_positions.csv`

If later approved, the next small extension after that would be:

- run the existing intraperiod builder once against the generated OHLCV CSV
- inspect the outcome CSV locally
- stop before report/daily-sync/runtime/deploy/trading integration

## Wiring Boundary by Stage

### 1. Fetch-to-local diagnostic artifact

- input: public exchange 15m OHLCV only
- output: `logs/csv/active_plan_intraperiod_ohlcv.csv`
- source label: `exchange-auto-public`
- no private/account/order endpoints
- no API keys
- no live trading

### 2. Intraperiod outcome builder

- input: `logs/csv/active_plan_paper_candidates.csv` plus generated OHLCV CSV
- output: `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`
- builder stays report-only
- no automatic order execution
- no `paper_positions.csv` integration

### 3. Markdown report generation

- input: generated outcome CSV
- output: dated Markdown analysis report
- report remains diagnostic only
- report content must keep `pending` visible as unresolved diagnostic state

### 4. Report-only daily-sync / report hub boundary

- daily-sync may surface diagnostics as report-only artifacts
- report hub may point to the latest report
- neither becomes a runtime trigger
- neither becomes an automatic order path

### 5. Human review gates

- human review is required before any runtime, deploy, or trading task
- `FORMAL_GO` is not implied by `ACTIVE_*`
- report-only diagnostics are evidence, not trading permission

## Still Prohibited

- new fetch execution
- builder rerun
- report regeneration
- daily-sync execution
- deploy/runtime work
- `main.py`
- `run_cycle`
- API keys
- secrets
- private/account/order endpoints
- live trading
- automatic orders
- evaluator semantic changes
- trading logic changes

## Next Decision

Conservative recommendation: keep this as a review-gated diagnostic boundary only, and have the next step be human review of this boundary design before any implementation task is approved.

Do not move to implementation until the boundary document is explicitly accepted.
