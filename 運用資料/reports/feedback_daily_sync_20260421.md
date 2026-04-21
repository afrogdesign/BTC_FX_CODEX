# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 26 件です。近似PF は 0.81、全体勝率は 61.5% でした。
- 事後評価では「待つ判断に使えた」が最も多く、11 件でした。
- 平均の役立ち度は 3.83 / 5 でした。
- 根拠整合の入力率は 46.2%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「ENTRY_OK と setup invalid の整合性崩れ」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-15 10:05 〜 2026-04-20 15:05
- 総観測件数: 26
- データ品質の内訳: ok=26
- 近似PF: 0.81

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: rr_below_min=11件, confidence_below_min=9件, entry_zone_not_reached=3件, inside_entry_zone_with_trigger=2件, near_entry_zone_waiting_trigger=1件

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 11件
- 見送り判断に使えた: 1件
- 平均の役立ち度: 3.83 / 5
- 値動きの主因の入力率: 46.2%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 46.2% / 整合率: 100.0%
- SL評価: SL は妥当=8件, SL が広すぎた=2件, SL が狭すぎた=2件
- TP評価: TP が遠すぎた=3件, TP は妥当=6件, TP が近すぎた=3件
- 4時間足評価: 一部弱い=8件, 弱い=1件, 妥当=3件
- 1時間足評価: 妥当=2件, 一部弱い=10件
- 15分足評価: 一部弱い=3件, 妥当=7件, 弱い=2件
### 改善アクション
- 分類: 入口条件を調整=8件, 観測継続=2件, 通知文面を調整=2件
- 重要度: 中=9件, 高=3件
- 高優先の代表例:
  - 20260418_110745: 通知文面を調整 / 件名と冒頭で「監視専用・新規エントリー非推奨」を先頭固定し、上方向バイアス表現より待機条件を前に出す。
  - 20260418_090500: 通知文面を調整 / 件名と本文冒頭に「エントリー非推奨（待機）」を固定し、方向バイアス表現より先に表示する。
  - 20260417_090500: 入口条件を調整 / 15分足で現値が直上レジスタンス至近かつ再検討帯未到達のときは通知を抑制し、下側流動性スイープ完了後のみ再発火する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=164 / backlog=41 / AI済み=123 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-04-20T18:36:36.372890Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. ENTRY_OK と setup invalid の整合性崩れ
   理由: 期間内で ENTRY_OK + invalid が 3 件あります。主理由: rr_below_min=3件
   主に触る場所: main.py, src/analysis/confidence.py, src/analysis/position_risk.py
2. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 2 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- ENTRY_OK + rr_below_min: 1件 / 平均 execution=21.0 / 平均 wait=70.4
- ENTRY_OK + rr_below_min の主な risk_flags: sweep_incomplete=1件

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=59.1%, 平均MFE=5.35, 平均MAE=5.92 (n=22) / データ不足 22/30
- transition: 勝率=50.0%, 平均MFE=1.35, 平均MAE=10.78 (n=2) / データ不足 2/30
- uptrend: 勝率=100.0%, 平均MFE=6.59, 平均MAE=6.67 (n=2) / データ不足 2/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=61.5%, 平均MFE=5.14, 平均MAE=6.36 (n=26) / データ不足 26/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=13.43, 平均MAE=3.71 (n=1) / データ不足 1/30
- RISKY_ENTRY: 勝率=62.5%, 平均MFE=5.54, 平均MAE=5.48 (n=8) / データ不足 8/30
- SWEEP_WAIT: 勝率=61.5%, 平均MFE=4.62, 平均MAE=6.70 (n=13) / データ不足 13/30
- NO_TRADE_CANDIDATE: 勝率=50.0%, 平均MFE=3.95, 平均MAE=7.66 (n=4) / データ不足 4/30

### bias別件数・勝率
- long: 勝率=60.9% (n=23) / データ不足 23/30
- short: 勝率=66.7% (n=3) / データ不足 3/30

### bias別 direction 正誤
- long: correct=7, wrong=12, unclear=4 / wrong_rate=52.2% (n=23)
- short: correct=1, wrong=2, unclear=0 / wrong_rate=66.7% (n=3)

### 成績指標
- 全体勝率: 61.5%
- 平均MFE(signal_based): 5.14
- 平均MAE(signal_based): 6.36
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 61.5%

### 通知品質
- A: 通知して良かった = 16件
- B: 通知したが微妙 = 10件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- long_flush_exhaustion: wrong_rate=63.6% (wrong=7/11)
- orderbook_ask_heavy: wrong_rate=63.6% (wrong=7/11)
- sweep_incomplete: wrong_rate=59.1% (wrong=13/22)
- lower_liquidity_close: wrong_rate=57.1% (wrong=12/21)
- ask_wall_close: wrong_rate=50.0% (wrong=3/6)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 2件
- direction_execution_conflict の主な理由: confidence_below_min=2件
- direction_execution_conflict の主な risk_flags: ask_wall_close=2件, lower_liquidity_close=2件, orderbook_ask_heavy=2件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 8件

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
- phase1_observation_gate=pass: 15件
- phase1_observation_gate=blocked: 11件
- 観測タイプ: direction_rr_learning=10件, setup_watch_learning=5件
- 観測候補全体: 15件 / 勝率=80.0% / TP1先行=80.0% / 近似PF=1.26 / 平均MFE=6.54 / 平均MAE=5.17
- direction_rr_learning: 10件 / 勝率=90.0% / TP1先行=90.0% / 近似PF=2.29 / 平均MFE=8.09 / 平均MAE=3.53
- setup_watch_learning: 5件 / 勝率=60.0% / TP1先行=60.0% / 近似PF=0.41 / 平均MFE=3.44 / 平均MAE=8.44
- 代表例: 20260420_060500, 20260420_040500, 20260418_110745, 20260418_090500, 20260417_090500
- 主な観測ブロック理由: confidence_below_min=9件, no_trade_candidate=4件, watch_conditions_not_met=1件

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 17件
- 主なブロック理由: phase1_inactive=17件, setup_not_ready=17件, wait_pressure_too_high=15件, execution_shadow_too_low=10件, no_trade_flags_present=3件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 17件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 3/3件

### risk_flags 有効性比較
- sweep_incomplete: negative_rate=81.8% (n=22)
- long_flush_exhaustion: negative_rate=81.8% (n=11)
- lower_liquidity_close: negative_rate=76.2% (n=21)
- orderbook_ask_heavy: negative_rate=63.6% (n=11)
