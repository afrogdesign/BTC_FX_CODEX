# Progress Log

更新日: 2026-04-22 02:09 JST

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
