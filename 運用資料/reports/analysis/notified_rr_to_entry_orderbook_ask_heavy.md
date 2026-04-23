# 現行 Setup 比較

- 比較対象 shadow 行数: 967
- フィルタ: 通知済みのみ
- フィルタ: 旧 reason=rr_below_min
- フィルタ: 現行 reason=entry_zone_not_reached
- フィルタ: risk_flag=orderbook_ask_heavy
- 現行 setup との差分あり: 14
- 差分ありのうち通知済み: 14
- 平均 execution_shadow: 7.1
- 平均 wait_shadow: 69.0
- 主な status 変化: watch->watch=13件, invalid->watch=1件
- 主な reason 変化: rr_below_min->entry_zone_not_reached=14件
- 主な risk_flags: orderbook_ask_heavy=14件, lower_liquidity_close=12件, sweep_incomplete=12件, ask_wall_close=7件, long_flush_exhaustion=3件
- 主な通知理由: status_upgraded=10件, confidence_jump=9件, prelabel_improved=3件

## status別集計
- watch->watch: 13件 / 平均 execution=5.7 / 平均 wait=68.9
- invalid->watch: 1件 / 平均 execution=26.0 / 平均 wait=70.4

## 代表例
- 20260415_210500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260414_140500: invalid/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=RISKY_ENTRY / notified=yes
- 20260411_200500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260411_180500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260411_170500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260411_140501: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260410_220500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260410_200500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260410_150500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260410_080500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260410_030500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260409_180500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260409_160500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260316_090500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
