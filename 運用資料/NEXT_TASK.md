# NEXT TASK TRACKER

更新日: 2026-03-13 17:05 JST
運用メモ: このファイルを AI の日常入口にする。実行履歴は `progress.md` に記録し、ここには「次の判断に必要な情報」だけを残す。
補足: フェーズや大型節目の確認が必要になったときだけ [開発ロードマップ.md](開発ロードマップ.md) を開く。

## 現在の状況
- 運用ブランチは `main` / `ver02.1-v1` / `snapshot/ver02.1` / `ver02.0-stable` / `ver01-baseline` に整理済み。
- 役割は固定済み（本番: `Ver02.1 API`、開発: `Ver02.1 CLI`、Ver01 は比較基準）。
- 自然観測の最新確認は 2026-03-13 15:23 JST。開発側は `signals=20260313_060501`（15:05 JST）まで更新、`heartbeat.txt` / `last_result.json` も 15:05 JST へ追随を確認。
- `logs/errors` の最新は `20260312_220848_ai_summary_error.log` のまま（2026-03-13 07:08 JST 以降の新規エラーなし）。
- API 側 snapshot は鍵認証で再取得済み。最新は `20260313_060501`（15:05 JST）で、同時刻比較母数をさらに追加できた。
- `MBP2020` への標準接続は `mbp2020-btc` alias + 専用鍵 `~/.ssh/mbp2020_btc_monitor` へ切替済み。`pull_ver021_prod_logs_auto.sh` は鍵認証で自動取得できることを確認した。
- 本番状態の普段使い入口は `zsh tools/sync_ver021_prod_status.sh` に切り替えた。軽量取得後に `tmp/status/prod_status_summary.json` / `tmp/status/prod_status_summary.md` を作る運用にする。
- `tmp/` は `status/`、`snapshots/`、`errors/` へ整理済み。日常確認は `tmp/status/` だけを見る。
- `pull_ver021_prod_logs_auto.sh` は鍵認証専用を標準にした。パスワード fallback は `pull_ver021_prod_logs_with_password.sh` を明示的に使う例外手順へ分離した。
- 今後は、デプロイ先データが必要でも AI がいきなり SSH の重いログを読むのではなく、先に Mac 側スクリプトで軽量同期してから参照する。
- 定期処理は Mac 側 `launchd` で `tools/sync_ver021_prod_status.sh` を 2 時間ごとに回す前提へ切り替えた。
- `com.afrog.btc-monitor-status-sync` は 2026-03-13 15:53 JST に登録済み。`launchctl print` で `run interval = 7200 seconds`、`last exit code = 0` を確認した。
- 普段の本番確認は、まず `tmp/status/prod_status_summary.md` と `tmp/status/prod_status_sync_last_success.txt` だけを見る。詳細ログは例外時だけ開く。
- `progress.md` は軽い入口にし、重い履歴は `運用資料/progress_weekly/` へ週ごとに退避する運用へ切り替えた。
- Obsidian 側 `資料/` に、現行運用整理・軽量運営モデル・Global_BOX反映設計の 3 本を追加し、次の共通化検討に入れる状態へ整理した。
- `Global_BOX` 本体は軽量運営前提へ更新した。`AGENTS_TEMPLATE.md`、`記録ファイル運用ルールテンプレート.md`、`progressテンプレート.md`、`NEXT_TASKテンプレート.md`、`案件初期化スクリプト.sh` を見直し、`進行状況/` のシンボリックリンク運用も維持した。
- `/Users/marupro/CODEX/` 配下の他案件 `AGENTS.md` も、軽量運営版の原則へ順次反映した。`IZUZYA_SP`、`インキャビラジオ`、`レシート処理`、`BTC_FX_Claude`、sandbox 側で入口順・軽量同期前提・更新条件・Git 粒度をそろえた。
- `運用資料/運用/記録ファイル運用ルール.md` に、秘書メモを崩さないためのチェックを追加した。`👩‍⚖️秘書.md` も人向け入口の短い形へ再整理した。
- Phase 1 は土台実装済み（サイズ計画・出口計画・ログ列追加）。実データ評価は通知発生待ち。
- この実行環境では外部 SSH が制限される場合があり、失敗時は `ssh: connect to host ... Operation not permitted` になる。疎通可能環境で再試行する。

## 次のタスク
1. 次の作業では、秘書メモが再び重くならないよう、必要なら `Global_BOX` 側のテンプレートにも同じチェック項目を逆輸入する。
2. 次回は `tmp/status/prod_status_summary.md` の更新時刻と `tmp/status/prod_status_sync_last_success.txt` を見て、2 時間ごとの軽量同期が継続しているか確認する。
3. 普段の本番確認は、まず `tmp/status/prod_status_summary.md` と `tmp/status/prod_status_sync_last_success.txt` を見て、異常や通知があるときだけ `zsh tools/pull_ver021_prod_logs_auto.sh` で詳細を掘る。
4. 鍵認証で詳細取得できない場面が出たときだけ、例外手順として `zsh tools/pull_ver021_prod_logs_with_password.sh` を使う。
5. 次回自然更新で CLI 側 `heartbeat` / `last_result` 継続更新と `ai_summary_error` 再発有無を確認する。
6. 通知発生時または比較材料がまとまって増えたときに、API/CLI の件名・本文・`notify_reason_codes`・`decision/quality/warnings` 差分を `運用資料/reports/cli_api定期比較レポート.md` に追記する。
7. 最初の通知から24時間後に本番で `./.venv312_prod/bin/python tools/log_feedback.py daily-sync` を実行し、`signal_outcomes.csv` / `shadow_log.csv` / `user_reviews.csv` の初回更新を確認する。
8. `📝通知レビュー.md` で `review_status=done` を1件以上作り、`logic_validated` 反映を確認する。
9. Phase 1 の正式評価（`phase1_active=true` 母数、TP1到達率、`max_size_capped` 発生率）を開始する。

## ブロッカー
- 通知発生がまだ無く、`daily-sync` と `logic_validated` の本番評価に進めない。
- `signal_outcomes.csv` / `user_reviews.csv` は未生成。
- `phase1_active` は実装済みだが、本番データ蓄積がまだ無い。

## 完了条件
- Phase 0: 通知発生から 24 時間後評価まで（`daily-sync` + レビュー反映）を本番で 1 周完了。
- Phase 1: `primary_setup_status=ready` を本有効として、正式指標を実データで確認できる状態にする。
