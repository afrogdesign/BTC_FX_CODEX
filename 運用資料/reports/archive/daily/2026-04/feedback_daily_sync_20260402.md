# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 33 件です。近似PF は 0.79、全体勝率は 72.7% でした。
- 人のレビューでは「見送り判断に使えた」が最も多く、1 件でした。
- 平均の役立ち度は 3.00 / 5 でした。
- 今回の改善候補の最上位は「ENTRY_OK と setup invalid の整合性崩れ」です。

## 2. 今回の対象
- 集計期間: 2026-03-26 09:05 〜 2026-04-01 00:05
- 総観測件数: 33
- データ品質の内訳: ok=33
- 近似PF: 0.79

## 3. 人のレビュー要約
- 見送り判断に使えた: 1件
- 平均の役立ち度: 3.00 / 5
- 値動きの主因の入力率: 3.0%

## 4. 改善候補
1. ENTRY_OK と setup invalid の整合性崩れ
   理由: 期間内で ENTRY_OK + invalid が 9 件あります
   主に触る場所: main.py, src/analysis/confidence.py, src/analysis/position_risk.py
2. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 3 件あります
   主に触る場所: tools/log_feedback.py

## 5. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- downtrend: 勝率=80.0%, 平均MFE=7.90, 平均MAE=7.72 (n=10) / データ不足 10/30
- range: 勝率=69.2%, 平均MFE=3.53, 平均MAE=5.52 (n=13) / データ不足 13/30
- transition: 勝率=75.0%, 平均MFE=6.49, 平均MAE=6.58 (n=8) / データ不足 8/30
- uptrend: 勝率=50.0%, 平均MFE=0.35, 平均MAE=11.60 (n=2) / データ不足 2/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=72.7%, 平均MFE=5.38, 平均MAE=6.81 (n=33)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=6.18, 平均MAE=5.72 (n=3) / データ不足 3/30
- RISKY_ENTRY: 勝率=63.6%, 平均MFE=3.43, 平均MAE=6.66 (n=11) / データ不足 11/30
- SWEEP_WAIT: 勝率=72.2%, 平均MFE=6.71, 平均MAE=7.19 (n=18) / データ不足 18/30
- NO_TRADE_CANDIDATE: 勝率=100.0%, 平均MFE=0.33, 平均MAE=5.04 (n=1) / データ不足 1/30

### bias別件数・勝率
- long: 勝率=50.0% (n=6) / データ不足 6/30
- short: 勝率=77.8% (n=27) / データ不足 27/30

### bias別 direction 正誤
- long: correct=0, wrong=5, unclear=1 / wrong_rate=83.3% (n=6)
- short: correct=9, wrong=12, unclear=6 / wrong_rate=44.4% (n=27)

### 成績指標
- 全体勝率: 72.7%
- 平均MFE(signal_based): 5.38
- 平均MAE(signal_based): 6.81
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 72.7%

### 通知品質
- A: 通知して良かった = 24件
- B: 通知したが微妙 = 9件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- lower_liquidity_close: wrong_rate=83.3% (wrong=5/6)
- long_flush_exhaustion: wrong_rate=77.8% (wrong=7/9)
- orderbook_bid_heavy: wrong_rate=60.0% (wrong=6/10)
- sweep_incomplete: wrong_rate=51.7% (wrong=15/29)
- upper_liquidity_close: wrong_rate=48.0% (wrong=12/25)
- bid_wall_close: wrong_rate=41.7% (wrong=5/12)
- short_cover_risk: wrong_rate=28.6% (wrong=2/7)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 3件
- ENTRY_OK + invalid: 1件
- countertrend_long_cluster: 4件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 33
- 本有効件数: 0
- 参考ログ件数: 33
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### risk_flags 有効性比較
- orderbook_bid_heavy: negative_rate=80.0% (n=10)
- upper_liquidity_close: negative_rate=64.0% (n=25)
- sweep_incomplete: negative_rate=62.1% (n=29)
- bid_wall_close: negative_rate=58.3% (n=12)
