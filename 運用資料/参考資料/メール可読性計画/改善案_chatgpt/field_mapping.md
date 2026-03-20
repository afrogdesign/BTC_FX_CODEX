# ⭕️元データ → 自然文用データの変換表

## 1. 結論系

- `prelabel` → `headline.entry_judgement`
- `location_risk` + `critical_zone` → `headline.position_label`
- `confidence` → `headline.confidence_score` / `headline.confidence_label`

## 2. 方向感

- `bias` → `direction.bias_label`
- `phase` → `direction.phase_label`
- `market_regime` → `direction.market_regime_label`
- `signals_4h` / `signals_1h` / `signals_15m` → `direction.timeframe_view`
- `long_score` / `short_score` / `score_gap` → `direction.score_summary`

## 3. 現在地

- `current_price` → `current_state.current_price`
- `support_zones[0]` + `resistance_zones[0]` → `current_state.location_character`
- `location_risk` → `current_state.location_risk_label`

## 4. 環境

- `funding_rate_display` → `market_conditions.funding`
- `atr_ratio` → `market_conditions.volatility_label`
- `volume_ratio` → `market_conditions.volume_label`
- `oi_change_pct` → `market_conditions.oi_label`
- `cvd_price_divergence` + `cvd_slope` → `market_conditions.cvd_label`
- `orderbook_bias` → `market_conditions.orderbook_label`

## 5. ゾーン

- `support_zones[0]` → `zones.nearest_support`
- `support_zones[1]` → `zones.second_support`
- `resistance_zones[0]` → `zones.nearest_resistance`
- `resistance_zones[1]` → `zones.second_resistance`

## 6. 流動性

- `nearest_liquidity_below_price` / `nearest_liquidity_above_price` → `liquidity_context.nearest_liquidity_label`
- `liquidity_swept_recently` → `liquidity_context.sweep_status` / `liquidity_context.sweep_label`
- `largest_liquidation_price` + `distance_to_largest_liquidation` → `liquidity_context.liquidation_label`

## 7. セットアップ

- `long_setup` → `setups.long`
- `short_setup` → `setups.short`
- `rr_estimate` → `rr_label`

## 8. 注意点

- `no_trade_flags` / `risk_flags` → `risks.risk_labels`
- `prelabel_primary_reason` + 流動性情報 → `risks.primary_reason`
