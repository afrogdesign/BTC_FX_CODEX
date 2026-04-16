# Progress Log

更新日: 2026-04-17 01:06 JST

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

- 2026-04-17 JST
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
