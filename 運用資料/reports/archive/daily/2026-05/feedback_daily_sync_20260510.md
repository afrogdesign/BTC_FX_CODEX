# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 24 件です。近似PF は 1.37、全体勝率は 66.7% でした。
- 事後評価では「待つ判断に使えた」が最も多く、13 件でした。
- 平均の役立ち度は 3.60 / 5 でした。
- 根拠整合の入力率は 75.0%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-03 08:05 〜 2026-05-08 17:05
- 総観測件数: 24
- データ品質の内訳: ok=24
- 近似PF: 1.37

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: entry_zone_not_reached=14件, near_entry_zone_waiting_trigger=5件, confidence_below_min=4件, inside_entry_zone_with_trigger=1件
- confidence_below_min 代表例: 20260503_160500(invalid/NO_TRADE_CANDIDATE, dir=49, exec=5, wait=100, MFE24h=17.74, MAE24h=4.26, outcome=win) / 20260503_140500(watch/SWEEP_WAIT, dir=52, exec=20, wait=80, MFE24h=16.79, MAE24h=4.12, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 13件
- 見送り判断に使えた: 4件
- 価値が低かった: 2件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.60 / 5
- 値動きの主因の入力率: 83.3%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 75.0% / 整合率: 100.0%
- SL評価: SL は妥当=16件, SL が狭すぎた=4件
- TP評価: TP が遠すぎた=5件, TP は妥当=10件, TP が近すぎた=5件
- 4時間足評価: 一部弱い=8件, 弱い=1件, 妥当=11件
- 1時間足評価: 一部弱い=16件, 妥当=4件
- 15分足評価: 妥当=6件, 弱い=9件, 一部弱い=5件
### 改善アクション
- 分類: 通知文面を調整=5件, 入口条件を調整=13件, 観測継続=2件
- 重要度: 高=11件, 中=8件, 低=1件
- 高優先の代表例:
  - 20260507_130500: 通知文面を調整 / 方向バイアス強調より先に「執行不可（WAIT）」を件名冒頭へ固定し、ENTRY_OK表現を監視専用文言に置換する。
  - 20260507_090500: 通知文面を調整 / 「高め本通知」でも執行不可の監視局面は件名先頭に「エントリー非推奨（待機）」を固定表示する。
  - 20260507_070500: 通知文面を調整 / 件名の「高め本通知」と上方向強調を弱め、監視専用通知と即時エントリー通知を文面で明確分離する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=250 / backlog=55 / AI済み=195 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-05-08T19:02:38.187743Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 9/20 件 (45.0%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 3/5 件 (60.0%)
   主に触る場所: config.py, src/analysis/position_risk.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 3 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 1件
- 主な通知理由: bias_changed=1件, confidence_jump=1件
- 代表例: 20260503_200500(bias_changed,confidence_jump, exec=20, wait=48)
- 現行watch再計算: 20260503_200500=>watch/entry_zone_not_reached/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=83.3%, 平均MFE=11.90, 平均MAE=3.00 (n=6) / データ不足 6/30
- transition: 勝率=0.0%, 平均MFE=0.00, 平均MAE=10.93 (n=1) / データ不足 1/30
- uptrend: 勝率=64.7%, 平均MFE=6.10, 平均MAE=5.80 (n=17) / データ不足 17/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=66.7%, 平均MFE=7.30, 平均MAE=5.32 (n=24) / データ不足 24/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=60.0%, 平均MFE=5.03, 平均MAE=6.05 (n=5) / データ不足 5/30
- RISKY_ENTRY: 勝率=50.0%, 平均MFE=7.41, 平均MAE=6.42 (n=4) / データ不足 4/30
- SWEEP_WAIT: 勝率=100.0%, 平均MFE=13.71, 平均MAE=6.73 (n=3) / データ不足 3/30
- NO_TRADE_CANDIDATE: 勝率=66.7%, 平均MFE=6.60, 平均MAE=4.29 (n=12) / データ不足 12/30

### bias別件数・勝率
- long: 勝率=66.7% (n=24) / データ不足 24/30

### bias別 direction 正誤
- long: correct=13, wrong=8, unclear=3 / wrong_rate=33.3% (n=24)

### 成績指標
- 全体勝率: 66.7%
- 平均MFE(signal_based): 7.30
- 平均MAE(signal_based): 5.32
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 66.7%

### 通知品質
- A: 通知して良かった = 16件
- B: 通知したが微妙 = 8件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- ask_wall_close: wrong_rate=33.3% (wrong=4/12)
- short_cover_risk: wrong_rate=30.0% (wrong=3/10)
- orderbook_ask_heavy: wrong_rate=30.0% (wrong=3/10)
- sweep_incomplete: wrong_rate=29.4% (wrong=5/17)
- long_flush_exhaustion: wrong_rate=28.6% (wrong=2/7)
- lower_liquidity_close: wrong_rate=27.8% (wrong=5/18)

### 直近12時間速報
- 対象件数: 11件
- direction_execution_conflict: 3件
- direction_execution_conflict の主な理由: confidence_below_min=3件
- direction_execution_conflict の主な risk_flags: lower_liquidity_close=3件, sweep_incomplete=3件, orderbook_ask_heavy=2件
- suppress_reason の内訳: confidence_below_long_min=9件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 9件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 24
- 本有効件数: 0
- 参考ログ件数: 24
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 11件
- phase1_observation_gate=blocked: 13件
- 観測タイプ: setup_watch_learning=11件
- 観測候補全体: 11件 / 勝率=63.6% / TP1先行=63.6% / 近似PF=1.10 / 平均MFE=7.19 / 平均MAE=6.55
- setup_watch_learning: 11件 / 勝率=63.6% / TP1先行=63.6% / 近似PF=1.10 / 平均MFE=7.19 / 平均MAE=6.55
- 代表例: 20260507_130500, 20260507_090500, 20260507_070500, 20260507_050501, 20260506_090500
- 主な観測ブロック理由: no_trade_candidate=12件, confidence_below_min=4件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 11件
- 観測タイプ: setup_watch_learning=11件
- 状態: observing=11件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 72.7%
- 代表例: 20260507_130500, 20260507_090500, 20260507_070500, 20260507_050501, 20260506_090500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### Phase 1B 昇格候補
- confidence_watch_learning 候補: 0件
- 扱い: `trade_execution_gate=pass` ではないが、限定条件付きで Phase 1B 候補へ昇格を検討する母集団

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 24件
- 主なブロック理由: phase1_inactive=24件, setup_not_ready=24件, execution_shadow_too_low=13件, wait_pressure_too_high=10件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 24件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 5/5件

### risk_flags 有効性比較
- orderbook_ask_heavy: negative_rate=60.0% (n=10)
- ask_wall_close: negative_rate=58.3% (n=12)
- sweep_incomplete: negative_rate=52.9% (n=17)
- lower_liquidity_close: negative_rate=50.0% (n=18)
- short_cover_risk: negative_rate=50.0% (n=10)
