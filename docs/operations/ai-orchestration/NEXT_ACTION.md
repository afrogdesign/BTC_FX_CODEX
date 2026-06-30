# NEXT_ACTION

- current_work_id: `BTCFX-20260630-MANUAL-SURFACE-EVIDENCE-SUMMARY`
- mode: `NORMAL_CODEX`

## Current goal

manual trading surface に `evidence_quality_summary` を report-only で表示する。

## Current summary

| Field | Value |
|---|---|
| Read | `src/ai/summary.py`, `src/notification/detail_page.py`, `tests/test_summary_format.py`, `tests/test_notification_detail_page.py`, `docs/operations/ai-orchestration/MANUAL_SURFACE_QUALITY_BACKLOG.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `src/ai/summary.py`, `src/notification/detail_page.py`, `tests/test_summary_format.py`, `tests/test_notification_detail_page.py`, `docs/operations/ai-orchestration/MANUAL_SURFACE_EVIDENCE_SUMMARY.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | manual trading surface に evidence quality summary を report-only で追加する |
| Tests | `./.venv312/bin/python -m unittest tests.test_summary_format tests.test_notification_detail_page`, `git diff --check -- src/ai/summary.py src/notification/detail_page.py tests/test_summary_format.py tests/test_notification_detail_page.py docs/operations/ai-orchestration/MANUAL_SURFACE_EVIDENCE_SUMMARY.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | source/test/docs の一区切りとして 1 commit |
| Stop | trading logic 変更が必要、runtime / old runtime / private / order / notification が必要、generated/logs 編集が必要、test 失敗、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-MANUAL-SURFACE-EVIDENCE-SUMMARY-APP-CONTRACT`
- Goal: expose the evidence quality summary in the app contract without changing trading logic.
