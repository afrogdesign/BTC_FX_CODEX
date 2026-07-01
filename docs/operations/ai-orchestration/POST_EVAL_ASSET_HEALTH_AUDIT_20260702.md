# POST_EVAL_ASSET_HEALTH_AUDIT_20260702

## Purpose

Ver04-v1 の first implementation step に入る前に、既存の事後評価資産を棚卸しし、Daily Proxy Loop / Weekly Review Loop / Biweekly Ground Truth Loop に何を使うかを固定する。

目的は manual trading support を強くすることであり、自動売買ではない。

```text
notification mail -> 15m human decision -> aggressive-but-controlled manual trading support
```

## Asset inventory

### Existing CSVs

- `logs/csv/user_reviews.csv`
- `logs/csv/signal_outcomes.csv`
- `logs/csv/active_plan_candidate_outcomes.csv`
- `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`

### Runtime / AI post review logs

- `logs/runtime/ai_post_reviews.out`
- `logs/runtime/feedback_daily_sync.out`
- `config.py` に AI post review 専用キーは見つからなかった

### Daily reports

- `運用資料/reports/feedback_daily_sync_20260702.md`
- `運用資料/reports/feedback_daily_sync_20260701.md`
- `運用資料/reports/feedback_daily_sync_20260630.md`

### MEXC export path

- `docs/mexc_csv/`
- present files:
  - `Futures-Futures Order History-2026-01-02-2026-07-02.xlsx`
  - `Futures-Futures Position History-2026-01-02-2026-07-02.xlsx`
  - `Futures-Futures Trade History-2026-01-02-2026-07-02.xlsx`

## Daily Proxy Loop inputs

Now available:

- `signal_outcomes.csv`
  - signal-level direction / entry / wait / skip / outcome trends
  - useful for regime drift and prelabel balance
- `active_plan_candidate_outcomes.csv`
  - candidate-level outcome and subject/side analysis
  - useful for candidate type / side / action breakdowns
- `active_plan_candidate_intraperiod_outcomes.csv`
  - intraperiod TP1 / TP2 / SL / timeout / MFE / MAE diagnostics
  - useful for entry-quality and turning-point calibration
- `user_reviews.csv`
  - human verdict / usefulness / memo / actual move driver
  - useful as qualitative enrichment and bias checks
- `feedback_daily_sync_*.md`
  - daily rollups, AI health, improvement candidates, and trend summaries
  - useful for human-readable proxy summaries

Limitations:

- these are report-only / proxy inputs
- denominators must be stated explicitly
- they do not equal actual human trade ground truth
- `logs/runtime/*` are operational history, not canonical evaluation inputs

## Weekly Review Loop inputs

Weekly summaries can be built from:

- weekly aggregation of `signal_outcomes.csv`
- weekly aggregation of `active_plan_candidate_outcomes.csv`
- weekly aggregation of `active_plan_candidate_intraperiod_outcomes.csv`
- weekly slices of `user_reviews.csv`
- weekly slices of `feedback_daily_sync_*.md`
- AI post review health trend from `logs/runtime/ai_post_reviews.out`

Use cases:

- short / long bias drift
- direction mismatch drift
- watch / skip / over-suppression drift
- turning-risk candidates
- candidate-type and side imbalance

Limitations:

- still proxy-level, not actual trade ground truth
- summarize only what the existing labels and report assets already encode

## Biweekly Ground Truth Loop inputs

### MEXC export path and categories

The user-provided MEXC delivery path is:

- `docs/mexc_csv/`

Workbook categories already available there:

- Order History
- Position History
- Trade History

Observed workbook schema only:

- Order History headers include UID, time, pair, side, leverage, order type, quantities, prices, pnl, fee, status
- Position History headers include UID, pair, open/close times, margin mode, average prices, side, size, fee, realized pnl, status
- Trade History headers include UID, time, pair, side, order type, fill quantities, fill price, fee, role, pnl

### Expected normalized outputs

- `logs/csv/manual_actual_trades.csv`
- `logs/csv/manual_actual_orders.csv`
- `logs/csv/manual_actual_positions.csv`
- `logs/csv/manual_trade_signal_links.csv`

### Privacy / local / generated policy

- raw MEXC exports stay local/generated
- raw exports are not committed
- actual human trades must not be mixed into `paper_positions.csv`
- normalized outputs are later-stage local artifacts unless explicitly documented otherwise

### Recommended future local import path

- `local/manual_trade_imports/YYYYMMDD/`

## MEXC export handling design

Recommended mapping:

- Trade History -> `manual_actual_trades.csv`
- Order History -> `manual_actual_orders.csv`
- Position History -> `manual_actual_positions.csv`
- linking / join output -> `manual_trade_signal_links.csv`

Design notes:

- preserve timestamps and source identifiers locally
- mask or hash sensitive identifiers when needed
- keep raw export as read-only sample input for schema design
- use the normalized outputs for later biweekly calibration

## AI post review status

### What exists

- `tools/run_ai_post_reviews.sh` is a thin wrapper around `tools/log_feedback.py sync-ai-post-reviews`
- `deploy/com.afrog.btc-ai-post-reviews.plist` runs on the canonical repo path
- `feedback_daily_sync_20260702.md` still records AI post review health and improvement candidates
- `config.py` search did not surface dedicated AI post review keys

### What is reusable

- qualitative enrichment for operator context
- review-note / review-form workflow support
- history of backlog size and failure state

### What is stale or risky

- `logs/runtime/ai_post_reviews.out` contains historical old-path references
- the latest health summary still shows `状態: 停止中`
- `eligible=599 / backlog=172 / AI済み=427 / human_override=0`
- `created=0 / reused=0 / request_failed=20 / daily_cap=0`
- the last error timestamp is still present

### Why deterministic evaluator must be primary

AI post review is stopped and failure-prone, so it cannot be the main evaluation layer.
Daily Proxy Loop and Weekly Review Loop should be deterministic first; AI post review remains optional qualitative enrichment only.

## Concrete implementation plan after this audit

### Smallest next implementation task

`BTCFX-20260702-DAILY-PROXY-EVALUATOR`

Scope:

- implement a report-only daily proxy evaluator from existing CSV/report assets only
- do not add MEXC import yet
- keep current evaluation deterministic and reproducible

### Files likely to edit next

- `tools/log_feedback.py`
- `tests/test_log_feedback.py`
- `docs/operations/ai-orchestration/NEXT_ACTION.md`

### Validations likely required

- targeted unit tests for the new report builder / CLI path
- `git diff --check`
- `git status --short --branch`

## Risks and stop rules

- do not call APIs
- do not read or print secrets
- do not restart runtime
- do not change launchd state
- do not change notification sending behavior
- do not fetch OHLCV or exchange data
- do not access private/account/order endpoints
- do not edit trading logic yet
- do not commit raw MEXC exports
- do not mix actual human trades into `paper_positions.csv`

## Final recommendation

Next Codex task:

`BTCFX-20260702-DAILY-PROXY-EVALUATOR`

Goal:

- build the first deterministic report-only daily proxy evaluator from existing CSV/report assets, using the audit conclusions above.
