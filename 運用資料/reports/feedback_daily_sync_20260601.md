# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 36 件です。近似PF は 1.39、全体勝率は 63.9% でした。
- 事後評価では「待つ判断に使えた」が最も多く、23 件でした。
- 平均の役立ち度は 3.58 / 5 でした。
- 根拠整合の入力率は 83.3%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-25 05:05 〜 2026-05-30 23:05
- 総観測件数: 36
- データ品質の内訳: ok=36
- 近似PF: 1.39

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=17件, entry_zone_not_reached=11件, near_entry_zone_waiting_trigger=6件, inside_entry_zone_with_trigger=2件
- confidence_below_min 代表例: 20260527_130500(invalid/NO_TRADE_CANDIDATE, dir=68, exec=11, wait=78, MFE24h=18.16, MAE24h=0.00, outcome=win) / 20260525_190500(watch/SWEEP_WAIT, dir=66, exec=28, wait=59, MFE24h=15.65, MAE24h=4.85, outcome=win)

## 4. AI事後評価サマリー
- 待つ判断に使えた: 23件
- 見送り判断に使えた: 5件
- 通知が遅すぎた: 1件
- 価値が低かった: 1件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.58 / 5
- レビュー source: ai=31件
- 値動きの主因の入力率: 86.1%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 83.3% / 整合率: 100.0%
- SL評価: SL が狭すぎた=9件, SL は妥当=21件, SL が広すぎた=1件
- TP評価: TP は妥当=23件, TP が遠すぎた=4件, TP が近すぎた=4件
- 4時間足評価: 一部弱い=22件, 妥当=9件
- 1時間足評価: 一部弱い=26件, 妥当=5件
- 15分足評価: 妥当=11件, 弱い=13件, 一部弱い=7件
### 改善アクション
- 分類: 入口条件を調整=22件, 観測継続=7件, 通知文面を調整=1件, 出口設計を調整=1件
- 重要度: 中=20件, 高=9件, 低=2件
- 高優先の代表例:
  - 20260529_050500: 入口条件を調整 / 15分足で上側流動性回収後の再失速確認（73,655付近の再拒否と出来高条件）を満たすまで通知を発火しない。
  - 20260529_030500: 入口条件を調整 / 15分足で主要サポート近接時は逆張り反発優先の待機条件を追加し、戻り売り発火をさらに遅らせる。
  - 20260528_070500: 入口条件を調整 / 15分足で再検討帯未到達かつ直下サポート近接時はショート監視通知の発火を抑制する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=393 / backlog=62 / AI済み=331 / human_override=0
- 今回の同期: created=8 / reused=0 / request_failed=0 / daily_cap=8
- 最終AI評価: 2026-05-30T18:37:39.217245Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 13/31 件 (41.9%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 3/3 件 (100.0%)
   主に触る場所: config.py, src/analysis/position_risk.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 2 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 2件
- 主な通知理由: bias_changed=1件, attention_bias_changed=1件
- 代表例: 20260530_010500(bias_changed, exec=18, wait=51) / 20260526_110500(attention_bias_changed, exec=15, wait=64)
- 現行watch再計算: 20260530_010500=>watch/entry_zone_not_reached/rr=1.30 / 20260526_110500=>ready/inside_entry_zone_with_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- downtrend: 勝率=50.0%, 平均MFE=4.10, 平均MAE=4.72 (n=6) / データ不足 6/30
- range: 勝率=62.5%, 平均MFE=6.86, 平均MAE=4.92 (n=24) / データ不足 24/30
- transition: 勝率=80.0%, 平均MFE=9.08, 平均MAE=5.33 (n=5) / データ不足 5/30
- volatile: 勝率=100.0%, 平均MFE=6.31, 平均MAE=0.23 (n=1) / データ不足 1/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=63.9%, 平均MFE=6.69, 平均MAE=4.81 (n=36)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=10.27, 平均MAE=2.51 (n=3) / データ不足 3/30
- RISKY_ENTRY: 勝率=40.0%, 平均MFE=5.77, 平均MAE=5.43 (n=10) / データ不足 10/30
- SWEEP_WAIT: 勝率=77.8%, 平均MFE=7.87, 平均MAE=3.82 (n=9) / データ不足 9/30
- NO_TRADE_CANDIDATE: 勝率=64.3%, 平均MFE=5.83, 平均MAE=5.50 (n=14) / データ不足 14/30

### bias別件数・勝率
- long: 勝率=40.0% (n=5) / データ不足 5/30
- short: 勝率=67.7% (n=31)

### bias別 direction 正誤
- long: correct=1, wrong=3, unclear=1 / wrong_rate=60.0% (n=5)
- short: correct=11, wrong=14, unclear=6 / wrong_rate=45.2% (n=31)

### 成績指標
- 全体勝率: 63.9%
- 平均MFE(signal_based): 6.69
- 平均MAE(signal_based): 4.81
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 65.7%

### 通知品質
- A: 通知して良かった = 23件
- B: 通知したが微妙 = 13件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- trend_flip_confirmed_up: wrong_rate=80.0% (wrong=4/5)
- trend_flip_confirmed_down: wrong_rate=66.7% (wrong=8/12)
- resistance_to_support_retest_confirmed: wrong_rate=66.7% (wrong=4/6)
- resistance_to_support_flip: wrong_rate=66.7% (wrong=4/6)
- failed_breakout_up_reversal: wrong_rate=60.0% (wrong=3/5)
- lower_liquidity_close: wrong_rate=60.0% (wrong=3/5)
- bid_wall_close: wrong_rate=53.3% (wrong=8/15)
- long_into_major_resistance: wrong_rate=47.8% (wrong=11/23)
- short_into_major_support: wrong_rate=46.4% (wrong=13/28)
- long_flush_exhaustion: wrong_rate=44.4% (wrong=4/9)
- major_support_rejection: wrong_rate=44.4% (wrong=4/9)
- support_to_resistance_retest_confirmed: wrong_rate=43.5% (wrong=10/23)
- upper_liquidity_close: wrong_rate=42.3% (wrong=11/26)
- support_to_resistance_flip: wrong_rate=41.7% (wrong=10/24)
- cvd_bearish_divergence: wrong_rate=40.0% (wrong=2/5)
- orderbook_bid_heavy: wrong_rate=37.5% (wrong=6/16)
- short_cover_risk: wrong_rate=37.5% (wrong=3/8)
- sweep_incomplete: wrong_rate=36.4% (wrong=8/22)
- failed_breakout_down_reversal: wrong_rate=25.0% (wrong=2/8)
- major_resistance_rejection: wrong_rate=23.1% (wrong=3/13)
- trend_flip_early_down: wrong_rate=18.8% (wrong=3/16)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 2件
- direction_execution_conflict の主な理由: confidence_below_min=2件
- direction_execution_conflict の主な risk_flags: orderbook_bid_heavy=2件, sweep_incomplete=2件, upper_liquidity_close=2件
- suppress_reason の内訳: confidence_below_short_min=4件, cooldown_active=1件, watch_sweep_recheck_wait=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 0件

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

### Phase 1 観測 gate
- phase1_observation_gate=pass: 11件
- phase1_observation_gate=blocked: 25件
- 観測タイプ: setup_watch_learning=11件
- 観測候補全体: 11件 / 勝率=54.5% / TP1先行=60.0% / 近似PF=2.61 / 平均MFE=8.28 / 平均MAE=3.17
- setup_watch_learning: 11件 / 勝率=54.5% / TP1先行=60.0% / 近似PF=2.61 / 平均MFE=8.28 / 平均MAE=3.17
- 代表例: 20260529_220500, 20260529_050500, 20260528_070500, 20260528_040500, 20260528_010500
- 主な観測ブロック理由: confidence_below_min=17件, no_trade_candidate=14件, watch_conditions_not_met=2件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 11件
- 観測タイプ: setup_watch_learning=11件
- 状態: observing=11件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 45.5%
- 代表例: 20260529_220500, 20260529_050500, 20260528_070500, 20260528_040500, 20260528_010500
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
- 記録あり: 36件
- primary_state: early_down=16件, confirmed_down=12件, confirmed_up=5件, near_major_resistance=2件, active_support=1件
- flags: short_into_major_support=28件, support_to_resistance_flip=24件, long_into_major_resistance=23件, support_to_resistance_retest_confirmed=23件, trend_flip_early_down=16件, major_resistance_rejection=13件, trend_flip_confirmed_down=12件, major_support_rejection=9件
- trend_state: early_down=16件, confirmed_down=12件, confirmed_up=5件
- 下方向反転系: 28件 / 勝率=64.3% / wrong_rate=39.3%
- 下方向反転系 平均MFE24h=7.51 / 平均MAE24h=3.83
- 代表例: 20260530_080500, 20260530_010500, 20260529_230500, 20260529_220500, 20260529_130500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 36件
- 主なブロック理由: phase1_inactive=36件, setup_not_ready=36件, no_trade_flags_present=29件, wait_pressure_too_high=17件, execution_shadow_too_low=12件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 36件
- opportunity_gate=pass: 14件
- paper_positions 記録: 14件
- 紙ポジション状態: closed=14件
- 紙ポジション終了状態: sl_hit=6件, missed_opportunity=6件, timeout=1件, tp2_hit=1件
- 紙実行候補タイプ: setup_watch_learning=11件, market_map_opportunity=3件
- opportunity_type 別 closed:
  - market_map_opportunity: 3件 / 勝率=0.0% / 平均R=1.30 / 簡易PF=0.00
  - setup_watch_learning: 11件 / 勝率=9.1% / 平均R=0.16 / 簡易PF=1.39
- missed_opportunity: 6件
- missed代表例: 20260528_070500, 20260528_040500, 20260528_010500
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 4/4件

### risk_flags 有効性比較
- trend_flip_confirmed_down: negative_rate=91.7% (n=12)
- bid_wall_close: negative_rate=80.0% (n=15)
- long_into_major_resistance: negative_rate=78.3% (n=23)
- short_into_major_support: negative_rate=75.0% (n=28)
- support_to_resistance_flip: negative_rate=75.0% (n=24)
- orderbook_bid_heavy: negative_rate=75.0% (n=16)
- support_to_resistance_retest_confirmed: negative_rate=73.9% (n=23)
- upper_liquidity_close: negative_rate=69.2% (n=26)
- sweep_incomplete: negative_rate=63.6% (n=22)
- trend_flip_early_down: negative_rate=62.5% (n=16)
- major_resistance_rejection: negative_rate=61.5% (n=13)
