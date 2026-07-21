# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 36 件です。近似PF は 3.69、全体勝率は 75.0% でした。
- 事後評価では「待つ判断に使えた」が最も多く、27 件でした。
- 平均の役立ち度は 3.76 / 5 でした。
- 根拠整合の入力率は 91.7%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-28 14:05 〜 2026-06-03 10:05
- 総観測件数: 36
- データ品質の内訳: ok=36
- 近似PF: 3.69

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: entry_zone_not_reached=21件, confidence_below_min=9件, near_entry_zone_waiting_trigger=3件, inside_entry_zone_with_trigger=3件
- confidence_below_min 代表例: 20260531_130500(watch/SWEEP_WAIT, dir=51, exec=18, wait=67, MFE24h=25.02, MAE24h=3.24, outcome=win) / 20260531_150500(watch/SWEEP_WAIT, dir=65, exec=33, wait=51, MFE24h=19.08, MAE24h=5.22, outcome=win)

## 4. AI事後評価サマリー
- 待つ判断に使えた: 27件
- 見送り判断に使えた: 6件
- 平均の役立ち度: 3.76 / 5
- レビュー source: ai=33件
- 値動きの主因の入力率: 91.7%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 91.7% / 整合率: 100.0%
- SL評価: SL は妥当=21件, SL が狭すぎた=12件
- TP評価: TP が遠すぎた=15件, TP は妥当=16件, TP が近すぎた=2件
- 4時間足評価: 妥当=20件, 一部弱い=13件
- 1時間足評価: 一部弱い=33件
- 15分足評価: 弱い=20件, 妥当=10件, 一部弱い=3件
### 改善アクション
- 分類: 出口設計を調整=11件, リスク設計を調整=2件, 入口条件を調整=15件, 通知文面を調整=1件, 観測継続=4件
- 重要度: 中=28件, 高=4件, 低=1件
- 高優先の代表例:
  - 20260530_140500: 通知文面を調整 / 「下方向バイアス」の主表示を弱め、実行不可・見送りを件名と冒頭に固定して誤読を防ぐ。
  - 20260529_050500: 入口条件を調整 / 15分足で上側流動性回収後の再失速確認（73,655付近の再拒否と出来高条件）を満たすまで通知を発火しない。
  - 20260529_030500: 入口条件を調整 / 15分足で主要サポート近接時は逆張り反発優先の待機条件を追加し、戻り売り発火をさらに遅らせる。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=415 / backlog=52 / AI済み=363 / human_override=0
- 今回の同期: created=8 / reused=0 / request_failed=0 / daily_cap=8
- 最終AI評価: 2026-06-03T18:41:39.585122Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 20/33 件 (60.6%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. TP が遠すぎるケースが多い
   理由: tp_eval=too_far が 15/33 件 (45.5%)
   主に触る場所: src/analysis/rr.py, src/trade/exit_manager.py
3. SL が狭すぎるケースが多い
   理由: sl_eval=too_tight が 12/33 件 (36.4%)
   主に触る場所: src/analysis/rr.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 1件
- 主な通知理由: bias_changed=1件
- 代表例: 20260530_010500(bias_changed, exec=18, wait=51)
- 現行watch再計算: 20260530_010500=>watch/entry_zone_not_reached/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- downtrend: 勝率=83.3%, 平均MFE=12.64, 平均MAE=2.01 (n=18) / データ不足 18/30
- range: 勝率=66.7%, 平均MFE=7.73, 平均MAE=4.21 (n=15) / データ不足 15/30
- transition: 勝率=66.7%, 平均MFE=19.31, 平均MAE=3.16 (n=3) / データ不足 3/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=75.0%, 平均MFE=11.15, 平均MAE=3.02 (n=36)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=13.40, 平均MAE=2.07 (n=4) / データ不足 4/30
- RISKY_ENTRY: 勝率=42.9%, 平均MFE=6.44, 平均MAE=4.68 (n=7) / データ不足 7/30
- SWEEP_WAIT: 勝率=80.0%, 平均MFE=14.25, 平均MAE=2.86 (n=5) / データ不足 5/30
- NO_TRADE_CANDIDATE: 勝率=80.0%, 平均MFE=11.58, 平均MAE=2.68 (n=20) / データ不足 20/30

### bias別件数・勝率
- long: 勝率=100.0% (n=1) / データ不足 1/30
- short: 勝率=74.3% (n=35)

### bias別 direction 正誤
- long: correct=1, wrong=0, unclear=0 / wrong_rate=0.0% (n=1)
- short: correct=19, wrong=11, unclear=5 / wrong_rate=31.4% (n=35)

### 成績指標
- 全体勝率: 75.0%
- 平均MFE(signal_based): 11.15
- 平均MAE(signal_based): 3.02
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 77.1%

### 通知品質
- A: 通知して良かった = 27件
- B: 通知したが微妙 = 9件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- major_support_rejection: wrong_rate=57.1% (wrong=4/7)
- resistance_to_support_retest_confirmed: wrong_rate=40.0% (wrong=2/5)
- resistance_to_support_flip: wrong_rate=40.0% (wrong=2/5)
- trend_flip_confirmed_down: wrong_rate=37.5% (wrong=6/16)
- support_to_resistance_retest_confirmed: wrong_rate=34.8% (wrong=8/23)
- support_to_resistance_flip: wrong_rate=34.8% (wrong=8/23)
- bid_wall_close: wrong_rate=31.8% (wrong=7/22)
- orderbook_bid_heavy: wrong_rate=30.0% (wrong=6/20)
- long_into_major_resistance: wrong_rate=30.0% (wrong=6/20)
- upper_liquidity_close: wrong_rate=29.6% (wrong=8/27)
- short_into_major_support: wrong_rate=29.6% (wrong=8/27)
- long_flush_exhaustion: wrong_rate=27.3% (wrong=3/11)
- trend_flip_early_down: wrong_rate=27.3% (wrong=3/11)
- sweep_incomplete: wrong_rate=25.0% (wrong=6/24)
- cvd_bullish_divergence: wrong_rate=20.0% (wrong=1/5)
- major_resistance_rejection: wrong_rate=18.2% (wrong=2/11)
- failed_breakout_down_reversal: wrong_rate=16.7% (wrong=1/6)
- short_cover_risk: wrong_rate=9.1% (wrong=1/11)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 0件
- suppress_reason の内訳: watch_sweep_recheck_wait=7件, no_material_change=4件
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
- phase1_observation_gate=pass: 8件
- phase1_observation_gate=blocked: 28件
- 観測タイプ: setup_watch_learning=8件
- 観測候補全体: 8件 / 勝率=75.0% / TP1先行=85.7% / 近似PF=3.58 / 平均MFE=10.88 / 平均MAE=3.04
- setup_watch_learning: 8件 / 勝率=75.0% / TP1先行=85.7% / 近似PF=3.58 / 平均MFE=10.88 / 平均MAE=3.04
- 代表例: 20260602_130500, 20260602_060500, 20260601_020500, 20260531_100500, 20260531_080501
- 主な観測ブロック理由: no_trade_candidate=20件, confidence_below_min=9件, watch_conditions_not_met=2件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 8件
- 観測タイプ: setup_watch_learning=8件
- 状態: observing=8件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 62.5%
- 代表例: 20260602_130500, 20260602_060500, 20260601_020500, 20260531_100500, 20260531_080501
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
- primary_state: confirmed_down=16件, early_down=11件, near_major_support=3件, near_major_resistance=2件, confirmed_up=2件
- flags: short_into_major_support=27件, support_to_resistance_flip=23件, support_to_resistance_retest_confirmed=23件, long_into_major_resistance=20件, trend_flip_confirmed_down=16件, major_resistance_rejection=11件, trend_flip_early_down=11件, major_support_rejection=7件
- trend_state: confirmed_down=16件, early_down=11件, confirmed_up=2件, early_up=1件
- 下方向反転系: 27件 / 勝率=70.4% / wrong_rate=33.3%
- 下方向反転系 平均MFE24h=10.47 / 平均MAE24h=3.20
- 代表例: 20260603_010500, 20260602_190500, 20260602_130500, 20260602_060500, 20260601_190500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 36件
- 主なブロック理由: phase1_inactive=36件, setup_not_ready=36件, no_trade_flags_present=29件, execution_shadow_too_low=16件, wait_pressure_too_high=13件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 36件
- opportunity_gate=pass: 9件
- quality guard blocked: 12件 / 理由=require_execution_for_high_wait=11件, require_execution_for_high_wait+suppress_long_high_wait+suppress_trend_flip_up_strong=1件
- hard_quality_blocked: 12件 / 理由=require_execution_for_high_wait=11件, require_execution_for_high_wait+suppress_long_high_wait+suppress_trend_flip_up_strong=1件
- soft_quality_risk: 0件 / 理由=なし
- market_map opportunity before/after guard: 23件 -> 1件
- market_map opportunity before/after hard guard: 23件 -> 1件
- paper_positions 記録: 9件
- 紙ポジション状態: closed=9件
- 紙ポジション終了状態: missed_opportunity=3件, tp2_hit=2件, sl_hit=2件, timeout=2件
- quality guard 該当 closed sl_hit: 0件
- 紙実行候補タイプ: setup_watch_learning=8件, market_map_opportunity=1件
- opportunity_type 別 closed:
  - market_map_opportunity: 1件 / 勝率=0.0% / 平均R=0.00 / 簡易PF=0.00
  - setup_watch_learning: 8件 / 勝率=25.0% / 平均R=0.85 / 簡易PF=4.59
- missed_opportunity: 3件
- missed代表例: 20260602_130500, 20260602_060500, 20260528_070500
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 2/2件

### risk_flags 有効性比較
- orderbook_bid_heavy: negative_rate=70.0% (n=20)
- short_cover_risk: negative_rate=63.6% (n=11)
- major_resistance_rejection: negative_rate=63.6% (n=11)
- trend_flip_early_down: negative_rate=63.6% (n=11)
- upper_liquidity_close: negative_rate=63.0% (n=27)
- long_into_major_resistance: negative_rate=60.0% (n=20)
- short_into_major_support: negative_rate=59.3% (n=27)
- bid_wall_close: negative_rate=59.1% (n=22)
- support_to_resistance_retest_confirmed: negative_rate=56.5% (n=23)
- support_to_resistance_flip: negative_rate=56.5% (n=23)
- trend_flip_confirmed_down: negative_rate=56.2% (n=16)
- sweep_incomplete: negative_rate=54.2% (n=24)
- long_flush_exhaustion: negative_rate=36.4% (n=11)
