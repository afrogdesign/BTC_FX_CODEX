# フェーズ別計画 Phase2-3

更新日: 2026-03-13 05:04 JST

このファイルは、`Phase 2` と `Phase 3` の実装判断を固定するための正本です。
ここでは「何を、どの順で、どこへ入れるか」を先に決め、AI が迷わず実装を進められる状態を目指します。
Obsidian 側の改善設計書は参考資料であり、このファイルに反映されるまで未決定として扱います。

## 現在の前提

- `Phase 2` と `Phase 3` は、`Phase 0` の実運用確認と `Phase 1` の中核導入が進んだあとに本格着手する
- 既にある基盤は流用し、未実装部分だけを段階的に足す
- `run_cycle()` が統合の中心であり、新機能は原則ここへつなぐ

## 旧設計書から引き継いだ主項目

### 採用予定

- `watch_prices`
- 価格乖離監視
- blackout
- 構造化 AI 審査出力
- `config_change_log`
- 因子相関分析
- prelabel 内部スコア化
- A/B 比較モード
- シナリオ分岐出力

### 保留

- paper execution

### ここでは採用しない

- なし

## Phase 2

### 目的

- 通知品質と危険回避を強化する

### 既にある土台

- 通知監査 A/B/C/D の集計基盤
- `shadow_log.csv`
- `notify_reason_codes`
- AI 助言呼び出しと本文生成呼び出しの分離

### 実装順

1. `watch_prices`
2. 価格乖離監視
3. blackout
4. 構造化 AI 審査出力
5. `config_change_log`

補足:

- 先に外部依存の少ない機能から入れます。
- `watch_prices` と価格乖離監視は、比較的単独で着手しやすい項目です。

### Phase 2-1 `watch_prices`

#### 目的

- 人間に「次に見る価格」と「今は何待ちか」をルールベースで返す

#### 着手条件

- `Phase 0` の通知後フロー一周は未完了でもよい
- `support_zones` / `resistance_zones` / `liquidity` / primary setup が result に載っていること

#### 外部依存

- なし

#### 入力元

- `bias`
- `current_price`
- `support_zones`
- `resistance_zones`
- `nearest_liquidity_above_price`
- `nearest_liquidity_below_price`
- `primary_setup_side`
- `primary_entry_mid`
- `primary_stop_loss`
- `warning_flags`
- `no_trade_flags`

#### 出力項目

- `wait_reasons_top3`
- `key_level_above`
- `key_level_below`
- `invalidation_price`
- `re_evaluation_price`
- `if_above`
- `if_below`

#### 保存先

- `result`
- `logs/signals/*.json`
- `logs/last_result.json`
- `trades.csv` の新列

#### `run_cycle()` への統合位置

- primary setup 確定後
- 件名・本文生成前

### Phase 2-2 価格乖離監視

#### 目的

- MEXC と Binance の価格差が大きいときに warning / no_trade を付ける

#### 着手条件

- 補助データ取得が安定していること
- `watch_prices` の仕様固定後でも前でも着手可

#### 外部依存

- あり
  - MEXC 価格
  - Binance 価格

#### 入力元

- MEXC の現在価格
- Binance の現在価格
- 過去 N 日分の価格差履歴

#### 出力項目

- `price_divergence_pct`
- `price_divergence_anomaly_score`
- `warning_flags` への `price_divergence`
- `warning_flags` への `price_divergence_anomaly`
- `no_trade_flags` への `price_divergence_critical`

#### 保存先

- `result`
- `logs/signals/*.json`
- `trades.csv` の新列
- `shadow_log.csv` へ必要列を転記

#### `run_cycle()` への統合位置

- 市場データ取得後
- `compute_scores()` の前

### Phase 2-3 blackout

#### 目的

- 重要なマクロイベント前後で通知品質悪化を避ける

#### 着手条件

- `Phase 0` の通知後フロー一周完了後
- 価格乖離監視の基礎ログが入った後を推奨

#### 外部依存

- あり
  - `data/economic_calendar.json` の手動管理ファイル

#### 入力元

- 現在 UTC 時刻
- `data/economic_calendar.json`

#### 出力項目

- `warning_flags` への `macro_event_approaching`
- `no_trade_flags` への `macro_event_blackout`
- `data_missing_fields` への `macro_calendar` 追加

#### 保存先

- `result`
- `logs/signals/*.json`
- `trades.csv`

#### `run_cycle()` への統合位置

- `compute_scores()` の前
- 最低でも通知判定の前に `warning_flags` / `no_trade_flags` へ反映されること

### Phase 2-4 構造化 AI 審査出力

#### 目的

- AI の自由文依存を減らし、事後分析しやすい構造化出力を保存する

#### 着手条件

- 既存の AI 助言 `api / cli` 切替が安定していること
- `Phase 0` の観測基盤が本番で一周していること

#### 外部依存

- あり
  - AI 実行系

#### 入力元

- `machine_payload`
- `qualitative_payload`

#### 出力項目

- `agreement`
- `override_prelabel`
- `confidence_delta`
- `additional_risk_flags`
- `disagreement_reason_code`

#### 保存先

- `result`
- `logs/signals/*.json`
- `trades.csv` の新列

#### `run_cycle()` への統合位置

- 既存の `request_ai_advice()` 呼び出しを置き換えるか、互換レイヤーを挟む
- `signal_tier` 判定の前に保存されていること

#### 実装方針

- 既存の自然文要約生成とは分離する
- まずは AI 審査を構造化し、本文生成は後段で別に扱う

### Phase 2-5 `config_change_log`

#### 目的

- 設定値変更と成績変化の因果関係を追えるようにする

#### 着手条件

- `Phase 2` の主要ログ列が固定していること

#### 外部依存

- なし

#### 入力元

- 手動更新された設定値
- 変更日時
- 変更理由

#### 出力項目

- `changed_at_jst`
- `changed_by`
- `target_key`
- `old_value`
- `new_value`
- `reason`
- `ticket_or_note`

#### 保存先

- `logs/config_change_log.csv`

#### `run_cycle()` への統合位置

- `run_cycle()` には直接統合しない
- 別コマンドまたは手動更新フローとして運用する

### Phase 2 完了条件

#### 実装完了条件

- `watch_prices` が保存・表示できる
- 価格乖離監視の列とフラグが入る
- blackout の判定とフラグ付与が入る
- AI 審査の構造化出力が保存される
- `config_change_log` の運用入口がある

#### 運用完了条件

- 通知監査 4 分類が集計可能
- blackout が正しく作動
- 価格乖離異常を live データで記録できる
- AI 審査出力と本文生成が分離された状態で live ログに残る
- ユーザーが次の監視価格を確認できる

## Phase 3

### 目的

- 蓄積ログを根拠にロジック自体を精密化する

### 実装順

1. 因子相関分析
2. A/B 比較モード
3. prelabel 内部スコア化
4. `build_setup()` 精密化
5. シナリオ分岐出力

補足:

- 先に分析と比較基盤を用意してから、ロジック変更へ進みます。

### Phase 3-1 因子相関分析

#### 目的

- 因子の冗長性や有効性を定量で見られるようにする

#### 着手条件

- `Phase 2` の安全装置が運用に乗っている
- 比較に使えるログ量がある

#### 外部依存

- なし

#### 入力元

- `shadow_log.csv`
- `signal_outcomes.csv`

#### 出力項目

- 因子別出現率
- 因子ペア同時出現率
- regime 別成績差
- 因子除外時の成績差

#### 保存先

- `運用資料/reports/` の分析レポート

#### `run_cycle()` への統合位置

- 直接統合しない
- 別ツールとして実装する

### Phase 3-2 A/B 比較モード

#### 目的

- 新旧ロジックを同時に記録して安全に比較する

#### 着手条件

- `config_change_log` が使える
- 分析レポートを読み分けられる状態になっている

#### 外部依存

- なし

#### 入力元

- 現行ロジックの result
- 比較対象ロジックの result

#### 出力項目

- `version_a_bias`
- `version_b_bias`
- `version_a_prelabel`
- `version_b_prelabel`
- 差分サマリ

#### 保存先

- 比較用 CSV
- `logs/signals/*.json` の比較節

#### `run_cycle()` への統合位置

- `result` 確定後
- 通知判定の前に比較結果を保持する

### Phase 3-3 prelabel 内部スコア化

#### 目的

- 4 分類表示は維持しつつ、内部では連続値で評価する

#### 着手条件

- 因子分析の結果がそろっている

#### 外部依存

- なし

#### 入力元

- 位置リスク関連の因子
- 補助市場データ

#### 出力項目

- `entry_quality_score`
- `sweep_risk_score`
- `chase_risk_score`
- `fake_break_risk_score`

#### 保存先

- `result`
- `logs/signals/*.json`
- `trades.csv` の新列

#### `run_cycle()` への統合位置

- `evaluate_position_risk()` の出力拡張として統合する

### Phase 3-4 `build_setup()` 精密化

#### 目的

- ready / watch / invalid の精度を上げる

#### 着手条件

- A/B 比較モードがある
- prelabel 内部スコアが使える

#### 外部依存

- なし

#### 入力元

- 現行 setup 生成結果
- 内部スコア
- 比較用パラメータ

#### 出力項目

- 改良版 setup 状態
- 差分理由コード

#### 保存先

- 比較用 JSON / CSV

#### `run_cycle()` への統合位置

- `build_setup()` の比較モードとして統合する

### Phase 3-5 シナリオ分岐出力

#### 目的

- 「この価格を超えたらどう見るか」をシナリオとして人間に渡す

#### 着手条件

- `watch_prices` が安定している
- A/B 比較なしでロジック変更しない前提が守れる

#### 外部依存

- あり
  - AI を使う場合あり

#### 入力元

- `watch_prices`
- `bias`
- setup 情報
- 直近の重要ゾーン

#### 出力項目

- 上抜け時シナリオ
- 下抜け時シナリオ
- 無効化シナリオ

#### 保存先

- `summary_body`
- `logs/signals/*.json`

#### `run_cycle()` への統合位置

- `watch_prices` と件名・本文生成の間

### Phase 3 完了条件

#### 実装完了条件

- 因子相関分析ツールが使える
- A/B 比較モードが使える
- prelabel 内部スコア化が導入されている
- `build_setup()` 精密化が比較可能な形で入っている
- シナリオ分岐出力がある

#### 運用完了条件

- 比較ログがたまり、改善判断に使える
- A/B 比較を根拠にしたロジック変更ができる

## 補足

- paper execution はこのファイルの対象外です
- paper execution は `Phase 4` の大型節目として別扱いにします

## AI向け共通ルール

- 通知未発生の間は、通知件数だけを理由に閾値調整しない
- 本番確認が必要な項目は「実装済み」と「完了」を分けて書く
- 旧設計書の具体案を採用するときは、先に repo 側計画書へ反映してから実装する
- 1 回の変更で複数フェーズをまたがない
- コードと計画書が食い違ったら、先に repo 側計画書を更新する
