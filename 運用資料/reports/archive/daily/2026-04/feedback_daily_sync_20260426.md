# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 34 件です。近似PF は 0.81、全体勝率は 64.7% でした。
- 事後評価では「待つ判断に使えた」が最も多く、14 件でした。
- 平均の役立ち度は 3.26 / 5 でした。
- 根拠整合の入力率は 55.9%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-19 09:05 〜 2026-04-24 22:05
- 総観測件数: 34
- データ品質の内訳: ok=34
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
- ready阻害理由: entry_zone_not_reached=16件, near_entry_zone_waiting_trigger=8件, confidence_below_min=7件, inside_entry_zone_with_trigger=3件
- confidence_below_min 代表例: 20260421_080500(invalid/NO_TRADE_CANDIDATE, dir=61, exec=5, wait=100, MFE24h=12.70, MAE24h=6.78, outcome=win) / 20260420_020500(watch/SWEEP_WAIT, dir=52, exec=12, wait=93, MFE24h=8.01, MAE24h=1.98, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 14件
- 通知が早すぎた: 2件
- 価値が低かった: 2件
- 通知が遅すぎた: 1件
- 平均の役立ち度: 3.26 / 5
- 値動きの主因の入力率: 55.9%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 55.9% / 整合率: 100.0%
- SL評価: SL は妥当=12件, SL が狭すぎた=7件
- TP評価: TP が遠すぎた=5件, TP は妥当=11件, TP が近すぎた=3件
- 4時間足評価: 一部弱い=9件, 妥当=9件, 弱い=1件
- 1時間足評価: 妥当=2件, 一部弱い=17件
- 15分足評価: 妥当=5件, 弱い=8件, 一部弱い=6件
### 改善アクション
- 分類: 通知文面を調整=4件, 入口条件を調整=13件, 観測継続=2件
- 重要度: 高=10件, 中=9件
- 高優先の代表例:
  - 20260423_160501: 通知文面を調整 / 件名と冒頭で「エントリー禁止の監視通知」であることを先頭固定し、上方向バイアス表現より待機条件を前面化する。
  - 20260423_150500: 通知文面を調整 / 件名と冒頭で「監視継続・未発火」を先頭固定し、方向バイアスより先に実行条件未達を明記する。
  - 20260423_130500: 入口条件を調整 / 15分足の発火条件に「下側流動性スイープ後の反発確定」を必須化して早入りを防ぐ。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=192 / backlog=53 / AI済み=139 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-04-24T18:36:40.272956Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 8/19 件 (42.1%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. SL が狭すぎるケースが多い
   理由: sl_eval=too_tight が 7/19 件 (36.8%)
   主に触る場所: src/analysis/rr.py
3. NO_TRADE_CANDIDATE が強すぎる
   理由: skip_too_strict が 4/9 件 (44.4%)
   主に触る場所: config.py, src/analysis/position_risk.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 12件
- 主な通知理由: prelabel_improved=10件, status_upgraded=8件, confidence_jump=6件
- 代表例: 20260422_050500(confidence_jump,prelabel_improved, exec=35, wait=24) / 20260423_100500(confidence_jump,prelabel_improved, exec=35, wait=32) / 20260420_060500(prelabel_improved, exec=35, wait=40)
- 現行watch再計算: 20260422_050500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260423_100500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260420_060500=>watch/entry_zone_not_reached/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=75.0%, 平均MFE=5.12, 平均MAE=6.50 (n=12) / データ不足 12/30
- transition: 勝率=80.0%, 平均MFE=6.50, 平均MAE=4.80 (n=5) / データ不足 5/30
- uptrend: 勝率=52.9%, 平均MFE=3.29, 平均MAE=4.92 (n=17) / データ不足 17/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=64.7%, 平均MFE=4.41, 平均MAE=5.46 (n=34)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=4.77, 平均MAE=6.57 (n=2) / データ不足 2/30
- RISKY_ENTRY: 勝率=85.7%, 平均MFE=3.93, 平均MAE=5.06 (n=7) / データ不足 7/30
- SWEEP_WAIT: 勝率=43.8%, 平均MFE=3.97, 平均MAE=6.39 (n=16) / データ不足 16/30
- NO_TRADE_CANDIDATE: 勝率=77.8%, 平均MFE=5.47, 平均MAE=3.87 (n=9) / データ不足 9/30

### bias別件数・勝率
- long: 勝率=65.6% (n=32)
- short: 勝率=50.0% (n=2) / データ不足 2/30

### bias別 direction 正誤
- long: correct=12, wrong=16, unclear=4 / wrong_rate=50.0% (n=32)
- short: correct=0, wrong=2, unclear=0 / wrong_rate=100.0% (n=2)

### 成績指標
- 全体勝率: 64.7%
- 平均MFE(signal_based): 4.41
- 平均MAE(signal_based): 5.46
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 64.7%

### 通知品質
- A: 通知して良かった = 22件
- B: 通知したが微妙 = 12件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- cvd_bearish_divergence: wrong_rate=71.4% (wrong=5/7)
- short_cover_risk: wrong_rate=66.7% (wrong=4/6)
- orderbook_ask_heavy: wrong_rate=52.9% (wrong=9/17)
- sweep_incomplete: wrong_rate=52.0% (wrong=13/25)
- lower_liquidity_close: wrong_rate=50.0% (wrong=13/26)
- long_flush_exhaustion: wrong_rate=33.3% (wrong=2/6)
- ask_wall_close: wrong_rate=16.7% (wrong=2/12)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 1件
- direction_execution_conflict の主な理由: inside_entry_zone_with_trigger=1件
- direction_execution_conflict の主な risk_flags: lower_liquidity_close=1件, orderbook_ask_heavy=1件
- suppress_reason の内訳: confidence_below_long_min=7件, bias_wait=3件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 7件

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

### Phase 1 観測 gate
- phase1_observation_gate=pass: 13件
- phase1_observation_gate=blocked: 21件
- 観測タイプ: setup_watch_learning=13件
- 観測候補全体: 13件 / 勝率=76.9% / TP1先行=76.9% / 近似PF=0.73 / 平均MFE=3.93 / 平均MAE=5.36
- setup_watch_learning: 13件 / 勝率=76.9% / TP1先行=76.9% / 近似PF=0.73 / 平均MFE=3.93 / 平均MAE=5.36
- 代表例: 20260423_150500, 20260423_100500, 20260422_230500, 20260422_210500, 20260422_140500
- 主な観測ブロック理由: no_trade_candidate=9件, confidence_below_min=7件, watch_conditions_not_met=7件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 13件
- 観測タイプ: setup_watch_learning=13件
- 状態: observing=13件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 69.2%
- 代表例: 20260423_150500, 20260423_100500, 20260422_230500, 20260422_210500, 20260422_140500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 34件
- 主なブロック理由: phase1_inactive=34件, setup_not_ready=34件, execution_shadow_too_low=17件, wait_pressure_too_high=14件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 34件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 3/3件

### risk_flags 有効性比較
- lower_liquidity_close: negative_rate=76.9% (n=26)
- orderbook_ask_heavy: negative_rate=76.5% (n=17)
- sweep_incomplete: negative_rate=76.0% (n=25)
- ask_wall_close: negative_rate=50.0% (n=12)
