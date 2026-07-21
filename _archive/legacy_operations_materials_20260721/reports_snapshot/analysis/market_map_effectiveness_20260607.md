# market_map 有効性レポート

- 対象 shadow 行数: 593 / 全体 2010
- フィルタ: date_from=2026-05-13
- フィルタ: date_to=2026-06-07
- market_map 記録あり: 589件
- primary_state: confirmed_down=252件, early_down=188件, confirmed_up=49件, early_up=47件, near_major_resistance=37件, near_major_support=9件, active_support=6件, active_resistance=1件
- market_map_flags: short_into_major_support=476件, long_into_major_resistance=414件, support_to_resistance_flip=385件, support_to_resistance_retest_confirmed=382件, trend_flip_confirmed_down=252件, major_resistance_rejection=191件, trend_flip_early_down=188件, major_support_rejection=171件, resistance_to_support_flip=119件, resistance_to_support_retest_confirmed=119件
- level_flip_state: support_to_resistance_confirmed=382件, resistance_to_support_confirmed=119件, support_to_resistance_early=3件
- failed_breakout_state: down_reversal=107件, up_reversal=91件
- trend_flip_state: confirmed_down=252件, early_down=188件, confirmed_up=49件, early_up=47件

## flag別成績
- short_into_major_support: 勝率=60.3%, wrong_rate=11.1%, 平均MFE24h=9.32, 平均MAE24h=4.49 (n=476)
  代表例: 20260606_180500, 20260606_170500, 20260606_160500, 20260606_150500, 20260606_140500
- long_into_major_resistance: 勝率=54.3%, wrong_rate=12.1%, 平均MFE24h=7.78, 平均MAE24h=4.91 (n=414)
  代表例: 20260606_170500, 20260606_160500, 20260606_150500, 20260606_140500, 20260606_130500
- support_to_resistance_flip: 勝率=70.2%, wrong_rate=8.8%, 平均MFE24h=9.67, 平均MAE24h=3.46 (n=385)
  代表例: 20260606_180500, 20260606_170500, 20260606_160500, 20260606_150500, 20260606_140500
- trend_flip_confirmed_down: 勝率=75.8%, wrong_rate=8.3%, 平均MFE24h=10.52, 平均MAE24h=2.89 (n=252)
  代表例: 20260606_170500, 20260606_160500, 20260606_120500, 20260606_110500, 20260606_010500
- resistance_to_support_flip: 勝率=35.9%, wrong_rate=21.8%, 平均MFE24h=6.60, 平均MAE24h=5.42 (n=119)
  代表例: 20260606_130500, 20260605_050500, 20260605_000501, 20260604_230500, 20260604_210500
- failed_breakout_down_reversal: 勝率=60.7%, wrong_rate=9.3%, 平均MFE24h=7.91, 平均MAE24h=4.46 (n=107)
  代表例: 20260606_150500, 20260606_140500, 20260606_130500, 20260606_090500, 20260605_230500
- failed_breakout_up_reversal: 勝率=56.5%, wrong_rate=14.3%, 平均MFE24h=5.14, 平均MAE24h=7.92 (n=91)
  代表例: 20260606_180500, 20260606_110500, 20260606_000500, 20260605_200500, 20260605_170500
- trend_flip_confirmed_up: 勝率=36.4%, wrong_rate=32.7%, 平均MFE24h=2.91, 平均MAE24h=9.06 (n=49)
  代表例: 20260531_010500, 20260531_000500, 20260530_230500, 20260530_220500, 20260530_210500

## 次に見る場所
- src/analysis/market_map.py
- src/analysis/scoring.py
- logs/csv/shadow_log.csv
