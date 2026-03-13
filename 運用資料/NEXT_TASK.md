# NEXT TASK TRACKER

更新日: 2026-03-13 13:36 JST
運用メモ: このファイルを AI の日常入口にする。実行履歴は `progress.md` に記録し、ここには「次の判断に必要な情報」だけを残す。
補足: フェーズや大型節目の確認が必要になったときだけ [開発ロードマップ.md](開発ロードマップ.md) を開く。

## 現在の状況
- `📒打ち合わせノート.md` の更新タイミングは「一定の作業が終わったら行う定期更新」に整理した。
- `📒打ち合わせノート.md` は「人が日々の作業要点を時系列で追う記録」として役割を再定義した。
- `運用/記録ファイル運用ルール.md` の秘書メモ表現を調整し、「古い不要情報は残しすぎず、今も有効な前提だけを短く残す」に整理した。
- 記録ファイルの相関ルールは `運用/記録ファイル運用ルール.md` へ分離し、`AGENTS.md` は要点参照に整理済み。
- AI の日常入口は `NEXT_TASK.md` → `開発ロードマップ.md` に固定し、`👩‍⚖️秘書.md` は人向け資料へ分離済み。
- `NEXT_TASK.md` は判断用、`progress.md` は履歴用として運用分離を明文化済み。
- 運用ブランチは `main` / `ver02.1-v1` / `snapshot/ver02.1` / `ver02.0-stable` / `ver01-baseline` に整理済み。
- 役割は固定済み（本番: `Ver02.1 API`、開発: `Ver02.1 CLI`、Ver01 は比較基準）。
- 自然観測の最新確認は 2026-03-13 12:00 JST。開発側は `signals=20260313_020500`（11:05 JST）まで更新、直近 4 サイクルで `ai_decision` / `summary_body` は連続成功。
- `logs/errors` の最新は `20260312_220848_ai_summary_error.log` で、07:08 JST 以降の新規エラーは未確認。
- API 側は 10:50 JST 取得 snapshot（`20260312_220500`〜`20260313_010500`）までは確認済み。11:05 JST 帯の同時刻比較母数は未追加。
- Phase 1 は土台実装済み（サイズ計画・出口計画・ログ列追加）。実データ評価は通知発生待ち。

## 次のタスク
1. API 側 snapshot を追加 pull し、11:05 JST 帯の API/CLI 同時刻比較を 1 件以上増やす。
2. 次回自然更新で CLI 側 `heartbeat` / `last_result` 継続更新と `ai_summary_error` 再発有無を確認する。
3. 通知発生時に API/CLI の件名・本文・`notify_reason_codes`・`decision/quality/warnings` 差分を `運用資料/reports/cli_api定期比較レポート.md` に追記する。
4. 最初の通知から24時間後に本番で `./.venv312_prod/bin/python tools/log_feedback.py daily-sync` を実行し、`signal_outcomes.csv` / `shadow_log.csv` / `user_reviews.csv` の初回更新を確認する。
5. `📝通知レビュー.md` で `review_status=done` を1件以上作り、`logic_validated` 反映を確認する。
6. Phase 1 の正式評価（`phase1_active=true` 母数、TP1到達率、`max_size_capped` 発生率）を開始する。

## ブロッカー
- API 側の追加 snapshot 未取得のため、同時刻比較の母数が不足。
- 通知発生がまだ無く、`daily-sync` と `logic_validated` の本番評価に進めない。
- `signal_outcomes.csv` / `user_reviews.csv` は未生成。
- `phase1_active` は実装済みだが、本番データ蓄積がまだ無い。

## 完了条件
- Phase 0: 通知発生から 24 時間後評価まで（`daily-sync` + レビュー反映）を本番で 1 周完了。
- Phase 1: `primary_setup_status=ready` を本有効として、正式指標を実データで確認できる状態にする。
