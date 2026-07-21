# market_map 有効性レポート

- 対象 shadow 行数: 537 / 全体 1954
- フィルタ: date_from=2026-05-13
- フィルタ: date_to=2026-06-04
- market_map 記録あり: 533件
- primary_state: confirmed_down=224件, early_down=171件, confirmed_up=49件, early_up=39件, near_major_resistance=37件, active_support=6件, near_major_support=6件, active_resistance=1件
- market_map_flags: short_into_major_support=429件, long_into_major_resistance=379件, support_to_resistance_flip=345件, support_to_resistance_retest_confirmed=342件, trend_flip_confirmed_down=224件, trend_flip_early_down=171件, major_resistance_rejection=170件, major_support_rejection=154件, resistance_to_support_flip=108件, resistance_to_support_retest_confirmed=108件
- level_flip_state: support_to_resistance_confirmed=342件, resistance_to_support_confirmed=108件, support_to_resistance_early=3件
- failed_breakout_state: down_reversal=96件, up_reversal=84件
- trend_flip_state: confirmed_down=224件, early_down=171件, confirmed_up=49件, early_up=39件

## flag別成績
- short_into_major_support: 勝率=62.0%, wrong_rate=10.3%, 平均MFE24h=8.58, 平均MAE24h=5.01 (n=429)
  代表例: 20260603_230500, 20260603_220500, 20260603_210500, 20260603_200500, 20260603_190500
- long_into_major_resistance: 勝率=54.2%, wrong_rate=10.6%, 平均MFE24h=6.92, 平均MAE24h=5.46 (n=379)
  代表例: 20260603_190500, 20260603_150500, 20260603_140500, 20260603_130500, 20260603_120500
- support_to_resistance_flip: 勝率=75.3%, wrong_rate=7.0%, 平均MFE24h=9.28, 平均MAE24h=3.86 (n=345)
  代表例: 20260604_040500, 20260604_010500, 20260604_000500, 20260603_230500, 20260603_210500
- trend_flip_confirmed_down: 勝率=77.6%, wrong_rate=7.1%, 平均MFE24h=10.21, 平均MAE24h=3.32 (n=224)
  代表例: 20260604_040500, 20260604_010500, 20260604_000500, 20260603_230500, 20260603_210500
- resistance_to_support_flip: 勝率=30.6%, wrong_rate=21.3%, 平均MFE24h=4.76, 平均MAE24h=6.26 (n=108)
  代表例: 20260531_230500, 20260531_120500, 20260531_010500, 20260531_000500, 20260530_230500
- failed_breakout_down_reversal: 勝率=69.2%, wrong_rate=6.2%, 平均MFE24h=6.80, 平均MAE24h=4.67 (n=96)
  代表例: 20260603_130500, 20260603_120500, 20260603_100500, 20260603_090500, 20260602_220500
- failed_breakout_up_reversal: 勝率=45.5%, wrong_rate=14.3%, 平均MFE24h=5.25, 平均MAE24h=8.63 (n=84)
  代表例: 20260604_010500, 20260603_220500, 20260603_200500, 20260603_050500, 20260603_040500
- trend_flip_confirmed_up: 勝率=22.7%, wrong_rate=32.7%, 平均MFE24h=3.03, 平均MAE24h=8.72 (n=49)
  代表例: 20260531_010500, 20260531_000500, 20260530_230500, 20260530_220500, 20260530_210500

## 次に見る場所
- src/analysis/market_map.py
- src/analysis/scoring.py
- logs/csv/shadow_log.csv
