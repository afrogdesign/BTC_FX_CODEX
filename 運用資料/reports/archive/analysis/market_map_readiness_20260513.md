# market_map readiness レポート

- 対象 shadow 行数: 4 / 全体 1421
- フィルタ: date_from=2026-05-13
- readiness: wait
- market_map 記録あり: 0件 / 必要件数 1件
- 最新 shadow: 20260512_180500 / 2026-05-13 03:05 / subject_version=Ver02.5-v4
- 最新 shadow の空 market_map 欄: market_map_primary_state, market_map_flags, nearest_major_support, nearest_major_resistance, active_level_role, level_flip_state, failed_breakout_state, trend_flip_state
- 最新 market_map: なし
- primary_state: なし
- market_map_flags: なし

## 判定
- market_map の実データはまだ入っていません。次回監視サイクル後に再確認します。

## 次のコマンド
- ./.venv312/bin/python tools/log_feedback.py build-market-map-readiness-report --date-from 2026-05-13
- ./.venv312/bin/python tools/log_feedback.py build-market-map-effectiveness-report --date-from 2026-05-13
