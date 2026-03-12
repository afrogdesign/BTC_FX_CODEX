# NEXT TASK TRACKER

## 現在の状況
- 今後の常駐運用ルールを `運用資料/今後の運用ルール.md` に明文化し、「本番 MBP2020 を正本」「MBA15 は検証専用」とする方針を固定した。
- 既存の `README.md`、`ログ検証と改善運用ガイド.md`、`運用コマンドメモ.md` も、この運用ルールに合わせて参照関係と手順を整理済み。
- 他AI評価用に、現行ロジックを実装ベースで整理した `運用資料/AI向けシステムロジック全体整理.md` を追加済み。
- 次スレッドへ移るための引き継ぎファイル `運用資料/次スレッド引き継ぎプロンプト_2026-03-11.md` は、2026-03-11 13:17 JST 時点で実ファイル不在を確認したため、現状に合わせて復元済み。
- Ver01 は本番運用フェーズで、MBP2020 上の `com.afrog.btc-monitor-ver01` を継続監視する段階。
- Ver02 の現時点はタグ `v2.3` として固定予定の内容まで反映済み。
- Ver02 には ログ活用基盤 フェーズ1 に加え、改善設計書 v2.1 の Phase 0 拡張を反映し、`shadow_log.csv`、12h MFE / MAE、`tp1_hit_first`、`outcome`、`actual_move_driver`、`logic_validated`、通知監査 A/B/C/D の土台まで実装済み。
- Ver02 では、Funding を `raw / % / ラベル` で扱う構成に変更し、判定単位を `%` に統一した。
- Ver02 のサポレジは、内部計算用 `all zones` と表示用（近い順 / 強度順）を分離し、表示用は「サポートは下側中心 / レジスタンスは上側中心」に補正済み。
- Ver02 には `signal_tier`（normal / strong_machine / strong_ai_confirmed）と `signal_badge`（🟡/🔥）を実装した。
- 通知トリガーは `signal_tier_upgraded` に対応し、クールダウン中でも段階昇格時は通知できる構成にした。
- 件名と本文にはバッジ表示を追加し、Funding は `ほぼ中立 (+0.0037%)` 形式で出せるようにした。
- CSV/JSON には `funding_rate_raw`、`funding_rate_pct`、`funding_rate_label`、`signal_tier`、`signal_badge` に加え、観測ログ用の `signal_id`、通知状態、最寄りサポレジ列、因子 breakdown、`prelabel_primary_reason`、`data_quality_flag`、通知理由コード列を追加済み。
- 位置フィルター層（`prelabel` / `location_risk` / `risk_flags`）と、Binance 市場構造データの取得は稼働済み。
- 清算イベントは `logs/cache/` へ蓄積する近似実装で運用中。効果検証はこれから。
- 単体テスト（`unittest`）は 13 件で、現時点は全件成功。
- 開発環境の実行スケジュールは、`.env` / `config.py` / `.env.example` をそろえて「毎時 `:05` の 24回実行」に統一済み。
- 2026-03-12 08:44 JST 時点でも `trades.csv` の `was_notified=True` は 0 件で、`signal_outcomes.csv` と `user_reviews.csv` はまだ未生成。
- `shadow_log.csv` は `build-shadow-log` で再生成し、`signal_id` ありの 32 行まで最新化済み。
- 直近 24 サイクルの主な抑制理由は `confidence_below_long_min`、`bias_wait`、`confidence_below_short_min` で、最大 `confidence` は 39。
- 環境整理として、ローカル開発機は MBA15 (`AFROG-MBA15.local`) で、今後は Ver02 の常駐を置かず一時検証専用として扱う。本番常時実行ホストは MBP2020 (`AFROG-MBP2020.local` / `192.168.1.38`) で、Ver01 / Ver02 を並走させる前提。
- Ver02 を本番同時常駐させる場合は、Ver01 と別ディレクトリ・別 `launchd` ラベル・別 plist・別ログ出力先が必要。
- Global BOX は `CODEX/Global_BOX` を本体の共通参照ルートとし、Obsidian 側 `00_Global_BOX` のファイル群も含めてシンボリックリンク運用へ統一済み。
- MBP2020 実機確認により、Ver01 本番は `com.afrog.btc-monitor-ver01` / `pid=91182` / `/Users/marupro/CODEX/BTC_FX_CODEX_ver01/btc_monitor` で稼働中。
- Ver02 は MBP2020 へ `/Users/marupro/CODEX/BTC_FX_CODEX_ver02/btc_monitor` として配備済みで、`com.afrog.btc-monitor-ver02` / `pid=98787` で起動済み。
- ローカル開発環境の Ver02 常駐 `com.afrog.btc-monitor` は停止済みで、LaunchAgents からも退避済み。
- 開発環境で蓄積した Ver02 ログのうち、`logs/csv/`、`logs/signals/`、`logs/cache/` は本番 Ver02 側へ移行済み（`csv=2`, `signals=60`, `cache=1`）。
- 打ち合わせノート参照先、ブランチ運用ルール、タグ運用ルール、Obsidian 側の `NEXT_TASK.md` リンク整備は完了済み。
- プロジェクト用 `AGENTS.md` は `btc_monitor/AGENTS.md` へ移動済み。

## 次のタスク
- 1. 次の定時サイクル後に、MBP2020 上の Ver02 `logs/heartbeat.txt` と `logs/last_result.json` が更新されるか確認する。
- 2. Ver01 / Ver02 の両方が本番で同時稼働している状態で、通知メール、`notify_reason_codes`、runtime ログが混線していないか確認する。
- 3. 次の通知発生サイクルを確認し、Ver02 の `trades.csv` と `logs/signals/*.json` に `was_notified=True` と `notify_reason_codes` が実データで入るか確認する。
- 4. 最初の通知から 24 時間経過後に、本番 Ver02 環境で `./.venv312_prod/bin/python tools/log_feedback.py daily-sync` を実行し、`signal_outcomes.csv`、`shadow_log.csv`、`📝通知レビュー.md` の初回本番更新を確認する。
- 5. `📝通知レビュー.md` に 1 件以上 `actual_move_driver` を入れて `review_status=done` にし、`daily-sync` または `import-reviews` 後に `logic_validated` が `user_reviews.csv` / `shadow_log.csv` へ正しく反映されるか確認する。
- 6. 上記の実運用確認が一周した後で、Phase 1 の paper trade 用モジュール設計（`src/trade/position_sizing.py`, `src/trade/exit_manager.py`）へ進む。

## ブロッカー
- 現在は通知済みシグナルが 0 件のため、`daily-sync` 初回本番確認と `logic_validated` 実データ確認は待ち状態。
- 通知が止まっている直接原因は現時点ではロジック異常ではなく、`confidence` 未達と `bias=wait` が中心に見える。
- Ver02 本番は起動したばかりで、確認時点では `heartbeat.txt` / `last_result.json` がまだ未生成だった。次の定時サイクル確認が必要。
- `signal_outcomes.csv` と `user_reviews.csv` はまだ存在せず、`daily-sync` 初回本番確認には通知発生待ちが必要。
- Ver01 / Ver02 の runtime ログはまだ 0 byte のため、実運用中にログが必要十分に残るかは引き続き観察が必要。
- 強条件（🟡 / 🔥）は市場条件が厳しめに設定されているため、発火確認までに数サイクル必要。
- `signal_outcomes.csv` / `shadow_log.csv` の本格評価は、通知から24時間経過した実データがたまるまで待ちが必要。
- 実メールの最終見え方確認は、次の定時サイクル待ち。

## 完了条件
- Ver01 を安定運用しつつ、Ver02 の Phase 0 拡張ログ（`shadow_log.csv`, reason codes, data_quality_flag, review連携）が本番 MBP2020 上で実データ運用でき、次の Phase 1 着手判断に使える状態になること。
