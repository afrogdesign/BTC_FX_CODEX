# START_HERE

新しい ChatGPT / Codex / future AI agent は、まずこのファイルから読み始めます。

## Repo doctrine

| Label | Path | Rule |
|---|---|---|
| MCP/Codex primary working repo | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` | 通常の read / edit / test / git はここで行う |
| Frozen old runtime execution repo | `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` | 今回の通常 orchestration task では edit/run しない |

- runtime execution repo は current editing target ではない
- runtime execution repo への反映は、MCP working repo で clean checkpoint branch/push を作ったあとに GitHub pull で行う
- ChatGPT は AFROG_MCP を primary repo inspection path として使う
- GitHub は checkpoint / history / sync 用であり、毎回の review の default read path ではない
- Codex は明示指示がない限り MCP working repo だけを編集する
- normal Codex task は local edit + local commit + compact report が基本
- push は `CHECKPOINT_PUSH` task だけで行う
- routine push は wasteful なので通常 task で要求しない

## Default avoid list

- `.venv312/`
- `logs/`
- generated CSV / report / HTML
- `docs/operations/ai-orchestration/TASK_LEDGER.md` 全文

必要な task で明示されたときだけ開くこと。

## Fixed low-cost read order

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`
3. `docs/operations/ai-orchestration/RESUME.md`
4. `docs/operations/ai-orchestration/CURRENT_STATE.md`
5. `docs/operations/ai-orchestration/NEXT_ACTION.md`
6. `docs/operations/ai-orchestration/CONTROL.md`
7. `docs/operations/ai-orchestration/PROMPTS.md`
8. `docs/operations/ai-orchestration/CHECKPOINT_RUNBOOK.md` when checkpoint design matters
9. `docs/operations/ai-orchestration/RUNTIME_PULL_HANDOFF.md` when runtime pull handoff matters
10. `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md`
11. `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md` when direction matters
12. `docs/operations/ai-orchestration/TASK_LEDGER.md` only as needed, latest rows only
13. `docs/operations/ai-orchestration/MINI_CODEX_RULES.md` when Codex is used
14. `docs/operations/ai-orchestration/PROMPT_PREFLIGHT_CHECKLIST.md` when ChatGPT is preparing a Codex prompt

## Quick rules

- repo正本は repo-local docs を優先し、chat history だけで判断しない
- current branch は `git status --short --branch` と `CONTROL.md` から読む
- runtime execution repo を通常 task で読みに行かない、走らせない、編集しない
- runtime execution repo への変更反映は checkpoint branch/push と GitHub pull のあとで行う
- 通常 work は push しない、runtime repo も触らない
- product behavior, trading logic, runtime behavior を変える前に explicit task scope を確認する
- Codex 5.4-mini medium には小さく機械的な task を渡す
- ChatGPT が scope を決めてから Codex を開始する
- ChatGPT は Codex prompt の前に preflight を通す
