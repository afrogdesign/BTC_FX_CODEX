# NEXT TASK TRACKER

更新日: 2026-05-25 JST

運用メモ: AI の日常入口として使う。履歴や経緯は `履歴/progress.md`、数値詳細は `reports/analysis/` に残し、ここには次判断に必要な情報だけを書く。

## 現在の状況

- 実行系の主状態は `iMac 2019` の `ver02.5-v8`、作業ブランチは `ver02.6-v1`。`paper_positions.csv` を紙ポジション台帳から `pending -> opened -> closed` の状態管理へ拡張中。
- `ver02.6-v1` では役割分担を変更する。診断、設計、再考、フェーズ管理は ChatGPT プロジェクトで行い、Codex は確定済み仕様の実装、検証、Git 操作、常駐確認に徹する。
- 新しい正本は `運用資料/計画/自動取引直前_高速到達計画_20260518.md` と `運用資料/計画/マイルストーン定義.md`。旧計画は `運用資料/計画/archive/superseded/2026-05-18_pre_auto_redesign/` へ退避済み。
- `opportunity_gate`、`paper_positions.csv`、通知ランク `紙実行候補・実弾不可`、日次レポートの紙ポジション集計を実装済み。紙ポジションは `pending -> opened -> closed`、TP2 / SL / timeout / missed_opportunity / entry_not_reached の後追い評価へ拡張中。実弾発注、取引所API送信、秘密鍵連携はまだ行わない。
- `Ver02.5-v7 先行実装パック` を実装済み。15分足の執行精度チェック、`trend_flip_confirmed_up` の弱評価化、詳細HTML/CSV保存、ロードマップ/タイムライン更新まで完了。
- `Ver02.5-v8` は紙ポジション状態遷移、TP2 / SL / timeout / missed_opportunity / entry_not_reached、日次レポートの closed 成績集計を追加する版。最新 commit `9441cf7` を `origin/ver02.5-v8` へ push 済み。全体テスト 179 件 OK。
- 常駐 `com.afrog.btc-monitor` は `Ver02.5-v8` で稼働中。PID `28498`、`state=running`、`logs/heartbeat.txt` は 2026-05-25 15:05 JST、`logs/last_result.json` は 2026-05-25 15:05:07 JST 更新、`logs/runtime/monitor.err` / `ai_post_reviews.err` / `feedback_daily_sync.err` は空。
- フェーズ加速用に `Phase 1B-lite` を追加済み。実装 commit `1401a69`、記録更新 commit `2b22b03` を `origin/ver02.5-v6` へ push 済みで、常駐 `com.afrog.btc-monitor` も最新コードで再起動済み。
- `Phase 1B-lite` は正式 `Phase 1B` でも実弾でもなく、`SWEEP_WAIT` 限定の専用紙トレード観測レーン。
- `Phase 1B` の実行候補はまだ 0 件。`feedback_daily_sync_20260525.md` でも `trade_execution_gate=pass=0件`、`paper_orders planned=0件`。
- 直近の勝率低下とトレンド転換取り逃し対策として、`market_map` 判定を実装・本番反映済み。
- メール文言は、実行候補ではない watch 通知をロング推奨と誤読しにくい表現へ調整済み。
- 通知ランクは `執行候補・強` / `執行候補` / `高優先監視・実行不可` / `通常監視・実行不可` / `注意報・売買非推奨` へ再設計済み。執行候補は `trade_execution_gate=pass` かつ `paper_order_status=planned` のときだけ出る。
- メール件名ラベルは `Ver02.5-v8` で実送信確認済み。`20260519_170500` は `紙実行候補・実弾不可`、`SYSTEM_LABEL=Ver02.5-v8`、`CLI` として保存済み。
- `execution_precision_*` は `logs/csv/trades.csv` と `last_result.json` へ保存済み。詳細HTMLにも `15分足 執行チェック` が出ており、`20260519_170500` では `wait_only` を確認済み。
- `market_map` は shadow 側でも値入り確認済み。`market_map_effectiveness_20260525.md` では 284 件記録あり。
- AI 事後評価は `request_failed=0` を維持。`feedback_daily_sync_20260525.md` では `created=8 / request_failed=0 / backlog=72`、`operational_focus_20260525.md` では未処理候補 37 件。

## 実装済みの前提

- `NO_TRADE_CANDIDATE` は hard flag があるときだけ強い見送りへ落とす。
- `watch + sweep_incomplete` は `watch_sweep_recheck_wait` / `watch_low_execution_recheck_wait` で main/attention を抑制する。
- `confidence_watch_learning` を追加し、`confidence_below_min` でも限定条件を満たす watch 群は `Phase 1A` 観測対象として追える。
- `Phase 1B-lite` は `confidence_watch_learning + SWEEP_WAIT + sweep_incomplete + lower_liquidity_close` かつ危険補助 flag なし、`direction>=55 / execution>=18 / wait<=85` の行だけを `phase1b_lite_paper_orders.csv` に分離保存する。
- `long_reversal_risk`、`counter_long_short_watch`、`failed_breakout_down_reversal` を追加し、上抜け失敗から下落へ切り替わる型を観測できる。
- `market_map` は複数時間足のレジサポ合流、反応回数、直近性、ヒゲ拒否、出来高タッチから主要ラインを作る。
- `market_map` は `support_to_resistance_flip`、`resistance_to_support_flip`、`failed_breakout_*_reversal`、`trend_flip_*` を score/risk/log/メール文言へ流す。
- 標準比較、運用焦点、Phase 1B 候補、失敗ブレイク、market_map readiness、有効性の各レポート CLI は実装済み。
- 作業ブランチは `ver02.5-v8` へ切り替え済み。
- 実装済みの計画書は `運用資料/計画/archive/implemented/2026-05-18/` へ整理済み。

## 直近の基準値

- 最新 daily-sync 基準: `feedback_daily_sync_20260525.md`。完了 39 件、近似PF 0.98、全体勝率 51.3%。`phase1_active=true` が 1 件出たが、`trade_execution_gate=pass` は 0 件。
- `paper_positions.csv` は daily-sync 集計で `closed=17件`、`sl_hit=9件`、`missed_opportunity=6件`、`tp2_hit=1件`、`timeout=1件`、24h超 pending 0件。`market_map_opportunity` は 9件 / 勝率 11.1% / 平均R 0.51 / 簡易PF 2.53。
- 新規ログ基準: `2026-04-18` 〜 `2026-05-25` では `notified_rr_to_entry=0件`、`notified_rr_to_entry_orderbook_ask_heavy=0件`、`rr_to_confidence=1件` を維持。
- `operational_focus_20260525.md`: Phase1 pass 163 件 / blocked 722 件。blocked 上位は `confidence_below_min=507件`、`no_trade_candidate=254件`。
- `relaxation_candidates_20260525.md`: 緩和候補 51 件。`SWEEP_WAIT=33件`、`RISKY_ENTRY=16件`、`NO_TRADE_CANDIDATE=2件`。平均 `execution=18.2 / wait=84.2` で一律緩和にはまだ弱い。
- `phase1b_promotion_candidates_20260525.md`: 候補 6 件、勝率 100.0%、TP1先行 100.0%、近似PF 1.26。ただし新規候補は増えておらず、正式 gate 緩和材料にはまだしない。
- `Phase 1B-lite`: lite 候補 5 件、専用紙トレード observing 5 件。10〜15 件の成功条件にはまだ未達。
- `market_map_effectiveness_20260525.md`: `2026-05-13` 以降の shadow 288 行中 284 件で `market_map` 記録あり。`support_to_resistance_flip=180件` は勝率 59.6%、平均MFE24h 7.23 / 平均MAE24h 5.28 と相対的に有効。
- `trend_flip_confirmed_up=29件` は勝率 37.5%、wrong_rate 31.0%、平均MFE24h 2.34 / 平均MAE24h 11.43 でまだ弱いため、上方向の強評価や gate 緩和には使わない。
- `paper_opportunity_diagnostics_20260525.md`: 5/13〜5/25 の紙ポジションは closed 135件 / 平均R 0.36 / 簡易PF 1.96。`market_map_opportunity` は 94件 / 平均R 0.40 / 簡易PF 2.16 だが、`long` は 18件 / 平均R -0.51 / 簡易PF 0.29、`wait>=60` は 36件 / 平均R -0.09 / 簡易PF 0.85 と弱い。
- AI 事後評価 health は `feedback_daily_sync_20260525.md` 基準で `eligible=347 / AI済み=275 / backlog=72 / created=8 / request_failed=0`。daily cap 8 は継続可能。

## 次のタスク

1. `phase1_active=true` が 1 件出たが、`trade_execution_gate=pass=0件` と `paper_orders planned=0件` は継続。実弾 gate 緩和ではなく、まず本有効候補の増加と再現性を見る。
2. 次の診断、設計、フェーズ判断は ChatGPT プロジェクトへ渡す。Codex は ChatGPT 側で確定した仕様を受けて実装する。
3. `sl_hit` と `missed_opportunity` が多いため、entry 条件と待機条件のズレを ChatGPT 側で再設計対象にする。
4. `market_map_opportunity` は累計では改善したが、`long`、`wait>=60`、`resistance_to_support_flip`、`trend_flip_confirmed_up` は弱い。紙候補からの抑制案は ChatGPT 側で検討する。
5. `trend_flip_confirmed_up` は 29 件でも弱い。次回 30 件到達時点の扱いは ChatGPT 側で再判定する。
6. `Phase 1B-lite` は 5 件で止まっている。10〜15 件まで専用CSVで追い、正式 `Phase 1B` へはまだ上げない。
7. AI backlog は 72 件で `request_failed=0`。daily cap 8 を維持し、backlog が自然減するか確認する。

## 残作業一覧

- 次回 `market_map_effectiveness_YYYYMMDD.md` を更新し、`trend_flip_confirmed_up` が 30 件に到達した時点で上方向転換系の扱いを再判定する。
- `com.afrog.btc-monitor` は `Ver02.5-v8` で稼働中。PID `28498`、`state=running`、`logs/runtime/monitor.err` は空。定時サイクルは 2026-05-25 15:05 JST まで更新確認済み。
- `feedback_daily_sync_YYYYMMDD.md` を次回生成し、AI事後評価の `eligible / AI済み / backlog / created / request_failed` を更新する。現状は `request_failed=0` だが backlog は 72 件残っている。
- AI事後評価の `AI_POST_REVIEW_DAILY_MAX=8` は安定確認済み。`request_failed` が増える場合だけ 4 または 6 へ戻す。
- 標準比較 3 本は 2026-05-25 基準でも `0 / 0 / 1` を維持。次回 daily-sync 後も崩れた箇所だけを見る。
- `market_map` は 284 件まで増えた。下方向側は相対的に有効だが、紙実行候補では `long` / 高 wait / 上方向転換系が弱いため、実弾 gate 緩和ではなく entry / wait 条件の検証を優先する。
- `paper_opportunity_diagnostics_YYYYMMDD.md` を次回も更新し、直近日次の悪化が一時的か、`long` / 高 wait 側の構造的な弱さかを切り分ける。
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
