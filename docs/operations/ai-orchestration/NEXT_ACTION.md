# NEXT_ACTION

- current_work_id: `BTCFX-20260630-MANUAL-SURFACE-EVIDENCE-SUMMARY-APP-CONTRACT`
- mode: `NORMAL_CODEX`

## Current goal

`evidence_quality_summary` を既存 app contract / stdout-json に report-only で露出する。

## Current summary

| Field | Value |
|---|---|
| Read | `tools/log_feedback.py`, `tests/test_log_feedback.py`, `docs/operations/ai-orchestration/MANUAL_SURFACE_EVIDENCE_SUMMARY.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `tools/log_feedback.py`, `tests/test_log_feedback.py`, `docs/operations/ai-orchestration/MANUAL_SURFACE_EVIDENCE_SUMMARY_APP_CONTRACT.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | app contract / stdout-json に evidence quality summary を report-only で追加する |
| Tests | `./.venv312/bin/python -m unittest tests.test_log_feedback`, `git diff --check -- tools/log_feedback.py tests/test_log_feedback.py docs/operations/ai-orchestration/MANUAL_SURFACE_EVIDENCE_SUMMARY_APP_CONTRACT.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | source/test/docs の一区切りとして 1 commit |
| Stop | trading logic 変更が必要、runtime / old runtime / private / order / notification が必要、generated/logs 編集が必要、test 失敗、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-EVIDENCE-QUALITY-CHECKPOINT-REVIEW`
- Goal: review the completed evidence-quality surface path and decide the next product-quality task.
