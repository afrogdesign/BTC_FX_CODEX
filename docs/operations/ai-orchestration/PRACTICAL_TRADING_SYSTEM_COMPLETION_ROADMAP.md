# PRACTICAL_TRADING_SYSTEM_COMPLETION_ROADMAP

## Purpose

MCP-primary の実運用を前提に、手動取引 surface から evidence 品質、handoff、将来の自動化までを短く整理する。

## Current completion status

- orchestration baseline: complete
- MCP-primary workflow: complete
- dashboard parity: complete
- checkpoint push: reported complete
- runtime repo reflection: not complete
- evidence / intraperiod / win-rate diagnostics: next product-quality phase
- semi-automatic approval path: not started
- automatic trading readiness: not started

## Completion phases

### Phase A: operation and orchestration baseline

- status: complete
- purpose: MCP-primary で安全に回る最小運用を固定する。
- required next evidence or gate: current docs alignment と checkpoint push report.

### Phase B: manual-trading surfaces

- status: complete
- purpose: public HTML / notification mail / local dashboard を同一判断ソースで揃える。
- required next evidence or gate: surface parity と report-only safety の明示。

### Phase C: runtime handoff

- status: not complete
- purpose: checkpoint push の反映可否を runtime repo 側でレビューする。
- required next evidence or gate: pull 対象 branch と確認手順の明示レビュー。

### Phase D: evidence / intraperiod / win-rate diagnostics

- status: next
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

1. `BTCFX-20260630-RUNTIME-PULL-HANDOFF-REVIEW`
   - Goal: old runtime execution repo が checkpoint pull を受けるべきかをレビューする。
   - Stop condition: pull, runtime restart, notification sending, trading actions を実行しない状態で結論を整理したら止める。
2. `BTCFX-20260630-RUNTIME-PULL-HANDOFF-PLAN`
   - Goal: pull handoff の手順、対象、確認点を task 単位で整える。
   - Stop condition: 実行を伴わない計画文書がまとまったら止める。
3. `BTCFX-20260630-EVIDENCE-ACCURACY-RESUME`
   - Goal: evidence と accuracy の診断再開点を整理する。
   - Stop condition: 再開に必要な evidence だけを特定できたら止める。
4. `BTCFX-20260630-INTRAPERIOD-WINRATE-DIAGNOSTIC-PASS`
   - Goal: intraperiod, win-rate, expectancy の診断観点を順に確認する。
   - Stop condition: 診断観点と必要データが揃った時点で止める。
5. `BTCFX-20260630-MANUAL-SURFACE-QUALITY-BACKLOG`
   - Goal: manual surface の品質改善 backlog を evidence 優先で並べる。
   - Stop condition: 取引ロジック変更を含めず、優先度付き backlog ができたら止める。

## Safety boundaries

- report-only
- not `FORMAL_GO`
- no automatic order
- no API keys
- no private/account/order endpoints
- human decides manually

## What is not complete yet

- system is not an automatic trading system yet
- runtime repo has not been updated from the checkpoint yet
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
