# NEXT TASK TRACKER

更新日: 2026-04-22 02:40 JST

運用メモ: AI の日常入口として使う。履歴は `履歴/progress.md` に残し、ここには次の判断に必要な情報だけを書く。

## 現在の状況

- 現行主流は `iMac 2019` 上の `ver02.5-v4`。日常の通知観測と品質判断はこの 1 本で進める。
- 最新コードは `ver02.5-v4` ブランチで再調整を継続中。`com.afrog.btc-monitor` は現行 repo の `main.py` を実行しており、2026-04-22 02:09 JST 時点で再起動済み。
- `MBP2020` の `Ver02.1` は停止・凍結済み。必要なときだけ archive と過去ログを参照する。
- 現在フェーズは `Phase 0` 本番観測中。実用化のため `Phase 1A` 観測紙トレードを開始し、厳格な実行候補は `Phase 1B` として分離する。
- 事後評価運用は `daily-sync` と `sync-ai-post-reviews` の 2 段構成。レビューの主軸は AI、必要なケースだけ `human_override` を使う。
- `sync-ai-post-reviews` の自動失敗は修正済み。`com.afrog.btc-ai-post-reviews` は `last exit code = 0` を確認した。
- `daily-sync` の最新レポートは `運用資料/reports/feedback_daily_sync_20260422.md`。完了データは 28 件、近似PF は 0.86、全体勝率は 64.3%。
- AI 事後評価 health は `eligible=166`、`AI済み=123`、`backlog=43`、`created=0`、`request_failed=0`。レポート側でも直近 runtime の同期結果を拾うように修正済み。
- `phase1_observation_gate=pass` は 16 件。内訳は `direction_rr_learning=10件`、`setup_watch_learning=6件`。
- `ENTRY_OK + invalid` は整合補正によりレポート上 0 件へ解消した。`prelabel=ENTRY_OK` かつ `primary_setup_status=invalid` は最終出力で `RISKY_ENTRY` へ寄せる。
- `RISKY_ENTRY + rr_below_min` のうち `execution>=20` の近閾値候補だけを補助集計するようにした。現時点の再調整候補は `20260417_090500` の 1 件。
- `20260417_090500` は過去ログでは `rr_below_min` だが、signal snapshot を現行 `build_setup` で再計算すると `watch / entry_zone_not_reached / rr=1.30` になる。今の主論点は RR 閾値より `sweep_incomplete` 中の再発火条件と通知タイミング。
- `NEXT_TASK` 優先の再調整として、setup 用 TP は最低 `1.3R / 2.4R` で下支えするように変更済み。近い抵抗帯/支持帯だけで `rr_below_min` に落ちすぎない形へ寄せた。
- `lower_liquidity_close` / `upper_liquidity_close` の単独 close 加点を強め、`ENTRY_OK + invalid` に残りやすいケースを `RISKY_ENTRY` 側へ寄せた。
- `confidence_execution_shadow <= 20` かつ `confidence_wait_shadow >= 60` の本通知は、`high_main` / `strong_main` に上げず `normal_main` へ抑制するようにした。
- `phase1_v1_shadow` として TP1=1.3R / TP2=2.4R の比較用出口を追加済み。現行 `phase1_v0` は維持。
- `trade_execution_gate` を追加済み。`rr_below_min`、低 execution、高 wait pressure、データ品質不良、no_trade_flags ありは紙トレード候補から除外する。
- `paper_orders.csv` への紙トレード planned 記録を追加済み。対象は `phase1_active=true` かつ `trade_execution_gate=pass` のみ。2026-04-20 の最新レポート時点でも `paper_orders planned=0件` で、CSV 自体も未生成。
- AI 事後評価は `ai_post_review_v2` を追加済み。`review_action_class`、`review_priority`、`next_action` を保存し、旧レビューは互換維持のまま改善アクションへ推定補完する。
- `AI_ADVICE_CLI_COMMAND` / `AI_SUMMARY_CLI_COMMAND` の旧 repo パス参照は現行 repo の wrapper へ自動補正するようにした。`.env` も現行パスへ修正済み。
- 既存 AI レビュー 111 件は `backfill-ai-post-review-v2` で `review_action_class`、`review_priority`、`next_action`、`review_variant=ai_post_review_v2` を補完済み。退避は `logs/csv/user_reviews_backfill_20260419_013047.csv` と `logs/review/ai_post_reviews_backfill_20260419_013047/`。
- `daily-sync` レポートは AI 事後評価から `改善アクション` と `高優先の代表例` を出せる状態にした。`tp_eval=too_close` は `tune_exit / high` として扱える。2026-04-20 の最新レポートでは `tp_eval=too_close=8/14件`、高優先代表例は `20260418_110745`、`20260417_090500`、`20260414_140500`。
- `通知評価シート.md` は `最終レビュー保存` と `最終再生成` を分け、さらに `AI自動評価状態` を出すようにした。2026-04-20 時点の状態は `backlogあり`、`backlog=40件`、`最終AI評価=2026-04-20T05:07:43.352804Z`、`最終エラー=2026-04-19T18:40:01.705120Z`。
- `feedback_daily_sync_20260420.md` では `AI事後評価 health` が `eligible=159`、`AI済み=119`、`backlog=40`、`created=0`、`request_failed=0`。手動 `sync-ai-post-reviews` では 3 件作成し、失敗 0 で動作確認済み。
- `sync-ai-post-reviews` は CLI usage limit 時に API fallback を使えるようにした。連続失敗は `AI_POST_REVIEW_MAX_CONSECUTIVE_FAILURES=3` で停止し、定刻実行が backlog 全体を無駄に叩き続けない。
- `ver02.5-v4` では Phase 1 の実行 gate と観測 gate を分離した。`trade_execution_gate` は実行候補として維持し、`phase1_observation_gate` は悪い相場でも学習対象を拾う紙観測用として扱う。
- `Phase 1A` 用に `observation_paper_orders.csv` を追加した。`phase1_observation_gate=pass` を実行候補ではなく、方向・待機条件・仮想SL/TPの観測紙トレードとして保存する。既存ログから 322 件を backfill 済みで、最新 weekly 範囲では 16 件。
- PR レビューで見つかった `main.py` の未定義変数 `prelabel_info` 参照は `effective_prelabel` へ修正済み。対象テスト 72 件と `git diff --check` は OK、常駐 PID は再起動後 `76350`。
- 2026-04-22 レポートでは `trade_execution_gate=pass:0件` のまま。`paper_orders planned=0件` で、紙トレード開始条件はまだ未達。
- `tests/test_codex_cli_wrapper.py` と `tests/test_log_feedback.py` の既知不一致は解消済み。両方 OK。
- `serve-review-form` は `com.afrog.btc-review-form` LaunchAgent で `state=running` を確認済み。
- Phase 1B へは閾値緩和で急がず、`ready=1件以上`、`phase1_active=true=5件以上`、`phase1_active=true=30件以上` の 3 段階で観測を進める。Phase 1A は `phase1_observation_gate=pass` を使って即日開始する。
- 直近の通知発生は `1日8〜9件` が続いており、全件追随より `main` 通知の代表例を優先して改善観測する前提で進める。

## 次のタスク

1. 次回 `daily-sync` で `phase1_observation_gate=pass` が 16 件前後を維持するか、特に `direction_rr_learning` の近似PFと代表例を確認する。
2. `observation_paper_orders.csv` が既存ログから backfill され、次回サイクル以降も自然に増えるか確認する。
3. `RISKY_ENTRY + rr_below_min かつ execution>=20` の補助集計を見て、`20260417_090500` 系が増えるか単発で終わるかを確認する。
4. `20260417_090500` と同型の `sweep_incomplete` ケースに対し、RR 閾値を緩めるのではなく、再発火条件と通知タイミングを先に詰める。
5. `confidence_below_min=9件` は引き続き観測 gate でも除外したままにし、成績が改善しないかを継続確認する。
6. `sync-ai-post-reviews` は LaunchAgent 側で `request_failed=0` を維持できるか、backlog `43件` が自然減するかを確認する。
7. 次回定時サイクル後、`monitor.err` に `NameError` や `phase1_observation_gate` 周辺の例外が出ていないか確認する。

## ブロッカー

- 通知の増加ペースは `1日8〜9件`、AI新規処理は `1日4件` のため、backlog 解消には日数がかかる。全件追随ではなく代表例優先の運用前提を崩さない。
- `trade_execution_gate=pass` はまだ 0 件で、Phase 1B の本有効条件は未達。Phase 1A の観測紙トレードを実行候補と混同しない。

## 完了条件

- `daily-sync` と `sync-ai-post-reviews` の運用が継続して回る。
- レビュー保存から `review_form_state.json`、`user_reviews.csv`、要約更新までの流れを維持する。
- `Phase 1A` の観測紙トレードと `Phase 1B` の本有効確認を実データで分けて追える状態を保つ。
- `ready=1件以上` で準備観測、`phase1_active=true=5件以上` で本有効観測レビュー、`phase1_active=true=30件以上` で Ver03 判断材料にする。
