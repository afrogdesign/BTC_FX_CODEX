# market_map 有効性レポート

- 対象 shadow 行数: 288 / 全体 1705
- フィルタ: date_from=2026-05-13
- フィルタ: date_to=2026-05-25
- market_map 記録あり: 284件
- primary_state: early_down=109件, confirmed_down=100件, confirmed_up=29件, early_up=25件, near_major_resistance=19件, active_support=1件, near_major_support=1件
- market_map_flags: short_into_major_support=242件, long_into_major_resistance=224件, support_to_resistance_flip=180件, support_to_resistance_retest_confirmed=179件, trend_flip_early_down=109件, major_resistance_rejection=102件, trend_flip_confirmed_down=100件, major_support_rejection=83件, resistance_to_support_flip=68件, resistance_to_support_retest_confirmed=68件
- level_flip_state: support_to_resistance_confirmed=179件, resistance_to_support_confirmed=68件, support_to_resistance_early=1件
- failed_breakout_state: down_reversal=57件, up_reversal=45件
- trend_flip_state: early_down=109件, confirmed_down=100件, confirmed_up=29件, early_up=25件

## flag別成績
- short_into_major_support: 勝率=51.4%, wrong_rate=11.6%, 平均MFE24h=6.20, 平均MAE24h=6.50 (n=242)
  代表例: 20260524_180500, 20260524_170500, 20260524_160500, 20260524_150500, 20260524_140501
- long_into_major_resistance: 勝率=44.9%, wrong_rate=12.1%, 平均MFE24h=5.44, 平均MAE24h=7.30 (n=224)
  代表例: 20260524_180500, 20260524_170500, 20260524_140501, 20260524_130500, 20260524_120500
- support_to_resistance_flip: 勝率=59.6%, wrong_rate=11.7%, 平均MFE24h=7.23, 平均MAE24h=5.28 (n=180)
  代表例: 20260524_160500, 20260524_150500, 20260524_140501, 20260524_130500, 20260524_120500
- trend_flip_confirmed_down: 勝率=55.2%, wrong_rate=13.0%, 平均MFE24h=7.43, 平均MAE24h=5.23 (n=100)
  代表例: 20260524_160500, 20260524_150500, 20260524_000500, 20260523_120500, 20260523_090500
- resistance_to_support_flip: 勝率=39.3%, wrong_rate=16.2%, 平均MFE24h=4.02, 平均MAE24h=8.66 (n=68)
  代表例: 20260524_100500, 20260524_070500, 20260523_210500, 20260523_140500, 20260523_040500
- failed_breakout_down_reversal: 勝率=33.3%, wrong_rate=8.8%, 平均MFE24h=7.17, 平均MAE24h=5.68 (n=57)
  代表例: 20260524_180500, 20260524_010500, 20260523_150500, 20260523_120500, 20260522_120500
- failed_breakout_up_reversal: 勝率=35.7%, wrong_rate=20.0%, 平均MFE24h=3.97, 平均MAE24h=9.71 (n=45)
  代表例: 20260524_170500, 20260524_140501, 20260524_120500, 20260524_110501, 20260524_020500
- trend_flip_confirmed_up: 勝率=37.5%, wrong_rate=31.0%, 平均MFE24h=2.34, 平均MAE24h=11.43 (n=29)
  代表例: 20260524_100500, 20260524_020500, 20260523_210500, 20260522_110500, 20260521_130500

## 次に見る場所
- src/analysis/market_map.py
- src/analysis/scoring.py
- logs/csv/shadow_log.csv
