# Progress Log

更新日: 2026-03-16 21:45 JST

このファイルは、現在の軽い進行ログ入口です。
重い履歴は `progress_weekly/` へ週ごとに退避します。

## 現在の運用

- ここには、新しい事実や実作業があったときだけ追記する。
- 報告系ファイルを更新したこと自体は、原則としてここへ書かない。
- 書く対象は、システム動作、運用手順、スクリプト、設定、検証結果など、監視システム本体に関わる変化を優先する。

## 週次アーカイブ

- 2026-W11: [progress_weekly/2026-W11.md](progress_weekly/2026-W11.md)

## 最新の実作業

- 2026-03-16 21:45 JST
  - `運用資料/運用/` 直下の混在を整理し、`ルール/`、`環境/`、`実務/`、`調整/` の4分類へ再編した。
  - 入口として `運用資料/運用/README.md` を追加し、各資料の置き場所を明示した。
  - `NEXT_TASK.md`、`progress.md`、`スレッド引き継ぎファイル.md`、`AI向けシステムロジック全体整理.md`、`AGENTS.md` の参照パスを新構成へ更新した。
- 2026-03-16 21:25 JST
  - `運用資料/参考資料/AI向けシステムロジック全体整理.md` を全面更新し、現行 `Ver02.1 CLI` 前提、現在の主要判定パラメーター、通知条件、`Phase 1` 条件を最新化した。
  - `運用資料/運用/ルール/記録ファイル運用ルール.md` に、判定しきい値や通知条件、`prelabel` 条件、`Phase 1` 条件、AI 実行方式を変えたときはこの資料も更新する、というルールを追記した。
- 2026-03-16 21:05 JST
  - 本番ログの軽量同期ジョブ `com.afrog.btc-monitor-status-sync` は、今後も常設で使う前提に整理した。
  - 開発環境の実行一覧を `運用資料/運用/環境/開発環境_実行ファイル一覧.md` と `/Users/marupro/CODEX/Global_BOX/10_共通仕様/開発環境_実行ファイル一覧.md` に新設し、同期ジョブも一覧対象に含めた。
  - `運用資料/運用/ルール/記録ファイル運用ルール.md` と `Global_BOX/30_テンプレート/記録ファイル運用ルールテンプレート.md` に、開発環境一覧と軽量同期ジョブの更新ルールを追記した。
- 2026-03-16 20:43 JST
  - `ver02.1-stable` を `main` へ fast-forward マージし、`main` / `ver02.1-stable` / `ver02.1-v2` の役割を整理した。`ver02.1-stable` は固定、`ver02.1-v2` は比較レポートだけを追加した開発ラインとして push 済み。
  - 本番 MBP2020 に `codex` 単体バイナリを `/Users/marupro/bin/codex` として導入し、通常ブラウザ認証で `codex login` を完了した。`codex login status` は `Logged in using ChatGPT` を確認した。
  - 本番 `Ver02.1 API` 常駐 `com.afrog.btc-monitor-ver021` を安全停止したあと、旧 API 実体は `/Users/marupro/CODEX/BTC_FX_CODEX_ver02_API_backup_20260316_2030` へ退避し、新しい `Ver02.1` 一式を `/Users/marupro/CODEX/BTC_FX_CODEX_ver02` として配置し直した。
  - コピー由来の不要物として `tmp/`、`logs/runtime/` 残骸、`__pycache__`、`.DS_Store` を本番側から削除し、`.env` は CLI 本番向けパスと `CODEX_BIN=/Users/marupro/bin/codex` に調整した。
  - 当初の `EX_CONFIG` は `.venv312_prod` 不在が原因だったため、`.venv312_prod -> .venv312` のリンクを作成して解消した。再起動後は `launch_agent_started:com.afrog.btc-monitor-ver021`、`state = running`、`pid = 19756` を確認し、`logs/last_result.json` は `system_mode_label=CLI` を返した。
- 2026-03-16 19:14 JST
  - 本番 `Ver01` の比較役目完了を受けて、`mbp2020-btc` へ SSH し `com.afrog.btc-monitor-ver01` を `launchctl bootout` で安全停止した。
  - 停止前は `launchctl print` で `state = running` と `pid = 91182` を確認し、停止後は `service not found` と実プロセス消滅を確認した。
  - 同時に本番軽量同期を最新化し、`Ver02.1 API` が `2026-03-16 17:05 JST` 時点で `ok / WAIT_FOR_SWEEP / NO_TRADE_CANDIDATE / long / Confidence 73` を返していることを確認した。
  - 今日の `CLI Ver02.1` 反応履歴を確認し、注意報 `16:27 JST` → 本命通知 `18:05 JST` の流れを確認したうえで、以後の主対象を `Ver02.1` 単独運用へ切り替えた。
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
  - 今後すぐ見直せるように `運用資料/運用/調整/採点調整シート.md` を追加し、閾値・影響先・確認場所・`.env` 優先の注意点を 1 枚に整理した。
  - `python3 -m unittest tests.test_notification_trigger tests.test_funding_and_signal tests.test_phase1_activation` を実行し、7件成功を確認した。
- 2026-03-13 17:29 JST
  - `AGENTS.md` と `Global_BOX` の報告義務文を削除し、sandbox / 隔離環境の扱いを「軽い方法優先」の文へ整理した。
  - `BTC_FX_Claude`、`レシート処理`、`インキャビラジオ`、sandbox 側にも同じ軽量化を反映した。
- 2026-03-13 17:18 JST
  - `AGENTS.md` と `Global_BOX` 側テンプレートから、通常運転で参照しない `共通 AGENTS テンプレート` の一文を削除した。
  - 他案件の `AGENTS.md` からも同じ一文を外し、通常入口を少し軽くした。
- 2026-03-13 17:05 JST
  - `運用資料/運用/ルール/記録ファイル運用ルール.md` を、秘書メモの軽量運営に合わせて再調整した。
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
