# BTC監視システム AI向けロジック全体整理

## 目的

この文書は、`btc_monitor` の実装ロジックを、別のAIや新しい担当者が短時間で理解できるように整理したものです。
コード上の事実を優先し、推測ではなく「実際に何をしているか」を中心にまとめています。

補足:
- `bias` は売買の方向感です。`long` は上目線、`short` は下目線、`wait` は様子見です。
- `ATR` は値動きの大きさの目安です。
- `RR` はリスクリワード比で、損切り幅に対してどれだけ利幅があるかの比率です。
- `prelabel` は「方向の前に、今の位置で入ってよいか」を表す位置評価です。

## システム全体像

このシステムは、MEXC の BTC データを主データとして取得し、Binance の補助データを重ねて、以下を1サイクルごとに実行します。

1. 価格データ取得
2. テクニカル指標計算
3. 相場環境判定
4. 売買方向の点数化
5. 位置リスク判定
6. ロング/ショートのセットアップ作成
7. AI による品質審査
8. 通知要否判定
9. メール本文生成
10. JSON / CSV ログ保存

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
- 清算データは `logs/cache/` にキャッシュし、直近一定時間の履歴を維持します。

## 実行フロー

`run_cycle()` の処理順は次の通りです。

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
12. スコア計算で `bias` を決定
13. 流動性、清算、OI/CVD、板の位置リスクを評価
14. 局面 `phase` を決定
15. 信頼度 `confidence` を算出
16. ロング/ショート両方のセットアップを生成
17. `prelabel` でセットアップ状態を補正
18. AI 審査 `ai_advice` を実行
19. シグナル段階 `signal_tier` を決定
20. 前回結果と比較して通知要否を判定
21. 件名・本文を生成
22. 通知する場合はメール送信
23. JSONスナップショット、CSV、last_result を保存

## 設定ファイルの考え方

設定は `config.py` で読み込みます。

### 必須

- `OPENAI_API_KEY`
- SMTP 関連
- 送信元/送信先メール

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

### Funding の扱い

Funding は内部で `%` 表現に変換して扱います。
例: `0.05` は `0.05%` です。

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
- それ以外は中立的な構造

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
- さらに反応回数を足す

### 出力の使い分け

- `support_zones_all`, `resistance_zones_all`
  - 内部計算用の全ゾーン
- `support_zones_by_strength`, `resistance_zones_by_strength`
  - 強度上位3件
- `support_zones`, `resistance_zones`
  - 現在価格に近い方向別の表示用ゾーン

### critical_zone

現在価格がどれかのゾーン内部にいる場合 `critical_zone = True` です。
これは「重要帯の上にいるので、値動きが不安定になりやすい」という警戒用です。

## 相場環境 `market_regime`

`regime.py` が担当します。

### 種類

- `uptrend`
- `downtrend`
- `range`
- `volatile`
- `transition`

### 判定条件の主軸

- 4時間足 EMA の並び
- EMA20 の傾き
- 4時間足 structure
- ATR比
- RSI
- EMA20 と EMA50 の位置関係

### 特徴

- ATR比が高すぎると `volatile`
- 4時間足のトレンド条件が明確なら `uptrend` / `downtrend`
- クロス前後で条件が混在すると `transition`
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

- `no_trade_flags`: 見送り判断に近いもの
- `warning_flags`: 注意だが即失格ではないもの

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

見るもの:
- swing 高値/安値
- 直近高値/安値
- 直近ローソク足群

主な出力:
- `liquidity_above`
- `liquidity_below`
- `nearest_liquidity_above_price`
- `nearest_liquidity_below_price`
- `liquidity_swept_recently`

`liquidity_swept_recently` は、「直近で高値または安値を掃除したか」を見る簡易判定です。

### 2. 清算クラスター `analyze_liquidation_clusters()`

目的:
- 近くに強い清算の塊があるかを見る

やっていること:
- 清算イベントを価格帯ごとにバケツ分けする
- 現在価格より上/下の合計量を出す
- 一番大きいクラスター価格を出す

主な出力:
- `liquidation_above`
- `liquidation_below`
- `largest_liquidation_price`
- `distance_to_largest_liquidation`

### 3. OI / CVD `analyze_oi_cvd()`

目的:
- 建玉の増減と成行フローの向きを見る

見るもの:
- `oi_change_pct`
- `cvd_series`
- 直近価格推移

主な出力:
- `oi_state`
  - `trend_supported_up`
  - `trend_supported_down`
  - `short_cover_risk`
  - `long_flush_exhaustion`
- `cvd_price_divergence`
  - `bullish`
  - `bearish`
  - `none`

### 4. 板 `analyze_orderbook()`

目的:
- 近い位置の大きな買い板/売り板をみる

主な出力:
- `orderbook_bid_wall_price`
- `orderbook_ask_wall_price`
- `orderbook_bid_wall_size`
- `orderbook_ask_wall_size`
- `orderbook_bias`

`orderbook_bias` は、板の厚さが片側に偏ると `bid_heavy` または `ask_heavy` になります。

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

この `prelabel` は、後段のセットアップ状態を上書きします。
つまり、スコアが強くても位置が悪ければ `ready` のまま通しません。

## 局面判定 `phase`

`phase.py` が局面を次のように返します。

- `trend_following`
- `pullback`
- `breakout`
- `range`
- `reversal_risk`

判定材料:
- breakout 成立有無
- pullback の深さ
- EMA50 と EMA200 の間にいるか
- RSI極端値や実体の弱さによる反転警戒

## 信頼度 `confidence`

`compute_confidence()` が 0-100 の信頼度を作ります。

### ベース

- `bias=long` ならロング表示点数
- `bias=short` ならショート表示点数
- `bias=wait` なら控えめな値

### 追加補正

- 3時間足ではなく、3つの時間足 `4h/1h/15m` の一致数
- 相場環境
- phase
- RR
- 逆側ゾーンまでの余白
- critical_zone
- warning_flags の個数

### ざっくりした思想

- 時間足がそろうと加点
- トレンド環境は加点
- レンジ・反転注意・警告フラグは減点
- RR が良いと加点

## セットアップ生成 `build_setup()`

ロング用とショート用を両方作ります。

### 手順

1. 現在価格に対して最も自然なエントリー帯を選ぶ
2. 損切り位置を ATR ベースで計算
3. 利確目標を逆側ゾーンまたは RR ベースで計算
4. RR を算出
5. 各種失格条件をチェック

### 判定状態

- `ready`
  - 現在価格がエントリー帯内で、トリガーも整っている
- `watch`
  - 監視対象だが即エントリーではない
- `invalid`
  - 条件不足

### `invalid_reason` に入る代表例

- `RR不足`
- `ATR極端値`
- `Funding禁止域`
- `confidence不足`
- `warning多発`

### トリガーの考え方

- ロング:
  - 上方向ブレイク
  - または出来高比が 1.2 以上
- ショート:
  - 下方向ブレイク
  - または出来高比が 1.2 以上

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
- `wait` のときは `ready` / `watch` の残り方で選ぶ

## AI 審査 `request_ai_advice()`

このシステムでは OpenAI API を使って、機械判定の「意味づけ」をさせています。

### 入力

- `machine_payload`: 機械判定結果一式
- `qualitative_payload`: 定性的補助情報

### 定性的補助情報の中身

- セッション帯: `asia`, `europe`, `us`
- pullback の深さ
- wick rejection
- body strength
- range/trend 状態
- late entry risk
- trend exhaustion risk
- rule conflicts

### AI の役割

再計算ではなく、構造化済みデータを読んで以下を返します。

- `decision`
- `quality`
- `confidence`
- `notes`
- `primary_reason`
- `market_interpretation`
- `warnings`
- `next_condition`

### 注意

- API キーがない場合、AI審査はスキップされます
- JSON で返らない場合は失敗扱いです
- 失敗内容は `logs/errors/*_ai_advice_error.log` に出ます

## シグナル段階 `signal_tier`

`compute_signal_tier()` が次を返します。

- `normal`
- `strong_machine`
- `strong_ai_confirmed`

### `strong_machine` 条件

全部満たす必要があります。

- `prelabel == ENTRY_OK`
- 主セットアップが `ready`
- confidence が最低ライン + 10 以上
- RR 2.0 以上
- `no_trade_flags` なし
- `risk_flags` なし
- `warning_flags` なし
- 機械整合性 `agreement_with_machine == agree`

### `strong_ai_confirmed` 条件

`strong_machine` に加えて、

- AI の方向が機械判定と一致
- AI confidence 0.70 以上
- AI quality が `A` または `B`

## 通知判定 `should_notify()`

通知は毎回送るわけではありません。
前回結果と比較し、「改善や重要変化があったとき」に送ります。

### まず最低条件

- `bias` が `long` か `short`
- `confidence` が最低ライン以上

### 通知理由になる変化

- `status_upgraded`
  - `invalid -> watch/ready`
  - `watch -> ready`
- `bias_changed`
  - `wait -> long/short`
- `prelabel_improved`
  - 位置評価が改善
- `confidence_jump`
  - 直近通知時から一定以上変化
- `agreement_changed`
  - 機械整合性が変化
- `signal_tier_upgraded`
  - `normal -> strong_machine -> strong_ai_confirmed`

### 抑制条件

- 主セットアップが悪く、`no_trade_flags` が多いと通知しない
- 通知クールダウン中は通常通知しない
- ただし `signal_tier_upgraded` はクールダウン中でも通す

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
- confidence

AI審査がない場合は、件名末尾に「機械判定のみ」の注意を付けます。

### 本文

`build_summary_body()` が担当します。

- API キーがある場合:
  - OpenAI に本文生成させる
- API キーがない場合:
  - `_fallback_summary()` で本文を組み立てる

本文では次を説明します。

- 結論
- 方向感
- 機械判定の要約
- 環境情報
- ロング/ショートセットアップ
- AI審査結果
- 注意点

## 保存される結果

### JSON

- `logs/signals/<signal_id>.json`
- `logs/last_result.json`
- `logs/last_notified.json`

### CSV

- `logs/csv/trades.csv`

### 主な保存項目

- 時刻
- 価格
- bias
- regime
- phase
- score
- confidence
- prelabel
- location_risk
- funding
- ATR / volume
- liquidity / liquidation / OI / CVD / orderbook
- long/short setup
- signal_tier
- summary_subject
- no_trade_flags
- 通知理由

## メール送信の失敗時

- 送信失敗時は `pending_email.json` に退避
- 次のサイクル開始時に再送を試行
- 3回以上失敗すると再送停止

## ログ整理

`cleanup_if_due()` が 24 時間に1回だけ古いファイルを削除します。

削除対象:
- `logs/signals`
- `logs/notifications`
- `logs/errors`

保存日数は設定値で制御します。

## 補助ツール

### `tools/log_feedback.py`

通知後の結果検証用です。

主な役割:
- 24時間後などの事後評価
- `signal_outcomes.csv` 更新
- 手動レビュー用 Markdown の出力
- 手動レビューの再取込
- 週次/月次フィードバックレポート生成

### `tools/log_analytics.py`

CSV ログを集計し、傾向確認用の Markdown を生成します。

### `backtest/runner.py`, `backtest/evaluator.py`

現在ロジックに近い形で過去データ評価を行うための簡易バックテスト群です。

## テストで守っている主題

`tests/` では少なくとも次を確認しています。

- Funding と signal 判定
- サポート/レジスタンスの挙動
- 通知トリガー
- 要約フォーマット
- ログフィードバック処理

つまり、見た目だけではなく、主要な判定仕様とログ後処理も一部テスト対象です。

## このシステムの判断思想

このシステムは、単純な「上がりそう / 下がりそう」判定だけではありません。
判断は大きく4層に分かれています。

1. 方向
   - スコアで `long` / `short` / `wait` を決める
2. 環境
   - `market_regime`, `phase`, 時間足整合性をみる
3. 位置
   - `prelabel`, `location_risk`, `risk_flags` で「今入る場所か」をみる
4. 品質確認
   - AI審査と `signal_tier` で、強い候補だけを上位扱いする

重要なのは、方向が合っていても位置が悪ければ止める設計になっていることです。
このため、実装思想としては「方向感より位置を優先」がかなり強いです。

## 他AIが読むときの最重要ポイント

別AIがこのシステムを評価する場合、まず次を押さえると全体を見失いにくいです。

1. 中心関数は `main.py` の `run_cycle()`
2. 売買方向は `compute_scores()`
3. 位置評価は `evaluate_position_risk()`
4. 実際の実行可否は `build_setup()` と `apply_prelabel_to_setup()`
5. 通知条件は `should_notify()`
6. AI は再計算器ではなく審査員
7. 重要出力は `bias`, `prelabel`, `confidence`, `primary_setup_status`, `signal_tier`

## 評価観点として有効な論点

このシステムを他AIに評価させるなら、次の観点が有効です。

- スコア加点/減点の整合性
- `prelabel` が強すぎるか弱すぎるか
- `signal_tier` 条件が厳しすぎるか
- 通知条件が多すぎる/少なすぎるか
- Funding や ATR のしきい値妥当性
- `range` と `transition` の切り分け妥当性
- OI/CVD/板/清算を位置リスクへ混ぜる重みが適切か

## 参照するとよい主要ファイル

- `main.py`
- `config.py`
- `src/analysis/scoring.py`
- `src/analysis/position_risk.py`
- `src/analysis/rr.py`
- `src/analysis/confidence.py`
- `src/notification/trigger.py`
- `src/ai/advice.py`
- `src/ai/summary.py`
- `tools/log_feedback.py`

## 最後に

このシステムは、

- MEXC の価格情報で方向を作り
- Binance の補助データで位置の危険度を補正し
- OpenAI で最終的な解釈品質を補助し
- 通知は「変化があったときだけ」送る

という構成です。

コードを1行ずつ追わなくても、上の流れを押さえれば、全体ロジックの骨格はかなり再現できます。
