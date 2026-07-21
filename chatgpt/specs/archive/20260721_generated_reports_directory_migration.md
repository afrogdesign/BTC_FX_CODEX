# Generated Reports Directory Migration

- created_at: 2026-07-21
- status: active implementation contract
- mode: bounded source/test/docs migration
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- frozen runtime repo: out of scope

## 1. Goal

Remove the obsolete Japanese top-level directory name `運用資料` from the active repository layout without breaking report generation, report discovery, tests, or operator-facing report paths.

Canonical generated report root becomes:

```text
local/reports/
```

After acceptance, no active source, test, script, current documentation, or generated-output contract may depend on `運用資料`.

## 2. Why `local/reports`

The repo already uses `local/` for generated, private, report-only, and non-committed assets such as:

- `local/manual_delivery_app_surface/`
- `local/manual_delivery_handoff/`
- `local/manual_trade_imports/`

Generated reports have the same lifecycle and should live under the same local-only boundary.

## 3. Current evidence

Active references exist in:

- `src/feedback/manual_scenario_coverage.py`
- `tools/run_daily_reports.py`
- `tools/render_notification_no_send_smoke.py`
- `tools/archive_progress_week.sh`
- `scripts/run_btcfx_ver03_v2_reports.sh`
- matching tests under `tests/`
- `.gitignore`
- current README/navigation documents

`運用資料/reports/` is therefore not safe to rename through documentation-only MCP work.

## 4. Observable contract

### 4.1 New path

All active default report paths must use:

```text
local/reports/
```

Expected subpaths include:

```text
local/reports/analysis/
local/reports/archive/analysis/
local/reports/archive/daily/
local/reports/archive/weekly/
local/reports/post_eval/
local/reports/report_hub_latest.md
```

### 4.2 Directory creation

Commands that write reports must create required parent directories before writing.

A fresh checkout with no pre-existing `local/reports/` directory must work.

### 4.3 Path output

CLI output, JSON fields, notification/detail-page report paths, smoke fixtures, and report hub references must expose `local/reports/...`, not `運用資料/reports/...`.

### 4.4 No fallback to the old path

Do not retain dual-write, silent fallback, symlink, or compatibility lookup for `運用資料/reports`.

The migration is one-way. Historical records may mention the old path, but active code and current docs may not.

### 4.5 Generated artifacts

Generated report artifacts remain local/uncommitted.

Do not commit dated generated Markdown reports merely because their path changed.

## 5. Existing filesystem migration

Treat tracked and generated files differently.

### Tracked historical files

Tracked historical files currently under `運用資料/reports/` must be moved to:

```text
_archive/legacy_operations_materials_20260721/reports_snapshot/
```

They are historical evidence, not active outputs.

### Ignored or untracked generated files

Existing ignored or untracked report outputs may be moved locally, preserving relative paths, from:

```text
運用資料/reports/<relative path>
```

to:

```text
local/reports/<relative path>
```

Do not stage or commit these generated artifacts.

### Top-level cleanup

After source migration and local artifact handling:

```text
運用資料/
```

must no longer exist in the active repo root.

Do not delete historical content already archived under `_archive/legacy_operations_materials_20260721/`.

## 6. Implementation boundaries

Codex may edit only files necessary to complete the migration, including:

- `.gitignore`
- active Python source with report-path defaults
- active tools and shell scripts with report-path defaults
- matching tests
- root `README.md`
- `chatgpt/README.md`
- `chatgpt/initial_settings.md`
- `docs/operations/ai-orchestration/README.md`
- `docs/operations/ai-orchestration/REPO_MAP.md`
- `docs/operations/ai-orchestration/CURRENT_STATE.md`
- `docs/operations/ai-orchestration/NEXT_ACTION.md`
- `運用資料/README.md` and `運用資料/reports/README.md` only as migration inputs; they should disappear with the old directory
- `_archive/legacy_operations_materials_20260721/README.md`
- tracked files moved from `運用資料/reports/` into the archive snapshot
- this active spec, which is archived only after acceptance

Codex may add one small shared path helper if it materially reduces duplicate path literals. Do not introduce a configuration framework.

## 7. Old progress script

`tools/archive_progress_week.sh` belongs to the retired `運用資料/progress` model.

Do not redirect it to `local/reports`. Either:

- archive it under `_archive/legacy_operations_materials_20260721/tools/`, or
- remove it if git history is sufficient and no active caller exists.

Confirm no active caller before removal.

## 8. Search boundary

Before editing, find active references to:

```text
運用資料
運用資料/reports
```

Exclude these historical areas from replacement requirements:

- `_archive/`
- `docs/operations/ai-orchestration/history/`
- `chatgpt/specs/archive/`
- `chatgpt/analysis/`
- `TASK_LEDGER.md`
- historical deploy/review documents

Historical files may retain exact old paths as evidence.

## 9. Required validation

Run the smallest matching validation that proves the path contract.

At minimum:

1. matching report-path and report-generation unittests, including:
   - `tests.test_run_daily_reports`
   - `tests.test_active_plan_report_family_registry`
   - `tests.test_daily_proxy_evaluator`
   - `tests.test_active_plan_candidate_outcomes_report`
   - relevant `manual_scenario_coverage` tests
2. notification/detail-page tests whose fixtures expose report paths
3. shell syntax check for the changed report script
4. one temporary-directory smoke proving a report command creates `local/reports/...` from an absent directory
5. task-scoped `git diff --check`
6. active-reference search showing no `運用資料` outside permitted history/archive locations

Do not run full replay, full multi-date bundles, runtime jobs, mail sending, launchd, or frozen-repo commands.

## 10. Acceptance criteria

- active source defaults use `local/reports`
- matching tests expect `local/reports`
- report directories are created when absent
- no dual-write or fallback to `運用資料`
- tracked old reports are archived
- generated local reports are not committed
- top-level `運用資料` no longer exists
- current navigation docs no longer describe it as active
- safety behavior is unchanged
- one local commit contains only this migration

## 11. Safety

- no trading logic changes
- no gate, scoring, threshold, classifier, notification, or mail behavior changes
- no runtime or launchd changes
- no frozen runtime repo access
- no private exports committed
- no reset, restore, checkout, clean, or stash manipulation
