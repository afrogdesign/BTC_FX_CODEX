# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 37 件です。近似PF は 10.18、全体勝率は 97.3% でした。
- 事後評価では「待つ判断に使えた」が最も多く、31 件でした。
- 平均の役立ち度は 3.97 / 5 でした。
- 根拠整合の入力率は 94.6%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-31 17:05 〜 2026-06-06 07:05
- 総観測件数: 37
- データ品質の内訳: ok=37
- 近似PF: 10.18

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: entry_zone_not_reached=24件, near_entry_zone_waiting_trigger=8件, inside_entry_zone_with_trigger=3件, confidence_below_min=2件
- confidence_below_min 代表例: 20260531_130500(watch/SWEEP_WAIT, dir=51, exec=18, wait=67, MFE24h=25.02, MAE24h=3.24, outcome=win) / 20260531_150500(watch/SWEEP_WAIT, dir=65, exec=33, wait=51, MFE24h=19.08, MAE24h=5.22, outcome=win)

## 4. AI事後評価サマリー
- 待つ判断に使えた: 31件
- 見送り判断に使えた: 4件
- 平均の役立ち度: 3.97 / 5
- レビュー source: ai=35件
- 値動きの主因の入力率: 94.6%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 94.6% / 整合率: 100.0%
- SL評価: SL は妥当=30件, SL が狭すぎた=5件
- TP評価: TP が遠すぎた=30件, TP は妥当=4件, TP が近すぎた=1件
- 4時間足評価: 妥当=35件
- 1時間足評価: 一部弱い=35件
- 15分足評価: 弱い=32件, 妥当=2件, 一部弱い=1件
### 改善アクション
- 分類: 出口設計を調整=30件, リスク設計を調整=2件, 入口条件を調整=3件
- 重要度: 中=35件
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=433 / backlog=46 / AI済み=387 / human_override=0
- 今回の同期: created=8 / reused=0 / request_failed=0 / daily_cap=8
- 最終AI評価: 2026-06-06T18:41:31.057865Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 32/35 件 (91.4%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. TP が遠すぎるケースが多い
   理由: tp_eval=too_far が 30/35 件 (85.7%)
   主に触る場所: src/analysis/rr.py, src/trade/exit_manager.py
3. NO_TRADE_CANDIDATE が強すぎる
   理由: skip_too_strict が 11/22 件 (50.0%)
   主に触る場所: config.py, src/analysis/position_risk.py

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- downtrend: 勝率=100.0%, 平均MFE=13.08, 平均MAE=0.85 (n=30)
- range: 勝率=100.0%, 平均MFE=17.56, 平均MAE=4.04 (n=4) / データ不足 4/30
- transition: 勝率=66.7%, 平均MFE=19.31, 平均MAE=3.16 (n=3) / データ不足 3/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=97.3%, 平均MFE=14.07, 平均MAE=1.38 (n=37)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=13.89, 平均MAE=1.63 (n=5) / データ不足 5/30
- RISKY_ENTRY: 勝率=100.0%, 平均MFE=13.07, 平均MAE=3.84 (n=2) / データ不足 2/30
- SWEEP_WAIT: 勝率=100.0%, 平均MFE=13.97, 平均MAE=1.75 (n=8) / データ不足 8/30
- NO_TRADE_CANDIDATE: 勝率=95.5%, 平均MFE=14.24, 平均MAE=0.97 (n=22) / データ不足 22/30

### bias別件数・勝率
- short: 勝率=97.3% (n=37)

### bias別 direction 正誤
- short: correct=29, wrong=3, unclear=5 / wrong_rate=8.1% (n=37)

### 成績指標
- 全体勝率: 97.3%
- 平均MFE(signal_based): 14.07
- 平均MAE(signal_based): 1.38
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 97.3%

### 通知品質
- A: 通知して良かった = 36件
- B: 通知したが微妙 = 1件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- major_support_rejection: wrong_rate=28.6% (wrong=2/7)
- trend_flip_confirmed_down: wrong_rate=14.3% (wrong=3/21)
- major_resistance_rejection: wrong_rate=12.5% (wrong=1/8)
- support_to_resistance_retest_confirmed: wrong_rate=11.1% (wrong=3/27)
- support_to_resistance_flip: wrong_rate=11.1% (wrong=3/27)
- upper_liquidity_close: wrong_rate=10.0% (wrong=3/30)
- sweep_incomplete: wrong_rate=9.1% (wrong=2/22)
- long_flush_exhaustion: wrong_rate=9.1% (wrong=1/11)
- orderbook_bid_heavy: wrong_rate=8.0% (wrong=2/25)
- bid_wall_close: wrong_rate=8.0% (wrong=2/25)
- short_into_major_support: wrong_rate=7.1% (wrong=2/28)
- long_into_major_resistance: wrong_rate=5.0% (wrong=1/20)
- short_cover_risk: wrong_rate=0.0% (wrong=0/14)
- trend_flip_early_down: wrong_rate=0.0% (wrong=0/7)
- cvd_bearish_divergence: wrong_rate=0.0% (wrong=0/6)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 3件
- direction_execution_conflict の主な理由: near_entry_zone_waiting_trigger=2件, entry_zone_not_reached=1件
- direction_execution_conflict の主な risk_flags: sweep_incomplete=3件, upper_liquidity_close=3件, short_into_major_support=3件
- rr_sweep_recheck_wait: 1件
- attention_rr_sweep_recheck_wait: 1件
- suppress_reason の内訳: no_material_change=4件, watch_sweep_recheck_wait=4件, confidence_below_short_min=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 0件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 37
- 本有効件数: 0
- 参考ログ件数: 37
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 10件
- phase1_observation_gate=blocked: 27件
- 観測タイプ: setup_watch_learning=10件
- 観測候補全体: 10件 / 勝率=100.0% / TP1先行=100.0% / 近似PF=5.86 / 平均MFE=12.10 / 平均MAE=2.06
- setup_watch_learning: 10件 / 勝率=100.0% / TP1先行=100.0% / 近似PF=5.86 / 平均MFE=12.10 / 平均MAE=2.06
- 代表例: 20260605_140500, 20260605_120500, 20260605_080500, 20260605_030500, 20260603_160500
- 主な観測ブロック理由: no_trade_candidate=22件, watch_conditions_not_met=3件, confidence_below_min=2件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 10件
- 観測タイプ: setup_watch_learning=10件
- 状態: observing=10件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 80.0%
- 代表例: 20260605_140500, 20260605_120500, 20260605_080500, 20260605_030500, 20260603_160500
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
- 記録あり: 37件
- primary_state: confirmed_down=21件, early_down=7件, early_up=4件, near_major_support=4件, near_major_resistance=1件
- flags: short_into_major_support=28件, support_to_resistance_flip=27件, support_to_resistance_retest_confirmed=27件, trend_flip_confirmed_down=21件, long_into_major_resistance=20件, major_resistance_rejection=8件, major_support_rejection=7件, trend_flip_early_down=7件
- trend_state: confirmed_down=21件, early_down=7件, early_up=4件
- 下方向反転系: 28件 / 勝率=96.4% / wrong_rate=10.7%
- 下方向反転系 平均MFE24h=13.78 / 平均MAE24h=1.67
- 代表例: 20260605_220500, 20260605_140500, 20260605_120500, 20260605_080500, 20260605_030500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 37件
- 主なブロック理由: phase1_inactive=37件, setup_not_ready=37件, no_trade_flags_present=30件, execution_shadow_too_low=18件, wait_pressure_too_high=9件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 37件
- opportunity_gate=pass: 11件
- quality guard blocked: 9件 / 理由=require_execution_for_high_wait=9件
- hard_quality_blocked: 9件 / 理由=require_execution_for_high_wait=9件
- soft_quality_risk: 0件 / 理由=なし
- market_map opportunity before/after guard: 24件 -> 1件
- market_map opportunity before/after hard guard: 24件 -> 1件
- paper_positions 記録: 11件
- 紙ポジション状態: closed=11件
- 紙ポジション終了状態: missed_opportunity=7件, tp2_hit=2件, sl_hit=1件, timeout=1件
- quality guard 該当 closed sl_hit: 0件
- 紙実行候補タイプ: setup_watch_learning=10件, market_map_opportunity=1件
- opportunity_type 別 closed:
  - market_map_opportunity: 1件 / 勝率=0.0% / 平均R=0.00 / 簡易PF=0.00
  - setup_watch_learning: 10件 / 勝率=20.0% / 平均R=1.35 / 簡易PF=38.83
- missed_opportunity: 7件
- missed代表例: 20260605_140500, 20260605_120500, 20260605_080500
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 1/1件

### risk_flags 有効性比較
- short_cover_risk: negative_rate=78.6% (n=14)
- orderbook_bid_heavy: negative_rate=64.0% (n=25)
- short_into_major_support: negative_rate=60.7% (n=28)
- trend_flip_confirmed_down: negative_rate=57.1% (n=21)
- upper_liquidity_close: negative_rate=56.7% (n=30)
- bid_wall_close: negative_rate=56.0% (n=25)
- long_into_major_resistance: negative_rate=55.0% (n=20)
- sweep_incomplete: negative_rate=54.5% (n=22)
- support_to_resistance_retest_confirmed: negative_rate=48.1% (n=27)
- support_to_resistance_flip: negative_rate=48.1% (n=27)
- long_flush_exhaustion: negative_rate=18.2% (n=11)
