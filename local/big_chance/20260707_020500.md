## Big Chance / Failed Thesis

- schema_version: big_chance_failed_thesis.v1
- present: true
- side: short
- type: long_failed_to_short
- status: follow_through
- score: 88
- grade: A
- headline: ロング失敗→ショート候補
- operator_summary: ロング仮説が崩れたため、ショート側の Big Chance を report-only で監視します。HTF の反転と 15m の起動を分けて見るのが要点です。

## Macro Context
- market_regime: transition
- phase: range
- signals_4h: wait
- signals_1h: wait
- signals_15m: wait
- market_map_primary_state: early_down
- level_flip_state: support_to_resistance_confirmed
- trend_flip_state: early_down
- failed_breakout_state: 
- transition_direction: up
- active_level_role: resistance
- previous_signal_id: 20260707_010500
- previous_notification_kind: attention
- previous_bias: long

## Failed Thesis
- prior_side: long
- failure_reason: ['failed_long_thesis', 'support_to_resistance_flip', 'trend_flip_early_down', 'short_side_activation']
- failure_reason_labels: ['ロング仮説が崩れた', 'サポート→レジスタンス反転', '早期下方向転換', 'ショート候補']
- thesis_summary: Failed thesis is opportunity

## Activation
- activation_tf: 15m
- activation_condition: signals_15m == short
- activation_state: watch
- price_position: inside_shallow_retest_zone
- price_position_trigger: above_zones

## Invalidation
- invalidation_tf: 15m
- invalidation_condition: signals_15m == long and signals_1h == long
- invalidation_state: watch
- price_position: above_zones
- price_position_trigger: below_zones

## Reason Codes
- previous_side_failed
- support_to_resistance_flip
- support_to_resistance_retest_confirmed
- trend_flip_early_down
- 1h_wait_pressure
- failed_long_thesis
- short_side_activation

## Reason Labels
- 前回仮説が崩れた流れ
- サポート→レジスタンス反転
- サポート→レジスタンスの再確認
- 早期下方向転換
- 1時間足は様子見
- ロング仮説が崩れた
- ショート候補

## Evidence
- current_price: 63815.0
- current_price_position_long: above_zones
- current_price_position_short: inside_shallow_retest_zone
- market_map_primary_state: early_down
- market_map_flags: ["long_into_major_resistance", "short_into_major_support", "support_to_resistance_flip", "support_to_resistance_retest_confirmed", "trend_flip_early_down"]
- level_flip_state: support_to_resistance_confirmed
- trend_flip_state: early_down
- failed_breakout_state: 
- transition_direction: up
- bias: short
- previous_bias: long
- long_value_defense: {"side": "long", "lifecycle_state": "continuation_candidate", "market_entry_status": "invalid", "shallow_retest_zone": {"low": 63489.99, "high": 63670.41}, "shallow_retest_risk": "high", "value_defense_zone": {"low": 63103.89, "high": 63277.41}, "defense_zone_basis": "next_support_below_shallow_zone", "invalidation_zone": {"low": 63154.18, "high": 63188.18}, "reclaim_trigger": 63383.7, "continuation_trigger": 63580.2, "operator_guidance": "浅い押し目だけで決め打ちせず、本命押し目と invalidation を先に確認する。", "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually"}
- short_value_defense: {"side": "short", "lifecycle_state": "shallow_retest_risk", "market_entry_status": "invalid", "shallow_retest_zone": {"low": 63802.49, "high": 64028.41}, "shallow_retest_risk": "high", "value_defense_zone": {"low": 64255.59, "high": 64365.51}, "defense_zone_basis": "next_resistance_above_shallow_zone", "invalidation_zone": {"low": 64330.22, "high": 64364.22}, "reclaim_trigger": 64142.0, "continuation_trigger": 63915.45, "operator_guidance": "浅い戻り売りだけで決め打ちせず、本命戻り売りと invalidation を先に確認する。", "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually"}

## Normal Score Context
- bias: short
- signals_4h: wait
- signals_1h: wait
- signals_15m: wait
- long_display_score: 46
- short_display_score: 59
- score_gap: -13
- confidence: 29
- primary_setup_status: invalid
- primary_setup_reason: confidence_below_min
- signal_tier: normal
- trade_execution_gate: blocked

## Safety Boundary
- report-only / not FORMAL_GO / no automatic order / human decides manually