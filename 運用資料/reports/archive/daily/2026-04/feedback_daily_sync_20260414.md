# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 40 件です。近似PF は 1.23、全体勝率は 80.0% でした。
- 事後評価では「待つ判断に使えた」が最も多く、13 件でした。
- 平均の役立ち度は 3.76 / 5 でした。
- 根拠整合の入力率は 40.0%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「ENTRY_OK と setup invalid の整合性崩れ」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-08 01:05 〜 2026-04-13 00:05
- 総観測件数: 40
- データ品質の内訳: ok=40
- 近似PF: 1.23

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 13件
- 入る判断に使えた: 7件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.76 / 5
- 値動きの主因の入力率: 40.0%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 40.0% / 整合率: 100.0%
- SL評価: SL は妥当=4件, SL が狭すぎた=2件, SL が広すぎた=6件
- TP評価: TP が近すぎた=9件, TP は妥当=2件, TP が遠すぎた=1件
- 4時間足評価: 妥当=8件, 一部弱い=3件, 弱い=1件
- 1時間足評価: 妥当=4件, 一部弱い=8件
- 15分足評価: 一部弱い=5件, 妥当=3件, 弱い=4件

## 5. 改善候補
1. ENTRY_OK と setup invalid の整合性崩れ
   理由: 期間内で ENTRY_OK + invalid が 11 件あります
   主に触る場所: main.py, src/analysis/confidence.py, src/analysis/position_risk.py
2. TP が近すぎるケースが多い
   理由: tp_eval=too_close が 9/12 件 (75.0%)
   主に触る場所: src/analysis/rr.py, src/trade/exit_manager.py
3. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 7/7 件 (100.0%)
   主に触る場所: config.py, src/analysis/position_risk.py

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=66.7%, 平均MFE=6.52, 平均MAE=2.83 (n=3) / データ不足 3/30
- transition: 勝率=100.0%, 平均MFE=9.66, 平均MAE=1.87 (n=5) / データ不足 5/30
- uptrend: 勝率=78.1%, 平均MFE=5.95, 平均MAE=5.99 (n=32)

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=80.0%, 平均MFE=6.45, 平均MAE=5.24 (n=40)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=85.7%, 平均MFE=6.33, 平均MAE=4.75 (n=7) / データ不足 7/30
- RISKY_ENTRY: 勝率=100.0%, 平均MFE=4.98, 平均MAE=2.19 (n=1) / データ不足 1/30
- SWEEP_WAIT: 勝率=77.4%, 平均MFE=6.14, 平均MAE=5.61 (n=31)
- NO_TRADE_CANDIDATE: 勝率=100.0%, 平均MFE=18.44, 平均MAE=0.35 (n=1) / データ不足 1/30

### bias別件数・勝率
- long: 勝率=80.0% (n=40)

### bias別 direction 正誤
- long: correct=14, wrong=13, unclear=13 / wrong_rate=32.5% (n=40)

### 成績指標
- 全体勝率: 80.0%
- 平均MFE(signal_based): 6.45
- 平均MAE(signal_based): 5.24
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 80.0%

### 通知品質
- A: 通知して良かった = 32件
- B: 通知したが微妙 = 8件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- short_cover_risk: wrong_rate=54.5% (wrong=6/11)
- lower_liquidity_close: wrong_rate=31.6% (wrong=12/38)
- sweep_incomplete: wrong_rate=30.0% (wrong=9/30)
- ask_wall_close: wrong_rate=29.2% (wrong=7/24)
- orderbook_ask_heavy: wrong_rate=27.8% (wrong=5/18)
- long_flush_exhaustion: wrong_rate=25.0% (wrong=2/8)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 3件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 5件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 40
- 本有効件数: 0
- 参考ログ件数: 40
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### risk_flags 有効性比較
- short_cover_risk: negative_rate=81.8% (n=11)
- lower_liquidity_close: negative_rate=65.8% (n=38)
- sweep_incomplete: negative_rate=60.0% (n=30)
- orderbook_ask_heavy: negative_rate=55.6% (n=18)
- ask_wall_close: negative_rate=54.2% (n=24)
