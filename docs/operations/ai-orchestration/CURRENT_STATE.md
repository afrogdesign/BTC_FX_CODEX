# CURRENT_STATE

last_updated: 2026-07-21

## Current posture

- current cleanup branch: `Ver04-v3`
- cleanup base: `3db0399` (`Migrate generated reports to local directory`)
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- active spec: `chatgpt/specs/active/20260721_ver04_v3_repo_structure_cleanup_checkpoint.md`
- safety: report-only / human-decided / no automatic order
- repository cleanup checkpoint: ready for ChatGPT MCP review

## Version policy

- `Ver04-v3`: repository structure and documentation consolidation line
- `Ver05`: reserved for an evidence-backed, explicitly approved, implemented, validated, and accepted M6 change
- M1–M5 acceptance alone does not qualify for `Ver05`

## Product state

- P1–P7 accepted
- P8 evidence pipeline accepted and collecting evidence
- P9 blocked pending adequate evidence and human approval
- M1–M5 accepted
- M6 not started and not authorized

Product implementation is paused in this thread. This thread is reserved for repository cleanup.

## MCP cleanup completed

- canonical plan and AI navigation consolidated
- former top-level operations directory removed
- generated reports migrated to `local/reports/`
- old operations material moved under `_archive/`
- `chatgpt/analysis/` retired and archived
- Ver03-v2 deploy records and temporary report script moved to `docs/operations/history/`
- the long Ver03-v4 manual-preview runbook archived and replaced with a short current runbook
- old Ver03-v4 integrated strategy plan archived
- `VALUE_DEFENSE_ENTRY_LAYER.md` moved to strategy
- completed smoke, diagnostic, preview, checkpoint, cleanup-audit, and handoff records moved out of the orchestration root
- duplicate handoff and compatibility entry routes retired
- `Branch_Command/` removed
- duplicate archived reports directory removed; `reports_snapshot/` retained
- stale README files and the obsolete Ver02 spec template updated
- redundant `.gitkeep` files and empty placeholder directories removed
- durable directory model recorded in `DECISIONS.md`

## Checkpoint status

The local branch, cleanup-only staging, bounded validation, and one local cleanup commit are complete. Return this checkpoint to ChatGPT for MCP acceptance review.

Do not start Product implementation or M6 work in this thread.
