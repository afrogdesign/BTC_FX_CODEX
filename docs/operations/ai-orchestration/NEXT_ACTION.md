# NEXT_ACTION

- current_work_id: `BTCFX-20260630-LIGHTWEIGHT-ORCHESTRATION-RULES`
- mode: `LIGHT_CODEX`

## Current goal

MCP 正本運用に合わせて、Codex のプロンプトと記録を軽量化する。

## Current summary

| Field | Value |
|---|---|
| Read | `docs/operations/ai-orchestration/MINI_CODEX_RULES.md`, `docs/operations/ai-orchestration/PROMPT_PREFLIGHT_CHECKLIST.md`, `docs/operations/ai-orchestration/CURRENT_STATE.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Edit | `docs/operations/ai-orchestration/MINI_CODEX_RULES.md`, `docs/operations/ai-orchestration/PROMPT_PREFLIGHT_CHECKLIST.md`, `docs/operations/ai-orchestration/CURRENT_STATE.md`, `docs/operations/ai-orchestration/NEXT_ACTION.md` |
| Do | lightweight orchestration の方針を短く同期する |
| Tests | `git diff --check -- docs/operations/ai-orchestration/MINI_CODEX_RULES.md docs/operations/ai-orchestration/PROMPT_PREFLIGHT_CHECKLIST.md docs/operations/ai-orchestration/CURRENT_STATE.md docs/operations/ai-orchestration/NEXT_ACTION.md`, `git diff --name-only`, `git status --short --branch`, staged diff checks |
| Commit policy | docs の軽量運用方針を人間に残す状態変更として 1 commit |
| Stop | docs 以外の編集が必要、old runtime repo access が必要、push/pull/runtime action が必要、trading logic 変更が必要、テスト失敗、allowed 外 file が stage される |

## Next recommended follow-up

- `BTCFX-20260630-CANDIDATE-TYPE-SIDE-BREAKDOWN`
- Goal: resume evidence-quality implementation with compact diff-based Codex prompts.
