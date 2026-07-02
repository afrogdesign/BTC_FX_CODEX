# CURRENT_PROGRESS

最終更新: 2026-07-01 JST

## 現在位置

- 最新 ACCEPT 済み WORK_ID: `BTCFX-20260630-OHLCV-STALE-COVERAGE-CHECKPOINT-REVIEW`
- Commit: `013146f docs: checkpoint stale ohlcv warning`
- Push: none
- 次の推奨 WORK_ID: `BTCFX-20260630-EVIDENCE-QUALITY-PHASE-CHECKPOINT`

## 今回完了したこと

stale OHLCV operator warning path を一区切りとして review した。

完了済みとして整理された path:

- `evidence_quality_summary`
- `ohlcv_source_coverage_summary`
- `ohlcv_range_freshness_status`
- `OHLCV stale coverage warning`
- summary text display
- detail HTML display
- app contract / stdout-json / exported artifacts freshness fields
- direct summary/detail render confirmation
- E2E smoke confirmation
- generated file commit なし

## 現在の evidence-quality state

- `candidate_rows`: `1418`
- `ohlcv_valid_rows`: `499`
- `window_covered_rows`: `88`
- `window_missing_rows`: `1330`
- `window_missing_rate`: 約 `93.8%`
- `candidate_timestamp_max`: `2026-06-30T03:05:00.923983+09:00`
- `ohlcv_end`: `2026-06-10T03:15:00+09:00`
- `candidate_max_after_ohlcv_end_hours`: 約 `479.8`
- `ohlcv_range_freshness_status`: `stale_before_latest_candidate`

## ここまでにできるようになったこと

- intraperiod outcomes から `evidence_quality_summary` を生成できる。
- `no_ohlcv` が多い原因を `ohlcv_source_coverage_summary` として分解できる。
- candidate timestamp と OHLCV coverage window のズレを見える化できる。
- OHLCV range の freshness / staleness を `ohlcv_range_freshness_status` で判定できる。
- 現在の実データでは `stale_before_latest_candidate` と判定済み。
- stale OHLCV coverage が検証根拠として誤認されないよう、summary / detail HTML に warning を出せる。
- smoke で warning と freshness fields の露出を確認済み。
- warning path の checkpoint review まで完了。

## 残っている制約

- stale OHLCV は visible / warned だが、OHLCV data 自体はまだ stale。
- performance interpretation はまだ弱い。
- OHLCV fetch は追加していない。
- trading logic は変更していない。
- automatic trading は開始していない。

## 安全境界

- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no private/account/order/runtime execution affordance
- OHLCV fetch なし
- trading logic 変更なし
- generated files commit なし

## 次にやること

`BTCFX-20260630-EVIDENCE-QUALITY-PHASE-CHECKPOINT`

目的:

- completed evidence-quality / OHLCV coverage visibility phase をまとめる。
- fetch / trading logic / execution affordance を追加せず、次の product-quality direction を決める。
