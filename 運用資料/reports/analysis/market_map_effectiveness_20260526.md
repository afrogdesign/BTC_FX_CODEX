# market_map 有効性レポート

- 対象 shadow 行数: 906 / 全体 1726
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-05-26
- market_map 記録あり: 305件
- primary_state: early_down=113件, confirmed_down=111件, confirmed_up=32件, early_up=25件, near_major_resistance=22件, active_support=1件, near_major_support=1件
- market_map_flags: short_into_major_support=259件, long_into_major_resistance=244件, support_to_resistance_flip=194件, support_to_resistance_retest_confirmed=193件, trend_flip_early_down=113件, trend_flip_confirmed_down=111件, major_resistance_rejection=109件, major_support_rejection=88件, resistance_to_support_flip=71件, resistance_to_support_retest_confirmed=71件
- level_flip_state: support_to_resistance_confirmed=193件, resistance_to_support_confirmed=71件, support_to_resistance_early=1件
- failed_breakout_state: down_reversal=61件, up_reversal=46件
- trend_flip_state: early_down=113件, confirmed_down=111件, confirmed_up=32件, early_up=25件

## flag別成績
- short_into_major_support: 勝率=51.9%, wrong_rate=12.7%, 平均MFE24h=6.02, 平均MAE24h=6.50 (n=259)
  代表例: 20260525_160500, 20260525_150500, 20260525_140500, 20260525_130500, 20260525_120500
- long_into_major_resistance: 勝率=45.3%, wrong_rate=13.1%, 平均MFE24h=5.23, 平均MAE24h=7.20 (n=244)
  代表例: 20260525_160500, 20260525_150500, 20260525_140500, 20260525_130500, 20260525_120500
- support_to_resistance_flip: 勝率=56.4%, wrong_rate=12.9%, 平均MFE24h=6.91, 平均MAE24h=5.44 (n=194)
  代表例: 20260525_160500, 20260525_120500, 20260525_110500, 20260525_090500, 20260525_080500
- trend_flip_confirmed_down: 勝率=50.0%, wrong_rate=15.3%, 平均MFE24h=6.82, 平均MAE24h=5.37 (n=111)
  代表例: 20260525_120500, 20260525_110500, 20260525_090500, 20260525_080500, 20260525_040500
- resistance_to_support_flip: 勝率=41.4%, wrong_rate=15.5%, 平均MFE24h=4.05, 平均MAE24h=8.41 (n=71)
  代表例: 20260525_150500, 20260525_140500, 20260525_130500, 20260524_100500, 20260524_070500
- failed_breakout_down_reversal: 勝率=35.3%, wrong_rate=11.5%, 平均MFE24h=6.54, 平均MAE24h=5.74 (n=61)
  代表例: 20260525_070500, 20260525_020500, 20260525_000501, 20260524_230500, 20260524_180500
- failed_breakout_up_reversal: 勝率=35.7%, wrong_rate=19.6%, 平均MFE24h=3.97, 平均MAE24h=9.71 (n=46)
  代表例: 20260525_160500, 20260524_170500, 20260524_140501, 20260524_120500, 20260524_110501
- trend_flip_confirmed_up: 勝率=41.2%, wrong_rate=28.1%, 平均MFE24h=2.50, 平均MAE24h=10.85 (n=32)
  代表例: 20260525_150500, 20260525_140500, 20260525_130500, 20260524_100500, 20260524_020500

## 次に見る場所
- src/analysis/market_map.py
- src/analysis/scoring.py
- logs/csv/shadow_log.csv
