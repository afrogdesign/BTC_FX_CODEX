# フェーズ別計画 Phase0-1

更新日: 2026-03-12 12:30 JST

このファイルは、現在の実務に直結する `Phase 0` と `Phase 1` の計画をまとめたものです。
直近の作業は、ここを見れば判断できる状態を目指します。

## 現在の前提

- 現在版は `Ver02.x`
- `Phase 0` は実装済み項目が多いが、通知後フローの本番確認がまだ一周していない
- `Phase 1` は `Phase 0` の通知待ちと並行で設計・導入準備を進める
- `Ver03` は `Phase 0` 一周完了と `Phase 1` 中核導入を両方満たしたときに名乗る
- 評価に使う最新ログの正本は MBP2020 本番環境とし、MBA15 ローカルは構造確認・単発確認用として扱う

## Phase 0

### 目的

- 今の Ver02 が「本当に測れているか」を本番実運用で確定する

### 既に入っているもの

- `shadow_log.csv`
- `signal_outcomes.csv` / `user_reviews.csv` の処理基盤
- `notify_reason_codes` / `suppress_reason_codes`
- `data_quality_flag`
- `actual_move_driver` / `logic_validated`
- 週次・月次レポート基盤

### 残確認

1. `was_notified=True` の本番ケース確認
2. `notify_reason_codes` の本番保存確認
3. 通知メール件名・本文と runtime ログの混線確認
4. 本番 Ver02 で `daily-sync` を 1 回完走
5. `📝通知レビュー.md` に `actual_move_driver` を入れ、`logic_validated` を反映
6. 2週間以上 / 50件以上 / regime 多様性 / 週次レポート2回正常生成の確認

### この段階でやらないこと

- 閾値調整
- 強条件の緩和
- 通知件数だけを理由にしたロジック変更

## Phase 1

### 目的

- エントリー後の損益管理を整え、資金毀損を抑える

### 実装対象

- `src/trade/position_sizing.py`
- `src/trade/exit_manager.py`

### 2026-03-12 時点の入口実装

- `position_sizing` と `exit_manager` の雛形モジュールは追加済み
- `main.py` から primary setup 確定後に Phase 1 計画を result へ載せる土台を追加済み
- `config.py` に `PHASE1_*` 設定値を追加済み
- `trades.csv` に Phase 1 用の保存列を追加済み
- `loss_streak` は `signal_outcomes.csv` + `trades.csv` の完了済み通知履歴から自動計算する構成へ接続済み
- `phase1_active` / `phase1_activation_reason` を追加し、`ready` と参考ログをコード上で分けられる状態にした
- `shadow_log.csv` と週次レポートに Phase 1 計画ログを流す接続も追加済み
- 未完了なのは、MBP2020 本番へ反映後の実データ確認、件数がたまった後の評価指標整理、timeout / stop 実測ログ化の要否判断

### Phase 1 を有効扱いにする条件

- まず前提として、`primary_setup_side` が `long` または `short` であること
- `primary_setup_status` は原則 `ready` を本有効、`watch` は参考ログのみとする
- `bias` が `wait` のときは Phase 1 を有効にしない
- `primary_stop_loss` と `primary_entry_mid` が両方あり、サイズ計算に必要な距離が正しく取れること
- `data_quality_flag` が `partial_missing` のときは本有効にせず、ログだけ残す
- `signal_tier=strong` でもサイズは増やさず、通常サイズのまま扱う
- `loss_streak` が増えたときはリスク縮小のみ許可し、拡大方向の調整はしない

補足:

- 当面は `ready` を「有効」、`watch` を「まだ発動しないが参考として残す」に分ける
- つまり次の実装段階では、Phase 1 計画は今まで通りログに残しつつ、実際の有効判定フラグは `primary_setup_status=ready` を中心に付ける方針にする

### Phase 1 で見る評価指標

- 前提:
  - 正式評価は MBP2020 本番ログだけを使う
  - 集計対象は、将来 `phase1_active=true` を付けた行、または当面は `primary_setup_status=ready` の行に絞る
  - `watch` / `invalid` / `none` を混ぜたまま Phase 1 成績を判断しない

- 最優先:
  - `tp1_hit_first`
  - `outcome`
  - `direction_outcome`
- 出口管理の確認:
  - TP1 到達率
  - `expired` 率
  - `tp1_hit_first=false` 率
  - `breakeven_after_tp1` の対象件数
- サイズ管理の確認:
  - 平均 `risk_percent_applied`
  - 平均 `planned_risk_usd`
  - 平均 `position_size_usd`
  - `max_size_capped` 発生率
  - 平均 `loss_streak_at_entry`
  - `loss_streak_at_entry > 0` の行だけで見た平均 `risk_percent_applied`
- 改善判断用:
  - `signal_based_MFE_24h` と `signal_based_MAE_24h`
  - `entry_ready_based_MFE_24h` と `entry_ready_based_MAE_24h`
  - `signal_tier` 別の勝率
  - `prelabel` 別の勝率

### 当面の正式指標

- Phase 1 の良し悪し判断は、当面は次の 7 指標を正本として見る
  1. 本有効件数 (`n`)
  2. TP1 到達率
  3. `tp1_hit_first=false` 率
  4. `expired` 率
  5. 平均 `risk_percent_applied`
  6. `loss_streak_at_entry > 0` の行だけで見た平均 `risk_percent_applied`
  7. `max_size_capped` 発生率

補足:

- 勝率だけで Phase 1 を判断しない
- 理由は、Phase 1 の主目的が「勝率を上げること」だけでなく、「資金毀損を抑えること」にあるため
- そのため、TP / stop proxy / expired proxy の出口比率と、実際にどれだけリスクを絞れたかを先に見る
- いまの `expired` は「12h timeout を直接観測した値」ではなく、現行ロジック上の暫定 proxy として扱う
- いまの `tp1_hit_first=false` も「SL が先だった可能性が高い」ことを見る proxy で、同一足で TP と stop が両方触れた曖昧ケースを含む

### 検証時の注意

- Phase 1 の実データ評価は、必ず MBP2020 本番環境の `trades.csv` / `shadow_log.csv` / `signal_outcomes.csv` を正本として行う
- ローカル MBA15 側の `btc_monitor` は停止済みなので、そこで見えるログは列追加や構造確認には使えても、現況判断の根拠にはしない
- したがって、件数・勝率・TP1 到達率などの正式判断は MBP2020 側でそろったデータだけを見る
- `time_out` 系の正式評価は、将来 `timeout_exit` を明示ログ化するまでは proxy 指標として扱う
- `stop` 系の正式評価も、将来より細かい約定順ログが入るまでは proxy 指標として扱う

### position_sizing の役割

- `account_balance`、`entry_price`、`stop_loss_price`、設定値からサイズを計算する
- 最大サイズ制限を適用する
- strong tier でもサイズを増やさない
- 連敗時リスク縮小ルールを適用する

### exit_manager の役割

- TP1 / TP2 を計算する
- TP1 到達後の建値移動条件を返す
- TP1 到達後のみ ATR トレイリングを有効にする
- 12h の時間切れ撤退条件を返す

### 追加して残すログ

- `risk_percent_applied`
- `planned_risk_usd`
- `position_size_usd`
- `max_size_capped`
- `size_reduction_reasons`
- `tp1_price`
- `tp2_price`
- `breakeven_after_tp1`
- `trail_atr_multiplier`
- `timeout_hours`
- `exit_rule_version`

### Phase 1 の進め方

1. 入出力仕様を固める
2. 独立モジュールとして実装する
3. `main.py` で primary setup 確定後に呼び出す
4. JSON / CSV 保存までつなぐ
5. テストと本番ログ確認を行う

### Phase 1 完了条件

- サイズ計画と出口計画が本番ログに残る
- 導入後の記録が 30 件以上たまる
- TP1 到達率、時間切れ撤退率、SL 到達率が集計可能
- 連敗時リスク縮小が実データまたはテストで確認できる

## Ver03 との関係

- `Ver03` 昇格には、以下の両方が必要
  - `Phase 0` の通知後フロー一周完了
  - `Phase 1` の中核導入完了

補足:

- `Phase 0` だけ終わっても `Ver03` には上げない
- `Phase 1` だけ先に実装しても、本番通知後フローが未確認なら `Ver02.x` のまま扱う
