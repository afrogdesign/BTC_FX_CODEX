# NEXT TASK TRACKER

更新日: 2026-05-13 JST

運用メモ: AI の日常入口として使う。履歴や経緯は `履歴/progress.md` に残し、ここには次判断に必要な情報だけを書く。

## 現在の状況

- 主系統は `iMac 2019` の `ver02.5-v4`。`Phase 0` 本番観測中で、`Phase 1A` 観測紙トレードを継続中。`Phase 1B` の実行候補はまだ 0 件。
- 最新レポートは `運用資料/reports/feedback_daily_sync_20260430.md`。完了 29 件、近似PF 1.10、全体勝率 44.8%。
- `phase1_observation_gate=pass` は 8 件。内訳は `setup_watch_learning=8件`。
- `trade_execution_gate=pass` は 0 件、`paper_orders planned=0件`。`Phase 1B` の開始条件は未達。
- AI 事後評価 health は `eligible=208`、`AI済み=155`、`backlog=53`、`request_failed=0`。`request_failed=0` は維持したが、backlog の自然減はまだ弱い。

## いまの論点

- `rr_below_min -> entry_zone_not_reached` は `2026-04-18` 〜 `2026-04-29` の新規ログでも 0 件のままだった。旧母集団の差分追跡は続けず、新規ログで残る差分だけを見る方針を維持する。
- `rr_below_min -> confidence_below_min` も同期間で 1 件だけのままだった。`confidence_below_min` の追加緩和は急がず、新規ログでの再現待ちを続ける。
- `watch_sweep_recheck_wait` は直近12時間速報でも 1 件出ている一方、`watch_low_execution_recheck_wait` はまだ未確認。低 execution 側は母集団待ちのまま。
- `operational_focus_20260429.md` では `confidence_below_min=147件`、`no_trade_candidate=81件` が blocked の上位で、両群とも `sweep_incomplete + lower_liquidity_close` 偏重が継続している。
- `phase1b_promotion_candidates_20260429.md` では限定昇格候補は 2 件だけで、近似PF 0.12、TP1先行 0.0% だった。現時点では「昇格候補を増やす」より「この型が再現するか」を見る段階。
- `20260429_100500` のように、内部は `watch + trade_execution_gate=blocked` なのにロング推奨に見える失敗があるため、`運用資料/計画/ロング誤判定と下落取り逃し改善計画_20260430.md` に原因と改善手順を整理した。

## 実装済みの前提

- `NO_TRADE_CANDIDATE` は hard flag があるときだけ強い見送りへ落とす形に調整済み。
- `watch + sweep_incomplete` は `watch_sweep_recheck_wait` と `watch_low_execution_recheck_wait` で main/attention を抑制済み。初回 `attention_bias_changed` は残す。
- `compare-current-setup` は `--date-from`、`--date-to`、`--status-transition` を使って、新規ログだけを `timestamp_jst` 基準で比較できる。
- 標準比較レポートは `運用資料/reports/analysis/` に固定済み。
- `build-operational-focus-report` を追加し、backlog 分布と `setup_watch_learning` 偏重を `shadow_log.csv` からローカル集計できるようにした。
- `confidence_watch_learning` を追加し、`confidence_below_min` でも限定条件を満たす watch 群だけは `Phase 1A` 観測と `Phase 1B` 昇格候補レポートで追えるようにした。
- `build-phase1b-promotion-report` を追加し、限定昇格候補の件数、成績、代表例を `運用資料/reports/analysis/phase1b_promotion_candidates_*.md` に固定出力できるようにした。
- `ロング誤判定と下落取り逃し改善計画_20260430.md` を追加し、`20260429_100500` の失敗原因を `文面誤読`、`方向スコア偏り`、`失敗ブレイク検知不足`、`ショート候補化遅れ` に分け、実装指示まで落とした。
- `watch + trade_execution_gate=blocked` の本通知は、件名を `上方向バイアス` ではなく `上方向監視` と読める形に変え、本文冒頭にも「これは実行候補ではありません」を追加した。
- `long_reversal_risk` を追加し、`transition/down + watch + sweep_incomplete` かつ抵抗要因ありのロング監視は `通常の本通知` へ抑制しつつ、通知理由に `下落警戒` を出せるようにした。
- `src/analysis/scoring.py` では `transition/down + breakout_up` に反転ペナルティを足し、上抜け失敗の下落初動をスコア上でも少し重く見るようにした。
- `2026-04-30` の更新では、`refresh-standard-setup-reports --date-from 2026-04-18 --date-to 2026-04-29` を再実行し、`notified_rr_to_entry=0件`、`notified_rr_to_entry_orderbook_ask_heavy=0件`、`rr_to_confidence=1件` のまま維持されることを確認した。
- 同日の `operational_focus_20260429.md` では、同期間の backlog 候補 18 件、`phase1 pass=33件 / blocked=232件`、pass 内訳 `setup_watch_learning=32件`、`direction_rr_learning=1件` を確認した。
- 同レポートの blocked 上位内訳では、`confidence_below_min=147件` は `SWEEP_WAIT=71件`、`NO_TRADE_CANDIDATE=60件`、`RISKY_ENTRY=16件` に分かれ、`no_trade_candidate=81件` は `NO_TRADE_CANDIDATE` 固定が続いた。
- `sweep_incomplete + lower_liquidity_close` 群の補助 flag を切ると、`confidence_below_min` 102 件のうち `補助flagなし` は 23 件、`no_trade_candidate` 69 件のうち `補助flagなし` は 1 件だけだった。緩和候補は引き続き少数群に限られる。
- `relaxation_candidates_20260429.md` では候補 23 件、`SWEEP_WAIT=16件`、`RISKY_ENTRY=6件`、`NO_TRADE_CANDIDATE=1件`、平均 `execution=18.5 / wait=84.8` を確認した。
- `phase1b_promotion_candidates_20260429.md` では候補 2 件、どちらも `SWEEP_WAIT`、平均 `direction=59.0 / execution=22.0 / wait=76.8`、ただし成績は `近似PF 0.12` と弱かった。
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
- `2026-04-18` 〜 `2026-04-29` の `notified_rr_to_entry.md`: 0 件。
- 同期間の `notified_rr_to_entry_orderbook_ask_heavy.md`: 0 件。
- 同期間の `rr_to_confidence.md`: 1 件、`watch->invalid=1件`、平均 `execution=11.0 / wait=100.0`。
- `watch_sweep_recheck_wait` は直近速報で 1 件、`watch_low_execution_recheck_wait` は 0 件。
- `operational_focus_20260429.md`: backlog 候補 18 件、`phase1_observation_type` は `blocked=14件`、`setup_watch_learning=4件`。`setup_watch_learning` の主 reason は `entry_zone_not_reached=18件`、`near_entry_zone_waiting_trigger=10件`。
- `blocked` 上位の内訳: `confidence_below_min=147件`、`no_trade_candidate=81件`。どちらも `sweep_incomplete`、`lower_liquidity_close` が支配的。
- `緩和候補の少数群`: `20260427_170500`、`20260427_110500`、`20260427_100500`、`20260426_210500`、`20260426_180501` など。新規帯でも `confidence_below_min` の少数群だけが増えている。
- `relaxation_candidates_20260429.md`: 候補 23 件。`SWEEP_WAIT=16件`、`RISKY_ENTRY=6件`、`NO_TRADE_CANDIDATE=1件`。risk flag は `short_cover_risk=10件` が最多。
- `phase1b_promotion_candidates_20260429.md`: 候補 2 件。`20260424_130500`、`20260420_130500`。どちらも `SWEEP_WAIT` だが、成績は弱く即昇格材料にはならない。

## 次のタスク

1. 次回 `daily-sync` 後も `refresh-standard-setup-reports --date-from 2026-04-18 --date-to YYYY-MM-DD` を実行し、標準 3 本の差分がまだ `0 / 0 / 1` のままかを確認する。
2. 新規ログ確認では `compare-current-setup --date-from YYYY-MM-DD --date-to YYYY-MM-DD` を使い、差分が 0 件の間は `watch->watch` や `invalid->watch` の追加分解を増やしすぎない。
3. `watch_sweep_recheck_wait` の件数推移と、`watch_low_execution_recheck_wait` が初めて出るタイミングを確認する。未出現が続くなら低 execution 抑制の追加判断は保留でよい。
4. `notified_rr_to_entry_orderbook_ask_heavy` が新規ログで 0 件のまま続くかを確認する。0 件継続なら `watch_orderbook_recheck_wait` 実装は見送る。
5. `rr_to_confidence` が新規ログで再び増えるかを確認する。1 件止まりの間は `confidence floor` 緩和より、`SWEEP_WAIT` 側の blocked 実態観測を優先する。
6. `phase1_observation_gate=pass` が 8 件まで落ちたため、単純な件数だけでなく `setup_watch_learning` の勝率と `entry_zone_not_reached` 偏重が続くかを見る。
7. `no_trade_candidate=81件` がほぼ `NO_TRADE_CANDIDATE` 固定で、`sweep_incomplete + lower_liquidity_close` に寄っているため、この組み合わせの hard flag 扱いは維持寄りで見る。
8. 緩和を検討するなら、まず `confidence_below_min` かつ `sweep_incomplete + lower_liquidity_close` でも `補助flagなし` の少数群 23 件だけを次回比較で追う。
9. `build-phase1b-promotion-report` で出た 2 件の型、特に `20260424_130500` が次回以降も再現するかを見る。2 件の成績が弱いため、件数が増えるまでは gate 緩和へ進まない。
10. `ロング誤判定と下落取り逃し改善計画_20260430.md` のうち、文面誤読防止と `long_reversal_risk` は実装済み。次は `failed_breakout_down_reversal` 集計と `counter_long_short_watch` の観測候補化を追加する。
11. `sync-ai-post-reviews` が `request_failed=0` を維持しつつ、backlog `53件` と新規帯 backlog 候補 `18件` が自然減するかを確認する。
12. 次回定時サイクル後も `monitor.err` に `NameError` や `phase1_observation_gate` 周辺の例外が出ていないか確認する。現状は `urllib3` の `NotOpenSSLWarning` のみ。

## ブロッカー

- 通知増加は `1日8〜9件`、AI新規処理は `1日4件` のため、backlog 解消には時間がかかる。
- `trade_execution_gate=pass` はまだ 0 件で、`Phase 1B` の本有効条件は未達。

## 完了条件

- `daily-sync` と `sync-ai-post-reviews` が継続して回る。
- `Phase 1A` の観測と `Phase 1B` の本有効確認を分けて追える。
- `phase1_active=true=30件以上` を Ver03 判断材料にできるだけの観測が貯まる。
