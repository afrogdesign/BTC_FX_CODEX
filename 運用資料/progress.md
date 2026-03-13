# Progress Log

更新日: 2026-03-13 17:03 JST

このファイルは、現在の軽い進行ログ入口です。
重い履歴は `progress_weekly/` へ週ごとに退避します。

## 現在の運用

- ここには、新しい事実や実作業があったときだけ追記する。
- 報告系ファイルを更新したこと自体は、原則としてここへ書かない。
- 書く対象は、システム動作、運用手順、スクリプト、設定、検証結果など、監視システム本体に関わる変化を優先する。

## 週次アーカイブ

- 2026-W11: [progress_weekly/2026-W11.md](progress_weekly/2026-W11.md)

## 最新の実作業

- 2026-03-13 17:03 JST
  - `/Users/marupro/CODEX/` 配下の他案件 `AGENTS.md` を軽量運営ルールへそろえた。
  - `IZUZYA_SP`、`インキャビラジオ`、`レシート処理`、`BTC_FX_Claude`、sandbox 側で、軽量同期前提・更新条件・Git 粒度・入口順を見直した。
  - `git 管理外` の案件はファイル反映まで、`git 管理下` の案件は `AGENTS.md` だけを独立して扱う前提で整理した。
- 2026-03-13 16:31 JST
  - 軽量同期の出力先を `tmp/status/`、詳細 snapshot を `tmp/snapshots/`、失敗記録を `tmp/errors/` へ整理した。
  - 詳細取得の標準を鍵認証専用に寄せ、パスワード fallback は `tools/pull_ver021_prod_logs_with_password.sh` へ分離した。
  - 週次 `progress` 圧縮用に `tools/archive_progress_week.sh` を追加し、日常確認をさらに軽くした。
- 2026-03-13 16:32 JST
  - 停止済み Automation の名残を現行文書から外し、`tools/sync_secretary_note.sh` を削除した。
  - `tools/archive_progress_week.sh` の圧縮を強め、`progress_weekly/2026-W11.md` を約 140KB から約 96KB へ縮小した。
- 2026-03-13 16:38 JST
  - Obsidian 側 `資料/` に、現行運用整理・軽量運営モデル・Global_BOX反映設計の 3 本を新規追加した。
  - 次段階の Global_BOX 共通化で、どの原則を残し、どの部分を案件固有に残すかを切り分けやすい状態へ整理した。
- 2026-03-13 16:48 JST
  - `Global_BOX` の `README.md`、`AGENTS_TEMPLATE.md`、`記録ファイル運用ルールテンプレート.md`、`progressテンプレート.md`、`NEXT_TASKテンプレート.md`、`案件初期化スクリプト.sh` を軽量運営向けに更新した。
  - 初期化スクリプトを一時ディレクトリで実行し、`進行状況/` の `progress.md` / `NEXT_TASK.md` シンボリックリンクが維持されることと、`progress_weekly/` が新規作成されることを確認した。
