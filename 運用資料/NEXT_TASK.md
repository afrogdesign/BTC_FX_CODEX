# NEXT TASK TRACKER

更新日: 2026-04-13 11:45 JST

運用メモ: AI の日常入口として使う。履歴は `履歴/progress.md` に残し、ここには次の判断に必要な情報だけを書く。

## 現在の状況

- 現行主流は `iMac 2019` 上の `Ver02.4-v1`。日常の通知観測と品質判断はこの 1 本で進める。
- `MBP2020` の `Ver02.1` は停止・凍結済み。必要なときだけ archive と過去ログを参照する。
- 現在フェーズは `Phase 0` 本番観測中。主判断は `Phase 1` の本有効確認へ移している。
- 事後評価運用は `daily-sync` と `sync-ai-post-reviews` の 2 段構成。レビューの主軸は AI、必要なケースだけ `human_override` を使う。
- `sync-ai-post-reviews` の自動失敗は修正済み。`com.afrog.btc-ai-post-reviews` は `last exit code = 0` を確認した。
- AI 事後評価の 1 日上限は `AI_POST_REVIEW_DAILY_MAX=4`。現在の進捗は `完了 38 / 未完了 26`、いま未処理だが 24 時間後評価済みの backlog は 19 件。
- 直近の通知発生は `1日8〜9件` が続いており、全件追随より `main` 通知の代表例を優先して改善観測する前提で進める。

## 次のタスク

1. `daily-sync` の最新結果どおり `primary_setup_status=ready=0` と `phase1_active=true=0` が続いているため、`Phase 1` 本有効待ちを維持しつつ通知観測を継続する。
2. `15分足評価=poor` が 14 件、`tp_eval=too_close` が 28 件、`sl_eval=too_loose` が 14 件あるため、まず `15分足のRR不足` と `TP近すぎ / SL広すぎ` の組み合わせを主論点にする。
3. `ENTRY_OK` が期間レポートで `poor_entry 7/7` と出ているため、`ENTRY_OK + invalid` や `direction_execution_conflict` の対象通知を切り出し、`position_risk` と `confidence` 側の閾値見直し候補を詰める。
4. 実送信メールの `📊 / 🟠 / 🔥 / 👀` 表示と 3 段チャートを見て、直感とズレる通知がないか確認する。

## ブロッカー

- フォーム保存は `serve-review-form` が前提。未起動だと localStorage にしか残らない。
- `tests/test_codex_cli_wrapper.py` と `tests/test_log_feedback.py` の既知不一致は別件として残っている。
- 通知の増加ペースは `1日8〜9件`、AI新規処理は `1日4件` のため、backlog を解消するには日数がかかる。全件追随ではなく代表例優先の運用前提を崩さない。

## 完了条件

- `daily-sync` と `sync-ai-post-reviews` の運用が継続して回る。
- レビュー保存から `review_form_state.json`、`user_reviews.csv`、要約更新までの流れを維持する。
- `Phase 1` の本有効確認を実データで追える状態を保つ。
