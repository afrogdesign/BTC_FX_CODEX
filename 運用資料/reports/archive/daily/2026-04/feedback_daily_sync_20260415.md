# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 41 件です。近似PF は 1.15、全体勝率は 75.6% でした。
- 事後評価では「待つ判断に使えた」が最も多く、16 件でした。
- 平均の役立ち度は 3.78 / 5 でした。
- 根拠整合の入力率は 41.5%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「ENTRY_OK と setup invalid の整合性崩れ」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-08 11:05 〜 2026-04-14 01:05
- 総観測件数: 41
- データ品質の内訳: ok=41
- 近似PF: 1.15

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: rr_below_min=34件, entry_zone_not_reached=3件, confidence_below_min=1件, inside_entry_zone_with_trigger=1件, near_entry_zone_with_trigger=1件

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 16件
- 入る判断に使えた: 7件
- 平均の役立ち度: 3.78 / 5
- 値動きの主因の入力率: 43.9%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 41.5% / 整合率: 100.0%
- SL評価: SL は妥当=6件, SL が狭すぎた=3件, SL が広すぎた=5件
- TP評価: TP が遠すぎた=2件, TP が近すぎた=9件, TP は妥当=3件
- 4時間足評価: 弱い=2件, 妥当=8件, 一部弱い=4件
- 1時間足評価: 一部弱い=10件, 妥当=4件
- 15分足評価: 妥当=4件, 一部弱い=7件, 弱い=3件

## 5. 改善候補
1. ENTRY_OK と setup invalid の整合性崩れ
   理由: 期間内で ENTRY_OK + invalid が 11 件あります。主理由: rr_below_min=11件
   主に触る場所: main.py, src/analysis/confidence.py, src/analysis/position_risk.py
2. TP が近すぎるケースが多い
   理由: tp_eval=too_close が 9/14 件 (64.3%)
   主に触る場所: src/analysis/rr.py, src/trade/exit_manager.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 5 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- ENTRY_OK + rr_below_min: 6件 / 平均 execution=10.3 / 平均 wait=64.8
- ENTRY_OK + rr_below_min の主な risk_flags: lower_liquidity_close=5件, short_cover_risk=1件, cvd_bullish_divergence=1件

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=50.0%, 平均MFE=10.39, 平均MAE=5.24 (n=6) / データ不足 6/30
- transition: 勝率=100.0%, 平均MFE=4.63, 平均MAE=2.55 (n=3) / データ不足 3/30
- uptrend: 勝率=78.1%, 平均MFE=5.95, 平均MAE=5.99 (n=32)

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=75.6%, 平均MFE=6.50, 平均MAE=5.63 (n=41)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=85.7%, 平均MFE=6.33, 平均MAE=4.75 (n=7) / データ不足 7/30
- RISKY_ENTRY: 勝率=100.0%, 平均MFE=4.98, 平均MAE=2.19 (n=1) / データ不足 1/30
- SWEEP_WAIT: 勝率=72.7%, 平均MFE=6.58, 平均MAE=5.92 (n=33)

### bias別件数・勝率
- long: 勝率=77.5% (n=40)
- short: 勝率=0.0% (n=1) / データ不足 1/30

### bias別 direction 正誤
- long: correct=12, wrong=14, unclear=14 / wrong_rate=35.0% (n=40)
- short: correct=0, wrong=1, unclear=0 / wrong_rate=100.0% (n=1)

### 成績指標
- 全体勝率: 75.6%
- 平均MFE(signal_based): 6.50
- 平均MAE(signal_based): 5.63
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 75.6%

### 通知品質
- A: 通知して良かった = 31件
- B: 通知したが微妙 = 10件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- short_cover_risk: wrong_rate=70.0% (wrong=7/10)
- sweep_incomplete: wrong_rate=35.5% (wrong=11/31)
- orderbook_ask_heavy: wrong_rate=33.3% (wrong=6/18)
- lower_liquidity_close: wrong_rate=32.4% (wrong=12/37)
- ask_wall_close: wrong_rate=29.2% (wrong=7/24)
- long_flush_exhaustion: wrong_rate=25.0% (wrong=2/8)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 5件
- direction_execution_conflict の主な理由: rr_below_min=5件
- direction_execution_conflict の主な risk_flags: lower_liquidity_close=5件, ask_wall_close=4件, sweep_incomplete=4件
- ENTRY_OK + invalid: 1件
- countertrend_long_cluster: 11件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 41
- 本有効件数: 0
- 参考ログ件数: 41
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### risk_flags 有効性比較
- short_cover_risk: negative_rate=90.0% (n=10)
- lower_liquidity_close: negative_rate=64.9% (n=37)
- sweep_incomplete: negative_rate=61.3% (n=31)
- orderbook_ask_heavy: negative_rate=55.6% (n=18)
- ask_wall_close: negative_rate=50.0% (n=24)
