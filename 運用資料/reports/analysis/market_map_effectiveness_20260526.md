# market_map 有効性レポート

- 対象 shadow 行数: 320 / 全体 1737
- フィルタ: date_from=2026-05-13
- フィルタ: date_to=2026-05-26
- market_map 記録あり: 316件
- primary_state: early_down=117件, confirmed_down=117件, confirmed_up=33件, early_up=25件, near_major_resistance=22件, active_support=1件, near_major_support=1件
- market_map_flags: short_into_major_support=270件, long_into_major_resistance=255件, support_to_resistance_flip=204件, support_to_resistance_retest_confirmed=203件, trend_flip_early_down=117件, trend_flip_confirmed_down=117件, major_resistance_rejection=115件, major_support_rejection=93件, resistance_to_support_flip=72件, resistance_to_support_retest_confirmed=72件
- level_flip_state: support_to_resistance_confirmed=203件, resistance_to_support_confirmed=72件, support_to_resistance_early=1件
- failed_breakout_state: down_reversal=64件, up_reversal=49件
- trend_flip_state: early_down=117件, confirmed_down=117件, confirmed_up=33件, early_up=25件

## flag別成績
- short_into_major_support: 勝率=51.9%, wrong_rate=12.6%, 平均MFE24h=6.10, 平均MAE24h=6.53 (n=270)
  代表例: 20260526_030500, 20260526_020500, 20260526_010501, 20260526_000500, 20260525_230500
- long_into_major_resistance: 勝率=45.5%, wrong_rate=12.9%, 平均MFE24h=5.36, 平均MAE24h=7.22 (n=255)
  代表例: 20260526_030500, 20260526_020500, 20260526_010501, 20260526_000500, 20260525_230500
- support_to_resistance_flip: 勝率=57.1%, wrong_rate=12.3%, 平均MFE24h=7.16, 平均MAE24h=5.35 (n=204)
  代表例: 20260526_030500, 20260526_020500, 20260526_010501, 20260526_000500, 20260525_230500
- trend_flip_confirmed_down: 勝率=50.0%, wrong_rate=14.5%, 平均MFE24h=7.16, 平均MAE24h=5.37 (n=117)
  代表例: 20260526_020500, 20260526_010501, 20260526_000500, 20260525_230500, 20260525_220500
- resistance_to_support_flip: 勝率=40.0%, wrong_rate=16.7%, 平均MFE24h=3.92, 平均MAE24h=8.67 (n=72)
  代表例: 20260525_170500, 20260525_150500, 20260525_140500, 20260525_130500, 20260524_100500
- failed_breakout_down_reversal: 勝率=38.9%, wrong_rate=10.9%, 平均MFE24h=6.82, 平均MAE24h=5.42 (n=64)
  代表例: 20260525_230500, 20260525_210500, 20260525_190500, 20260525_070500, 20260525_020500
- failed_breakout_up_reversal: 勝率=35.7%, wrong_rate=18.4%, 平均MFE24h=3.97, 平均MAE24h=9.71 (n=49)
  代表例: 20260526_030500, 20260526_020500, 20260526_010501, 20260525_160500, 20260524_170500
- trend_flip_confirmed_up: 勝率=38.9%, wrong_rate=30.3%, 平均MFE24h=2.36, 平均MAE24h=11.14 (n=33)
  代表例: 20260525_170500, 20260525_150500, 20260525_140500, 20260525_130500, 20260524_100500

## 次に見る場所
- src/analysis/market_map.py
- src/analysis/scoring.py
- logs/csv/shadow_log.csv
