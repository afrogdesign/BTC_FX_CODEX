# NEXT TASK TRACKER

更新日: 2026-05-18 JST

運用メモ: AI の日常入口として使う。履歴や経緯は `履歴/progress.md`、数値詳細は `reports/analysis/` に残し、ここには次判断に必要な情報だけを書く。

## 現在の状況

- 主系統は `iMac 2019` の `ver02.5-v7`。自動取引直前へ向けた `Phase A` 開始。正式 gate 待ちだけでなく、`opportunity_gate` と `paper_positions.csv` で紙実行候補を拾う方針へ変更。
- 新しい正本は `運用資料/計画/自動取引直前_高速到達計画_20260518.md` と `運用資料/計画/マイルストーン定義.md`。旧計画は `運用資料/計画/archive/superseded/2026-05-18_pre_auto_redesign/` へ退避済み。
- `opportunity_gate`、`paper_positions.csv`、通知ランク `紙実行候補・実弾不可`、日次レポートの紙ポジション集計を実装済み。commit `27c2db8` を `origin/ver02.5-v7` へ push 済み。実弾発注、取引所API送信、秘密鍵連携はまだ行わない。
- `Ver02.5-v7 先行実装パック` を実装済み。15分足の執行精度チェック、`trend_flip_confirmed_up` の弱評価化、詳細HTML/CSV保存、ロードマップ/タイムライン更新まで完了。全体テスト 163 件 OK。
- 常駐 `com.afrog.btc-monitor` は `Ver02.5-v7` 反映後に再起動済み。PID `98649`、`state=running`、`monitor.err` は空。
- フェーズ加速用に `Phase 1B-lite` を追加済み。実装 commit `1401a69`、記録更新 commit `2b22b03` を `origin/ver02.5-v6` へ push 済みで、常駐 `com.afrog.btc-monitor` も最新コードで再起動済み。
- `Phase 1B-lite` は正式 `Phase 1B` でも実弾でもなく、`SWEEP_WAIT` 限定の専用紙トレード観測レーン。
- `Phase 1B` の実行候補はまだ 0 件。`feedback_daily_sync_20260518.md` でも `trade_execution_gate=pass=0件`、`paper_orders planned=0件`。
- 直近の勝率低下とトレンド転換取り逃し対策として、`market_map` 判定を実装・本番反映済み。
- メール文言は、実行候補ではない watch 通知をロング推奨と誤読しにくい表現へ調整済み。
- 通知ランクは `執行候補・強` / `執行候補` / `高優先監視・実行不可` / `通常監視・実行不可` / `注意報・売買非推奨` へ再設計済み。執行候補は `trade_execution_gate=pass` かつ `paper_order_status=planned` のときだけ出る。
- メール件名ラベルは `Ver02.5-v6` で実送信確認済み。通常監視は `20260515_230500`、注意報は `20260516_060500` で新ランク表示を確認済み。`Ver02.5-v7` は再起動後の次回送信で確認する。
- `market_map` は shadow 側でも値入り確認済み。`market_map_effectiveness_20260518.md` では 116 件記録あり。
- AI 事後評価は `request_failed=0` を維持。`feedback_daily_sync_20260518.md` では backlog 75 件。

## 実装済みの前提

- `NO_TRADE_CANDIDATE` は hard flag があるときだけ強い見送りへ落とす。
- `watch + sweep_incomplete` は `watch_sweep_recheck_wait` / `watch_low_execution_recheck_wait` で main/attention を抑制する。
- `confidence_watch_learning` を追加し、`confidence_below_min` でも限定条件を満たす watch 群は `Phase 1A` 観測対象として追える。
- `Phase 1B-lite` は `confidence_watch_learning + SWEEP_WAIT + sweep_incomplete + lower_liquidity_close` かつ危険補助 flag なし、`direction>=55 / execution>=18 / wait<=85` の行だけを `phase1b_lite_paper_orders.csv` に分離保存する。
- `long_reversal_risk`、`counter_long_short_watch`、`failed_breakout_down_reversal` を追加し、上抜け失敗から下落へ切り替わる型を観測できる。
- `market_map` は複数時間足のレジサポ合流、反応回数、直近性、ヒゲ拒否、出来高タッチから主要ラインを作る。
- `market_map` は `support_to_resistance_flip`、`resistance_to_support_flip`、`failed_breakout_*_reversal`、`trend_flip_*` を score/risk/log/メール文言へ流す。
- 標準比較、運用焦点、Phase 1B 候補、失敗ブレイク、market_map readiness、有効性の各レポート CLI は実装済み。
- 作業ブランチは `ver02.5-v7` へ切り替え済み。
- 実装済みの計画書は `運用資料/計画/archive/implemented/2026-05-18/` へ整理済み。

## 直近の基準値

- 最新 daily-sync 基準: `feedback_daily_sync_20260518.md`。完了 47 件、近似PF 0.73、全体勝率 46.8%。
- 新規ログ基準: `2026-04-18` 〜 `2026-05-18` では `notified_rr_to_entry=0件`、`notified_rr_to_entry_orderbook_ask_heavy=0件`、`rr_to_confidence=1件` を維持。
- `operational_focus_20260518.md`: Phase1 pass 142 件 / blocked 575 件。blocked 上位は `confidence_below_min=385件`、`no_trade_candidate=207件`。
- `relaxation_candidates_20260518.md`: 緩和候補 48 件。`SWEEP_WAIT=31件`、`RISKY_ENTRY=16件`、`NO_TRADE_CANDIDATE=1件`。件数は 20260516 から横ばい。
- `phase1b_promotion_candidates_20260518.md`: 候補 6 件、勝率 100.0%、TP1先行 100.0%、近似PF 1.26。ただし新規候補は増えておらず、正式 gate 緩和材料にはまだしない。
- `Phase 1B-lite`: lite 候補 5 件、専用紙トレード observing 5 件。10〜15 件の成功条件にはまだ未達。
- `market_map_effectiveness_20260518.md`: `2026-05-13` 以降の shadow 120 行中 116 件で `market_map` 記録あり。`support_to_resistance_flip=75件` は勝率 69.6%、平均MFE24h 7.56 / 平均MAE24h 5.52 と相対的に有効。
- `trend_flip_confirmed_up=16件` は勝率 37.5%、wrong_rate 31.2%、平均MFE24h 1.59 / 平均MAE24h 13.09 で弱いため、`Ver02.5-v7` では score 加点を弱め、表示も慎重評価へ変更済み。
- AI 事後評価 health は `feedback_daily_sync_20260518.md` 基準で `eligible=302 / AI済み=227 / backlog=75 / created=4 / request_failed=0`。

## 次のタスク

1. 次回サイクルで `SYSTEM_LABEL=Ver02.5-v7`、`execution_precision_*`、`15分足 執行チェック` が result / CSV / 詳細HTMLへ入るか確認する。
2. 次回 `daily-sync` で `opportunity_gate=pass`、`paper_positions`、`紙実行候補・実弾不可` の集計が出るか確認する。
3. `paper_positions.csv` の pending / opened が live で増えるか確認し、次段階で closed / TP / SL / timeout 判定を実装する。
4. `trend_flip_confirmed_up` は 16 件でも弱い。上方向転換の強評価や gate 緩和には使わず、30 件までは観測継続する。
5. `Phase 1B-lite` は 5 件で止まっている。10〜15 件まで専用CSVで追い、正式 `Phase 1B` へはまだ上げない。
6. AI backlog は 75 件へ増加したが `request_failed=0`。安定優先なら daily cap 4 維持、backlog 解消優先なら 6 または 8 を検討する。

## 残作業一覧

- 次回 `market_map_effectiveness_YYYYMMDD.md` を更新し、`trend_flip_confirmed_up`、`resistance_to_support_flip`、`failed_breakout_down_reversal` の成績がサンプル増でどう変わるか見る。
- `com.afrog.btc-monitor` は `Ver02.5-v7` 反映後に再起動済み。PID `98649`、`state=running`、`monitor.err` は空。`logs/heartbeat.txt` と `logs/last_result.json` は次回定刻サイクルで更新確認する。
- `feedback_daily_sync_YYYYMMDD.md` を次回生成し、AI事後評価の `eligible / AI済み / backlog / created / request_failed` を更新する。現状は `request_failed=0` だが backlog は 75 件残っている。
- AI事後評価の `AI_POST_REVIEW_DAILY_MAX=4` は安定運用優先なら維持する。backlog 解消を優先する場合のみ `6` または `8` への増加を検討する。
- 標準比較 3 本、`operational_focus`、`relaxation_candidates`、`phase1b_promotion_candidates` を次回 daily-sync 後に更新し、`0 / 0 / 1` 基準から崩れた箇所だけを見る。
- `market_map` は 116 件まで増えた。下方向側は相対的に有効だが上方向転換系が弱いため、上方向のスコア重みや gate はまだ大きく変更しない。
- `trade_execution_gate=pass` と `paper_orders planned` が出るまでは `Phase 1B` へ進めない。候補が増えても成績が弱い間は gate 緩和しない。
- `Phase 1B-lite` は件名ランクを執行候補へ上げない。正式 `paper_orders.csv` とは混ぜず、専用CSVでだけ観測する。
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
