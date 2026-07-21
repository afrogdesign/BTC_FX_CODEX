# Ver04-v1 Integrated Product Plan

## Metadata

- repo: `afrogdesign/BTC_FX_CODEX`
- working_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- active_branch: `Ver04-v1`
- prior_baseline: `Ver03-v4`
- status: active high-level product plan for the Ver04-v1 branch
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

## Purpose

Ver04-v1 は、notification mail を受け取った人間が 15分足を確認し、攻めの姿勢で勝てる manual trading support system を作るための新しい product direction である。

Ver03-v4 は prior baseline / history として保持し、Ver04-v1 を active branch として進める。

## Product direction

```text
notification mail -> 15m chart check -> aggressive-but-controlled human trading support
```

狙いは、自動売買ではなく、人間の manual decision を支えること。

この branch では次を重視する。

- mail は triage / entry point
- public HTML / notification mail / local dashboard は single-source doctrine を共有する
- daily proxy / weekly review / biweekly actual trade ground truth の self-improvement loop を回す
- automatic trading は later-stage only

## Source of truth

今後の product / evaluation / implementation 判断は次の順で読む。

1. `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
2. `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
3. `docs/operations/ai-orchestration/MILESTONES.md`
4. `docs/operations/ai-orchestration/NEXT_ACTION.md`

## Implementation route

### Phase V1-1: Post-eval asset health audit

First Ver04-v1 implementation task.

- audit existing post-evaluation assets
- identify reusable inputs for deterministic daily proxy evaluation
- keep it read-only / docs-only

### Phase V1-2: Daily proxy evaluator

- generate daily proxy report without actual-trade import
- evaluate mail usefulness / direction / over-suppression / turning risk

### Phase V1-3: Manual actual trade import schema

- accept periodic futures Excel export as local import
- keep raw export local only

### Phase V1-4: Actual trade to signal linking

- link actual trade to notification / signal / mail events
- track confidence

### Phase V1-5: Biweekly ground truth report

- compare proxy with actual human trade results
- calibrate the loop

### Phase V1-6: Recommendation engine

- rank improvement candidates from evidence

### Phase V1-7: Surface integration

- expose post-eval status on public HTML / mail / dashboard in report-only form

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- no private/account/order endpoints
- no runtime restart during normal product work
- no raw exchange export commit
- no `paper_positions.csv` integration unless explicitly approved
- human decides manually
