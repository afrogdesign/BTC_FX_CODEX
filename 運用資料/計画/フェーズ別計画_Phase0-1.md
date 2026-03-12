# フェーズ別計画 Phase0-1

更新日: 2026-03-12 11:10 JST

このファイルは、現在の実務に直結する `Phase 0` と `Phase 1` の計画をまとめたものです。
直近の作業は、ここを見れば判断できる状態を目指します。

## 現在の前提

- 現在版は `Ver02.x`
- `Phase 0` は実装済み項目が多いが、通知後フローの本番確認がまだ一周していない
- `Phase 1` は `Phase 0` の通知待ちと並行で設計・導入準備を進める
- `Ver03` は `Phase 0` 一周完了と `Phase 1` 中核導入を両方満たしたときに名乗る

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
