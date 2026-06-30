# PRACTICAL_TRADING_SYSTEM_COMPLETION_ROADMAP

## Purpose

MCP-primary の実運用を前提に、手動取引 surface から evidence 品質、handoff、将来の自動化までを短く整理する。

## Current completion status

- orchestration baseline: complete
- MCP-primary workflow: complete
- dashboard parity: complete
- checkpoint push: reported complete
- source-of-truth consolidation: complete
- runtime repo reflection: not required unless explicitly reopened
- evidence / intraperiod / win-rate diagnostics: current
- semi-automatic approval path: not started
- automatic trading readiness: not started

practical trading system is now in the evidence-quality phase.

## Completion phases

### Phase A: operation and orchestration baseline

- status: complete
- purpose: MCP-primary で安全に回る最小運用を固定する。
- required next evidence or gate: current docs alignment と checkpoint push report.

### Phase B: manual-trading surfaces

- status: complete
- purpose: public HTML / notification mail / local dashboard を同一判断ソースで揃える。
- required next evidence or gate: surface parity と report-only safety の明示。

### Phase C: source-of-truth consolidation

- status: complete
- purpose: MCP repo が current source of truth であり、old runtime pull handoff が不要であることを確認する。
- required next evidence or gate: source-of-truth 宣言と runtime pull handoff closed の記録。

### Phase D: evidence / intraperiod / win-rate diagnostics

- status: current
- purpose: 実運用データから entry, timeout, TP/SL, expectancy を評価する。
- required next evidence or gate: intraperiod evidence と win-rate diagnostics の再開。

### Phase E: semi-automatic approval path

- status: not started
- purpose: human review 前提の承認補助を検討する。
- required next evidence or gate: explicit safety design と承認基準。

### Phase F: automatic trading readiness

- status: not started
- purpose: automatic trading の可否を別途厳格に判断する。
- required next evidence or gate: proven metrics, explicit `FORMAL_GO`, separate approval.

## Phase acceptance gates

- no separate decision path
- report-only safety remains visible
- public HTML / mail / dashboard stay aligned
- runtime pull is reviewed before execution
- no private/account/order endpoints before explicit safety design
- automatic trading requires explicit `FORMAL_GO` and separate approval

## Next 5 recommended tasks

1. `BTCFX-20260630-EVIDENCE-ACCURACY-RESUME`
   - Goal: evidence baseline を確認し、診断再開に必要な入口を整える。
   - Stop condition: current source of truth と既存 evidence を整理できたら止める。
2. `BTCFX-20260630-INTRAPERIOD-WINRATE-DIAGNOSTIC-PASS`
   - Goal: intraperiod outcome reports から次に必要な metrics と tests を特定する。
   - Stop condition: 変更せずに、次の診断項目が明確になったら止める。
3. `BTCFX-20260630-EVIDENCE-QUALITY-BACKLOG`
   - Goal: evidence 品質の改善 backlog を優先順に並べる。
   - Stop condition: trading logic を変えずに優先度付き backlog ができたら止める。
4. `BTCFX-20260630-MANUAL-SURFACE-QUALITY-BACKLOG`
   - Goal: manual surface の品質改善 backlog を evidence 優先で並べる。
   - Stop condition: 手動 surface の改善項目が evidence ベースで整理できたら止める。
5. `BTCFX-20260630-SEMI-AUTO-APPROVAL-READINESS-REVIEW`
   - Goal: semi-automatic approval path の前提条件を review-only で確認する。
   - Stop condition: explicit safety gap と未解決の前提を一覧化したら止める。

## Safety boundaries

- report-only
- not `FORMAL_GO`
- no automatic order
- no API keys
- no private/account/order endpoints
- human decides manually

## What is not complete yet

- system is not an automatic trading system yet
- runtime repo reflection is not required unless explicitly reopened
- no live/private/order endpoint work is approved
- win-rate / expectancy improvement is not complete
- evidence-based tuning is the next major product work

## Mini Codex task-shaping notes

- prefer 1 to 3 edit files
- explicit read/edit/do-not-edit lists
- no broad repo exploration
- no product judgment delegated to Codex
- all runtime/pull/push tasks must be explicit
- validation at task end
- compact report to `response.txt` exactly once
