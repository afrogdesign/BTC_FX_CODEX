# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 35 件です。近似PF は 1.22、全体勝率は 88.6% でした。
- 事後評価では「待つ判断に使えた」が最も多く、8 件でした。
- 平均の役立ち度は 3.81 / 5 でした。
- 根拠整合の入力率は 28.6%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「ENTRY_OK と setup invalid の整合性崩れ」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-07 01:05 〜 2026-04-12 07:05
- 総観測件数: 35
- データ品質の内訳: ok=35
- 近似PF: 1.22

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
- 待つ判断に使えた: 8件
- 入る判断に使えた: 7件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.81 / 5
- 値動きの主因の入力率: 31.4%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 28.6% / 整合率: 100.0%
- SL評価: SL が広すぎた=4件, SL は妥当=2件, SL が狭すぎた=1件
- TP評価: TP が近すぎた=7件
- 4時間足評価: 妥当=6件, 一部弱い=1件
- 1時間足評価: 一部弱い=6件, 弱い=1件
- 15分足評価: 妥当=3件, 一部弱い=1件, 弱い=3件

## 5. 改善候補
1. ENTRY_OK と setup invalid の整合性崩れ
   理由: 期間内で ENTRY_OK + invalid が 12 件あります
   主に触る場所: main.py, src/analysis/confidence.py, src/analysis/position_risk.py
2. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 7/7 件 (100.0%)
   主に触る場所: config.py, src/analysis/position_risk.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 7 件あります
   主に触る場所: tools/log_feedback.py

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- transition: 勝率=100.0%, 平均MFE=8.33, 平均MAE=3.07 (n=6) / データ不足 6/30
- uptrend: 勝率=86.2%, 平均MFE=6.48, 平均MAE=6.11 (n=29) / データ不足 29/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=88.6%, 平均MFE=6.80, 平均MAE=5.59 (n=35)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=85.7%, 平均MFE=6.18, 平均MAE=5.44 (n=7) / データ不足 7/30
- RISKY_ENTRY: 勝率=100.0%, 平均MFE=4.98, 平均MAE=2.19 (n=1) / データ不足 1/30
- SWEEP_WAIT: 勝率=88.5%, 平均MFE=6.59, 平均MAE=5.96 (n=26) / データ不足 26/30
- NO_TRADE_CANDIDATE: 勝率=100.0%, 平均MFE=18.44, 平均MAE=0.35 (n=1) / データ不足 1/30

### bias別件数・勝率
- long: 勝率=88.6% (n=35)

### bias別 direction 正誤
- long: correct=12, wrong=12, unclear=11 / wrong_rate=34.3% (n=35)

### 成績指標
- 全体勝率: 88.6%
- 平均MFE(signal_based): 6.80
- 平均MAE(signal_based): 5.59
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 88.6%

### 通知品質
- A: 通知して良かった = 31件
- B: 通知したが微妙 = 4件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- short_cover_risk: wrong_rate=60.0% (wrong=6/10)
- ask_wall_close: wrong_rate=35.0% (wrong=7/20)
- sweep_incomplete: wrong_rate=34.6% (wrong=9/26)
- lower_liquidity_close: wrong_rate=33.3% (wrong=11/33)
- orderbook_ask_heavy: wrong_rate=31.2% (wrong=5/16)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 7件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 8件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 35
- 本有効件数: 0
- 参考ログ件数: 35
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### risk_flags 有効性比較
- short_cover_risk: negative_rate=80.0% (n=10)
- lower_liquidity_close: negative_rate=63.6% (n=33)
- sweep_incomplete: negative_rate=57.7% (n=26)
- orderbook_ask_heavy: negative_rate=56.2% (n=16)
- ask_wall_close: negative_rate=50.0% (n=20)
