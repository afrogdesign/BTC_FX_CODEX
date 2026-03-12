# NEXT TASK TRACKER

## 現在の状況
- 2026-03-13 07:05 JST 時点で `/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/logs/heartbeat.txt` の更新は確認できた。一方で `signals` 最新は `20260312_210500.json`、`last_result.json` は 2026-03-13 06:06 JST 更新で、同時進行の継続確認は未完了。
- 同ログ配下の `logs/errors/` には 2026-03-12 20:05 台の `*_ai_advice_error.log` / `*_ai_summary_error.log` が残っており、自然観測の継続確認が必要。
- 本番は `Ver02.1 API`、開発は `Ver02.1 CLI` に役割を固定した。件名は `[Ver02.1] [API] [BTC監視] ...` / `[Ver02.1] [CLI] [BTC監視] ...` を基本形にする。
- 本番 launchd は `com.afrog.btc-monitor-ver021` へ移行済みで、旧 `com.afrog.btc-monitor-ver02` は停止確認済み。実体パスはログ保全のため従来の `/Users/marupro/CODEX/BTC_FX_CODEX_ver02/btc_monitor` を継続利用する。
- 本番ログは保持したまま反映しており、確認時点で `trades.csv` は 81 行、`shadow_log.csv` は 32 行のまま残っている。
- Git の作業正本ブランチは `codex/ver02.1` に切り替えた。
- `codex/ver02.1` は `origin/codex/ver02.1` へ push 済みで、今後の Ver02.1 系の作業正本として使える。
- sandbox `/Users/marupro/CODEX/BTC_FX_CODEX_sandbox/btc_monitor` で CLI 版を合計 6 サイクル連続確認し、`ai_decision` 欠落なし、`summary_body` 正常生成、`data_quality_flag=ok`、`data_missing_fields=[]`、`logs/errors/` 空を確認した。
- CLI 側は `codex` 実行パス自動解決に加えて、`src/ai/advice.py` / `src/ai/summary.py` で `retry_count` を使う再試行を実装済み。単発失敗 1 回で AI 欠落になりにくい状態へ補強した。
- 比較環境を汚さない確認用として `/Users/marupro/CODEX/BTC_FX_CODEX_sandbox/btc_monitor` を作成済みで、sandbox 側は `SYSTEM_LABEL=Ver02.1-sandbox` / `DRYRUN_MODE=true` に切り替えてある。
- CLI ラッパーは `codex` 実行パスを自動解決するよう修正済みで、薄い `PATH` を再現した単発確認でも要約テキストが返ることを確認した。
- `signal_tier` の値名ズレは `position_sizing.py` と `tests/test_phase1_trade_plans.py` で同期済みで、strong 系 tier は `strong_machine` / `strong_ai_confirmed` を正式値として扱うようそろえた。
- `運用資料/計画/` を今後の実装正本として再編し、`マイルストーン定義.md`・`フェーズ別計画_Phase0-1.md`・`フェーズ別計画_Phase2-3.md` だけで判断順、`Phase 1` の実装状態、`Phase 2` の実装順が読める状態に更新済み。
- `運用資料/参考資料/AI向けシステムロジック全体整理.md` を 2026-03-13 04:43 JST 時点の現行実装へ更新し、`api / cli` 切替、`Phase 1`、`shadow_log.csv`、`daily-sync`、`logic_validated` まで反映済み。
- Obsidian 側の `仕様書/Ver02判定ロジック早見表.md` を追加し、Ver02 の判定条件、通知条件、強ランク条件、実ログの読み方を1ページで確認できるようにした。
- 運営ルールの正本は `AGENTS.md` とし、文書の役割分担と入口順はそこに従う。秘書メモは軽い入口、大きな報告は打ち合わせノート、全体計画はロードマップと `運用資料/計画/` に置く。
- `運用資料/スレッド引き継ぎファイル.md` には、次スレッドでも `AGENTS.md` を確認してから再開する旨を追記済み。
- 現在の版位置づけは `Ver02.1` で、`Phase 0` 実運用確認中。次の大型節目は `Ver03`。
- `Ver03` は、`Phase 0` の通知後フロー一周完了と `Phase 1` 中核導入を両方満たしたときに昇格する。
- 過去の Ver02 系ログ `logs/csv/`、`logs/signals/`、`logs/cache/` は本番 Ver02.1 側へ移行済み。
- `signal_outcomes.csv` と `user_reviews.csv` はまだ未生成で、通知後 24 時間の本番確認待ち。
- `Phase 1` の設計入口として、`src/trade/position_sizing.py` と `src/trade/exit_manager.py` を追加し、`main.py` からサイズ計画 / 出口計画の雛形ログを出せる土台を入れた。
- `config.py` には `PHASE1_*` 設定値の入口を追加し、`trades.csv` へ `risk_percent_applied`、`planned_risk_usd`、`position_size_usd`、`tp1_price`、`exit_rule_version` などの保存列を追加した。
- Phase 1 のテスト入口として `tests/test_phase1_trade_plans.py` を追加し、サイズ上限制御と TP 計算の最小確認は通過済み。
- `loss_streak` は `signal_outcomes.csv` と `trades.csv` の完了済み通知履歴から自動計算するように変更し、履歴がまだ無い場合だけ `PHASE1_LOSS_STREAK` を予備値として使う構成にした。
- `tools/log_feedback.py` は Phase 1 計画列を `shadow_log.csv` と週次/月次レポートへ流すよう更新済みで、現時点では件数 0 の空集計まで確認済み。
- ただし、この空集計確認はローカル構造確認であり、Phase 1 の実データ評価は MBP2020 本番ログで行う前提に戻す。
- `phase1_active` と `phase1_activation_reason` はコードに追加済みで、今後は `ready` 行だけを正式集計対象にしやすい状態になった。
- 本番反映方法は、手動 tar 配備より「Git 管理下ファイルを rsync で反映」「本番ログは別 pull」で回す方針に整理し、`tools/deploy_ver021_prod.sh` と `tools/pull_ver021_prod_logs.sh` を入口にする。

## 次のタスク
- 1. 本番 Ver02.1 と開発 Ver02.1 の次回自然更新を観測し、両方で `heartbeat.txt` / `last_result.json` が進み続けるか確認する。
- 2. API 本番 / CLI 開発の比較通知が実際に来たら、件名・本文・AI助言・通知理由コードの差を確認する。
- 3. 本番は API、開発は CLI の役割分担のまま、差分観測のメモを `運用資料/reports/` と `📒打ち合わせノート.md` へ整理する。
- 4. 今後の本番反映は `zsh tools/deploy_ver021_prod.sh`、本番ログ確認は `zsh tools/pull_ver021_prod_logs.sh` を入口にする。
- 4.5. 将来の軽改修候補として、「通知しない回は要約本文 AI を呼ばず、通知時だけメール作文 AI を回す」構成にできるか検討する。これは Ver03 昇格条件とは別の効率改善メモとして扱う。
- 5. 次の通知発生サイクルを確認し、Ver02.1 の `trades.csv` と `logs/signals/*.json` に `was_notified=True` と `notify_reason_codes` が実データで入るか確認する。
- 6. 通知が 1 件でも発生したら、Ver01 / Ver02.1 の通知メール件名・本文・`notify_reason_codes`・runtime ログが混線していないか確認する。
- 7. 最初の通知から 24 時間経過後に、本番 Ver02.1 環境で `./.venv312_prod/bin/python tools/log_feedback.py daily-sync` を実行し、`signal_outcomes.csv`、`shadow_log.csv`、`📝通知レビュー.md` の初回本番更新を確認する。
- 8. `📝通知レビュー.md` に 1 件以上 `actual_move_driver` を入れて `review_status=done` にし、`daily-sync` または `import-reviews` 後に `logic_validated` が `user_reviews.csv` / `shadow_log.csv` へ正しく反映されるか確認する。
- 9. Phase 1 の有効条件は「`primary_setup_status=ready` を本有効、`watch` は参考ログのみ」として次の実装へ落とし込む。
- 10. `loss_streak` の自動計算結果を将来 `user_reviews.csv` や別状態ファイルへ固定保存する必要があるかを判断する。
- 11. Phase 1 の正式指標は、本有効件数 (`n`) / TP1 到達率 / `tp1_hit_first=false` 率 / `expired` 率 / 平均 `risk_percent_applied` / 連敗時平均 `risk_percent_applied` / `max_size_capped` 発生率を優先監視する。
- 12. `phase1_active=true` の行だけで MBP2020 本番ログを集計し、正式指標の最初の母数 (`n`) を確認する。
- 13. `expired` と `tp1_hit_first=false` は現状 proxy 指標なので、将来の timeout / stop 実測ログ化が必要かを判断する。
- 14. `Ver03` 昇格条件に照らして、`Phase 0` と `Phase 1` のどちらが未充足かを `運用資料/計画/フェーズ別計画_Phase0-1.md` で定期確認する。

## ブロッカー
- 2026-03-13 07:05 JST 時点で heartbeat は更新しているが、`signals` / `last_result.json` が同サイクルで進む状態はまだ確認できていない。
- この端末で即時に確認できた観測先は `/Users/marupro/CODEX/BTC_FX_CODEX/btc_monitor/logs` 側のみで、API本番とCLI開発の2系統を同時に追跡する観測先整理が未完了。
- 本番 Ver02.1 API 版は再起動済みだが、新件名形式と新 launchd ラベルでの最初の自然サイクル更新はまだ未観測。
- sandbox では 6 サイクル連続成功したが、本流の常駐開発環境 `Ver02.1` で今回の再試行補強後ログがまだ自然観測できていない。
- CLI は長めタイムアウトと再試行で安定度を上げたが、launchd 常駐での長時間認証持続までは未確認。
- API 本番 / CLI 開発の実メール比較は、通知条件に達するまで待ちが必要。
- 現在は通知済みシグナルが 0 件のため、`daily-sync` 初回本番確認と `logic_validated` 実データ確認は待ち状態。
- 通知が止まっている直接原因は、現時点の実データではしきい値未達の可能性が高い。
- `signal_outcomes.csv` と `user_reviews.csv` はまだ存在せず、`daily-sync` 初回本番確認には通知発生待ちが必要。
- Ver01 / Ver02.1 の runtime ログはまだ 0 byte のため、実運用中にログが必要十分に残るかは引き続き観察が必要。
- 強条件（🟡 / 🔥）は市場条件が厳しめに設定されているため、発火確認までに数サイクル必要。
- `signal_outcomes.csv` / `shadow_log.csv` の本格評価は、通知から24時間経過した実データがたまるまで待ちが必要。
- `Phase 1` はサイズ計画・出口計画・活性化判定の土台までは入ったが、実データでの有効化確認と正式評価はまだ未完了で、`Ver03` 昇格には通知後フロー確認とあわせて継続観測が必要。
- `loss_streak` は自動反映に切り替わったが、履歴 0 件の間は `PHASE1_LOSS_STREAK` 予備値へフォールバックする。
- `Phase 1` の追加ログ列は `shadow_log.csv` と週次レポートまで接続済みだが、件数 0 のため実データ評価はまだできない。
- `phase1_active` は実装済みだが、MBP2020 本番ログ側でまだこの列を蓄積できていない。
- `expired` と `tp1_hit_first=false` は、現状では timeout / stop の proxy であり、厳密な実測指標ではない。

## 完了条件
- Ver01 を比較基準として維持しつつ、Ver02.1 の `Phase 0` 通知後フローが本番で一周完了し、あわせて `Phase 1` の有効条件と正式指標が文書と実装候補の両方で整理されていること。
