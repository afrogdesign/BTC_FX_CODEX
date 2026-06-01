# NEXT TASK TRACKER

更新日: 2026-06-01 JST

運用メモ: AI の日常入口として使う。履歴や経緯は `履歴/progress.md`、数値詳細は `reports/analysis/` に残し、ここには次判断に必要な情報だけを書く。

## 現在のブランチ

- 現在の作業ブランチ: `ver02.6-v2`
- 運用本体の参照ブランチ: `ver02.5-v8`
- 新しいブランチを切ったら、この節を同じ作業単位で必ず更新する。

## ChatGPT が最初に開くレポート

1. `運用資料/reports/report_hub_latest.md`
2. `運用資料/reports/feedback_daily_sync_20260601.md`
3. `運用資料/reports/analysis/market_map_effectiveness_20260526.md`
4. `運用資料/reports/analysis/operational_focus_20260526.md`
5. `運用資料/reports/analysis/paper_opportunity_diagnostics_20260601.md`
6. 設計テーマが `sl_hit` 偏重なら `運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260526.md`

## ChatGPT が次に引き継ぐ分析メモ

- `chatgpt/analysis/20260526_entry_sl_tp_wait_redesign.md`
- `chatgpt/analysis/20260526_trend_flip_confirmed_up_reassessment.md`

`chatgpt/specs/active/` が空のとき、ChatGPT はこの2本を継続メモとして使い、設計が固まったら `chatgpt/specs/active/` に確定仕様を書く。

## 現在の状況

- 実行系の主状態は `iMac 2019` の `ver02.6-v2`。現在の常駐 `com.afrog.btc-monitor` はこの worktree の branch / commit で動いている。`paper_positions.csv` を紙ポジション台帳から `pending -> opened -> closed` の状態管理へ拡張中。
- `ver02.6-v2` では役割分担を変更する。診断、設計、再考、フェーズ管理は ChatGPT プロジェクトで行い、Codex は確定済み仕様の実装、検証、Git 操作、常駐確認に徹する。
- 新しい正本は `運用資料/計画/自動取引直前_高速到達計画_20260518.md` と `運用資料/計画/マイルストーン定義.md`。旧計画は `運用資料/計画/archive/superseded/2026-05-18_pre_auto_redesign/` へ退避済み。
- `opportunity_gate`、`paper_positions.csv`、通知ランク `紙実行候補・実弾不可`、日次レポートの紙ポジション集計を実装済み。紙ポジションは `pending -> opened -> closed`、TP2 / SL / timeout / missed_opportunity / entry_not_reached の後追い評価へ拡張中。実弾発注、取引所API送信、秘密鍵連携はまだ行わない。
- `Ver02.5-v7 先行実装パック` を実装済み。15分足の執行精度チェック、`trend_flip_confirmed_up` の弱評価化、詳細HTML/CSV保存、ロードマップ/タイムライン更新まで完了。
- 旧 `Ver02.5-v8` は紙ポジション状態遷移、TP2 / SL / timeout / missed_opportunity / entry_not_reached、日次レポートの closed 成績集計を追加した節目版。現在の実行コードは `ver02.6-v2` へ進んでいる。
- 常駐 `com.afrog.btc-monitor` は `ver02.6-v2` で稼働中。直近のローカル更新痕跡として、`logs/heartbeat.txt` と `logs/last_result.json` は 2026-06-01 03:05 更新を確認した。`logs/runtime/monitor.err` / `ai_post_reviews.err` / `feedback_daily_sync.err` は空。
- フェーズ加速用に `Phase 1B-lite` を追加済み。実装 commit `1401a69`、記録更新 commit `2b22b03` を `origin/ver02.5-v6` へ push 済みで、常駐 `com.afrog.btc-monitor` も最新コードで再起動済み。
- `Phase 1B-lite` は正式 `Phase 1B` でも実弾でもなく、`SWEEP_WAIT` 限定の専用紙トレード観測レーン。
- `Phase 1B` の実行候補はまだ 0 件。`feedback_daily_sync_20260601.md` でも `trade_execution_gate=pass=0件`、`paper_orders planned=0件`。
- 直近の勝率低下とトレンド転換取り逃し対策として、`market_map` 判定を実装・本番反映済み。
- メール文言は、実行候補ではない watch 通知をロング推奨と誤読しにくい表現へ調整済み。
- 通知ランクは `執行候補・強` / `執行候補` / `高優先監視・実行不可` / `通常監視・実行不可` / `注意報・売買非推奨` へ再設計済み。執行候補は `trade_execution_gate=pass` かつ `paper_order_status=planned` のときだけ出る。
- メール件名ラベルの正本は `SYSTEM_LABEL=Ver02.6-v2`。現在の branch 名と揃えて運用する。
- `execution_precision_*` は `logs/csv/trades.csv` と `last_result.json` へ保存済み。詳細HTMLにも `15分足 執行チェック` が出ており、`20260519_170500` では `wait_only` を確認済み。
- `market_map` は shadow 側でも値入り確認済み。`market_map_effectiveness_20260526.md` では 305 件記録あり。
- AI 事後評価は `request_failed=0` を維持。最新 `feedback_daily_sync_20260601.md` 基準では `created=8 / request_failed=0 / backlog=54`。
- `ver02.6-v2` では `src/trade/opportunity_gate.py` に paper opportunity quality guard の hard / soft 分離まで反映済み。`trade_execution_gate` と `phase1b_lite_gate` は変更していない。
- 既存 CLI でレポートを再生成し、`feedback_daily_sync_20260601.md` と `paper_opportunity_diagnostics_20260601.md` に hard / soft 集計を反映済み。
- `chatgpt/specs/active/` は現在 `.gitkeep` のみ。直近の quality guard 仕様は `archive/` へ移動済みで、次の実装は ChatGPT 側の新しい確定仕様待ち。

## 実装済みの前提

- `NO_TRADE_CANDIDATE` は hard flag があるときだけ強い見送りへ落とす。
- `watch + sweep_incomplete` は `watch_sweep_recheck_wait` / `watch_low_execution_recheck_wait` で main/attention を抑制する。
- `confidence_watch_learning` を追加し、`confidence_below_min` でも限定条件を満たす watch 群は `Phase 1A` 観測対象として追える。
- `Phase 1B-lite` は `confidence_watch_learning + SWEEP_WAIT + sweep_incomplete + lower_liquidity_close` かつ危険補助 flag なし、`direction>=55 / execution>=18 / wait<=85` の行だけを `phase1b_lite_paper_orders.csv` に分離保存する。
- `long_reversal_risk`、`counter_long_short_watch`、`failed_breakout_down_reversal` を追加し、上抜け失敗から下落へ切り替わる型を観測できる。
- `market_map` は複数時間足のレジサポ合流、反応回数、直近性、ヒゲ拒否、出来高タッチから主要ラインを作る。
- `market_map` は `support_to_resistance_flip`、`resistance_to_support_flip`、`failed_breakout_*_reversal`、`trend_flip_*` を score/risk/log/メール文言へ流す。
- 標準比較、運用焦点、Phase 1B 候補、失敗ブレイク、market_map readiness、有効性の各レポート CLI は実装済み。
- 現行の作業ブランチ兼実行ブランチは `ver02.6-v2`。
- 実装済みの計画書は `運用資料/計画/archive/implemented/2026-05-18/` へ整理済み。

## 直近の基準値

- 最新 daily-sync 基準: `feedback_daily_sync_20260601.md`。完了 33 件、近似PF 1.49、全体勝率 66.7%。`phase1_active=true` は 0 件、`trade_execution_gate=pass` は 0 件。
- `paper_positions.csv` は daily-sync 集計で `closed=14件`、`sl_hit=5件`、`missed_opportunity=6件`、`tp2_hit=2件`、`timeout=1件`、24h超 pending 0件。`market_map_opportunity` は 5件 / 勝率 20.0% / 平均R 1.26 / 簡易PF 0.00。
- 新規ログ基準: `2026-04-18` 〜 `2026-05-26` では `notified_rr_to_entry=0件`、`notified_rr_to_entry_orderbook_ask_heavy=0件`、`rr_to_confidence=1件` を維持。
- `operational_focus_20260526.md`: Phase1 pass 167 件 / blocked 739 件。blocked 上位は `confidence_below_min=519件`、`no_trade_candidate=263件`。
- `relaxation_candidates_20260526.md`: 緩和候補 51 件。`SWEEP_WAIT=33件`、`RISKY_ENTRY=16件`、`NO_TRADE_CANDIDATE=2件`。平均 `execution=18.2 / wait=84.2` で一律緩和にはまだ弱い。
- `phase1b_promotion_candidates_20260526.md`: 候補 6 件、勝率 100.0%、TP1先行 100.0%、近似PF 1.26。ただし新規候補は増えておらず、正式 gate 緩和材料にはまだしない。
- `Phase 1B-lite`: lite 候補 5 件、専用紙トレード observing 5 件。10〜15 件の成功条件にはまだ未達。
- `market_map_effectiveness_20260526.md`: `2026-05-13` 以降の shadow 305 行中 305 件で `market_map` 記録あり。`support_to_resistance_flip=194件` は勝率 56.4%、平均MFE24h 6.91 / 平均MAE24h 5.44 と相対的に有効。
- `trend_flip_confirmed_up=32件` は勝率 41.2%、wrong_rate 28.1%、平均MFE24h 2.50 / 平均MAE24h 10.85 でまだ弱いため、上方向の強評価や gate 緩和には使わない。
- `paper_opportunity_diagnostics_20260526.md`: 4/18〜5/26 の紙ポジションは closed 264件 / 平均R 0.33 / 簡易PF 1.82。`market_map_opportunity` は 97件 / 平均R 0.36 / 簡易PF 1.97 だが、`long` は 18件 / 平均R -0.51 / 簡易PF 0.29、`wait>=60` は 39件 / 平均R -0.16 / 簡易PF 0.74 と弱い。
- `paper_entry_sl_wait_redesign_20260526.md`: `sl_hit` 原因を切り分ける追加診断を実施。`wait>=80` は 7件 / 平均R -0.84 / `sl_hit=6件`、`execution<20` は 44件 / 平均R -0.02 / `sl_hit=29件`、`long` は 18件 / 平均R -0.51 / `sl_hit=15件`、`trend_flip_confirmed_up` は 7件すべて `sl_hit`。SL 失敗分類は `late_wait_sl=20件`、`trend_flip_long_sl=10件`、`other_sl=18件`。proposal は `suppress_long_high_wait`、`suppress_trend_flip_up_strong`、`require_execution_for_high_wait`、`delay_entry_on_sweep_wait` を出力した。
- AI 事後評価 health は `feedback_daily_sync_20260601.md` 基準で `eligible=393 / AI済み=339 / backlog=54 / created=8 / request_failed=0`。daily cap 8 は継続可能。
- 最新 daily-sync 基準は `feedback_daily_sync_20260601.md`。`trade_execution_gate=pass=0件`、`paper_orders planned=0件`、`quality guard blocked=1件`、`hard_quality_blocked=1件`、`soft_quality_risk=1件`、`market_map opportunity before/after hard guard=24件 -> 5件`。
- AI事後評価は今後 `feedback_daily_sync` だけでなく `paper_opportunity_diagnostics` と `paper_entry_sl_wait_redesign` の設計根拠にも使う。`human_override` は例外で、日常判断は AI 評価を主系にする。

## 次のタスク

1. 最新 daily-sync は `2026-06-01` 基準で `hard_quality_blocked=1件`、`soft_quality_risk=1件`、`trade_execution_gate=pass=0件`、`paper_orders planned=0件`。Phase 1B や実弾寄りの緩和は進めず、hard / soft の推移を観測継続する。
2. 次の診断、設計、フェーズ判断は ChatGPT プロジェクトへ渡す。Codex は ChatGPT 側で確定した仕様を受けて実装する。
3. `paper_entry_sl_wait_redesign_20260526.md` で `sl_hit` の主因が高 wait、低 execution、long、上方向転換系に偏ることを追加確認した。ChatGPT 側は entry 発火条件、SL/TP 条件、wait/execution 抑制条件を分けて再設計する。
4. `market_map_opportunity` は累計では改善したが、`long`、`wait>=60`、`resistance_to_support_flip`、`trend_flip_confirmed_up` は弱い。特に `wait>=80` と `execution<20` の抑制案は ChatGPT 側で具体化する。
5. `trend_flip_confirmed_up` は 32 件に到達したが依然弱く、紙ポジションでも 7 件すべて `sl_hit`。上方向転換系を強評価へ戻さず、次の扱いは ChatGPT 側で再判定する。
6. `Phase 1B-lite` は 5 件で止まっている。10〜15 件まで専用CSVで追い、正式 `Phase 1B` へはまだ上げない。
7. AI backlog は 54 件で `request_failed=0`。daily cap 8 を維持し、backlog が自然減するか確認する。
8. `paper_entry_sl_wait_redesign` は専用 CLI が見当たらず、今回の再生成対象から外した。既存 report builder 構造の中でどこに置くかを ChatGPT 側で判断する。
9. `quality_guard_effectiveness_20260601.md` を追加し、daily-sync と paper diagnostics の `quality guard` 件数差は母集団差として整理した。`guard該当 closed sl_hit=0件` は成功証拠ではなく、保存仕様と集計母集団差を含めて解釈する。
10. 次に見る論点は `counterfactual_quality_guard` の正式 builder 化要否と、`paper_entry_sl_wait_redesign` builder の扱いである。guard 条件そのものは今回は変更しない。
11. `quality_guard_effectiveness_20260601.md` に reason別・複合条件別 counterfactual を追加した。次に ChatGPT が見るべき論点は、reason組み合わせ別の `sl_hit_rate` と `tp2_hit / missed_opportunity` 巻き込み率であり、guard 条件変更はまだ行っていない。
12. builder 正式化は次回以降の論点とし、今回は `paper_positions.csv` と `shadow_log.csv` の後付け再計算で材料整理だけを行った。
13. `paper opportunity quality guard` の hard / soft 分離を実装し、仕様書は `chatgpt/specs/archive/20260601_quality_guard_hard_soft_split.md` へ移した。`A=require_execution_for_high_wait` を含む group は hard blocker、`B/C` 単独と `B+C` は soft risk として扱う。
14. `trade_execution_gate` と `phase1b_lite_gate` は変更していない。`soft_quality_risk=1件` と少数のため、次回もまず観測継続とし、継続的に積み上がる場合だけ soft risk 側の閾値再調整を検討する。

## 残作業一覧

- `trend_flip_confirmed_up` は 32 件に到達したため、`market_map_effectiveness_20260526.md` を基準に ChatGPT 側で上方向転換系の扱いを再判定する。
- `com.afrog.btc-monitor` は `ver02.6-v2` で稼働中。ローカル更新痕跡として `logs/heartbeat.txt` と `logs/last_result.json` は 2026-06-01 03:05 更新、`logs/runtime/monitor.err` は空を確認済み。次サイクル確認待ち。
- `feedback_daily_sync_YYYYMMDD.md` を次回生成し、AI事後評価の `eligible / AI済み / backlog / created / request_failed` を更新する。現状は `request_failed=0` だが backlog は 54 件残っている。
- `paper_opportunity_diagnostics_20260601.md` の quality guard 集計を基準に、`require_execution_for_high_wait`、`suppress_long_high_wait`、`suppress_trend_flip_up_strong` が `sl_hit` 偏重の抑制に効くかを次回も追う。
- `quality_guard_effectiveness_20260601.md` を基準に、daily-sync の新規観測と diagnostics の累積 closed 母集団を混同せずに評価する。必要なら `counterfactual_quality_guard` を report builder 化する。
- `quality_guard_effectiveness_20260601.md` の reason組み合わせ別表を基準に、`A only`、`B only`、`C only`、`A+B` のどこを維持し、どこを閾値再調整候補にするかを ChatGPT 側で判断する。
- hard / soft 分離後は、`hard_quality_blocked` と `soft_quality_risk` の推移を基準に、`A` を維持したまま `B/C` 単独の扱いをさらに調整するかを ChatGPT 側で決める。
- 次回は `daily-sync` と `paper_opportunity_diagnostics` で `hard_quality_blocked` と `soft_quality_risk` の推移を見る。
- AI事後評価の `AI_POST_REVIEW_DAILY_MAX=8` は安定確認済み。`request_failed` が増える場合だけ 4 または 6 へ戻す。
- 標準比較 3 本は 2026-05-26 基準でも `0 / 0 / 1` を維持。次回 daily-sync 後も崩れた箇所だけを見る。
- `market_map` は 305 件まで増えた。下方向側は相対的に有効だが、紙実行候補では `long` / 高 wait / 上方向転換系が弱いため、実弾 gate 緩和ではなく entry / wait 条件の検証を優先する。
- `paper_opportunity_diagnostics_YYYYMMDD.md` を次回も更新し、`sl_hit` 偏重が一時的か、`long` / 高 wait / trend_flip_confirmed_up 側の構造的な弱さかを切り分ける。
- `paper_entry_sl_wait_redesign_YYYYMMDD.md` を次回も更新し、`late_wait_sl` / `trend_flip_long_sl` の比率変化と proposal の妥当性を追う。`mfe_atr` / `mae_atr` / `rr_estimate` は 97 件欠損しているため、数値補強が入るまでは thin RR 判定を過信しない。
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
