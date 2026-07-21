# CURRENT_STATE

last_updated: 2026-07-21

## Current posture

- current branch: `Ver04-v3` (reported by bounded local git execution)
- accepted repository-cleanup checkpoint: `bff7669`
- accepted Product checkpoint: `0eeb26b` (`P8 issue lifecycle alignment`)
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- active spec: none
- safety: report-only / human-decided / no automatic order
- push: none

MCP does not independently expose git branch, HEAD, commit objects, or the complete dirty tree. Branch and commit locators come from bounded local-git reports; acceptance-critical source, tests, CLI routes, specs, state paths, and local artifact availability were reviewed directly through MCP.

## Version policy

- `Ver04-v3`: current accepted repository and Product working line
- `Ver05`: reserved for an evidence-backed, explicitly approved, implemented, validated, and accepted M6 change
- M1–M5 acceptance and P8 UI/report corrections do not qualify for `Ver05`

## Product state

- P1–P7 accepted
- P8 evidence pipeline accepted and collecting evidence
- P9 blocked pending adequate evidence and human approval
- M1–M5 accepted
- M6 not started and not authorized

Current evidence posture:

- actual-backed evidence remains missing / 0 eligible episodes in the latest reviewed P8 artifacts
- `P8-ISSUE-001` remains an evidence-driven `open hypothesis`
- `P8-ISSUE-002`, `P8-ISSUE-003`, and `P8-ISSUE-004` are resolved UI-contract issues
- the issue-summary generator represents those three UI lifecycle states deterministically without inventing market occurrences, resolved rows, or actual evidence
- P9 readiness remains false

## Accepted P8 lifecycle alignment

Direct MCP review confirmed:

- all existing issue keys are preserved
- issue 001 status and proxy evidence semantics are unchanged
- issues 002–004 are emitted as `resolved`
- each resolved UI issue has stable machine-readable accepted-implementation resolution metadata
- evaluation counts, class distribution, comparison metrics, global STOP metrics, actual evidence, and P9 readiness calculation paths remain unchanged
- focused unittest and task-scoped `git diff --check` were reported passing
- no classifier, score, gate, threshold, notification, mail, runtime, API, account, position, order, or automatic-tuning behavior changed

Archived acceptance spec:

- `chatgpt/specs/archive/20260721_p8_issue_lifecycle_alignment.md`

Issue register reconciliation:

- `docs/operations/ai-orchestration/P8_P9_ISSUE_REGISTER.md`

## Actual-evidence readiness review

`BTCFX-20260721-P8-ACTUAL-EVIDENCE-READINESS-REVIEW` is complete as a review-only task.

Directly confirmed availability:

- canonical private input directory `local/manual_trade_imports/` is absent
- `logs/csv/manual_actual_trades.csv` is absent
- `logs/csv/manual_actual_orders.csv` is absent
- `logs/csv/manual_actual_positions.csv` is absent
- `logs/csv/manual_trade_episodes.csv` is absent
- `logs/csv/manual_trade_signal_links.csv` is absent
- `local/manual_trade_imports/` is protected by `.gitignore`

Therefore the latest eligible actual evidence is 0 because no exchange export batch has entered the accepted local importer → episode builder → signal linker route. This is an input-availability blocker, not a P8 evaluator defect.

Accepted raw workbook contract:

- Trade History `.xlsx`: `UID`, `時間(UTC+09:00)`, `先物取引ペア`, `方向`, `注文の種類`, `約定価格`, `取引手数料`, `手数料支払い暗号資産`, `役割`, `決済損益`, plus at least one accepted quantity column
- Order History `.xlsx`: `UID`, `時間(UTC+09:00)`, `先物取引ペア`, `方向`, `レバレッジ`, `注文の種類`, `約定数量`, `平均約定価格`, `決済損益`, `手数料`, `ステータス`
- Position History `.xlsx`: `UID`, `取引ペア`, `オープン時間(UTC+09:00)`, `決済時刻`, `方向`, `実現損益`, `ステータス`

Accepted generated route:

1. `import-manual-actual-trades`
2. `build-manual-trade-episodes`
3. `link-manual-trades-to-signals`
4. P8 operating-cycle use of the episode/link pair

No source implementation is currently required. The next action requires a human-supplied local export batch.

## Repository model

Repository cleanup remains accepted. Active implementation areas remain `src/`, `tools/`, `scripts/`, `tests/`, `docs/operations/`, and `chatgpt/specs/active/`. Generated evidence and raw private inputs remain under ignored/uncommitted `local/` or `logs/` paths unless a separate artifact contract explicitly says otherwise.

## Active blocker

The main P8/P9 blocker is the absence of a complete privacy-safe local actual-trade export batch and, after import, sufficient high/medium-confidence linked episodes and an established validation window. No production tuning or phase promotion is authorized.
