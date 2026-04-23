# NEXT TASK TRACKER

更新日: 2026-04-24 04:55 JST

運用メモ: AI の日常入口として使う。履歴や経緯は `履歴/progress.md` に残し、ここには次判断に必要な情報だけを書く。

## 現在の状況

- 主系統は `iMac 2019` の `ver02.5-v4`。`Phase 0` 本番観測中で、`Phase 1A` 観測紙トレードを継続中。`Phase 1B` の実行候補はまだ 0 件。
- 最新レポートは `運用資料/reports/feedback_daily_sync_20260424.md`。完了 31 件、近似PF 0.87、全体勝率 71.0%。
- `phase1_observation_gate=pass` は 13 件。内訳は `direction_rr_learning=2件`、`setup_watch_learning=11件`。
- `trade_execution_gate=pass` は 0 件、`paper_orders planned=0件`。`Phase 1B` の開始条件は未達。
- AI 事後評価 health は `eligible=179`、`AI済み=131`、`backlog=48`、`request_failed=0`。backlog はまだ自然減していない。

## いまの論点

- `watch + sweep_incomplete` 系の再通知をどこまで抑えるか。
- `rr_below_min` より、現行再計算で `entry_zone_not_reached` へ寄るケースの扱いをどう詰めるか。
- `NO_TRADE_CANDIDATE` をこれ以上緩める前に、`confidence_below_min` への落ち方を先に見るべきか。

## 実装済みの前提

- `NO_TRADE_CANDIDATE` は hard flag があるときだけ強い見送りへ落とす形に調整済み。
- `watch + sweep_incomplete` は `watch_sweep_recheck_wait` と `watch_low_execution_recheck_wait` で main/attention を抑制済み。初回 `attention_bias_changed` は残す。
- `compare-current-setup` は `--date-from`、`--date-to`、`--status-transition` を使って、新規ログだけを `timestamp_jst` 基準で比較できる。
- 標準比較レポートは `運用資料/reports/analysis/` に固定済み。

## 比較レポート基準値

- `notified_rr_to_entry.md`: 33 件、`watch->watch=25件`、`invalid->watch=8件`。
- `notified_rr_to_entry_orderbook_ask_heavy.md`: 14 件、`watch->watch=13件`、平均 `execution=7.1 / wait=69.0`。
- `rr_to_confidence.md`: 487 件、通知済み 64 件、`invalid->invalid=278件`、`watch->invalid=209件`。
- `--date-from 2026-04-09 --date-to 2026-04-24 --status-transition 'watch->watch'` の実データ確認では 14 件、平均 `execution=5.9 / wait=76.1`。

## 次のタスク

1. 次の `daily-sync` から最低 3 回分、`運用資料/reports/analysis/notified_rr_to_entry.md`、`notified_rr_to_entry_orderbook_ask_heavy.md`、`rr_to_confidence.md` を毎回更新する。
2. 新規ログ確認では `compare-current-setup --date-from YYYY-MM-DD --date-to YYYY-MM-DD` を使い、必要に応じて `--status-transition watch->watch` と `invalid->watch` で分ける。
3. `watch_low_execution_recheck_wait` と `watch_sweep_recheck_wait` が実際に出るか、`watch 系通知済み履歴` の `prelabel_improved` / `status_upgraded` 偏重が減るかを確認する。
4. `notified_rr_to_entry_orderbook_ask_heavy` で `watch->watch` が過半、平均 `execution<=8`、平均 `wait>=60` が継続するか確認する。条件が揃ったときだけ `watch_orderbook_recheck_wait` 実装へ進む。
5. `rr_to_confidence` が新規ログでも主差分のまま残るかを確認する。残る場合だけ confidence floor / penalty 調整へ進む。
6. `phase1_observation_gate=pass` が 13 件前後を維持するか、特に `direction_rr_learning=2件` がさらに痩せないかを確認する。
7. `sync-ai-post-reviews` が `request_failed=0` を維持しつつ、backlog `48件` が自然減するかを確認する。
8. 次回定時サイクル後、`monitor.err` に `NameError` や `phase1_observation_gate` 周辺の例外が出ていないか確認する。

## ブロッカー

- 通知増加は `1日8〜9件`、AI新規処理は `1日4件` のため、backlog 解消には時間がかかる。
- `trade_execution_gate=pass` はまだ 0 件で、`Phase 1B` の本有効条件は未達。

## 完了条件

- `daily-sync` と `sync-ai-post-reviews` が継続して回る。
- `Phase 1A` の観測と `Phase 1B` の本有効確認を分けて追える。
- `phase1_active=true=30件以上` を Ver03 判断材料にできるだけの観測が貯まる。
