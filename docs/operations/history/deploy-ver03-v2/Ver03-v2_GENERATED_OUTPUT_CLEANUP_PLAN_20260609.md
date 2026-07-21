# BTCFX Ver03-v2 Generated Output Cleanup / Archive Plan

## 1. Purpose

Define exact-path handling for Ver03-v2 generated diagnostics in the local iMac workspace without deleting, moving, archiving, staging, or committing them in this task.

## 2. Scope

- This plan applies only to Ver03-v2 generated diagnostics in the local iMac workspace.
- This plan does not delete files.
- This plan does not move files.
- This plan does not archive files.
- This plan does not change `.gitignore`.
- This plan does not change runtime behavior.
- This plan does not decide trading behavior.

## 3. Current observed generated outputs

| Path | Status | Date | Source command | Notes |
|---|---|---:|---|---|
| `logs/csv/active_plan_candidate_intraperiod_outcomes.csv` | untracked | 2026-06-09 | unknown | Intraperiod CSV diagnostic; `no_ohlcv=21件` in the paired report, so trading-performance inference is not possible from the intraperiod output alone |
| `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260609.md` | untracked | 2026-06-09 | unknown | Intraperiod review artifact; `no_ohlcv=21件`, `entry到達: 0件` |
| `運用資料/reports/analysis/active_plan_candidate_outcomes_20260609.md` | untracked | 2026-06-09 | unknown | Forward-close comparison artifact; all 21 rows are flat in the visible summary |
| `運用資料/reports/feedback_daily_sync_20260609.md` | untracked | 2026-06-09 | unknown | Daily-sync summary report; present as a generated review artifact |
| `運用資料/reports/report_hub_latest.md` | modified | 2026-06-09 | unknown | Latest report pointer; current workspace pointer for report navigation |

## 4. Recommended per-path action

- `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`
  - Keep local unless an exact archive task is approved.
  - Do not commit by default.
- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260609.md`
  - Archive candidate only if ChatGPT wants the review artifact preserved.
  - Do not commit by default.
- `運用資料/reports/analysis/active_plan_candidate_outcomes_20260609.md`
  - Archive candidate only if ChatGPT wants the comparison artifact preserved.
  - Do not commit by default.
- `運用資料/reports/feedback_daily_sync_20260609.md`
  - Archive candidate only if the daily-sync review is explicitly approved.
  - Do not commit by default.
- `運用資料/reports/report_hub_latest.md`
  - Keep local as the generated latest pointer.
  - Do not commit by default unless explicitly approved.

## 5. Archive candidate paths

Future archive destination pattern only:

- `運用資料/reports/archive/20260609/`

Plan-only mappings:

| Source path | Proposed archive path | Reason |
|---|---|---|
| `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260609.md` | `運用資料/reports/archive/20260609/active_plan_candidate_intraperiod_outcomes_20260609.md` | Review artifact for intraperiod evidence |
| `運用資料/reports/analysis/active_plan_candidate_outcomes_20260609.md` | `運用資料/reports/archive/20260609/active_plan_candidate_outcomes_20260609.md` | Comparison artifact for forward-close evidence |
| `運用資料/reports/feedback_daily_sync_20260609.md` | `運用資料/reports/archive/20260609/feedback_daily_sync_20260609.md` | Daily-sync review artifact |

## 6. Leave-in-workspace candidate paths

- `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`
- `運用資料/reports/report_hub_latest.md`
- Any generated diagnostic output not explicitly approved for archive or review commit

## 7. Do-not-touch paths

- `logs/csv/paper_positions.csv`
- Historical or archive reports
- Ver03-v1 planning docs
- Branch names
- Python package/module names
- Machine paths
- Source code and tests

## 8. Cleanup execution rules

- Cleanup must be a separate explicit task.
- Cleanup tasks must list exact paths.
- Cleanup tasks must decide whether each path action is `delete`, `archive`, `leave`, or `commit-as-review-artifact`.
- Cleanup tasks must not touch `logs/csv/paper_positions.csv`.
- Cleanup tasks must not infer extra files.
- Cleanup tasks must run `git status --short --branch --untracked-files=all` before and after.
- Cleanup tasks must stop if unexpected source/doc changes are dirty.

## 9. Review/archive execution options

- Option A: archive selected generated reports as review artifacts.
- Option B: leave all generated outputs local and proceed to controlled daily-sync review.
- Option C: add `.gitignore` rules in a future separate task.
- Option D: perform exact-path cleanup after user approval.

## 10. Safety boundary

- No live trading.
- No automatic order execution.
- No exchange/API key access.
- No runtime restart.
- No `main.py` execution.
- No `run_cycle` execution.
- No daily-sync execution.
- No `paper_positions` integration.
- No trading logic changes.
- No evaluator semantics changes.

## 11. Non-changes in this task

- No files were deleted.
- No files were moved.
- No files were archived.
- No generated diagnostic outputs were staged or committed.
- No `.gitignore` changes were made.
- No code changes were made.
- No runtime restart was performed.
- No daily-sync execution was performed.

## 12. Suggested next tasks

### Option A

```text
NEXT BTCFX-20260608-071
Goal: Archive explicitly approved Ver03-v2 generated report artifacts by exact path.
Read: docs/operations/deploy/Ver03-v2_GENERATED_OUTPUT_CLEANUP_PLAN_20260609.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Edit: only exact archive destination files approved by ChatGPT plus CONTROL/TASK_LEDGER
Test: `git diff --check`; `git status --short --branch --untracked-files=all`
Stop: if source code changes, runtime restart, live trading, API keys, automatic order execution, or unapproved generated paths are involved
Report: compact
```

### Option B

```text
NEXT BTCFX-20260608-068
Goal: Run one controlled daily-sync dry-run/review command only if explicitly approved, then capture output facts.
Read: docs/operations/deploy/Ver03-v2_DAILY_SYNC_OUTPUT_REVIEW_20260609.md, docs/operations/deploy/Ver03-v2_GENERATED_OUTPUT_POLICY_20260609.md, docs/operations/deploy/Ver03-v2_GENERATED_OUTPUT_CLEANUP_PLAN_20260609.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Edit: docs/operations/deploy/Ver03-v2_DAILY_SYNC_DRY_RUN_REVIEW_20260609.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Test: `git diff --check`
Stop: if runtime restart, live trading, API keys, automatic order execution, paper_positions.csv integration, or unclear generated output handling is required
Report: compact
```

### Option C

```text
NEXT BTCFX-20260608-072
Goal: Add explicit .gitignore policy for approved Ver03-v2 generated diagnostics.
Read: docs/operations/deploy/Ver03-v2_GENERATED_OUTPUT_POLICY_20260609.md, docs/operations/deploy/Ver03-v2_GENERATED_OUTPUT_CLEANUP_PLAN_20260609.md, .gitignore, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Edit: .gitignore, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Test: `git diff --check`; `git status --short --branch --untracked-files=all`
Stop: if source code changes, runtime restart, live trading, API keys, or automatic order execution are required
Report: compact
```
