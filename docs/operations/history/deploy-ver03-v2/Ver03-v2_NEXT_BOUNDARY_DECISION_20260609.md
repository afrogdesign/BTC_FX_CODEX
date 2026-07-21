# BTCFX Ver03-v2 Next Boundary Decision Prep

## 1. Purpose

This note prepares the next integration boundary decision for ChatGPT after the temporary Ver03-v2 execution review and retry.

## 2. Current verified state

- Ver03-v2 has a temporary manual diagnostic entrypoint: `scripts/run_btcfx_ver03_v2_reports.sh`.
- The rerun after `BTCFX-20260608-061-FIX` exited successfully.
- The intraperiod outcome CSV generation path exists.
- The intraperiod Markdown report path exists.
- The report hub output path is fixed to `運用資料/reports/report_hub_latest.md`.
- `logs/csv/active_plan_intraperiod_ohlcv.csv` may be missing, which causes `no_ohlcv` behavior.
- The flow remains diagnostic/manual only.

## 3. Temporary execution result summary

- The candidate intraperiod outcome report was generated.
- The report hub was written successfully on the retry.
- The intraperiod outcome CSV shows 21 rows, all `no_ohlcv`.
- Entry was not reached in the observed rows.
- TP1, TP2, SL, timeout, ambiguous, and pending counts were all zero in the observed output.

## 4. Generated outputs

- `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`
- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260609.md`
- `運用資料/reports/report_hub_latest.md`
- `docs/operations/deploy/Ver03-v2_EXECUTION_REVIEW_20260609.md`

## 5. Safety boundary

- No live trading.
- No automatic order execution.
- No runtime restart.
- No `main.py` execution.
- No `run_cycle` execution.
- No direct daily-sync call.
- No exchange API keys.
- No `paper_positions.csv` integration.
- `ACTIVE_*` is not FORMAL_GO.
- Active Plan candidates are not automatic orders.

## 6. Candidate next boundaries

### Option A: Keep manual execution for several cycles

- Pros:
  - safest
  - preserves manual verification
  - avoids hidden runtime side effects
- Cons:
  - requires manual run
  - daily report remains incomplete unless manually generated

### Option B: Wire only report generation into daily-sync

- Pros:
  - makes reports consistently available
  - still avoids live trading
- Cons:
  - daily-sync surface area grows
  - generated files need lifecycle rules

### Option C: Add preflight checks before daily-sync wiring

- Pros:
  - clarifies OHLCV availability, candidate CSV availability, output cleanliness
  - reduces noisy `no_ohlcv` runs
- Cons:
  - adds another prep task before integration

### Option D: Start email label audit only

- Pros:
  - aligns user-facing Ver03-v2 labeling
  - does not change execution path
- Cons:
  - does not improve report automation

## 7. Recommendation candidates for ChatGPT

- No final decision is made in this document.
- If a ranking is needed, the neutral preference order is:
  1. Option C: preflight checks
  2. Option B: report-only daily-sync wiring
  3. Option D: email label audit
- ChatGPT / the human owner must choose the actual next boundary.

## 8. Explicit non-decisions

- This document does not decide whether to wire into daily-sync.
- This document does not implement daily-sync wiring.
- This document does not promote `ACTIVE_*` to formal GO.
- This document does not change trading logic.
- This document does not change evaluator semantics.
- This document does not alter runtime behavior.

## 9. Stop conditions before any integration

- Stop if runtime restart is required.
- Stop if live trading or automatic order execution is required.
- Stop if exchange API keys are required.
- Stop if `paper_positions.csv` would need to change.
- Stop if trading logic or evaluator semantics would need to change.
- Stop if the work would require deciding the boundary inside Codex instead of documenting options.

## 10. Suggested next Codex task options

### Option C task

```text
NEXT BTCFX-20260608-063
Goal: Add preflight checks for Ver03-v2 manual diagnostic execution outputs and input availability.
Read: scripts/run_btcfx_ver03_v2_reports.sh, docs/operations/deploy/Ver03-v2_NEXT_BOUNDARY_DECISION_20260609.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Edit: scripts/run_btcfx_ver03_v2_reports.sh, docs/operations/deploy/Ver03-v2_TEMP_EXECUTION.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Test: `bash -n scripts/run_btcfx_ver03_v2_reports.sh`; `git diff --check`
Stop: if daily-sync code changes, runtime restart, live trading, API keys, or automatic order execution are required
Report: compact
```

### Option B task

```text
NEXT BTCFX-20260608-064
Goal: Wire Ver03-v2 intraperiod report generation into daily-sync as report-only diagnostics.
Read: tools/log_feedback.py, scripts/run_btcfx_ver03_v2_reports.sh, docs/operations/deploy/Ver03-v2_NEXT_BOUNDARY_DECISION_20260609.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Edit: tools/log_feedback.py, tests/test_log_feedback.py, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Test: `./.venv312/bin/python -m unittest tests/test_log_feedback.py`; `git diff --check`
Stop: if runtime restart, live trading, API keys, automatic order execution, paper_positions.csv integration, or evaluator changes are required
Report: compact
```

### Option D task

```text
NEXT BTCFX-20260608-065
Goal: Audit and prepare BTCFX Ver03-v2 email subject/report label migration without changing runtime behavior.
Read: docs/operations/deploy/Ver03-v2_NEXT_BOUNDARY_DECISION_20260609.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Edit: docs/operations/deploy/Ver03-v2_EMAIL_LABEL_AUDIT_20260609.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Test: `git diff --check`
Stop: if email sending code, runtime restart, API keys, or live trading changes are required
Report: compact
```
