# NEXT TASK TRACKER

## 現在の状況
- MEXCベースの既存判定に、Binance公開APIを使う市場構造取得と位置フィルター層を追加済み。
- `prelabel`、`location_risk`、`risk_flags`、流動性・清算・OI/CVD・板の各項目を result payload に追加済み。
- `ver02` は「流動性・清算・板情報を追加した版」を表す正式ブランチ名として扱う。
- 通知、要約、CSVログ、バックテストも新しい位置判定に追従済み。
- 清算は有料ヒートマップではなく、直近清算イベントの集計による近似実装。
- OpenAI API を使う手動 `run_cycle` は実施済み（`WAIT_FOR_SWEEP` 応答を確認）。
- Ver01（`main`）は MBP2020 へ本番配備済み。launchd ラベル `com.afrog.btc-monitor-ver01` で常駐起動中。
- 件名識別用に `SYSTEM_LABEL` を導入し、Ver01/Ver02 を件名で判別できる状態にした。
- 打ち合わせシートへも、件名識別対応の最新状況を反映済み。
- Ver02（ローカル）のAI待ち時間は 2 倍設定へ変更済み（`AI_TIMEOUT_SEC=10`, `AI_SUMMARY_TIMEOUT_SEC=20`）。
- ただし、現在 Ver02 は常駐停止中のため、設定反映は次回起動時に有効。
- Ver01 も待ち時間を同値（10秒/20秒）へ反映し、`launchd` 再起動で適用済み。
- Ver02 コードでは、Binance 清算イベントを `logs/cache/` に蓄積して次サイクルへ引き継ぐ実装を追加済み。
- Ver02 の保存ブランチとして `ver02` を作成済み。旧名 `流動性・清算・板情報対応版` は廃止予定。
- ブランチ運用ルールは `運用資料/README.md` に明記済み。
- 旧本番パス `/Users/marupro/BTC_FX_CODEX_ver01` は削除済み。現在の本番配置は `~/CODEX` 配下に統一済み。
- ローカルの不要常駐 `com.afrog.btc-monitor` は停止済み（LaunchAgentは `.disabled` 化）。
- 方針として、Ver01 の開発は一旦区切り、以後は Ver02 の改善へ注力する。

## 次のタスク
- 1. Ver01 は運用監視として、`logs/last_result.json` と `logs/runtime/monitor.err` の継続更新だけ確認する。
- 2. Ver02 で位置フィルターが強すぎるか弱すぎるか、`location_risk` と `risk_flags` を数サイクル分観察して閾値を調整する。
- 3. Ver02 の清算イベント蓄積（`logs/cache`）が実運用で有効かを確認し、必要なら保持秒数・件数を再調整する。

## 完了条件
- Ver01 を安定運用しつつ、Ver02 の調整項目をログ根拠で詰められる状態になること。
