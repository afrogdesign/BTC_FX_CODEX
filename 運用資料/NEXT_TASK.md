# NEXT TASK TRACKER

## 現在の状況
- 開発環境ローカルの件名ラベルは `Ver02.1` へ切り替え済みで、単発確認でも `[Ver02.1] [BTC監視] ...` を確認した。
- 現行本番相当の凍結退避点として `codex/ver02.0-freeze` を `7b89190` から作成し、remote へ push 済み。
- 開発環境ローカル常駐 `com.afrog.btc-monitor` を起動し、`state = running`、`pid = 32695` を確認した。
- 最新の `logs/last_result.json` では `system_label=Ver02`、`signal_id=20260312_081920`、`ai_decision=WAIT_FOR_SWEEP`、`was_notified=False`、`data_quality_flag=ok` まで確認済み。
- `.env` のローカル設定では、AI助言・要約の両方を CLI ラッパーへ向け、`run_cycle()` 1 回実行で `ai_decision` と `summary_body` が埋まることを確認した。
- 初回は `AI_TIMEOUT_SEC=10` / `AI_SUMMARY_TIMEOUT_SEC=20` でタイムアウトしたが、CLI 用に 45 秒 / 60 秒へ広げた後は通過した。
- `codex/ai-cli-wrapper-validation` で `tools/codex_cli_wrapper.py` を追加し、`summary` と `ai_advice` の両方を `codex exec` 経由で返す最小ラッパーを作成した。
- `tests/test_codex_cli_wrapper.py` を追加し、`.venv312/bin/python -m unittest tests.test_codex_cli_wrapper tests.test_summary_format` で通過確認済み。
- 単発スモークでは、要約側で本文テキスト、助言側で JSON オブジェクトが返ることを確認した。CLI 実行形式はラッパー 1 本を両方へ指定する形で固まった。
- `ver02` はコミット `7b89190` まで `origin/ver02` へ push 済みで、検証用ブランチ `codex/ai-cli-wrapper-validation` を切った。
- AI助言と要約生成を、それぞれ `.env` の `AI_ADVICE_PROVIDER` / `AI_SUMMARY_PROVIDER` で `api` と `cli` に切り替えられるよう実装した。CLI 使用時は `AI_ADVICE_CLI_COMMAND` / `AI_SUMMARY_CLI_COMMAND` を実行する。
- Obsidian 側の `仕様書/Ver02判定ロジック早見表.md` を追加し、Ver02 の判定条件、通知条件、強ランク条件、実ログの読み方を1ページで確認できるようにした。
- 運営ルールの正本は `AGENTS.md` とし、文書の役割分担と入口順はそこに従う。秘書メモは軽い入口、大きな報告は打ち合わせノート、全体計画はロードマップと `運用資料/計画/` に置く。
- `運用資料/スレッド引き継ぎファイル.md` には、次スレッドでも `AGENTS.md` を確認してから再開する旨を追記済み。
- `スレッド引き継ぎファイル.md` は 2026-03-12 11:39 JST 時点の運用設計整理と Git 反映状況まで更新済み。
- `運用資料/` 直下は日常で使う資料だけに整理し、運用手順は `運用/`、参考資料とログ分析レポートは `参考資料/` に移した。
- 読む優先度は `👩‍⚖️秘書.md` → `運用資料/開発ロードマップ.md` → `NEXT_TASK.md`。ここで不足する場合だけ `運用資料/スレッド引き継ぎファイル.md` を開く。`progress.md` は履歴確認が必要なときだけ参照する。
- `運用資料/開発ロードマップ.md` と `運用資料/計画/` 配下を新設し、全体計画はそこで管理する運用へ切り替えた。
- 常駐の正本は MBP2020。本番では Ver01 を比較基準、Ver02 を改善検証対象として並走運用する。
- MBA15 は開発・単発確認専用で、ローカル常駐 `com.afrog.btc-monitor` は停止済み。
- 現状の最新ログと運用判断の正本は MBP2020 本番環境にある。MBA15 側の `btc_monitor` ログは構造確認や単発確認には使えるが、現況判断の正本には使わない。
- Ver02 本番は `/Users/marupro/CODEX/BTC_FX_CODEX_ver02/btc_monitor` / `com.afrog.btc-monitor-ver02`、Ver01 本番は `/Users/marupro/CODEX/BTC_FX_CODEX_ver01/btc_monitor` / `com.afrog.btc-monitor-ver01` で稼働中。
- 2026-03-12 10:44 JST に MBP2020 実機へ SSH 接続して再確認し、Ver01 / Ver02 とも `state = running`、Ver01 `pid=91182`、Ver02 `pid=98787` を確認した。`heartbeat.txt` は両系統とも `2026-03-12 10:05:00 JST`、`last_result.json` は Ver01 `10:05:15 JST`、Ver02 `10:05:24 JST` 更新で、定時サイクル更新確認は完了した。
- 現在の版位置づけは `Ver02.x` で、`Phase 0` 実運用確認中。次の大型節目は `Ver03`。
- `Ver03` は、`Phase 0` の通知後フロー一周完了と `Phase 1` 中核導入を両方満たしたときに昇格する。
- 過去の Ver02 ログ `logs/csv/`、`logs/signals/`、`logs/cache/` は本番 Ver02 側へ移行済み。
- `signal_outcomes.csv` と `user_reviews.csv` はまだ未生成で、通知後 24 時間の本番確認待ち。
- 直近の本番最新データでは、Ver01 は `bias=wait`・`confidence=30`・`signal_id=None`、Ver02 は `signal_id=20260312_010500`・`was_notified=False`・`bias=long`・`confidence=0` で、通知済みシグナルはまだ確認できていない。
- `Phase 1` の設計入口として、`src/trade/position_sizing.py` と `src/trade/exit_manager.py` を追加し、`main.py` からサイズ計画 / 出口計画の雛形ログを出せる土台を入れた。
- `config.py` には `PHASE1_*` 設定値の入口を追加し、`trades.csv` へ `risk_percent_applied`、`planned_risk_usd`、`position_size_usd`、`tp1_price`、`exit_rule_version` などの保存列を追加した。
- Phase 1 のテスト入口として `tests/test_phase1_trade_plans.py` を追加し、サイズ上限制御と TP 計算の最小確認は通過済み。
- `loss_streak` は `signal_outcomes.csv` と `trades.csv` の完了済み通知履歴から自動計算するように変更し、履歴がまだ無い場合だけ `PHASE1_LOSS_STREAK` を予備値として使う構成にした。
- `tools/log_feedback.py` は Phase 1 計画列を `shadow_log.csv` と週次/月次レポートへ流すよう更新済みで、現時点では件数 0 の空集計まで確認済み。
- ただし、この空集計確認はローカル構造確認であり、Phase 1 の実データ評価は MBP2020 本番ログで行う前提に戻す。
- `phase1_active` と `phase1_activation_reason` はコードに追加済みで、今後は `ready` 行だけを正式集計対象にしやすい状態になった。
- 本番反映方法は、手動 tar 配備より「Git 管理下ファイルを rsync で反映」「本番ログは別 pull」で回す方針に整理し、`tools/deploy_ver02_prod.sh` と `tools/pull_ver02_prod_logs.sh` を追加した。

## 次のタスク
- 1. 開発環境の `DRYRUN_MODE` を false にするか判断し、必要なら Ver02 / Ver02.1 の比較通知を実際に取る準備をする。
- 2. 開発環境の常駐をしばらく維持し、次の更新サイクルでも `heartbeat.txt` と `last_result.json` が進むか確認する。
- 3. 問題がなければ本番 Ver02 へコード反映し、MBP2020 側 `.env` にも同じ CLI 設定を入れる手順を整理する。
- 4. 今後の本番反映は `zsh tools/deploy_ver02_prod.sh`、本番ログ確認は `zsh tools/pull_ver02_prod_logs.sh` を入口にする。
- 5. 次の通知発生サイクルを確認し、Ver02 の `trades.csv` と `logs/signals/*.json` に `was_notified=True` と `notify_reason_codes` が実データで入るか確認する。
- 6. 通知が 1 件でも発生したら、Ver01 / Ver02 の通知メール件名・本文・`notify_reason_codes`・runtime ログが混線していないか確認する。
- 7. 最初の通知から 24 時間経過後に、本番 Ver02 環境で `./.venv312_prod/bin/python tools/log_feedback.py daily-sync` を実行し、`signal_outcomes.csv`、`shadow_log.csv`、`📝通知レビュー.md` の初回本番更新を確認する。
- 8. `📝通知レビュー.md` に 1 件以上 `actual_move_driver` を入れて `review_status=done` にし、`daily-sync` または `import-reviews` 後に `logic_validated` が `user_reviews.csv` / `shadow_log.csv` へ正しく反映されるか確認する。
- 6. Phase 1 の有効条件は「`primary_setup_status=ready` を本有効、`watch` は参考ログのみ」として次の実装へ落とし込む。
- 7. `loss_streak` の自動計算結果を将来 `user_reviews.csv` や別状態ファイルへ固定保存する必要があるかを判断する。
- 8. Phase 1 の正式指標は、本有効件数 (`n`) / TP1 到達率 / `tp1_hit_first=false` 率 / `expired` 率 / 平均 `risk_percent_applied` / 連敗時平均 `risk_percent_applied` / `max_size_capped` 発生率を優先監視する。
- 9. `phase1_active=true` の行だけで MBP2020 本番ログを集計し、正式指標の最初の母数 (`n`) を確認する。
- 10. `expired` と `tp1_hit_first=false` は現状 proxy 指標なので、将来の timeout / stop 実測ログ化が必要かを判断する。
- 11. `Ver03` 昇格条件に照らして、`Phase 0` と `Phase 1` のどちらが未充足かを `運用資料/計画/フェーズ別計画_Phase0-1.md` で定期確認する。

## ブロッカー
- Codex CLI は `run_cycle()` 1 回では通ったが、長時間運転したときの認証持続やエラー回復はまだ未確認。
- CLI 切り替え直後の初回実行ではタイムアウトが発生したため、現在は長めタイムアウト前提で運用している。
- 開発環境は `DRYRUN_MODE=true` で回しているため、通知送信やメール文面の最終確認には使っていない。
- そのため、Ver02 / Ver02.1 の実メール比較はまだ未実施。
- 現在は通知済みシグナルが 0 件のため、`daily-sync` 初回本番確認と `logic_validated` 実データ確認は待ち状態。
- 通知が止まっている直接原因は、現時点の実データでは Ver01 `bias=wait`、Ver02 `was_notified=False` / `confidence=0` で、しきい値未達の可能性が高い。
- `signal_outcomes.csv` と `user_reviews.csv` はまだ存在せず、`daily-sync` 初回本番確認には通知発生待ちが必要。
- Ver01 / Ver02 の runtime ログはまだ 0 byte のため、実運用中にログが必要十分に残るかは引き続き観察が必要。
- 強条件（🟡 / 🔥）は市場条件が厳しめに設定されているため、発火確認までに数サイクル必要。
- `signal_outcomes.csv` / `shadow_log.csv` の本格評価は、通知から24時間経過した実データがたまるまで待ちが必要。
- `Phase 1` の中核実装はまだ未着手で、`Ver03` 昇格には通知後フロー確認だけでなく損益管理モジュール導入も必要。
- `loss_streak` は自動反映に切り替わったが、履歴 0 件の間は `PHASE1_LOSS_STREAK` 予備値へフォールバックする。
- `Phase 1` の追加ログ列は `shadow_log.csv` と週次レポートまで接続済みだが、件数 0 のため実データ評価はまだできない。
- `phase1_active` は実装済みだが、MBP2020 本番ログ側でまだこの列を蓄積できていない。
- `expired` と `tp1_hit_first=false` は、現状では timeout / stop の proxy であり、厳密な実測指標ではない。

## 完了条件
- Ver01 を比較基準として維持しつつ、Ver02 の `Phase 0` 通知後フローが本番で一周完了し、あわせて `Phase 1` の有効条件と正式指標が文書と実装候補の両方で整理されていること。
