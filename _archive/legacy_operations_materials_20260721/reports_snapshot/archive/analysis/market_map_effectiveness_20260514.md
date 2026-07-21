# market_map 有効性レポート

- 対象 shadow 行数: 37 / 全体 1454
- フィルタ: date_from=2026-05-13
- フィルタ: date_to=2026-05-14
- market_map 記録あり: 33件
- primary_state: confirmed_down=17件, early_down=8件, early_up=4件, confirmed_up=4件
- market_map_flags: long_into_major_resistance=31件, short_into_major_support=26件, support_to_resistance_flip=21件, support_to_resistance_retest_confirmed=21件, trend_flip_confirmed_down=17件, major_resistance_rejection=14件, major_support_rejection=13件, resistance_to_support_flip=12件, resistance_to_support_retest_confirmed=12件, failed_breakout_up_reversal=8件
- level_flip_state: support_to_resistance_confirmed=21件, resistance_to_support_confirmed=12件
- failed_breakout_state: up_reversal=8件, down_reversal=6件
- trend_flip_state: confirmed_down=17件, early_down=8件, early_up=4件, confirmed_up=4件

## flag別成績
- long_into_major_resistance: 勝率=57.1%, wrong_rate=16.1%, 平均MFE24h=6.86, 平均MAE24h=6.64 (n=31)
  代表例: 20260514_050500, 20260514_040500, 20260514_030500, 20260514_020500, 20260514_000500
- short_into_major_support: 勝率=66.7%, wrong_rate=11.5%, 平均MFE24h=7.85, 平均MAE24h=5.68 (n=26)
  代表例: 20260514_050500, 20260514_030500, 20260514_020500, 20260514_010500, 20260514_000500
- support_to_resistance_flip: 勝率=70.0%, wrong_rate=14.3%, 平均MFE24h=9.12, 平均MAE24h=2.28 (n=21)
  代表例: 20260514_040500, 20260514_030500, 20260514_000500, 20260513_220500, 20260513_210500
- trend_flip_confirmed_down: 勝率=57.1%, wrong_rate=17.6%, 平均MFE24h=8.77, 平均MAE24h=2.66 (n=17)
  代表例: 20260514_000500, 20260513_220500, 20260513_210500, 20260513_190500, 20260513_180500
- resistance_to_support_flip: 勝率=40.0%, wrong_rate=16.7%, 平均MFE24h=1.65, 平均MAE24h=14.45 (n=12)
  代表例: 20260514_050500, 20260514_020500, 20260514_010500, 20260513_230500, 20260513_180500
- failed_breakout_up_reversal: 勝率=100.0%, wrong_rate=0.0%, 平均MFE24h=9.00, 平均MAE24h=1.84 (n=8)
  代表例: 20260514_040500, 20260514_030500, 20260514_000500, 20260513_110500, 20260513_070500
- failed_breakout_down_reversal: 勝率=50.0%, wrong_rate=16.7%, 平均MFE24h=11.09, 平均MAE24h=2.43 (n=6)
  代表例: 20260514_010500, 20260513_180500, 20260513_040501, 20260513_020500, 20260512_200500
- trend_flip_confirmed_up: 勝率=0.0%, wrong_rate=50.0%, 平均MFE24h=0.47, 平均MAE24h=19.68 (n=4)
  代表例: 20260513_100500, 20260513_090500, 20260513_050501, 20260513_030500

## 次に見る場所
- src/analysis/market_map.py
- src/analysis/scoring.py
- logs/csv/shadow_log.csv
