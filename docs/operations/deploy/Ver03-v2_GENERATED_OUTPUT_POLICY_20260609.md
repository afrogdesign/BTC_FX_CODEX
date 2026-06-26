# BTCFX Ver03-v2 Generated Output Lifecycle Policy

## 1. Purpose

Define how Ver03-v2 report-only diagnostic outputs are treated in the local workspace, review docs, and implementation tasks.

## 2. Scope

- This policy applies only to Ver03-v2 report-only diagnostics generated outputs.
- This policy does not apply to historical archived reports.
- This policy does not change runtime behavior.
- This policy does not decide live trading or automatic order behavior.

## 3. Generated output classes

### Class A: Runtime CSV diagnostics

- `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`
- Default policy: generated, not committed by implementation tasks unless explicitly approved.

### Class B: Dated Markdown analysis reports

- `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_YYYYMMDD.md`
- `運用資料/reports/analysis/active_plan_candidate_outcomes_YYYYMMDD.md`
- Default policy: generated, not committed by implementation tasks unless explicitly approved for review or archive.

### Class C: Latest pointer / hub reports

- `運用資料/reports/report_hub_latest.md`
- Default policy: generated pointer, not committed unless explicitly approved.

### Class D: Daily-sync dated reports

- `運用資料/reports/feedback_daily_sync_YYYYMMDD.md`
- Default policy: generated, not committed unless explicitly approved.

### Class E: Governance docs

- `docs/operations/deploy/*.md`
- `docs/operations/ai-orchestration/*.md`
- Default policy: commit when created or updated by an approved Codex task.

## 4. Current observed generated outputs

| Path | Status | Notes |
|---|---|---|
| `logs/csv/active_plan_candidate_intraperiod_outcomes.csv` | untracked | Generated runtime CSV diagnostic |
| `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260609.md` | untracked | Dated intraperiod analysis report |
| `運用資料/reports/analysis/active_plan_candidate_outcomes_20260609.md` | untracked | Dated candidate outcomes report |
| `運用資料/reports/feedback_daily_sync_20260609.md` | untracked | Daily-sync dated report |
| `運用資料/reports/report_hub_latest.md` | modified | Latest pointer / hub report |

- The intraperiod report shows `no_ohlcv` behavior, so trading-performance inference is not possible from that output alone.
- The reviewed daily-sync output is a report-only diagnostic surface.
- The observed outputs are present in the local workspace and are not part of this task's commit set.

## 5. Commit policy

- Implementation tasks commit source, tests, and governance docs only.
- Generated outputs are not staged or committed by default.
- Generated outputs may be committed only when:
  - ChatGPT explicitly scopes them in `Edit`.
  - The purpose is review or archive.
  - The task says which exact output files may be staged.
- Codex must never infer generated outputs should be committed just because they exist.

## 6. Workspace retention policy

- Generated outputs may remain in the local iMac workspace after diagnostic or manual runs.
- Codex should leave them untouched unless a task explicitly instructs cleanup or archive.
- Untracked generated outputs are acceptable if listed as known generated outputs in the prompt.
- If unexpected generated outputs appear, Codex must report them without staging.

## 7. Review policy

- For ChatGPT review, generated outputs should be summarized in docs rather than committed by default.
- Output facts to record:
  - path
  - status: present / missing / modified / untracked
  - source command if known
  - date
  - `no_ohlcv` or missing-input status if visible
  - whether trading-performance inference is possible
- `no_ohlcv`-only outputs must not be used to infer trading performance.

## 8. Cleanup policy

- Do not delete generated outputs in implementation tasks.
- Cleanup must be a separate explicit task.
- Cleanup tasks must list exact paths to remove or archive.
- Do not clean `paper_positions.csv`.
- Do not clean historical or archive reports unless explicitly approved.

## 9. Daily-sync interaction policy

- daily-sync may generate report-only diagnostics.
- daily-sync generated reports remain diagnostic only.
- daily-sync generated intraperiod outputs must not be mixed into `paper_positions.csv`.
- `ACTIVE_*` remains not `FORMAL_GO`.
- Missing OHLCV may produce `no_ohlcv`; this is diagnostic, not a failure.
- Runtime restart remains separate and not approved by this policy.

## 10. Safety boundary

- No live trading.
- No automatic order execution.
- No exchange/API key access.
- No runtime restart.
- No `main.py` execution.
- No `run_cycle` execution.
- No `paper_positions` integration.
- No trading logic changes.
- No evaluator semantics changes.

## 11. Open decisions

- Whether to commit selected generated reports as review artifacts.
- Whether to archive daily-sync generated reports on a schedule.
- Whether to add `.gitignore` rules for specific generated outputs.
- Whether to create a cleanup or archive command.
- Whether to run a controlled real daily-sync review task.

## 12. Suggested next tasks

### Option A

```text
NEXT BTCFX-20260608-068
Goal: Run one controlled daily-sync dry-run/review command only if explicitly approved, then capture output facts.
Read: docs/operations/deploy/Ver03-v2_DAILY_SYNC_OUTPUT_REVIEW_20260609.md, docs/operations/deploy/Ver03-v2_GENERATED_OUTPUT_POLICY_20260609.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Edit: docs/operations/deploy/Ver03-v2_DAILY_SYNC_DRY_RUN_REVIEW_20260609.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Test: `git diff --check`
Stop: if runtime restart, live trading, API keys, automatic order execution, paper_positions.csv integration, or unclear generated output handling is required
Report: compact
```

### Option B

```text
NEXT BTCFX-20260609-SYNC
Goal: Batch-sync reviewed pending_review metadata after accepted Ver03-v2 orchestration tasks.
Read: docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Edit: docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Test: `git diff --check`
Stop: if implementation code changes are required
Report: compact
```

### Option C

```text
NEXT BTCFX-20260608-070
Goal: Prepare exact-path cleanup/archive plan for Ver03-v2 generated diagnostics without deleting files.
Read: docs/operations/deploy/Ver03-v2_GENERATED_OUTPUT_POLICY_20260609.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Edit: docs/operations/deploy/Ver03-v2_GENERATED_OUTPUT_CLEANUP_PLAN_20260609.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Test: `git diff --check`
Stop: if file deletion, runtime restart, live trading, API keys, or automatic order execution is required
Report: compact
```

## 13. Non-changes in this task

- No generated diagnostic outputs were staged or committed.
- No daily-sync execution was performed.
- No code changes were made.
- No runtime restart was performed.
- No live trading or automatic order execution was performed.
- No `paper_positions.csv` integration was added.
- No trading logic or evaluator semantics were changed.
