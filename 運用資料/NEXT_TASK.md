# NEXT TASK TRACKER

更新日: 2026-03-24 13:40 JST
運用メモ: このファイルを AI の日常入口にする。実行履歴は `progress.md` に記録し、ここには「次の判断に必要な情報」だけを残す。
補足: フェーズや大型節目の確認が必要になったときだけ [開発ロードマップ.md](開発ロードマップ.md) を開く。

## 現在の状況
- `Ver02.3` は、評価ロジック再調整、backtest の `ready` 限定 fill、比較説明資料、`chart_pattern_shadow` v1 実装まで反映済みです。
- 比較 backtest は再生成済みで、標準区間・拡張区間の両方で `rebalanced` が取引数を絞る代わりに PF と DD で優位でした。主因は `baseline` が `watch` も約定扱いにしている点です。
- `chart_pattern_shadow` は `shadow-only` で実装済みです。`main.py` では AI / notify / summary payload と分離し、`last_result.json` と `signals/*.json` へだけ保存する設計です。backtest 側は `run_backtest()` の返り値 dict にだけ載せます。
- 実装確認は `.venv312` での unit test と `compileall` まで完了しています。実装コミットは `6b6ece0` (`chart_pattern_shadow の shadow 保存を実装`) です。
- 開発用 `iMac 2019` の `Ver02.3-OBS` は 2026-03-24 13:38 JST に再起動し、`com.afrog.btc-monitor` は新 PID `68086` で `running` を確認しました。
- 直前に確認できている定刻実行は 2026-03-24 13:05 JST サイクルです。この時点の `last_result.json` には `chart_pattern_shadow` は未保存で、常駐再起動前の出力でした。
- 本番観測対象は引き続き `MBP2020` の `com.afrog.btc-monitor-ver021`、開発観測対象は `iMac 2019` の `Ver02.3-OBS` です。

## 次のタスク
1. `Ver02.3-OBS` の次回以降サイクルでも heartbeat / last_result 更新が継続するかを確認し、実メール受信有無は別途受信箱側で確認する。
2. 次回の `Ver02.3-OBS` 定刻実行で `chart_pattern_shadow` が `last_result.json` と `signals/*.json` に保存されるかを確認する。
3. 本番 `Ver02.1` で通知発生から 24 時間後評価までを 1 周確認し、Phase 0 の完了条件を満たす。

## ブロッカー
- 緊急ブロッカーはない。
- 実メール受信結果は、この端末からは未確認です。直近確認済みの `last_result.json` は 2026-03-24 13:05 JST サイクルのものでした。
- `logs/runtime/monitor.out` は 0 byte のままで、通常ログからの追跡情報は弱いです。実害は未確認だが、必要なら出力設計の見直し余地があります。
- `chart_pattern_shadow` はコード実装と常駐再起動までは完了したが、再起動後の定刻実行での live JSON 出力確認はまだです。
- 2 台並行作業では、同じ記録ファイルを未 push のまま両方で触ると競合しやすいです。切替前の同期は引き続き必須です。

## 完了条件
- Ver02.3: 比較 CSV を踏まえて、`baseline / rebalanced` の差分内容を説明できる状態にする。
- Phase 0: 通知発生から 24 時間後評価までを本番で 1 周完了する。
- Phase 1: `primary_setup_status=ready` を本有効として、正式指標を実データで確認できる状態にする。
