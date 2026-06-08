# NEXT TASK TRACKER

更新日: 2026-06-08 JST

運用メモ: AI の日常入口として使う。履歴や経緯は `履歴/progress.md`、数値詳細は `reports/analysis/` に残し、ここには次判断に必要な情報だけを書く。

## 現在のブランチ

- 現在の作業ブランチ: `Ver03-v1`
- Ver03-v1 は、Ver02.6-v2 までの資産を土台に Active Trade Plan レイヤーを追加する再設計ブランチ。
- 実弾発注、取引所API送信、秘密鍵連携はまだ行わない。
- `trade_execution_gate` は高信頼 gate として維持し、実務上の行動計画は `active_trade_plan` で別レーン化する。

## ChatGPT が最初に開くレポート

1. `運用資料/reports/report_hub_latest.md`
2. `運用資料/計画/Ver03-v1_現行資産棚卸し_20260607.md`
3. `運用資料/reports/analysis/active_trade_plan_diagnostics_20260608.md`
4. `運用資料/reports/feedback_daily_sync_20260607.md`
5. `運用資料/reports/analysis/market_map_effectiveness_20260607.md`
6. `運用資料/reports/analysis/paper_opportunity_diagnostics_20260607.md`

注記:
- `feedback_daily_sync_20260608.md` はローカル未追跡として存在する可能性があるが、現時点では Ver03-v1 の正本参照に入れない。
- `active_plan_candidates.csv` はまだ未生成のため、Active Plan 診断はレーン接続確認段階。
- Active Plan runtime確認手順: `運用資料/計画/Ver03-v1_ActivePlan_runtime確認手順_20260608.md`

## ChatGPT が次に引き継ぐ分析メモ

- `chatgpt/analysis/20260526_entry_sl_tp_wait_redesign.md`
- `chatgpt/analysis/20260526_trend_flip_confirmed_up_reassessment.md`
- `chatgpt/analysis/20260601_entry_recheck_counterfactual_next_judgement.md`

`chatgpt/specs/active/` が空のとき、ChatGPT はこの3本を継続メモとして使い、設計が固まったら `chatgpt/specs/active/` に確定仕様を書く。

## 現在の状況

### Ver03-v1 現在の状況

- `BTCFX-20260607-031` で `運用資料/計画/Ver03-v1_現行資産棚卸し_20260607.md` を作成済み。commit: `fad5316`
- `BTCFX-20260608-032` で `active_trade_plan` 候補を `logs/csv/active_plan_candidates.csv` へ記録するレーンを追加済み。commit: `2546081`
- `BTCFX-20260608-033` で `active_trade_plan_diagnostics_YYYYMMDD.md` builder / CLI を追加済み。commit: `bb0208f`
- `main.py` は `active_trade_plan` を生成し、`active_primary_action` と `active_headline` を payload に入れる。
- `src/storage/csv_logger.py` は `active_trade_plan` の主要列を `trades.csv` へ保存し、候補別CSV `active_plan_candidates.csv` も出力できる。
- 2026-06-08 時点の `active_trade_plan_diagnostics_20260608.md` では、`active_plan_candidates.csv: missing`。これは、032以降の新しい監視サイクルがまだ候補CSVを生成していないため。
- 既存 `trades.csv` は 2075 行あるが、過去データのため `active_primary_action` は blank。
- 次に必要なのは、新しい監視サイクルで `active_plan_candidates.csv` が生成されることを確認し、その後に Active Plan 候補別 outcome / daily-sync 接続へ進むこと。
- 既知のローカル未追跡ファイルは、別作業で採用・保留・削除を判断する。今回の正本には混ぜない。

- 実行系の主状態は `iMac 2019` の `ver02.6-v2`。現在の常駐 `com.afrog.btc-monitor` はこの worktree の branch / commit で動いている。`paper_positions.csv` を紙ポジション台帳から `pending -> opened -> closed` の状態管理へ拡張中。
- `ver02.6-v2` では役割分担を変更する。診断、設計、再考、フェーズ管理は ChatGPT プロジェクトで行い、Codex は確定済み仕様の実装、検証、Git 操作、常駐確認に徹する。
- 新しい正本は `運用資料/計画/自動取引直前_高速到達計画_20260518.md` と `運用資料/計画/マイルストーン定義.md`。旧計画は `運用資料/計画/archive/superseded/2026-05-18_pre_auto_redesign/` へ退避済み。
- `opportunity_gate`、`paper_positions.csv`、通知ランク `紙実行候補・実弾不可`、日次レポートの紙ポジション集計を実装済み。紙ポジションは `pending -> opened -> closed`、TP2 / SL / timeout / missed_opportunity / entry_not_reached の後追い評価へ拡張中。実弾発注、取引所API送信、秘密鍵連携はまだ行わない。
- `Ver02.5-v7 先行実装パック` を実装済み。15分足の執行精度チェック、`trend_flip_confirmed_up` の弱評価化、詳細HTML/CSV保存、ロードマップ/タイムライン更新まで完了。
- 旧 `Ver02.5-v8` は紙ポジション状態遷移、TP2 / SL / timeout / missed_opportunity / entry_not_reached、日次レポートの closed 成績集計を追加した節目版。現在の実行コードは `ver02.6-v2` へ進んでいる。
- 常駐 `com.afrog.btc-monitor` は `ver02.6-v2` で稼働中。直近のローカル更新痕跡として、`logs/heartbeat.txt` と `logs/last_result.json` は 2026-06-01 03:05 更新を確認した。`logs/runtime/monitor.err` / `ai_post_reviews.err` / `feedback_daily_sync.err` は空。
- フェーズ加速用に `Phase 1B-lite` を追加済み。実装 commit `1401a69`、記録更新 commit `2b22b03` を `origin/ver02.5-v6` へ push 済みで、常駐 `com.afrog.btc-monitor` も最新コードで再起動済み。
- `Phase 1B-lite` は正式 `Phase 1B` でも実弾でもなく、`SWEEP_WAIT` 限定の専用紙トレード観測レーン。
- `Phase 1B` の実行候補はまだ 0 件。最新 `feedback_daily_sync_20260607.md` でも `trade_execution_gate=pass=0件`、`paper_orders planned=0件`。
- 直近の勝率低下とトレンド転換取り逃し対策として、`market_map` 判定を実装・本番反映済み。
- メール文言は、実行候補ではない watch 通知をロング推奨と誤読しにくい表現へ調整済み。
- 通知ランクは `執行候補・強` / `執行候補` / `高優先監視・実行不可` / `通常監視・実行不可` / `注意報・売買非推奨` へ再設計済み。執行候補は `trade_execution_gate=pass` かつ `paper_order_status=planned` のときだけ出る。
- メール件名ラベルの正本は `SYSTEM_LABEL=Ver02.6-v2`。現在の branch 名と揃えて運用する。
- `execution_precision_*` は `logs/csv/trades.csv` と `last_result.json` へ保存済み。詳細HTMLにも `15分足 執行チェック` が出ており、`20260519_170500` では `wait_only` を確認済み。
- `market_map` は shadow 側でも値入り確認済み。最新 `market_map_effectiveness_20260607.md` では 589 件記録あり。
- AI 事後評価は `request_failed=0` を維持。最新 `feedback_daily_sync_20260607.md` 基準では `created=8 / request_failed=0 / backlog=46`。
- `ver02.6-v2` では `src/trade/opportunity_gate.py` に paper opportunity quality guard の hard / soft 分離まで反映済み。`trade_execution_gate` と `phase1b_lite_gate` は変更していない。
- 既存 CLI でレポートを再生成し、`feedback_daily_sync_20260601.md` と `paper_opportunity_diagnostics_20260601.md` に hard / soft 集計を反映済み。
- `counterfactual_quality_guard` builder を `tools/log_feedback.py` に実装し、`./.venv312/bin/python tools/log_feedback.py --quality-guard-effectiveness` で `運用資料/reports/analysis/quality_guard_effectiveness_20260601.md` を再生成した。
- report hub は `./.venv312/bin/python tools/log_feedback.py --report-hub` で更新済み。`trade_execution_gate` / `phase1b_lite_gate` / `opportunity_gate` は今回も変更していない。
- 実施済み仕様 `chatgpt/specs/archive/20260601_counterfactual_quality_guard_builder.md` と `chatgpt/specs/archive/20260601_quality_guard_effectiveness_metric_split.md` へ移動済み。BTCFX-20260601-02 で `quality_guard_effectiveness` の entered / non-entered split、`entered_avg_R` / `non_entered_avg_R` / `judgement` を実装し、`trade_execution_gate` / `phase1b_lite_gate` / `opportunity_gate` は変更していない。
- BTCFX-20260601-04 で `paper_entry_sl_wait_redesign` report の正式 builder / CLI 化を実装済み。`build_paper_entry_sl_wait_redesign_report(...)`、`build-paper-entry-sl-wait-redesign-report`、`--paper-entry-sl-wait-redesign` を追加し、report hub は最新 `paper_entry_sl_wait_redesign_20260601.md` を参照するよう更新済み。`trade_execution_gate` / `phase1b_lite_gate` / `opportunity_gate` は変更せず、active spec は `chatgpt/specs/archive/20260601_paper_entry_sl_wait_redesign_builder.md` へ移動済み。
- BTCFX-20260601-05 で次回実装用 active spec `chatgpt/specs/active/20260601_soft_risk_collateral_damage_report.md` を作成。目的は B/C 単独 soft risk の collateral damage を評価する report builder / CLI 化で、今回は仕様作成のみ（実装は次回）。
- BTCFX-20260601-06 で `soft_risk_collateral_damage` report の builder / CLI 化を実装済み。`build_soft_risk_collateral_damage_report(...)`、`build-soft-risk-collateral-damage-report`、`--soft-risk-collateral-damage` を追加し、report hub は最新 `soft_risk_collateral_damage_20260601.md` を参照するよう更新済み。B/C 単独 soft risk は現時点で hard blocker 化せず、`trade_execution_gate` / `phase1b_lite_gate` / `opportunity_gate` は変更していない。active spec は `chatgpt/specs/archive/20260601_soft_risk_collateral_damage_report.md` へ移動済み。
- BTCFX-20260601-07 で次回実装用 active spec `chatgpt/specs/active/20260601_entry_wait_price_distance_redesign.md` を作成。目的は high wait / low execution / long弱さ / trend_flip_confirmed_up 弱さを踏まえた entry / wait / price-distance 再設計で、今回は仕様作成のみ（実装は次回）。
- BTCFX-20260601-08 で `entry / wait / price-distance` 再設計を実装済み。`entry_recheck_required_high_wait` / `entry_recheck_required_low_execution` / `entry_recheck_required_long_weakness` / `entry_recheck_required_trend_flip_up` / `price_distance_missing` を `market_map_opportunity` 候補の再確認 reason に追加し、`trade_execution_gate` / `phase1b_lite_gate` / 既存 hard quality guard は変更していない。B/C 単独 soft risk は hard blocker 化せず、`trend_flip_confirmed_up` を強評価へ戻していない。active spec は `chatgpt/specs/archive/20260601_entry_wait_price_distance_redesign.md` へ移動済み。
- BTCFX-20260601-09 で次回実装用 active spec `chatgpt/specs/active/20260601_entry_recheck_impact_report.md` を作成。
- 目的は BTCFX-20260601-08 で追加した entry recheck reason の影響を `paper_entry_sl_wait_redesign` report 内で見える化すること。
- 今回は仕様作成のみ。実装は次回。
- BTCFX-20260601-10 で `paper_entry_sl_wait_redesign` report に `entry recheck reason impact` を追加済み。
- BTCFX-20260601-08 で追加した entry recheck reason の影響を既存 report 内で確認可能にした。
- 新しい standalone report は追加していない。
- `trade_execution_gate` / `phase1b_lite_gate` は変更していない。
- B/C 単独 soft risk は hard blocker 化していない。
- active spec は archive 済み。
- BTCFX-20260601-11 で次回実装用 active spec `chatgpt/specs/active/20260601_entry_recheck_counterfactual_impact.md` を作成。
- 目的は BTCFX-20260601-08 の entry recheck reason を過去 market_map_opportunity に後付け再計算し、counterfactual impact として `paper_entry_sl_wait_redesign` report 内で確認できるようにすること。
- 今回は仕様作成のみ。実装は次回。
- BTCFX-20260601-12 で `paper_entry_sl_wait_redesign` report に `entry recheck counterfactual impact` を追加済み。
- BTCFX-20260601-08 の recheck 条件を過去 market_map_opportunity 行へ後付け再計算し、logged impact と counterfactual impact の差を同一 report 内で確認可能にした。
- 新しい standalone report は追加していない。
- `trade_execution_gate` / `phase1b_lite_gate` は変更していない。
- B/C 単独 soft risk は hard blocker 化していない。
- active spec は archive 済み。
- BTCFX-20260601-13 で analysis `chatgpt/analysis/20260601_entry_recheck_counterfactual_next_judgement.md` を作成。
- `chatgpt/specs/active/` は `.gitkeep` のみで、active spec はまだ空のまま。
- 次回 ChatGPT は上記 analysis を先に読み、次に active spec 化する対象（entry recheck 条件微調整 / collateral damage 追加診断）を判断する。
- BTCFX-20260601-14 で active spec `chatgpt/specs/active/20260601_entry_recheck_collateral_damage_breakdown.md` を作成。
- 次回はこの active spec を正本に、paper_entry_sl_wait_redesign report へ collateral damage breakdown を実装する。
- BTCFX-20260601-15 で entry recheck collateral damage breakdown を実装。
- paper_entry_sl_wait_redesign_20260601.md に新セクションを追加。
- active spec は archive 済み。
- 次回は breakdown 結果を読んで、high_wait / low_execution の条件微調整に進むか判断。

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

- 最新 daily-sync 基準: `feedback_daily_sync_20260607.md`。完了 37 件、近似PF 10.18、全体勝率 97.3%。`phase1_active=true` は 0 件、`trade_execution_gate=pass` は 0 件。
- `paper_positions.csv` は daily-sync 集計で `closed=11件`、`sl_hit=1件`、`missed_opportunity=7件`、`tp2_hit=2件`、`timeout=1件`、24h超 pending 0件。`market_map_opportunity` は 1件 / 勝率 0.0% / 平均R 0.00 / 簡易PF 0.00。
- 標準比較 3 本は `2026-04-18` 〜 `2026-06-07` 基準でも `notified_rr_to_entry=0件`、`notified_rr_to_entry_orderbook_ask_heavy=0件`、`rr_to_confidence=1件` を維持。
- `operational_focus_20260607.md`: Phase1 pass 265 件 / blocked 925 件。blocked 上位は `confidence_below_min=594件`、`no_trade_candidate=359件`。
- `relaxation_candidates_20260607.md`: 緩和候補の最新棚卸しを 6/7 基準で再生成済み。引き続き一律緩和には使わず、ChatGPT 側の設計判断材料として使う。
- `phase1b_promotion_candidates_20260607.md`: 昇格候補の最新棚卸しを 6/7 基準で再生成済み。候補は 6 件のままで、正式 gate 緩和材料にはまだ使わない。
- `Phase 1B-lite`: lite 候補 0 件、専用紙トレード observing 5 件。10〜15 件の成功条件にはまだ未達。
- `market_map_effectiveness_20260607.md`: `2026-05-13` 以降の shadow 593 行中 589 件で `market_map` 記録あり。`support_to_resistance_flip=385件` は勝率 70.2%、平均MFE24h 9.67 / 平均MAE24h 3.46 と相対的に有効。
- `trend_flip_confirmed_up=49件` は勝率 36.4%、wrong_rate 32.7%、平均MFE24h 2.91 / 平均MAE24h 9.06 でまだ弱いため、上方向の強評価や gate 緩和には使わない。
- `paper_opportunity_diagnostics_20260607.md`: 4/18〜6/7 の紙ポジションは closed 376件 / 平均R 0.51 / 簡易PF 2.58。`market_map_opportunity` は 117件 / 平均R 0.37 / 簡易PF 2.05 だが、`execution<24` は 79件 / 平均R 0.09 / 簡易PF 1.21、`wait>=80` は 7件 / 平均R -0.84 と弱い。
- `paper_entry_sl_wait_redesign_20260607.md`: 最新の `entry/wait/sl` 再設計診断を再生成済み。high wait / low execution / long / trend_flip_confirmed_up は引き続き recheck 候補で、counterfactual では `entry_recheck_any=76件 / sl_hit_rate 78.9% / avg_R 0.12`。
- `quality_guard_effectiveness_20260607.md`: closed 376件のうち `guard該当全体=57件`、entered split では `entered_sl_hit_rate=79.5%`。`A only` と `A+B` は hard blocker 維持材料、`B only` / `C only` は巻き込み確認を優先する。
- `soft_risk_collateral_damage_20260607.md`: `B/C soft risk 全体=14件` は `monitor_only` 判定で、B/C 単独 soft risk は現時点でも hard blocker 化しない。
- AI 事後評価 health は `feedback_daily_sync_20260607.md` 基準で `eligible=433 / AI済み=387 / backlog=46 / created=8 / request_failed=0`。daily cap 8 は継続可能。
- 最新 daily-sync 基準は `feedback_daily_sync_20260607.md`。`trade_execution_gate=pass=0件`、`paper_orders planned=0件`、`quality guard blocked=9件`、`hard_quality_blocked=9件`、`soft_quality_risk=0件`、`market_map opportunity before/after hard guard=24件 -> 1件`。
- AI事後評価は今後 `feedback_daily_sync` だけでなく `paper_opportunity_diagnostics` と `paper_entry_sl_wait_redesign` の設計根拠にも使う。`human_override` は例外で、日常判断は AI 評価を主系にする。

## 次のタスク

1. 最新 daily-sync は `2026-06-07` 基準で `hard_quality_blocked=9件`、`soft_quality_risk=0件`、`trade_execution_gate=pass=0件`、`paper_orders planned=0件`。Phase 1B や実弾寄りの緩和は進めず、hard blocker 偏重が続くかを観測継続する。
2. 次の診断、設計、フェーズ判断は ChatGPT プロジェクトへ渡す。`counterfactual_quality_guard` builder、`quality_guard_effectiveness` の entered / non-entered split、`paper_entry_sl_wait_redesign` builder は実装済みのため、次は `B/C` 単独 soft risk の collateral damage と entry / wait / price-distance 再設計を整理する。
3. `paper_entry_sl_wait_redesign_20260607.md` を基準に、`sl_hit` の主因が高 wait、低 execution、long、上方向転換系へどの程度残っているかを再確認する。ChatGPT 側は entry 発火条件、SL/TP 条件、wait/execution 抑制条件を分けて再設計する。
4. `market_map_opportunity` は累計では改善したが、`long`、`wait>=60`、`resistance_to_support_flip`、`trend_flip_confirmed_up` は弱い。特に `wait>=80` と `execution<20` の抑制案は ChatGPT 側で具体化する。
5. `trend_flip_confirmed_up` は 49 件に到達したが依然弱く、紙ポジションでも 9 件中 7 件が `sl_hit`。上方向転換系を強評価へ戻さず、次の扱いは ChatGPT 側で再判定する。
6. `Phase 1B-lite` は 5 件で止まっている。10〜15 件まで専用CSVで追い、正式 `Phase 1B` へはまだ上げない。
7. AI backlog は 46 件で `request_failed=0`。daily cap 8 を維持し、backlog が自然減するか確認する。
8. `paper_entry_sl_wait_redesign` は専用 CLI を追加済み。次回は `paper_entry_sl_wait_redesign_20260607.md` を基準に、抑制案の優先順位と副作用（missed/opportunity 側）を整理する。
9. `quality_guard_effectiveness_20260607.md` を再生成済み。daily-sync と paper diagnostics の `quality guard` 件数差は母集団差として整理しつつ、最新 closed 母集団での解釈に使う。
10. 次に見る論点は `B/C` 単独 soft risk の collateral damage と、entry / wait / price-distance 再設計である。guard 条件そのものは今回は変更しない。
11. `quality_guard_effectiveness_20260607.md` に reason別・複合条件別 counterfactual を再生成済み。次に ChatGPT が見るべき論点は、reason組み合わせ別の `sl_hit_rate` と `tp2_hit / missed_opportunity` 巻き込み率であり、guard 条件変更はまだ行っていない。
12. `paper_entry_sl_wait_redesign` builder は `paper_positions.csv` と `shadow_log.csv` の後付け再計算で再生成可能になった。次回は出力推移を使って設計判断へ進める。
13. `paper opportunity quality guard` の hard / soft 分離を実装し、仕様書は `chatgpt/specs/archive/20260601_quality_guard_hard_soft_split.md` へ移した。`A=require_execution_for_high_wait` を含む group は hard blocker、`B/C` 単独と `B+C` は soft risk として扱う。
14. `trade_execution_gate` と `phase1b_lite_gate` は変更していない。直近も `soft_quality_risk=0件` のため、次回もまず観測継続とし、再発時だけ soft risk 側の閾値再調整を検討する。

## 次にやること

1. 新しい監視サイクル後に `logs/csv/active_plan_candidates.csv` が生成されるか確認する。
2. 生成後、`python tools/log_feedback.py --build-active-trade-plan-diagnostics --active-plan-report-date <YYYYMMDD>` で Active Plan 診断を再生成する。
3. 候補CSVに実データが入ったら、`active_plan_candidate_outcomes` / daily-sync 接続を次作業にする。
4. 既知の未追跡ファイル 3 件は `BTCFX-20260608-036` で扱い決定済み。
   - 生成レポート候補2件は repo 外へ退避。
   - 参考資料1件は repo に採用。
- Active Plan runtime確認結果: `運用資料/作業ログ/BTCFX-20260608-038_active_plan_runtime_status.md`
- 監視実行コード確認結果: `運用資料/作業ログ/BTCFX-20260608-039_monitor_runtime_code_status.md`
- 監視再起動確認結果: `運用資料/作業ログ/BTCFX-20260608-040_monitor_restart_status.md`
- 再起動後 Active Plan 反映確認結果: `運用資料/作業ログ/BTCFX-20260608-041_active_plan_post_restart_status.md`
- 再起動後サイクル Active Plan 確認結果: `運用資料/作業ログ/BTCFX-20260608-042_active_plan_cycle_status.md`
- 再起動後後続サイクル Active Plan 確認結果: `運用資料/作業ログ/BTCFX-20260608-043_active_plan_second_cycle_status.md`
- `active_plan_candidates.csv` はまだ未生成。次は Ver03-v1 の監視サイクルが最新commitで走っているか確認する。
- AUTO_SUBMIT_HEALTHCHECK: `運用資料/作業ログ/BTCFX-20260608-044_auto_submit_healthcheck.md`
- healthcheck OK。次は `active_plan_candidate_outcomes` builder / CLI 正本化へ進む。
- LaunchAgent の起動対象は `Ver03-v1` / `97c0c9b` / `.venv312/bin/python` だが、監視 PID は `2026-06-06 16:24:40` 起動の継続稼働だった。次は、安全に監視 worktree と実行中プロセスの同期状態を確認し、必要なら LaunchAgent 再起動手順を出す。
- `com.afrog.btc-monitor` は再起動済み。次の監視サイクル後に `active_trade_plan` / `active_plan_candidates.csv` の生成を確認する。
- `Active Plan runtime 反映未確認のため diagnostics 再生成なし`。次の定刻サイクル後に再確認する。
- Active Plan は runtime 反映済みだが、`active_plan_candidates.csv` は header only。次は `active_plan_candidate_outcomes` builder / CLI 正本化へ進む。

## 残作業一覧

- `trend_flip_confirmed_up` は最新 `market_map_effectiveness_20260607.md` でも弱いため、ChatGPT 側で上方向転換系の扱いを再判定する。
- `com.afrog.btc-monitor` の LaunchAgent 実行先は `Ver03-v1` worktree / `.venv312/bin/python` / `main.py`。ただし監視 PID は `2026-06-06 16:24:40` 起動の継続稼働で、`logs/heartbeat.txt` と `logs/last_result.json` は 2026-06-08 19:05 更新、`logs/runtime/monitor.err` は空だった。runtime 出力にはまだ Active Plan が反映されていない。
- `feedback_daily_sync_YYYYMMDD.md` を次回生成し、AI事後評価の `eligible / AI済み / backlog / created / request_failed` を更新する。現状は `request_failed=0` だが backlog は 46 件残っている。
- `paper_opportunity_diagnostics_20260607.md` の quality guard 集計を基準に、`require_execution_for_high_wait`、`suppress_long_high_wait`、`suppress_trend_flip_up_strong` が `sl_hit` 偏重の抑制に効くかを次回も追う。
- `quality_guard_effectiveness_20260607.md` を基準に、daily-sync の新規観測と diagnostics の累積 closed 母集団を混同せずに評価する。必要なら `counterfactual_quality_guard` を report builder 化する。
- `quality_guard_effectiveness_20260607.md` の reason組み合わせ別表を基準に、`A only`、`B only`、`C only`、`A+B` のどこを維持し、どこを閾値再調整候補にするかを ChatGPT 側で判断する。
- hard / soft 分離後は、`hard_quality_blocked` と `soft_quality_risk` の推移を基準に、`A` を維持したまま `B/C` 単独の扱いをさらに調整するかを ChatGPT 側で決める。
- 次回は `daily-sync` と `paper_opportunity_diagnostics` で `hard_quality_blocked` と `soft_quality_risk` の推移を見る。
- AI事後評価の `AI_POST_REVIEW_DAILY_MAX=8` は安定確認済み。`request_failed` が増える場合だけ 4 または 6 へ戻す。
- 標準比較 3 本は 2026-05-26 基準でも `0 / 0 / 1` を維持。次回 daily-sync 後も崩れた箇所だけを見る。
- `market_map` は 589 件まで増えた。下方向側は相対的に有効だが、紙実行候補では `long` / 高 wait / 上方向転換系が弱いため、実弾 gate 緩和ではなく entry / wait 条件の検証を優先する。
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
- BTCFX-20260601-16 で active spec `chatgpt/specs/active/20260601_short_low_execution_recheck.md` を作成。
- 次回はこの active spec を正本に、short + execution<20 の entry recheck 追加を実装する。
- BTCFX-20260601-17 で short + execution<20 の entry recheck reason を実装。
- entry_recheck_required_short_low_execution を追加し、paper_entry_sl_wait_redesign report の counterfactual impact に反映。
- active spec は archive 済み。
- trade_execution_gate / phase1b_lite_gate / paper_orders planned は変更していない。
- 次回は再生成された report の結果を見て、条件を維持するか追加調整するか判断。
- BTCFX-20260601-18 で影響範囲を確認し、entry_recheck_required_short_low_execution の count=44 は market_map_opportunity 全体の short+execution<20 再計算（重複込み）であることを確認。
- entry_recheck_none 内の9件は short_low_execution 単独ヒット分で、通知数44件減を直接意味しない点を確認メモとして残した。
- BTCFX-20260601-19 で ver02.6-v2 の最新 commit (`aed8063fc64f8b57120d559ca24e143737493ac7`) を常駐 com.afrog.btc-monitor へ反映し、再起動を実施。
- SYSTEM_LABEL / 通知ラベルは Ver02.6-v2 のまま維持（.env: `SYSTEM_LABEL=Ver02.6-v2` を確認）。
- 常駐再起動後に launchctl state=running、runtime err=空、通知ディレクトリ未作成（当該確認対象なし）を確認。
- trade_execution_gate / phase1b_lite_gate / paper_orders planned は変更していない。
