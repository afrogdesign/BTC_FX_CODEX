# market_map readiness レポート

- 対象 shadow 行数: 37 / 全体 1454
- フィルタ: date_from=2026-05-13
- readiness: pass
- market_map 記録あり: 33件 / 必要件数 1件
- 最新 shadow: 20260514_050500 / 2026-05-14 14:05 / subject_version=Ver02.5-v5
- 最新 shadow の空 market_map 欄: failed_breakout_state
- 最新 market_map: 20260514_050500 / 2026-05-14 14:05
- primary_state: confirmed_down=17件, early_down=8件, early_up=4件, confirmed_up=4件
- market_map_flags: long_into_major_resistance=31件, short_into_major_support=26件, support_to_resistance_flip=21件, support_to_resistance_retest_confirmed=21件, trend_flip_confirmed_down=17件, major_resistance_rejection=14件, major_support_rejection=13件, resistance_to_support_flip=12件, resistance_to_support_retest_confirmed=12件, failed_breakout_up_reversal=8件

## 判定
- market_map の実データが入り始めています。次は有効性レポートで flag 別成績を確認します。

## 次のコマンド
- ./.venv312/bin/python tools/log_feedback.py build-market-map-readiness-report --date-from 2026-05-13
- ./.venv312/bin/python tools/log_feedback.py build-market-map-effectiveness-report --date-from 2026-05-13
