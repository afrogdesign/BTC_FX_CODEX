# PRACTICAL_TRADING_SYSTEM_COMPLETION_ROADMAP

status: historical / superseded as active execution route
last_reviewed: 2026-07-10

## Current source of truth

この文書は、2026-06-30時点のevidence-quality phaseを整理した旧ロードマップである。

現在のmanual trading practicality作業では、次を正本とする。

1. `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
2. `docs/operations/ai-orchestration/MANUAL_TRADING_PRACTICALITY_EXECUTION_ROUTE_20260710.md`
3. `docs/operations/strategy/MANUAL_TRADING_PRACTICALITY_IMPROVEMENT_PLAN_20260710.md`
4. `docs/operations/ai-orchestration/NEXT_ACTION.md`

この文書に残っていた旧`Next 5 recommended tasks`は、すでに後続のevidence / OHLCV / self-review作業へ展開されているため、current next taskとして使わない。

## Historical purpose

MCP-primaryの実運用を前提に、手動取引surface、evidence品質、handoff、将来の自動化までを段階化した。

## Historical phase summary

### Phase A: operation and orchestration baseline

- status: complete
- MCP-primaryで安全に回る最小運用を固定した。

### Phase B: manual-trading surfaces

- status: complete
- public HTML / notification mail / local dashboardのsingle-source方針を整えた。

### Phase C: source-of-truth consolidation

- status: complete
- MCP repoをcurrent source of truthとして整理した。

### Phase D: evidence / intraperiod / win-rate diagnostics

- status: evolved into current self-review and practicality route
- no_ohlcv、valid sample、entry outcome、candidate side breakdownを扱った。

### Phase E: semi-automatic approval path

- status: not approved
- current practicality routeではmanual human decisionを維持する。

### Phase F: automatic trading readiness

- status: not started
- explicit `FORMAL_GO`と別承認が必要。

## Current replacement phase sequence

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

## Current safety boundaries

- report-only
- not `FORMAL_GO`
- no automatic order
- no API keys
- no private/account/order endpoints
- no raw export commit
- no gate relaxation without human approval
- human decides manually

## Historical value

この文書は、evidence-quality phaseへ移行した経緯の参照として保持する。

future AIは、この文書からnext taskを決めず、`START_HERE.md`と`NEXT_ACTION.md`を使う。
