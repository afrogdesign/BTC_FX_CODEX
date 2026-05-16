# NEXT TASK TRACKER

更新日: 2026-05-16 JST

運用メモ: AI の日常入口として使う。履歴や経緯は `履歴/progress.md`、数値詳細は `reports/analysis/` に残し、ここには次判断に必要な情報だけを書く。

## 現在の状況

- 主系統は `iMac 2019` の `ver02.5-v6`。`Phase 0` 本番観測中、`Phase 1A` 観測紙トレード継続中。
- `Phase 1B` の実行候補はまだ 0 件。`trade_execution_gate=pass` と `paper_orders planned` が出るまでは本有効へ進めない。
- 直近の勝率低下とトレンド転換取り逃し対策として、`market_map` 判定を実装・本番反映済み。
- メール文言は、実行候補ではない watch 通知をロング推奨と誤読しにくい表現へ調整済み。
- 通知ランクは `執行候補・強` / `執行候補` / `高優先監視・実行不可` / `通常監視・実行不可` / `注意報・売買非推奨` へ再設計済み。執行候補は `trade_execution_gate=pass` かつ `paper_order_status=planned` のときだけ出る。
- メール件名ラベルは `Ver02.5-v6` で実送信確認済み。通常監視は `20260515_230500`、注意報は `20260516_060500` で新ランク表示を確認済み。
- `market_map` は shadow 側でも値入り確認済み。`market_map_effectiveness_20260516.md` では 68 件記録あり。
- AI 事後評価は `request_failed=0` を維持。`feedback_daily_sync_20260516.md` では backlog 69 件。

## 実装済みの前提

- `NO_TRADE_CANDIDATE` は hard flag があるときだけ強い見送りへ落とす。
- `watch + sweep_incomplete` は `watch_sweep_recheck_wait` / `watch_low_execution_recheck_wait` で main/attention を抑制する。
- `confidence_watch_learning` を追加し、`confidence_below_min` でも限定条件を満たす watch 群は `Phase 1A` 観測対象として追える。
- `long_reversal_risk`、`counter_long_short_watch`、`failed_breakout_down_reversal` を追加し、上抜け失敗から下落へ切り替わる型を観測できる。
- `market_map` は複数時間足のレジサポ合流、反応回数、直近性、ヒゲ拒否、出来高タッチから主要ラインを作る。
- `market_map` は `support_to_resistance_flip`、`resistance_to_support_flip`、`failed_breakout_*_reversal`、`trend_flip_*` を score/risk/log/メール文言へ流す。
- 標準比較、運用焦点、Phase 1B 候補、失敗ブレイク、market_map readiness、有効性の各レポート CLI は実装済み。
- 作業ブランチは `ver02.5-v6` へ切り替え済み。
- 通知ランク再設計の実装設計は `運用資料/計画/通知ランク再設計_実装設計_20260515.md` に保存済み。

## 直近の基準値

- 最新 daily-sync 基準: `feedback_daily_sync_20260516.md`。完了 38 件、近似PF 0.76、全体勝率 57.9%。
- 新規ログ基準: `2026-04-18` 〜 `2026-05-16` では `notified_rr_to_entry=0件`、`notified_rr_to_entry_orderbook_ask_heavy=0件`、`rr_to_confidence=1件`。
- `operational_focus_20260516.md`: blocked 上位は `confidence_below_min=350件`、`no_trade_candidate=192件`。どちらも `sweep_incomplete` と `lower_liquidity_close` への偏りが強い。
- `relaxation_candidates_20260516.md`: 緩和候補 48 件。`SWEEP_WAIT=31件`、`RISKY_ENTRY=16件`、`NO_TRADE_CANDIDATE=1件`。
- `phase1b_promotion_candidates_20260516.md`: 候補 6 件、勝率 50.0%、TP1先行 100.0%、近似PF 1.26。ただし全件 `trade_execution_gate=blocked` のため gate 緩和材料にはまだしない。
- `market_map_effectiveness_20260516.md`: `2026-05-13` 以降の shadow 72 行中 68 件で `market_map` 記録あり。`support_to_resistance_flip=39件`、`trend_flip_confirmed_down=33件`、`failed_breakout_up_reversal=15件`。
- `trend_flip_confirmed_up=11件` は勝率 33.3%、wrong_rate 27.3%、平均MAE24h 14.51 で引き続き弱く、上方向転換の gate 強化候補として観測継続。
- AI 事後評価 health は `feedback_daily_sync_20260516.md` 基準で `eligible=288 / AI済み=219 / backlog=69 / created=4 / request_failed=0`。

## 次のタスク

1. 次回 `daily-sync` 後、`market_map_effectiveness_YYYYMMDD.md` を更新し、`trend_flip_confirmed_up` の弱さが継続するか確認する。
2. `trend_flip_confirmed_up` は上方向転換として弱い。サンプル 30 件までは gate 変更せず、wrong_rate と平均MAEが改善しないかを見る。
3. 次回 `daily-sync` 後、標準 3 本の比較レポートを更新し、新規ログ基準 `0 / 0 / 1` から崩れた部分だけを掘る。
4. `watch_sweep_recheck_wait` と `watch_low_execution_recheck_wait` の件数推移を見る。低 execution 側が未出現の間は追加抑制を急がない。
5. `confidence_below_min` の緩和は、`sweep_incomplete + lower_liquidity_close` でも補助 flag が薄い少数群だけを対象に検討する。
6. `phase1b_promotion_candidates` は候補数と成績がさらに増えるまで gate 緩和へ進めない。`20260516` 時点では候補 6 件、勝率 50.0%、近似PF 1.26。
7. `sync-ai-post-reviews` が `request_failed=0` を維持しつつ backlog を自然減できているか確認する。
8. 新ランク反映後の実メールで、`高優先監視・実行不可` が実行候補に見えず、`執行候補` 系が実行ゲート通過時だけ出ることを確認する。通常監視と注意報は確認済み。

## 残作業一覧

- 次回 `market_map_effectiveness_YYYYMMDD.md` を更新し、`trend_flip_confirmed_up`、`resistance_to_support_flip`、`failed_breakout_down_reversal` の成績がサンプル増でどう変わるか見る。
- `com.afrog.btc-monitor` は `Ver02.5-v6` 反映後に再起動済み。`[Ver02.5-v6] [CLI]` 件名は本通知・注意報とも確認済み。
- `feedback_daily_sync_YYYYMMDD.md` を次回生成し、AI事後評価の `eligible / AI済み / backlog / created / request_failed` を更新する。現状は `request_failed=0` だが backlog は 69 件残っている。
- AI事後評価の `AI_POST_REVIEW_DAILY_MAX=4` は安定運用優先なら維持する。backlog 解消を優先する場合のみ `6` または `8` への増加を検討する。
- 標準比較 3 本、`operational_focus`、`relaxation_candidates`、`phase1b_promotion_candidates` を次回 daily-sync 後に更新し、`0 / 0 / 1` 基準から崩れた箇所だけを見る。
- `market_map` は 68 件まで増えたが、上方向転換系が弱いためスコア重みや gate はまだ大きく変更しない。まず flag 別の wrong_rate、平均MFE/MAE、代表例を増やす。
- `trade_execution_gate=pass` と `paper_orders planned` が出るまでは `Phase 1B` へ進めない。候補が増えても成績が弱い間は gate 緩和しない。
- 定時サイクル後の `monitor.err`、`ai_post_reviews.err`、`feedback_daily_sync.err` が空であることを継続確認する。

## ブロッカー

- 通知増加は AI 事後評価の処理量を上回りやすく、backlog 解消には時間がかかる。
- `trade_execution_gate=pass` はまだ 0 件で、`Phase 1B` の本有効条件は未達。
- `market_map` は値入り確認済みだが、上方向転換系の弱さが残っており、flag 別の有効性判断にはまだ継続観測が必要。

## 完了条件

- `daily-sync` と `sync-ai-post-reviews` が継続して回る。
- `market_map` の値入りログが増え、失敗型を分離できるか評価できる。
- `Phase 1A` の観測と `Phase 1B` の本有効確認を分けて追える。
- `phase1_active=true=30件以上` を Ver03 判断材料にできるだけの観測が貯まる。
