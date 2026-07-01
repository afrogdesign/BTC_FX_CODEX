# VER04-v1 Implementation Readiness Package

## Purpose

この文書は、この thread の環境準備フェーズを閉じ、次の implementation thread が clean に開始できるようにする readiness package である。

ここでは実装を進めず、次に何を実装するかを迷わない程度に具体化する。

## Active objective

```text
notification mail -> human checks 15m chart -> aggressive-but-controlled manual trading support
```

automatic trading は later-stage only であり、今は対象外。

## Completed components

- Ver04-v1 branch / product route baseline を整備済み
- post-eval asset health audit を完了済み
- Daily Proxy Evaluator を実装済み

Daily Proxy Evaluator の既存出力と入口は次のとおり。

- output: `運用資料/reports/post_eval/daily_proxy_evaluator_YYYYMMDD.md`
- CLI: `build-daily-proxy-evaluator-report`
- safety: `proxy-only / not FORMAL_GO / no automatic order / no private/account/order endpoints / human decides manually`

## Current source of truth

次の docs を active source-of-truth とする。

- `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
- `docs/operations/ai-orchestration/POST_EVAL_ASSET_HEALTH_AUDIT_20260702.md`
- `docs/operations/strategy/VER04_V1_INTEGRATED_PRODUCT_PLAN.md`
- `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
- `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`

## MEXC export design input

MEXC actual trade exports の raw input path は当面次のローカル領域で扱う。

- raw path: `docs/mexc_csv/`

Observed file categories:

- Futures Order History xlsx
- Futures Position History xlsx
- Futures Trade History xlsx

Observed sheet structure:

- each workbook has `Sheet1`

Observed header categories:

- Order History: UID, 時間(UTC+09:00), 先物取引ペア, 方向, レバレッジ, 注文の種類, 約定数量, 平均約定価格, 決済損益, 手数料, ステータス
- Position History: UID, 取引ペア, オープン時間(UTC+09:00), 決済時刻, 方向, 実現損益, ステータス
- Trade History: UID, 時間(UTC+09:00), 先物取引ペア, 方向, 注文の種類, 約定価格, 取引手数料, 役割, 決済損益

Raw exports are private/local/generated inputs. They must not be committed.

## MEXC normalized output design

Canonical normalized outputs for later implementation are:

- `logs/csv/manual_actual_trades.csv`
- `logs/csv/manual_actual_orders.csv`
- `logs/csv/manual_actual_positions.csv`
- `logs/csv/manual_trade_signal_links.csv`

Policy:

- do not mix actual human trades into `paper_positions.csv`
- keep raw exports local only
- normalize into generated CSVs before linking or reporting

## Proposed next implementation task

- Work ID: `BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER`
- Scope:
  - local xlsx importer only
  - no API
  - no secrets
  - no private/account/order endpoints
  - no order execution
  - normalize MEXC xlsx to local generated CSVs
  - add tests with small synthetic fixtures, not raw exports

## After importer, next sequence

1. actual trade to signal linker
2. biweekly ground truth report
3. proxy-vs-actual calibration
4. recommendation engine
5. surface integration

## Files likely to touch in next thread

- `tools/log_feedback.py`
- `tests/test_mexc_actual_trade_importer.py`
- `docs/operations/ai-orchestration/NEXT_ACTION.md`

No runtime/deploy/source trading logic files unless explicitly approved.

## New-thread start instructions

- read `START_HERE.md`, `RESUME.md`, `CURRENT_STATE.md`, `CONTROL.md`, `PRODUCT_IMPLEMENTATION_ROUTE.md`, and this readiness package first
- verify branch `Ver04-v1`
- do not use the old runtime repo
- do not commit raw MEXC exports
