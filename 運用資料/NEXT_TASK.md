# NEXT TASK TRACKER

更新日: 2026-05-13 JST

運用メモ: AI の日常入口として使う。履歴や経緯は `履歴/progress.md`、数値詳細は `reports/analysis/` に残し、ここには次判断に必要な情報だけを書く。

## 現在の状況

- 主系統は `iMac 2019` の `ver02.5-v5`。`Phase 0` 本番観測中、`Phase 1A` 観測紙トレード継続中。
- `Phase 1B` の実行候補はまだ 0 件。`trade_execution_gate=pass` と `paper_orders planned` が出るまでは本有効へ進めない。
- 直近の勝率低下とトレンド転換取り逃し対策として、`market_map` 判定を実装・本番反映済み。
- メール文言は、実行候補ではない watch 通知をロング推奨と誤読しにくい表現へ調整済み。
- `market_map` の値入り確認用に `build-market-map-readiness-report` を追加済み。現状は `readiness=wait`。
- AI 事後評価は `request_failed=0` を維持。backlog は残っているため、自然減を継続観測する。

## 実装済みの前提

- `NO_TRADE_CANDIDATE` は hard flag があるときだけ強い見送りへ落とす。
- `watch + sweep_incomplete` は `watch_sweep_recheck_wait` / `watch_low_execution_recheck_wait` で main/attention を抑制する。
- `confidence_watch_learning` を追加し、`confidence_below_min` でも限定条件を満たす watch 群は `Phase 1A` 観測対象として追える。
- `long_reversal_risk`、`counter_long_short_watch`、`failed_breakout_down_reversal` を追加し、上抜け失敗から下落へ切り替わる型を観測できる。
- `market_map` は複数時間足のレジサポ合流、反応回数、直近性、ヒゲ拒否、出来高タッチから主要ラインを作る。
- `market_map` は `support_to_resistance_flip`、`resistance_to_support_flip`、`failed_breakout_*_reversal`、`trend_flip_*` を score/risk/log/メール文言へ流す。
- 標準比較、運用焦点、Phase 1B 候補、失敗ブレイク、market_map readiness、有効性の各レポート CLI は実装済み。
- 作業ブランチ `ver02.5-v5` は `origin/ver02.5-v5` へ push 済み。

## 直近の基準値

- 最新 daily-sync 基準: `feedback_daily_sync_20260430.md`。完了 29 件、近似PF 1.10、全体勝率 44.8%。
- 新規ログ基準: `2026-04-18` 〜 `2026-04-29` では `notified_rr_to_entry=0件`、`notified_rr_to_entry_orderbook_ask_heavy=0件`、`rr_to_confidence=1件`。
- `operational_focus_20260429.md`: blocked 上位は `confidence_below_min=147件`、`no_trade_candidate=81件`。どちらも `sweep_incomplete` と `lower_liquidity_close` への偏りが強い。
- `relaxation_candidates_20260429.md`: 緩和候補 23 件。`SWEEP_WAIT=16件`、`RISKY_ENTRY=6件`、`NO_TRADE_CANDIDATE=1件`。
- `phase1b_promotion_candidates_20260429.md`: 候補 2 件のみ。成績が弱いため gate 緩和材料にはしない。
- `market_map_effectiveness_20260513.md`: `2026-05-01` 〜 `2026-05-13` の shadow 292 行では `market_map 記録あり=0件`。デプロイ前ログが対象のため正常。次回以降のサイクルで値入り行を確認する。
- `market_map_readiness_20260513.md`: `2026-05-13` の shadow 4 行では `readiness=wait`。最新 shadow は `20260512_180500 / 03:05 / Ver02.5-v4` で、まだ `ver02.5-v5` の market_map 実ログは出ていない。

## 次のタスク

1. 次回監視サイクル後、`build-market-map-readiness-report --date-from 2026-05-13` で `market_map_*` の値入りを確認する。
2. 値入り後に `build-market-map-effectiveness-report --date-from 2026-05-13 --date-to YYYY-MM-DD` を実行し、主要レジサポ接近、サポレジ転換、失敗ブレイク、トレンド転換初動が負けパターンを分離できているか見る。
3. 次回 `daily-sync` 後、標準 3 本の比較レポートを更新し、新規ログ基準 `0 / 0 / 1` から崩れた部分だけを掘る。
4. `watch_sweep_recheck_wait` と `watch_low_execution_recheck_wait` の件数推移を見る。低 execution 側が未出現の間は追加抑制を急がない。
5. `confidence_below_min` の緩和は、`sweep_incomplete + lower_liquidity_close` でも補助 flag が薄い少数群だけを対象に検討する。
6. `phase1b_promotion_candidates` は候補数と成績が増えるまで gate 緩和へ進めない。現時点の 2 件だけでは不十分。
7. `sync-ai-post-reviews` が `request_failed=0` を維持しつつ backlog を自然減できているか確認する。
8. 定時サイクル後、`monitor.err` に `NameError` や `market_map` / `phase1_observation_gate` 周辺の例外が出ていないか確認する。

## ブロッカー

- 通知増加は AI 事後評価の処理量を上回りやすく、backlog 解消には時間がかかる。
- `trade_execution_gate=pass` はまだ 0 件で、`Phase 1B` の本有効条件は未達。
- `market_map` は本番反映直後のため、実ログでの有効性はまだ未判定。

## 完了条件

- `daily-sync` と `sync-ai-post-reviews` が継続して回る。
- `market_map` の値入りログが増え、失敗型を分離できるか評価できる。
- `Phase 1A` の観測と `Phase 1B` の本有効確認を分けて追える。
- `phase1_active=true=30件以上` を Ver03 判断材料にできるだけの観測が貯まる。
