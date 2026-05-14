# Progress Log

更新日: 2026-05-15 JST

このファイルは、現在の軽い進行ログ入口です。
重い履歴は `progress_weekly/` へ週ごとに退避します。

## このファイルに残すもの

- 仕様変更
- 運用前提の変更
- 実行方式や保存方式の変更
- 後で「何を変えたか」を追いたくなる節目

## 週次アーカイブ

- 2026-W11: [progress_weekly/2026-W11.md](progress_weekly/2026-W11.md)

## 圧縮サマリ

- 2026-03-13 〜 2026-03-17
  - `Ver02.1` 系の通知本文と件名の可読性改善、注意報メール追加、重複メール調査と二重起動対処を進めた。
  - 本番 `Ver02.1` の実行方式、軽量同期、運用資料構成を整理し、`daily-sync` / 軽量 snapshot / 週次 archive の土台を作った。
- 2026-03-18 〜 2026-03-23
  - レビュー導線を `通知評価シート.md` + `評価シート入力フォーム.html` に整理し、`daily-sync`・`export-review-queue`・関連テストを整備した。
  - `Global_BOX` と案件内運用資料の入口を見直し、`iMac 2019` を主観測先、`MBA M4` を軽作業機として整理した。

## 重要な節目ログ

- 2026-05-15 JST
  - 改善案 `2026-05-15_042121_btc_notification_design_codex.md` を実装方針へ落とし込み、`運用資料/計画/通知ランク再設計_実装設計_20260515.md` を追加した。
  - 通知ランクを `執行候補・強` / `執行候補` / `高優先監視・実行不可` / `通常監視・実行不可` / `注意報・売買非推奨` に再設計した。`trade_execution_gate=pass` かつ `paper_order_status=planned` のときだけ執行候補を出し、それ以外の本通知は監視系として表示する。
  - 件名・本文冒頭・詳細ページの期待値を新ランクへ合わせ、注意報は「売買推奨ではない」こと、監視通知は「実行候補ではない」ことを先に出すようにした。
  - `zsh tools/start_monitor.sh` で `com.afrog.btc-monitor` を再起動し、`state=running`、PID `21314`、実行元 `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/main.py` を確認した。05:05 サイクルで `logs/last_result.json` と `logs/heartbeat.txt` が更新され、`monitor.err` は空。05:05 は `final_rank_code=no_send` のため、`[Ver02.5-v6] [CLI]` 件名確認は次回送信時に持ち越し。

- 2026-05-15 JST
  - `ver02.5-v5` から新ブランチ `ver02.5-v6` を作成した。
  - `.env` / `.env.example` の `SYSTEM_LABEL` を `Ver02.5-v6` へ更新し、入口資料の現行版表記も `Ver02.5-v6` に合わせた。
  - 常駐 `com.afrog.btc-monitor` の再起動と次回件名 `[Ver02.5-v6] [CLI]` の確認は次作業に残した。

- 2026-05-15 JST
  - `./.venv312/bin/python tools/log_feedback.py build-market-map-readiness-report --output-md 運用資料/reports/analysis/market_map_readiness_20260514.md --date-from 2026-05-13` を実行し、`readiness=pass`、対象 shadow 37 行中 `market_map 記録あり=33件` を確認した。
  - `./.venv312/bin/python tools/log_feedback.py build-market-map-effectiveness-report --output-md 運用資料/reports/analysis/market_map_effectiveness_20260514.md --date-from 2026-05-13 --date-to 2026-05-14` を実行し、`support_to_resistance_flip=21件`、`trend_flip_confirmed_down=17件`、`failed_breakout_up_reversal=8件` を確認した。
  - 初期サンプルでは `trend_flip_confirmed_up=4件` が勝率 0.0% / wrong_rate 50.0% と弱く、次回以降の有効性レポートで継続確認する対象にした。`trade_execution_gate=pass` と `paper_orders planned` は引き続き 0 件で、Phase 1B 本有効は未達。
  - `com.afrog.btc-monitor` は iMac 2019 上で running、`logs/heartbeat.txt` と `logs/last_result.json` は 2026-05-15 00:05 JST 更新、`monitor.err` / `ai_post_reviews.err` / `feedback_daily_sync.err` は空であることを確認した。
  - `NEXT_TASK.md` を `feedback_daily_sync_20260514.md` と新規 market_map レポート基準へ更新し、古い `readiness=wait` 前提を解消した。

- 2026-05-13 JST
  - 現時点の差分一式を `ver02.5-v5` ブランチとして切り出し、commit `2a0ca4b Prepare ver02.5-v5 updates and reports` を作成して `origin/ver02.5-v5` へ push した。
  - `watch + trade_execution_gate=blocked` の本通知がロング実行推奨に見えないよう、`src/presentation/sanitize.py` と `src/ai/summary.py` を更新した。件名は `上方向監視 / 下方向監視` を使い、本文冒頭にも「これは実行候補ではありません。監視と再評価のための通知です。」を追加した。
  - `ENTRY_OK + watch + entry_zone_not_reached` の表示を `位置は悪くないが未到達` に変更し、`trade_execution_gate=blocked` 時の執行判断も `監視継続（実行不可）` と出すようにした。
  - `src/analysis/result_flags.py` に `long_reversal_risk` 派生判定を追加し、`transition/down + watch + sweep_incomplete` かつ抵抗要因ありのロング監視で risk flag を付けるようにした。`src/analysis/scoring.py` でも `transition/down + breakout_up` に反転ペナルティを追加した。
  - `long_reversal_risk` がある本通知は `高め本通知` へ上げず、`通常の本通知` に抑えたうえで `下落警戒` を主理由に出すようにした。これで `20260429_100500` 型の誤読防止を先に実装した。
  - 確認は `./.venv312/bin/python -m unittest tests.test_summary_format tests.test_summary_wording tests.test_notification_rank tests.test_eval_rebalance tests.test_notification_detail_page tests.test_notification_trigger tests.test_phase1_trade_plans tests.test_log_feedback` を実施し、109 件 OK を確認した。
  - 続けて `src/trade/observation_gate.py` に `counter_long_short_watch` を追加し、`long_reversal_risk` が付いたロング watch で反対側 short setup が `watch/ready` のときは、ショート観測候補として Phase 1A 母集団へ通せるようにした。
  - `src/storage/csv_logger.py` と `tools/log_feedback.py` も合わせ、`counter_long_short_watch` は `observation_paper_orders` 上で `side=short` として保存されるように揃えた。既存 trades からの backfill でも同じ向きが出るようにしてある。
  - `tools/log_feedback.py` に `build-failed-breakout-down-reversal-report` を追加し、`breakout_up` を含むロング watch が `direction_outcome=wrong`、`entry_outcome=poor_entry`、`MAE24h>=5.0` で終わった失敗型を専用レポートとして再生成できるようにした。
  - `build_feedback_report` には `counter_long_short_watch` と `failed_breakout_down_reversal` の要約を足し、日次の確認でも件数と代表例を追いやすくした。
  - 確認は `./.venv312/bin/python -m unittest tests.test_phase1_trade_plans tests.test_log_feedback` を実施し、64 件 OK を確認した。
  - 勝率低下とトレンド転換取り逃しへの対策として `src/analysis/market_map.py` を追加し、複数時間足のレジサポ合流、反応回数、直近性、ヒゲ拒否、出来高タッチから主要ラインを構築するようにした。
  - `market_map` では `support_to_resistance_flip`、`resistance_to_support_flip`、`failed_breakout_down_reversal`、`failed_breakout_up_reversal`、`trend_flip_*` を出し、`main.py`、`src/analysis/scoring.py`、`src/analysis/result_flags.py`、`src/storage/csv_logger.py` へ接続した。
  - `tools/log_feedback.py` に `build-market-map-effectiveness-report` を追加し、`market_map_flags` 別の勝率、wrong_rate、平均MFE/MAE、代表例を `shadow_log.csv` から検証できるようにした。`build_feedback_report` にも `market_map` セクションを追加した。
  - テストは `./.venv312/bin/python -m unittest discover -s tests` を実施し、151 件 OK を確認した。併せて `git diff --check` も OK。
  - `market_map` 系のメール文言を明示化し、`long_into_major_resistance`、`support_to_resistance_flip`、`failed_breakout_down_reversal`、`trend_flip_*` などが「内部要因」ではなく、追いかけ注意、戻り売り確認、押し目確認、転換初動として読めるようにした。
  - 件名の主理由、本文の「いま重視する理由」、次に見る条件、無効化目安でも market_map 系の意味が出るようにし、`watch + blocked` の誤読をさらに減らした。
  - 確認は `./.venv312/bin/python -m unittest discover -s tests` を実施し、153 件 OK を確認した。併せて `git diff --check` も OK。
  - `tools/log_feedback.py` に `build-market-map-readiness-report` を追加し、`market_map` が実ログへ入り始めたかを短く判定できるようにした。`2026-05-13` 時点では `readiness=wait`、最新 shadow は `20260512_180500 / 03:05 / Ver02.5-v4` で、`ver02.5-v5` の値入りは次サイクル待ち。
  - readiness 結果は `運用資料/reports/analysis/market_map_readiness_20260513.md` に保存した。確認は `./.venv312/bin/python -m unittest tests.test_log_feedback -k market_map` を実施し、5 件 OK。
  - メール件名ラベルを `.env` / `.env.example` とも `SYSTEM_LABEL=Ver02.5-v5` に更新し、`com.afrog.btc-monitor` を再起動した。件名生成の確認では `[Ver02.5-v5] [CLI]` が出ることを確認済み。
  - 残作業は `NEXT_TASK.md`、`👩‍⚖️秘書.md`、`📒打ち合わせノート.md` に整理した。主な残りは、`shadow_log.csv` 更新後の market_map readiness / effectiveness 再生成、次回メール件名の `Ver02.5-v5` 確認、AI事後評価 backlog 約50件の自然減確認、Phase 1B gate 緩和可否の継続判定。

- 2026-04-30 JST
  - `20260429_100500` のように、内部は `watch + trade_execution_gate=blocked` なのにロング推奨に見える通知が大きな下落になった失敗を受け、`運用資料/計画/ロング誤判定と下落取り逃し改善計画_20260430.md` を追加した。
  - 同計画では、失敗原因を `文面の誤読`、`上位足ロング要因の残りすぎ`、`失敗ブレイク型の未検出`、`ショート候補化の遅れ` に分けた。
  - 改善手順は、まず `watch + trade_execution_gate=blocked` の件名と本文を `監視 / 実行不可` と読めるようにし、次に `long_reversal_risk`、`counter_long_short_watch`、`failed_breakout_down_reversal` レポートを順に追加する方針にした。
  - `NEXT_TASK.md` に計画への参照と次タスクを追加し、次回実装ではこの計画を入口にして着手できる状態にした。

- 2026-04-30 JST
  - `src/trade/observation_gate.py` に `confidence_watch_learning` を追加し、`watch + confidence_below_min + SWEEP_WAIT/RISKY_ENTRY + sweep_incomplete + lower_liquidity_close + 補助 hard flag なし + direction>=55 + execution>=18 + wait<=85` の少数群だけは Phase 1A 観測候補として拾えるようにした。
  - `main.py` と `tools/log_feedback.py` を更新し、live 判定と分析レポートの両方で同じ限定条件を使うように揃えた。
  - `tools/log_feedback.py` に `build-phase1b-promotion-report` を追加し、限定昇格候補を独立レポート化できるようにした。`daily-sync` にも `Phase 1B 昇格候補` セクションを追加した。
  - `tests/test_phase1_trade_plans.py` と `tests/test_log_feedback.py` を更新し、限定候補判定、専用レポート、CLI 入口を含めて `.venv312/bin/python -m unittest tests.test_phase1_trade_plans tests.test_log_feedback` 60 件 OK を確認した。
  - 実データでは `./.venv312/bin/python tools/log_feedback.py build-phase1b-promotion-report --output-md 運用資料/reports/analysis/phase1b_promotion_candidates_20260429.md --date-from 2026-04-18 --date-to 2026-04-29` を実行し、候補は 2 件、どちらも `SWEEP_WAIT`、平均 `direction=59.0 / execution=22.0 / wait=76.8` だった。
  - ただし成績は `勝率 0.0% / TP1先行 0.0% / 近似PF 0.12` で弱く、この型だけではまだ `Phase 1B` 昇格材料として不足と確認した。現時点では「昇格条件の即緩和」ではなく「この型の再現監視」を優先する。
  - `./.venv312/bin/python tools/log_feedback.py daily-sync --output-md 運用資料/reports/feedback_daily_sync_20260430.md` を実行し、完了 29 件、近似PF 1.10、全体勝率 44.8%、`phase1_observation_gate=pass:8件`、`confidence_watch_learning 候補:1件`、`trade_execution_gate=pass:0件` を確認した。
  - 入口資料 `NEXT_TASK.md`、計画 `実用化計画_Phase1A-1B.md`、運用メモ `運用コマンドメモ.md` を更新し、新しい昇格候補導線と現状判断を反映した。

- 2026-04-30 JST
  - 未反映だった `運用資料/reports/feedback_daily_sync_20260426.md` 〜 `feedback_daily_sync_20260429.md` を確認し、入口判断を `2026-04-29` 時点へ更新した。
  - `./.venv312/bin/python tools/log_feedback.py refresh-standard-setup-reports --date-from 2026-04-18 --date-to 2026-04-29` を実行し、`notified_rr_to_entry=0件`、`notified_rr_to_entry_orderbook_ask_heavy=0件`、`rr_to_confidence=1件` が維持されることを確認した。
  - これにより、`rr_below_min -> entry_zone_not_reached` と `orderbook_ask_heavy` 付き差分は、新規ログ帯でも追加実装を急ぐ段階ではないと再確認できた。
  - `./.venv312/bin/python tools/log_feedback.py build-operational-focus-report --output-md 運用資料/reports/analysis/operational_focus_20260429.md --date-from 2026-04-18 --date-to 2026-04-29` を実行し、backlog 候補 18 件、`phase1 pass=33件 / blocked=232件`、blocked 上位は `confidence_below_min=147件`、`no_trade_candidate=81件` と確認した。
  - `setup_watch_learning` pass は 32 件で継続している一方、blocked 群は `sweep_incomplete + lower_liquidity_close` 同居が依然支配的で、`confidence floor` や `NO_TRADE_CANDIDATE` の一律緩和はまだ早いと整理した。
  - `./.venv312/bin/python tools/log_feedback.py build-relaxation-candidates-report --output-md 運用資料/reports/analysis/relaxation_candidates_20260429.md --date-from 2026-04-18 --date-to 2026-04-29` を実行し、緩和候補は 23 件、`SWEEP_WAIT=16件`、`RISKY_ENTRY=6件`、`NO_TRADE_CANDIDATE=1件`、平均 `execution=18.5 / wait=84.8` と確認した。
  - 少数群の先頭は `20260427_170500`、`20260427_110500`、`20260427_100500`、`20260426_210500`、`20260426_180501` で、次回以降はこの新顔群が再現するかを優先監視する方針にした。
  - `logs/runtime/monitor.err` と `logs/heartbeat.txt`、`logs/last_result.json` も確認し、定時更新は `2026-04-30 01:05 JST` まで進んでおり、runtime エラーは従来どおり `urllib3` の `NotOpenSSLWarning` のみだった。
  - 入口資料 `NEXT_TASK.md` を `2026-04-29` 基準へ更新し、比較帯、backlog、緩和候補、次判断を最新観測に合わせて整理した。

- 2026-04-25 JST
  - `build-relaxation-candidates-report` を追加し、`confidence_below_min + sweep_incomplete + lower_liquidity_close` だが `orderbook_ask_heavy`、`ask_wall_close`、`long_flush_exhaustion` を持たない少数群だけを独立抽出できるようにした。
  - `tests/test_log_feedback.py` に候補抽出のレポートテストと CLI 入口テストを追加し、`.venv312/bin/python -m unittest tests.test_log_feedback` で 45 件 OK を確認した。
  - 実データでは `relaxation_candidates_20260425.md` を生成し、候補 13 件、`SWEEP_WAIT=9件`、`RISKY_ENTRY=3件`、`NO_TRADE_CANDIDATE=1件`、平均 `execution=18.2 / wait=84.1` と確認した。
  - 候補の上位は `20260424_130500`、`20260421_140500`、`20260421_060500`、`20260421_020500`、`20260420_180500` で、次回以降はこの少数群が新規ログでも再現するかだけを見ればよい状態に整理できた。
  - `build-operational-focus-report` をさらに拡張し、`sweep_incomplete + lower_liquidity_close` を持つ blocked 群について、`orderbook_ask_heavy`、`ask_wall_close`、`long_flush_exhaustion` の補助 flag 有無と、補助 flag なしの少数候補を直接出せるようにした。
  - 実データでは `confidence_below_min` 67 件のうち `補助flagなし=13件`、`no_trade_candidate` 54 件のうち `補助flagなし=1件` だった。`no_trade_candidate` 側はほぼ hard flag 付きのため、緩和候補から外しやすい構図になった。
  - 緩和候補の少数群としては `20260424_130500`、`20260421_140500`、`20260421_060500`、`20260421_020500`、`20260420_180500` などが抽出できた。いずれも `confidence_below_min` だが補助 hard flag が薄い。
  - これで「どこを残して、どこだけ緩和候補にするか」をコード変更なしで先に切り分けられたため、次回以降の新規ログでは少数群が再現するかだけを追えばよい段階まで整理できた。
  - `build-operational-focus-report` を拡張し、blocked 上位理由ごとの `prelabel`、`setup status`、`setup reason`、`risk_flags`、代表 signal を出せるようにした。
  - 実データでは `confidence_below_min=84件` が `NO_TRADE_CANDIDATE=39件` と `SWEEP_WAIT=38件` に二分し、`risk_flags` は `sweep_incomplete=76件`、`lower_liquidity_close=74件`、`orderbook_ask_heavy=39件` が支配的だった。
  - `no_trade_candidate=59件` はほぼ `NO_TRADE_CANDIDATE` 固定で、`setup reason` は `confidence_below_min=39件` が最大、`risk_flags` は `sweep_incomplete=57件`、`lower_liquidity_close=56件`、`ask_wall_close=46件` が上位だった。
  - これにより、今すぐ `confidence floor` や `NO_TRADE_CANDIDATE` を一律に緩めるより、`sweep_incomplete + lower_liquidity_close` の扱いを新規ログでもう 2 サイクル観測してから触る方が妥当と整理した。
  - `tools/log_feedback.py` に `build-operational-focus-report` を追加し、`shadow_log.csv` から backlog 分布と `setup_watch_learning` 偏重をローカル集計できるようにした。
  - `tests/test_log_feedback.py` に運用フォーカス分析の集計テストと CLI 入口テストを追加し、`.venv312/bin/python -m unittest tests.test_log_feedback` で 43 件 OK を確認した。
  - 実データでは `./.venv312/bin/python tools/log_feedback.py build-operational-focus-report --output-md 運用資料/reports/analysis/operational_focus_20260425.md --date-from 2026-04-18 --date-to 2026-04-25` を実行し、同期間の backlog 候補は 20 件、`phase1 pass=27件 / blocked=143件`、pass 内訳は `setup_watch_learning=26件`、`direction_rr_learning=1件` と確認した。
  - `setup_watch_learning` の主 reason は `entry_zone_not_reached=16件`、`near_entry_zone_waiting_trigger=8件`、blocked 理由の上位は `confidence_below_min=83件`、`no_trade_candidate=59件`、`no_directional_setup=22件`、`watch_conditions_not_met=18件` だった。
  - `tools/log_feedback.py` に `refresh-standard-setup-reports` を追加し、標準比較レポート 3 本を 1 コマンドで更新できるようにした。`--date-from` と `--date-to` をそのまま受け、既存の `compare-current-setup` フィルタを標準3本へまとめて適用する。
  - `tests/test_log_feedback.py` に標準3本の生成テストと CLI 入口テストを追加し、`.venv312/bin/python -m unittest tests.test_log_feedback` で 41 件 OK を確認した。
  - 実データでも `./.venv312/bin/python tools/log_feedback.py refresh-standard-setup-reports --date-from 2026-04-18 --date-to 2026-04-25` を実行し、`notified_rr_to_entry`、`notified_rr_to_entry_orderbook_ask_heavy`、`rr_to_confidence` をまとめて再生成できることを確認した。
  - さらに `compare-current-setup` の日付帯を `--date-to 2026-04-25` まで伸ばして再生成したが、比較結果は維持された。`notified_rr_to_entry=0件`、`notified_rr_to_entry_orderbook_ask_heavy=0件`、`rr_to_confidence=1件` のままで、02:05 JST の追加1本でも差分傾向は変わらなかった。
  - 続けて `./.venv312/bin/python tools/log_feedback.py daily-sync --output-md 運用資料/reports/feedback_daily_sync_20260425.md` を再実行し、定刻 02:05 JST の signal を取り込んだ最新日次レポートへ更新した。
  - 最新値は、完了データ 40 件、近似PF 0.67、全体勝率 57.5%、`watch 系通知済み履歴=15件`、AI 事後評価 health は `eligible=190`、`AI済み=135`、`backlog=55`、`request_failed=0`。
  - `launchctl print gui/$(id -u)/com.afrog.btc-monitor` と `logs/runtime/monitor.err` も確認し、LaunchAgent は `running`、runtime エラーは実害のない `urllib3` の `NotOpenSSLWarning` のみだった。
  - 未反映だった `運用資料/reports/feedback_daily_sync_20260425.md` を確認し、最新値を `NEXT_TASK.md` へ反映した。完了データ 39 件、近似PF 0.68、全体勝率 59.0%、`phase1_observation_gate=pass:15件`、`trade_execution_gate=pass:0件`、AI 事後評価 backlog は `54件`。
  - `./.venv312/bin/python tools/log_feedback.py compare-current-setup --output-md ... --date-from 2026-04-18 --date-to 2026-04-24` で標準比較レポート 3 本を新規ログ帯に更新した。
  - 結果は `notified_rr_to_entry.md=0件`、`notified_rr_to_entry_orderbook_ask_heavy.md=0件`、`rr_to_confidence.md=1件` で、旧母集団で大きく見えていた `rr_below_min -> entry_zone_not_reached` / `confidence_below_min` 差分は新規ログではほぼ再現していないことを確認した。
  - `logs/csv/shadow_log.csv` では `watch_sweep_recheck_wait` が 5 件出ていた一方、`watch_low_execution_recheck_wait` はまだ 0 件だった。抑制自体は動いているが、低 execution 側の抑制条件はまだ新規母集団待ちと整理した。
  - このため次判断は、`watch_orderbook_recheck_wait` や confidence 緩和の追加実装へ急がず、あと 2 回分の `daily-sync` で同じ比較を継続する方針に寄せた。

- 2026-04-24 JST
  - `tools/log_feedback.py compare-current-setup` に `--date-from`、`--date-to`、`--status-transition` を追加し、新規ログだけを `timestamp_jst` 基準で比較できるようにした。
  - `tests/test_log_feedback.py` に日付帯・status遷移フィルタの回帰テストを追加し、`.venv312/bin/python -m unittest tests.test_log_feedback` で 39 件 OK を確認した。
  - 標準比較レポートを `運用資料/reports/analysis/` に生成した。`notified_rr_to_entry.md` は 33 件、`notified_rr_to_entry_orderbook_ask_heavy.md` は 14 件、`rr_to_confidence.md` は 487 件。
  - `rr_to_confidence.md` では通知済みが 64 件あり、status は `invalid->invalid=278件`、`watch->invalid=209件`。今後の Phase 1A 仕上げでは `position_risk` 追加緩和より前に confidence 側の落ち方を観測する基準を作れた。
  - 実データで `--date-from 2026-04-09 --date-to 2026-04-24 --status-transition 'watch->watch'` も確認し、通知済み `rr_below_min -> entry_zone_not_reached` は 14 件、平均 `execution=5.9 / wait=76.1` だった。`watch_orderbook_recheck_wait` を入れるかどうかは、この post-change 母集団が次回以降も維持されるかで判断する方針にした。

- 2026-04-24 JST
  - `./.venv312/bin/python tools/log_feedback.py daily-sync` を再実行し、`運用資料/reports/feedback_daily_sync_20260424.md` を生成した。
  - 最新値は、完了データ 31 件、近似PF 0.87、全体勝率 71.0%、`phase1_observation_gate=pass:13件`、`direction_rr_learning=2件`、`setup_watch_learning=11件`、`trade_execution_gate=pass:0件`。
  - 新しく追加した `watch 系通知済み履歴` は実データで 10 件出ており、主な通知理由は `prelabel_improved=9件`、`status_upgraded=6件`、`confidence_jump=4件`。代表例は `20260418_090500`、`20260422_050500`、`20260420_060500`。
  - `AI事後評価 health` は `eligible=179`、`AI済み=131`、`backlog=48`、`created=4`、`request_failed=0` で、backlog 自然減はまだ確認できていない。

- 2026-04-24 JST
  - `src/analysis/position_risk.py` で `NO_TRADE_CANDIDATE` 判定を絞り、`近接流動性 + 近接板 + sweep_incomplete` だけでは `SWEEP_WAIT` に留め、`orderbook_*_heavy`、`liquidation_cluster_*`、OI/CVD 系などの hard flag があるときだけ `NO_TRADE_CANDIDATE` へ落とすようにした。
  - `src/notification/trigger.py` で `watch + sweep_incomplete` 系の再通知条件を詰め、`status_upgraded`、`prelabel_improved`、`confidence_jump` だけで本通知へ上がるケースを `watch_sweep_recheck_wait` で抑制するようにした。
  - 確認は `.venv312/bin/python -m unittest tests.test_log_feedback tests.test_eval_rebalance tests.test_notification_trigger` を実施し、62 件 OK。
  - その後 `./.venv312/bin/python tools/log_feedback.py daily-sync` を再実行したが、`daily-sync` は既存 `shadow_log.csv` と通知履歴の集計であるため、過去ログの `NO_TRADE_CANDIDATE 3/8` と `watch 系通知済み履歴 10件` はそのまま維持された。効果確認は次回以降の新規ログで見る前提。
  - 既存ログでも現行 `build_setup` のズレを見られるよう、`tools/log_feedback.py compare-current-setup` を追加した。`shadow_log.csv` と signal snapshot を突き合わせ、旧 setup と現行 setup の差分件数、主な status/reason 変化、代表例を即確認できる。
  - 実データで `./.venv312/bin/python tools/log_feedback.py compare-current-setup --limit 10` を実行し、`shadow 967行中 724件` に差分、通知済みは `149件` を確認した。主変化は `rr_below_min -> confidence_below_min=487件`、`rr_below_min -> entry_zone_not_reached=73件`、`watch->invalid=254件`、`invalid->watch=77件` で、過去判定と現行 `build_setup` の乖離が想定以上に大きいことが分かった。
  - さらに `./.venv312/bin/python tools/log_feedback.py compare-current-setup --only-notified --previous-reason rr_below_min --current-reason entry_zone_not_reached --limit 10` を実行し、通知済みだけでも 33 件あることを確認した。内訳は `watch->watch=25件`、`invalid->watch=8件` で、`20260417_090500`、`20260415_210500`、`20260414_140500` を次の再調整母集団に使える。
  - `compare-current-setup` へ `only-notified`、`previous-reason`、`current-reason`、`prelabel` フィルタを追加し、差分母集団の `risk_flags`、通知理由、execution/wait 平均、status別集計も出せるようにした。
  - 同じ 33 件の主特徴は `sweep_incomplete=25件`、`lower_liquidity_close=22件`、`orderbook_ask_heavy=14件`、`ask_wall_close=13件`、通知理由は `confidence_jump=24件`、`status_upgraded=19件`、`prelabel_improved=16件`。`watch->watch` は平均 `execution=3.6 / wait=52.0`、`invalid->watch` は平均 `execution=15.6 / wait=64.0` で、次の再通知条件見直しに十分な粒度まで絞れた。
  - 追加で `src/notification/trigger.py` に `watch_low_execution_recheck_wait` を入れ、`watch + sweep_incomplete + lower_liquidity_close + execution<=10 + wait>=45` は main/attention を抑制するようにした。初回の `attention_bias_changed` だけは残す。
  - 確認は `.venv312/bin/python -m unittest tests.test_log_feedback tests.test_notification_trigger` を実施し、51 件 OK。
  - さらに `compare-current-setup` へ `risk_flag` フィルタを追加し、`orderbook_ask_heavy` 群を独立抽出できるようにした。実データでは `通知済み + rr_below_min -> entry_zone_not_reached + orderbook_ask_heavy` が 14 件あり、`watch->watch=13件`、平均 `execution=5.7 / wait=68.9`、`lower_liquidity_close=12件`、`sweep_incomplete=12件` を確認した。

- 2026-04-24 JST
  - `src/notification/trigger.py` の `sweep_incomplete` 再通知待ち条件を拡張し、従来の `invalid + rr_below_min + RISKY_ENTRY` だけでなく、現行再計算で出やすい `watch + entry_zone_not_reached + SWEEP_WAIT/RISKY_ENTRY` 系でも main 通知を抑え、score/gap だけの attention 再発火を抑制するようにした。
  - 初回の方向転換検知は `attention_bias_changed` として残しつつ、再発火条件と通知タイミングを先に詰める方向へ寄せた。
  - 確認は `.venv312/bin/python -m unittest tests.test_notification_trigger` を実施し、9 件 OK。
  - `tools/log_feedback.py` に `sweep_incomplete` を含む `watch + entry_zone_not_reached` 系の通知済み履歴集計を追加し、日次レポートから `watch 系通知済み履歴` と `現行watch再計算` を直接読めるようにした。
  - 確認は `.venv312/bin/python -m unittest tests.test_log_feedback tests.test_notification_trigger` を実施し、46 件 OK。

- 2026-04-24 JST
  - `運用資料/reports/feedback_daily_sync_20260423.md` を基準に、`NEXT_TASK.md` と `運用資料/reports/README.md` の入口情報を更新した。
  - 現在の基準値は、完了データ 28 件、近似PF 0.79、全体勝率 67.9%、`phase1_observation_gate=pass:14件`、`direction_rr_learning=6件`、`setup_watch_learning=8件`、`trade_execution_gate=pass:0件`。
  - AI 事後評価 health は `eligible=171`、`AI済み=127`、`backlog=44`、`created=4`、`request_failed=0` とし、backlog 自然減はまだ確認できていない前提へ揃えた。
  - `observation_paper_orders` は `observing=14件`、`gate pass だが観測紙トレード未記録=0件` で、Phase 1A の保存導線自体は維持されていることを入口資料へ反映した。

- 2026-04-22 JST
  - `./.venv312/bin/python tools/log_feedback.py daily-sync` を複数回再実行し、`運用資料/reports/feedback_daily_sync_20260422.md` を更新した。完了データは 27 件、近似PF は 0.84、全体勝率は 59.3%、`phase1_observation_gate=pass:16件`、`trade_execution_gate=pass:0件`。
  - `AI事後評価 health` は `eligible=165`、`AI済み=123`、`backlog=42`、`created=4`、`request_failed=0` へ更新された。`daily-sync` 側で `sync-ai-post-reviews` の直近 runtime ログを読んで health 表示を補完するように修正した。
  - `tools/log_feedback.py` に `rr_below_min` と `confidence_below_min` の代表例表示を追加し、日次レポートの Phase 1 判定サマリーから代表 signal と execution / wait / MFE / MAE を直接読めるようにした。
  - `prelabel=ENTRY_OK` かつ `primary_setup_status=invalid` の不整合を解消するため、`main.py` と `tools/log_feedback.py` に整合補正を追加した。最終出力では `ENTRY_OK + invalid` を `RISKY_ENTRY` へ寄せ、4/22 レポート上の `ENTRY_OK + invalid` は 0 件になった。
  - `RISKY_ENTRY + rr_below_min` のうち `execution>=20` の近閾値候補だけを補助集計するようにした。4/22 レポート時点の候補は `20260417_090500` の 1 件で、`exec=21`、`dir=87`、`wait=70.4`、`MFE24h=13.43`、`MAE24h=3.71`。
  - 同 signal の snapshot を現行 `src/analysis/rr.py` の `build_setup` で再計算する helper を `tools/log_feedback.py` に追加し、レポートへ `現行RR再計算` を出すようにした。`20260417_090500` は過去ログでは `rr_below_min` だが、現行ロジックでは `watch / entry_zone_not_reached / rr=1.30` になることを確認した。
  - この結果、今の主論点は `MIN_RR_RATIO` の追加緩和ではなく、`sweep_incomplete` を伴う long の再発火条件と通知タイミングであると整理した。
  - 確認は `.venv312/bin/python -m unittest tests.test_eval_rebalance`、`.venv312/bin/python -m unittest tests.test_log_feedback tests.test_phase1_trade_plans tests.test_summary_format` を実施し、全件 OK を確認した。
  - PR レビューで `main.py` の `phase1_observation_gate` 呼び出しに未定義変数 `prelabel_info` 参照が残っていることを確認した。
  - `prelabel=prelabel_info["prelabel"]` を `prelabel=effective_prelabel` へ修正し、通常サイクルで `NameError` が起きるリスクを解消した。
  - 追加確認は `.venv312/bin/python -m unittest tests.test_phase1_trade_plans tests.test_notification_trigger tests.test_eval_rebalance`、`.venv312/bin/python -m unittest tests.test_log_feedback tests.test_summary_format`、`git diff --check` を実施し、合計 72 件 OK。
  - `zsh tools/start_monitor.sh` で `com.afrog.btc-monitor` を再起動し、`state=running`、PID `76350`、実行元 `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor/main.py` を確認した。
  - `monitor.err` の直近は `urllib3` の LibreSSL 警告のみで、今回修正に伴う致命的エラーは確認されていない。
  - 実用化のため Phase 1 を `Phase 1A` 観測紙トレードと `Phase 1B` 厳格紙トレードへ分離する計画を `運用資料/計画/実用化計画_Phase1A-1B.md` として追加した。
  - `observation_paper_orders.csv` を追加し、`phase1_observation_gate=pass` を実行候補ではなく方向・待機条件・仮想SL/TPの検証ログとして保存するようにした。
  - `daily-sync` に `Phase 1A 観測紙トレード` セクションを追加し、既存 `shadow_log.csv` から 322 件を backfill した。最新 weekly 範囲では `observation_paper_orders observing=16件`。
  - `Phase 1B` 用の `paper_orders.csv` と `trade_execution_gate` は厳格条件のまま維持し、`trade_execution_gate=pass:0件` として引き続き本有効待ち。
  - 確認は `.venv312/bin/python -m unittest tests.test_phase1_trade_plans tests.test_log_feedback tests.test_eval_rebalance tests.test_notification_trigger tests.test_summary_format` と `git diff --check` を実施し、74 件 OK。
  - `zsh tools/start_monitor.sh` で常駐を再起動し、`state=running`、PID `82442` を確認した。

- 2026-04-20 JST
  - `./.venv312/bin/python tools/log_feedback.py daily-sync` を実行し、`運用資料/reports/feedback_daily_sync_20260420.md` を更新した。完了データは 27 件、近似PF は 1.11、全体勝率は 66.7%、Phase 1 は `ready=0` / `phase1_active=true=0` の本有効待ち。
  - `sync-ai-post-reviews` を手動実行し、AI 事後評価を 3 件作成した。結果は `created=3`、`request_failed=0`、`daily_cap=4`、`already_reviewed_today=1`、`backlog_pending=40`。
  - 再度 `daily-sync` を実行し、AI 事後評価 health は `eligible=159`、`AI済み=119`、`backlog=40`、最終AI評価 `2026-04-20T05:07:43.352804Z` になった。
  - 最新レポートの改善候補は `TP が近すぎるケースが多い` が最上位で、`tp_eval=too_close=8/14件`。`ENTRY_OK + invalid=4件`、`ENTRY_OK + rr_below_min=2件` は継続観測する。
  - `trade_execution_gate=pass` は 0 件、`paper_orders planned=0件` のまま。紙トレードはまだ開始条件未達。
  - `sync-ai-post-reviews` の 03:35 定刻実行では CLI usage limit により `request_failed=41` が出ていたため、CLI 失敗時に API fallback へ切り替える設定を追加した。
  - 併せて `AI_POST_REVIEW_MAX_CONSECUTIVE_FAILURES=3` を追加し、API fallback も失敗する場合は連続失敗で停止して backlog 全体を叩き続けないようにした。
  - 確認は `.venv312/bin/python -m unittest tests.test_log_feedback` を実施し、33 件 OK。追加確認の `sync-ai-post-reviews` は当日 cap 到達済みで `created=0`、`request_failed=0`、`already_reviewed_today=4`。
  - Phase 1 が進まない問題に対し、実行 gate と観測 gate を分離した。`trade_execution_gate` は実行候補として維持し、新たに `phase1_observation_gate`、`phase1_observation_type`、`phase1_observation_reasons` を追加した。
  - `rr_below_min` でも方向観測価値があるものは `direction_rr_learning`、watch 系で execution / wait が許容範囲のものは `setup_watch_learning` として記録する。`confidence_below_min`、`NO_TRADE_CANDIDATE`、データ品質不良、Funding禁止、ATR極端値は観測対象外にした。
  - `daily-sync` を再実行し、`feedback_daily_sync_20260420.md` に `Phase 1 観測 gate` を追加した。結果は `phase1_observation_gate=pass:17件`、`direction_rr_learning=13件`、`setup_watch_learning=4件`、観測候補全体の近似PF 1.64。
  - 確認は `.venv312/bin/python -m unittest tests.test_phase1_trade_plans tests.test_log_feedback` を実施し、44 件 OK。

- 2026-04-19 JST
  - AI 事後評価の 24 時間後レビュー運用を見直し、`tools/log_feedback.py` に CLI パス自動補正、health 集計、`backfill-ai-post-review-v2` を追加した。
  - `.env` の `AI_ADVICE_CLI_COMMAND` と `AI_SUMMARY_CLI_COMMAND` は、旧 repo パスから現行 repo の `tools/codex_cli_wrapper.py` へ修正した。
  - `./.venv312/bin/python tools/log_feedback.py backfill-ai-post-review-v2` を実行し、既存 AI レビュー 111 件と snapshot 111 件を `ai_post_review_v2` 相当へ補完した。
  - backfill 前の退避は `logs/csv/user_reviews_backfill_20260419_013047.csv` と `logs/review/ai_post_reviews_backfill_20260419_013047/` に保存した。
  - `通知評価シート.md` は `最終レビュー保存` と `最終再生成` を分け、さらに `AI自動評価状態` を出すようにした。別 Mac で HTML を開いたときは閲覧中心であることが分かる警告表示も追加した。
  - `./.venv312/bin/python tools/log_feedback.py daily-sync` を再実行し、`feedback_daily_sync_20260419.md` に `AI事後評価 health` を追加した。状態は `停止中`、`eligible=150`、`AI済み=111`、`backlog=39`、`created=0`、`request_failed=5`。
  - この変更で Phase 1 判定条件自体は変えていない。変わったのは、AI 事後評価が止まったときに日次レポートと通知評価シートで即座に分かるようになった点。
  - 確認は `.venv312/bin/python -m unittest tests.test_log_feedback` を実施し、31 件 OK。全体の `.venv312/bin/python -m unittest discover tests` は `tests/test_notification_detail_page.py` の既存不一致 1 件で失敗し、今回の変更範囲とは別系統として保留にした。

- 2026-04-19 JST
  - `./.venv312/bin/python tools/log_feedback.py daily-sync` を実行し、`運用資料/reports/feedback_daily_sync_20260419.md` を更新した。
  - 最新集計は完了データ 29 件、近似PF 1.13、全体勝率 75.9%、`待つ判断に使えた=14件`、平均役立ち度 3.60 / 5。
  - `ready阻害理由` の `rr_below_min` は 22 件で、前回 27 件から減少した。`ENTRY_OK + invalid` も 7 件から 5 件へ減少した。
  - `ENTRY_OK + rr_below_min` は 2 件で横ばいだが、平均 `execution=23.5` まで上がり、前回 14.5 より改善した。
  - `tp_eval=too_close` は 10/15 件で、前回 11/16 件から微減した。代表 signal は `20260414_140500`、`20260414_090500`、`20260414_020500` 周辺に残っている。
  - `execution<=20 かつ wait>=60` の抑制確認として、該当しやすい行は `signal_tier=normal` 側に寄っていることを確認した。直近12時間速報でも `direction_execution_conflict` の主理由は `confidence_below_min=2件` に変わり、`rr_below_min` 主因から外れた。
  - `紙トレード準備` は `trade_execution_gate=pass:0件`、`blocked:3件`、`paper_orders planned:0件` で、`paper_orders.csv` もまだ未生成だった。
  - これにより、今回の再調整は `rr_below_min` 過多と `ENTRY_OK + invalid` の改善傾向が見え始めた一方、`Phase 1` の本有効と紙トレード候補は引き続き未発生として継続観測に据える。

- 2026-04-18 JST
  - `NEXT_TASK` と `feedback_daily_sync_20260417.md` の改善候補に合わせ、通知判定のバランス再調整を実施した。
  - `src/analysis/rr.py` は近い抵抗帯/支持帯だけで `rr_below_min` に落ちすぎないよう、setup 用 TP を最低 `1.3R / 2.4R` で下支えする形へ変更した。
  - `src/analysis/position_risk.py` は `lower_liquidity_close` と `upper_liquidity_close` の単独 close 加点を強め、`ENTRY_OK + invalid` に残りやすいケースを `RISKY_ENTRY` 側へ寄せた。
  - `src/presentation/sanitize.py` は `confidence_execution_shadow <= 20` かつ `confidence_wait_shadow >= 60` の本通知を `high_main` / `strong_main` に上げず、`normal_main` へ抑制するようにした。
  - 追加確認として `tests/test_eval_rebalance.py` に TP 下限と流動性近接単独ケース、`tests/test_notification_rank.py` に低 execution / 高 wait のランク抑制を追加した。
  - 確認は `.venv312/bin/python -m unittest tests.test_eval_rebalance tests.test_notification_rank` を実施し、15 件 OK。
  - これにより、`rr_below_min` 過多、`ENTRY_OK + invalid`、`execution<=20 & wait>=60` の上位本通知化を次回 `daily-sync` で再観測できる状態にした。

- 2026-04-17 JST
  - AI 事後評価を `ai_post_review_v2` へ拡張し、`review_action_class`、`review_priority`、`next_action` を返して保存できるようにした。
  - 既存の `user_verdict`、`tp_eval`、`sl_eval`、時間足評価はそのまま維持し、旧レビュー行は互換のまま改善アクションへ推定補完する。
  - `daily-sync` レポートへ `改善アクション` セクションを追加し、分類件数、重要度件数、高優先の代表例を出せるようにした。
  - `tp_eval=too_close` は `tune_exit / high / TP1/TP2 を遠めにする候補を検証する` として扱えるようにした。
  - 確認は `.venv312/bin/python -m unittest tests.test_log_feedback` で 28 件 OK、`.venv312/bin/python -m unittest discover tests` で 97 件 OK。
  - GitHub へ `c2651bd Add actionable AI post review fields` を push 済み。
  - これにより、AI 事後評価は「役に立ったか」の記録だけでなく、「次に何を直すか」まで daily-sync 上で追える状態になった。
  - `👩‍⚖️秘書.md` の書き方がぶれないよう、`AGENTS.md` と `運用資料/運用/ルール/記録ファイル運用ルール.md` に固定フォーマットを明文化した。
  - 今後の `👩‍⚖️秘書.md` は `最新状態`、`次に見る`、`入口` の 3 見出しだけにし、最新状態は最大4行、次に見るは最大3行、入口は最大2リンクに制限する。
  - 履歴、経緯、古い版の説明、実施内容の詳細は `📒打ち合わせノート.md`、`NEXT_TASK.md`、`progress.md` へ分ける。
  - `ver02.5-v1` の最新コミット `7e074bc` を iMac 2019 の常設 `com.afrog.btc-monitor` へ反映した。
  - 反映前に `.venv312/bin/python -m unittest discover tests` を実行し、96 件 OK を確認した。
  - `zsh tools/start_monitor.sh` で LaunchAgent を再登録・再起動し、`launchctl print gui/501/com.afrog.btc-monitor` で `state = running`、PID `20830` を確認した。
  - `logs/runtime/monitor.pid` と `logs/heartbeat.txt` の更新も確認し、最新コードの常駐反映を完了扱いにした。

- 2026-04-16 JST
  - 2026-04-17 JST 追加: 勝てるトレードの実務精度と自動取引準備のため、`phase1_v1_shadow`、`trade_execution_gate`、`paper_orders.csv` の紙トレード記録を追加した。
  - `phase1_v1_shadow` は現行 `phase1_v0` を維持したまま、比較用出口として TP1=1.3R / TP2=2.4R を記録する。実注文は出さない。
  - `trade_execution_gate` は `phase1_active=true` に加え、`rr_below_min`、低 execution、高 wait pressure、データ品質不良、no_trade_flags をブロック理由として記録する。
  - `paper_orders.csv` は `trade_execution_gate=pass` のときだけ `planned` を1 signal_id 1行で保存する。
  - `daily-sync` レポートには `紙トレード準備` 欄を追加し、gate pass/blocked、主なブロック理由、paper_orders planned、`tp_eval=too_close` に対する shadow TP の比較候補を確認できるようにした。
  - 確認は `.venv312/bin/python -m unittest discover tests` を実施し、96 件 OK。
  - 2026-04-17 JST 追加: ブロッカー整理として `tests/test_codex_cli_wrapper.py` と `tests/test_log_feedback.py` の既知不一致を解消した。
  - `tools/codex_cli_wrapper.py` は `_build_command()` の `image_paths` を省略可能に戻し、既存テスト呼び出し互換を維持した。
  - `tests/test_log_feedback.py` は weekly 期間フィルタに依存する2件の固定日付を現在時刻基準へ変更した。
  - 確認は `.venv312/bin/python -m unittest tests.test_codex_cli_wrapper` と `.venv312/bin/python -m unittest tests.test_log_feedback` を実施し、どちらも OK。
  - `com.afrog.btc-review-form` は `launchctl print gui/501/com.afrog.btc-review-form` で `state = running`、PID `89754` を確認し、フォーム保存の未起動ブロッカーは現時点では解消済みとして扱う。
  - ディレクトリ移動後の旧配置参照を、現行パス `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor` へ整理した。
  - 対象は `README.md`、`.env.example`、`deploy/com.afrog.btc-*.plist`、`運用資料/運用/実務/運用コマンドメモ.md`、`運用資料/reports/README.md`、`運用資料/計画/README.md`。
  - `~/Library/LaunchAgents` 側の `com.afrog.btc-monitor`、`com.afrog.btc-review-form`、`com.afrog.btc-feedback-daily-sync`、`com.afrog.btc-ai-post-reviews` も新パスへ更新し、launchd の読み込み済み設定が新パスになっていることを確認した。
  - 追加確認で `/Users/marupro/CODEX` 全体の旧配置参照も同じ現行パスへ統一した。
  - `ENTRY_OK + rr_below_min` の次判断用に、daily-sync レポートの補助集計へ `position_risk` と `confidence` の見直し候補を出すようにした。
  - 最新実データでは `ENTRY_OK + rr_below_min=4件`、平均 `execution=10.8` / `wait=70.8` で、候補は `lower_liquidity_close` 単独加点の再確認と `execution<=20 かつ wait>=60` の本通知上位扱い抑制。

- 2026-04-15 JST
  - `daily-sync` を実行し、`運用資料/reports/feedback_daily_sync_20260415.md` を更新した。完了データは 41 件、近似PF は 1.15、全体勝率は 75.6%、Phase 1 は `ready=0` / `phase1_active=true=0` の本有効待ち。
  - 改善候補生成で `ENTRY_OK + primary_setup_status=invalid` を `ENTRY_OK が甘め` から分離し、独立した `ENTRY_OK と setup invalid の整合性崩れ` として出すようにした。
  - `shadow_log.csv` に `primary_setup_reason` を出力するようにし、最新レポートでは期間内 `ENTRY_OK + invalid=11件`、主理由 `rr_below_min=11件` を確認できるようにした。
  - `tests/test_log_feedback.py` に、`ENTRY_OK + invalid` が通常の `ENTRY_OK が甘め` 集計へ混ざらない回帰テストを追加した。
  - 確認は `.venv312/bin/python -m unittest tests.test_log_feedback tests.test_summary_format` を実施し、30 件 OK。
  - 追加で、`ENTRY_OK + rr_below_min` の補助集計、`ready阻害理由`、`direction_execution_conflict` の主理由と risk_flags をレポートに出すようにした。通知表示は `rr_below_min` なら `位置は悪くないがRR未成立`、`confidence_below_min` なら `位置は悪くないが強度未成立` に分けた。
  - 次フェーズ判定は、閾値緩和ではなく `ready=1件以上`、`phase1_active=true=5件以上`、`phase1_active=true=30件以上` の 3 段階で進める方針にした。

- 2026-04-13 11:40 JST
  - `sync-ai-post-reviews` が LaunchAgent 経由で `int(None)` により毎日失敗していたため、`tools/log_feedback.py` の引数処理を修正し、`max_new_ai_reviews` 未指定でも既定値へ流れるようにした。
  - 旧ログ互換として、`was_notified=true` なのに `notification_kind` が空の行を `main` 扱いで AI 事後評価対象に含めるようにした。
  - `export_review_queue()` のレビューソース統合順を修正し、`user_reviews.csv` の新しい AI 評価が古い `review_form_state.json` の `pending` に上書きされないようにした。
  - `tests/test_log_feedback.py` に、LaunchAgent 相当の未指定引数、`notification_kind` 欠落互換、CSV 優先マージのテストを追加し、`unittest` 4本で確認した。
  - 手動で `sync-ai-post-reviews` と `daily-sync` を実行し、通知評価の進捗を `完了 21 / 未完了 43` から `完了 38 / 未完了 26` へ更新した。
  - `launchctl kickstart -k "gui/$(id -u)/com.afrog.btc-ai-post-reviews"` 後に `last exit code = 0` を確認し、自動 AI レビューの復旧を確認した。
  - `.env` の `AI_POST_REVIEW_DAILY_MAX` を `2 -> 4` へ変更し、当日分は `already_reviewed_today=4` に達するまで追加消化されることを確認した。
  - 直近レビュー分析では `ENTRY_OK` が `primary_setup_status=invalid` と同居するケースが多く、件名と本文でエントリー寄りに誤読されやすかったため、`src/presentation/sanitize.py` を調整した。
  - `ENTRY_OK + invalid` のときは表示ラベルを `位置は悪くないが条件未成立` に抑え、`高め本通知` へ昇格しないようにした。ロジック値そのものは維持しつつ、表示上の誤読だけを減らす修正にとどめた。
  - `tests/test_summary_format.py` に回帰テストを追加し、`unittest` 3本で確認した。

- 2026-04-10 18:40 JST
  - 通知評価フォームの状態表示を整理し、各通知カードの上部で `24時間後機械評価` `AIレビュー` `人が確認` の3段階が見えるようにした。
  - `未完了だけ表示` ボタンは `ON / OFF` が文言と色で分かるトグル表示に変更した。
  - これにより、`機械評価待ち` `AIレビュー待ち` `AI評価済み` `人が確認・修正済み` の違いを人が画面上で追いやすくした。

- 2026-04-03 04:31 JST
  - `serve-review-form` を `com.afrog.btc-review-form` として LaunchAgent 化し、iMac 2019 のログイン後に自動起動する構成へ切り替えた。
  - 追加ファイルは `deploy/com.afrog.btc-review-form.plist` と `tools/start_review_form.sh`。`~/Library/LaunchAgents/com.afrog.btc-review-form.plist` へ配置し、`launchctl print` で `state = running` を確認した。
  - これにより、通知評価フォームの `保存` ボタンから `review_form_state.json` / `user_reviews.csv` / `通知評価シート.md` へ正本保存できる前提を常時満たす状態にした。

- 2026-04-02 15:20 JST
  - 詳細HTMLの視認性改善を進め、再検討ラインチャートを主役にした視覚寄りレイアウトへ更新した。
  - ロング / ショート再検討帯は右の価格軸まで伸ばし、上下限を価格軸側で読む形に変更した。
  - `3つの数字を丁寧に読む` は縦並びへ変更し、`主要ファクト` は `元メールの要点` の直前へ移した。
  - チャート内価格は整数表示へ統一し、吹き出しと補助ラベルの重なりを減らす座標調整を行った。
  - 確認は `.venv312/bin/python -m unittest tests.test_notification_detail_page` を実施した。

- 2026-04-02 14:35 JST
  - 通知共通層 `notification_context` を追加し、件名・本文・詳細HTML・`evaluation_trace` が同じ通知判断ラベルを使う形へそろえた。
  - 表示順を `ステータス` → `執行判断` → `方向判断` へ変更し、`上目線だが今は待つ` を件名先頭でも読み違えにくい形へ寄せた。
  - 実務メモ [通知共通層_notification_contextメモ.md](運用/実務/通知共通層_notification_contextメモ.md) を追加した。確認は `.venv312/bin/python -m unittest tests.test_summary_format tests.test_summary_wording tests.test_ai_cli_retry tests.test_notification_detail_page tests.test_evaluation_trace` を実施した。

- 2026-03-31 03:39 JST
  - `MBP2020` 本番 `com.afrog.btc-monitor-ver021` を停止し、`/Users/marupro/CODEX/archive/BTC_FX_CODEX_ver02_20260331_0339.tgz` へ凍結退避した。
  - `~/Library/LaunchAgents/com.afrog.btc-monitor-ver021.plist` も archive へ退避し、自動再起動しない状態にした。
  - これ以降、日常の主対象は `iMac 2019` の `Ver02.3v3-OBS` 1 本に寄せる前提へ切り替えた。

- 2026-03-31 03:24 JST
  - `./.venv312/bin/python tools/log_feedback.py daily-sync` を実行し、週次レポート [feedback_daily_sync_20260331.md](reports/feedback_daily_sync_20260331.md) を更新した。
  - 集計結果は、完了データ 32 件、全体勝率 71.9%、近似PF 0.75、レビュー要約は `useful_entry=3`、`too_late=1`、平均役立ち度 2.25 / 5。
  - 次の改善観測論点を `ENTRY_OK` の昇格タイミング、`NO_TRADE_CANDIDATE` の過剰抑止有無、`lower_liquidity_close` / `upper_liquidity_close` / `sweep_incomplete` の重み整合へ整理した。

- 2026-03-30
  - 通知表示を `Ver02.3v3-OBS` 向けに更新し、件名から単独の `総合強度` 表示を外した。
  - 本文は `方向の強さ` `実行しやすさ` `待機圧力` の 3 指標表示へ切り替え、`no_trade_flags / risk_flags / warning_flags` の責務を分離した。
  - `evaluation_trace v0.2` を追加し、`watch / invalid` 通知で方向判断と行動指示が混ざらない形へ整理した。

- 2026-03-30
  - 通知ごとの詳細HTMLページを、メール本文とは別ユニットで生成・公開できるようにした。
  - 実装は `src/notification/detail_page.py` と `tools/render_notification_detail_page.py` に分離し、公開失敗時も従来の本文通知を止めない設計にした。
  - `NOTIFICATION_HTML_*` 設定で ON/OFF できるようにし、`core_result` に `detail_page_status` と `detail_page_url` も保存するようにした。

- 2026-03-30
  - 通知評価フォーム運用を `HTML + JSON` 正本へ切り替えた。
  - 入力正本は `logs/review/review_form_state.json`、集計互換は `logs/csv/user_reviews.csv`、Obsidian 側 `通知評価シート.md` は進捗要約ノートとして扱う構成にした。
  - レビュー画面と集計対象は `2026-03-30 05:05 JST` 以降の通知だけに限定し、旧通知はフォームと集計から外すようにした。

- 2026-03-30
  - フォーム UI を新体制向けカードへ更新し、通知時刻の大表示、日本語ラベル、優先入力項目の強調、3 指標と通知理由中心の確認導線へ変更した。
  - `保存` / `再読込` ボタン付きにし、localhost 補助と組み合わせて JSON / CSV / Obsidian 要約を自動更新できるようにした。

- 2026-03-31
  - AI 用入口資料を圧縮し、`NEXT_TASK.md` は日常判断、`開発ロードマップ.md` は現在地と節目、`スレッド引き継ぎファイル.md` は archive / sandbox の例外前提だけを残す形へ再整理した。
  - `Global_BOX` の `本番環境.md` も実機確認ベースへ更新し、`MBP2020` で現在ロード中なのは `ReceiptBox` と `Tweet Sync` のみ、`BTC監視 ver021` は停止・凍結済みであることを反映した。
