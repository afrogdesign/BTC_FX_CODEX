# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 36 件です。近似PF は 2.34、全体勝率は 69.4% でした。
- 事後評価では「待つ判断に使えた」が最も多く、25 件でした。
- 平均の役立ち度は 3.67 / 5 でした。
- 根拠整合の入力率は 91.7%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「SL が狭すぎるケースが多い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-27 07:05 〜 2026-06-01 18:05
- 総観測件数: 36
- データ品質の内訳: ok=36
- 近似PF: 2.34

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: entry_zone_not_reached=15件, confidence_below_min=15件, inside_entry_zone_with_trigger=3件, near_entry_zone_waiting_trigger=3件
- confidence_below_min 代表例: 20260531_130500(watch/SWEEP_WAIT, dir=51, exec=18, wait=67, MFE24h=25.02, MAE24h=3.24, outcome=win) / 20260531_150500(watch/SWEEP_WAIT, dir=65, exec=33, wait=51, MFE24h=19.08, MAE24h=5.22, outcome=win)

## 4. AI事後評価サマリー
- 待つ判断に使えた: 25件
- 見送り判断に使えた: 7件
- 通知が遅すぎた: 1件
- 平均の役立ち度: 3.67 / 5
- レビュー source: ai=33件
- 値動きの主因の入力率: 91.7%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 91.7% / 整合率: 100.0%
- SL評価: SL が狭すぎた=13件, SL は妥当=20件
- TP評価: TP は妥当=24件, TP が近すぎた=3件, TP が遠すぎた=6件
- 4時間足評価: 妥当=14件, 一部弱い=19件
- 1時間足評価: 一部弱い=30件, 妥当=3件
- 15分足評価: 妥当=14件, 弱い=13件, 一部弱い=6件
### 改善アクション
- 分類: リスク設計を調整=2件, 入口条件を調整=22件, 通知文面を調整=2件, 観測継続=7件
- 重要度: 中=24件, 高=7件, 低=2件
- 高優先の代表例:
  - 20260530_140500: 通知文面を調整 / 「下方向バイアス」の主表示を弱め、実行不可・見送りを件名と冒頭に固定して誤読を防ぐ。
  - 20260529_050500: 入口条件を調整 / 15分足で上側流動性回収後の再失速確認（73,655付近の再拒否と出来高条件）を満たすまで通知を発火しない。
  - 20260529_030500: 入口条件を調整 / 15分足で主要サポート近接時は逆張り反発優先の待機条件を追加し、戻り売り発火をさらに遅らせる。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=404 / backlog=57 / AI済み=347 / human_override=0
- 今回の同期: created=8 / reused=0 / request_failed=0 / daily_cap=8
- 最終AI評価: 2026-06-01T18:39:16.821876Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. SL が狭すぎるケースが多い
   理由: sl_eval=too_tight が 13/33 件 (39.4%)
   主に触る場所: src/analysis/rr.py
2. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 13/33 件 (39.4%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
3. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 4/4 件 (100.0%)
   主に触る場所: config.py, src/analysis/position_risk.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 1件
- 主な通知理由: bias_changed=1件
- 代表例: 20260530_010500(bias_changed, exec=18, wait=51)
- 現行watch再計算: 20260530_010500=>watch/entry_zone_not_reached/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- downtrend: 勝率=57.1%, 平均MFE=6.07, 平均MAE=4.19 (n=7) / データ不足 7/30
- range: 勝率=70.8%, 平均MFE=8.86, 平均MAE=4.15 (n=24) / データ不足 24/30
- transition: 勝率=80.0%, 平均MFE=15.11, 平均MAE=2.47 (n=5) / データ不足 5/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=69.4%, 平均MFE=9.19, 平均MAE=3.93 (n=36)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=11.93, 平均MAE=2.86 (n=4) / データ不足 4/30
- RISKY_ENTRY: 勝率=50.0%, 平均MFE=7.71, 平均MAE=4.91 (n=10) / データ不足 10/30
- SWEEP_WAIT: 勝率=87.5%, 平均MFE=12.16, 平均MAE=2.07 (n=8) / データ不足 8/30
- NO_TRADE_CANDIDATE: 勝率=64.3%, 平均MFE=7.76, 平均MAE=4.59 (n=14) / データ不足 14/30

### bias別件数・勝率
- long: 勝率=33.3% (n=3) / データ不足 3/30
- short: 勝率=72.7% (n=33)

### bias別 direction 正誤
- long: correct=1, wrong=1, unclear=1 / wrong_rate=33.3% (n=3)
- short: correct=15, wrong=12, unclear=6 / wrong_rate=36.4% (n=33)

### 成績指標
- 全体勝率: 69.4%
- 平均MFE(signal_based): 9.19
- 平均MAE(signal_based): 3.93
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 71.4%

### 通知品質
- A: 通知して良かった = 25件
- B: 通知したが微妙 = 11件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- failed_breakout_up_reversal: wrong_rate=60.0% (wrong=3/5)
- major_support_rejection: wrong_rate=55.6% (wrong=5/9)
- trend_flip_confirmed_down: wrong_rate=50.0% (wrong=7/14)
- bid_wall_close: wrong_rate=43.8% (wrong=7/16)
- resistance_to_support_retest_confirmed: wrong_rate=40.0% (wrong=2/5)
- resistance_to_support_flip: wrong_rate=40.0% (wrong=2/5)
- orderbook_bid_heavy: wrong_rate=38.9% (wrong=7/18)
- short_into_major_support: wrong_rate=38.5% (wrong=10/26)
- upper_liquidity_close: wrong_rate=36.0% (wrong=9/25)
- long_into_major_resistance: wrong_rate=35.0% (wrong=7/20)
- support_to_resistance_retest_confirmed: wrong_rate=34.6% (wrong=9/26)
- support_to_resistance_flip: wrong_rate=33.3% (wrong=9/27)
- long_flush_exhaustion: wrong_rate=33.3% (wrong=3/9)
- sweep_incomplete: wrong_rate=30.4% (wrong=7/23)
- short_cover_risk: wrong_rate=25.0% (wrong=2/8)
- major_resistance_rejection: wrong_rate=20.0% (wrong=2/10)
- cvd_bullish_divergence: wrong_rate=20.0% (wrong=1/5)
- failed_breakout_down_reversal: wrong_rate=20.0% (wrong=1/5)
- trend_flip_early_down: wrong_rate=17.6% (wrong=3/17)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 1件
- direction_execution_conflict の主な理由: entry_zone_not_reached=1件
- direction_execution_conflict の主な risk_flags: cvd_bullish_divergence=1件, long_flush_exhaustion=1件, orderbook_bid_heavy=1件
- suppress_reason の内訳: watch_sweep_recheck_wait=7件, no_material_change=4件, cooldown_active=1件
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
- 観測候補全体: 11件 / 勝率=81.8% / TP1先行=90.0% / 近似PF=3.76 / 平均MFE=11.13 / 平均MAE=2.96
- setup_watch_learning: 11件 / 勝率=81.8% / TP1先行=90.0% / 近似PF=3.76 / 平均MFE=11.13 / 平均MAE=2.96
- 代表例: 20260601_020500, 20260531_100500, 20260531_080501, 20260529_220500, 20260529_050500
- 主な観測ブロック理由: confidence_below_min=15件, no_trade_candidate=14件, watch_conditions_not_met=2件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 11件
- 観測タイプ: setup_watch_learning=11件
- 状態: observing=11件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 54.5%
- 代表例: 20260601_020500, 20260531_100500, 20260531_080501, 20260529_220500, 20260529_050500
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
- primary_state: early_down=17件, confirmed_down=14件, confirmed_up=3件, near_major_resistance=1件, active_support=1件
- flags: support_to_resistance_flip=27件, support_to_resistance_retest_confirmed=26件, short_into_major_support=26件, long_into_major_resistance=20件, trend_flip_early_down=17件, trend_flip_confirmed_down=14件, major_resistance_rejection=10件, major_support_rejection=9件
- trend_state: early_down=17件, confirmed_down=14件, confirmed_up=3件
- 下方向反転系: 31件 / 勝率=71.0% / wrong_rate=32.3%
- 下方向反転系 平均MFE24h=10.13 / 平均MAE24h=3.40
- 代表例: 20260601_090500, 20260601_060500, 20260601_020500, 20260531_170500, 20260531_150500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 36件
- 主なブロック理由: phase1_inactive=36件, setup_not_ready=36件, no_trade_flags_present=28件, wait_pressure_too_high=14件, execution_shadow_too_low=12件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 36件
- opportunity_gate=pass: 14件
- quality guard blocked: 11件 / 理由=require_execution_for_high_wait=9件, require_execution_for_high_wait+suppress_long_high_wait+suppress_trend_flip_up_strong=2件
- hard_quality_blocked: 11件 / 理由=require_execution_for_high_wait=9件, require_execution_for_high_wait+suppress_long_high_wait+suppress_trend_flip_up_strong=2件
- soft_quality_risk: 0件 / 理由=なし
- market_map opportunity before/after guard: 28件 -> 3件
- market_map opportunity before/after hard guard: 28件 -> 3件
- paper_positions 記録: 14件
- 紙ポジション状態: closed=14件
- 紙ポジション終了状態: missed_opportunity=5件, sl_hit=4件, tp2_hit=3件, timeout=2件
- quality guard 該当 closed sl_hit: 0件
- 紙実行候補タイプ: setup_watch_learning=11件, market_map_opportunity=3件
- opportunity_type 別 closed:
  - market_map_opportunity: 3件 / 勝率=0.0% / 平均R=0.87 / 簡易PF=0.00
  - setup_watch_learning: 11件 / 勝率=27.3% / 平均R=0.84 / 簡易PF=5.85
- missed_opportunity: 5件
- missed代表例: 20260528_070500, 20260528_040500, 20260528_010500
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 3/3件

### risk_flags 有効性比較
- trend_flip_confirmed_down: negative_rate=85.7% (n=14)
- orderbook_bid_heavy: negative_rate=77.8% (n=18)
- short_into_major_support: negative_rate=69.2% (n=26)
- bid_wall_close: negative_rate=68.8% (n=16)
- support_to_resistance_flip: negative_rate=66.7% (n=27)
- support_to_resistance_retest_confirmed: negative_rate=65.4% (n=26)
- long_into_major_resistance: negative_rate=65.0% (n=20)
- upper_liquidity_close: negative_rate=64.0% (n=25)
- major_resistance_rejection: negative_rate=60.0% (n=10)
- sweep_incomplete: negative_rate=56.5% (n=23)
- trend_flip_early_down: negative_rate=52.9% (n=17)
