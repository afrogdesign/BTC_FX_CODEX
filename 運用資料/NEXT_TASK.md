# NEXT TASK TRACKER

更新日: 2026-03-17 04:51 JST
運用メモ: このファイルを AI の日常入口にする。実行履歴は `progress.md` に記録し、ここには「次の判断に必要な情報」だけを残す。
補足: フェーズや大型節目の確認が必要になったときだけ [開発ロードマップ.md](開発ロードマップ.md) を開く。

## 現在の状況
- 現在の役割は固定済み。本番は `Ver02.1 CLI` を 1 本だけ稼働、開発 `Ver02.1 CLI` 常駐は `2026-03-17 04:48 JST` に停止して切り分け観測へ入った。`Ver01` 本番常駐は `2026-03-16 19:14 JST` に停止済み、旧 `Ver02.1 API` 実体は `/Users/marupro/CODEX/BTC_FX_CODEX_ver02_API_backup_20260316_2030` へ退避済み。
- 日常の本番確認は `zsh tools/sync_ver021_prod_status.sh` で軽量同期し、まず `tmp/status/prod_status_summary.md` と `tmp/status/prod_status_sync_last_success.txt` だけを見る。
- 本番軽量同期ジョブ `com.afrog.btc-monitor-status-sync` は常設運用とし、一時ジョブ扱いにしない。
- 開発環境で「何が動いているか」は `運用資料/運用/環境/開発環境_実行ファイル一覧.md` と `/Users/marupro/CODEX/Global_BOX/10_共通仕様/開発環境_実行ファイル一覧.md` を入口に確認する。
- 詳細取得は鍵認証の `tools/pull_ver021_prod_logs_auto.sh` を標準とし、パスワード版は例外手順に分離済み。
- `Phase 1` の土台実装は完了しており、今は通知発生待ちで実データ評価にはまだ入っていない。
- 上昇初動の取り逃がし対策として、実効設定を `CONFIDENCE_LONG_MIN=40`、`MIN_RR_RATIO=1.15`、`sweep_incomplete=+4` へ調整済み。確認入口は `運用資料/運用/調整/採点調整シート.md`。
- 本命通知とは別に `注意報メール` を追加済み。件名の強さレイヤーは `👀 [注意報]`、`🟡 好条件接近`、`🔥 ゴールデン条件`。
- 注意報の閾値は `ATTENTION_ALERT_SCORE_MIN=52`、`ATTENTION_ALERT_GAP_MIN=12`、`ATTENTION_ALERT_COOLDOWN_MINUTES=30`。本命通知とは別履歴で管理する。
- `Ver01` は比較完了として常駐停止済み。以後の観測と改善判断は `Ver02.1` を主対象に進める。
- 本番 `Ver02.1 CLI` は復旧済みで、自然更新と AI 審査の復帰まで確認済み。03/17 未明の重複メールは本番二重起動が主因と判断し、余分な本番プロセスは停止済み。しばらくは本番1本での観測を優先し、急ぎの追加実装は入れない。
- 通知本文の読みやすさ改善は検討価値が高いが、現時点では実装に入らず、`運用資料/参考資料/自然文章化設計書.md` を参考設計として保持する。
- この実行環境では外部 SSH が制限されることがあり、失敗時は疎通可能環境で再試行する。

## 次のタスク
1. しばらくは `tmp/status/prod_status_summary.md` を入口に、本番 `Ver02.1 CLI` 1本運用での自然更新と通知品質を観測する。
2. 次回通知または異常が出たときだけ `zsh tools/pull_ver021_prod_logs_auto.sh` で詳細を掘り、本番側で `ai_advice_error` / `ai_summary_error` が出ていないかを確認する。
3. 本命通知されないロング回や違和感のある本文が出たときだけ、`運用資料/運用/調整/採点調整シート.md` と `運用資料/参考資料/自然文章化設計書.md` を入口に見直す。
4. 最初の通知から24時間後に本番で `./.venv312_prod/bin/python tools/log_feedback.py daily-sync` を実行し、`signal_outcomes.csv` / `shadow_log.csv` / `user_reviews.csv` の初回更新を確認する。
5. `📝通知レビュー.md` で `review_status=done` を1件以上作り、`logic_validated` と `Phase 1` の正式評価開始へつなげる。

## ブロッカー
- 直近の急ぎブロッカーはない。現在は本番観測フェーズ。
- `daily-sync` 実行タイミング到来とレビュー反映がまだで、`logic_validated` の本番評価にはまだ進み切れていない。
- `signal_outcomes.csv` / `user_reviews.csv` は未生成。
- `phase1_active` は実装済みだが、本番 `CLI` へ切り替え直後のため、連続サイクルの母数がまだ無い。

## 完了条件
- Phase 0: 通知発生から 24 時間後評価まで（`daily-sync` + レビュー反映）を本番で 1 周完了。
- Phase 1: `primary_setup_status=ready` を本有効として、正式指標を実データで確認できる状態にする。
