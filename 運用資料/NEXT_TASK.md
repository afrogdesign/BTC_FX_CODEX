# NEXT TASK TRACKER

更新日: 2026-04-19 JST

運用メモ: AI の日常入口として使う。履歴は `履歴/progress.md` に残し、ここには次の判断に必要な情報だけを書く。

## 現在の状況

- 現行主流は `iMac 2019` 上の `ver02.5-v2`。日常の通知観測と品質判断はこの 1 本で進める。
- 最新コードは `ver02.5-v2` ブランチで再調整を継続中。`com.afrog.btc-monitor` の常設反映状況は次回デプロイ時に更新する。
- `MBP2020` の `Ver02.1` は停止・凍結済み。必要なときだけ archive と過去ログを参照する。
- 現在フェーズは `Phase 0` 本番観測中。主判断は `Phase 1` の本有効確認へ移している。
- 事後評価運用は `daily-sync` と `sync-ai-post-reviews` の 2 段構成。レビューの主軸は AI、必要なケースだけ `human_override` を使う。
- `sync-ai-post-reviews` の自動失敗は修正済み。`com.afrog.btc-ai-post-reviews` は `last exit code = 0` を確認した。
- `daily-sync` の最新レポートは `運用資料/reports/feedback_daily_sync_20260419.md`。完了データは 29 件、近似PF は 1.13、全体勝率は 75.9%。
- AI 事後評価の最新集計では `待つ判断に使えた=14件`、平均役立ち度は `3.60 / 5`。
- `ENTRY_OK + invalid` は改善候補として独立集計するように修正済み。最新レポートでは期間内 5 件、主理由は `rr_below_min=5件`。
- `ENTRY_OK + rr_below_min` の補助集計に見直し候補を追加済み。現時点の候補は `lower_liquidity_close` の単独加点再確認と、`execution<=20 かつ wait>=60` の本通知上位扱い抑制。
- `NEXT_TASK` 優先の再調整として、setup 用 TP は最低 `1.3R / 2.4R` で下支えするように変更済み。近い抵抗帯/支持帯だけで `rr_below_min` に落ちすぎない形へ寄せた。
- `lower_liquidity_close` / `upper_liquidity_close` の単独 close 加点を強め、`ENTRY_OK + invalid` に残りやすいケースを `RISKY_ENTRY` 側へ寄せた。
- `confidence_execution_shadow <= 20` かつ `confidence_wait_shadow >= 60` の本通知は、`high_main` / `strong_main` に上げず `normal_main` へ抑制するようにした。
- `phase1_v1_shadow` として TP1=1.3R / TP2=2.4R の比較用出口を追加済み。現行 `phase1_v0` は維持。
- `trade_execution_gate` を追加済み。`rr_below_min`、低 execution、高 wait pressure、データ品質不良、no_trade_flags ありは紙トレード候補から除外する。
- `paper_orders.csv` への紙トレード planned 記録を追加済み。対象は `phase1_active=true` かつ `trade_execution_gate=pass` のみ。2026-04-19 の最新レポート時点でも `paper_orders planned=0件` で、CSV 自体も未生成。
- AI 事後評価は `ai_post_review_v2` を追加済み。`review_action_class`、`review_priority`、`next_action` を保存し、旧レビューは互換維持のまま改善アクションへ推定補完する。
- `AI_ADVICE_CLI_COMMAND` / `AI_SUMMARY_CLI_COMMAND` の旧 repo パス参照は現行 repo の wrapper へ自動補正するようにした。`.env` も現行パスへ修正済み。
- 既存 AI レビュー 111 件は `backfill-ai-post-review-v2` で `review_action_class`、`review_priority`、`next_action`、`review_variant=ai_post_review_v2` を補完済み。退避は `logs/csv/user_reviews_backfill_20260419_013047.csv` と `logs/review/ai_post_reviews_backfill_20260419_013047/`。
- `daily-sync` レポートは AI 事後評価から `改善アクション` と `高優先の代表例` を出せる状態にした。`tp_eval=too_close` は `tune_exit / high` として扱える。2026-04-19 の最新レポートでは `tp_eval=too_close=10/15件` まで減少したが、主な signal_id は `20260414_140500`、`20260414_090500`、`20260414_020500` 周辺に残っている。
- `通知評価シート.md` は `最終レビュー保存` と `最終再生成` を分け、さらに `AI自動評価状態` を出すようにした。2026-04-19 時点の状態は `停止中`、`backlog=39件`、`最終AI評価=2026-04-15T18:36:50.508594Z`、`最終エラー=2026-04-17T18:35:03.067173Z`。
- `feedback_daily_sync_20260419.md` には `AI事後評価 health` を追加済み。`eligible=150`、`AI済み=111`、`backlog=39`、`created=0`、`request_failed=5` を日次で追える。
- `tests/test_codex_cli_wrapper.py` と `tests/test_log_feedback.py` の既知不一致は解消済み。両方 OK。
- `serve-review-form` は `com.afrog.btc-review-form` LaunchAgent で `state=running` を確認済み。
- Phase 1 へは閾値緩和で急がず、`ready=1件以上`、`phase1_active=true=5件以上`、`phase1_active=true=30件以上` の 3 段階で観測を進める。
- 直近の通知発生は `1日8〜9件` が続いており、全件追随より `main` 通知の代表例を優先して改善観測する前提で進める。

## 次のタスク

1. `sync-ai-post-reviews` の backlog `39件` が減るかを最優先で確認する。新規 AI レビューが現行 repo の wrapper 経由で再開し、`ai_post_review_v2` の項目付きで保存されるかを観測する。
2. 次回 `daily-sync` で `ready阻害理由` の `rr_below_min=22件`、`ENTRY_OK + invalid=5件`、`ENTRY_OK + rr_below_min=2件` がさらに減るかを確認する。
3. `tp_eval=too_close` は `10/15件` まで下がったため、次回は `20260414_*` 以降の新しい signal_id に同傾向が残るかを見て、TP 再調整の効き始めを継続確認する。
4. `execution<=20 かつ wait>=60` の抑制は、現行集計では `signal_tier=normal` に寄っている。次回は直近期間でも同条件が `high_main` / `strong_main` に再上昇しないかを確認する。
5. `paper_orders.csv` は未生成のままなので、まず `trade_execution_gate=pass` が出るかを観測する。planned が出たら `紙トレード準備` 欄で勝敗 proxy、TP1先行、timeout を確認する。
6. `MIN_RR_RATIO` はまだ緩めない。`trade_execution_gate=pass` が 0 件でも、今回の再調整後データは `rr_below_min` と `ENTRY_OK + invalid` が減っているため、もう 1 回観測してから判断する。

## ブロッカー

- 通知の増加ペースは `1日8〜9件`、AI新規処理は `1日4件` のため、backlog を解消するには日数がかかる。全件追随ではなく代表例優先の運用前提を崩さない。
- AI 事後評価は health 表示で `停止中` を検知できるようになったが、2026-04-19 時点では `backlog=39件` が残っている。Phase 判定を動かす前に、自動レビュー再開を確認する必要がある。

## 完了条件

- `daily-sync` と `sync-ai-post-reviews` の運用が継続して回る。
- レビュー保存から `review_form_state.json`、`user_reviews.csv`、要約更新までの流れを維持する。
- `Phase 1` の本有効確認を実データで追える状態を保つ。
- `ready=1件以上` で準備観測、`phase1_active=true=5件以上` で本有効観測レビュー、`phase1_active=true=30件以上` で Ver03 判断材料にする。
