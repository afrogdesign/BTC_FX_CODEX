# NEXT TASK TRACKER

更新日: 2026-04-25 04:20 JST

運用メモ: AI の日常入口として使う。履歴や経緯は `履歴/progress.md` に残し、ここには次判断に必要な情報だけを書く。

## 現在の状況

- 主系統は `iMac 2019` の `ver02.5-v4`。`Phase 0` 本番観測中で、`Phase 1A` 観測紙トレードを継続中。`Phase 1B` の実行候補はまだ 0 件。
- 最新レポートは `運用資料/reports/feedback_daily_sync_20260425.md`。完了 40 件、近似PF 0.67、全体勝率 57.5%。
- `phase1_observation_gate=pass` は 15 件。内訳は `setup_watch_learning=15件`。
- `trade_execution_gate=pass` は 0 件、`paper_orders planned=0件`。`Phase 1B` の開始条件は未達。
- AI 事後評価 health は `eligible=190`、`AI済み=135`、`backlog=55`、`request_failed=0`。backlog は自然減せず、むしろ増加した。

## いまの論点

- `watch_sweep_recheck_wait` は新規ログでも 5 件出ている。`watch_low_execution_recheck_wait` がまだ未出現なので、低 execution 条件の母集団待ちを続けるかを判断する。
- `rr_below_min -> entry_zone_not_reached` は `2026-04-18` 〜 `2026-04-25` の新規ログでは 0 件だった。旧母集団の差分を追う段階から、新規ログで本当に残る差分だけを見る段階へ切り替える。
- `rr_below_min -> confidence_below_min` も同期間では 1 件だけだった。`confidence_below_min` の追加緩和は急がず、まず新規 2〜3 サイクルで再現するかを確認する。

## 実装済みの前提

- `NO_TRADE_CANDIDATE` は hard flag があるときだけ強い見送りへ落とす形に調整済み。
- `watch + sweep_incomplete` は `watch_sweep_recheck_wait` と `watch_low_execution_recheck_wait` で main/attention を抑制済み。初回 `attention_bias_changed` は残す。
- `compare-current-setup` は `--date-from`、`--date-to`、`--status-transition` を使って、新規ログだけを `timestamp_jst` 基準で比較できる。
- 標準比較レポートは `運用資料/reports/analysis/` に固定済み。
- `build-operational-focus-report` を追加し、backlog 分布と `setup_watch_learning` 偏重を `shadow_log.csv` からローカル集計できるようにした。
- `2026-04-25` の更新では、`2026-04-18` 〜 `2026-04-25` 範囲で `notified_rr_to_entry=0件`、`notified_rr_to_entry_orderbook_ask_heavy=0件`、`rr_to_confidence=1件` を確認した。
- 同日の `daily-sync` 再実行では、`watch 系通知済み履歴=15件`、`prelabel_improved=13件`、`status_upgraded=10件`、`confidence_jump=7件` を確認した。
- 同日の `operational_focus_20260425.md` では、同期間の backlog 候補 20 件、`phase1 pass=27件 / blocked=143件`、pass 内訳 `setup_watch_learning=26件`、`direction_rr_learning=1件` を確認した。
- 同レポートの blocked 上位内訳では、`confidence_below_min=84件` は `NO_TRADE_CANDIDATE=39件` と `SWEEP_WAIT=38件` に二分、`no_trade_candidate=59件` はほぼ `NO_TRADE_CANDIDATE` 固定だった。両群とも `sweep_incomplete + lower_liquidity_close` の同居が強い。
- さらに `sweep_incomplete + lower_liquidity_close` 群の補助 flag を切ると、`confidence_below_min` 67 件のうち `補助flagなし` は 13 件、`no_trade_candidate` 54 件のうち `補助flagなし` は 1 件だけだった。緩和候補は少数群に限られる。
- `build-relaxation-candidates-report` を追加し、緩和候補の少数群だけを独立レポート化できるようにした。`2026-04-18` 〜 `2026-04-25` では候補 13 件、`SWEEP_WAIT=9件`、平均 `execution=18.2 / wait=84.1`。

## 比較レポート基準値

- 全期間基準値:
- `notified_rr_to_entry.md`: 33 件、`watch->watch=25件`、`invalid->watch=8件`。
- `notified_rr_to_entry_orderbook_ask_heavy.md`: 14 件、`watch->watch=13件`、平均 `execution=7.1 / wait=69.0`。
- `rr_to_confidence.md`: 487 件、通知済み 64 件、`invalid->invalid=278件`、`watch->invalid=209件`。
- 新規ログ基準値:
- `2026-04-18` 〜 `2026-04-25` の `notified_rr_to_entry.md`: 0 件。
- 同期間の `notified_rr_to_entry_orderbook_ask_heavy.md`: 0 件。
- 同期間の `rr_to_confidence.md`: 1 件、`watch->invalid=1件`、平均 `execution=11.0 / wait=100.0`。
- `watch_sweep_recheck_wait` は同期間で 5 件、`watch_low_execution_recheck_wait` は 0 件。
- `operational_focus_20260425.md`: backlog 候補 20 件、`phase1_observation_type` は `blocked=13件`、`setup_watch_learning=7件`。`setup_watch_learning` の主 reason は `entry_zone_not_reached=16件`、`near_entry_zone_waiting_trigger=8件`。
- `blocked` 上位の内訳: `confidence_below_min=84件`、`no_trade_candidate=59件`。どちらも `sweep_incomplete`、`lower_liquidity_close` が支配的。
- `緩和候補の少数群`: `20260424_130500`、`20260421_140500`、`20260421_060500`、`20260421_020500`、`20260420_180500` など。いずれも `confidence_below_min` だが補助 hard flag が薄い。
- `relaxation_candidates_20260425.md`: 候補 13 件。`SWEEP_WAIT=9件`、`RISKY_ENTRY=3件`、`NO_TRADE_CANDIDATE=1件`。risk flag は `short_cover_risk=6件` が最多。

## 次のタスク

1. `daily-sync` 3 回観測のうち 1 回分は更新済み。残り 2 回分も `運用資料/reports/analysis/notified_rr_to_entry.md`、`notified_rr_to_entry_orderbook_ask_heavy.md`、`rr_to_confidence.md` を同じ日付帯で毎回更新する。
2. 新規ログ確認では `compare-current-setup --date-from YYYY-MM-DD --date-to YYYY-MM-DD` を使い、差分が 0 件の間は `watch->watch` や `invalid->watch` の追加分解を増やしすぎない。
3. `watch_sweep_recheck_wait` の件数推移と、`watch_low_execution_recheck_wait` が初めて出るタイミングを確認する。
4. `notified_rr_to_entry_orderbook_ask_heavy` が新規ログで 0 件のまま続くかを確認する。0 件継続なら `watch_orderbook_recheck_wait` 実装は見送る。
5. `rr_to_confidence` が新規ログで再び増えるかを確認する。1 件止まりでも、blocked 実態では `confidence_below_min` が 84 件あるため、`SWEEP_WAIT` 側にどこまで寄っているかを継続して見る。
6. `phase1_observation_gate=pass` が 15 件前後を維持するか、`setup_watch_learning` 偏重のままで良いかを確認する。特に `entry_zone_not_reached` と `near_entry_zone_waiting_trigger` が pass 群の大半を占め続けるかを見る。
7. `no_trade_candidate=59件` がほぼ `NO_TRADE_CANDIDATE` 固定で、`sweep_incomplete + lower_liquidity_close` に寄っているため、この組み合わせの hard flag 扱いは維持寄りで見る。
8. 緩和を検討するなら、まず `confidence_below_min` かつ `sweep_incomplete + lower_liquidity_close` でも `補助flagなし` の少数群だけを次回比較で追う。
9. 少数群 13 件のうち、`SWEEP_WAIT + confidence_below_min` が次回以降も再現するか、特に `20260424_130500` 近辺の型が増えるかを見る。
10. `sync-ai-post-reviews` が `request_failed=0` を維持しつつ、backlog `55件` が自然減するかを確認する。新規帯の backlog 候補 `20件` がまず減るかを優先して見る。
11. 次回定時サイクル後、`monitor.err` に `NameError` や `phase1_observation_gate` 周辺の例外が出ていないか確認する。

## ブロッカー

- 通知増加は `1日8〜9件`、AI新規処理は `1日4件` のため、backlog 解消には時間がかかる。
- `trade_execution_gate=pass` はまだ 0 件で、`Phase 1B` の本有効条件は未達。

## 完了条件

- `daily-sync` と `sync-ai-post-reviews` が継続して回る。
- `Phase 1A` の観測と `Phase 1B` の本有効確認を分けて追える。
- `phase1_active=true=30件以上` を Ver03 判断材料にできるだけの観測が貯まる。
