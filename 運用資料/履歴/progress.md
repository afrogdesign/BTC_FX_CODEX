# Progress Log

更新日: 2026-04-03 04:31 JST

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
