# AI Orchestration

新しい ChatGPT / Codex / future AI agent は最初に `START_HERE.md` を読みます。

## Purpose

- ChatGPT / Codex / future agents の resume cost を下げる
- MCP primary workflow で repo confusion を防ぐ
- Ver04-v1 product implementation が迷子にならないように、source-of-truth route を固定する

## Two repo paths

| Label | Path | Use |
|---|---|---|
| MCP primary working repo | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` | 通常の inspection / edit / test / git |
| Frozen old runtime execution repo | `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` | frozen execution side; manual GitHub pull later at clean checkpoints only |

- frozen old runtime repo は current editing target ではない。
- GitHub は checkpoint / history / sync 用であり、毎回の default read path ではない。
- GitHub push は meaningful checkpoint branch のときだけ行う。
- routine push は wasteful なので default では要求しない。
- frozen old runtime repo への反映は checkpoint push 後の GitHub pull later で行う。

## Current product objective

```text
notification mail を受け取った人間が、
15分足を確認し、
攻めの姿勢で勝てる manual trading support system を作る。
```

Automatic trading is later-stage only.

## Roles

- ChatGPT: commander, planning, review, scope selection, Codex prompt creation
- Codex: fixed-scope edit, validation, local commit, compact reporting

## First files

1. `START_HERE.md`
2. `RESUME.md`
3. `CURRENT_STATE.md`
4. `NEXT_ACTION.md`
5. `CONTROL.md`
6. `PRODUCT_IMPLEMENTATION_ROUTE.md`

## Product source-of-truth files

| File | Role |
|---|---|
| `PRODUCT_IMPLEMENTATION_ROUTE.md` | active product route and next implementation sequence |
| `../strategy/VER04_V1_INTEGRATED_PRODUCT_PLAN.md` | high-level Ver04-v1 plan |
| `../strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md` | final self-improvement loop design |
| `../strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md` | definition of “manual 15m win” |

## Default next implementation route

Unless the user overrides it, the next implementation route starts with:

```text
BTCFX-20260702-POST-EVAL-ASSET-HEALTH-AUDIT
```

This is a read-only / docs-only audit before implementing evaluator code.

## Default operation

- MCP primary
- local edit / local validation / local commit
- `PUSH: none` for normal tasks
- checkpoint push only
- avoid `.venv312/`, logs, generated files, raw exchange exports, and full `TASK_LEDGER.md` by default

## Core orchestration files

| File | Role |
|---|---|
| `START_HERE.md` | first-read entrypoint |
| `RESUME.md` | restart protocol and current product guard |
| `CURRENT_STATE.md` | short current operating state |
| `NEXT_ACTION.md` | current narrow task frame |
| `CONTROL.md` | current objective, constraints, validation, next decision |
| `PRODUCT_IMPLEMENTATION_ROUTE.md` | product route for future AI work |
| `MILESTONES.md` | durable accepted history |
| `TASK_LEDGER.md` | work ledger, read only as needed |
| `REPO_MAP.md` | repo reading map |
| `PROMPTS.md` | prompt templates |
| `handoffs/CURRENT_HANDOFF.md` | active handoff anchor |

## Rule

長い履歴を prompt に詰め込まず、repo-local docs を source of truth に使う。
