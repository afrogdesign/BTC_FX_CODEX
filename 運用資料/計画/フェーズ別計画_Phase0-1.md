# フェーズ別計画 Phase0-1

更新日: 2026-03-13 05:04 JST

このファイルは、現在の実務に直結する `Phase 0` と `Phase 1` の計画をまとめた正本です。
`Phase 0` と `Phase 1` の実装判断は、まずこのファイルを見て行います。
Obsidian 側の `📝 改善設計書_v2.1_最終版.md` は参考資料であり、ここに書かれていない内容は未決定として扱います。

## 現在の前提

- 現在版は `Ver02.x`
- `Phase 0` は実装済み項目が多いが、通知後フローの本番確認がまだ一周していない
- `Phase 1` は `Phase 0` の通知待ちと並行で導入を進めている
- `Ver03` は `Phase 0` 一周完了と `Phase 1` 中核導入を両方満たしたときに名乗る
- 評価に使う最新ログの正本は MBP2020 本番環境とし、MBA15 ローカルは構造確認・単発確認用として扱う

## 旧設計書から引き継いだ主項目

### 採用済み

- `shadow_log.csv`
- `signal_outcomes.csv` / `user_reviews.csv`
- `notify_reason_codes` / `suppress_reason_codes`
- `data_quality_flag`
- `actual_move_driver` / `logic_validated`
- `Phase 1` の `position_sizing` / `exit_manager`
- strong tier でもサイズを増やさない方針

### 保留

- 連敗後の通常リスク復帰条件
- timeout / stop の厳密実測ログ
- `Phase 1` の実約定制御

### ここでは採用しない

- なし

## Phase 0

### 目的

- 今の Ver02 が「本当に測れているか」を本番実運用で確定する

### 実装済み

- `shadow_log.csv`
- `signal_outcomes.csv` / `user_reviews.csv` の処理基盤
- `notify_reason_codes` / `suppress_reason_codes`
- `data_quality_flag`
- `actual_move_driver` / `logic_validated`
- 週次・月次レポート基盤
- `signal_based` / `entry_ready_based` の事後評価基盤

### 部分実装

- 通知監査 A/B/C/D は集計基盤まであるが、本番通知ケースがまだ不足している
- `logic_validated` は自動計算実装済みだが、本番の手動レビュー反映確認は未完了

### 本番確認待ち

1. `was_notified=True` の本番ケース確認
2. `notify_reason_codes` の本番保存確認
3. 通知メール件名・本文と runtime ログの混線確認
4. 本番 Ver02 で `daily-sync` を 1 回完走
5. `📝通知レビュー.md` に `actual_move_driver` を入れ、`logic_validated` を反映
6. 2週間以上 / 50件以上 / regime 多様性 / 週次レポート2回正常生成の確認

### 未実装

- なし

### この段階でやらないこと

- 閾値調整
- 強条件の緩和
- 通知件数だけを理由にしたロジック変更

## Phase 1

### 目的

- エントリー後の損益管理を整え、資金毀損を抑える

### 正式な値と用語

- `signal_tier` の正式値は次の 3 つです
  - `normal`
  - `strong_machine`
  - `strong_ai_confirmed`
- 計画上の canonical は上の 3 値です
- 旧表現の `strong` は正式値として使いません

補足:

- いまのコードの一部には `strong` 前提の条件が残っている可能性があります。
- その場合は「計画とコードの未同期」として扱い、今後の修正候補へ残します。

### 実装対象

- `src/trade/activation.py`
- `src/trade/position_sizing.py`
- `src/trade/exit_manager.py`
- `src/trade/performance_state.py`

### 実装済み

- `main.py` から primary setup 確定後に `Phase 1` 計画を result へ載せる流れ
- `config.py` の `PHASE1_*` 設定値
- `trades.csv` の `Phase 1` 用保存列
- `loss_streak` を `signal_outcomes.csv` + `trades.csv` の完了済み通知履歴から自動計算する構成
- `phase1_active` / `phase1_activation_reason`
- `shadow_log.csv` と週次レポートに `Phase 1` 計画列を流す接続
- サイズ計画の出力
  - `risk_percent_applied`
  - `planned_risk_usd`
  - `position_size_usd`
  - `max_size_capped`
  - `size_reduction_reasons`
- 出口計画の出力
  - `tp1_price`
  - `tp2_price`
  - `breakeven_after_tp1`
  - `trail_atr_multiplier`
  - `timeout_hours`
  - `exit_rule_version`

### 部分実装

- `exit_manager` は「計画値記録」まで実装済みで、実約定制御までは未実装
- `position_sizing` は連敗縮小・上限制御まで実装済みだが、復帰条件の状態管理までは未実装
- `expired` と `tp1_hit_first=false` は現時点では proxy 指標であり、厳密な timeout / stop 実測ではない

### 本番確認待ち

- MBP2020 本番へ反映後の `phase1_active` 実データ蓄積確認
- `phase1_active=true` の行だけで見た正式指標の最初の母数確認
- `Phase 1` のサイズ計画・出口計画が本番 `shadow_log.csv` へ自然に流れる確認

### 未実装

- 連敗後の通常リスク復帰条件の固定ルール
- timeout / stop の厳密実測ログ
- 分割利確・建値移動・トレイリングの実約定制御
- `Phase 0` 期間との損失分布比較レポート

### 現在の正式仕様

#### `phase1_active` の有効条件

- `primary_setup_side` が `long` または `short`
- `primary_setup_status` は `ready` のときだけ本有効
- `watch` は参考ログのみ
- `bias=wait` のときは本有効にしない
- `primary_stop_loss` と `primary_entry_mid` が両方ある
- `data_quality_flag=partial_missing` のときは本有効にしない

#### `loss_streak` の現行ルール

- 完了済みかつ通知済みの履歴だけを対象に連敗数を数える
- `loss` と `expired` を連敗として数える
- `win` と `breakeven` が出た時点で連敗を打ち切る
- 履歴が無いときだけ `PHASE1_LOSS_STREAK` を予備値として使う

#### サイズ管理の現行ルール

- 基本は固定リスク率ベース
- `loss_streak` が増えたときは減算方式でリスク率を下げる
- 最大サイズ上限を超えたら `max_position_size_capped=true`
- strong 系 tier でもサイズは増やさない

#### 出口管理の現行ルール

- `tp1_price` / `tp2_price` は RR 倍率から算出する
- `breakeven_after_tp1=true` は出口計画上のフラグとして保存する
- `trail_atr_multiplier` と `timeout_hours` は計画値として保存する
- ただし、これは「実際にその条件で自動決済する」意味ではなく、現時点では計画値記録です

### proxy 指標と未実測指標の境界

#### proxy 指標として使うもの

- `expired`
- `tp1_hit_first=false`

#### まだ実測していないもの

- `timeout_exit` の明示ログ
- `stop_exit` の明示ログ
- 同一足で TP と stop が両方触れたケースの順序確定

### Phase 1 で見る評価指標

- 正式評価は MBP2020 本番ログだけを使う
- 集計対象は `phase1_active=true` の行を優先し、暫定的に `primary_setup_status=ready` で補助確認してよい
- `watch` / `invalid` / `none` を混ぜたまま `Phase 1` 成績を判断しない

#### 当面の正式指標

1. 本有効件数 (`n`)
2. TP1 到達率
3. `tp1_hit_first=false` 率
4. `expired` 率
5. 平均 `risk_percent_applied`
6. `loss_streak_at_entry > 0` の行だけで見た平均 `risk_percent_applied`
7. `max_size_capped` 発生率

補足:

- 勝率だけで `Phase 1` を判断しません。
- 理由は、`Phase 1` の主目的が「勝率向上」より「資金毀損の抑制」にあるためです。

### 設計上はあるが現行では未採用の項目

- 連敗解消後に通常リスクへ戻す復帰条件
- timeout / stop の厳密観測に基づく評価
- 実約定制御まで含めた自動出口管理

この 3 点は、旧設計書では候補として有用ですが、現計画では未決定または未採用として扱います。
今後採用する場合は、先にこのファイルへ仕様を反映してから実装します。

### Phase 1 完了条件

#### 実装完了条件

- `activation`、`position_sizing`、`exit_manager`、`performance_state` がコードへ入っている
- サイズ計画と出口計画が JSON / CSV / `shadow_log.csv` へ保存される
- 連敗時リスク縮小がテストまたはコード読解で確認できる

#### 運用完了条件

- 本番ログに `Phase 1` 記録が載る
- 導入後の記録が 30 件以上たまる
- TP1 到達率、時間切れ撤退率、SL proxy が集計可能になる

## Ver03 との関係

- `Ver03` 昇格には、以下の両方が必要です
  - `Phase 0` の通知後フロー一周完了
  - `Phase 1` の中核導入完了

補足:

- `Phase 0` だけ終わっても `Ver03` には上げません。
- `Phase 1` だけ先に実装しても、本番通知後フローが未確認なら `Ver02.x` のまま扱います。

## AI向け共通ルール

- 通知未発生の間は、通知件数だけを理由に閾値調整しない
- 本番確認が必要な項目は「実装済み」と「完了」を分けて書く
- 旧設計書の具体案を採用するときは、先に repo 側計画書へ反映してから実装する
- 1 回の変更で複数フェーズをまたがない
- コードと計画書が食い違ったら、先に repo 側計画書を更新する
