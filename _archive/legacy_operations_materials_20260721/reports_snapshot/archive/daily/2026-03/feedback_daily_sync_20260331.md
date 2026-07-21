# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 32 件です。近似PF は 0.75、全体勝率は 71.9% でした。
- 人のレビューでは「入る判断に使えた」が最も多く、3 件でした。
- 平均の役立ち度は 2.25 / 5 でした。
- 目立った改善候補はまだ確定していません。

## 2. 今回の対象
- 集計期間: 2026-03-24 13:05 〜 2026-03-30 01:05
- 総観測件数: 32
- データ品質の内訳: ok=32
- 近似PF: 0.75

## 3. 人のレビュー要約
- 入る判断に使えた: 3件
- 通知が遅すぎた: 1件
- 平均の役立ち度: 2.25 / 5
- 値動きの主因の入力率: 12.5%

## 4. 改善候補
- まだ改善候補を絞れるだけのデータがありません

## 5. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- downtrend: 勝率=100.0%, 平均MFE=12.38, 平均MAE=7.98 (n=4) / データ不足 4/30
- range: 勝率=66.7%, 平均MFE=2.72, 平均MAE=5.06 (n=9) / データ不足 9/30
- transition: 勝率=70.6%, 平均MFE=5.10, 平均MAE=6.73 (n=17) / データ不足 17/30
- uptrend: 勝率=50.0%, 平均MFE=0.35, 平均MAE=11.60 (n=2) / データ不足 2/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=71.9%, 平均MFE=5.04, 平均MAE=6.72 (n=32)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=4.06, 平均MAE=4.13 (n=2) / データ不足 2/30
- RISKY_ENTRY: 勝率=60.0%, 平均MFE=2.91, 平均MAE=6.23 (n=10) / データ不足 10/30
- SWEEP_WAIT: 勝率=76.5%, 平均MFE=6.97, 平均MAE=7.26 (n=17) / データ不足 17/30
- NO_TRADE_CANDIDATE: 勝率=66.7%, 平均MFE=1.88, 平均MAE=7.03 (n=3) / データ不足 3/30

### bias別件数・勝率
- long: 勝率=58.3% (n=12) / データ不足 12/30
- short: 勝率=80.0% (n=20) / データ不足 20/30

### 成績指標
- 全体勝率: 71.9%
- 平均MFE(signal_based): 5.04
- 平均MAE(signal_based): 6.72
- 平均MFE(entry_ready_based): 4.34
- 平均MAE(entry_ready_based): 7.09
- TP1先行率: 71.9%

### 通知品質
- A: 通知して良かった = 23件
- B: 通知したが微妙 = 9件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 32
- 本有効件数: 1
- 参考ログ件数: 31
- 平均 risk_percent_applied: 0.50
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 50.00
- 平均 position_size_usd: 3000.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 100.0%
- 平均 timeout_hours: 12.00

### risk_flags 有効性比較
- lower_liquidity_close: negative_rate=91.7% (n=12)
- upper_liquidity_close: negative_rate=70.6% (n=17)
- sweep_incomplete: negative_rate=69.0% (n=29)
- bid_wall_close: negative_rate=60.0% (n=10)
