# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 34 件です。近似PF は 0.94、全体勝率は 76.5% でした。
- 事後評価では「待つ判断に使えた」が最も多く、15 件でした。
- 平均の役立ち度は 3.62 / 5 でした。
- 根拠整合の入力率は 44.1%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「TP が近すぎるケースが多い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-11 05:05 〜 2026-04-17 02:05
- 総観測件数: 34
- データ品質の内訳: ok=34
- 近似PF: 0.94

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: rr_below_min=27件, entry_zone_not_reached=3件, inside_entry_zone_with_trigger=2件, confidence_below_min=1件, near_entry_zone_with_trigger=1件

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 15件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.62 / 5
- 値動きの主因の入力率: 47.1%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 44.1% / 整合率: 100.0%
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
   理由: 期間内で ENTRY_OK + invalid が 7 件あります。主理由: rr_below_min=7件
   主に触る場所: main.py, src/analysis/confidence.py, src/analysis/position_risk.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 7 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- ENTRY_OK + rr_below_min: 2件 / 平均 execution=14.5 / 平均 wait=72.8
- ENTRY_OK + rr_below_min の主な risk_flags: orderbook_ask_heavy=1件, lower_liquidity_close=1件, short_cover_risk=1件
- confidence候補: execution<=20 かつ wait>=60 の本通知上位扱いを抑制

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=77.8%, 平均MFE=8.32, 平均MAE=3.88 (n=18) / データ不足 18/30
- uptrend: 勝率=75.0%, 平均MFE=4.38, 平均MAE=10.19 (n=16) / データ不足 16/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=76.5%, 平均MFE=6.46, 平均MAE=6.85 (n=34)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=4.54, 平均MAE=9.51 (n=3) / データ不足 3/30
- RISKY_ENTRY: 勝率=83.3%, 平均MFE=8.12, 平均MAE=3.07 (n=6) / データ不足 6/30
- SWEEP_WAIT: 勝率=70.8%, 平均MFE=6.42, 平均MAE=7.58 (n=24) / データ不足 24/30
- NO_TRADE_CANDIDATE: 勝率=100.0%, 平均MFE=3.38, 平均MAE=4.00 (n=1) / データ不足 1/30

### bias別件数・勝率
- long: 勝率=78.8% (n=33)
- short: 勝率=0.0% (n=1) / データ不足 1/30

### bias別 direction 正誤
- long: correct=12, wrong=15, unclear=6 / wrong_rate=45.5% (n=33)
- short: correct=0, wrong=1, unclear=0 / wrong_rate=100.0% (n=1)

### 成績指標
- 全体勝率: 76.5%
- 平均MFE(signal_based): 6.46
- 平均MAE(signal_based): 6.85
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 76.5%

### 通知品質
- A: 通知して良かった = 26件
- B: 通知したが微妙 = 8件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- short_cover_risk: wrong_rate=75.0% (wrong=6/8)
- orderbook_ask_heavy: wrong_rate=45.0% (wrong=9/20)
- long_flush_exhaustion: wrong_rate=44.4% (wrong=4/9)
- lower_liquidity_close: wrong_rate=43.3% (wrong=13/30)
- sweep_incomplete: wrong_rate=42.9% (wrong=12/28)
- ask_wall_close: wrong_rate=37.5% (wrong=6/16)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 7件
- direction_execution_conflict の主な理由: rr_below_min=5件, near_entry_zone_waiting_trigger=1件, confidence_below_min=1件
- direction_execution_conflict の主な risk_flags: orderbook_ask_heavy=6件, lower_liquidity_close=5件, sweep_incomplete=5件
- ENTRY_OK + invalid: 2件
- countertrend_long_cluster: 8件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 34
- 本有効件数: 0
- 参考ログ件数: 34
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 1件
- 主なブロック理由: execution_shadow_too_low=1件, no_trade_flags_present=1件, phase1_inactive=1件, rr_below_min=1件, setup_not_ready=1件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 1件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 0/11件

### risk_flags 有効性比較
- lower_liquidity_close: negative_rate=63.3% (n=30)
- ask_wall_close: negative_rate=62.5% (n=16)
- sweep_incomplete: negative_rate=60.7% (n=28)
- orderbook_ask_heavy: negative_rate=55.0% (n=20)
