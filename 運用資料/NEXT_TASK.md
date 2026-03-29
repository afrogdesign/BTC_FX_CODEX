# NEXT TASK TRACKER

更新日: 2026-03-30 20:10 JST
運用メモ: このファイルを AI の日常入口にする。実行履歴は `progress.md` に記録し、ここには「次の判断に必要な情報」だけを残す。
補足: フェーズや大型節目の確認が必要になったときだけ [開発ロードマップ.md](開発ロードマップ.md) を開く。

## 現在の状況
- `iMac 2019` の観測常駐 `com.afrog.btc-monitor` は、今回の要約層改善を反映した `Ver02.3v2-OBS` へ更新しました。`.env` の `SYSTEM_LABEL` は `Ver02.3v2-OBS`、launchd 再起動後の実 PID は `90461` です。
- `2026-03-30 05:05 JST` の定刻出力で、`logs/last_result.json` / `logs/last_notified.json` / `heartbeat.txt` の更新を確認しました。`system_label` は `Ver02.3v2-OBS`、件名は `下方向バイアス / 下目線/見送り` で、再起動後の新ラベル反映は確認済みです。
- `Ver02.3v3` 向けの本格改善として、`no_trade_flags` と `risk_flags` の責務分離、`Critical_zone_warning` の warning 側移動、`long_setup/short_setup.blocking_flags` 追加、`evaluation_trace` の分離観測強化まで実装しました。
- 通知件名から単独の `総合強度` 表示を外し、本文と注意報本文は `方向の強さ` `実行しやすさ` `待機圧力` の 3 指標表示へ切り替えました。内部の `confidence` 数値は gate とログ互換のため維持しています。
- 今回の変更は scoring 本体の全面改造ではなく、`summary / advice` の誤読防止、`confidence` 分解、`evaluation_trace` 追加が中心です。
- `summary / advice` は `方向判断` と `いまの扱い` を分離し、`watch / invalid` では待機・見送り優先の文面へ切り替えました。
- `confidence_components`、`confidence_direction_shadow`、`confidence_execution_shadow`、`confidence_wait_shadow`、`evaluation_trace` を保存する実装まで反映済みです。
- live の `last_result.json` / `last_notified.json` で `evaluation_trace` と `chart_pattern_shadow` も出力済みです。次回観測では `evaluation_trace_version=v0.2` と件名の数値削除後フォーマットを確認する段階です。
- フェーズ判定はまだ `Ver02.3 / Phase 0 本番観測中` のままです。今回の更新は運用復旧と評価導線の安定化であり、`Phase 1` へはまだ昇格していません。
- 通知評価フォームは、JavaScript 構文エラー修正後に iCloud 配下の `評価シート入力フォーム.html` でも正常動作することを確認しました。主因は配置場所ではなく、生成 HTML 内の構文エラーでした。
- レビュー入力運用は「フォームで入力し、下のプレビュー全文を `通知評価シート.md` に貼り付ける」に固定しました。`Markdownを保存` は廃止し、`通知評価シート.md` を唯一の正本として扱います。
- フォーム画面では `2026-03-25 JST` 以降のレビュー対象だけを表示し、同じ境界より前の低精度レビューは `import_reviews()` と集計からも除外する実装にしました。
- フォーム UI は、通知時刻の大表示 `MM/DD HH:MM`、優先入力項目の強調、日本語ラベル化まで反映済みです。
- 直近の repo 検証として `.venv312/bin/python -m unittest tests.test_log_feedback` を実行し、11 件成功を確認しました。
- 本番 MBP2020 の接続先は `100.104.218.101` に更新しました。実務では引き続き `mbp2020-btc` alias を正本として使います。
- `mbp2020-btc` alias の実体を `100.104.218.101` へ更新し、Global_BOX と Obsidian 側の接続メモも同じ前提にそろえました。
- `tools/log_feedback.py`、`tests/test_log_feedback.py`、`運用資料/運用/実務/ログ検証と改善運用ガイド.md`、`Global_BOX/本番環境.md` を更新済みです。
- `tests/test_codex_cli_wrapper.py` は別件で未整理の変更が残っているため、今回のコミットには含めない前提で扱います。
- 旧 `Ver02.1` の待機系本文は「方向感は様子見」の中に方向判断と行動指示が混在していましたが、`Ver02.3v2-OBS` では件名と本文冒頭で `下方向バイアス` と `下目線だが現状は見送り` を分離できていることを実ログで確認しました。
- 今回の v3 実装で、通知抑止や signal tier 判定に位置リスクが `no_trade_flags` 経由で再混入しない構造へ修正しました。

## 次のタスク
1. 次回以降の `Ver02.3v3` 通知で、件名が数値なしフォーマットへ切り替わり、本文が 3 指標表示になっていることを数件確認する。
2. `watch / invalid` 相当の通知で、位置リスクだけでは main 通知抑止にならないことと、実行 blocker があるときだけ抑止されることを live ログでも確認する。
3. iCloud 側の `評価シート入力フォーム.html` を使って、件名の印象と本文 3 指標表示が誤読防止に効いたかをレビューする。
4. レビューがたまった段階で `daily-sync` もしくは AI への「集計して」で `user_reviews.csv` と集計を更新する。
5. `Phase 0` 完了条件を、通知後 24 時間評価の一周完了とレビュー蓄積で判断する。満たすまでは `Phase 1` へ上げない。
6. `tests/test_codex_cli_wrapper.py` の不一致は、通知評価フォーム運用が落ち着いたあとに切り分けて整合化する。

## ブロッカー
- 過去に iCloud 配下 HTML を不安定と判断したが、主因は JavaScript 構文エラーでした。現在は iCloud 側フォームを正式運用に戻しています。
- フォームは表示と入力導線までは安定したが、最終反映は `通知評価シート.md` への全文貼り付け前提です。完全自動保存にはしていません。
- MBP2020 本番は LaunchAgent 復旧までは完了したが、復旧後の heartbeat 更新確認は別系統で継続中です。
- repo の別件として `tests/test_codex_cli_wrapper.py` の不一致が残っていますが、今回のレビュー運用とは切り離して扱います。

## 完了条件
- レビュー運用: iCloud 側フォームからの入力と `通知評価シート.md` への全文貼り付けで、通知評価を迷わず継続できる状態にする。
- Phase 0: 通知発生から 24 時間後評価までを本番で 1 周完了し、`2026-03-25 JST` 以降レビューを数件ためて傾向を読める状態にする。
- Phase 1: `primary_setup_status=ready` を本有効として、正式指標を実データで確認できる状態にする。現時点では未到達。
