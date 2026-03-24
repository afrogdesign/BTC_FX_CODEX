# NEXT TASK TRACKER

更新日: 2026-03-24 12:53 JST
運用メモ: このファイルを AI の日常入口にする。実行履歴は `progress.md` に記録し、ここには「次の判断に必要な情報」だけを残す。
補足: フェーズや大型節目の確認が必要になったときだけ [開発ロードマップ.md](開発ロードマップ.md) を開く。

## 現在の状況
- 開発ブランチ `Ver02.3` で、評価ロジック再調整を実装済みです。
- 今回入れた主変更は、breakout 判定修正、score / confidence / setup / position_risk / signal_tier の再調整、backtest の `ready` 限定 fill ロジック追加です。
- 追加テストは通っています。実施済み確認は `compileall`、`tests.test_funding_and_signal`、`tests.test_eval_rebalance`、`tests.test_notification_trigger`、`tests.test_summary_format`、`tests.test_phase1_activation`、`tests.test_phase1_trade_plans` です。
- `tmp/backtest/comparison_summary.csv` と `tmp/backtest_extended/comparison_summary.csv` は再生成済みで、標準区間・拡張区間の両方で `baseline / rebalanced` の差分が確認できています。
- `run_cycle()` は通知送信なし・AIスタブ化の安全モードで 1 回実行し、正常終了を確認しました。
- `main.py` 実行環境の復旧も完了しています。Python 3.12 の再導入、`.venv312` のリンク修正、依存の再インストールまで済んでいます。
- `Ver02.3` は commit `87fa154` で整理済み、`origin/Ver02.3` へ push 済みです。PR は `#1` を作成しました。
- 開発用 `iMac 2019` では `com.afrog.btc-monitor` を比較観測用として起動済みです。`.env` は `SYSTEM_LABEL=Ver02.3-OBS`、`DRYRUN_MODE=false`、Ver02.3 閾値へ同期済みで、`launchd` 上は `state = running` を確認しました。
- backtest レビュー指摘 3 件を反映しました。主内容は「ready の signal bar fill」「方向別 trigger」「baseline の旧 breakout / fill 近似復元」です。
- 人向け資料として `運用資料/reports/Ver02.3のレポート/Ver02.3_評価システム解説.html`、`運用資料/reports/Ver02.3のレポート/Ver02.3_レビュー改善ループ解説.html`、`運用資料/reports/Ver02.3のレポート/Ver02.3_比較CSV解説.html` を整備しました。
- 本番は引き続き `MBP2020` の `com.afrog.btc-monitor-ver021` を観測対象にし、開発側は `btc_monitor` ローカルで Ver02.3 を進めます。
- `Ver02.3-OBS` は 2026-03-24 12:05 JST の定刻実行まで継続確認できました。`logs/heartbeat.txt` は 12:05 JST、`logs/last_result.json` は 12:05:00 JST へ更新され、`signal_id=20260324_030500`、`system_label=Ver02.3-OBS`、`system_mode_label=API/CLI` を確認しました。`launchd` 上も `com.afrog.btc-monitor` は `state = running` のままです。
- 同サイクルの `was_notified` は `False` で、実通知フラグは立っていません。`logs/runtime/monitor.out` は 0 byte のまま、`logs/runtime/monitor.err` は 3 月 9 日の LibreSSL 警告のみで、新しい実行エラーは見えていません。
- backtest comparison は MEXC 再取得で再生成しました。標準区間では `baseline` が `filled_trades=15 / avg_realized_rr=-0.2222 / profit_factor=0.697 / max_drawdown_rr=6.0`、`rebalanced` が `filled_trades=3 / avg_realized_rr=0.9626 / profit_factor=3.8877 / max_drawdown_rr=1.0` でした。
- 拡張区間 `tmp/backtest_extended/comparison_summary.csv` でも差が出ました。`baseline` は `filled_trades=45 / avg_realized_rr=0.1818 / profit_factor=1.3408 / max_drawdown_rr=8.4452`、`rebalanced` は `filled_trades=4 / avg_realized_rr=0.4719 / profit_factor=1.9438 / max_drawdown_rr=1.0` でした。
- 旧メモにあった「今回の取得区間では差分は出ていない」は、再生成後の現状とは不一致です。現状は「取引数は減るが、rebalanced のほうが損益効率とドローダウンで優位」です。
- `baseline` の `filled_trades` が多い主因は、backtest 上で `watch` も約定扱いにしているためです。標準区間は 15 件中 13 件、拡張区間は 45 件中 42 件が `watch` 起点でした。`rebalanced` は `ready` 限定 fill なので、回数は減る一方で PF / DD 改善が見えやすくなっています。
- 状態変化では、拡張区間で `baseline` の `invalid -> rebalanced の watch` が 14 件、`invalid -> ready` が 1 件ありました。標準区間でも `invalid -> ready` が 1 件あり、以前は捨てていた場面の一部を監視・実行候補として拾えるようになっています。
- `運用資料/計画/改善設計図_v1_チャートパターン拡張.md` は正式設計へ更新しました。v1 は `chart_pattern_shadow` wrapper 配下の `shadow-only` 保存に限定し、AI / notify payload から分離、live 保存先は `last_result.json` と `signals/*.json`、backtest 側は `run_backtest()` の返り値 dict のみと固定しました。

## 次のタスク
1. `Ver02.3-OBS` の次回以降サイクルでも heartbeat / last_result 更新が継続するかを確認し、実メール受信有無は別途受信箱側で確認する。
2. 本番 `Ver02.1` で通知発生から 24 時間後評価までを 1 周確認し、Phase 0 の完了条件を満たす。
3. `chart_pattern_shadow` v1 を実装し、既存の `bias / prelabel / confidence / signal_tier / notify` を変えずに `last_result.json`、`signals/*.json`、`run_backtest()` の返り値へ載せる。

## ブロッカー
- 緊急ブロッカーはない。
- 実メール受信結果は、この端末からは未確認です。`last_result.json` 上は 2026-03-24 12:05 JST サイクルでも `was_notified=False` でした。
- `logs/runtime/monitor.out` は 0 byte のままで、通常ログからの追跡情報は弱いです。実害は未確認だが、必要なら出力設計の見直し余地があります。
- 2 台並行作業では、同じ記録ファイルを未 push のまま両方で触ると競合しやすいです。切替前の同期は引き続き必須です。

## 完了条件
- Ver02.3: 比較 CSV を踏まえて、`baseline / rebalanced` の差分内容を説明できる状態にする。
- Phase 0: 通知発生から 24 時間後評価までを本番で 1 周完了する。
- Phase 1: `primary_setup_status=ready` を本有効として、正式指標を実データで確認できる状態にする。
