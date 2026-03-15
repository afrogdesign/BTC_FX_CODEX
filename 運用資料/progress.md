# Progress Log

更新日: 2026-03-15 14:30 JST

このファイルは、現在の軽い進行ログ入口です。
重い履歴は `progress_weekly/` へ週ごとに退避します。

## 現在の運用

- ここには、新しい事実や実作業があったときだけ追記する。
- 報告系ファイルを更新したこと自体は、原則としてここへ書かない。
- 書く対象は、システム動作、運用手順、スクリプト、設定、検証結果など、監視システム本体に関わる変化を優先する。

## 週次アーカイブ

- 2026-W11: [progress_weekly/2026-W11.md](progress_weekly/2026-W11.md)

## 最新の実作業

- 2026-03-15 14:30 JST
  - 本命通知とは別に、ロング・ショート両対応の `注意報メール` を実装した。
  - 注意報は `notification_kind=attention` として本命通知と分離し、専用履歴 `logs/last_attention_notified.json` でクールダウン管理する形にした。
  - 件名はロング `🟡 [注意報] ...`、ショート `🔵 [注意報] ...` で、本文冒頭にも「売買推奨ではなく注意報」と明記するようにした。
  - 閾値は `ATTENTION_ALERT_SCORE_MIN=55`、`ATTENTION_ALERT_GAP_MIN=15`、`ATTENTION_ALERT_COOLDOWN_MINUTES=60` を追加した。
  - `python3 -m unittest tests.test_notification_trigger tests.test_summary_format tests.test_funding_and_signal tests.test_phase1_activation` を実行し、11件成功を確認した。
  - 実装はコミット `54376e4` `注意報メールを追加してロング・ショート初動を通知可能にする` として確定した。
- 2026-03-13 22:39 JST
  - 朝 `08:05` と `09:05` の `Ver02.1` 判定を追跡し、上昇初動を取り逃がした主因が `CONFIDENCE_LONG_MIN`、`MIN_RR_RATIO`、`sweep_incomplete` 加点の厳しさにあることを確認した。
  - 実効設定を `CONFIDENCE_LONG_MIN=40`、`MIN_RR_RATIO=1.15`、`sweep_incomplete=+4` へ調整し、`.env` / `.env.example` / 関連テストまで反映した。
  - 今後すぐ見直せるように `運用資料/運用/採点調整シート.md` を追加し、閾値・影響先・確認場所・`.env` 優先の注意点を 1 枚に整理した。
  - `python3 -m unittest tests.test_notification_trigger tests.test_funding_and_signal tests.test_phase1_activation` を実行し、7件成功を確認した。
- 2026-03-13 17:29 JST
  - `AGENTS.md` と `Global_BOX` の報告義務文を削除し、sandbox / 隔離環境の扱いを「軽い方法優先」の文へ整理した。
  - `BTC_FX_Claude`、`レシート処理`、`インキャビラジオ`、sandbox 側にも同じ軽量化を反映した。
- 2026-03-13 17:18 JST
  - `AGENTS.md` と `Global_BOX` 側テンプレートから、通常運転で参照しない `共通 AGENTS テンプレート` の一文を削除した。
  - 他案件の `AGENTS.md` からも同じ一文を外し、通常入口を少し軽くした。
- 2026-03-13 17:05 JST
  - `運用資料/運用/記録ファイル運用ルール.md` を、秘書メモの軽量運営に合わせて再調整した。
  - `👩‍⚖️秘書.md` を、人向け入口として短く読みやすい形へ整理し直した。
  - 再発防止用に、秘書メモ更新時のチェック項目をルールへ追加した。
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
