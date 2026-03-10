# Progress Log

- 日時: 2026-03-11 02:24 JST
- 実施内容: Ver02 の現時点を `v2.3` として固定する前提で、大幅な改善を一式実装した。主な内容は、(1) `signal_id`・通知結果・抑制理由・データ欠損状態などを `result` / JSON / CSV に保存する詳細ログ化、(2) `signal_tier` を理由コード付きで返す構成への拡張、(3) 通知判定を `notify_reason_codes` / `suppress_reason_codes` を返す構造へ整理、(4) Funding 取得失敗時を中立扱いしつつ欠損として記録する処理、(5) スコア内訳・主要因・主要セットアップ理由の保存、(6) `tools/log_feedback.py` とレビュー導線・週次/月次レポート基盤の追加、(7) 関連 README / 運用資料の整備、である。
- 変更ファイル: `main.py`, `src/analysis/position_risk.py`, `src/analysis/rr.py`, `src/analysis/scoring.py`, `src/analysis/signal_tier.py`, `src/notification/trigger.py`, `src/storage/csv_logger.py`, `src/storage/json_store.py`, `tools/log_feedback.py`, `tests/test_log_feedback.py`, `tests/test_funding_and_signal.py`, `tests/test_notification_trigger.py`, `運用資料/README.md`, `運用資料/ログ検証と改善運用ガイド.md`, `運用資料/AI向けシステムログ全体整理.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: ログ活用基盤は実装済みだが、実運用データをためた後の週次・月次レポート活用はこれから。
- メモ: `./.venv312/bin/python -m unittest discover -s tests -v` で 13 件すべて成功。

- 日時: 2026-03-11 02:19 JST
- 実施内容: 改善設計書 v2.1 に沿って、Ver02 の観測基盤 Phase 0 を拡張実装した。主な内容は、(1) `compute_scores()` に因子寄与度内訳と上位 positive / negative factor を追加、(2) `evaluate_position_risk()` に `prelabel_primary_reason` と breakdown を追加、(3) `build_setup()` に `status_reason_code` / `invalid_reason_codes` を追加、(4) `compute_signal_tier()` と `should_notify()` を理由コードつき返却へ変更、(5) `main.py` で `data_quality_flag` / `data_missing_fields` / `notify_reason_codes` / `suppress_reason_codes` / `ai_decision` / `ai_confidence` / `primary_setup` 価格情報を payload へ追加、(6) Funding 取得失敗時は中立扱いで継続し `data_missing_fields=funding` を残す構成へ変更、(7) `trades.csv` に Phase 0 用の追加列を実装、(8) `tools/log_feedback.py` を `shadow_log.csv` / 12h 評価 / `tp1_hit_first` / `outcome` / `actual_move_driver` / `logic_validated` / 通知監査 A/B/C/D 対応へ全面拡張、(9) Obsidian `📝通知レビュー.md` を新列付きで再出力、(10) README と運用ガイドへ `shadow_log.csv` と `build-shadow-log` を追記、(11) `unittest` 13件成功、`py_compile` 成功、`build-feedback-report --period weekly` の煙テスト成功、(12) 開発環境常駐 `com.afrog.btc-monitor` を再起動し、再起動前 `pid=47314`、再起動後 `pid=54689` を確認した。
- 変更ファイル: `main.py`, `src/analysis/scoring.py`, `src/analysis/position_risk.py`, `src/analysis/rr.py`, `src/analysis/signal_tier.py`, `src/notification/trigger.py`, `src/storage/csv_logger.py`, `tools/log_feedback.py`, `tests/test_log_feedback.py`, `tests/test_notification_trigger.py`, `tests/test_funding_and_signal.py`, `運用資料/README.md`, `運用資料/ログ検証と改善運用ガイド.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`, `📒打ち合わせノート.md`, `📝通知レビュー.md`
- 未解決事項: `shadow_log.csv` と追加列が次回の定時サイクルで実データとして自然に流れるかは未確認。`daily-sync` の本番初回確認と `actual_move_driver` 入力後の `logic_validated` 実運用確認もこれから。Phase 1 の paper trade / 損益管理モジュール着手は未実施。
- メモ: ChatGPT API を使う実行は今回行っていない。確認は `./.venv312/bin/python -m unittest discover -s tests -v`、`./.venv312/bin/python -m py_compile ...`、`./.venv312/bin/python tools/log_feedback.py build-feedback-report --period weekly --output-md /tmp/btc_feedback_weekly_phase0.md`、`./.venv312/bin/python tools/log_feedback.py export-review-queue`、`zsh tools/start_monitor.sh` で実施。

- 日時: 2026-03-11 00:50 JST
- 実施内容: 他AI評価用として、現行 `btc_monitor` のロジック全体を実装ベースで整理した仕様書 `運用資料/AI向けシステムロジック全体整理.md` を新規作成した。内容は、定時実行フロー、MEXC/Binance の取得データ、各分析モジュールの役割、`bias` / `prelabel` / `confidence` / `signal_tier` / 通知条件 / ログ保存 / 補助ツールまでを一連の判断レイヤーとして説明する形にまとめた。コード変更はドキュメント追加と運用記録更新のみで、実行ロジック本体は変更していない。
- 変更ファイル: `運用資料/AI向けシステムロジック全体整理.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 新規仕様書は実装ベースで整理済みだが、他AIへ評価依頼したあとの指摘反映は未実施。
- メモ: ChatGPT API を使う実行は今回行っていない。コード読取対象は `main.py`, `config.py`, `src/analysis/*`, `src/data/*`, `src/ai/*`, `src/notification/*`, `src/storage/*`, `tools/log_feedback.py` を中心に確認した。

- 日時: 2026-03-11 00:33 JST
- 実施内容: ログ活用基盤 フェーズ1 を実装した。主な内容は、(1) 観測ログへ `signal_id`、通知有無、通知時刻、`atr_15m_value`、最寄りサポレジ、`summary_subject` を追加、(2) `save_signal_snapshot()` を `signal_id` ベース保存へ変更、(3) `tools/log_feedback.py` を新規追加して `update-outcomes` / `export-review-queue` / `import-reviews` / `build-feedback-report` / `daily-sync` を実装、(4) `signal_outcomes.csv` と `user_reviews.csv` を扱う upsert ロジック、事後評価ロジック、レビュー Markdown テーブルの入出力を追加、(5) フィードバック週次・月次レポートの雛形と改善候補抽出ロジックを実装、(6) `📝通知レビュー.md` を Obsidian 側へ新規作成し、README と運用ガイドへ運用コマンドを追記、(7) `unittest` 4件を追加して全12件成功を確認、(8) 開発環境常駐 `com.afrog.btc-monitor` を再起動して最新コードを反映、である。再起動前 `pid=42329`、再起動後 `pid=47314` を確認した。
- 変更ファイル: `main.py`, `src/storage/csv_logger.py`, `src/storage/json_store.py`, `tools/log_feedback.py`, `tests/test_log_feedback.py`, `運用資料/README.md`, `運用資料/ログ検証と改善運用ガイド.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`, `📒打ち合わせノート.md`, `📝通知レビュー.md`
- 未解決事項: `tools/log_feedback.py daily-sync` を実データで回した初回結果の確認は未実施。新しい `signal_id` / `was_notified` / `notified_at_utc` / 最寄りサポレジ列が実ログへ想定どおり入るかも次回定時サイクル確認が必要。
- メモ: 確認は `./.venv312/bin/python -m unittest discover -s tests -v`、`./.venv312/bin/python tools/log_feedback.py build-feedback-report --period weekly --output-md /tmp/btc_feedback_weekly.md`、`./.venv312/bin/python tools/log_feedback.py export-review-queue --review-note /tmp/btc_feedback_review.md` で実施。ChatGPT API は未使用。

- 日時: 2026-03-10 23:26 JST
- 実施内容: Ver02 開発環境の常駐 `com.afrog.btc-monitor` を再起動し、今回の近場サポレジ表示補正を常駐プロセスへ反映した。再起動前は `pid=37563`、再起動後は `pid=42329` となり、`launchctl print gui/$(id -u)/com.afrog.btc-monitor` で `state = running`、`program = .../.venv312/bin/python` を確認した。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 補正後の表示が次回以降の実メールで自然に見えるかは、定時サイクル確認が必要。
- メモ: `zsh tools/start_monitor.sh` をローカルで実行。ChatGPT API を使う処理は今回行っていない。

- 日時: 2026-03-10 23:20 JST
- 実施内容: Ver02 の最優先タスクとして、直近5サイクル（21:05 / 21:36 / 22:05 / 22:47 / 23:05 JST）のログを確認し、`location_risk` / `risk_flags` / `signal_tier` の出方を点検した。観察の結果、`signal_tier` は全件 `normal` で、`prelabel` は `SWEEP_WAIT` と `NO_TRADE_CANDIDATE` が中心、主な阻害要因は `lower_liquidity_close`、`sweep_incomplete`、`ask_wall_close`、および `RR_insufficient` だった。あわせて、表示用の近場サポレジに「現在価格の反対側の帯」が混ざるケースを確認したため、表示ロジックを修正し、サポートは価格下側中心、レジスタンスは価格上側中心で出すよう調整した。`unittest` へ回帰テストを1件追加し、全8件成功を確認した。
- 変更ファイル: `main.py`, `src/analysis/support_resistance.py`, `tests/test_support_resistance.py`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`, `📒打ち合わせノート.md`
- 未解決事項: 強条件（🟡 / 🔥）と `signal_tier_upgraded` の実運用発火確認は未完了。今回のサポレジ表示修正が実メール上で自然に見えるかも次回サイクルで確認が必要。
- メモ: OpenAI API を使う実行は今回行っていない。確認は既存ログ読取と `./.venv312/bin/python -m unittest discover -s tests -v` で実施。

- 日時: 2026-03-10 22:58 JST
- 実施内容: Ver02 の現時点を `v2.2` として固定する前提で、そこそこの改善を一式反映した。主な内容は、(1) Funding 閾値と表示を `%` 単位で統一、(2) `signal_tier` / `signal_badge` と昇格通知ロジックを追加、(3) サポレジを内部計算用と表示用に分離、(4) 件名・本文の Funding 表示と強条件バッジ表示を改善、(5) CSV/JSON とバックテストを新仕様へ追従、(6) `unittest` 7件を追加して全件成功、(7) プロジェクト用 `AGENTS.md` を `btc_monitor/` 配下へ移動、である。
- 変更ファイル: `main.py`, `src/analysis/funding.py`, `src/analysis/signal_tier.py`, `src/analysis/support_resistance.py`, `src/notification/trigger.py`, `src/ai/summary.py`, `src/storage/csv_logger.py`, `backtest/runner.py`, `prompts/summary_prompt.md`, `.env.example`, `README.md`, `tests/test_funding_and_signal.py`, `tests/test_notification_trigger.py`, `tests/test_support_resistance.py`, `tests/test_summary_format.py`, `AGENTS.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 強条件バッジ（🟡 / 🔥）の実運用発火確認と、実メール文面の最終微調整は継続。
- メモ: 確認は `./.venv312/bin/python -m unittest discover -s tests -v` で実施し、7件すべて成功。

- 日時: 2026-03-10 21:55 JST
- 実施内容: Ver02 の現時点コミットをタグ `v2.1` として固定し、GitHub へ push した。`v2.1` の主な内容は、Funding 表示の `%` 統一、サポレジの近接順表示、距離表示、TP順整列、`signal_tier` / `signal_badge` 追加、通知昇格トリガー対応、件名・本文の見せ方改善、および関連テスト追加である。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 強条件バッジ（🟡 / 🔥）の実運用発火確認は未完了。
- メモ: タグ `v2.1` はコミット `93e462a` を指す。

- 日時: 2026-03-10 22:52 JST
- 実施内容: ユーザー依頼により、打ち合わせノートへ最新状況を要約追記した。内容は「Ver02 改善実装完了」「常駐再起動済み」「手動実行で Funding 新表示確認済み」「現在は実メール観察フェーズ」「強条件バッジ発火確認は市場条件待ち」。
- 変更ファイル: `📒打ち合わせノート.md`, `運用資料/progress.md`
- 未解決事項: 強条件（🟡 / 🔥）の実運用発火確認は未完了。
- メモ: 実装フェーズから観察フェーズへ移行したことを、打ち合わせノート側の文脈にも反映した。

- 日時: 2026-03-10 22:48 JST
- 実施内容: ユーザー許可のうえで Ver02 の手動 `run_cycle` を1回実行し、新仕様の実動作を確認した。結果は `timestamp_jst=2026-03-10T22:47:18+09:00`、`prelabel=SWEEP_WAIT`、`signal_tier=normal`、`signal_badge=''`、`funding_rate_raw=0.000023`、`funding_rate_pct=0.0023`、`funding_rate_display='ほぼ中立 (+0.0023%)'`。`last_result.json` でも同値を確認し、メール本文に「ファンディングレート: ほぼ中立 (+0.0023%)」が反映されることを確認した。今回の条件は強条件に未到達のため、バッジ非表示挙動（normal）が正しく動作した。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 強条件（🟡 / 🔥）が実際に発火するケースの実運用確認は未実施。
- メモ: OpenAI API 使用はユーザー許可取得済み。通知理由は空配列。

- 日時: 2026-03-10 22:42 JST
- 実施内容: Ver02 改善計画を実装した。主な内容は、(1) Funding を raw / % / ラベル表示に分離して判定単位を `%` に統一、(2) サポレジを内部計算用 `all zones` と表示用（近い順 / 強度順）に分離、(3) `signal_tier`（`normal` / `strong_machine` / `strong_ai_confirmed`）と `signal_badge`（🟡/🔥）を追加、(4) 通知トリガーへ `signal_tier_upgraded` を追加してクールダウン中の昇格通知を許可、(5) 要約件名・本文へバッジ表示と Funding 表示（例: ほぼ中立 (+0.0037%)）を反映、(6) CSV/JSON へ新項目を追加。バックテスト側も `all zones` と `%単位Funding` へ揃え、ライブとのロジック差分を減らした。あわせて `unittest` を新規追加し、7件すべて成功を確認した。
- 変更ファイル: `main.py`, `src/analysis/funding.py`, `src/analysis/signal_tier.py`, `src/analysis/support_resistance.py`, `src/notification/trigger.py`, `src/ai/summary.py`, `src/storage/csv_logger.py`, `backtest/runner.py`, `prompts/summary_prompt.md`, `.env.example`, `README.md`, `tests/test_funding_and_signal.py`, `tests/test_notification_trigger.py`, `tests/test_support_resistance.py`, `tests/test_summary_format.py`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 実メールでの最終見え方確認（件名バッジ、Funding表示、signal_tier動作）は未実施。`run_cycle` 実行には OpenAI API 利用が含まれるため、次回は許可取得のうえで確認する。
- メモ: 構文チェック `python3 -m py_compile` と `./.venv312/bin/python -m unittest discover -s tests -v` は成功。

- 日時: 2026-03-10 22:06 JST
- 実施内容: ユーザー依頼により、打ち合わせノートへ「このシステムでかなり理想に近い場面」の短い整理メモを追記した。あわせて、そうした場面を今後はメール内で絵文字や目立つラベル付きで分かりやすく伝えたい、という実装方針も記録した。`NEXT_TASK.md` にも、強い好条件通知の視覚強調を検討項目として追加した。
- 変更ファイル: `📒打ち合わせノート.md`, `運用資料/NEXT_TASK.md`, `運用資料/progress.md`
- 未解決事項: 実装自体はまだ未着手。
- メモ: 方向・位置・RR がそろった場面を、通常通知と視覚的に差別化する方針。

- 日時: 2026-03-10 21:53 JST
- 実施内容: ユーザー依頼により、打ち合わせノートへ「次の作業タイミング」の判断メモを追記した。内容は、軽い文面見直しは 2026-03-11 に一度行う、本格的な閾値調整は Ver02 通知を 3〜5 サイクル分ためてから行う、という運用方針。
- 変更ファイル: `📒打ち合わせノート.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: なし
- メモ: 実装フェーズから観察・調整フェーズへ移っていることを、打ち合わせノート側にも反映した。

- 日時: 2026-03-10 21:48 JST
- 実施内容: `NEXT_TASK.md` の運用形式を整理し、見出しを `現在の状況` / `次のタスク` / `ブロッカー` / `完了条件` の構成へ書き直した。あわせて、「現在の状況」は履歴ではなく、不要項目を消す・並べ替える・短く整える前提の整理欄として扱うルールを `Global_BOX/AGENTS_TEMPLATE.md` に追記した。Obsidian 側の `00_Global_BOX` は `Global_BOX` へのシンボリックリンク構成のため、同内容がそのまま反映される状態。
- 変更ファイル: `運用資料/NEXT_TASK.md`, `/Users/marupro/CODEX/Global_BOX/AGENTS_TEMPLATE.md`, `運用資料/progress.md`
- 未解決事項: なし
- メモ: `NEXT_TASK.md` は履歴ではなく、毎回見やすく更新する「最新版の作業メモ」として運用する。

- 日時: 2026-03-10 21:42 JST
- 実施内容: ユーザー指示により、Ver02 開発環境の常駐 `com.afrog.btc-monitor` を再起動した。`./tools/start_monitor.sh` 実行後、`launchctl print gui/$(id -u)/com.afrog.btc-monitor` で `state = running`、`pid = 33064`、`program = .../.venv312/bin/python` を確認し、`logs/runtime/monitor.pid` も `33064` に更新されていることを確認した。これにより、今回の表示改善コードを常駐プロセスへ反映した。
- 変更ファイル: `運用資料/progress.md`
- 未解決事項: なし
- メモ: 今後は「開発環境の実行ファイルに関わる変更」を行った作業の終了時に、常駐有無を確認し、稼働中なら必要に応じて再起動する運用で進める。

- 日時: 2026-03-10 21:36 JST
- 実施内容: ユーザー許可のうえで Ver02 の手動 `run_cycle` を1回実行し、表示改善の実動作を確認した。`summary_subject` は `[Ver02] [BTC監視] 2026-03-10 21:36 SWEEP_WAIT / long / 70,356.30 / Confidence 77`。`last_result.json` では `support_zones` / `resistance_zones` が現在価格に近い順へ並び、`distance_from_price` も付与されていることを確認した。`support_zones_by_strength` / `resistance_zones_by_strength` には従来の強度順も保持されている。TP順も `long: TP1 69263.31 -> TP2 69947.99`、`short: TP1 69521.3 -> TP2 68387.01` と自然順で確認できた。AI要約本文でも、最寄りサポート・レジスタンスを距離つきで記述することを確認した。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: AI要約本文は改善意図どおり概ね反映されたが、表現としてまだ「方向感」と「いま入る位置」がやや近接して読める箇所があるため、必要なら次回さらにプロンプト調整する。
- メモ: OpenAI API 使用はユーザー許可取得済み。通知理由は `confidence_jump`。

- 日時: 2026-03-10 21:34 JST
- 実施内容: Ver02 の「見せ方調整」を実装した。サポート / レジスタンスは計算用の強度上位3件を残したまま、通知や `last_result.json` に載せる表示用データを「現在価格に近い順」へ並び替え、各ゾーンに `distance_from_price` を追加した。あわせて、ロング / ショートの TP1 / TP2 が逆転しないよう正規化処理を `src/analysis/rr.py` に追加し、要約フォールバック文と AI 要約プロンプトも「方向感」と「いま入る位置」を分けて書く形へ調整した。
- 変更ファイル: `main.py`, `src/analysis/support_resistance.py`, `src/analysis/rr.py`, `src/ai/summary.py`, `prompts/summary_prompt.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 実メール本文での見え方確認は未実施。`run_cycle` は OpenAI API を使うため、今回こちらでは実行していない。
- メモ: `python3 -m py_compile` と `.venv312` 上のローカル確認スクリプトで、構文エラーなし・近接順表示・TP順整列を確認済み。

- 日時: 2026-03-10 21:27 JST
- 実施内容: Ver01メールと現在チャートのズレに関する考察を、Ver02改善方針として打ち合わせノートへ追記した。要点は「サポレジ表示が強度優先で、現在価格に近い順ではないため直感とズレる」「方向感と位置の説明が混ざっている」「TP1/TP2の順序逆転が起こりうる」の3点。あわせて `NEXT_TASK.md` を更新し、Ver02での改善項目として「近接順表示」「距離併記」「TP順整列」を追加した。
- 変更ファイル: `📒打ち合わせノート.md`, `運用資料/NEXT_TASK.md`, `運用資料/progress.md`
- 未解決事項: 実装は未着手で、現在は改善方針の整理まで。
- メモ: Ver02へ反映したい方向性として明文化済み。

- 日時: 2026-03-10 21:07 JST
- 実施内容: ユーザー依頼により、Obsidian プロジェクトフォルダへ `NEXT_TASK.md` のシンボリックリンクを作成した。リンク先は `btc_monitor/運用資料/NEXT_TASK.md` で、同フォルダ内の `README.md` と同じ運用（実体はコード側・参照はObsidian側）に揃えた。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`（※シンボリックリンクを新規作成）
- 未解決事項: なし
- メモ: 作成先 `/Users/marupro/Library/Mobile Documents/iCloud~md~obsidian/Documents/AFROG電脳/10_デジタルスキル/00_PROJECT/FX/トレード支援システム/NEXT_TASK.md`

- 日時: 2026-03-10 21:05 JST
- 実施内容: ユーザー依頼により、`📒打ち合わせノート.md` へ最新報告を追記した。内容は、Ver02 の現在価格表示対応と常駐確認状態、Ver01 の運用監視フェーズ化、以後の調整方針（`location_risk` / `risk_flags` 観察、清算イベント蓄積評価）を要約したもの。
- 変更ファイル: `📒打ち合わせノート.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: なし
- メモ: 打ち合わせノートは日時先頭＋3ブロック（今の状況/現在の動向/今後のやるべきこと）で統一。

- 日時: 2026-03-10 21:03 JST
- 実施内容: 打ち合わせノートの保存先変更に合わせて、参照先パスを更新した。プロジェクト運用ルールの `AGENTS.md` で、旧パス（`.../FX/CODEX版/BTC＋CODEX版 監視システム 打ちあわせシート.md`）を新パス（`.../FX/トレード支援システム/📒打ち合わせノート.md`）へ置換。関連参照を再検索し、旧パス参照が残っていないことを確認した。
- 変更ファイル: `AGENTS.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: なし
- メモ: 新ノートは実在確認済み、旧ファイルは存在しない状態。

- 日時: 2026-03-10 20:55 JST
- 実施内容: 打ち合わせシートの見出しマークアップを `####` 基準で統一した。日付ブロックと各セクション（今の状況 / 現在の動向 / 今後のやるべきこと）を揃え、見出しレベルの混在（`##` / `###` / `####`）を整理した。
- 変更ファイル: `打ち合わせシート.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: なし
- メモ: 既存の本文内容は変更せず、見出しレベルのみ調整。

- 日時: 2026-03-10 20:50 JST
- 実施内容: ユーザー指定の打ち合わせシートへ、開発環境の確認コマンドを現在の記載スタイルに合わせて追記した。追加内容は `launchctl print ... | grep -E 'state =|pid ='` による最終確認コマンドと、`state = running` / `pid` の読み方。
- 変更ファイル: `打ち合わせシート.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: なし
- メモ: 既存の本番確認コマンド・開発確認コマンドの構成は維持したまま、最終確認行だけ追加。

- 日時: 2026-03-10 20:43 JST
- 実施内容: ユーザー許可のうえで Ver02 ローカル `run_cycle` を実行し、現在価格表示の実動作を確認した。件名は `[Ver02] [BTC監視] 2026-03-10 20:42 SWEEP_WAIT / long / 70,617.10 / Confidence 62` となり、本文先頭にも「現在のBTC価格は70,617.1ドル」と表示された。`ai_advice_none=False` で AI 判定は取得成功、通知理由は空配列だった。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: Ver01 側へ同じ「現在価格表示」を取り込むかは次回本番反映時の判断が必要。
- メモ: 観察目的の手動実行として実施。OpenAI API 使用は事前許可取得済み。

- 日時: 2026-03-10 20:39 JST
- 実施内容: 「メールに現在BTC価格を入れたい」という要望に対応し、Ver02コードへ反映した。`result` に `current_price` を追加し、件名へ価格表示（例: `... / long / 69,321.12 / Confidence 62`）を追加。フォールバック本文にも「現在価格は xxx USDT」を明記し、AI要約プロンプトにも現在価格を必ず含める制約を追記した。
- 変更ファイル: `main.py`, `src/ai/summary.py`, `prompts/summary_prompt.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: Ver01へ同変更を入れるかは次回デプロイ判断が必要（現時点はVer02のみ反映）。
- メモ: OpenAI API を使う実行確認は未実施。`py_compile` とローカル生成テストで件名・本文への価格反映を確認。

- 日時: 2026-03-10 20:35 JST
- 実施内容: ユーザー許可のうえで Ver02 ローカル `run_cycle` を1回実行した。結果は `summary_subject=[Ver02] [BTC監視] 2026-03-10 20:34 SWEEP_WAIT / long / Confidence 62`、`prelabel=SWEEP_WAIT`、`location_risk=68.0`、`ai_advice_none=False`。通知理由は `confidence_jump`。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: Ver02 の継続観測（`location_risk` / `risk_flags` の閾値調整）は引き続き必要。
- メモ: OpenAI API を使う手動実行は許可取得後に実施。

- 日時: 2026-03-10 19:41 JST
- 実施内容: `運用資料/README.md` のブランチ運用ルールに、タグ番号の付け方を追記した。Ver01 -> `v1.0`、Ver02 -> `v2.0`、Ver02 の軽微修正版 -> `v2.1` のように、世代番号とタグ番号をそろえる方針を明文化した。
- 変更ファイル: `運用資料/README.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: なし
- メモ: タグは push ごとではなく、安定版や本番反映の節目で付けるルールも併記。

- 日時: 2026-03-10 19:27 JST
- 実施内容: `運用資料/README.md` にブランチ運用ルールを追記した。`main` / `ver01` / `v1.0` / `ver02` の役割と、Ver02 で開発して安定後に `main` へ取り込む基本手順を、初心者でも追いやすい形で明文化した。
- 変更ファイル: `運用資料/README.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: なし
- メモ: 今後は人だけでなく AI も、この記述を参照すればブランチの意味を取り違えにくい。

- 日時: 2026-03-10 19:16 JST
- 実施内容: `ver02` と同じ内容を指していた旧ブランチ `流動性・清算・板情報対応版` を廃止する方針に合わせ、以後は `ver02` を「流動性・清算・板情報を追加した版」の正式な名前として扱う運用へ整理した。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: なし
- メモ: Ver01 は追加前の安定版、Ver02 は追加後の拡張版、という位置づけで整理。

- 日時: 2026-03-10 19:11 JST
- 実施内容: 現在の開発ブランチ `流動性・清算・板情報対応版` の先頭コミットから、Ver02 用の保存ブランチ `ver02` を新規作成した。これにより、Ver01 は `ver01` / `v1.0`、Ver02 は `ver02` として Git 上で系統を分けて扱える状態にした。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: `ver02` を今後の正式開発本線にするか、さらに作業ブランチを切って進めるかは運用判断が必要。
- メモ: `ver02` の起点は作成時点の `流動性・清算・板情報対応版` 先頭コミット。

- 日時: 2026-03-10 18:58 JST
- 実施内容: ユーザー指示に従い、Ver01 本番へ AI 待ち時間再調整（10秒/20秒）をデプロイした。MBP2020上で `.env` と `load_config` の値を確認後、`com.afrog.btc-monitor-ver01` を再起動し `running` を確認。あわせて打ち合わせシートへ「Ver01開発は一旦ここまで、以後はVer02注力」の方針を追記し、`NEXT_TASK.md` も同方針へ更新した。
- 変更ファイル: `打ち合わせシート.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`（※Ver01反映はリモート環境で実施）
- 未解決事項: Ver01 は運用監視を継続。改善作業は Ver02 側で進行。
- メモ: OpenAI API を使う手動実行は今回行っていない（設定反映と再起動のみ）。

- 日時: 2026-03-10 18:53 JST
- 実施内容: ユーザー依頼に合わせて `NEXT_TASK.md` を整理し、完了済みタスク（Ver01/Ver02の件名確認）を削除した。未完了の項目のみを残し、次回着手順を 3 件へ圧縮した。
- 変更ファイル: `運用資料/NEXT_TASK.md`, `運用資料/progress.md`
- 未解決事項: Ver01 の継続更新確認、位置フィルター閾値調整、清算イベント蓄積の本番適用は継続。
- メモ: 完了済みを残さない運用へ合わせて更新。

- 日時: 2026-03-10 18:50 JST
- 実施内容: 「清算イベント0件が続く時間帯を減らす」ため、Binance清算イベントのローカル蓄積を実装した。`fetch_market_structure` に `base_dir` を渡し、`logs/cache/binance_liquidations_{symbol}.json` へ直近イベントを保持。次サイクルではWS取得分とキャッシュをマージして TTL 内イベントを利用できるようにした（重複除去・件数上限あり）。あわせて設定値 `BINANCE_LIQUIDATION_CACHE_SEC` と `BINANCE_LIQUIDATION_CACHE_MAX` を追加し、構文チェックを通過。Ver01のログ確認も行い、現時点の `last_result` は 18:05 のまま、`monitor.err` に直近エラー追記なしを確認。
- 変更ファイル: `src/data/exchange_fetcher.py`, `main.py`, `config.py`, `.env.example`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: この清算イベント蓄積実装は現時点でローカルVer02側のみ。Ver01へ反映するには次回デプロイ時の取り込みが必要。
- メモ: OpenAI API を使う検証は行っていない（構文/ローカルロジック検証のみ）。

- 日時: 2026-03-10 18:38 JST
- 実施内容: ユーザー許可のうえで Ver02 ローカル `run_cycle` を再実行した。結果は `summary_subject=[Ver02] [BTC監視] 2026-03-10 18:37 SWEEP_WAIT / long / Confidence 74`、`prelabel=SWEEP_WAIT`、`location_risk=45.0`、`ai_advice_none=False`。通知理由は空配列で、今回は通知トリガー条件に該当しなかった。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: Ver01 は設定更新済みだが未再起動のため、10秒/20秒設定の実反映確認は保留。
- メモ: OpenAI API を使う手動実行はユーザー許可後に実施。

- 日時: 2026-03-10 18:29 JST
- 実施内容: ユーザー指示により、Ver01（本番側ファイル）の AI 待ち時間設定を Ver02 と同値へ更新した。MBP2020 の `~/CODEX/BTC_FX_CODEX_ver01/btc_monitor/.env` と `.env.example` を `AI_TIMEOUT_SEC=10`、`AI_SUMMARY_TIMEOUT_SEC=20` に変更。デプロイ不要指定のため、`launchd` 再起動は実施していない。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`（※Ver01実ファイルはリモート環境で更新）
- 未解決事項: Ver01 の実行プロセスは再起動していないため、設定値は次回再起動後に有効化される。
- メモ: 現在の `com.afrog.btc-monitor-ver01` は `running` 継続中。

- 日時: 2026-03-10 18:25 JST
- 実施内容: ローカル Ver02 で手動 `run_cycle` を1回実行した。待ち時間2倍設定（`AI_TIMEOUT_SEC=10`, `AI_SUMMARY_TIMEOUT_SEC=20`）適用後の実行で、`summary_subject=[Ver02] ...`、`prelabel=SWEEP_WAIT`、`location_risk=63.0`、`ai_advice_none=False` を確認した。通知理由は `agreement_changed / confidence_jump / prelabel_improved` だった。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: Ver02 の件名ラベル表示は実行結果で確認できたが、実メール受信での見え方確認は継続タスク。
- メモ: 本番 Ver01 には未反映（ローカル Ver02 のみ確認）。

- 日時: 2026-03-10 18:23 JST
- 実施内容: ユーザー要望に合わせて、ローカル開発環境（Ver02）のAI待ち時間を2倍に変更した。`.env` と `.env.example` の `AI_TIMEOUT_SEC` を 5→10 秒、`AI_SUMMARY_TIMEOUT_SEC` を 10→20 秒に更新。本番（Ver01）は未変更。あわせてローカルの常駐状態を確認し、現在 Ver02 は起動中ではない（`launchctl` / `ps` とも該当なし）ことを確認した。
- 変更ファイル: `.env`, `.env.example`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: Ver02 は現在停止中のため、設定は次回起動時に反映される。必要なら再起動手順を実施する。
- メモ: 本番への適用は未実施（ユーザー指示どおり）。

- 日時: 2026-03-10 18:10 JST
- 実施内容: 打ち合わせシートへ最新報告を追記した。内容は、Ver01/Ver02 の通知メール件名に環境ラベル（`[Ver01]` / `[Ver02]`）を付けて識別できるようにした点と、本番側再起動まで完了している点を中心に整理した。
- 変更ファイル: `打ち合わせシート.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 次回の実着信メールで、件名ラベルの表示が期待どおりか最終確認が必要。
- メモ: 打ち合わせシートは「今の状況 / 現在の動向 / 今後のやるべきこと」の形式で追記。

- 日時: 2026-03-10 18:07 JST
- 実施内容: メール件名で Ver01/Ver02 を識別できるように対応した。ローカル（Ver02）は `SYSTEM_LABEL=Ver02` を導入し、件名生成ロジックへ環境ラベルを反映。あわせて本番MBP2020（Ver01）にも `SYSTEM_LABEL=Ver01` を設定し、`main.py` で件名へプレフィックス付与する修正を反映。文法チェック後に `com.afrog.btc-monitor-ver01` を再起動し、`state=running` を確認した。
- 変更ファイル: `config.py`, `main.py`, `src/ai/summary.py`, `.env`, `.env.example`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 次回通知メールの実着信で、件名が期待どおり `Ver01` / `Ver02` 表示になるか最終確認が必要。
- メモ: 本番側はリモート編集後に `python -m py_compile` と `launchctl` 再起動で反映済み。

- 日時: 2026-03-10 17:22 JST
- 実施内容: ブランチ環境と常駐ジョブの棚卸しを実施し、不要な常駐をクリーンアップした。ローカル開発機では `com.afrog.btc-monitor` を停止し、`~/Library/LaunchAgents/com.afrog.btc-monitor.plist` は無効化ファイル（`.disabled_...`）へリネーム。本番MBP2020側は `com.afrog.btc-monitor-ver01` のみ残し、`launchd` が参照していた旧パスを `~/CODEX/BTC_FX_CODEX_ver01/...` へ修正して再登録し、`state=running` を確認した。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: なし（常駐の重複・旧パス参照は解消）。
- メモ: ローカルのCodexアプリ常駐（`application.com.openai.codex...`）は開発ツール本体のため維持。

- 日時: 2026-03-10 17:16 JST
- 実施内容: MBP2020 側の旧本番パス `/Users/marupro/BTC_FX_CODEX_ver01` を削除した。移行後の運用先は `/Users/marupro/CODEX/BTC_FX_CODEX_ver01` に統一済みで、削除後に旧パスが存在しないことを確認した。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: なし（本番配置の旧パス整理は完了）。
- メモ: 今後の本番アップロード先は `~/CODEX` 配下のみを使用する。

- 日時: 2026-03-10 16:55 JST
- 実施内容: VPN接続後に MBP2020 (`192.168.1.38`) へSSH接続し、Ver01（`main`）を本番専用ディレクトリ `~/BTC_FX_CODEX_ver01/btc_monitor` へ配備した。Python 3.12.10 を導入し、`.venv312_prod` を作成、依存関係をインストール、`.env` を配置。`launchd` は新ラベル `com.afrog.btc-monitor-ver01` で登録し、`running` 状態（専用作業ディレクトリ・専用ログパス）を確認した。Ver02専用ファイル（例: `src/analysis/liquidity.py`）が存在しないことも確認し、Ver01運用分離を達成。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: Ver01本番の定時実行で `last_result.json` が継続更新されるかの追跡確認が必要。
- メモ: 既存ローカル開発（Ver02）は未変更。今回の本番起動は `com.afrog.btc-monitor-ver01` のみ。

- 日時: 2026-03-10 16:39 JST
- 実施内容: Ver01/Ver02 の本番分離作業に着手し、指定先 `192.168.1.38` への到達確認を実施した。`ping` は 100% loss、`ssh` は `port 22 timeout` で接続できず、現時点では VPN 未接続または経路未到達のためデプロイ作業本体は未開始。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: VPN接続後に再度SSH疎通確認し、Ver01（main）をMBP2020へ配備する必要あり。
- メモ: ローカル側の実装・検証状態は維持されており、接続回復後はそのまま本番分離手順へ移行可能。

- 日時: 2026-03-10 16:19 JST
- 実施内容: ユーザー許可のうえで `run_cycle` を手動1回実行し、Ver02の新項目が実出力に入ることを確認した。結果は `prelabel=SWEEP_WAIT`、`location_risk=60.0`、`oi_value=81815.097`、`orderbook_bias=bid_heavy`、`market_structure_missing_fields=[]`、AI判定 `WAIT_FOR_SWEEP` で、位置フィルターと市場構造データが実運用ラインで動作していることを確認した。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: WS清算イベントは時間帯によって0件が続くため、イベント蓄積（ローカル保存）による安定化が次タスク。
- メモ: OpenAI API を使う手動実行は本件で実施済み（許可取得済み）。

- 日時: 2026-03-10 15:42 JST
- 実施内容: `NEXT_TASK` の実行を進め、`.venv312` に `websocket-client` を導入した。Binance REST 側（OI/板/CVD材料）の取得は実データで成功を確認した。WS清算イベントは0件継続だったため、`!forceOrder@arr` フォールバックと SSL 検証失敗時の接続フォールバックを追加して取りこぼし耐性を上げた。あわせて通知本文フォールバックの先頭が「方向」ではなく「位置評価」になることをローカル生成で確認した。
- 変更ファイル: `requirements.txt`, `src/data/provider_client/binance_market.py`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 清算イベントはテスト時点で0件のため、次の本番サイクルで実測確認が必要。`last_result.json` の新項目確認は1サイクル実行後に実施予定。OpenAI API を使う実通信確認はユーザー許可待ち。
- メモ: `fetch_market_structure` 単体テストで `missing_fields=[]`、`oi_value`・`oi_change_pct`・orderbook件数は取得できた。

- 日時: 2026-03-10 15:15 JST
- 実施内容: 打ち合わせシートに、今回のブランチ評価として「実用性はかなり上がったが、精度の大幅向上はまだ運用確認待ち」という整理を追記した。期待しすぎず、それでも前進ははっきりしているという温度感でまとめた。
- 変更ファイル: `打ち合わせシート.md`, `運用資料/progress.md`
- 未解決事項: 実ログ確認後に、この見立てを「仮評価」から「実績評価」へ更新する必要がある。
- メモ: 打ち合わせシートの `updated` は `2026-03-10 15:13 JST` に更新済み。

- 日時: 2026-03-10 15:05 JST
- 実施内容: Obsidian の打ち合わせシートに、今回の「流動性・清算・OI・CVD・板情報対応版」実装の報告を追記した。内容は技術ログではなく、今の状況・現在の動向・今後のやるべきことに分けて、位置フィルター化の意味が追いやすい形へ整理した。
- 変更ファイル: `打ち合わせシート.md`, `運用資料/progress.md`
- 未解決事項: 打ち合わせシート上の今後のやるべきことは、次回の本番サイクル確認後に進捗反映が必要。
- メモ: Obsidian ノートの `updated` は `2026-03-10 14:57 JST` に更新済み。

- 日時: 2026-03-10 14:57 JST
- 実施内容: 無料API前提の「流動性・清算・板情報対応版」を実装した。MEXCベースの既存判定は維持しつつ、Binance公開APIを使う市場構造取得層、流動性・清算クラスター・OI/CVD・板の分析モジュール、位置フィルターによる `prelabel` / `location_risk` / `risk_flags`、通知・要約・CSV・バックテスト追従を追加した。清算は有料ヒートマップではなく、直近の清算イベント集計による近似実装にした。
- 変更ファイル: `main.py`, `config.py`, `requirements.txt`, `.env.example`, `README.md`, `backtest/runner.py`, `prompts/advice_prompt.md`, `prompts/summary_prompt.md`, `src/data/exchange_fetcher.py`, `src/data/provider_client/binance_market.py`, `src/analysis/liquidity.py`, `src/analysis/liquidation.py`, `src/analysis/oi_cvd.py`, `src/analysis/orderbook.py`, `src/analysis/position_risk.py`, `src/ai/advice.py`, `src/ai/summary.py`, `src/notification/trigger.py`, `src/storage/csv_logger.py`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: Binanceの清算イベント取得は `websocket-client` 導入後に本番環境で実データ確認が必要。OpenAI API を使う実通信確認は、許可をもらってから行う。
- メモ: 構文チェックは `.venv312/bin/python -m compileall .` で通過。位置判定モジュールの単体サンプル実行でも `prelabel` と `risk_flags` の出力を確認した。

- 日時: 2026-03-10 13:48 JST
- 実施内容: 他プロジェクトでも使い回せるよう、`Global_BOX` に打ち合わせノート共通テンプレートを新規作成し、`AGENTS_TEMPLATE.md` に打ち合わせノートの運用ルールを追加した。今後は各案件で保存先だけ決めれば、同じ型をそのまま導入できる状態にした。
- 変更ファイル: `Global_BOX/AGENTS_TEMPLATE.md`, `Global_BOX/打ち合わせノートテンプレート.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 既存プロジェクトへ反映する場合は、それぞれの `AGENTS.md` に保存先と参照ルールを追記する必要がある。
- メモ: テンプレート本体と運用ルールを分けて用意したので、ノートの見た目と運用基準の両方を使い回せる。

- 日時: 2026-03-10 13:46 JST
- 実施内容: ユーザーが打ち合わせノートの見出しとレイアウトを調整した内容を確認した。今後は `見立て` ではなく `現在の動向` を使い、`今の状況` → `現在の動向` → `今後のやるべきこと` の順で、読みやすさ優先の追記形式に合わせる方針を反映した。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: なし
- メモ: 打ち合わせノートは技術ログ化せず、短く状況判断しやすい形を優先する。

- 日時: 2026-03-10 13:36 JST
- 実施内容: Obsidian の打ち合わせシートに、現在の監視システムの状況と今後やるべきことを、専門ログではなく判断しやすい要約として追記した。あわせて `NEXT_TASK.md` も、直近の確認ポイントがより追いやすい表現へ整理した。
- 変更ファイル: `打ち合わせシート.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: AI 判定復帰とメール本文の読みやすさは、次回以降の定時実行結果を見て確認が必要。
- メモ: 打ち合わせシートには中長期の見立てを、`運用資料/` には実務ログを置く使い分けを維持した。

- 日時: 2026-03-10 13:05 JST
- 実施内容: `progress.md` の日時記録を、推測ではなく実時刻ベースで残す運用に修正した。今後は更新直前に `date` コマンドで取得した JST をそのまま記録する。あわせて、根拠が取れた直近エントリの時刻をファイル更新時刻ベースで補正した。
- 変更ファイル: `運用資料/progress.md`
- 未解決事項: すでに残っている古いエントリには概算時刻が混ざる可能性があるため、厳密性が必要な場合は都度ログ照合が必要。
- メモ: 以後は「手入力のだいたい時刻」を避け、必ず実時刻を入れる。

- 日時: 2026-03-10 12:13 JST
- 実施内容: メール本文が `bias=short` や `long=59 short=74` のような生データ中心で読みにくい問題に対応した。`src/ai/summary.py` のフォールバック本文を、数値の意味を日本語で説明する文章へ変更し、AI要約成功時も同じ方向性になるよう `prompts/summary_prompt.md` を調整した。
- 変更ファイル: `src/ai/summary.py`, `prompts/summary_prompt.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 次回メールで、AI要約成功時とフォールバック時の両方が十分読みやすいか確認が必要。
- メモ: 「数字を見せる」より「意味を伝える」を優先する方向へ調整。

- 日時: 2026-03-10 08:11 JST
- 実施内容: 08:05 実行で `ai_summary_error` が発生し、要約生成のみ `APITimeoutError` で失敗していることを確認したため、要約側だけ別タイムアウト設定を持てるよう修正した。`AI_SUMMARY_TIMEOUT_SEC=10` を追加し、判定AIは `AI_TIMEOUT_SEC=5` のまま、要約生成のみ 10 秒待つ構成へ変更した。
- 変更ファイル: `config.py`, `main.py`, `.env`, `.env.example`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 設定反映後の次回実行で `ai_summary_error` が再発するかは確認が必要。
- メモ: 判定AIと要約AIを同じ待ち時間にせず、要約だけ長めにしたので、全体の応答性を大きく落としにくい。

- 記録ルール: 以後、`日付` ではなく `日時` を `YYYY-MM-DD HH:MM JST` 形式で記録し、更新直前に `date` コマンドで取得した実時刻を使う。

- 日時: 2026-03-10 07:53 JST
- 実施内容: 定時実行を 4時間ごとから 1時間ごとへ変更した。`.env` の `REPORT_TIMES` を毎時 `:05` 実行に更新し、常駐再起動で反映する前提にした。ユーザー観察として、2026-03-09 朝9時ごろのロングが理想タイミングだったという情報も踏まえ、短めの機会を逃しにくい運用へ寄せた。
- 変更ファイル: `.env`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 1時間運用で通知量が増えすぎないか、数サイクルの観察が必要。
- メモ: 15分足を使う判定ロジックに対して、1時間実行は 4時間実行より実戦に寄せた設定。

- 日時: 2026-03-10 07:48 JST
- 実施内容: `tools/start_monitor.sh` に実PID保存処理を追加し、`launchctl print` で取得した PID を `logs/runtime/monitor.pid` に書き込むよう修正した。修正反映のため常駐プロセスを再起動し、`monitor.pid=49076` と `launchd` 上の実PIDが一致することを確認した。
- 変更ファイル: `tools/start_monitor.sh`, `運用資料/README.md`, `運用資料/運用コマンドメモ.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 次回定時サイクル後に AI判定が復帰するかは引き続き確認が必要。
- メモ: PID ファイルは再起動時に同期される方式。手動で `launchctl` 操作だけ行った場合は、`tools/start_monitor.sh` を使う運用に寄せるとずれにくい。

- 日時: 2026-03-10 07:42 JST
- 実施内容: `tools/start_monitor.sh` で `launchd` 常駐プロセスを再起動し、最新の `.env` とコード変更を反映した。`launchctl print` で `com.afrog.btc-monitor` が `running`、PID `48843`、実行バイナリが `.venv312/bin/python` であることを確認した。あわせて `monitor.err` に新しいAIエラーは出ていないことも確認した。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: `logs/runtime/monitor.pid` は古い PID `37423` のままで、実プロセスPIDと一致していない。必要なら PID ファイル更新処理を別途追加する。
- メモ: `logs/heartbeat.txt` と `logs/last_result.json` の更新時刻はまだ前回サイクル時刻のままなので、次回定時実行後に AI判定復帰可否を確認する。

- 日時: 2026-03-10 07:38 JST
- 実施内容: ChatGPT API の実接続テストを実施し、`.venv312` から `gpt-4o-mini` へ正常応答 `OK` を確認した。これにより API キー不正や接続不能ではないことを確認できたため、AI判定エラーの主因を `.env` の `AI_TIMEOUT_SEC=1` / `AI_RETRY_COUNT=1` と判断し、`AI_TIMEOUT_SEC=5`、`AI_RETRY_COUNT=3` に戻した。
- 変更ファイル: `.env`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 設定変更後の常駐サイクルで `ai_error` が解消するかは次回実行結果の確認が必要。
- メモ: ChatGPT API 実接続テストはユーザー許可のうえで実施。最小限の疎通確認のみで、本番ロジック全体の実行までは行っていない。

- 日時: 2026-03-10 07:20 JST
- 実施内容: AI判定エラーを調査した。`logs/last_result.json` では 2026-03-10 05:05 JST 時点の `ai_advice=null` と `reason_for_notification=["confidence_jump","ai_error"]` を確認。設定も点検し、`.env` の `AI_TIMEOUT_SEC=1`・`AI_RETRY_COUNT=1` が原因候補として強いと判断した。あわせて、AI例外が握りつぶされて詳細不明になる問題を改善し、`src/ai/advice.py` と `src/ai/summary.py` に失敗理由を `logs/errors/` へ保存するログ出力を追加した。
- 変更ファイル: `src/ai/advice.py`, `src/ai/summary.py`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 実際の OpenAI 応答失敗理由は、次回サイクル実行後に新設ログを確認するまで確定しない。設定上はタイムアウト1秒が最有力。
- メモ: APIキー自体は設定済み。常駐実行は `.venv312/bin/python` を使っており、そこで `openai 2.26.0` は導入済み。今回こちらから ChatGPT API 実行テストはしていない。

- 日時: 2026-03-10 00:20 JST
- 実施内容: 通知設定を「気づき重視」に調整した。`CONFIDENCE_LONG_MIN=60`、`CONFIDENCE_SHORT_MIN=65`、`CONFIDENCE_ALERT_CHANGE=7`、`ALERT_COOLDOWN_MINUTES=30` に変更し、通知が少し早めに来るようにした。あわせて記録ファイルを整理し、この案件で今必要な情報だけ残す形へ簡素化した。`launchd` 再起動後、常駐プロセスが新しい PID で動作していることも確認した。さらに、状態確認・ログ確認・再起動・停止・自動起動確認をまとめた運用メモを新規作成し、資料類を `運用資料/` に集約した。
- 変更ファイル: `.env`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`, `運用資料/運用コマンドメモ.md`, `運用資料/README.md`, `運用資料/ログ検証と改善運用ガイド.md`
- 未解決事項: 変更後の実際の通知頻度はまだ未確認。次回以降の `last_notified.json` と通知メールの増え方を見て微調整が必要な可能性がある。
- メモ: この通知は「売買サイン」ではなく「考えるきっかけ」を目的にした軽め設定。通知が増えすぎる場合は、まず `CONFIDENCE_ALERT_CHANGE` を 7 から 8 か 9 へ戻すと調整しやすい。
