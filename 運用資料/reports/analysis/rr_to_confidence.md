# 現行 Setup 比較

- 比較対象 shadow 行数: 967
- フィルタ: 旧 reason=rr_below_min
- フィルタ: 現行 reason=confidence_below_min
- 現行 setup との差分あり: 487
- 差分ありのうち通知済み: 64
- 平均 execution_shadow: 2.0
- 平均 wait_shadow: 51.3
- 主な status 変化: invalid->invalid=278件, watch->invalid=209件
- 主な reason 変化: rr_below_min->confidence_below_min=487件
- 主な risk_flags: sweep_incomplete=425件, lower_liquidity_close=277件, upper_liquidity_close=182件, ask_wall_close=150件, orderbook_ask_heavy=144件
- 主な通知理由: attention_gap_crossed=46件, attention_score_crossed=42件, attention_bias_changed=26件, confidence_jump=2件, status_upgraded=1件

## status別集計
- invalid->invalid: 278件 / 平均 execution=2.5 / 平均 wait=47.0
- watch->invalid: 209件 / 平均 execution=1.3 / 平均 wait=56.9

## 代表例
- 20260417_150500: watch/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=SWEEP_WAIT / notified=no
- 20260417_140500: invalid/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=RISKY_ENTRY / notified=no
- 20260417_120500: watch/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=SWEEP_WAIT / notified=no
- 20260417_110500: invalid/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=NO_TRADE_CANDIDATE / notified=no
- 20260417_100500: invalid/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=NO_TRADE_CANDIDATE / notified=no
- 20260417_080500: invalid/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=RISKY_ENTRY / notified=no
- 20260417_070500: watch/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=SWEEP_WAIT / notified=no
- 20260417_060500: invalid/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=NO_TRADE_CANDIDATE / notified=no
- 20260417_050500: invalid/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=RISKY_ENTRY / notified=no
- 20260417_040500: invalid/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=NO_TRADE_CANDIDATE / notified=no
- 20260417_030758: invalid/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=RISKY_ENTRY / notified=no
- 20260417_020657: watch/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=SWEEP_WAIT / notified=no
- 20260417_010500: invalid/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=RISKY_ENTRY / notified=no
- 20260417_000556: invalid/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=RISKY_ENTRY / notified=no
- 20260416_230500: watch/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=SWEEP_WAIT / notified=no
- 20260416_220500: watch/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=SWEEP_WAIT / notified=no
- 20260416_210500: invalid/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=RISKY_ENTRY / notified=no
- 20260416_202320: invalid/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=RISKY_ENTRY / notified=yes
- 20260416_180500: invalid/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=NO_TRADE_CANDIDATE / notified=no
- 20260416_170500: watch/rr_below_min -> invalid/confidence_below_min / rr=1.30 / prelabel=SWEEP_WAIT / notified=yes
