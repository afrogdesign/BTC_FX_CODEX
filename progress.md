# Progress Log

- 日付: 2026-03-10
- 実施内容: `/Users/marupro/CODEX/Global_BOX/PROJECT開始指南書.md` を新規作成し、新規プロジェクト開始時に使う定型プロンプト集をまとめた。設計のみ、初期構築、API利用、既存案件引き継ぎなどのケース別テンプレートを整理した。
- 変更ファイル: `/Users/marupro/CODEX/Global_BOX/PROJECT開始指南書.md`, `progress.md`, `NEXT_TASK.md`
- 未解決事項: BTC監視の次回定時実行結果の確認は継続。`PROJECT開始指南書.md` の内容を今後の実運用で微調整する可能性あり。
- メモ: `Global_BOX` を起点にすること、公開可否、API事前許可、仮想環境利用を毎回プロンプトへ入れやすい形にした。

- 日付: 2026-03-09
- 実施内容: `/Users/marupro/CODEX/BTC_FX_CODEX/開発環境` を `/Users/marupro/CODEX/Global_BOX` へ移動し、全プロジェクト共通の非公開参照ボックスへ整理した。`Global_BOX/README.md`、`Global_BOX/AGENTS_TEMPLATE.md` を追加し、開発環境仕様書も共通参照前提へ更新した。さらに Obsidian 側の `📄 AGENTS_TEMPLATE.md` を同内容へ整理し、`BTC_FX_CODEX`、`BTC_FX_Claude`、`レシート処理` の `AGENTS.md` 先頭に `Global_BOX` 参照を追加した。
- 変更ファイル: `/Users/marupro/CODEX/Global_BOX/README.md`, `/Users/marupro/CODEX/Global_BOX/開発環境仕様書.md`, `/Users/marupro/CODEX/Global_BOX/AGENTS_TEMPLATE.md`, `/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_デジタルスキル/AI/エージェントAI関連/📄 AGENTS_TEMPLATE.md`, `/Users/marupro/CODEX/BTC_FX_CODEX/AGENTS.md`, `/Users/marupro/CODEX/BTC_FX_Claude/AGENTS.md`, `/Users/marupro/CODEX/レシート処理/AGENTS.md`, `progress.md`, `NEXT_TASK.md`
- 未解決事項: BTC監視の次回定時実行確認は継続。今後新規プロジェクトを作るときも `Global_BOX/AGENTS_TEMPLATE.md` ベースで `AGENTS.md` を作る運用を守る必要がある。
- メモ: `Global_BOX` は公開禁止の共通箱として定義し、個人情報や秘密情報は原則「実値ではなく保存場所とルール」を書く方針に統一した。

- 日付: 2026-03-09
- 実施内容: 他プロジェクトでも再利用しやすいように、非公開前提の開発環境仕様書を `/Users/marupro/CODEX/BTC_FX_CODEX/開発環境/開発環境仕様書.md` に新規作成した。OS、GitHub、Python 3.12 並行インストール、`.venv312`、`launchd` 本番常駐、秘密情報の扱い、Codex 運用ルールを整理した。
- 変更ファイル: `/Users/marupro/CODEX/BTC_FX_CODEX/開発環境/開発環境仕様書.md`, `progress.md`, `NEXT_TASK.md`
- 未解決事項: BTC監視の次回定時実行後に `heartbeat` / `last_result` / `errors` の更新確認が必要。新仕様書を他の引き継ぎ資料へ転記するかは未判断。
- メモ: 秘密情報の実値は仕様書に書かず、保存場所と運用ルールのみ記載した。公開禁止であることを文書冒頭に明記した。

- 日付: 2026-03-09
- 実施内容: Python 3.12.10 を既存 3.9 と並行インストールし、`.venv312` を新規作成して依存関係を再インストールした。`launchd` の実行先を `.venv312/bin/python` へ切り替え、`launchctl print gui/501/com.afrog.btc-monitor` で `state = running`、`program = /Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/.venv312/bin/python`、`pid = 38773` を確認した。
- 変更ファイル: `.gitignore`, `deploy/com.afrog.btc-monitor.plist`, `README.md`, `progress.md`, `NEXT_TASK.md`
- 未解決事項: 次回定時実行の 2026-03-10 01:05 JST 以降に `logs/heartbeat.txt` と `logs/last_result.json` の更新確認が必要。通知条件発火時の本番メール確認も継続。
- メモ: `.venv312/bin/python` では `OpenSSL 3.0.16` を確認済み。`logs/runtime/monitor.err` の LibreSSL 警告は 23:35 の旧ログで、Python 3.12 切り替え後には更新されていない。

- 日付: 2026-03-09
- 実施内容: macOS `launchd` 用の `deploy/com.afrog.btc-monitor.plist` を追加し、`~/Library/LaunchAgents/com.afrog.btc-monitor.plist` へ登録した。`launchctl print gui/501/com.afrog.btc-monitor` で `state = running` と `pid = 37687` を確認し、本番常駐へ切り替えた。あわせて `tools/start_monitor.sh` を `launchd` 再登録用に更新し、README に本番起動手順を追記した。
- 変更ファイル: `deploy/com.afrog.btc-monitor.plist`, `tools/start_monitor.sh`, `README.md`, `progress.md`
- 未解決事項: 次回定時実行は 2026-03-10 01:05 JST のため、その後に `logs/heartbeat.txt` と `logs/last_result.json` の更新確認が必要。通知条件発火時の本番メール確認も継続。
- メモ: `logs/runtime/monitor.err` に LibreSSL 由来の `urllib3` 警告が出るが、起動自体は継続している。旧 `monitor.pid` は先行確認時の一時ファイルで、常駐管理は `launchd` に移行済み。

- 日付: 2026-03-09
- 実施内容: 本番常駐向けの起動スクリプト `tools/start_monitor.sh` を追加し、既存プロセスの重複起動を防ぎつつ PID とログを残せるようにした。これから本番常駐起動と動作確認を行う。
- 変更ファイル: `tools/start_monitor.sh`, `progress.md`
- 未解決事項: 実際の常駐起動後に、`logs/runtime/monitor.pid` と `logs/heartbeat.txt` の更新確認が必要。通知条件発火時の本番メール確認も残っている。
- メモ: OpenAI API 利用については 2026-03-09 にユーザー許可あり。本番運用の実行確認後に `NEXT_TASK.md` を更新する。
