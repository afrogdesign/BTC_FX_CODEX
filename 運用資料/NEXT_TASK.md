# NEXT TASK TRACKER

## 現在の状況
- 運営ルールの正本は `AGENTS.md` とし、文書の役割分担と入口順はそこに従う。秘書メモは軽い入口、大きな報告は打ち合わせノート、全体計画はロードマップと `運用資料/計画/` に置く。
- `スレッド引き継ぎファイル.md` は 2026-03-12 11:39 JST 時点の運用設計整理と Git 反映状況まで更新済み。
- `運用資料/` 直下は日常で使う資料だけに整理し、運用手順は `運用/`、参考資料とログ分析レポートは `参考資料/` に移した。
- 読む優先度は `👩‍⚖️秘書.md` → `運用資料/開発ロードマップ.md` → `NEXT_TASK.md`。ここで不足する場合だけ `運用資料/スレッド引き継ぎファイル.md` を開く。`progress.md` は履歴確認が必要なときだけ参照する。
- `運用資料/開発ロードマップ.md` と `運用資料/計画/` 配下を新設し、全体計画はそこで管理する運用へ切り替えた。
- 常駐の正本は MBP2020。本番では Ver01 を比較基準、Ver02 を改善検証対象として並走運用する。
- MBA15 は開発・単発確認専用で、ローカル常駐 `com.afrog.btc-monitor` は停止済み。
- Ver02 本番は `/Users/marupro/CODEX/BTC_FX_CODEX_ver02/btc_monitor` / `com.afrog.btc-monitor-ver02`、Ver01 本番は `/Users/marupro/CODEX/BTC_FX_CODEX_ver01/btc_monitor` / `com.afrog.btc-monitor-ver01` で稼働中。
- 2026-03-12 10:44 JST に MBP2020 実機へ SSH 接続して再確認し、Ver01 / Ver02 とも `state = running`、Ver01 `pid=91182`、Ver02 `pid=98787` を確認した。`heartbeat.txt` は両系統とも `2026-03-12 10:05:00 JST`、`last_result.json` は Ver01 `10:05:15 JST`、Ver02 `10:05:24 JST` 更新で、定時サイクル更新確認は完了した。
- 現在の版位置づけは `Ver02.x` で、`Phase 0` 実運用確認中。次の大型節目は `Ver03`。
- `Ver03` は、`Phase 0` の通知後フロー一周完了と `Phase 1` 中核導入を両方満たしたときに昇格する。
- 過去の Ver02 ログ `logs/csv/`、`logs/signals/`、`logs/cache/` は本番 Ver02 側へ移行済み。
- `signal_outcomes.csv` と `user_reviews.csv` はまだ未生成で、通知後 24 時間の本番確認待ち。
- 直近の本番最新データでは、Ver01 は `bias=wait`・`confidence=30`・`signal_id=None`、Ver02 は `signal_id=20260312_010500`・`was_notified=False`・`bias=long`・`confidence=0` で、通知済みシグナルはまだ確認できていない。

## 次のタスク
- 1. 次の通知発生サイクルを確認し、Ver02 の `trades.csv` と `logs/signals/*.json` に `was_notified=True` と `notify_reason_codes` が実データで入るか確認する。
- 2. 通知が 1 件でも発生したら、Ver01 / Ver02 の通知メール件名・本文・`notify_reason_codes`・runtime ログが混線していないか確認する。
- 3. 最初の通知から 24 時間経過後に、本番 Ver02 環境で `./.venv312_prod/bin/python tools/log_feedback.py daily-sync` を実行し、`signal_outcomes.csv`、`shadow_log.csv`、`📝通知レビュー.md` の初回本番更新を確認する。
- 4. `📝通知レビュー.md` に 1 件以上 `actual_move_driver` を入れて `review_status=done` にし、`daily-sync` または `import-reviews` 後に `logic_validated` が `user_reviews.csv` / `shadow_log.csv` へ正しく反映されるか確認する。
- 5. 通知待ちと並行して、`src/trade/position_sizing.py` と `src/trade/exit_manager.py` の入出力定義、追加設定値、ログ保存項目を固める。
- 6. `Ver03` 昇格条件に照らして、`Phase 0` と `Phase 1` のどちらが未充足かを `運用資料/計画/フェーズ別計画_Phase0-1.md` で定期確認する。

## ブロッカー
- 現在は通知済みシグナルが 0 件のため、`daily-sync` 初回本番確認と `logic_validated` 実データ確認は待ち状態。
- 通知が止まっている直接原因は、現時点の実データでは Ver01 `bias=wait`、Ver02 `was_notified=False` / `confidence=0` で、しきい値未達の可能性が高い。
- `signal_outcomes.csv` と `user_reviews.csv` はまだ存在せず、`daily-sync` 初回本番確認には通知発生待ちが必要。
- Ver01 / Ver02 の runtime ログはまだ 0 byte のため、実運用中にログが必要十分に残るかは引き続き観察が必要。
- 強条件（🟡 / 🔥）は市場条件が厳しめに設定されているため、発火確認までに数サイクル必要。
- `signal_outcomes.csv` / `shadow_log.csv` の本格評価は、通知から24時間経過した実データがたまるまで待ちが必要。
- `Phase 1` の中核実装はまだ未着手で、`Ver03` 昇格には通知後フロー確認だけでなく損益管理モジュール導入も必要。

## 完了条件
- Ver01 を比較基準として維持しつつ、Ver02 の `Phase 0` 通知後フローが本番で一周完了し、あわせて `Phase 1` 中核導入の着手条件と設計入口が固まっていること。
