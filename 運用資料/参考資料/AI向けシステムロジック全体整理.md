# BTC監視システム AI向けロジック全体整理

更新日: 2026-03-13 04:43 JST

## 目的

この文書は、`btc_monitor` の現行 `Ver02.x` 実装を、別の AI や新しい担当者が短時間でつかめるように整理したものです。
推測ではなく、現在のコードと運用資料に入っている事実を優先してまとめています。

補足:

- `bias` は売買の方向感です。`long` は上目線、`short` は下目線、`wait` は様子見です。
- `ATR` は値動きの荒さを見る指標です。
- `RR` はリスクリワード比で、損切り幅に対して利幅がどれだけあるかの比率です。
- `prelabel` は「方向の前に、今の位置で入ってよいか」を示す位置評価です。
- `Phase 1` は、通知後ではなく「セットアップ確定後のサイズ計画と出口計画」を扱う損益管理レイヤーです。

## 現在地

- 現在の主対象は `Ver02.x` です。
- `Phase 0` は、通知と事後評価の運用確認中です。
- `Phase 1` は、サイズ計画・出口計画・評価用ログの土台まで実装済みです。
- 本番では Ver01 を比較基準、Ver02.1 を改善版として並走させています。
- 開発側でも同じ `Ver02.1` 世代を使い、件名の `[API]` / `[CLI]` で運転モードを見分けます。
- ただし、現時点では通知発生待ちで、`daily-sync` を含む本番の一周確認はまだ未完了です。

## システム全体像

このシステムは、MEXC の BTC データを主データとして取得し、Binance の補助データを重ねて、1 サイクルごとに次を実行します。

1. 価格データ取得
2. テクニカル指標計算
3. 相場環境判定
4. 方向感スコア計算
5. 位置リスク判定
6. ロング/ショートのセットアップ生成
7. AI 助言
8. シグナル強度判定
9. 通知要否判定
10. 要約本文生成
11. JSON / CSV / 事後評価用ログ保存

定時実行は `main.py` の `main()` が担当し、`REPORT_TIMES` の時刻ごとに `run_cycle()` を呼びます。

## 使用データ

### 主データ

- 取引所: MEXC
- 銘柄: 既定値は `BTC_USDT`
- 足: `4h`, `1h`, `15m`
- 追加データ: Funding Rate

### 補助データ

- 取引所: Binance Futures
- データ:
  - Open Interest
  - Open Interest の推移
  - Taker Buy/Sell Volume
  - Orderbook
  - Liquidation events

### データ取得上の注意

- MEXC の未確定足は除外します。
- 取得失敗時はリトライします。
- Binance の補助データは一部欠けても処理継続します。
- Funding 取得失敗時も中立扱いで継続し、欠損は `data_missing_fields` と `data_quality_flag` へ残します。
- 清算データは `logs/cache/` にキャッシュし、直近一定時間の履歴を維持します。

## `run_cycle()` の実行フロー

現行 `run_cycle()` の大きな流れは次の通りです。

1. ハートビート更新
2. 古いログ削除
3. 未送信メール再送
4. MEXC サーバー時刻取得
5. `4h`, `1h`, `15m` ローソク足取得
6. ローソク足の妥当性検証
7. 各時間足ごとに EMA / RSI / ATR / Volume Ratio / Swing / Structure を計算
8. 現在価格・ATR比・Funding を確定
9. Binance 補助データ取得
10. サポート/レジスタンス帯を構築
11. 相場環境 `market_regime` を判定
12. 方向感スコアから `bias` を決定
13. 流動性、清算、OI/CVD、板を使って位置リスクを評価
14. 局面 `phase` を決定
15. 信頼度 `confidence` と機械整合性を算出
16. ロング/ショート両方のセットアップを生成
17. `prelabel` でセットアップ状態を補正
18. AI 助言 `ai_advice` を実行
19. `signal_tier` と `signal_tier_reason_codes` を決定
20. `data_quality_flag` と `data_missing_fields` を確定
21. `Phase 1` の有効判定、サイズ計画、出口計画を追加
22. 前回結果と比較して通知要否を判定
23. 件名と本文を生成
24. 通知する場合はメール送信
25. `signals/*.json`、`last_result.json`、`trades.csv` などへ保存

## 設定ファイルの考え方

設定は `config.py` で読み込みます。

### 必須

- `OPENAI_API_KEY`
- SMTP 関連
- 送信元/送信先メール

補足:

- 現行コードでは必須キーに `OPENAI_API_KEY` が入っています。
- ただし AI 実行方式は `api` 固定ではなく、`api / cli` を独立切替できます。

### 主な既定値

- EMA: 20 / 50 / 200
- RSI: 14
- ATR: 14
- しきい値:
  - `CONFIDENCE_LONG_MIN = 65`
  - `CONFIDENCE_SHORT_MIN = 70`
  - `MIN_RR_RATIO = 1.3`
  - `MAX_ACCEPTABLE_ATR_RATIO = 2.0`
  - `MIN_ACCEPTABLE_ATR_RATIO = 0.3`

### AI 関連の重要設定

- `AI_ADVICE_PROVIDER`
- `AI_SUMMARY_PROVIDER`
- `AI_ADVICE_CLI_COMMAND`
- `AI_SUMMARY_CLI_COMMAND`
- `OPENAI_ADVICE_MODEL`
- `OPENAI_SUMMARY_MODEL`
- `AI_TIMEOUT_SEC`
- `AI_SUMMARY_TIMEOUT_SEC`
- `AI_RETRY_COUNT`
- `SYSTEM_LABEL`

### Funding の扱い

Funding は内部で `%` 表現に変換して扱います。
例: `0.05` は `0.05%` です。

### `SYSTEM_LABEL` の役割

`SYSTEM_LABEL` は版名を示す識別ラベルです。
現在は本番・開発とも `Ver02.1` を使い、件名側ではこれに加えて実行モードの `[API]` / `[CLI]` を自動付与して見分けます。

## 時間足ごとの前処理

`_prepare_tf()` で各時間足に対して次を計算します。

- `ema_fast`: EMA20
- `ema_mid`: EMA50
- `ema_slow`: EMA200
- `rsi`
- `atr`
- `volume_ratio`
- `swings`
- `structure`
- `ema_alignment`
- `signal`

### Swing 検出

`detect_swings()` は、前後 `n` 本と比べて高値/安値が突出している場所を swing として抽出します。

### Structure 判定

`classify_structure()` は swing 高値・安値の並びから次を返します。

- `hh_hl`: 高値切り上げ + 安値切り上げ
- `lh_ll`: 高値切り下げ + 安値切り下げ
- それ以外は中立寄り

### 時間足シグナル

`calc_tf_signal()` は EMA の並びと structure を合わせて、各時間足を `long` / `short` / `wait` で返します。

## サポート/レジスタンス帯

`support_resistance.py` が担当します。

### 作り方

1. 各時間足の swing 高値/安値から候補帯を作る
2. 帯の幅は ATR と価格比率で決める
3. ローソク足がその帯に何回反応したかを数える
4. 近い帯を統合する
5. 強度付きゾーンとして保存する

### 強度の考え方

- `4h` の重み: 3
- `1h` の重み: 2
- `15m` の重み: 1
- さらに反応回数を足します

### 出力の使い分け

- `all_support_zones`, `all_resistance_zones`
  - 内部計算用の全ゾーン
- `support_zones`, `resistance_zones`
  - 現在価格に近い表示用ゾーン
- `critical_zone`
  - 現在価格が重要帯の内側にいるかを示す警戒フラグ

## 相場環境 `market_regime`

`regime.py` が担当します。

### 種類

- `uptrend`
- `downtrend`
- `range`
- `volatile`
- `transition`

### 判定の主軸

- 4時間足 EMA の並び
- EMA20 の傾き
- 4時間足 structure
- ATR比
- RSI
- EMA20 と EMA50 の位置関係

### 特徴

- ATR比が高すぎると `volatile`
- トレンド条件が明確なら `uptrend` / `downtrend`
- 条件混在時は `transition`
- 上記以外は `range`

`transition` のときは、補助的に `transition_direction` が `up` または `down` になります。

## 方向感スコア `compute_scores()`

この関数が機械判定の中心です。
ロングとショートを別々に採点し、その差で `bias` を決めます。

### 加点材料

- 相場環境
- 4時間足 EMA 配列
- 4時間足 EMA20 傾き
- 価格と 4時間足 EMA50 の位置
- 4時間足 structure
- 1時間足 structure
- サポート/レジスタンスへの近さ
- 直近高値/安値ブレイク
- 出来高比
- RSI 範囲

### 減点材料

- 逆側ゾーンが近い
- RR不足
- レンジ中央
- ATR極端値
- Funding 警戒/禁止域

### 重要フラグ

- `no_trade_flags`
- `warning_flags`
- `top_positive_factors`
- `top_negative_factors`
- `score_factor_breakdown_long`
- `score_factor_breakdown_short`

### 最終判定

表示用に 0-100 スケールへ変換したあと、

- ロング優位差がしきい値以上なら `long`
- ショート優位差がしきい値以上なら `short`
- それ以外は `wait`

となります。

## 補助分析

### 1. 流動性 `analyze_liquidity()`

目的:

- 近くの高値群・安値群を「流動性が溜まりやすい価格」として扱う

主な出力:

- `liquidity_above`
- `liquidity_below`
- `nearest_liquidity_above_price`
- `nearest_liquidity_below_price`
- `liquidity_swept_recently`

### 2. 清算クラスター `analyze_liquidation_clusters()`

目的:

- 近くに強い清算の塊があるかを見る

主な出力:

- `liquidation_above`
- `liquidation_below`
- `largest_liquidation_price`
- `distance_to_largest_liquidation`

### 3. OI / CVD `analyze_oi_cvd()`

目的:

- 建玉の増減と成行フローの向きを見る

主な出力:

- `oi_state`
- `cvd_price_divergence`

### 4. 板 `analyze_orderbook()`

目的:

- 近い位置の大きな買い板/売り板を見る

主な出力:

- `orderbook_bid_wall_price`
- `orderbook_ask_wall_price`
- `orderbook_bid_wall_size`
- `orderbook_ask_wall_size`
- `orderbook_bias`

## 位置リスク `evaluate_position_risk()`

これは「方向が合っていても、今の位置で入るのが危険ではないか」を判定する層です。

### スコアに使う材料

- 近い流動性
- 近い板の壁
- 大きい清算クラスター
- `liquidity_swept_recently`
- `oi_state`
- `cvd_price_divergence`
- `orderbook_bias`

### 返すもの

- `location_risk`: 0-100
- `risk_flags`
- `prelabel`
- `prelabel_primary_reason`

### `prelabel` の意味

- `ENTRY_OK`
  - 位置的には問題が小さい
- `RISKY_ENTRY`
  - 危険寄り。入るなら慎重
- `SWEEP_WAIT`
  - 先に流動性回収を待ちたい
- `NO_TRADE_CANDIDATE`
  - 現位置はかなり悪い

### 重要ポイント

この `prelabel` は、後段のセットアップ状態を補正します。
つまり、方向感が強くても位置が悪ければ `ready` を維持しません。

## 局面判定 `phase`

`phase.py` が担当します。

### 現行の値

- `trend_following`
- `pullback`
- `breakout`
- `range`
- `reversal_risk`

### 判定材料

- breakout 成立有無
- pullback の深さ
- EMA50 と EMA200 の間にいるか
- reversal risk の有無
- `market_regime`
- `bias`

補足:

- 旧資料で `trend_follow` と書かれている場合がありますが、現行コードは `trend_following` です。

## 信頼度 `confidence`

`compute_confidence()` が 0-100 の信頼度を作ります。

### ベース

- `bias=long` ならロング表示点数
- `bias=short` ならショート表示点数
- `bias=wait` なら控えめ

### 追加補正

- `4h/1h/15m` の一致数
- 相場環境
- `phase`
- RR
- 逆側ゾーンまでの余白
- `critical_zone`
- `warning_flags`

## セットアップ生成 `build_setup()`

ロング用とショート用を両方作ります。

### 手順

1. 現在価格に対して自然なエントリー帯を選ぶ
2. 損切り位置を ATR ベースで計算
3. 利確目標を逆側ゾーンまたは RR ベースで計算
4. RR を算出
5. 失格条件を確認

### 判定状態

- `ready`
- `watch`
- `invalid`

### `prelabel` の反映

`apply_prelabel_to_setup()` により、

- `RISKY_ENTRY`: `ready` を `watch` に落とす
- `SWEEP_WAIT`: `watch` に落とす
- `NO_TRADE_CANDIDATE`: `invalid` に落とす

となります。

## 主セットアップ選択

`choose_primary_setup()` は通知や表示の基準になる主セットアップを決めます。

- `bias=long` ならロング優先
- `bias=short` ならショート優先
- `wait` のときは残っている `ready` / `watch` を見て選びます

## AI 助言と要約

このシステムの AI 部分は、現在 `api` と `cli` を独立して切り替えられます。

### 1. AI 助言 `request_ai_advice()`

役割:

- 機械判定を再計算するのではなく、構造化済みデータの「意味づけ」と品質審査を返す

入力:

- `machine_payload`
- `qualitative_payload`

主な出力:

- `decision`
- `quality`
- `confidence`
- `notes`
- `primary_reason`
- `market_interpretation`
- `warnings`
- `next_condition`

### 2. 要約本文 `build_summary_body()`

役割:

- 通知メール本文を作る
- AI が使えない場合は `_fallback_summary()` で本文を構成する

### `api / cli` 切替

- `AI_ADVICE_PROVIDER`
- `AI_SUMMARY_PROVIDER`

で、それぞれ `api` / `cli` を独立切替できます。

### API モード

- OpenAI API を使います
- JSON 解釈失敗や例外時は失敗扱いです
- 助言失敗時はエラーログを `logs/errors/` に出します

### CLI モード

- `AI_ADVICE_CLI_COMMAND`
- `AI_SUMMARY_CLI_COMMAND`

に指定したコマンドへ JSON を標準入力で渡し、標準出力を受け取ります。

### `tools/codex_cli_wrapper.py` の役割

このラッパーは、監視側から渡される JSON の `task` を見て、

- `summary`
- `ai_advice`

を切り替え、`codex exec` を使って本文または JSON を返す最小アダプタです。

### 失敗時の扱い

- 助言側:
  - CLI コマンド未設定や実行失敗時は `None` 扱い
  - 失敗内容は `logs/errors/*_ai_advice_error.log` へ出力
- 要約側:
  - CLI コマンド未設定や実行失敗時は `_fallback_summary()` を返す
  - 失敗内容は `logs/errors/*_summary_error.log` へ出力

## シグナル段階 `signal_tier`

`compute_signal_tier()` が次を返します。

- `normal`
- `strong_machine`
- `strong_ai_confirmed`

加えて、なぜその段階になったかを `signal_tier_reason_codes` に残します。

## 通知判定 `should_notify()`

通知は毎回送るわけではありません。
前回結果や直近通知と比較し、「改善や重要変化があったとき」に送ります。

### 最低条件

- `bias` が `long` か `short`
- `confidence` が最低ライン以上

### 通知理由になる変化

- `status_upgraded`
- `bias_changed`
- `prelabel_improved`
- `confidence_jump`
- `agreement_changed`
- `signal_tier_upgraded`

### 抑制理由

- `bias_wait`
- `confidence_below_long_min`
- `confidence_below_short_min`
- `multiple_no_trade_flags`
- `no_material_change`
- `cooldown_active`

### 保存のしかた

通知側の理由は、

- `notify_reason_codes`
- `suppress_reason_codes`

として `result`、JSON、CSV に残します。

## Phase 1 損益管理レイヤー

`Phase 1` は、通知そのものではなく、主セットアップが出たあとのサイズ計画と出口計画を整える層です。

### 入口モジュール

- `src/trade/activation.py`
- `src/trade/position_sizing.py`
- `src/trade/exit_manager.py`
- `src/trade/performance_state.py`

### 1. 有効判定 `determine_phase1_activation()`

主な考え方:

- `primary_setup_side` が `long` / `short` であること
- `bias=wait` では有効にしない
- 価格入力が壊れている場合は無効
- `data_quality_flag=partial_missing` では本有効にしない
- `primary_setup_status=ready` のときだけ `phase1_active=true`
- `watch` は参考ログのみで、`phase1_active=false`

主な出力:

- `phase1_active`
- `phase1_activation_reason`

### 2. 連敗数 `load_loss_streak()`

役割:

- `signal_outcomes.csv` と `trades.csv` の「完了済みかつ通知済み」の履歴から連敗数を自動計算する
- 履歴がまだ無い場合だけ `PHASE1_LOSS_STREAK` を予備値として使う

### 3. サイズ計画 `build_position_size_plan()`

役割:

- `account_balance`、`entry_price`、`stop_loss_price` からサイズを計算する
- 最大サイズ制限を適用する
- 連敗時はリスクを縮小する
- `signal_tier` が強くてもサイズは増やさない

主な出力:

- `risk_percent_applied`
- `planned_risk_usd`
- `position_size_usd`
- `max_size_capped`
- `size_reduction_reasons`
- `loss_streak_at_entry`

### 4. 出口計画 `build_exit_plan()`

役割:

- TP1 / TP2 を計算する
- TP1 到達後の建値移動条件を返す
- ATR トレイリング条件を返す
- 時間切れ撤退条件を返す

主な出力:

- `tp1_price`
- `tp2_price`
- `breakeven_after_tp1`
- `trail_atr_multiplier`
- `timeout_hours`
- `exit_rule_version`

## 件名と本文

### 件名

`build_summary_subject()` が生成します。

含まれる要素:

- バッジ
- `SYSTEM_LABEL`
- JST 時刻
- `prelabel`
- `bias`
- 現在価格
- `confidence`

AI 審査がない場合は「機械判定のみ」の注意が付きます。

### 本文

`build_summary_body()` が担当します。

- `api` または `cli` のどちらかで本文生成を試みる
- 使えない場合は `_fallback_summary()` へフォールバックする

## 保存される結果

### JSON

- `logs/signals/<signal_id>.json`
- `logs/last_result.json`
- `logs/last_notified.json`

### CSV

- `logs/csv/trades.csv`
- `logs/csv/signal_outcomes.csv`
- `logs/csv/user_reviews.csv`
- `logs/csv/shadow_log.csv`

### `trades.csv` の主な保存項目

- 時刻
- 価格
- `bias`
- `market_regime`
- `phase`
- スコア
- `confidence`
- `prelabel`
- `location_risk`
- `signal_tier`
- `signal_tier_reason_codes`
- `data_quality_flag`
- `data_missing_fields`
- `notify_reason_codes`
- `suppress_reason_codes`
- `summary_subject`
- `phase1_active`
- `phase1_activation_reason`
- `risk_percent_applied`
- `planned_risk_usd`
- `position_size_usd`
- `loss_streak_at_entry`
- `tp1_price`
- `tp2_price`
- `timeout_hours`
- `exit_rule_version`

## 事後評価とレビュー

### `tools/log_feedback.py`

このツールは通知後の事後評価をまとめる中核です。

主な役割:

- `daily-sync`
- `build-shadow-log`
- `import-reviews`
- 週次/月次レポート生成

### `daily-sync` の位置づけ

通知から 24 時間経過した後に実行し、次を進めます。

- `signal_outcomes.csv` 更新
- `shadow_log.csv` 再構築
- `📝通知レビュー.md` 更新
- `user_reviews.csv` 取込後の反映

### `shadow_log.csv` の役割

`trades.csv`、`signal_outcomes.csv`、`user_reviews.csv` をつなぎ、

- 観測ログ
- 24h 事後評価
- ユーザーレビュー
- `Phase 1` のサイズ計画・出口計画

を 1 枚で見やすくする統合ログです。

### `logic_validated` の考え方

`logic_validated` は手入力欄ではなく、自動計算欄です。

- `prelabel_primary_reason`
- `actual_move_driver`

の組み合わせから、ロジックの見立てが実際の動きと合っていたかを `true / false / 空欄` で返します。

### 現在の未完了事項

- 通知発生ケースがまだ無く、`was_notified=True` の本番確認は未完了
- 本番 `daily-sync` の一周確認は未完了
- `actual_move_driver` 入力後の `logic_validated` 本番確認も未完了

## メール送信失敗時

- 送信失敗時は `pending_email.json` に退避します
- 次サイクル開始時に再送を試みます
- 一定回数以上失敗すると再送停止します

## ログ整理

`cleanup_if_due()` が 24 時間に 1 回だけ古いファイルを削除します。

削除対象:

- `logs/signals`
- `logs/notifications`
- `logs/errors`

保存日数は設定値で制御します。

## テストで押さえている主題

`tests/` では少なくとも次を確認しています。

- Funding と signal 判定
- サポート/レジスタンスの挙動
- 通知トリガー
- 要約フォーマット
- CLI ラッパー
- `Phase 1` のサイズ計画と出口計画
- `phase1_active` 判定
- `loss_streak` 自動計算
- `log_feedback` の `shadow_log` / `logic_validated`

## このシステムの判断思想

このシステムは、単純な「上がりそう / 下がりそう」判定だけではありません。
判断は大きく 5 層に分かれています。

1. 方向
   - スコアで `long` / `short` / `wait` を決める
2. 環境
   - `market_regime`, `phase`, 時間足整合性を見る
3. 位置
   - `prelabel`, `location_risk`, `risk_flags` で「今入る場所か」を見る
4. 品質確認
   - AI 助言と `signal_tier` で候補の強さを絞る
5. 損益管理
   - `Phase 1` でサイズと出口を計画し、後から評価しやすくする

重要なのは、方向が合っていても位置が悪ければ止める設計であることです。
さらに現行版では、位置だけでなく「データ欠損時に Phase 1 を本有効にしない」「通知理由と抑制理由を保存する」といった観測性も重視しています。

## 他AIが読むときの最重要ポイント

1. 中心関数は `main.py` の `run_cycle()`
2. 方向判定は `compute_scores()`
3. 位置評価は `evaluate_position_risk()`
4. 実行可否は `build_setup()` と `apply_prelabel_to_setup()`
5. 通知条件は `should_notify()`
6. AI は再計算器ではなく審査員
7. `Phase 1` はサイズ計画・出口計画・評価ログの層
8. 重要出力は `bias`, `prelabel`, `confidence`, `primary_setup_status`, `signal_tier`, `phase1_active`

## 評価観点として有効な論点

- スコア加点/減点の整合性
- `prelabel` が強すぎるか弱すぎるか
- `signal_tier` 条件が厳しすぎるか
- 通知条件が多すぎる/少なすぎるか
- Funding や ATR のしきい値妥当性
- `range` と `transition` の切り分け妥当性
- OI/CVD/板/清算を位置リスクへ混ぜる重み
- `Phase 1` の本有効条件が厳しすぎるか
- `loss_streak` によるリスク縮小幅が妥当か

## 参照するとよい主要ファイル

- `main.py`
- `config.py`
- `src/analysis/scoring.py`
- `src/analysis/position_risk.py`
- `src/analysis/rr.py`
- `src/analysis/confidence.py`
- `src/analysis/signal_tier.py`
- `src/notification/trigger.py`
- `src/ai/advice.py`
- `src/ai/summary.py`
- `src/trade/activation.py`
- `src/trade/position_sizing.py`
- `src/trade/exit_manager.py`
- `src/trade/performance_state.py`
- `tools/codex_cli_wrapper.py`
- `tools/log_feedback.py`

## 最後に

このシステムは、

- MEXC の価格情報で方向を作り
- Binance の補助データで位置の危険度を補正し
- AI 助言で意味づけを補助し
- 通知は「変化があったときだけ」送り
- `Phase 1` と `shadow_log.csv` で後から検証しやすくする

という構成です。

現状はまだ通知発生待ちの段階ですが、コード上では「通知理由」「抑制理由」「データ欠損」「事後評価」「レビュー反映」「Phase 1 の計画値」まで追える形に進んでいます。
