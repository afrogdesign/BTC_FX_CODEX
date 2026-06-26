更新日: 2026-03-16 21:25 JST

# BTC監視システム AI向けロジック全体整理

この文書は、`btc_monitor` の現行 `Ver02.1` を別の AI や次担当が短時間で理解するための整理資料です。
いまは本番も開発も `Ver02.1 CLI` を主系統として扱います。

## 1. この文書の位置づけ

- この文書は、現行ロジックの全体像と、判定に効く主要パラメーターをまとめた参照資料です。
- 実際に走る最終値は `.env` が最優先です。
- `.env` に無い値は `config.py` の既定値が使われます。
- 実装の最終正本はコードです。
- ただし、日常の判断ではまずこの文書を見れば、今の判定構造と調整点を一通りつかめるように保ちます。

## 2. 現在地

- 現在版: `Ver02.1`
- 本番運用: `CLI`
- 開発運用: `CLI`
- 本番主ラベル: `com.afrog.btc-monitor-ver021`
- 開発主ラベル: `com.afrog.btc-monitor`
- 本番ログ確認の標準入口: `tools/sync_ver021_prod_status.sh`
- 本番軽量同期ジョブ: `com.afrog.btc-monitor-status-sync`

補足:

- `bias` は方向感です。`long` は上目線、`short` は下目線、`wait` は様子見です。
- `prelabel` は「方向の前に、今その位置で入ってよいか」の位置評価です。
- `RR` はリスクリワード比で、損切り幅に対して利幅がどれだけあるかの比率です。
- `Phase 1` は、通知後ではなく「セットアップ確定後のサイズ計画と出口計画」を扱う層です。

## 3. 1サイクルの流れ

1. ハートビート更新
2. 古いログ削除
3. 未送信メール再送
4. MEXC データ取得
5. Binance 補助データ取得
6. テクニカル計算
7. 相場環境 `market_regime` 判定
8. 方向感スコア計算
9. 位置リスク評価
10. 局面 `phase` 判定
11. `confidence` 算出
12. ロング/ショートのセットアップ生成
13. `prelabel` 反映
14. AI 助言
15. `signal_tier` 決定
16. `Phase 1` 有効判定、サイズ計画、出口計画
17. 通知要否判定
18. 件名と本文生成
19. JSON / CSV / 評価用ログ保存

定時実行は `main.py` の `main()` から、`REPORT_TIMES` に合わせて `run_cycle()` が呼ばれます。

## 4. 判定ロジックの骨格

### 4.1 相場環境 `market_regime`

主な材料:

- 4時間足 EMA 配列
- EMA20 の傾き
- 4時間足 structure
- ATR 比
- RSI

主な出力:

- `uptrend`
- `downtrend`
- `range`
- `volatile`
- `transition`

### 4.2 方向感 `bias`

ロング点数とショート点数を別々に計算し、その差で `long` / `short` / `wait` を決めます。

主な加点材料:

- 相場環境
- 4時間足、1時間足 structure
- EMA 配列
- 出来高比
- RSI
- ブレイク状況
- サポート/レジスタンスとの距離

主な減点材料:

- 逆側ゾーンの近さ
- RR不足
- レンジ中央
- ATR 極端値
- Funding 警戒域

### 4.3 位置評価 `prelabel`

方向が合っていても、今その位置で入るのが危険なら止めます。

主な材料:

- 近い流動性
- 近い板の壁
- 清算クラスター
- `liquidity_swept_recently`
- `oi_state`
- `cvd_price_divergence`
- `orderbook_bias`

主な出力:

- `ENTRY_OK`
- `RISKY_ENTRY`
- `SWEEP_WAIT`
- `NO_TRADE_CANDIDATE`

### 4.4 局面 `phase`

主な値:

- `trend_following`
- `pullback`
- `breakout`
- `range`
- `reversal_risk`

### 4.5 信頼度 `confidence`

0 から 100 の強度です。主に次を見ます。

- `bias` 側のベース点
- 時間足の一致数
- `market_regime`
- `phase`
- RR
- 逆側ゾーンまでの余白
- `critical_zone`
- `warning_flags`

### 4.6 セットアップ状態

ロング用とショート用を別々に作り、主に次を持ちます。

- `entry`
- `stop_loss`
- `take_profit`
- `rr_ratio`
- `setup_status`

`setup_status` は次のどれかです。

- `ready`
- `watch`
- `invalid`

その後 `prelabel` により補正されます。

- `RISKY_ENTRY`: `ready` を `watch` に落としやすい
- `SWEEP_WAIT`: `watch` に落とす
- `NO_TRADE_CANDIDATE`: `invalid` に落とす

## 5. 通知ロジック

通知には 2 層あります。

### 5.1 本命通知

本命通知は、主に次で決まります。

- `bias`
- `confidence`
- `signal_tier`
- 前回通知からの差分
- クールダウン

代表的な停止条件:

- `confidence` が最低値未満
- `setup_status` が弱い
- クールダウン中

### 5.2 注意報通知

本命未満でも、初動の変化を先に拾うための通知です。

主に次で決まります。

- `ATTENTION_ALERT_SCORE_MIN`
- `ATTENTION_ALERT_GAP_MIN`
- `ATTENTION_ALERT_COOLDOWN_MINUTES`

## 6. Phase 1

`Phase 1` は「通知後の損益管理をどう設計するか」を扱います。

主な出力:

- `phase1_active`
- `phase1_activation_reason`
- `risk_percent_applied`
- `loss_streak_at_entry`
- `max_position_size_usd`
- `tp1`
- `tp2`
- `trail_atr_multiplier`

有効化は `src/trade/activation.py`、サイズ計画は `src/trade/position_sizing.py` が担当します。

## 7. 現在の主要パラメーター一覧

この表は、現在の `.env` と `config.py` をもとにした、判定や通知に効く主要パラメーター一覧です。
秘密情報はここに書きません。

### 7.1 実行モード

| 項目 | 現在値 | 役割 |
| --- | --- | --- |
| `SYSTEM_LABEL` | `Ver02.1` | 件名や版識別に使う |
| `AI_ADVICE_PROVIDER` | `cli` | AI助言の実行方式 |
| `AI_SUMMARY_PROVIDER` | `cli` | 要約生成の実行方式 |
| `AI_TIMEOUT_SEC` | `45` | AI助言の待機秒数 |
| `AI_SUMMARY_TIMEOUT_SEC` | `60` | 要約生成の待機秒数 |
| `AI_RETRY_COUNT` | `3` | AI 再試行回数 |

### 7.2 テクニカル基本値

| 項目 | 現在値 | 役割 |
| --- | --- | --- |
| `EMA_FAST` | `20` | 短期 EMA |
| `EMA_MID` | `50` | 中期 EMA |
| `EMA_SLOW` | `200` | 長期 EMA |
| `RSI_LENGTH` | `14` | RSI 計算長 |
| `ATR_LENGTH` | `14` | ATR 計算長 |
| `SWING_N_4H` | `3` | 4時間足 swing 判定幅 |
| `SWING_N_1H` | `2` | 1時間足 swing 判定幅 |
| `SWING_N_15M` | `2` | 15分足 swing 判定幅 |

### 7.3 方向判定と confidence

| 項目 | 現在値 | 役割 |
| --- | --- | --- |
| `LONG_SHORT_DIFF_THRESHOLD` | `10` | ロング優位差のしきい値 |
| `SHORT_LONG_DIFF_THRESHOLD` | `12` | ショート優位差のしきい値 |
| `CONFIDENCE_LONG_MIN` | `40` | ロング本命通知の最低 confidence |
| `CONFIDENCE_SHORT_MIN` | `65` | ショート本命通知の最低 confidence |
| `CONFIDENCE_ALERT_CHANGE` | `7` | 前回通知との差分しきい値 |

### 7.4 RR とボラティリティ

| 項目 | 現在値 | 役割 |
| --- | --- | --- |
| `MIN_RR_RATIO` | `1.15` | 最低損益比率 |
| `SL_ATR_MULTIPLIER` | `1.5` | 損切りの ATR 倍率 |
| `MAX_ACCEPTABLE_ATR_RATIO` | `2.0` | ATR が高すぎると警戒 |
| `MIN_ACCEPTABLE_ATR_RATIO` | `0.3` | ATR が低すぎると警戒 |

### 7.5 Funding

| 項目 | 現在値 | 役割 |
| --- | --- | --- |
| `FUNDING_SHORT_WARNING` | `-0.03` | ショート警戒域 |
| `FUNDING_SHORT_PROHIBITED` | `-0.05` | ショート禁止域 |
| `FUNDING_LONG_WARNING` | `0.05` | ロング警戒域 |
| `FUNDING_LONG_PROHIBITED` | `0.08` | ロング禁止域 |

### 7.6 通知

| 項目 | 現在値 | 役割 |
| --- | --- | --- |
| `ALERT_COOLDOWN_MINUTES` | `30` | 本命通知の基本クールダウン |
| `ATTENTION_ALERT_SCORE_MIN` | `52` | 注意報の最低 score |
| `ATTENTION_ALERT_GAP_MIN` | `12` | 注意報の差分しきい値 |
| `ATTENTION_ALERT_COOLDOWN_MINUTES` | `30` | 注意報のクールダウン |

### 7.7 位置リスクと補助判定

| 項目 | 現在値 | 役割 |
| --- | --- | --- |
| `LIQUIDITY_EQUAL_THRESHOLD_PCT` | `0.0008` | 同値付近の流動性判定 |
| `POSITION_RISK_MEDIUM_THRESHOLD` | `45.0` | `SWEEP_WAIT` へ寄る境界 |
| `POSITION_RISK_HIGH_THRESHOLD` | `70.0` | `NO_TRADE_CANDIDATE` へ寄る境界 |

補足:

- `sweep_incomplete` の加点は、現在 `src/analysis/position_risk.py` 側で `+4` 運用です。
- これは `.env` ではなくコード側ロジックにあります。

### 7.8 Phase 1

| 項目 | 現在値 | 役割 |
| --- | --- | --- |
| `PHASE1_ACCOUNT_BALANCE_USD` | `10000.0` | 口座想定残高 |
| `PHASE1_BASE_RISK_PCT` | `0.5` | 基本リスク率 |
| `PHASE1_MIN_RISK_PCT` | `0.2` | 最低リスク率 |
| `PHASE1_LOSS_STREAK_STEP_PCT` | `0.1` | 連敗時の逓減幅 |
| `PHASE1_MAX_POSITION_SIZE_USD` | `3000.0` | 最大ポジション額 |
| `PHASE1_TP1_RR_MULTIPLE` | `1.0` | TP1 の RR 倍率 |
| `PHASE1_TP2_RR_MULTIPLE` | `2.0` | TP2 の RR 倍率 |
| `PHASE1_TRAIL_ATR_MULTIPLIER` | `1.5` | トレールの ATR 倍率 |
| `PHASE1_TIMEOUT_HOURS` | `12` | 期限切れ判定時間 |
| `PHASE1_LOSS_STREAK` | `0` | 既定の初期連敗数 |

## 8. 主要な参照先

- 実行設定の正本: `.env`
- 既定値の正本: `config.py`
- 判定フローの入口: `main.py`
- confidence: `src/analysis/confidence.py`
- scoring: `src/analysis/scoring.py`
- 位置評価: `src/analysis/position_risk.py`
- signal tier: `src/analysis/signal_tier.py`
- 通知判定: `src/notification/trigger.py`
- Phase 1 有効化: `src/trade/activation.py`
- Position sizing: `src/trade/position_sizing.py`
- 採点調整の早見表: `運用資料/運用/調整/採点調整シート.md`

## 9. 更新ルール

- 判定ロジックを変えたら、この文書も更新する。
- 対象は少なくとも次のどれかが変わったときです。
  - `confidence` のしきい値
  - RR 関連のしきい値
  - 注意報や本命通知のしきい値
  - `prelabel` を決める位置リスク条件
  - `signal_tier` 条件
  - `Phase 1` の有効化条件やサイズ計画
  - 本番 / 開発の AI 実行方式
- 数値だけ変えたときも更新対象です。
- `.env` とコードのどちらを変えたかが分かるように書く。

## 10. ひとことで言うと

- 判定の最終正本は `.env` とコードです。
- ただし、この文書は「今どんな考え方で、どの数値で、何が通知を止めているか」を最短でつかむための入口として、最新に保ちます。
