# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 39 件です。近似PF は 1.04、全体勝率は 74.4% でした。
- 事後評価では「待つ判断に使えた」が最も多く、17 件でした。
- 平均の役立ち度は 3.71 / 5 でした。
- 根拠整合の入力率は 43.6%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「TP が近すぎるケースが多い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-09 16:05 〜 2026-04-15 15:05
- 総観測件数: 39
- データ品質の内訳: ok=39
- 近似PF: 1.04

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: rr_below_min=33件, entry_zone_not_reached=3件, confidence_below_min=1件, inside_entry_zone_with_trigger=1件, near_entry_zone_with_trigger=1件

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 17件
- 入る判断に使えた: 3件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.71 / 5
- 値動きの主因の入力率: 46.2%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 43.6% / 整合率: 100.0%
- SL評価: SL は妥当=8件, SL が広すぎた=5件, SL が狭すぎた=3件
- TP評価: TP が近すぎた=11件, TP が遠すぎた=2件, TP は妥当=3件
- 4時間足評価: 妥当=7件, 一部弱い=7件, 弱い=2件
- 1時間足評価: 一部弱い=11件, 妥当=5件
- 15分足評価: 弱い=3件, 妥当=5件, 一部弱い=8件

## 5. 改善候補
1. TP が近すぎるケースが多い
   理由: tp_eval=too_close が 11/16 件 (68.8%)
   主に触る場所: src/analysis/rr.py, src/trade/exit_manager.py
2. ENTRY_OK と setup invalid の整合性崩れ
   理由: 期間内で ENTRY_OK + invalid が 8 件あります。主理由: rr_below_min=8件
   主に触る場所: main.py, src/analysis/confidence.py, src/analysis/position_risk.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 2 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- ENTRY_OK + rr_below_min: 5件 / 平均 execution=12.8 / 平均 wait=65.9
- ENTRY_OK + rr_below_min の主な risk_flags: lower_liquidity_close=3件, orderbook_ask_heavy=1件, short_cover_risk=1件

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=66.7%, 平均MFE=8.23, 平均MAE=4.64 (n=12) / データ不足 12/30
- uptrend: 勝率=77.8%, 平均MFE=5.37, 平均MAE=6.65 (n=27) / データ不足 27/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=74.4%, 平均MFE=6.25, 平均MAE=6.03 (n=39)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=4.68, 平均MAE=6.29 (n=6) / データ不足 6/30
- RISKY_ENTRY: 勝率=66.7%, 平均MFE=8.26, 平均MAE=3.11 (n=3) / データ不足 3/30
- SWEEP_WAIT: 勝率=69.0%, 平均MFE=6.46, 平均MAE=6.35 (n=29) / データ不足 29/30
- NO_TRADE_CANDIDATE: 勝率=100.0%, 平均MFE=3.38, 平均MAE=4.00 (n=1) / データ不足 1/30

### bias別件数・勝率
- long: 勝率=76.3% (n=38)
- short: 勝率=0.0% (n=1) / データ不足 1/30

### bias別 direction 正誤
- long: correct=10, wrong=16, unclear=12 / wrong_rate=42.1% (n=38)
- short: correct=0, wrong=1, unclear=0 / wrong_rate=100.0% (n=1)

### 成績指標
- 全体勝率: 74.4%
- 平均MFE(signal_based): 6.25
- 平均MAE(signal_based): 6.03
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 74.4%

### 通知品質
- A: 通知して良かった = 29件
- B: 通知したが微妙 = 10件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- short_cover_risk: wrong_rate=70.0% (wrong=7/10)
- sweep_incomplete: wrong_rate=40.6% (wrong=13/32)
- lower_liquidity_close: wrong_rate=38.2% (wrong=13/34)
- ask_wall_close: wrong_rate=38.1% (wrong=8/21)
- orderbook_ask_heavy: wrong_rate=38.1% (wrong=8/21)
- long_flush_exhaustion: wrong_rate=28.6% (wrong=2/7)

### 直近12時間速報
- 対象件数: 4件
- direction_execution_conflict: 2件
- direction_execution_conflict の主な理由: rr_below_min=2件
- direction_execution_conflict の主な risk_flags: lower_liquidity_close=2件, sweep_incomplete=2件, cvd_bullish_divergence=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 3件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 39
- 本有効件数: 0
- 参考ログ件数: 39
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### risk_flags 有効性比較
- short_cover_risk: negative_rate=90.0% (n=10)
- lower_liquidity_close: negative_rate=67.6% (n=34)
- sweep_incomplete: negative_rate=62.5% (n=32)
- ask_wall_close: negative_rate=57.1% (n=21)
- orderbook_ask_heavy: negative_rate=57.1% (n=21)
