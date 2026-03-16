# NEXT TASK TRACKER

更新日: 2026-03-16 21:10 JST
運用メモ: このファイルを AI の日常入口にする。実行履歴は `progress.md` に記録し、ここには「次の判断に必要な情報」だけを残す。
補足: フェーズや大型節目の確認が必要になったときだけ [開発ロードマップ.md](開発ロードマップ.md) を開く。

## 現在の状況
- 現在の役割は固定済み。本番は `Ver02.1 CLI`、開発は `Ver02.1 CLI`。`Ver01` 本番常駐は `2026-03-16 19:14 JST` に停止済み、旧 `Ver02.1 API` 実体は `/Users/marupro/CODEX/BTC_FX_CODEX_ver02_API_backup_20260316_2030` へ退避済み。
- 日常の本番確認は `zsh tools/sync_ver021_prod_status.sh` で軽量同期し、まず `tmp/status/prod_status_summary.md` と `tmp/status/prod_status_sync_last_success.txt` だけを見る。
- 本番軽量同期ジョブ `com.afrog.btc-monitor-status-sync` は常設運用とし、一時ジョブ扱いにしない。
- 開発環境で「何が動いているか」は `運用資料/運用/環境/開発環境_実行ファイル一覧.md` と `/Users/marupro/CODEX/Global_BOX/10_共通仕様/開発環境_実行ファイル一覧.md` を入口に確認する。
- 詳細取得は鍵認証の `tools/pull_ver021_prod_logs_auto.sh` を標準とし、パスワード版は例外手順に分離済み。
- `Phase 1` の土台実装は完了しており、今は通知発生待ちで実データ評価にはまだ入っていない。
- 上昇初動の取り逃がし対策として、実効設定を `CONFIDENCE_LONG_MIN=40`、`MIN_RR_RATIO=1.15`、`sweep_incomplete=+4` へ調整済み。確認入口は `運用資料/運用/調整/採点調整シート.md`。
- 本命通知とは別に `注意報メール` を追加済み。件名の強さレイヤーは `👀 [注意報]`、`🟡 好条件接近`、`🔥 ゴールデン条件`。
- 注意報の閾値は `ATTENTION_ALERT_SCORE_MIN=52`、`ATTENTION_ALERT_GAP_MIN=12`、`ATTENTION_ALERT_COOLDOWN_MINUTES=30`。本命通知とは別履歴で管理する。
- `Ver01` は比較完了として常駐停止済み。以後の観測と改善判断は `Ver02.1` を主対象に進める。
- 本番 `Ver02.1 CLI` は `2026-03-16 20:40 JST` に再起動し、`com.afrog.btc-monitor-ver021` は `running` を確認済み。まずは次の自然サイクルで継続更新を確認する。
- この実行環境では外部 SSH が制限されることがあり、失敗時は疎通可能環境で再試行する。

## 次のタスク
1. 次回自然更新で、本番 `Ver02.1 CLI` の `heartbeat.txt` と `last_result.json` が継続更新されるか確認する。
2. 本番 `Ver02.1 CLI` の初回通知発生後、`notification_kind`、件名、`notify_reason_codes`、AI助言の出力品質を確認する。
3. 本命通知されないロング回が出たら、`運用資料/運用/調整/採点調整シート.md` を入口に `logs/csv/trades.csv` と `logs/signals/*.json` を照合する。
4. 異常や通知が出たときだけ `zsh tools/pull_ver021_prod_logs_auto.sh` で詳細を掘り、材料が増えたら `運用資料/reports/cli_api定期比較レポート.md` を更新する。
5. 最初の通知から24時間後に本番で `./.venv312_prod/bin/python tools/log_feedback.py daily-sync` を実行し、`signal_outcomes.csv` / `shadow_log.csv` / `user_reviews.csv` の初回更新を確認する。
6. `📝通知レビュー.md` で `review_status=done` を1件以上作り、`logic_validated` と `Phase 1` の正式評価開始へつなげる。

## ブロッカー
- 通知は発生済みだが、`daily-sync` 実行タイミング到来とレビュー反映がまだで、`logic_validated` の本番評価に進み切れていない。
- `signal_outcomes.csv` / `user_reviews.csv` は未生成。
- `phase1_active` は実装済みだが、本番 `CLI` へ切り替え直後のため、連続サイクルの母数がまだ無い。

## 完了条件
- Phase 0: 通知発生から 24 時間後評価まで（`daily-sync` + レビュー反映）を本番で 1 周完了。
- Phase 1: `primary_setup_status=ready` を本有効として、正式指標を実データで確認できる状態にする。
