# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 29 件です。近似PF は 1.13、全体勝率は 75.9% でした。
- 事後評価では「待つ判断に使えた」が最も多く、14 件でした。
- 平均の役立ち度は 3.60 / 5 でした。
- 根拠整合の入力率は 48.3%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「TP が近すぎるケースが多い」です。
- AI事後評価は停止中です。候補残 39 件、直近エラー 2026-04-17T18:35:03.067173Z。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-12 02:05 〜 2026-04-17 18:05
- 総観測件数: 29
- データ品質の内訳: ok=29
- 近似PF: 1.13

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: rr_below_min=22件, entry_zone_not_reached=3件, inside_entry_zone_with_trigger=2件, confidence_below_min=1件, near_entry_zone_with_trigger=1件

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 14件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.60 / 5
- 値動きの主因の入力率: 51.7%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 48.3% / 整合率: 100.0%
- SL評価: SL は妥当=8件, SL が広すぎた=4件, SL が狭すぎた=3件
- TP評価: TP が近すぎた=10件, TP が遠すぎた=2件, TP は妥当=3件
- 4時間足評価: 妥当=6件, 一部弱い=7件, 弱い=2件
- 1時間足評価: 一部弱い=10件, 妥当=5件
- 15分足評価: 弱い=3件, 妥当=5件, 一部弱い=7件
### 改善アクション
- 分類: 通知文面を調整=3件, 出口設計を調整=11件, リスク設計を調整=1件
- 重要度: 高=12件, 中=3件
- 高優先の代表例:
  - 20260414_140500: 通知文面を調整 / 通知件名と本文の強さを抑え、執行可能と誤読されない表現にする
  - 20260414_090500: 出口設計を調整 / TP1/TP2 を遠めにする候補を検証する
  - 20260414_020500: 出口設計を調整 / TP1/TP2 を遠めにする候補を検証する
### AI事後評価 health
- 状態: 停止中
- 候補件数: eligible=150 / backlog=39 / AI済み=111 / human_override=0
- 今回の同期: created=0 / reused=0 / request_failed=5 / daily_cap=0
- 最終AI評価: 2026-04-15T18:36:50.508594Z / 最終エラー: 2026-04-17T18:35:03.067173Z

## 5. 改善候補
1. TP が近すぎるケースが多い
   理由: tp_eval=too_close が 10/15 件 (66.7%)
   主に触る場所: src/analysis/rr.py, src/trade/exit_manager.py
2. ENTRY_OK と setup invalid の整合性崩れ
   理由: 期間内で ENTRY_OK + invalid が 5 件あります。主理由: rr_below_min=5件
   主に触る場所: main.py, src/analysis/confidence.py, src/analysis/position_risk.py

補助集計:
- ENTRY_OK + rr_below_min: 2件 / 平均 execution=23.5 / 平均 wait=70.4
- ENTRY_OK + rr_below_min の主な risk_flags: sweep_incomplete=1件, orderbook_ask_heavy=1件

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=80.0%, 平均MFE=8.62, 平均MAE=3.82 (n=20) / データ不足 20/30
- uptrend: 勝率=66.7%, 平均MFE=3.12, 平均MAE=11.27 (n=9) / データ不足 9/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=75.9%, 平均MFE=6.91, 平均MAE=6.13 (n=29) / データ不足 29/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=6.16, 平均MAE=5.60 (n=3) / データ不足 3/30
- RISKY_ENTRY: 勝率=85.7%, 平均MFE=8.26, 平均MAE=3.03 (n=7) / データ不足 7/30
- SWEEP_WAIT: 勝率=66.7%, 平均MFE=6.70, 平均MAE=7.54 (n=18) / データ不足 18/30
- NO_TRADE_CANDIDATE: 勝率=100.0%, 平均MFE=3.38, 平均MAE=4.00 (n=1) / データ不足 1/30

### bias別件数・勝率
- long: 勝率=78.6% (n=28) / データ不足 28/30
- short: 勝率=0.0% (n=1) / データ不足 1/30

### bias別 direction 正誤
- long: correct=12, wrong=11, unclear=5 / wrong_rate=39.3% (n=28)
- short: correct=0, wrong=1, unclear=0 / wrong_rate=100.0% (n=1)

### 成績指標
- 全体勝率: 75.9%
- 平均MFE(signal_based): 6.91
- 平均MAE(signal_based): 6.13
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 75.9%

### 通知品質
- A: 通知して良かった = 22件
- B: 通知したが微妙 = 7件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- short_cover_risk: wrong_rate=66.7% (wrong=4/6)
- orderbook_ask_heavy: wrong_rate=43.8% (wrong=7/16)
- sweep_incomplete: wrong_rate=40.0% (wrong=10/25)
- lower_liquidity_close: wrong_rate=37.5% (wrong=9/24)
- long_flush_exhaustion: wrong_rate=37.5% (wrong=3/8)
- ask_wall_close: wrong_rate=18.2% (wrong=2/11)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 1件
- direction_execution_conflict の主な理由: confidence_below_min=1件
- direction_execution_conflict の主な risk_flags: ask_wall_close=1件, long_flush_exhaustion=1件, lower_liquidity_close=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 10件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 29
- 本有効件数: 0
- 参考ログ件数: 29
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 3件
- 主なブロック理由: no_trade_flags_present=3件, phase1_inactive=3件, rr_below_min=3件, setup_not_ready=3件, wait_pressure_too_high=3件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 3件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 0/10件

### risk_flags 有効性比較
- sweep_incomplete: negative_rate=64.0% (n=25)
- lower_liquidity_close: negative_rate=62.5% (n=24)
- orderbook_ask_heavy: negative_rate=56.2% (n=16)
- ask_wall_close: negative_rate=54.5% (n=11)
