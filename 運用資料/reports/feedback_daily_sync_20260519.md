# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 47 件です。近似PF は 0.80、全体勝率は 48.9% でした。
- 事後評価では「待つ判断に使えた」が最も多く、14 件でした。
- 平均の役立ち度は 3.55 / 5 でした。
- 根拠整合の入力率は 34.0%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「反発示唆の過大評価」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-12 05:05 〜 2026-05-17 23:05
- 総観測件数: 47
- データ品質の内訳: ok=47
- 近似PF: 0.80

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=30件, entry_zone_not_reached=12件, near_entry_zone_waiting_trigger=3件, inside_entry_zone_with_trigger=2件
- confidence_below_min 代表例: 20260513_110500(watch/SWEEP_WAIT, dir=58, exec=18, wait=67, MFE24h=15.38, MAE24h=0.00, outcome=win) / 20260516_060500(watch/SWEEP_WAIT, dir=51, exec=18, wait=59, MFE24h=14.77, MAE24h=0.00, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 14件
- 見送り判断に使えた: 4件
- 価値が低かった: 2件
- 平均の役立ち度: 3.55 / 5
- 値動きの主因の入力率: 42.6%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 34.0% / 整合率: 100.0%
- SL評価: SL は妥当=15件, SL が狭すぎた=5件
- TP評価: TP が近すぎた=3件, TP が遠すぎた=6件, TP は妥当=11件
- 4時間足評価: 妥当=7件, 一部弱い=13件
- 1時間足評価: 一部弱い=15件, 妥当=2件, 弱い=3件
- 15分足評価: 一部弱い=8件, 妥当=6件, 弱い=6件
### 改善アクション
- 分類: 入口条件を調整=16件, 観測継続=3件, 通知文面を調整=1件
- 重要度: 高=7件, 中=12件, 低=1件
- 高優先の代表例:
  - 20260516_060500: 入口条件を調整 / 15分足で下抜け再加速が出た時はSWEEP待ちを緩和し、段階的にエントリー許可する条件へ修正する。
  - 20260515_140500: 入口条件を調整 / 15分足で再ショート発火条件を厳格化し、主要サポート直上では通知を待機専用に固定する。
  - 20260513_163400: 入口条件を調整 / 15分足で79,202明確上抜け時はショート監視を即失効にする条件を追加する
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=308 / backlog=77 / AI済み=231 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-05-17T18:36:04.874815Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 反発示唆の過大評価
   理由: countertrend_long_cluster の wrong が 11/18 件 (61.1%)
   主に触る場所: src/analysis/confidence.py, src/analysis/position_risk.py
2. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 3/4 件 (75.0%)
   主に触る場所: config.py, src/analysis/position_risk.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 2 件あります
   主に触る場所: tools/log_feedback.py

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=50.0%, 平均MFE=7.80, 平均MAE=7.45 (n=20) / データ不足 20/30
- transition: 勝率=54.2%, 平均MFE=5.28, 平均MAE=7.62 (n=24) / データ不足 24/30
- uptrend: 勝率=0.0%, 平均MFE=1.10, 平均MAE=7.87 (n=3) / データ不足 3/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=48.9%, 平均MFE=6.09, 平均MAE=7.57 (n=47)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=50.0%, 平均MFE=7.25, 平均MAE=5.65 (n=4) / データ不足 4/30
- RISKY_ENTRY: 勝率=50.0%, 平均MFE=4.37, 平均MAE=8.20 (n=12) / データ不足 12/30
- SWEEP_WAIT: 勝率=58.8%, 平均MFE=6.76, 平均MAE=8.00 (n=17) / データ不足 17/30
- NO_TRADE_CANDIDATE: 勝率=35.7%, 平均MFE=6.40, 平均MAE=7.05 (n=14) / データ不足 14/30

### bias別件数・勝率
- long: 勝率=27.3% (n=22) / データ不足 22/30
- short: 勝率=68.0% (n=25) / データ不足 25/30

### bias別 direction 正誤
- long: correct=5, wrong=12, unclear=5 / wrong_rate=54.5% (n=22)
- short: correct=13, wrong=10, unclear=2 / wrong_rate=40.0% (n=25)

### 成績指標
- 全体勝率: 48.9%
- 平均MFE(signal_based): 6.09
- 平均MAE(signal_based): 7.57
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 48.9%

### 通知品質
- A: 通知して良かった = 23件
- B: 通知したが微妙 = 24件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- failed_breakout_up_reversal: wrong_rate=66.7% (wrong=6/9)
- trend_flip_confirmed_up: wrong_rate=62.5% (wrong=5/8)
- lower_liquidity_close: wrong_rate=61.1% (wrong=11/18)
- trend_flip_confirmed_down: wrong_rate=56.2% (wrong=9/16)
- long_flush_exhaustion: wrong_rate=55.6% (wrong=5/9)
- orderbook_ask_heavy: wrong_rate=54.5% (wrong=6/11)
- sweep_incomplete: wrong_rate=51.4% (wrong=18/35)
- major_support_rejection: wrong_rate=50.0% (wrong=7/14)
- ask_wall_close: wrong_rate=50.0% (wrong=5/10)
- orderbook_bid_heavy: wrong_rate=44.4% (wrong=4/9)
- support_to_resistance_retest_confirmed: wrong_rate=43.5% (wrong=10/23)
- support_to_resistance_flip: wrong_rate=43.5% (wrong=10/23)
- cvd_bullish_divergence: wrong_rate=42.9% (wrong=3/7)
- short_cover_risk: wrong_rate=41.7% (wrong=5/12)
- short_into_major_support: wrong_rate=39.4% (wrong=13/33)
- long_into_major_resistance: wrong_rate=37.5% (wrong=12/32)
- resistance_to_support_retest_confirmed: wrong_rate=35.7% (wrong=5/14)
- resistance_to_support_flip: wrong_rate=35.7% (wrong=5/14)
- bid_wall_close: wrong_rate=33.3% (wrong=3/9)
- upper_liquidity_close: wrong_rate=26.3% (wrong=5/19)
- failed_breakout_down_reversal: wrong_rate=22.2% (wrong=2/9)
- major_resistance_rejection: wrong_rate=21.4% (wrong=3/14)
- trend_flip_early_up: wrong_rate=20.0% (wrong=1/5)
- trend_flip_early_down: wrong_rate=11.1% (wrong=1/9)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 2件
- direction_execution_conflict の主な理由: confidence_below_min=2件
- direction_execution_conflict の主な risk_flags: bid_wall_close=2件, sweep_incomplete=2件, upper_liquidity_close=2件
- suppress_reason の内訳: confidence_below_short_min=10件, bias_wait=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 0件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 47
- 本有効件数: 0
- 参考ログ件数: 47
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 9件
- phase1_observation_gate=blocked: 38件
- 観測タイプ: setup_watch_learning=9件
- 観測候補全体: 9件 / 勝率=44.4% / TP1先行=44.4% / 近似PF=0.46 / 平均MFE=4.22 / 平均MAE=9.10
- setup_watch_learning: 9件 / 勝率=44.4% / TP1先行=44.4% / 近似PF=0.46 / 平均MFE=4.22 / 平均MAE=9.10
- 代表例: 20260517_010500, 20260514_160500, 20260514_080500, 20260513_163400, 20260513_120500
- 主な観測ブロック理由: confidence_below_min=30件, no_trade_candidate=14件, watch_conditions_not_met=1件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 9件
- 観測タイプ: setup_watch_learning=9件
- 状態: observing=9件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 77.8%
- 代表例: 20260517_010500, 20260514_160500, 20260514_080500, 20260513_163400, 20260513_120500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### Phase 1B 昇格候補
- confidence_watch_learning 候補: 0件
- 扱い: `trade_execution_gate=pass` ではないが、限定条件付きで Phase 1B 候補へ昇格を検討する母集団

### Phase 1B-lite
- lite 候補: 0件
- phase1b_lite_paper_orders observing: 5件
- lite pass だが専用紙トレード未記録: 0件
- 状態: observing=5件
- 扱い: 実弾ではなく、正式 Phase 1B でもない。件名ランクは執行候補へ上げない

### counter_long_short_watch
- 候補件数: 0件
- 扱い: ロング監視の失敗初動をショート観測候補として切り出す Phase 1A 母集団

### failed_breakout_down_reversal
- 件数: 0件
- 扱い: breakout_up が効かず大きく下落した watch 群の失敗型を継続追跡する

### market_map
- 記録あり: 39件
- primary_state: confirmed_down=16件, early_down=9件, confirmed_up=8件, early_up=5件, near_major_resistance=1件
- flags: short_into_major_support=33件, long_into_major_resistance=32件, support_to_resistance_flip=23件, support_to_resistance_retest_confirmed=23件, trend_flip_confirmed_down=16件, major_resistance_rejection=14件, resistance_to_support_flip=14件, resistance_to_support_retest_confirmed=14件
- trend_state: confirmed_down=16件, early_down=9件, confirmed_up=8件, early_up=5件
- 下方向反転系: 25件 / 勝率=64.0% / wrong_rate=40.0%
- 下方向反転系 平均MFE24h=8.76 / 平均MAE24h=5.74
- 代表例: 20260517_140501, 20260517_110500, 20260517_050500, 20260517_010500, 20260516_220500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 47件
- 主なブロック理由: phase1_inactive=47件, setup_not_ready=47件, execution_shadow_too_low=25件, wait_pressure_too_high=23件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 47件
- opportunity_gate=pass: 33件
- paper_positions 記録: 33件
- 紙ポジション状態: closed=33件
- 紙ポジション終了状態: sl_hit=17件, missed_opportunity=13件, tp2_hit=3件
- 紙実行候補タイプ: market_map_opportunity=24件, setup_watch_learning=9件
- opportunity_type 別 closed:
  - market_map_opportunity: 24件 / 勝率=12.5% / 平均R=0.47 / 簡易PF=2.24
  - setup_watch_learning: 9件 / 勝率=0.0% / 平均R=-0.12 / 簡易PF=0.78
- missed_opportunity: 13件
- missed代表例: 20260517_140501, 20260517_110500, 20260517_010500
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 3/3件

### risk_flags 有効性比較
- lower_liquidity_close: negative_rate=94.4% (n=18)
- sweep_incomplete: negative_rate=88.6% (n=35)
- major_support_rejection: negative_rate=85.7% (n=14)
- short_cover_risk: negative_rate=83.3% (n=12)
- orderbook_ask_heavy: negative_rate=81.8% (n=11)
- trend_flip_confirmed_down: negative_rate=81.2% (n=16)
- ask_wall_close: negative_rate=80.0% (n=10)
- resistance_to_support_retest_confirmed: negative_rate=78.6% (n=14)
- resistance_to_support_flip: negative_rate=78.6% (n=14)
- short_into_major_support: negative_rate=75.8% (n=33)
- long_into_major_resistance: negative_rate=75.0% (n=32)
- major_resistance_rejection: negative_rate=71.4% (n=14)
- support_to_resistance_retest_confirmed: negative_rate=69.6% (n=23)
- support_to_resistance_flip: negative_rate=69.6% (n=23)
- upper_liquidity_close: negative_rate=68.4% (n=19)
