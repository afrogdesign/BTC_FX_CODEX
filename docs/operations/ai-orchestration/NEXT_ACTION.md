# NEXT_ACTION

- current_work_id: `BTCFX-20260630-EVIDENCE-QUALITY-SUMMARY-SURFACE-WIRING`
- mode: `NORMAL_CODEX`

## Current goal

`build_intraperiod_evidence_quality_summary` を既存 manual surface / app snapshot / app contract path に配線する。

## Current summary

| Field | Value |
|---|---|
| Read | `tools/log_feedback.py`, `src/trade/active_plan_intraperiod.py`, `src/ai/summary.py`, `src/notification/detail_page.py`, `tests/test_active_plan_notification_formatting.py`, `tests/test_log_feedback.py`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `tools/log_feedback.py`, `tests/test_active_plan_notification_formatting.py`, `tests/test_log_feedback.py`, `docs/operations/ai-orchestration/EVIDENCE_QUALITY_SUMMARY_SURFACE_WIRING.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | generated `evidence_quality_summary` を app contract / stdout-json / exported surface に配線する |
| Tests | `./.venv312/bin/python -m unittest tests.test_log_feedback tests.test_active_plan_notification_formatting`, `git diff --check -- tools/log_feedback.py tests/test_active_plan_notification_formatting.py tests/test_log_feedback.py docs/operations/ai-orchestration/EVIDENCE_QUALITY_SUMMARY_SURFACE_WIRING.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | source/test/docs の一区切りとして 1 commit |
| Stop | trading logic 変更が必要、runtime / old runtime / private / order / notification が必要、generated/logs commit が必要、test 失敗、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-EVIDENCE-QUALITY-SUMMARY-E2E-SMOKE`
- Goal: manual surface export/check の smoke path を走らせ、generated `evidence_quality_summary` が exported artifacts に出ることを確認する。
