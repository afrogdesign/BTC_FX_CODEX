# NEXT TASK TRACKER

更新日: 2026-04-15 JST

運用メモ: AI の日常入口として使う。履歴は `履歴/progress.md` に残し、ここには次の判断に必要な情報だけを書く。

## 現在の状況

- 現行主流は `iMac 2019` 上の `Ver02.4-v1`。日常の通知観測と品質判断はこの 1 本で進める。
- `MBP2020` の `Ver02.1` は停止・凍結済み。必要なときだけ archive と過去ログを参照する。
- 現在フェーズは `Phase 0` 本番観測中。主判断は `Phase 1` の本有効確認へ移している。
- 事後評価運用は `daily-sync` と `sync-ai-post-reviews` の 2 段構成。レビューの主軸は AI、必要なケースだけ `human_override` を使う。
- `sync-ai-post-reviews` の自動失敗は修正済み。`com.afrog.btc-ai-post-reviews` は `last exit code = 0` を確認した。
- `daily-sync` の最新レポートは `運用資料/reports/feedback_daily_sync_20260415.md`。完了データは 41 件、近似PF は 1.15、全体勝率は 75.6%。
- AI 事後評価の最新集計では `待つ判断に使えた=16件`、`入る判断に使えた=7件`、平均役立ち度は `3.78 / 5`。
- `ENTRY_OK + invalid` は改善候補として独立集計するように修正済み。期間内 11 件の主理由は `rr_below_min=11件`。
- Phase 1 へは閾値緩和で急がず、`ready=1件以上`、`phase1_active=true=5件以上`、`phase1_active=true=30件以上` の 3 段階で観測を進める。
- 直近の通知発生は `1日8〜9件` が続いており、全件追随より `main` 通知の代表例を優先して改善観測する前提で進める。

## 次のタスク

1. `daily-sync` の最新結果どおり `primary_setup_status=ready=0` と `phase1_active=true=0` が続いているため、`Phase 1` 本有効待ちを維持しつつ通知観測を継続する。
2. 次の実装論点は `ENTRY_OK + invalid` の発生源を `rr_below_min` 中心に絞り、`position_risk` と `confidence` 側の閾値見直し候補を詰める。`MIN_RR_RATIO` はまだ緩めない。
3. 次点の改善候補は `TP が近すぎるケースが多い`。最新レポートでは `tp_eval=too_close` が 9/14 件。
4. 直近12時間では `direction_execution_conflict=5件` が出ているため、ENTRY_OK整合性の次に速報監視側の扱いを確認する。

## ブロッカー

- フォーム保存は `serve-review-form` が前提。未起動だと localStorage にしか残らない。
- `tests/test_codex_cli_wrapper.py` と `tests/test_log_feedback.py` の既知不一致は別件として残っている。
- 通知の増加ペースは `1日8〜9件`、AI新規処理は `1日4件` のため、backlog を解消するには日数がかかる。全件追随ではなく代表例優先の運用前提を崩さない。

## 完了条件

- `daily-sync` と `sync-ai-post-reviews` の運用が継続して回る。
- レビュー保存から `review_form_state.json`、`user_reviews.csv`、要約更新までの流れを維持する。
- `Phase 1` の本有効確認を実データで追える状態を保つ。
- `ready=1件以上` で準備観測、`phase1_active=true=5件以上` で本有効観測レビュー、`phase1_active=true=30件以上` で Ver03 判断材料にする。
