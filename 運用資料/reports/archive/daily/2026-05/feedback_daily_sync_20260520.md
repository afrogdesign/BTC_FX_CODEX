# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 43 件です。近似PF は 0.92、全体勝率は 60.5% でした。
- 事後評価では「待つ判断に使えた」が最も多く、13 件でした。
- 平均の役立ち度は 3.55 / 5 でした。
- 根拠整合の入力率は 34.9%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-13 04:05 〜 2026-05-18 22:05
- 総観測件数: 43
- データ品質の内訳: ok=43
- 近似PF: 0.92

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=30件, entry_zone_not_reached=10件, near_entry_zone_waiting_trigger=2件, inside_entry_zone_with_trigger=1件
- confidence_below_min 代表例: 20260513_110500(watch/SWEEP_WAIT, dir=58, exec=18, wait=67, MFE24h=15.38, MAE24h=0.00, outcome=win) / 20260516_060500(watch/SWEEP_WAIT, dir=51, exec=18, wait=59, MFE24h=14.77, MAE24h=0.00, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 13件
- 見送り判断に使えた: 4件
- 価値が低かった: 3件
- 平均の役立ち度: 3.55 / 5
- 値動きの主因の入力率: 46.5%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 34.9% / 整合率: 100.0%
- SL評価: SL が狭すぎた=5件, SL は妥当=15件
- TP評価: TP は妥当=10件, TP が近すぎた=4件, TP が遠すぎた=6件
- 4時間足評価: 妥当=8件, 一部弱い=12件
- 1時間足評価: 一部弱い=14件, 妥当=3件, 弱い=3件
- 15分足評価: 弱い=7件, 妥当=6件, 一部弱い=7件
### 改善アクション
- 分類: 入口条件を調整=16件, 観測継続=3件, 通知文面を調整=1件
- 重要度: 高=7件, 中=12件, 低=1件
- 高優先の代表例:
  - 20260517_140501: 入口条件を調整 / 15分足で上側流動性回収と再失速確認が出るまでエントリー無効を明示し、発火条件を厳格化する。
  - 20260516_060500: 入口条件を調整 / 15分足で下抜け再加速が出た時はSWEEP待ちを緩和し、段階的にエントリー許可する条件へ修正する。
  - 20260515_140500: 入口条件を調整 / 15分足で再ショート発火条件を厳格化し、主要サポート直上では通知を待機専用に固定する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=312 / backlog=77 / AI済み=235 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-05-18T18:36:05.225884Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 7/20 件 (35.0%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=68.4%, 平均MFE=8.36, 平均MAE=6.61 (n=19) / データ不足 19/30
- transition: 勝率=54.2%, 平均MFE=5.28, 平均MAE=7.62 (n=24) / データ不足 24/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=60.5%, 平均MFE=6.64, 平均MAE=7.18 (n=43)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=66.7%, 平均MFE=7.98, 平均MAE=5.76 (n=3) / データ不足 3/30
- RISKY_ENTRY: 勝率=66.7%, 平均MFE=5.11, 平均MAE=8.73 (n=9) / データ不足 9/30
- SWEEP_WAIT: 勝率=64.7%, 平均MFE=7.16, 平均MAE=7.22 (n=17) / データ不足 17/30
- NO_TRADE_CANDIDATE: 勝率=50.0%, 平均MFE=6.70, 平均MAE=6.43 (n=14) / データ不足 14/30

### bias別件数・勝率
- long: 勝率=37.5% (n=16) / データ不足 16/30
- short: 勝率=74.1% (n=27) / データ不足 27/30

### bias別 direction 正誤
- long: correct=4, wrong=7, unclear=5 / wrong_rate=43.8% (n=16)
- short: correct=15, wrong=9, unclear=3 / wrong_rate=33.3% (n=27)

### 成績指標
- 全体勝率: 60.5%
- 平均MFE(signal_based): 6.64
- 平均MAE(signal_based): 7.18
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 60.5%

### 通知品質
- A: 通知して良かった = 26件
- B: 通知したが微妙 = 17件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- trend_flip_confirmed_up: wrong_rate=62.5% (wrong=5/8)
- failed_breakout_up_reversal: wrong_rate=60.0% (wrong=6/10)
- trend_flip_confirmed_down: wrong_rate=52.9% (wrong=9/17)
- lower_liquidity_close: wrong_rate=50.0% (wrong=6/12)
- long_flush_exhaustion: wrong_rate=50.0% (wrong=5/10)
- major_support_rejection: wrong_rate=46.7% (wrong=7/15)
- orderbook_ask_heavy: wrong_rate=44.4% (wrong=4/9)
- sweep_incomplete: wrong_rate=42.4% (wrong=14/33)
- short_cover_risk: wrong_rate=41.7% (wrong=5/12)
- support_to_resistance_flip: wrong_rate=40.0% (wrong=10/25)
- support_to_resistance_retest_confirmed: wrong_rate=40.0% (wrong=10/25)
- orderbook_bid_heavy: wrong_rate=40.0% (wrong=4/10)
- long_into_major_resistance: wrong_rate=37.5% (wrong=12/32)
- short_into_major_support: wrong_rate=36.1% (wrong=13/36)
- resistance_to_support_retest_confirmed: wrong_rate=35.7% (wrong=5/14)
- resistance_to_support_flip: wrong_rate=35.7% (wrong=5/14)
- bid_wall_close: wrong_rate=30.0% (wrong=3/10)
- ask_wall_close: wrong_rate=25.0% (wrong=2/8)
- upper_liquidity_close: wrong_rate=22.7% (wrong=5/22)
- failed_breakout_down_reversal: wrong_rate=22.2% (wrong=2/9)
- major_resistance_rejection: wrong_rate=21.4% (wrong=3/14)
- cvd_bullish_divergence: wrong_rate=16.7% (wrong=1/6)
- trend_flip_early_up: wrong_rate=16.7% (wrong=1/6)
- trend_flip_early_down: wrong_rate=10.0% (wrong=1/10)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 1件
- direction_execution_conflict の主な理由: confidence_below_min=1件
- direction_execution_conflict の主な risk_flags: bid_wall_close=1件, cvd_bearish_divergence=1件, short_cover_risk=1件
- suppress_reason の内訳: confidence_below_short_min=4件, bias_wait=2件, watch_sweep_recheck_wait=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 0件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 43
- 本有効件数: 0
- 参考ログ件数: 43
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 6件
- phase1_observation_gate=blocked: 37件
- 観測タイプ: setup_watch_learning=6件
- 観測候補全体: 6件 / 勝率=66.7% / TP1先行=66.7% / 近似PF=0.48 / 平均MFE=4.95 / 平均MAE=10.27
- setup_watch_learning: 6件 / 勝率=66.7% / TP1先行=66.7% / 近似PF=0.48 / 平均MFE=4.95 / 平均MAE=10.27
- 代表例: 20260517_010500, 20260514_160500, 20260514_080500, 20260513_163400, 20260513_120500
- 主な観測ブロック理由: confidence_below_min=30件, no_trade_candidate=14件, watch_conditions_not_met=1件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 6件
- 観測タイプ: setup_watch_learning=6件
- 状態: observing=6件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 100.0%
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
- 記録あり: 43件
- primary_state: confirmed_down=17件, early_down=10件, confirmed_up=8件, early_up=6件, near_major_support=1件
- flags: short_into_major_support=36件, long_into_major_resistance=32件, support_to_resistance_flip=25件, support_to_resistance_retest_confirmed=25件, trend_flip_confirmed_down=17件, major_support_rejection=15件, major_resistance_rejection=14件, resistance_to_support_flip=14件
- trend_state: confirmed_down=17件, early_down=10件, confirmed_up=8件, early_up=6件
- 下方向反転系: 27件 / 勝率=66.7% / wrong_rate=37.0%
- 下方向反転系 平均MFE24h=8.59 / 平均MAE24h=5.36
- 代表例: 20260518_130500, 20260518_000500, 20260517_140501, 20260517_110500, 20260517_050500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 43件
- 主なブロック理由: phase1_inactive=43件, setup_not_ready=43件, execution_shadow_too_low=22件, wait_pressure_too_high=20件, no_trade_flags_present=2件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 43件
- opportunity_gate=pass: 20件
- paper_positions 記録: 20件
- 紙ポジション状態: closed=20件
- 紙ポジション終了状態: missed_opportunity=11件, sl_hit=8件, tp2_hit=1件
- 紙実行候補タイプ: market_map_opportunity=14件, setup_watch_learning=6件
- opportunity_type 別 closed:
  - market_map_opportunity: 14件 / 勝率=7.1% / 平均R=0.56 / 簡易PF=2.56
  - setup_watch_learning: 6件 / 勝率=0.0% / 平均R=0.32 / 簡易PF=1.95
- missed_opportunity: 11件
- missed代表例: 20260518_130500, 20260518_000500, 20260517_140501
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 4/4件

### risk_flags 有効性比較
- failed_breakout_up_reversal: negative_rate=90.0% (n=10)
- long_flush_exhaustion: negative_rate=90.0% (n=10)
- lower_liquidity_close: negative_rate=83.3% (n=12)
- short_cover_risk: negative_rate=83.3% (n=12)
- trend_flip_confirmed_down: negative_rate=82.4% (n=17)
- sweep_incomplete: negative_rate=81.8% (n=33)
- major_support_rejection: negative_rate=80.0% (n=15)
- orderbook_bid_heavy: negative_rate=80.0% (n=10)
- resistance_to_support_retest_confirmed: negative_rate=78.6% (n=14)
- resistance_to_support_flip: negative_rate=78.6% (n=14)
- long_into_major_resistance: negative_rate=75.0% (n=32)
- short_into_major_support: negative_rate=72.2% (n=36)
- support_to_resistance_flip: negative_rate=72.0% (n=25)
- support_to_resistance_retest_confirmed: negative_rate=72.0% (n=25)
- major_resistance_rejection: negative_rate=71.4% (n=14)
- upper_liquidity_close: negative_rate=68.2% (n=22)
- bid_wall_close: negative_rate=60.0% (n=10)
- trend_flip_early_down: negative_rate=60.0% (n=10)
