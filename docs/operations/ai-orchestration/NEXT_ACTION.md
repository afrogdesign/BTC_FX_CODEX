# NEXT_ACTION

- current_work_id: `BTCFX-20260721-GENERATED-REPORTS-DIRECTORY-MIGRATION`
- mode: `BOUNDED_CODEX`
- expected_branch: `Ver04-v2`
- active_spec: `chatgpt/specs/active/20260721_generated_reports_directory_migration.md`
- task_manifest: none
- status: ready for implementation
- push: none

## Goal

Migrate the active generated-report contract to `local/reports/`, then remove the obsolete top-level operations directory.

## Required result

- active source, tests, scripts, fixtures, and current docs use `local/reports`
- report writers create missing directories
- tracked historical report files move to `_archive/legacy_operations_materials_20260721/reports_snapshot/`
- ignored/untracked generated reports remain local/uncommitted and may be moved to `local/reports`
- retired progress tooling is archived or removed after caller check
- no active fallback or dual-write to the former output area
- one local commit

## Read

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`
3. active spec
4. active files containing the former output-area path
5. matching tests
6. current git status and tracked/untracked classification under the former report directory

Do not broadly read historical files merely because they contain the old path.

## Validation

Use the active spec's matching test set, one temporary-directory creation smoke, shell syntax check for changed scripts, active-reference search, and task-scoped `git diff --check`.

No heavy replay, runtime task, mail, notification, launchd, or frozen-repo operation.

## Safety

- preserve unrelated dirty changes
- do not commit generated reports
- no reset、restore、checkout、clean、or stash manipulation
- no trading logic、gate、threshold、classifier、scoring、runtime、mail、or notification change

This file contains exactly one current task.
