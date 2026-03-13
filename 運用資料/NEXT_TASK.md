# NEXT TASK TRACKER

更新日: 2026-03-13 15:04 JST
運用メモ: このファイルを AI の日常入口にする。実行履歴は `progress.md` に記録し、ここには「次の判断に必要な情報」だけを残す。
補足: フェーズや大型節目の確認が必要になったときだけ [開発ロードマップ.md](開発ロードマップ.md) を開く。

## 現在の状況
- 運用ブランチは `main` / `ver02.1-v1` / `snapshot/ver02.1` / `ver02.0-stable` / `ver01-baseline` に整理済み。
- 役割は固定済み（本番: `Ver02.1 API`、開発: `Ver02.1 CLI`、Ver01 は比較基準）。
- 自然観測の最新確認は 2026-03-13 14:57 JST。開発側は `signals=20260313_050500`（14:05 JST）まで更新、`heartbeat.txt` / `last_result.json` も 14:05 JST へ追随を確認。
- `logs/errors` の最新は `20260312_220848_ai_summary_error.log` のまま（2026-03-13 07:08 JST 以降の新規エラーなし）。
- API 側 snapshot は 14:57 JST 時点で再取得済み。最新は `20260313_050500`（14:05 JST）で、11:05 JST 帯以降の比較母数を追加できた。
- `tools/pull_ver021_prod_logs.sh` は `BTC_MONITOR_PROD_SSH_PASSWORD` を使った非対話実行に対応し、Automation でも取得可能になった。
- Automation 安定化として、API 取得は `zsh tools/pull_ver021_prod_logs_auto.sh`、秘書同期は `zsh tools/sync_secretary_note.sh` を固定入口にした。
- Phase 1 は土台実装済み（サイズ計画・出口計画・ログ列追加）。実データ評価は通知発生待ち。

## 次のタスク
1. 次回は `zsh tools/pull_ver021_prod_logs_auto.sh` で API 側 snapshot を追加 pull し、同時刻比較母数を継続拡張する。
2. 次回自然更新で CLI 側 `heartbeat` / `last_result` 継続更新と `ai_summary_error` 再発有無を確認する。
3. 通知発生時に API/CLI の件名・本文・`notify_reason_codes`・`decision/quality/warnings` 差分を `運用資料/reports/cli_api定期比較レポート.md` に追記する。
4. 最初の通知から24時間後に本番で `./.venv312_prod/bin/python tools/log_feedback.py daily-sync` を実行し、`signal_outcomes.csv` / `shadow_log.csv` / `user_reviews.csv` の初回更新を確認する。
5. `📝通知レビュー.md` で `review_status=done` を1件以上作り、`logic_validated` 反映を確認する。
6. Phase 1 の正式評価（`phase1_active=true` 母数、TP1到達率、`max_size_capped` 発生率）を開始する。

## ブロッカー
- 通知発生がまだ無く、`daily-sync` と `logic_validated` の本番評価に進めない。
- `signal_outcomes.csv` / `user_reviews.csv` は未生成。
- `phase1_active` は実装済みだが、本番データ蓄積がまだ無い。

## 完了条件
- Phase 0: 通知発生から 24 時間後評価まで（`daily-sync` + レビュー反映）を本番で 1 周完了。
- Phase 1: `primary_setup_status=ready` を本有効として、正式指標を実データで確認できる状態にする。
