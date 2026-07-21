# BTCFX Ver03-v2 Email / Report Label Audit

## 1. Purpose

Audit the current email subject and report label surface for Ver03-v2 without changing runtime behavior.

## 2. Required temporary label convention

- Primary visible label: `BTCFX Ver03-v2`
- Email subject prefix should eventually use: `[BTCFX Ver03-v2]`
- Report titles for Ver03-v2-specific reports should include: `BTCFX Ver03-v2`
- Historical/archive report labels must not change.
- Ver03-v1 planning file names must not change.
- Existing generated historical report files must not be renamed.
- Branch names must not change.
- Python package/module names must not change.
- Machine paths must not change.

## 3. Current known Ver03-v2-compliant labels

| File | String found | Class |
|---|---|---|
| `scripts/run_btcfx_ver03_v2_reports.sh` | `BTCFX Ver03-v2` | compliant |
| `docs/operations/deploy/Ver03-v2_TEMP_EXECUTION.md` | `BTCFX Ver03-v2` | compliant |
| `docs/operations/deploy/Ver03-v2_NEXT_BOUNDARY_DECISION_20260609.md` | `BTCFX Ver03-v2` | compliant |
| `tools/log_feedback.py` | `# BTCFX Ver03-v2 Active Plan 候補別 intraperiod 評価` | compliant |
| `docs/operations/deploy/Ver03-v2_EXECUTION_REVIEW_20260609.md` | `# BTCFX Ver03-v2 Temporary Execution Review` | compliant |

## 4. Email subject / summary subject candidates found

| File | String found | Class |
|---|---|---|
| `main.py` | `summary_subject` / `send_email(...)` / `save_pending_email(...)` | unclear / follow-up needed |
| `main.py` | `core_result["summary_subject"] = build_summary_subject(core_result)` | unclear / follow-up needed |
| `src/ai/summary.py` | `build_summary_subject(result)` | needs migration |
| `src/ai/summary.py` | `system_label`, `system_mode_label`, `active_subject_label` | needs migration |
| `src/ai/summary.py` | `legacy_subject` | needs migration |
| `src/ai/summary.py` | `"{rank_emoji} [{rank_label}] {active_label} / 実弾不可・行動計画 | {active_detail} ..."` | needs migration |
| `src/notification/detail_page.py` | `summary_subject`, `active_subject_label` | historical/display, do-not-change yet |
| `src/storage/csv_logger.py` | `summary_subject`, `active_subject_label` | historical/logging, do-not-change yet |
| `src/presentation/sanitize.py` | `active_subject_label` | unclear / follow-up needed |

Current narrow search result: the email subject construction path is visible in `main.py` and `src/ai/summary.py`, but no hard-coded `BTCFX Ver03-v2` email subject prefix was found there. The migration target is therefore subject-assembly logic, not the email transport layer.

## 5. Report title candidates found

| File | String found | Class |
|---|---|---|
| `tools/log_feedback.py` | `# BTCFX Ver03-v2 Active Plan 候補別 intraperiod 評価` | compliant |
| `docs/operations/deploy/Ver03-v2_TEMP_EXECUTION.md` | `# BTCFX Ver03-v2 Temporary Execution / Deploy Note` | compliant |
| `docs/operations/deploy/Ver03-v2_EXECUTION_REVIEW_20260609.md` | `# BTCFX Ver03-v2 Temporary Execution Review` | compliant |
| `docs/operations/deploy/Ver03-v2_NEXT_BOUNDARY_DECISION_20260609.md` | `# BTCFX Ver03-v2 Next Boundary Decision Prep` | compliant |
| `運用資料/reports/analysis/active_plan_candidate_intraperiod_outcomes_20260609.md` | `# BTCFX Ver03-v2 Active Plan 候補別 intraperiod 評価` | historical/generated, do-not-change yet |
| `運用資料/reports/report_hub_latest.md` | `# Report Hub` | historical hub label, do-not-change yet |
| `運用資料/reports/analysis/active_plan_candidate_outcomes_20260609.md` | report title entry for candidate outcomes | historical/generated, do-not-change yet |
| `運用資料/reports/feedback_daily_sync_20260609.md` | report title entry for daily sync | historical/generated, do-not-change yet |

## 6. Labels that should not change yet

- Historical and archive report labels.
- Existing generated report filenames.
- `Ver03-v1` planning file names.
- Branch names.
- Python package/module names.
- Machine paths.
- The current email transport implementation layer.

## 7. Required migration rules

- Use `BTCFX Ver03-v2` as the primary visible label for future Ver03-v2 email/report work.
- When email subject prefixes are migrated, use `[BTCFX Ver03-v2]`.
- Keep archive and historical labels unchanged.
- Keep generated historical file names unchanged.
- Do not rename branches, package names, or machine paths.
- Do not change runtime behavior in this task.

## 8. Risks

- The current email subject path is assembled from multiple values (`system_label`, `system_mode_label`, `active_subject_label`), so a future migration may need coordinated edits.
- Subject changes could affect legacy email rendering or saved pending-email payloads if not isolated.
- Ver03-v2 report titles are already aligned, so changing only email subject strings may create a partial migration if the label policy is not applied consistently.
- Historical and generated report files must remain untouched, so the migration boundary has to be explicit.

## 9. Proposed follow-up task options

### Option 1

```text
NEXT BTCFX-20260608-066
Goal: Apply BTCFX Ver03-v2 label migration to explicitly approved email/report subject strings.
Read: docs/operations/deploy/Ver03-v2_EMAIL_LABEL_AUDIT_20260609.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md, and only files listed as `needs migration` in the audit
Edit: only explicitly approved files from the audit plus CONTROL/TASK_LEDGER
Test: targeted tests for changed files; `git diff --check`
Stop: if runtime restart, live trading, API keys, automatic order execution, or unclear label ownership is encountered
Report: compact
```

### Option 2

```text
NEXT BTCFX-20260608-067
Goal: Add daily-sync output review for BTCFX Ver03-v2 report-only diagnostics before label migration.
Read: docs/operations/deploy/Ver03-v2_EMAIL_LABEL_AUDIT_20260609.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Edit: docs/operations/deploy/Ver03-v2_DAILY_SYNC_OUTPUT_REVIEW_20260609.md, CONTROL, TASK_LEDGER
Test: `git diff --check`
Stop: if runtime restart, live trading, API keys, automatic order execution, or code changes are required
Report: compact
```

## 10. Non-changes in this task

- No email sending code was changed.
- No runtime behavior was changed.
- No daily-sync integration was implemented.
- No label migration was applied.
- No archive or generated historical report files were renamed.
- No branch names, package names, or machine paths were changed.
