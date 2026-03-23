# NEXT TASK TRACKER

更新日: 2026-03-24 04:24 JST
運用メモ: このファイルを AI の日常入口にする。実行履歴は `progress.md` に記録し、ここには「次の判断に必要な情報」だけを残す。
補足: フェーズや大型節目の確認が必要になったときだけ [開発ロードマップ.md](開発ロードマップ.md) を開く。

## 現在の状況
- 開発ブランチ `Ver02.3` で、評価ロジック再調整を実装済みです。
- 今回入れた主変更は、breakout 判定修正、score / confidence / setup / position_risk / signal_tier の再調整、backtest の `ready` 限定 fill ロジック追加です。
- 追加テストは通っています。実施済み確認は `compileall`、`tests.test_funding_and_signal`、`tests.test_eval_rebalance`、`tests.test_notification_trigger`、`tests.test_summary_format`、`tests.test_phase1_activation`、`tests.test_phase1_trade_plans` です。
- `tmp/backtest/comparison_summary.csv` を作成し、`baseline / rebalanced` の比較出力までは確認済みです。ただし今回の取得区間では差分は出ていません。
- `run_cycle()` は通知送信なし・AIスタブ化の安全モードで 1 回実行し、正常終了を確認しました。
- `main.py` 実行環境の復旧も完了しています。Python 3.12 の再導入、`.venv312` のリンク修正、依存の再インストールまで済んでいます。
- `Ver02.3` は commit `87fa154` で整理済み、`origin/Ver02.3` へ push 済みです。PR は `#1` を作成しました。
- 開発用 `iMac 2019` では `com.afrog.btc-monitor` を観測用として起動済みです。`.env` は `SYSTEM_LABEL=Ver02.3-OBS`、`DRYRUN_MODE=true`、Ver02.3 閾値へ同期済みで、`launchd` 上は `state = running` を確認しました。
- 本番は引き続き `MBP2020` の `com.afrog.btc-monitor-ver021` を観測対象にし、開発側は `btc_monitor` ローカルで Ver02.3 を進めます。

## 次のタスク
1. 開発用 `iMac 2019` の `Ver02.3-OBS` が次回定刻実行で正常に 1 サイクル回るか、`monitor.out`、`monitor.err`、heartbeat を確認する。
2. `tmp/backtest/comparison_summary.csv` の結果を前提に、より長い取得区間や別期間で差分が出るか再確認する。
3. PR `#1` のレビュー観点を整理し、必要なら補足説明や追修正を入れる。

## ブロッカー
- 緊急ブロッカーはない。
- 比較 CSV は作成できたが、今回の取得区間では `baseline / rebalanced` の差が出ていません。差分確認には別区間の再検証が必要です。
- 開発用観測ジョブは起動済みですが、次回定刻実行前のため heartbeat 更新はまだ確認していません。
- 2 台並行作業では、同じ記録ファイルを未 push のまま両方で触ると競合しやすいです。切替前の同期は引き続き必須です。

## 完了条件
- Ver02.3: 比較 CSV を踏まえて、差分が出る区間を含む再検証か、差が出なかった理由の説明を残せる状態にする。
- Phase 0: 通知発生から 24 時間後評価までを本番で 1 周完了する。
- Phase 1: `primary_setup_status=ready` を本有効として、正式指標を実データで確認できる状態にする。
