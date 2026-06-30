# AI Orchestration

新しい agent は最初に `START_HERE.md` を読みます。

## Purpose

- ChatGPT / Codex / future agents の resume cost を下げる
- MCP primary workflow で repo confusion を防ぐ

## Two repo paths

| Label | Path | Use |
|---|---|---|
| MCP primary working repo | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` | 通常の inspection / edit / test / git |
| Old runtime execution repo | `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` | 後で GitHub pull 反映する実行側 |

- runtime execution repo は current editing target ではない
- GitHub は checkpoint / history / sync 用であり、毎回の default read path ではない
- GitHub push は meaningful checkpoint branch のときだけ行う
- routine push は wasteful なので default では要求しない
- old runtime repo への反映は checkpoint push 後の GitHub pull later で行う

## Roles

- ChatGPT: commander, planning, review
- Codex: fixed-scope edit, validation, compact reporting

## First files

1. `START_HERE.md`
2. `RESUME.md`
3. `CURRENT_STATE.md`
4. `NEXT_ACTION.md`
5. `CONTROL.md`

## Default operation

- MCP primary
- local edit / local validation / local commit
- `PUSH: none` for normal tasks
- checkpoint push only
- avoid `.venv312/`, logs, generated files, and full `TASK_LEDGER.md` by default

## Core files

| File | Role |
|---|---|
| `START_HERE.md` | first-read entrypoint |
| `CURRENT_STATE.md` | short current operating state |
| `NEXT_ACTION.md` | current task frame and recommended next follow-up |
| `CONTROL.md` | current objective, constraints, validation, next decision |
| `TASK_LEDGER.md` | work ledger, read only as needed |
| `REPO_MAP.md` | repo reading map |
| `PROMPTS.md` | prompt templates |
| `handoffs/CURRENT_HANDOFF.md` | active handoff anchor |

## Rule

長い履歴を prompt に詰め込まず、repo-local docs を source of truth に使う。
