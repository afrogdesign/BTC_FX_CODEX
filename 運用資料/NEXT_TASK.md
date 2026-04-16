# NEXT TASK TRACKER

更新日: 2026-04-17 01:10 JST

運用メモ: AI の日常入口として使う。履歴は `履歴/progress.md` に残し、ここには次の判断に必要な情報だけを書く。

## 現在の状況

- 現行主流は `iMac 2019` 上の `ver02.5-v1`。日常の通知観測と品質判断はこの 1 本で進める。
- 最新コードは `ver02.5-v1` / `ac4b451` まで Push 済みで、`com.afrog.btc-monitor` へデプロイ済み。`launchctl` では `state=running`、PID `20830` を確認済み。
- `MBP2020` の `Ver02.1` は停止・凍結済み。必要なときだけ archive と過去ログを参照する。
- 現在フェーズは `Phase 0` 本番観測中。主判断は `Phase 1` の本有効確認へ移している。
- 事後評価運用は `daily-sync` と `sync-ai-post-reviews` の 2 段構成。レビューの主軸は AI、必要なケースだけ `human_override` を使う。
- `sync-ai-post-reviews` の自動失敗は修正済み。`com.afrog.btc-ai-post-reviews` は `last exit code = 0` を確認した。
- `daily-sync` の最新レポートは `運用資料/reports/feedback_daily_sync_20260417.md`。完了データは 37 件、近似PF は 0.97、全体勝率は 75.7%。
- AI 事後評価の最新集計では `待つ判断に使えた=15件`、平均役立ち度は `3.62 / 5`。
- `ENTRY_OK + invalid` は改善候補として独立集計するように修正済み。期間内 8 件の主理由は `rr_below_min=8件`。
- `ENTRY_OK + rr_below_min` の補助集計に見直し候補を追加済み。現時点の候補は `lower_liquidity_close` の単独加点再確認と、`execution<=20 かつ wait>=60` の本通知上位扱い抑制。
- `phase1_v1_shadow` として TP1=1.3R / TP2=2.4R の比較用出口を追加済み。現行 `phase1_v0` は維持。
- `trade_execution_gate` を追加済み。`rr_below_min`、低 execution、高 wait pressure、データ品質不良、no_trade_flags ありは紙トレード候補から除外する。
- `paper_orders.csv` への紙トレード planned 記録を追加済み。対象は `phase1_active=true` かつ `trade_execution_gate=pass` のみ。2026-04-17 の最新レポート時点では `paper_orders planned=0件`。
- `tests/test_codex_cli_wrapper.py` と `tests/test_log_feedback.py` の既知不一致は解消済み。両方 OK。
- `serve-review-form` は `com.afrog.btc-review-form` LaunchAgent で `state=running` を確認済み。
- Phase 1 へは閾値緩和で急がず、`ready=1件以上`、`phase1_active=true=5件以上`、`phase1_active=true=30件以上` の 3 段階で観測を進める。
- 直近の通知発生は `1日8〜9件` が続いており、全件追随より `main` 通知の代表例を優先して改善観測する前提で進める。

## 次のタスク

1. `daily-sync` の最新結果どおり `primary_setup_status=ready=0` と `phase1_active=true=0` が続いているため、`Phase 1` 本有効待ちを維持しつつ通知観測を継続する。
2. `ver02.5-v1` デプロイ後の新規ログで、`phase1_v1_shadow` が `tp_eval=too_close` の改善候補になっているか観測する。
3. `paper_orders.csv` に planned が出たら、daily-sync の `紙トレード準備` 欄で勝敗 proxy、TP1先行、timeout を確認する。
4. `MIN_RR_RATIO` はまだ緩めない。`trade_execution_gate=pass` が少なすぎる場合も、先に TP/entry 条件の実データを見てから判断する。

## ブロッカー

- 通知の増加ペースは `1日8〜9件`、AI新規処理は `1日4件` のため、backlog を解消するには日数がかかる。全件追随ではなく代表例優先の運用前提を崩さない。

## 完了条件

- `daily-sync` と `sync-ai-post-reviews` の運用が継続して回る。
- レビュー保存から `review_form_state.json`、`user_reviews.csv`、要約更新までの流れを維持する。
- `Phase 1` の本有効確認を実データで追える状態を保つ。
- `ready=1件以上` で準備観測、`phase1_active=true=5件以上` で本有効観測レビュー、`phase1_active=true=30件以上` で Ver03 判断材料にする。
