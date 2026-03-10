# NEXT TASK TRACKER

## 現在の状況
- 他AI評価用に、現行ロジックを実装ベースで整理した `運用資料/AI向けシステムロジック全体整理.md` を追加済み。
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
- 開発環境の常駐 `com.afrog.btc-monitor` は再起動済みで、最新コード反映後の `pid=54689` を確認済み。
- 打ち合わせノート参照先、ブランチ運用ルール、タグ運用ルール、Obsidian 側の `NEXT_TASK.md` リンク整備は完了済み。
- プロジェクト用 `AGENTS.md` は `btc_monitor/AGENTS.md` へ移動済み。

## 次のタスク
- 1. 次回の定時サイクル後に、`trades.csv` と `signals/*.json` に `top_positive_factors` / `prelabel_primary_reason` / `data_quality_flag` / `notify_reason_codes` / `suppress_reason_codes` が想定どおり入るか確認する。
- 2. 通知から24時間経過したシグナルが出た段階で `./.venv312/bin/python tools/log_feedback.py daily-sync` を実データで実行し、`signal_outcomes.csv`、`shadow_log.csv`、`📝通知レビュー.md` が正しく更新されるか確認する。
- 3. `📝通知レビュー.md` に 1 件以上 `actual_move_driver` 付きで手動レビューを入れ、`import-reviews` または `daily-sync` 後に `logic_validated` が期待どおり計算されるか確認する。
- 4. 他AI評価結果が来たら、`compute_scores()` / `evaluate_position_risk()` / `should_notify()` のどこを先に触るべきかを、今回追加した `shadow_log.csv` を根拠に切り分ける。
- 5. Phase 1 の着手として、`src/trade/position_sizing.py` と `src/trade/exit_manager.py` の paper trade 用モジュール設計を具体化し、実装順を決める。
- 6. 強条件（`strong_machine` / `strong_ai_confirmed`）が出た時に、件名バッジ（🟡 / 🔥）と通知理由（`signal_tier_upgraded`）が期待どおり動くか確認する。
- 7. Ver01 は運用監視として、`logs/last_result.json` と `logs/runtime/monitor.err` の継続更新だけ確認する。

## ブロッカー
- 現時点で明確なブロッカーはなし。
- 強条件（🟡 / 🔥）は市場条件が厳しめに設定されているため、発火確認までに数サイクル必要。
- `signal_outcomes.csv` / `shadow_log.csv` の本格評価は、通知から24時間経過した実データがたまるまで待ちが必要。
- 実メールの最終見え方確認は、次の定時サイクル待ち。

## 完了条件
- Ver01 を安定運用しつつ、Ver02 の Phase 0 拡張ログ（`shadow_log.csv`, reason codes, data_quality_flag, review連携）が実データで安定運用でき、次の Phase 1 着手判断に使える状態になること。
