# 現行 Setup 比較

- 比較対象 shadow 行数: 967
- フィルタ: 通知済みのみ
- フィルタ: 旧 reason=rr_below_min
- フィルタ: 現行 reason=entry_zone_not_reached
- 現行 setup との差分あり: 33
- 差分ありのうち通知済み: 33
- 平均 execution_shadow: 6.5
- 平均 wait_shadow: 54.9
- 主な status 変化: watch->watch=25件, invalid->watch=8件
- 主な reason 変化: rr_below_min->entry_zone_not_reached=33件
- 主な risk_flags: sweep_incomplete=25件, lower_liquidity_close=22件, orderbook_ask_heavy=14件, ask_wall_close=13件, upper_liquidity_close=6件
- 主な通知理由: confidence_jump=24件, status_upgraded=19件, prelabel_improved=16件

## status別集計
- watch->watch: 25件 / 平均 execution=3.6 / 平均 wait=52.0
- invalid->watch: 8件 / 平均 execution=15.6 / 平均 wait=64.0

## 代表例
- 20260417_090500: invalid/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=RISKY_ENTRY / notified=yes
- 20260415_210500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260414_140500: invalid/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=RISKY_ENTRY / notified=yes
- 20260411_220500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260411_200500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260411_180500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260411_170500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260411_140501: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260410_220500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260410_200500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260410_180500: invalid/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=RISKY_ENTRY / notified=yes
- 20260410_150500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260410_100501: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260410_080500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260410_030500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260409_230500: invalid/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=RISKY_ENTRY / notified=yes
- 20260409_180500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260409_160500: watch/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
- 20260409_100500: invalid/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=RISKY_ENTRY / notified=yes
- 20260409_020500: invalid/rr_below_min -> watch/entry_zone_not_reached / rr=1.30 / prelabel=RISKY_ENTRY / notified=yes
