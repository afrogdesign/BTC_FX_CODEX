# NEXT_ACTION

- current_work_id: `BTCFX-20260630-EVIDENCE-QUALITY-SUMMARY-E2E-SMOKE`
- mode: `LIGHT_CODEX`

## Current goal

manual surface export/check の smoke path を走らせ、generated `evidence_quality_summary` が exported artifacts に出ることを確認する。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/EVIDENCE_QUALITY_SUMMARY_SURFACE_WIRING.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/EVIDENCE_QUALITY_SUMMARY_E2E_SMOKE.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | manual surface export/check の smoke 結果を docs に記録する |
| Tests | smoke commands above, `git diff --check -- docs/operations/ai-orchestration/EVIDENCE_QUALITY_SUMMARY_E2E_SMOKE.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | docs smoke record の区切りとして docs 2 files だけ 1 commit |
| Stop | smoke command 失敗、generated `evidence_quality_summary` 未確認、runtime / old runtime / private / order / notification が必要、generated/logs commit が必要、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-NO-OHLCV-SOURCE-COVERAGE-CAUSE-DIAGNOSTIC`
- Goal: diagnose why `no_ohlcv` dominates and identify the next report-only coverage improvement without changing trading logic.
