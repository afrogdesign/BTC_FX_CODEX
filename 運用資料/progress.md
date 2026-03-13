# Progress Log

更新日: 2026-03-13 16:31 JST

このファイルは、現在の軽い進行ログ入口です。
重い履歴は `progress_weekly/` へ週ごとに退避します。

## 現在の運用

- ここには、新しい事実や実作業があったときだけ追記する。
- 報告系ファイルを更新したこと自体は、原則としてここへ書かない。
- 書く対象は、システム動作、運用手順、スクリプト、設定、検証結果など、監視システム本体に関わる変化を優先する。

## 週次アーカイブ

- 2026-W11: [progress_weekly/2026-W11.md](progress_weekly/2026-W11.md)

## 最新の実作業

- 2026-03-13 16:31 JST
  - 軽量同期の出力先を `tmp/status/`、詳細 snapshot を `tmp/snapshots/`、失敗記録を `tmp/errors/` へ整理した。
  - 詳細取得の標準を鍵認証専用に寄せ、パスワード fallback は `tools/pull_ver021_prod_logs_with_password.sh` へ分離した。
  - 週次 `progress` 圧縮用に `tools/archive_progress_week.sh` を追加し、日常確認をさらに軽くした。
