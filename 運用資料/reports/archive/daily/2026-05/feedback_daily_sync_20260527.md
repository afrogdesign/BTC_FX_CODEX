# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 44 件です。近似PF は 0.79、全体勝率は 40.9% でした。
- 事後評価では「待つ判断に使えた」が最も多く、27 件でした。
- 平均の役立ち度は 3.69 / 5 でした。
- 根拠整合の入力率は 70.5%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「SL が狭すぎるケースが多い」です。
- Phase 1 判定では ready=2 件、phase1_active=true=2 件です。
- 判定: Phase 1 の本有効確認を進めてよい (phase1_active=true の実データが出ているため、正式指標の観測を優先する)

## 2. 今回の対象
- 集計期間: 2026-05-20 04:05 〜 2026-05-26 02:05
- 総観測件数: 44
- データ品質の内訳: ok=44
- 近似PF: 0.79

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 2
- `phase1_active=true` 件数: 2
- 判定: Phase 1 の本有効確認を進めてよい
- 補足: phase1_active=true の実データが出ているため、正式指標の観測を優先する
- TP1 到達率: 50.0%
- `tp1_hit_first=false` 率: 50.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 100.0%
- ready阻害理由: confidence_below_min=31件, near_entry_zone_waiting_trigger=7件, entry_zone_not_reached=3件, inside_entry_zone_with_trigger=1件
- confidence_below_min 代表例: 20260522_140500(invalid/RISKY_ENTRY, dir=45, exec=35, wait=48, MFE24h=23.21, MAE24h=0.00, outcome=win) / 20260522_060500(invalid/RISKY_ENTRY, dir=61, exec=29, wait=42, MFE24h=17.65, MAE24h=0.72, outcome=win)
- 直近の観測対象:
  - 2026-05-24 06:05 / 20260523_210500 / setup=ready / phase1_active=True / outcome=loss
  - 2026-05-23 23:05 / 20260523_140500 / setup=ready / phase1_active=True / outcome=win

## 4. AI事後評価サマリー
- 待つ判断に使えた: 27件
- 見送り判断に使えた: 6件
- 価値が低かった: 1件
- 入る判断に使えた: 1件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.69 / 5
- レビュー source: ai=36件
- 値動きの主因の入力率: 81.8%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 70.5% / 整合率: 100.0%
- SL評価: SL が狭すぎた=16件, SL は妥当=18件, SL が広すぎた=2件
- TP評価: TP が遠すぎた=13件, TP は妥当=18件, TP が近すぎた=5件
- 4時間足評価: 弱い=1件, 一部弱い=29件, 妥当=6件
- 1時間足評価: 一部弱い=25件, 妥当=7件, 弱い=4件
- 15分足評価: 一部弱い=9件, 妥当=15件, 弱い=12件
### 改善アクション
- 分類: 入口条件を調整=27件, 観測継続=5件, 通知文面を調整=2件, 対応なし=1件, リスク設計を調整=1件
- 重要度: 中=23件, 高=10件, 低=3件
- 高優先の代表例:
  - 20260524_130500: 入口条件を調整 / 15分足でレジスタンス再否定の成立時に限定して、wait固定を解除する発火条件を追加する。
  - 20260524_000500: 入口条件を調整 / 15分足は主要S/R同居の臨界帯では発火禁止を強め、流動性掃除後の再テスト確認を必須化する。
  - 20260523_210500: 通知文面を調整 / 「ENTRY_OK/執行可」と「実弾不可・待機」を同時表示しない文面に統一し、待機専用通知として明確化する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=363 / backlog=72 / AI済み=291 / human_override=0
- 今回の同期: created=8 / reused=0 / request_failed=0 / daily_cap=8
- 最終AI評価: 2026-05-25T18:37:03.344761Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. SL が狭すぎるケースが多い
   理由: sl_eval=too_tight が 16/36 件 (44.4%)
   主に触る場所: src/analysis/rr.py
2. TP が遠すぎるケースが多い
   理由: tp_eval=too_far が 13/36 件 (36.1%)
   主に触る場所: src/analysis/rr.py, src/trade/exit_manager.py
3. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 3/4 件 (75.0%)
   主に触る場所: config.py, src/analysis/position_risk.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 3件
- 主な通知理由: bias_changed=2件, confidence_jump=2件, attention_gap_crossed=1件
- 代表例: 20260523_190500(bias_changed,confidence_jump, exec=33, wait=43) / 20260521_010500(attention_gap_crossed,attention_score_crossed, exec=32, wait=61) / 20260519_190500(bias_changed,confidence_jump, exec=25, wait=48)
- 現行watch再計算: 20260523_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260521_010500=>watch/entry_zone_not_reached/rr=1.30 / 20260519_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=45.9%, 平均MFE=5.53, 平均MAE=6.48 (n=37)
- transition: 勝率=14.3%, 平均MFE=5.52, 平均MAE=9.52 (n=7) / データ不足 7/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=40.9%, 平均MFE=5.52, 平均MAE=6.96 (n=44)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=50.0%, 平均MFE=6.22, 平均MAE=4.73 (n=4) / データ不足 4/30
- RISKY_ENTRY: 勝率=55.6%, 平均MFE=8.36, 平均MAE=4.94 (n=9) / データ不足 9/30
- SWEEP_WAIT: 勝率=35.7%, 平均MFE=4.70, 平均MAE=7.94 (n=14) / データ不足 14/30
- NO_TRADE_CANDIDATE: 勝率=35.3%, 平均MFE=4.54, 平均MAE=7.76 (n=17) / データ不足 17/30

### bias別件数・勝率
- long: 勝率=33.3% (n=15) / データ不足 15/30
- short: 勝率=44.8% (n=29) / データ不足 29/30

### bias別 direction 正誤
- long: correct=4, wrong=8, unclear=3 / wrong_rate=53.3% (n=15)
- short: correct=10, wrong=15, unclear=4 / wrong_rate=51.7% (n=29)

### 成績指標
- 全体勝率: 40.9%
- 平均MFE(signal_based): 5.52
- 平均MAE(signal_based): 6.96
- 平均MFE(entry_ready_based): 9.66
- 平均MAE(entry_ready_based): 2.27
- TP1先行率: 40.9%

### 通知品質
- A: 通知して良かった = 18件
- B: 通知したが微妙 = 26件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- failed_breakout_down_reversal: wrong_rate=80.0% (wrong=4/5)
- major_support_rejection: wrong_rate=66.7% (wrong=4/6)
- trend_flip_confirmed_down: wrong_rate=61.5% (wrong=8/13)
- lower_liquidity_close: wrong_rate=60.0% (wrong=6/10)
- cvd_bearish_divergence: wrong_rate=60.0% (wrong=3/5)
- ask_wall_close: wrong_rate=57.1% (wrong=4/7)
- short_into_major_support: wrong_rate=54.3% (wrong=19/35)
- upper_liquidity_close: wrong_rate=54.2% (wrong=13/24)
- bid_wall_close: wrong_rate=52.9% (wrong=9/17)
- support_to_resistance_flip: wrong_rate=51.9% (wrong=14/27)
- support_to_resistance_retest_confirmed: wrong_rate=51.9% (wrong=14/27)
- long_into_major_resistance: wrong_rate=51.4% (wrong=19/37)
- major_resistance_rejection: wrong_rate=50.0% (wrong=7/14)
- short_cover_risk: wrong_rate=50.0% (wrong=6/12)
- resistance_to_support_retest_confirmed: wrong_rate=50.0% (wrong=6/12)
- resistance_to_support_flip: wrong_rate=50.0% (wrong=6/12)
- sweep_incomplete: wrong_rate=48.3% (wrong=14/29)
- trend_flip_early_down: wrong_rate=46.7% (wrong=7/15)
- trend_flip_confirmed_up: wrong_rate=44.4% (wrong=4/9)
- orderbook_bid_heavy: wrong_rate=42.9% (wrong=6/14)
- orderbook_ask_heavy: wrong_rate=37.5% (wrong=3/8)
- long_flush_exhaustion: wrong_rate=33.3% (wrong=4/12)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 2件
- direction_execution_conflict の主な理由: inside_entry_zone_with_trigger=1件, near_entry_zone_waiting_trigger=1件
- direction_execution_conflict の主な risk_flags: sweep_incomplete=2件, upper_liquidity_close=2件, short_into_major_support=2件
- suppress_reason の内訳: confidence_below_short_min=4件, no_material_change=2件, watch_sweep_recheck_wait=2件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 2件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 44
- 本有効件数: 2
- 参考ログ件数: 42
- 平均 risk_percent_applied: 0.50
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 50.00
- 平均 position_size_usd: 3000.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 100.0%
- 平均 timeout_hours: 12.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 10件
- phase1_observation_gate=blocked: 34件
- 観測タイプ: setup_watch_learning=10件
- 観測候補全体: 10件 / 勝率=20.0% / TP1先行=20.0% / 近似PF=0.72 / 平均MFE=4.78 / 平均MAE=6.66
- setup_watch_learning: 10件 / 勝率=20.0% / TP1先行=20.0% / 近似PF=0.72 / 平均MFE=4.78 / 平均MAE=6.66
- 代表例: 20260525_120500, 20260525_040500, 20260525_020500, 20260523_200500, 20260523_190500
- 主な観測ブロック理由: confidence_below_min=31件, no_trade_candidate=17件, setup_not_observable=2件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 10件
- 観測タイプ: setup_watch_learning=10件
- 状態: observing=10件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 20.0%
- 代表例: 20260525_120500, 20260525_040500, 20260525_020500, 20260523_200500, 20260523_190500
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
- 記録あり: 44件
- primary_state: early_down=15件, confirmed_down=13件, confirmed_up=9件, early_up=4件, near_major_resistance=3件
- flags: long_into_major_resistance=37件, short_into_major_support=35件, support_to_resistance_flip=27件, support_to_resistance_retest_confirmed=27件, trend_flip_early_down=15件, major_resistance_rejection=14件, trend_flip_confirmed_down=13件, resistance_to_support_flip=12件
- trend_state: early_down=15件, confirmed_down=13件, confirmed_up=9件, early_up=4件
- 下方向反転系: 28件 / 勝率=42.9% / wrong_rate=53.6%
- 下方向反転系 平均MFE24h=5.95 / 平均MAE24h=5.83
- 代表例: 20260525_120500, 20260525_040500, 20260525_020500, 20260524_180500, 20260524_150500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 44件
- 主なブロック理由: phase1_inactive=42件, setup_not_ready=42件, no_trade_flags_present=37件, wait_pressure_too_high=25件, execution_shadow_too_low=18件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 44件
- opportunity_gate=pass: 14件
- paper_positions 記録: 14件
- 紙ポジション状態: closed=14件
- 紙ポジション終了状態: sl_hit=9件, missed_opportunity=4件, tp2_hit=1件
- 紙実行候補タイプ: setup_watch_learning=9件, market_map_opportunity=5件
- opportunity_type 別 closed:
  - market_map_opportunity: 5件 / 勝率=20.0% / 平均R=1.06 / 簡易PF=6.30
  - setup_watch_learning: 9件 / 勝率=0.0% / 平均R=-0.74 / 簡易PF=0.16
- missed_opportunity: 4件
- missed代表例: 20260524_150500, 20260522_180500, 20260521_140500
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 5/5件

### risk_flags 有効性比較
- bid_wall_close: negative_rate=94.1% (n=17)
- trend_flip_confirmed_down: negative_rate=92.3% (n=13)
- lower_liquidity_close: negative_rate=90.0% (n=10)
- upper_liquidity_close: negative_rate=87.5% (n=24)
- long_into_major_resistance: negative_rate=86.5% (n=37)
- major_resistance_rejection: negative_rate=85.7% (n=14)
- short_cover_risk: negative_rate=83.3% (n=12)
- resistance_to_support_retest_confirmed: negative_rate=83.3% (n=12)
- resistance_to_support_flip: negative_rate=83.3% (n=12)
- sweep_incomplete: negative_rate=82.8% (n=29)
- short_into_major_support: negative_rate=80.0% (n=35)
- orderbook_bid_heavy: negative_rate=78.6% (n=14)
- support_to_resistance_flip: negative_rate=77.8% (n=27)
- support_to_resistance_retest_confirmed: negative_rate=77.8% (n=27)
- trend_flip_early_down: negative_rate=66.7% (n=15)
- long_flush_exhaustion: negative_rate=66.7% (n=12)
