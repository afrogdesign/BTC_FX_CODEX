# CURRENT_STATE

last_updated: 2026-07-21

## Current posture

- current branch: `Ver04-v3` (reported by local git checkpoint)
- cleanup base: `3db0399`
- accepted cleanup checkpoint: `bff7669` (`docs: complete Ver04-v3 repository structure cleanup`)
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- active spec: none
- safety: report-only / human-decided / no automatic order
- repository cleanup: accepted

MCP does not independently expose git branch, HEAD, or commit objects. The branch and commit locators above come from the bounded local-git report; source paths, navigation files, archive placement, and removed-path boundaries were reviewed directly through MCP.

## Version policy

- `Ver04-v3`: accepted repository-structure and documentation-consolidation line
- `Ver05`: reserved for an evidence-backed, explicitly approved, implemented, validated, and accepted M6 change
- M1–M5 acceptance alone does not qualify for `Ver05`

## Product state

- P1–P7 accepted
- P8 evidence pipeline accepted and collecting evidence
- P9 blocked pending adequate evidence and human approval
- M1–M5 accepted
- M6 not started and not authorized

Product implementation remains outside this repository-cleanup thread.

## Accepted repository model

Active areas:

- `src/`
- `tools/`
- `scripts/`
- `tests/`
- `docs/operations/ai-orchestration/`
- `docs/operations/strategy/`
- `chatgpt/specs/active/`
- `local/` for generated uncommitted artifacts

Historical areas:

- `_archive/legacy_operations_materials_20260721/`
- `_archive/legacy_chatgpt_analysis_20260721/`
- `docs/operations/ai-orchestration/history/`
- `docs/operations/history/`
- `docs/operations/strategy/archive/`
- `chatgpt/specs/archive/`

Removed active routes that must not be recreated:

- former top-level Japanese operations directory
- `Branch_Command/`
- `chatgpt/analysis/`
- `docs/operations/deploy/`
- `docs/operations/ai-orchestration/handoffs/`
- old Ver03-v2 report script at `scripts/run_btcfx_ver03_v2_reports.sh`

## Acceptance evidence

- root README and repository map match the current directory model
- old report root is absent from active source, tools, and tests
- required strategy and history destinations exist
- duplicate decision heading is corrected to `DEC-20260721-010`
- active/history directory model is recorded in `DEC-20260721-011`
- reported focused tests: 19 pass
- reported shell syntax and `git diff --check`: pass
- reported generated `local/` and `logs/` files staged: none
- unrelated dirty changes were preserved
- push: none

## Cleanup status

The Ver04-v3 repository cleanup is complete and accepted. Further changes in this thread require a new explicit repository-cleanup finding; do not start Product or M6 work here.
