# NEXT_ACTION

- current_work_id: `BTCFX-20260630-EVIDENCE-QUALITY-SMOKE-EXPORT`
- mode: `LIGHT_CODEX`

## Current goal

既存 manual surface export/check path を smoke 実行し、exported artifacts に `evidence_quality_summary` が出ることを確認する。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/manual-preview/ACTIVE_PLAN_MANUAL_PREVIEW_RUNBOOK.md`, `docs/operations/ai-orchestration/EVIDENCE_QUALITY_CHECKPOINT_REVIEW.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/EVIDENCE_QUALITY_SMOKE_EXPORT.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | 既存 manual surface export/check path を smoke 実行し、exported artifacts に `evidence_quality_summary` が出ることを確認する |
| Tests | smoke commands, `git diff --check -- docs/operations/ai-orchestration/EVIDENCE_QUALITY_SMOKE_EXPORT.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | docs smoke record として 1 commit |
| Stop | source/test 編集が必要、generated/logs 編集を commit する必要がある、trading logic 変更が必要、runtime / old runtime / private / order / notification が必要、test 失敗、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-PRODUCT-QUALITY-NEXT-DECISION`
- Goal: decide the next product-quality implementation task after evidence-quality surface verification.
