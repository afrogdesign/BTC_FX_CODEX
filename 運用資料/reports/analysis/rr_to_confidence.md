# 現行 Setup 比較

- 比較対象 shadow 行数: 1705
- フィルタ: 旧 reason=rr_below_min
- フィルタ: 現行 reason=confidence_below_min
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-05-25
- 現行 setup との差分あり: 1
- 差分ありのうち通知済み: 0
- 平均 execution_shadow: 11.0
- 平均 wait_shadow: 100.0
- 主な status 変化: watch->invalid=1件
- 主な reason 変化: rr_below_min->confidence_below_min=1件
- 主な risk_flags: liquidation_cluster_below=1件, lower_liquidity_close=1件, orderbook_ask_heavy=1件, sweep_incomplete=1件

## status別集計
- watch->invalid: 1件 / 平均 execution=11.0 / 平均 wait=100.0

## 代表例
- 20260417_150500: watch/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=SWEEP_WAIT / notified=no
