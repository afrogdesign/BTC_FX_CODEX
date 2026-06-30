# NEXT_ACTION

- current_work_id: `BTCFX-20260630-REMOVE-EDIT-FILE-LIMIT`
- mode: `LIGHT_CODEX`

## Current goal

`MINI_CODEX_RULES.md` から edit file 数の上限ルールを削除する。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/MINI_CODEX_RULES.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/MINI_CODEX_RULES.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | edit file 数の上限ルールを削除し、ChatGPT 主導の範囲判断に寄せる |
| Tests | `git diff --check -- docs/operations/ai-orchestration/MINI_CODEX_RULES.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | 運用ルール変更として 1 commit |
| Stop | docs 以外の編集が必要、old runtime repo access が必要、push/pull/runtime action が必要、trading logic 変更が必要、test 失敗、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-MANUAL-SURFACE-EVIDENCE-SUMMARY`
- Goal: expose the evidence-quality summaries on the manual trading surface without changing trading logic.
