# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 26 件です。近似PF は 0.94、全体勝率は 65.4% でした。
- 事後評価では「待つ判断に使えた」が最も多く、12 件でした。
- 平均の役立ち度は 3.62 / 5 でした。
- 根拠整合の入力率は 46.2%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「TP が近すぎるケースが多い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-14 01:05 〜 2026-04-19 09:05
- 総観測件数: 26
- データ品質の内訳: ok=26
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
- ready阻害理由: rr_below_min=14件, confidence_below_min=7件, inside_entry_zone_with_trigger=2件, entry_zone_not_reached=2件, near_entry_zone_waiting_trigger=1件

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 12件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.62 / 5
- 値動きの主因の入力率: 50.0%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 46.2% / 整合率: 100.0%
- SL評価: SL は妥当=8件, SL が広すぎた=3件, SL が狭すぎた=2件
- TP評価: TP が遠すぎた=3件, TP は妥当=3件, TP が近すぎた=7件
- 4時間足評価: 一部弱い=7件, 弱い=2件, 妥当=4件
- 1時間足評価: 一部弱い=11件, 妥当=2件
- 15分足評価: 妥当=6件, 弱い=4件, 一部弱い=3件
### 改善アクション
- 分類: 入口条件を調整=7件, 通知文面を調整=2件, 出口設計を調整=4件
- 重要度: 中=7件, 高=6件
- 高優先の代表例:
  - 20260418_110745: 通知文面を調整 / 件名と冒頭で「監視専用・新規エントリー非推奨」を先頭固定し、上方向バイアス表現より待機条件を前に出す。
  - 20260417_090500: 入口条件を調整 / 15分足で現値が直上レジスタンス至近かつ再検討帯未到達のときは通知を抑制し、下側流動性スイープ完了後のみ再発火する。
  - 20260414_140500: 通知文面を調整 / 通知件名と本文の強さを抑え、執行可能と誤読されない表現にする
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=159 / backlog=40 / AI済み=119 / human_override=0
- 今回の同期: created=0 / reused=0 / request_failed=0 / daily_cap=0
- 最終AI評価: 2026-04-20T05:07:43.352804Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. TP が近すぎるケースが多い
   理由: tp_eval=too_close が 7/13 件 (53.8%)
   主に触る場所: src/analysis/rr.py, src/trade/exit_manager.py
2. ENTRY_OK と setup invalid の整合性崩れ
   理由: 期間内で ENTRY_OK + invalid が 4 件あります。主理由: rr_below_min=4件
   主に触る場所: main.py, src/analysis/confidence.py, src/analysis/position_risk.py

補助集計:
- ENTRY_OK + rr_below_min: 2件 / 平均 execution=23.5 / 平均 wait=70.4
- ENTRY_OK + rr_below_min の主な risk_flags: sweep_incomplete=1件, orderbook_ask_heavy=1件

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=62.5%, 平均MFE=5.46, 平均MAE=5.85 (n=24) / データ不足 24/30
- uptrend: 勝率=100.0%, 平均MFE=6.59, 平均MAE=6.67 (n=2) / データ不足 2/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=65.4%, 平均MFE=5.55, 平均MAE=5.91 (n=26) / データ不足 26/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=7.89, 平均MAE=6.28 (n=2) / データ不足 2/30
- RISKY_ENTRY: 勝率=75.0%, 平均MFE=7.36, 平均MAE=3.62 (n=8) / データ不足 8/30
- SWEEP_WAIT: 勝率=58.3%, 平均MFE=4.49, 平均MAE=6.80 (n=12) / データ不足 12/30
- NO_TRADE_CANDIDATE: 勝率=50.0%, 平均MFE=3.95, 平均MAE=7.66 (n=4) / データ不足 4/30

### bias別件数・勝率
- long: 勝率=66.7% (n=24) / データ不足 24/30
- short: 勝率=50.0% (n=2) / データ不足 2/30

### bias別 direction 正誤
- long: correct=8, wrong=12, unclear=4 / wrong_rate=50.0% (n=24)
- short: correct=1, wrong=1, unclear=0 / wrong_rate=50.0% (n=2)

### 成績指標
- 全体勝率: 65.4%
- 平均MFE(signal_based): 5.55
- 平均MAE(signal_based): 5.91
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 65.4%

### 通知品質
- A: 通知して良かった = 17件
- B: 通知したが微妙 = 9件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- orderbook_ask_heavy: wrong_rate=66.7% (wrong=8/12)
- long_flush_exhaustion: wrong_rate=60.0% (wrong=6/10)
- lower_liquidity_close: wrong_rate=52.4% (wrong=11/21)
- sweep_incomplete: wrong_rate=52.2% (wrong=12/23)
- ask_wall_close: wrong_rate=50.0% (wrong=3/6)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 1件
- direction_execution_conflict の主な理由: confidence_below_min=1件
- direction_execution_conflict の主な risk_flags: bid_wall_close=1件, sweep_incomplete=1件, upper_liquidity_close=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 5件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 26
- 本有効件数: 0
- 参考ログ件数: 26
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 17件
- phase1_observation_gate=blocked: 9件
- 観測タイプ: direction_rr_learning=13件, setup_watch_learning=4件
- 観測候補全体: 17件 / 勝率=88.2% / TP1先行=88.2% / 近似PF=1.64 / 平均MFE=7.11 / 平均MAE=4.33
- direction_rr_learning: 13件 / 勝率=92.3% / TP1先行=92.3% / 近似PF=1.98 / 平均MFE=7.73 / 平均MAE=3.91
- setup_watch_learning: 4件 / 勝率=75.0% / TP1先行=75.0% / 近似PF=0.90 / 平均MFE=5.09 / 平均MAE=5.68
- 代表例: 20260418_110745, 20260418_090500, 20260417_090500, 20260416_202320, 20260416_170500
- 主な観測ブロック理由: confidence_below_min=7件, no_trade_candidate=4件, watch_conditions_not_met=1件

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 12件
- 主なブロック理由: phase1_inactive=12件, setup_not_ready=12件, wait_pressure_too_high=12件, execution_shadow_too_low=7件, no_trade_flags_present=3件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 12件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 3/7件

### risk_flags 有効性比較
- long_flush_exhaustion: negative_rate=80.0% (n=10)
- sweep_incomplete: negative_rate=73.9% (n=23)
- lower_liquidity_close: negative_rate=71.4% (n=21)
- orderbook_ask_heavy: negative_rate=66.7% (n=12)
