# market_map 有効性レポート

- 対象 shadow 行数: 120 / 全体 1537
- フィルタ: date_from=2026-05-13
- フィルタ: date_to=2026-05-18
- market_map 記録あり: 116件
- primary_state: confirmed_down=56件, early_down=32件, confirmed_up=16件, early_up=8件, near_major_resistance=4件
- market_map_flags: short_into_major_support=101件, long_into_major_resistance=92件, support_to_resistance_flip=75件, support_to_resistance_retest_confirmed=75件, trend_flip_confirmed_down=56件, major_resistance_rejection=44件, major_support_rejection=40件, trend_flip_early_down=32件, resistance_to_support_flip=31件, resistance_to_support_retest_confirmed=31件
- level_flip_state: support_to_resistance_confirmed=75件, resistance_to_support_confirmed=31件
- failed_breakout_state: down_reversal=25件, up_reversal=21件
- trend_flip_state: confirmed_down=56件, early_down=32件, confirmed_up=16件, early_up=8件

## flag別成績
- short_into_major_support: 勝率=57.6%, wrong_rate=12.9%, 平均MFE24h=6.36, 平均MAE24h=6.65 (n=101)
  代表例: 20260517_180500, 20260517_170500, 20260517_160500, 20260517_150500, 20260517_140501
- long_into_major_resistance: 勝率=53.1%, wrong_rate=13.0%, 平均MFE24h=5.90, 平均MAE24h=7.50 (n=92)
  代表例: 20260517_180500, 20260517_170500, 20260517_160500, 20260517_140501, 20260517_130500
- support_to_resistance_flip: 勝率=69.6%, wrong_rate=13.3%, 平均MFE24h=7.56, 平均MAE24h=5.52 (n=75)
  代表例: 20260517_170500, 20260517_160500, 20260517_150500, 20260517_140501, 20260517_120500
- trend_flip_confirmed_down: 勝率=56.2%, wrong_rate=16.1%, 平均MFE24h=6.98, 平均MAE24h=5.84 (n=56)
  代表例: 20260517_120500, 20260517_110500, 20260517_090500, 20260517_070501, 20260517_060500
- resistance_to_support_flip: 勝率=35.7%, wrong_rate=16.1%, 平均MFE24h=2.52, 平均MAE24h=10.34 (n=31)
  代表例: 20260517_180500, 20260517_100500, 20260517_050500, 20260517_040500, 20260515_210500
- failed_breakout_down_reversal: 勝率=44.4%, wrong_rate=8.0%, 平均MFE24h=6.33, 平均MAE24h=5.74 (n=25)
  代表例: 20260517_140501, 20260517_130500, 20260517_060500, 20260517_050500, 20260517_040500
- failed_breakout_up_reversal: 勝率=44.4%, wrong_rate=28.6%, 平均MFE24h=3.50, 平均MAE24h=8.45 (n=21)
  代表例: 20260517_010500, 20260516_140500, 20260516_070500, 20260516_020500, 20260515_210500
- trend_flip_confirmed_up: 勝率=37.5%, wrong_rate=31.2%, 平均MFE24h=1.59, 平均MAE24h=13.09 (n=16)
  代表例: 20260517_180500, 20260517_100500, 20260516_020500, 20260515_200500, 20260515_190500

## 次に見る場所
- src/analysis/market_map.py
- src/analysis/scoring.py
- logs/csv/shadow_log.csv
