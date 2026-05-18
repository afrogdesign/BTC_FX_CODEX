# market_map 有効性レポート

- 対象 shadow 行数: 72 / 全体 1489
- フィルタ: date_from=2026-05-13
- フィルタ: date_to=2026-05-16
- market_map 記録あり: 68件
- primary_state: confirmed_down=33件, early_down=15件, confirmed_up=11件, early_up=7件, near_major_resistance=2件
- market_map_flags: long_into_major_resistance=58件, short_into_major_support=56件, support_to_resistance_flip=39件, support_to_resistance_retest_confirmed=39件, trend_flip_confirmed_down=33件, major_resistance_rejection=27件, resistance_to_support_flip=25件, resistance_to_support_retest_confirmed=25件, major_support_rejection=23件, failed_breakout_down_reversal=17件
- level_flip_state: support_to_resistance_confirmed=39件, resistance_to_support_confirmed=25件
- failed_breakout_state: down_reversal=17件, up_reversal=15件
- trend_flip_state: confirmed_down=33件, early_down=15件, confirmed_up=11件, early_up=7件

## flag別成績
- long_into_major_resistance: 勝率=52.2%, wrong_rate=13.8%, 平均MFE24h=5.99, 平均MAE24h=8.31 (n=58)
  代表例: 20260515_180500, 20260515_170500, 20260515_160500, 20260515_150500, 20260515_140500
- short_into_major_support: 勝率=54.5%, wrong_rate=14.3%, 平均MFE24h=6.42, 平均MAE24h=7.32 (n=56)
  代表例: 20260515_170500, 20260515_160500, 20260515_150500, 20260515_140500, 20260515_130500
- support_to_resistance_flip: 勝率=58.8%, wrong_rate=17.9%, 平均MFE24h=7.52, 平均MAE24h=6.51 (n=39)
  代表例: 20260515_150500, 20260515_140500, 20260515_130500, 20260515_120500, 20260515_100500
- trend_flip_confirmed_down: 勝率=45.5%, wrong_rate=18.2%, 平均MFE24h=6.56, 平均MAE24h=7.04 (n=33)
  代表例: 20260515_150500, 20260515_140500, 20260515_130500, 20260515_120500, 20260515_100500
- resistance_to_support_flip: 勝率=40.0%, wrong_rate=16.0%, 平均MFE24h=2.56, 平均MAE24h=11.16 (n=25)
  代表例: 20260515_180500, 20260515_170500, 20260515_160500, 20260515_030500, 20260515_010500
- failed_breakout_down_reversal: 勝率=42.9%, wrong_rate=11.8%, 平均MFE24h=7.30, 平均MAE24h=6.78 (n=17)
  代表例: 20260515_150500, 20260515_020500, 20260515_000500, 20260514_230500, 20260514_220500
- failed_breakout_up_reversal: 勝率=60.0%, wrong_rate=26.7%, 平均MFE24h=4.70, 平均MAE24h=6.44 (n=15)
  代表例: 20260515_160500, 20260515_130500, 20260515_100500, 20260515_060500, 20260515_050500
- trend_flip_confirmed_up: 勝率=33.3%, wrong_rate=27.3%, 平均MFE24h=1.42, 平均MAE24h=14.51 (n=11)
  代表例: 20260515_180500, 20260515_010500, 20260514_190500, 20260514_180500, 20260514_170500

## 次に見る場所
- src/analysis/market_map.py
- src/analysis/scoring.py
- logs/csv/shadow_log.csv
