# NEXT TASK TRACKER

## 現在の状況
- MEXCベースの既存判定に、Binance公開APIを使う市場構造取得と位置フィルター層を追加済み。
- `prelabel`、`location_risk`、`risk_flags`、流動性・清算・OI/CVD・板の各項目を result payload に追加済み。
- 通知、要約、CSVログ、バックテストも新しい位置判定に追従済み。
- 清算は有料ヒートマップではなく、直近清算イベントの集計による近似実装。
- OpenAI API を使う手動 `run_cycle` は実施済み（`WAIT_FOR_SWEEP` 応答を確認）。
- Ver01（`main`）は MBP2020 へ本番配備済み。launchd ラベル `com.afrog.btc-monitor-ver01` で常駐起動中。
- 旧本番パス `/Users/marupro/BTC_FX_CODEX_ver01` は削除済み。現在の本番配置は `~/CODEX` 配下に統一済み。
- ローカルの不要常駐 `com.afrog.btc-monitor` は停止済み（LaunchAgentは `.disabled` 化）。

## 次のタスク
- 1. MBP2020 側の Ver01 で、次回定時実行後に `logs/last_result.json` と `logs/runtime/monitor.err` を確認する。
- 2. Ver01本番で通知本文と AI判定が安定するか、数サイクル追跡する。
- 3. Ver02（ローカル開発）を再常駐する場合は、`com.afrog.btc-monitor-ver02` など別ラベルで起動する運用ルールを固定する。
- 4. 位置フィルターが強すぎるか弱すぎるか、`location_risk` と `risk_flags` を数サイクル分観察して閾値を調整する。
- 5. Binance WS 清算イベントが0件になる時間帯を減らすため、イベント蓄積（ローカル保存）を追加する。

## 完了条件
- 市場構造データが本番サイクルで安定取得でき、`prelabel` と通知文が実運用で使える粒度になっていること。
