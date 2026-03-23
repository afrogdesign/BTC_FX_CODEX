# Progress Log

更新日: 2026-03-23 18:40 JST

このファイルは、現在の軽い進行ログ入口です。
重い履歴は `progress_weekly/` へ週ごとに退避します。

## 現在の運用

- ここには、新しい事実や実作業があったときだけ追記する。
- 報告系ファイルを更新したこと自体は、原則としてここへ書かない。
- 書く対象は、システム動作、運用手順、スクリプト、設定、検証結果など、監視システム本体に関わる変化を優先する。

## 週次アーカイブ

- 2026-W11: [progress_weekly/2026-W11.md](progress_weekly/2026-W11.md)

## 最新の実作業

- 2026-03-23 18:35 JST
  - `iMac 2019` を本番軽量同期とログ取得の常設先、`MBA M4` を持ち運び前提の作業機に再整理した。
  - `README.md`、`NEXT_TASK.md`、`開発ロードマップ.md`、`スレッド引き継ぎファイル.md`、運用ルール類を iMac 常設前提へ更新した。
  - `com.afrog.btc-monitor-status-sync` を iMac 側へ登録し、`tmp/status/prod_status_sync_last_success.txt` が `2026-03-23 17:58 JST` へ更新されることを確認した。
  - `MBA M4` 側では `com.afrog.btc-monitor-status-sync` を停止し、`~/Library/LaunchAgents/com.afrog.btc-monitor-status-sync.plist.disabled_20260323_1840` へ退避して常設を外した。
- 2026-03-23 18:20 JST
  - 今日以降 `iMac 2019` と `MBA M4` の両方で BTC を触る前提に合わせ、入口と運用ルールを再調整した。
  - `運用資料/README.md`、`NEXT_TASK.md`、`今後の運用ルール.md`、`記録ファイル運用ルール.md` に、切替前の commit / push、開始前の `git pull --rebase`、記録ファイルの単独更新原則を追記した。
  - 役割分担は `iMac 2019` を主な実装・テスト、`MBA M4` を軽量同期確認・ログ確認・軽い文書修正の優先機として整理した。
- 2026-03-23 18:00 JST
  - `運用資料/運用/` 配下を棚卸しし、入口・ルール・実務・調整の各文書を軽量版へ整理した。
  - `運用/README.md` は「まず何を見るか」だけの入口に縮め、`今後の運用ルール.md` と `記録ファイル運用ルール.md` は長い補足を削って短い正本へ作り直した。
  - `運用コマンドメモ.md`、`ログ検証と改善運用ガイド.md`、`採点調整シート.md` も、日常で本当に使う内容だけを残し、重い説明や将来拡張の記述を外した。
- 2026-03-23 17:30 JST
  - `Global_BOX` の現行正本が iCloud 側 `/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_💻️デジタルスキル/00_🗃️PROJECT/00_Global_BOX` に移っていることを確認し、BTC 側の入口文書と運用スクリプトの参照先を新構成へ更新した。
  - 実機確認として、iMac 2019 は BTC 常駐なし・`com.afrog.chatgptmdwatcher.plist` のみ、MBA M4 は `com.afrog.btc-monitor-status-sync` 常設・`com.afrog.btc-monitor` は未ロード、MBP2020 は `com.afrog.btc-monitor-ver021` 稼働中・`receiptbox` と `tweet-sync` も登録済みであることを取り直した。
  - `Global_BOX/20_環境情報/実行ファイル/本番環境.md`、`Global_BOX/20_環境情報/実行ファイル/開発環境/MBA M4.md`、`Global_BOX/20_環境情報/実行ファイル/開発環境/iMac 2019.md` を実機状態へ更新し、BTC 側は Mac 横断一覧の複製をやめて案件固有メモだけを残す形へ整理した。
- 2026-03-19 16:20 JST
  - ユーザー報告の「API と CLI の 2 通が同時に届く」現象を調査したところ、本番 `Ver02.1 API` に加えて、ローカル開発の `com.afrog.btc-monitor` が実際には `state = running` で残っていたことを確認した。
  - ローカル `launchctl print gui/$(id -u)/com.afrog.btc-monitor` では、`/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/.venv312/bin/python -u main.py` が `pid = 790` で常駐していた。
  - `launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.afrog.btc-monitor.plist` を実行し、停止後は `Could not find service "com.afrog.btc-monitor"` を確認した。重複メールの主因は「本番 API + ローカル CLI の同時送信」が濃厚。
- 2026-03-19 02:33 JST
  - ユーザー依頼により、本番 `Ver02.1` の AI 実行方式を `CLI` から `API` へ戻した。本番 MBP2020 の `.env` で `AI_ADVICE_PROVIDER=api`、`AI_SUMMARY_PROVIDER=api` へ変更し、`com.afrog.btc-monitor-ver021` を再起動した。
  - 再起動後は `launch_agent_started:com.afrog.btc-monitor-ver021` を確認し、`launchctl print` で `state = running`、`pid = 39245` を確認した。`logs/runtime/monitor.pid` も更新済み。
  - `.venv312_prod/bin/python` から `config.load_config()` を読み、実行時設定が `AI_ADVICE_PROVIDER=api`、`AI_SUMMARY_PROVIDER=api` になっていることを確認した。
- 2026-03-18 01:45 JST
  - 評価導線の命名を安定化するため、repo 側では `通知評価シート.md`、`評価シート入力フォーム.html`、`評価シート書き方.md` に表記を統一した。`tools/log_feedback.py` の既定出力先、フォーム名、テスト見出し、関連ドキュメント参照も追従更新した。
  - Obsidian 側でも評価シート関連の実ファイル名を同じ表記へ変更し、案件フォルダのパスは `10_💻️デジタルスキル/00_🗃️PROJECT/📁FX/トレード支援システム` のようにスペースなしへ整理した。
  - 変更後、repo 内の旧パス / 旧ファイル名参照が残っていないことを検索で確認し、`.venv312/bin/python -m unittest tests.test_log_feedback` で 5 件成功を確認した。
- 2026-03-18 01:21 JST
  - `運用資料/参考資料/BTC判定システム改善案_0317/` の内容を、現行の `NEXT_TASK.md`、`開発ロードマップ.md`、`計画/マイルストーン定義.md`、`計画/フェーズ別計画_Phase0-1.md` と照合し、全面実装ではなく段階採用と判断した。
  - 正式な受け皿として `運用資料/計画/評価システム改善仕様書_Ver02x-Ver05接続.md` を新設し、採用目的、非目的、`evaluation_trace` の初期対象、実装順、テスト方針を固定した。
  - あわせて `開発ロードマップ.md` と `NEXT_TASK.md` を更新し、直近は `Phase 0` 一周、重複メール再発確認、通知本文の安定化を優先し、その次段で「最終判定を変えない内部観測強化」に進む方針を明文化した。
- 2026-03-18 01:03 JST
  - Obsidian 側レビュー運用を簡単にするため、`通知評価シート.md` と同じフォルダに選択式の `評価シート入力フォーム.html` を追加した。各通知ごとにプルダウンで `user_verdict`、`would_trade`、`actual_move_driver`、`review_status` などを選べる。
  - あわせて `評価シート書き方.md` を新規作成し、各列の意味、選択肢の意味、最低限埋めればよい項目、記入例を日本語で整理した。
  - `tools/log_feedback.py` を更新し、今後は `daily-sync` や `export-review-queue` 実行時に `評価シート入力フォーム.html` も自動生成されるようにした。本番へ反映後、実際に Obsidian フォルダへフォーム生成できることを確認した。
  - 関連パスの更新として、プロジェクト内と `Global_BOX` 内の Obsidian 保存先表記を新しいベースパスへそろえた。
- 2026-03-18 00:34 JST
  - `daily-sync` の実行条件を確認し、最初の通知 `2026-03-16 07:05 JST` から 24 時間以上経過していることを確認したうえで、本番 `Ver02.1 CLI` で `./.venv312_prod/bin/python tools/log_feedback.py daily-sync` を実行した。
  - 実行は成功し、`logs/csv/signal_outcomes.csv`、`logs/csv/user_reviews.csv`、`運用資料/reports/feedback_daily_sync_20260318.md` の生成を確認した。`shadow_log.csv` も更新され、日次集計レポートには総観測件数 3、近似PF 5.58、通知品質 A=3 が出力された。
  - `signal_outcomes.csv` の先頭確認では、`2026-03-17 23:05 JST` の `signal_id=20260317_140500` も評価対象へ入っていることを確認した。`user_reviews.csv` はヘッダーのみで、手動レビュー入力待ち。
  - 次の実務は `通知評価シート.md` で `review_status=done` を 1 件以上作り、`logic_validated` の評価開始へ進める段階になった。
- 2026-03-18 00:01 JST
  - 03/17 23:05 JST の重複メールを調査した。件名は同一だが本文が大きく異なる 2 通が届いており、受信メール実物の比較では AI 作文が別々に走った形に近いことを確認した。
  - 本番 `trades.csv` と `last_result.json` を直接確認したところ、`signal_id=20260317_140500` の保存記録は 1 件で、保存済み `summary_body` は受信した 2 通のうち 1 通分と一致した。23:05 台の `smtp_error`、`ai_summary_error`、`pending_email.json` は見つからなかった。
  - 本番 Mac の `launchd` と実プロセスを再確認し、再起動前に `main.py` 系の残りプロセスが見えていたため、重複の主因は二重起動の再発が濃厚と判断した。
  - 本番 `com.afrog.btc-monitor-ver021` を `bootout` → 残存 `main.py` 整理 → `bootstrap` / `kickstart` で再起動し、最終的に `main.py` 実プロセス 1 本、`pid = 29988` を確認した。`logs/runtime/monitor.pid` も `29988` へ更新して整合を取った。
  - 未解決事項: 23:05 台の 2 通目がどの経路でログ保存をすり抜けたかは未特定。再発防止として、送信前に `signal_id` 単位で重複送信を止めるガード追加を今後の候補として残す。
- 2026-03-17 05:17 JST
  - 通知メールの可読性改善を完了し、本文は待機回でも再検討帯 / 損切り / TP1 / TP2 を残す形へ変更した。内部ラベルは本文で日本語に言い換えるよう整理した。
  - 件名は `[BTC監視]` を廃止し、日本語の判断文 → `【BTC:価格】` → `信頼度xx` → 日時 → `[Ver02.1] [CLI]` の順へ変更した。AI 失敗時は先頭に `⚠️ 機械判定のみ` を出す形へそろえた。
  - `python3 -m unittest tests.test_summary_format tests.test_ai_cli_retry` を実行し、8件成功を確認した。
  - コミット `e7105e9` `通知メールの件名と本文を読みやすく改善` を作成し、`zsh tools/deploy_ver021_prod.sh` で本番へ反映した。再起動後の本番 `com.afrog.btc-monitor-ver021` は `state = running`、`pid = 24498` を確認した。
- 2026-03-17 04:51 JST
  - 03/17 04時台の重複メールを調査し、本番 `Ver02.1 CLI` で `main.py` が二重起動していたことを確認した。同じ `signal_id` が本番 `trades.csv` に重複記録されており、04:05台の同内容メール2通はこの二重起動が主因と判断した。
  - 本番側の余分な `main.py` プロセスを停止し、`com.afrog.btc-monitor-ver021` の1本だけが残る状態を確認した。
  - 切り分けのため、開発環境の常駐 `com.afrog.btc-monitor` を停止した。以後は本番1本だけで通知と AI エラーの有無を観測する。
  - 開発環境の 04:05 相当ログでは `ai_advice` と `summary_body` の両方が生成済みで、開発側の本文生成は成功していることを確認した。今回の本文崩れ疑いは本番側優先で追う。
- 2026-03-17 01:52 JST
  - 報告系入口を現状に合わせて見直し、`NEXT_TASK.md` と `スレッド引き継ぎファイル.md` を「しばらくは本番観測中心で、急ぎの追加実装は入れない」前提へ更新した。
  - 自然文章化は参考設計として保持し、本文改善が必要になったときだけ `運用資料/参考資料/自然文章化設計書.md` を参照する整理にした。
- 2026-03-17 01:46 JST
  - `運用資料/参考資料/natural_report_package` の内容を精査し、そのまま実装投入せず、自然文章化の発想源として扱う方針を整理した。
  - `運用資料/参考資料/自然文章化設計書.md` を新設し、通知本文改善の目的、非目的、`意味優先 + 数字保持` の方針、保持すべき情報、比較対象ケースを参考設計としてまとめた。
  - `運用資料/運用/ルール/記録ファイル運用ルール.md` に、通知本文の設計思想を見直したときはこの設計書も更新対象に含めるルールを追記した。
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
