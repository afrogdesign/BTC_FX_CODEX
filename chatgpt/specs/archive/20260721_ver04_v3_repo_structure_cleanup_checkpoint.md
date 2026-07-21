# Ver04-v3 Repository Structure Cleanup Checkpoint

- created_at: 2026-07-21
- work_id: `BTCFX-20260721-VER04-V3-REPO-CLEANUP-CHECKPOINT`
- status: active implementation contract
- mode: `BOUNDED_CODEX`
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- source branch: expected `Ver04-v2`; verify from local git
- target branch: `Ver04-v3`
- push: none

## Goal

Finalize the repository-only cleanup already performed through MCP, create the `Ver04-v3` development line without losing the dirty working tree, validate the active paths, and create one local cleanup checkpoint commit.

## Known state

- Generated reports were previously migrated to `local/reports/`; reported commit locator: `3db0399`.
- The current working tree contains later MCP documentation and filesystem cleanup changes.
- Source, trading behavior, runtime, notification behavior, gates, scoring, and classifiers were not intentionally changed by the later cleanup.
- Unrelated pre-existing dirty changes may exist and must be preserved.
- The frozen runtime repo is out of scope.

## Expected cleanup result

Active repository areas:

- `src/`
- `tools/`
- `scripts/`
- `tests/`
- `chatgpt/specs/`
- `chatgpt/tasks/` as optional strict tooling
- `chatgpt/templates/`
- `docs/operations/ai-orchestration/`
- `docs/operations/strategy/`
- `docs/operations/manual-preview/`
- generated local assets under `local/`

Historical areas:

- `_archive/legacy_operations_materials_20260721/`
- `_archive/legacy_chatgpt_analysis_20260721/`
- `docs/operations/ai-orchestration/history/`
- `docs/operations/history/`
- `docs/operations/strategy/archive/`
- `chatgpt/specs/archive/`

Removed active areas:

- former top-level Japanese operations directory
- `Branch_Command/`
- `chatgpt/analysis/`
- `docs/operations/deploy/`
- `docs/operations/ai-orchestration/handoffs/`

## MCP cleanup already performed

- consolidated canonical planning and AI navigation
- archived old planning, runtime-transition, task-specific smoke, diagnostic, preview, checkpoint, and handoff records
- moved Ver03-v2 deployment records to `docs/operations/history/deploy-ver03-v2/`
- moved the temporary `scripts/run_btcfx_ver03_v2_reports.sh` into that historical area
- replaced the long Ver03-v4 manual-preview runbook with a short current runbook and archived the original
- moved the Ver03-v4 integrated strategy plan to `docs/operations/strategy/archive/`
- moved `VALUE_DEFENSE_ENTRY_LAYER.md` from AI orchestration to strategy
- retired compatibility entry files and `chatgpt/initial_settings.md` into orchestration history
- removed redundant `.gitkeep` files from non-empty directories
- removed duplicate archived `reports/` while retaining `reports_snapshot/`
- updated current and archive README files
- updated the spec template from the obsolete Ver02 format

## Required work

1. Confirm actual branch, HEAD, and dirty-tree state from local git.
2. Confirm commit `3db0399` exists in the current history.
3. If currently on `Ver04-v2` and local branch `Ver04-v3` does not exist, create and switch to `Ver04-v3` while preserving the dirty tree.
4. If already on `Ver04-v3`, continue.
5. If the current branch is unexpected, or `Ver04-v3` already exists but cannot be entered safely without risking unrelated dirty changes, stop and report.
6. Review the full cleanup diff by name/status and content. Preserve unrelated changes.
7. Fix the duplicate decision heading in `DECISIONS.md`: the second `DEC-20260721-009` heading for the Ver04-v3/Ver05 version gate becomes `DEC-20260721-010`.
8. Add or finalize `DEC-20260721-011` for the current repository directory model and retirement of duplicate compatibility routes.
9. Update `CURRENT_STATE.md` and `NEXT_ACTION.md` only to accurately describe this checkpoint as ready for ChatGPT review; do not self-accept Product or M6 work.
10. Stage only cleanup-related files and create one local commit.

## Active-path validation

Prove that active source, tools, scripts, tests, root README, current ChatGPT docs, and current operations docs do not depend on removed routes.

Search terms:

```text
運用資料
Branch_Command
chatgpt/analysis
docs/operations/deploy
scripts/run_btcfx_ver03_v2_reports.sh
handoffs/CURRENT_HANDOFF.md
VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md
PROMPTS.md
MINI_CODEX_RULES.md
PROMPT_PREFLIGHT_CHECKLIST.md
CHATGPT_COMMANDER_PROMPT.md
chatgpt/initial_settings.md
```

Permitted matches:

- `_archive/`
- `docs/operations/history/`
- `docs/operations/ai-orchestration/history/`
- `docs/operations/strategy/archive/`
- `chatgpt/specs/archive/`
- `docs/operations/ai-orchestration/TASK_LEDGER.md`
- explicit current text describing a removed path as removed
- historical decisions where supersession is clear

## Required path checks

Must be absent:

```text
運用資料/
Branch_Command/
chatgpt/analysis/
docs/operations/deploy/
docs/operations/ai-orchestration/handoffs/
scripts/run_btcfx_ver03_v2_reports.sh
```

Must be present:

```text
AGENTS.md
docs/operations/README.md
docs/operations/ai-orchestration/START_HERE.md
docs/operations/ai-orchestration/MASTER_PLAN.md
docs/operations/ai-orchestration/CURRENT_STATE.md
docs/operations/ai-orchestration/NEXT_ACTION.md
docs/operations/ai-orchestration/AI_WORKFLOW.md
docs/operations/ai-orchestration/CONTROL.md
docs/operations/ai-orchestration/REPO_MAP.md
docs/operations/strategy/README.md
docs/operations/strategy/MACRO_IMPLEMENTATION_ROUTE.md
docs/operations/strategy/VALUE_DEFENSE_ENTRY_LAYER.md
docs/operations/manual-preview/ACTIVE_PLAN_MANUAL_PREVIEW_RUNBOOK.md
docs/operations/history/README.md
docs/operations/history/deploy-ver03-v2/
_archive/legacy_operations_materials_20260721/reports_snapshot/
```

## Validation budget

Run only bounded validation:

- `bash -n scripts/refresh_current_manual_delivery_app_surface.command`
- `./.venv312/bin/python -m unittest tests.test_ai_task_contract tests.test_run_daily_reports tests.test_active_plan_report_family_registry`
- targeted active-path search described above
- targeted canonical-path existence checks
- verify no generated `local/` or `logs/` files are staged
- task-scoped or full cleanup `git diff --check`

Do not run replay, real-data bundles, runtime jobs, mail, notification sending, launchd, or frozen-repo commands.

## Scope boundaries

Do not change:

- application logic
- trading logic
- thresholds, gates, scoring, or classifiers
- runtime or launchd configuration
- notification or mail behavior
- private/account/position/order integrations
- generated evidence under `local/` or runtime evidence under `logs/`
- M6 authorization or implementation

## Dirty-tree rules

- preserve unrelated changes
- do not make a clean tree a completion condition
- no reset, restore, checkout, clean, or stash manipulation
- creating `Ver04-v3` with `git switch -c Ver04-v3` is allowed only after confirming the current branch and branch absence

## Commit

- branch: `Ver04-v3`
- one local commit
- recommended message: `docs: complete Ver04-v3 repository structure cleanup`
- push: none

## Report

Return the compact report format with:

- actual source branch and resulting branch
- base HEAD and new commit
- moved/deleted directory summary
- README/template audit result
- active old-path search result
- validation commands and results
- unrelated dirty changes preserved

Write the same compact report exactly once to:

`/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt`

After writing, do not read, check existence, retry, watch, poll, or recreate the file.
