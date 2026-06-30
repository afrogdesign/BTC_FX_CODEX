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

1. `BTCFX-20260630-NO-OHLCV-COVERAGE-DIAGNOSTIC`
   - Goal: no_ohlcv が支配的な理由を見つけ、valid sample の分母を明確にする。
   - Stop condition: report-only で no_ohlcv 率の扱いが固定されたら止める。
2. `BTCFX-20260630-VALID-SAMPLE-WINRATE-REPORT`
   - Goal: valid sample に限定した win-rate report を整える。
   - Stop condition: no_ohlcv 除外の分母が明示されたら止める。
3. `BTCFX-20260630-ENTRY-REACHED-OUTCOME-BREAKDOWN`
   - Goal: entry-reached subset の outcome 分布を整理する。
   - Stop condition: entry 後の outcome 分布が report-only で見えるようになったら止める。
4. `BTCFX-20260630-CANDIDATE-TYPE-SIDE-BREAKDOWN`
   - Goal: candidate_type / side / active_primary_action の分布を揃える。
   - Stop condition: 3 軸の breakdown が一致した基準で出たら止める。
5. `BTCFX-20260630-MAJOR-TURN-CANDIDATE-REVIEW`
   - Goal: potential_fakeout / potential_missed_turn / bad_entry_timing を review-only で整理する。
   - Stop condition: human review 用の候補一覧が揃ったら止める。

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
