# ログ分析レポート

## 1. 集計条件
- 対象CSV: `logs/csv/trades.csv`
- 抽出条件: {'year': 'all', 'month': 'all', 'from': 'none', 'to': 'none'}
- 対象期間: 2026-03-09T19:35:22.868644+09:00 〜 2026-03-09T22:07:19.270223+09:00
- 件数: 4

## 2. 全体KPI
- 平均 confidence: `54.50`
- high confidence (>=80): `2` 件 (50.0%)
- primary_setup_status=invalid: `4` 件 (100.0%)
- ai_error 発生: `4` 件 (100.0%)

## 3. 分布
### bias
- short: 4
### phase
- range: 2
- trend_following: 2
### market_regime
- transition: 2
- downtrend: 2
### primary_setup_status
- invalid: 4

## 4. no_trade_flags 上位
- RR_insufficient: 4
- RR_insufficient_long: 4
- RR_insufficient_short: 4
- Critical_zone_warning: 2

## 5. 年次集計
| year | count | avg_conf | invalid_rate | ai_error_rate |
|---|---:|---:|---:|---:|
| 2026 | 4 | 54.50 | 100.0% | 100.0% |

## 6. 月次集計
| month | count | avg_conf | invalid_rate | ai_error_rate |
|---|---:|---:|---:|---:|
| 2026-03 | 4 | 54.50 | 100.0% | 100.0% |

## 7. 時間帯別（JST）
| hour | count | avg_conf | invalid_rate |
|---|---:|---:|---:|
| 19:00 | 2 | 19.00 | 100.0% |
| 21:00 | 1 | 90.00 | 100.0% |
| 22:00 | 1 | 90.00 | 100.0% |

## 8. 改善アクション候補
1. サンプル数が少ないため、まずは50件以上のログを蓄積してから閾値調整する。
2. invalid比率が高い。`MIN_RR_RATIO` と `critical_zone` 周りの判定条件を優先レビューする。
3. AIエラー率が高い。`AI_TIMEOUT_SEC` と `AI_RETRY_COUNT` を見直し、API障害時の影響を下げる。
4. `RR_insufficient` が最多。S/R算出ロジックまたは `MIN_RR_RATIO` の妥当性を検証する。

## 9. 制約
- このログには実トレード損益（PnL）がないため、勝率や期待値の厳密検証は不可。
- 将来は約定結果（entry/exit/pnl）を記録すると、改善精度が大きく上がる。