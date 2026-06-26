# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 36 件です。近似PF は 0.96、全体勝率は 75.0% でした。
- 事後評価では「待つ判断に使えた」が最も多く、15 件でした。
- 平均の役立ち度は 3.62 / 5 でした。
- 根拠整合の入力率は 41.7%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「TP が近すぎるケースが多い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-10 08:05 〜 2026-04-15 23:05
- 総観測件数: 36
- データ品質の内訳: ok=36
- 近似PF: 0.96

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: rr_below_min=30件, entry_zone_not_reached=3件, confidence_below_min=1件, inside_entry_zone_with_trigger=1件, near_entry_zone_with_trigger=1件

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 15件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.62 / 5
- 値動きの主因の入力率: 44.4%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 41.7% / 整合率: 100.0%
- SL評価: SL は妥当=8件, SL が広すぎた=5件, SL が狭すぎた=3件
- TP評価: TP が近すぎた=11件, TP が遠すぎた=2件, TP は妥当=3件
- 4時間足評価: 妥当=7件, 一部弱い=7件, 弱い=2件
- 1時間足評価: 一部弱い=11件, 妥当=5件
- 15分足評価: 弱い=3件, 妥当=5件, 一部弱い=8件
### 改善アクション
- 分類: 出口設計を調整=13件, リスク設計を調整=2件, 対応なし=1件
- 重要度: 高=11件, 中=4件, 低=1件
- 高優先の代表例:
  - 20260414_140500: 出口設計を調整 / TP1/TP2 を遠めにする候補を検証する
  - 20260414_090500: 出口設計を調整 / TP1/TP2 を遠めにする候補を検証する
  - 20260414_020500: 出口設計を調整 / TP1/TP2 を遠めにする候補を検証する

## 5. 改善候補
1. TP が近すぎるケースが多い
   理由: tp_eval=too_close が 11/16 件 (68.8%)
   主に触る場所: src/analysis/rr.py, src/trade/exit_manager.py
2. ENTRY_OK と setup invalid の整合性崩れ
   理由: 期間内で ENTRY_OK + invalid が 8 件あります。主理由: rr_below_min=8件
   主に触る場所: main.py, src/analysis/confidence.py, src/analysis/position_risk.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 5 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- ENTRY_OK + rr_below_min: 4件 / 平均 execution=10.8 / 平均 wait=70.8
- ENTRY_OK + rr_below_min の主な risk_flags: lower_liquidity_close=3件, orderbook_ask_heavy=1件, short_cover_risk=1件
- position_risk候補: lower_liquidity_close の単独加点を強めるか close 閾値を再確認
- confidence候補: execution<=20 かつ wait>=60 の本通知上位扱いを抑制

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=73.3%, 平均MFE=7.99, 平均MAE=4.22 (n=15) / データ不足 15/30
- uptrend: 勝率=76.2%, 平均MFE=4.62, 平均MAE=7.70 (n=21) / データ不足 21/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=75.0%, 平均MFE=6.03, 平均MAE=6.25 (n=36)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=3.87, 平均MAE=6.47 (n=5) / データ不足 5/30
- RISKY_ENTRY: 勝率=75.0%, 平均MFE=7.74, 平均MAE=3.17 (n=4) / データ不足 4/30
- SWEEP_WAIT: 勝率=69.2%, 平均MFE=6.28, 平均MAE=6.77 (n=26) / データ不足 26/30
- NO_TRADE_CANDIDATE: 勝率=100.0%, 平均MFE=3.38, 平均MAE=4.00 (n=1) / データ不足 1/30

### bias別件数・勝率
- long: 勝率=77.1% (n=35)
- short: 勝率=0.0% (n=1) / データ不足 1/30

### bias別 direction 正誤
- long: correct=11, wrong=15, unclear=9 / wrong_rate=42.9% (n=35)
- short: correct=0, wrong=1, unclear=0 / wrong_rate=100.0% (n=1)

### 成績指標
- 全体勝率: 75.0%
- 平均MFE(signal_based): 6.03
- 平均MAE(signal_based): 6.25
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 75.0%

### 通知品質
- A: 通知して良かった = 27件
- B: 通知したが微妙 = 9件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- short_cover_risk: wrong_rate=70.0% (wrong=7/10)
- ask_wall_close: wrong_rate=42.1% (wrong=8/19)
- orderbook_ask_heavy: wrong_rate=42.1% (wrong=8/19)
- sweep_incomplete: wrong_rate=41.4% (wrong=12/29)
- lower_liquidity_close: wrong_rate=40.6% (wrong=13/32)
- long_flush_exhaustion: wrong_rate=33.3% (wrong=2/6)

### 直近12時間速報
- 対象件数: 11件
- direction_execution_conflict: 5件
- direction_execution_conflict の主な理由: rr_below_min=5件
- direction_execution_conflict の主な risk_flags: lower_liquidity_close=5件, long_flush_exhaustion=4件, sweep_incomplete=4件
- ENTRY_OK + invalid: 1件
- countertrend_long_cluster: 11件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 36
- 本有効件数: 0
- 参考ログ件数: 36
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 0件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 0/11件

### risk_flags 有効性比較
- short_cover_risk: negative_rate=80.0% (n=10)
- lower_liquidity_close: negative_rate=68.8% (n=32)
- ask_wall_close: negative_rate=63.2% (n=19)
- sweep_incomplete: negative_rate=62.1% (n=29)
- orderbook_ask_heavy: negative_rate=57.9% (n=19)
