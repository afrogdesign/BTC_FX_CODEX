# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 21 件です。近似PF は 1.09、全体勝率は 71.4% でした。
- 事後評価では「待つ判断に使えた」が最も多く、11 件でした。
- 平均の役立ち度は 3.53 / 5 でした。
- 根拠整合の入力率は 81.0%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-05 06:05 〜 2026-05-11 01:05
- 総観測件数: 21
- データ品質の内訳: ok=21
- 近似PF: 1.09

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: entry_zone_not_reached=10件, confidence_below_min=6件, near_entry_zone_waiting_trigger=4件, inside_entry_zone_with_trigger=1件
- confidence_below_min 代表例: 20260509_120501(watch/SWEEP_WAIT, dir=55, exec=21, wait=62, MFE24h=8.90, MAE24h=1.46, outcome=win) / 20260509_163138(invalid/NO_TRADE_CANDIDATE, dir=70, exec=12, wait=93, MFE24h=7.72, MAE24h=0.72, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 11件
- 見送り判断に使えた: 4件
- 通知が早すぎた: 2件
- 価値が低かった: 2件
- 平均の役立ち度: 3.53 / 5
- 値動きの主因の入力率: 90.5%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 81.0% / 整合率: 100.0%
- SL評価: SL が狭すぎた=4件, SL は妥当=15件
- TP評価: TP は妥当=11件, TP が近すぎた=3件, TP が遠すぎた=5件
- 4時間足評価: 妥当=11件, 一部弱い=7件, 弱い=1件
- 1時間足評価: 一部弱い=16件, 妥当=3件
- 15分足評価: 弱い=8件, 一部弱い=4件, 妥当=7件
### 改善アクション
- 分類: 入口条件を調整=12件, 通知文面を調整=5件, 観測継続=2件
- 重要度: 中=11件, 高=8件
- 高優先の代表例:
  - 20260507_130500: 通知文面を調整 / 方向バイアス強調より先に「執行不可（WAIT）」を件名冒頭へ固定し、ENTRY_OK表現を監視専用文言に置換する。
  - 20260507_090500: 通知文面を調整 / 「高め本通知」でも執行不可の監視局面は件名先頭に「エントリー非推奨（待機）」を固定表示する。
  - 20260507_070500: 通知文面を調整 / 件名の「高め本通知」と上方向強調を弱め、監視専用通知と即時エントリー通知を文面で明確分離する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=255 / backlog=52 / AI済み=203 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-05-10T18:36:10.587410Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 8/19 件 (42.1%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. NO_TRADE_CANDIDATE が強すぎる
   理由: skip_too_strict が 4/10 件 (40.0%)
   主に触る場所: config.py, src/analysis/position_risk.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 4 件あります
   主に触る場所: tools/log_feedback.py

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=100.0%, 平均MFE=7.39, 平均MAE=2.91 (n=7) / データ不足 7/30
- transition: 勝率=0.0%, 平均MFE=0.00, 平均MAE=10.93 (n=1) / データ不足 1/30
- uptrend: 勝率=61.5%, 平均MFE=5.02, 平均MAE=5.85 (n=13) / データ不足 13/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=71.4%, 平均MFE=5.57, 平均MAE=5.11 (n=21) / データ不足 21/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=75.0%, 平均MFE=6.36, 平均MAE=7.07 (n=4) / データ不足 4/30
- RISKY_ENTRY: 勝率=33.3%, 平均MFE=3.27, 平均MAE=8.18 (n=3) / データ不足 3/30
- SWEEP_WAIT: 勝率=100.0%, 平均MFE=6.85, 平均MAE=4.52 (n=4) / データ不足 4/30
- NO_TRADE_CANDIDATE: 勝率=70.0%, 平均MFE=5.43, 平均MAE=3.64 (n=10) / データ不足 10/30

### bias別件数・勝率
- long: 勝率=71.4% (n=21) / データ不足 21/30

### bias別 direction 正誤
- long: correct=12, wrong=7, unclear=2 / wrong_rate=33.3% (n=21)

### 成績指標
- 全体勝率: 71.4%
- 平均MFE(signal_based): 5.57
- 平均MAE(signal_based): 5.11
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 71.4%

### 通知品質
- A: 通知して良かった = 15件
- B: 通知したが微妙 = 6件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- long_flush_exhaustion: wrong_rate=33.3% (wrong=2/6)
- ask_wall_close: wrong_rate=30.8% (wrong=4/13)
- lower_liquidity_close: wrong_rate=25.0% (wrong=4/16)
- sweep_incomplete: wrong_rate=25.0% (wrong=3/12)
- orderbook_ask_heavy: wrong_rate=25.0% (wrong=2/8)
- short_cover_risk: wrong_rate=12.5% (wrong=1/8)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 4件
- direction_execution_conflict の主な理由: confidence_below_min=4件
- direction_execution_conflict の主な risk_flags: lower_liquidity_close=4件, sweep_incomplete=4件, orderbook_ask_heavy=3件
- suppress_reason の内訳: confidence_below_long_min=7件, watch_sweep_recheck_wait=2件, cooldown_active=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 9件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 21
- 本有効件数: 0
- 参考ログ件数: 21
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 9件
- phase1_observation_gate=blocked: 12件
- 観測タイプ: setup_watch_learning=8件, confidence_watch_learning=1件
- 観測候補全体: 9件 / 勝率=66.7% / TP1先行=66.7% / 近似PF=0.68 / 平均MFE=5.16 / 平均MAE=7.63
- setup_watch_learning: 8件 / 勝率=62.5% / TP1先行=62.5% / 近似PF=0.63 / 平均MFE=4.94 / 平均MAE=7.90
- confidence_watch_learning: 1件 / 勝率=100.0% / TP1先行=100.0% / 近似PF=1.26 / 平均MFE=6.95 / 平均MAE=5.50
- 代表例: 20260510_160500, 20260509_212745, 20260507_130500, 20260507_090500, 20260507_070500
- 主な観測ブロック理由: no_trade_candidate=10件, confidence_below_min=5件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 9件
- 観測タイプ: setup_watch_learning=8件, confidence_watch_learning=1件
- 状態: observing=9件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 75.0%
- 代表例: 20260510_160500, 20260509_212745, 20260507_130500, 20260507_090500, 20260507_070500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### Phase 1B 昇格候補
- confidence_watch_learning 候補: 1件
- prelabel: SWEEP_WAIT=1件
- 勝率=100.0% / TP1先行=100.0% / 近似PF=1.26
- 平均 direction=60.0 / 平均 execution=22.0 / 平均 wait=76.8
- 平均MFE=6.95 / 平均MAE=5.50
- 代表例: 20260509_212745
- 扱い: `trade_execution_gate=pass` ではないが、限定条件付きで Phase 1B 候補へ昇格を検討する母集団

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 21件
- 主なブロック理由: phase1_inactive=21件, setup_not_ready=21件, wait_pressure_too_high=10件, execution_shadow_too_low=10件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 21件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 3/3件

### risk_flags 有効性比較
- ask_wall_close: negative_rate=69.2% (n=13)
- sweep_incomplete: negative_rate=66.7% (n=12)
- lower_liquidity_close: negative_rate=62.5% (n=16)
