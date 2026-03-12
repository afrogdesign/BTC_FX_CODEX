# NEXT TASK TRACKER

## 現在の状況
- 読む優先度は `👩‍⚖️秘書.md` → `運用資料/スレッド引き継ぎファイル.md` → `NEXT_TASK.md`。`progress.md` は履歴確認が必要なときだけ参照する。
- 常駐の正本は MBP2020。本番では Ver01 を比較基準、Ver02 を改善検証対象として並走運用する。
- MBA15 は開発・単発確認専用で、ローカル常駐 `com.afrog.btc-monitor` は停止済み。
- Ver02 本番は `/Users/marupro/CODEX/BTC_FX_CODEX_ver02/btc_monitor` / `com.afrog.btc-monitor-ver02`、Ver01 本番は `/Users/marupro/CODEX/BTC_FX_CODEX_ver01/btc_monitor` / `com.afrog.btc-monitor-ver01` で稼働中。
- Ver02 には、ログ活用基盤フェーズ1と改善設計書 v2.1 の Phase 0 拡張まで実装済み。
- 過去の Ver02 ログ `logs/csv/`、`logs/signals/`、`logs/cache/` は本番 Ver02 側へ移行済み。
- `signal_outcomes.csv` と `user_reviews.csv` はまだ未生成で、通知後 24 時間の本番確認待ち。
- 直近では `was_notified=True` は 0 件で、通知未発生の主因は `confidence` 未達と `bias=wait` に見えている。
- Global_BOX には Git 自動運用、GitHub 接続情報、`👩‍⚖️秘書.md` / `スレッド引き継ぎファイル.md` を含む共通運営体制を標準化済み。

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
- Ver02 本番の定時更新は、次の `heartbeat.txt` / `last_result.json` 実確認がまだ必要。
- `signal_outcomes.csv` と `user_reviews.csv` はまだ存在せず、`daily-sync` 初回本番確認には通知発生待ちが必要。
- Ver01 / Ver02 の runtime ログはまだ 0 byte のため、実運用中にログが必要十分に残るかは引き続き観察が必要。
- 強条件（🟡 / 🔥）は市場条件が厳しめに設定されているため、発火確認までに数サイクル必要。
- `signal_outcomes.csv` / `shadow_log.csv` の本格評価は、通知から24時間経過した実データがたまるまで待ちが必要。
- 実メールの最終見え方確認は、次の定時サイクル待ち。

## 完了条件
- Ver01 を安定運用しつつ、Ver02 の Phase 0 拡張ログ（`shadow_log.csv`, reason codes, data_quality_flag, review連携）が本番 MBP2020 上で実データ運用でき、次の Phase 1 着手判断に使える状態になること。
