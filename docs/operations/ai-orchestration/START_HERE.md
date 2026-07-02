# START_HERE

新しい ChatGPT / Codex / future AI agent は、まずこのファイルから読み始めます。

## Repo doctrine

| Label | Path | Rule |
|---|---|---|
| MCP/Codex primary working repo | `/Users/marupro/CODEX/100_MCP_Server/btc_monitor` | 通常の read / edit / test / git はここで行う |
| Frozen old runtime execution repo | `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` | 通常 orchestration / product task では edit/run/inspect しない |

- runtime execution repo は current editing target ではない。
- runtime execution repo への反映は、MCP working repo で clean checkpoint branch/push を作ったあとに GitHub pull で行う。
- ChatGPT は AFROG_MCP_Business を primary repo inspection path として使う。会話内では `AFROG_MCP` と呼ぶ。
- GitHub は checkpoint / history / sync 用であり、毎回の review の default read path ではない。
- Codex は明示指示がない限り MCP working repo だけを編集する。
- normal Codex task は local edit + local validation + local commit + compact report が基本。
- push は `CHECKPOINT_PUSH` task だけで行う。
- routine push は wasteful なので通常 task で要求しない。

## Current product objective

現時点の最優先目的は、自動売買ではない。

```text
notification mail を受け取った人間が、
15分足を確認し、
攻めの姿勢で勝てる manual trading support system を作る。
```

Ver03-v4 は prior baseline / history、Ver04-v1 が active product branch です。

## Tiered read order

### Tier 0 / always

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`

### Tier 1 / state needed

1. `docs/operations/ai-orchestration/CURRENT_STATE.md`
2. `docs/operations/ai-orchestration/NEXT_ACTION.md`
3. `docs/operations/ai-orchestration/CONTROL.md`

### Tier 2 / by task type only

- product route:
  - `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
  - `docs/operations/strategy/VER04_V1_INTEGRATED_PRODUCT_PLAN.md`
  - `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
  - `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
- Codex prompt work:
  - `docs/operations/ai-orchestration/PROMPTS.md`
  - `docs/operations/ai-orchestration/MINI_CODEX_RULES.md`
  - `docs/operations/ai-orchestration/PROMPT_PREFLIGHT_CHECKLIST.md`
- checkpoint:
  - `docs/operations/ai-orchestration/CHECKPOINT_RUNBOOK.md`
- runtime pull handoff:
  - `docs/operations/ai-orchestration/RUNTIME_PULL_HANDOFF.md`
- accepted history:
  - `docs/operations/ai-orchestration/MILESTONES.md`
- handoff only:
  - `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md`
- specific historical lookup only:
  - `docs/operations/ai-orchestration/TASK_LEDGER.md` by search / latest rows only

`TASK_LEDGER.md` と `handoffs/CURRENT_HANDOFF.md` は default startup read ではない。
`docs/operations/ai-orchestration/` 直下の historical task notes は、task で明示されたときだけ読む。

## Product source-of-truth shortcut

When the task is about product direction, post-evaluation, manual trading support, mail wording, long/short opportunity display, or actual trade import, read in this order:

1. `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
2. `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
3. `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
4. `docs/operations/strategy/VER04_V1_INTEGRATED_PRODUCT_PLAN.md`

## Default avoid list

- `.venv312/`
- `logs/`
- generated CSV / report / HTML
- raw exchange exports under `local/manual_trade_imports/`
- full `docs/operations/ai-orchestration/TASK_LEDGER.md`
- historical task notes in `docs/operations/ai-orchestration/` root unless explicitly named

必要な task で明示されたときだけ開くこと。

## Quick rules

- repo正本は repo-local docs を優先し、chat history だけで判断しない。
- current branch は `git status --short --branch` と `CONTROL.md` から読む。
- runtime execution repo を通常 task で読みに行かない、走らせない、編集しない。
- 通常 work は push しない、runtime repo も触らない。
- raw exchange exports は commit しない。
- `paper_positions.csv` と actual human trades を明示許可なく混ぜない。
- product behavior, trading logic, runtime behavior を変える前に explicit task scope を確認する。
- Codex には scope 固定済みの小さく機械的な task を渡す。
- ChatGPT が scope を決めてから Codex を開始する。
- ChatGPT は Codex prompt の前に preflight を通す。
