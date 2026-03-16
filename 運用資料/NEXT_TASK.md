# NEXT TASK TRACKER

更新日: 2026-03-16 19:14 JST
運用メモ: このファイルを AI の日常入口にする。実行履歴は `progress.md` に記録し、ここには「次の判断に必要な情報」だけを残す。
補足: フェーズや大型節目の確認が必要になったときだけ [開発ロードマップ.md](開発ロードマップ.md) を開く。

## 現在の状況
- 現在の役割は固定済み。本番は `Ver02.1 API`、開発は `Ver02.1 CLI`。`Ver01` 本番常駐は `2026-03-16 19:14 JST` に停止済みで、必要時だけ再開する。
- 日常の本番確認は `zsh tools/sync_ver021_prod_status.sh` で軽量同期し、まず `tmp/status/prod_status_summary.md` と `tmp/status/prod_status_sync_last_success.txt` だけを見る。
- 詳細取得は鍵認証の `tools/pull_ver021_prod_logs_auto.sh` を標準とし、パスワード版は例外手順に分離済み。
- `Phase 1` の土台実装は完了しており、今は通知発生待ちで実データ評価にはまだ入っていない。
- 上昇初動の取り逃がし対策として、実効設定を `CONFIDENCE_LONG_MIN=40`、`MIN_RR_RATIO=1.15`、`sweep_incomplete=+4` へ調整済み。確認入口は `運用資料/運用/採点調整シート.md`。
- 本命通知とは別に `注意報メール` を追加済み。件名の強さレイヤーは `👀 [注意報]`、`🟡 好条件接近`、`🔥 ゴールデン条件`。
- 注意報の閾値は `ATTENTION_ALERT_SCORE_MIN=55`、`ATTENTION_ALERT_GAP_MIN=15`、`ATTENTION_ALERT_COOLDOWN_MINUTES=60`。本命通知とは別履歴で管理する。
- `Ver01` は比較完了として常駐停止済み。以後の観測と改善判断は `Ver02.1` を主対象に進める。
- この実行環境では外部 SSH が制限されることがあり、失敗時は疎通可能環境で再試行する。

## 次のタスク
1. 次回自然更新で、緩和後の `Ver02.1` がロング初動をどこまで拾えるか確認する。対象は `bias / confidence / prelabel / suppress_reason_codes / no_trade_flags`。
2. 注意報メールの頻度と実用性を自然観測で確認する。対象は `notification_kind=attention`、件名、方向、クールダウンの効き方。
3. 本命通知されないロング回が出たら、`運用資料/運用/採点調整シート.md` を入口に `logs/csv/trades.csv` と `logs/signals/*.json` を照合する。
4. 異常や通知が出たときだけ `zsh tools/pull_ver021_prod_logs_auto.sh` で詳細を掘り、材料が増えたら `運用資料/reports/cli_api定期比較レポート.md` を更新する。
5. 最初の通知から24時間後に本番で `./.venv312_prod/bin/python tools/log_feedback.py daily-sync` を実行し、`signal_outcomes.csv` / `shadow_log.csv` / `user_reviews.csv` の初回更新を確認する。
6. `📝通知レビュー.md` で `review_status=done` を1件以上作り、`logic_validated` と `Phase 1` の正式評価開始へつなげる。

## ブロッカー
- 通知は発生済みだが、`daily-sync` 実行タイミング到来とレビュー反映がまだで、`logic_validated` の本番評価に進み切れていない。
- `signal_outcomes.csv` / `user_reviews.csv` は未生成。
- `phase1_active` は実装済みだが、本番データ蓄積がまだ無い。

## 完了条件
- Phase 0: 通知発生から 24 時間後評価まで（`daily-sync` + レビュー反映）を本番で 1 周完了。
- Phase 1: `primary_setup_status=ready` を本有効として、正式指標を実データで確認できる状態にする。
