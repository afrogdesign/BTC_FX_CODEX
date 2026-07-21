# AI Orchestration

新しい ChatGPT / Codex / future AI agent は最初に `START_HERE.md` を読みます。

## Purpose

- ChatGPT / Codex / future agents のresume costを下げる
- MCP primary workflowでrepo confusionを防ぐ
- manual trading practicality routeを段階実行する
- planning、active spec、implementation、human approvalを混同しない

## Two repo paths

| Label | Path | Use |
|---|---|---|
| MCP primary working repo | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` | 通常のinspection / edit / test / git |
| Frozen old runtime execution repo | `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` | 通常taskではread/edit/runしない |

- frozen old runtime repoはcurrent editing targetではない。
- GitHubはcheckpoint / history / sync用。
- routine pushはdefaultでは要求しない。
- runtime変更は明示taskだけで行う。

## Current product objective

```text
notification mail を受け取った人間が、
15分足を確認し、
攻めの姿勢で勝てる manual trading support system を作る。
```

Automatic trading is later-stage only.

## Current practicality route

```text
A_FORMAL
B_CHECK_15M
C_WATCH_ZONE
STOP_OR_EXIT
```

この4分類はoperator action layerであり、既存gateの置換ではない。

- strict A candidate qualityを維持する
- Bで人間が15分足確認できる候補を増やす
- Cで未到達scenarioを監視する
- STOPで新規停止・利確・撤退を支援する
- candidate rowをscenarioへ圧縮する
- actual trade ground truthで評価を補正する

## Roles

- ChatGPT: commander, planning, review, scope selection, active spec design, Codex prompt creation
- Codex: fixed-scope implementation, validation, local commit, compact reporting
- Human: production threshold / gate / notification / runtime / live behavior approval

## Active anchors

- `START_HERE.md`
- `CURRENT_STATE.md`
- `NEXT_ACTION.md`
- `CONTROL.md`
- `PRODUCT_IMPLEMENTATION_ROUTE.md`
- `MANUAL_TRADING_PRACTICALITY_EXECUTION_ROUTE_20260710.md`
- `../strategy/MANUAL_TRADING_PRACTICALITY_IMPROVEMENT_PLAN_20260710.md`
- `MILESTONES.md`

## Product source-of-truth files

| File | Role |
|---|---|
| `PRODUCT_IMPLEMENTATION_ROUTE.md` | active product route |
| `MANUAL_TRADING_PRACTICALITY_EXECUTION_ROUTE_20260710.md` | AI phase execution and anti-skip rules |
| `../strategy/MANUAL_TRADING_PRACTICALITY_IMPROVEMENT_PLAN_20260710.md` | detailed architecture review and improvement plan |
| `../strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md` | daily/weekly/biweekly evaluation loop |
| `../strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md` | manual decision success definition |
| `PHASE4_SELF_IMPROVEMENT_CONTROL_PLAN_20260707.md` | observation / cue / approval gate |

## Current posture and next task

- runtime/product observation continues
- Phase4 tuning remains blocked
- planning route is approved
- production tuning is not approved
- current exact next task: `BTCFX-20260710-MTP-ACTUAL-TRADE-IMPORT-SPEC`
- next task is active-spec creation only
- importer implementation begins only after spec review

## Phase sequence

```text
P1 importer active spec
→ P2 importer implementation
→ P3 trade-to-signal/scenario linking
→ P4 coverage and scenario normalization
→ P5 offline A/B/C/STOP classifier
→ P6 historical replay
→ P7 shadow surface
→ P8 human manual trial
→ P9 evidence-backed tuning review
```

Do not skip or merge phases without explicit redesign approval.

## Historical / non-default files

- `TASK_LEDGER.md` is historical/specific lookup only
- `handoffs/CURRENT_HANDOFF.md` is handoff-only
- `PRACTICAL_TRADING_SYSTEM_COMPLETION_ROADMAP.md` is an older evidence-phase roadmap and is not the current practicality execution route
- older task notes are not current source of truth unless explicitly named

## Default operation

- MCP primary
- local edit / local validation / local commit
- checkpoint push only
- avoid `.venv312/`, logs, generated files, raw exchange exports, and full `TASK_LEDGER.md` by default
- active spec is required before source implementation

## Hard safety rules

- no automatic order
- no API keys or secrets
- no private/account/order endpoints
- no raw exchange export commit
- no `paper_positions.csv` mixing
- no gate relaxation without explicit human approval
- no tuning from single examples
- no unresolved/no_ohlcv win-loss claims

## Rule

長い履歴をpromptへ詰め込まず、repo-local source-of-truth docsを使う。
