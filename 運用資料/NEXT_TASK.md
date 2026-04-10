# NEXT TASK TRACKER

更新日: 2026-04-11 11:00 JST

運用メモ: AI の日常入口として使う。履歴は `履歴/progress.md` に残し、ここには次の判断に必要な情報だけを書く。

## 現在の状況

- 現行主流は `iMac 2019` 上の `Ver02.4-v1`。日常の通知観測と品質判断はこの 1 本で進める。
- `MBP2020` の `Ver02.1` は停止・凍結済み。必要なときだけ archive と過去ログを参照する。
- 現在フェーズは `Phase 0` 本番観測中。主判断は `Phase 1` の本有効確認へ移している。
- 事後評価運用は `daily-sync` と `sync-ai-post-reviews` の 2 段構成。レビューの主軸は AI、必要なケースだけ `human_override` を使う。

## 次のタスク

1. `daily-sync` の最新結果で `primary_setup_status=ready` と `phase1_active=true` の母数を確認する。
2. `launchd` の `com.afrog.btc-feedback-daily-sync` と `com.afrog.btc-ai-post-reviews` が動いているか確認する。
3. `15分足評価=poor` や `tp_eval=too_far / too_close` がどの通知で出ているかを見て、価格帯・SL・TP の改善対象を切り出す。
4. 実送信メールの `📊 / 🟠 / 🔥 / 👀` 表示と 3 段チャートを見て、直感とズレる通知がないか確認する。

## ブロッカー

- フォーム保存は `serve-review-form` が前提。未起動だと localStorage にしか残らない。
- `tests/test_codex_cli_wrapper.py` と `tests/test_log_feedback.py` の既知不一致は別件として残っている。

## 完了条件

- `daily-sync` と `sync-ai-post-reviews` の運用が継続して回る。
- レビュー保存から `review_form_state.json`、`user_reviews.csv`、要約更新までの流れを維持する。
- `Phase 1` の本有効確認を実データで追える状態を保つ。
