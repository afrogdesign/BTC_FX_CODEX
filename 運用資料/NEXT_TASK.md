# NEXT TASK TRACKER

更新日: 2026-03-23 18:35 JST
運用メモ: このファイルを AI の日常入口にする。実行履歴は `progress.md` に記録し、ここには「次の判断に必要な情報」だけを残す。
補足: フェーズや大型節目の確認が必要になったときだけ [開発ロードマップ.md](開発ロードマップ.md) を開く。

## 現在の状況
- 本番は `MBP2020` の `com.afrog.btc-monitor-ver021`。開発側の補助ジョブ `com.afrog.btc-monitor-status-sync` は `iMac 2019` を常設先にし、`MBA M4` には常設しない。
- 本番 `.env` は `cli / cli` だが、実装は `CLI 優先 + API 自動フォールバック`。件名と `system_mode_label` は実際に使えた経路で変わる。
- 日常確認の入口は `tmp/status/prod_status_summary.md` と `tmp/status/prod_status_sync_last_success.txt`。詳細が必要なときだけ `tools/pull_ver021_prod_logs_auto.sh` を使う。
- `Phase 0` は本番観測中。`Phase 1` の土台実装は入っているが、レビュー反映と実データ評価はまだ不足。
- Mac 横断の実行ファイル一覧は `Global_BOX` を正本にし、この案件内には BTC 固有メモだけ残す。
- 今日以降は `iMac 2019` と `MBA M4` の両方で作業する前提。開始前に `git pull --rebase`、切替前に commit / push、次の判断は `NEXT_TASK.md` へ寄せる。軽量同期とログ取得の常設基盤は `iMac 2019` を優先する。

## 次のタスク
1. 本番の自然更新を観測し、`CLI` 失敗回だけ `API` へ自動フォールバックしているか確認する。
2. 通知または異常が出た回だけ本番詳細ログを掘り、`ai_advice_error` / `ai_summary_error`、件名の `[CLI]` / `[API]`、`system_mode_label` を確認する。
3. 次の通知改善では、AI 自由作文を減らし、コード側テンプレート主導で本文を安定化する。
4. `通知評価シート.md` に `review_status=done` を作り、`logic_validated` と `Phase 1` の正式評価開始へつなげる。
5. 判定改善を再開するときは、`評価システム改善仕様書_Ver02x-Ver05接続.md` を入口に shadow 指標の最小版から着手する。

## ブロッカー
- 緊急ブロッカーはない。現在は本番観測フェーズ。
- `codex` は本番機で未ログインのため、CLI は毎回成功する前提ではない。
- `daily-sync` は回り始めているが、レビュー反映母数がまだ少ない。
- 2 台並行作業では、同じファイルを未 push のまま両方で触ると競合しやすい。特に `NEXT_TASK.md`、`progress.md`、運用ルール群は切替前の同期必須。

## 完了条件
- Phase 0: 通知発生から 24 時間後評価までを本番で 1 周完了する。
- Phase 1: `primary_setup_status=ready` を本有効として、正式指標を実データで確認できる状態にする。
