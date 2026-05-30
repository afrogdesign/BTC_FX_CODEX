# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 43 件です。近似PF は 0.89、全体勝率は 46.5% でした。
- 事後評価では「待つ判断に使えた」が最も多く、26 件でした。
- 平均の役立ち度は 3.63 / 5 でした。
- 根拠整合の入力率は 76.7%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「SL が狭すぎるケースが多い」です。
- Phase 1 判定では ready=2 件、phase1_active=true=2 件です。
- 判定: Phase 1 の本有効確認を進めてよい (phase1_active=true の実データが出ているため、正式指標の観測を優先する)

## 2. 今回の対象
- 集計期間: 2026-05-21 05:05 〜 2026-05-27 00:05
- 総観測件数: 43
- データ品質の内訳: ok=43
- 近似PF: 0.89

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 2
- `phase1_active=true` 件数: 2
- 判定: Phase 1 の本有効確認を進めてよい
- 補足: phase1_active=true の実データが出ているため、正式指標の観測を優先する
- TP1 到達率: 50.0%
- `tp1_hit_first=false` 率: 50.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 100.0%
- ready阻害理由: confidence_below_min=32件, near_entry_zone_waiting_trigger=6件, inside_entry_zone_with_trigger=2件, entry_zone_not_reached=1件
- confidence_below_min 代表例: 20260522_140500(invalid/RISKY_ENTRY, dir=45, exec=35, wait=48, MFE24h=23.21, MAE24h=0.00, outcome=win) / 20260522_060500(invalid/RISKY_ENTRY, dir=61, exec=29, wait=42, MFE24h=17.65, MAE24h=0.72, outcome=win)
- 直近の観測対象:
  - 2026-05-24 06:05 / 20260523_210500 / setup=ready / phase1_active=True / outcome=loss
  - 2026-05-23 23:05 / 20260523_140500 / setup=ready / phase1_active=True / outcome=win

## 4. AI事後評価サマリー
- 待つ判断に使えた: 26件
- 見送り判断に使えた: 8件
- 通知が早すぎた: 2件
- 価値が低かった: 1件
- 入る判断に使えた: 1件
- 平均の役立ち度: 3.63 / 5
- レビュー source: ai=38件
- 値動きの主因の入力率: 88.4%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 76.7% / 整合率: 100.0%
- SL評価: SL は妥当=17件, SL が狭すぎた=19件, SL が広すぎた=2件
- TP評価: TP は妥当=19件, TP が遠すぎた=14件, TP が近すぎた=5件
- 4時間足評価: 一部弱い=30件, 弱い=2件, 妥当=6件
- 1時間足評価: 一部弱い=29件, 妥当=7件, 弱い=2件
- 15分足評価: 弱い=15件, 妥当=14件, 一部弱い=9件
### 改善アクション
- 分類: 入口条件を調整=29件, 出口設計を調整=1件, 観測継続=4件, 通知文面を調整=2件, 対応なし=1件, リスク設計を調整=1件
- 重要度: 中=26件, 高=10件, 低=2件
- 高優先の代表例:
  - 20260525_020500: 入口条件を調整 / 15分足で上側流動性回収後の再失速確定（戻り高値切り下げ＋出来高条件）まで発火を遅らせる。
  - 20260524_130500: 入口条件を調整 / 15分足でレジスタンス再否定の成立時に限定して、wait固定を解除する発火条件を追加する。
  - 20260524_000500: 入口条件を調整 / 15分足は主要S/R同居の臨界帯では発火禁止を強め、流動性掃除後の再テスト確認を必須化する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=368 / backlog=69 / AI済み=299 / human_override=0
- 今回の同期: created=8 / reused=0 / request_failed=0 / daily_cap=8
- 最終AI評価: 2026-05-26T18:37:33.700394Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. SL が狭すぎるケースが多い
   理由: sl_eval=too_tight が 19/38 件 (50.0%)
   主に触る場所: src/analysis/rr.py
2. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 15/38 件 (39.5%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
3. TP が遠すぎるケースが多い
   理由: tp_eval=too_far が 14/38 件 (36.8%)
   主に触る場所: src/analysis/rr.py, src/trade/exit_manager.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 3件
- 主な通知理由: attention_bias_changed=1件, bias_changed=1件, confidence_jump=1件
- 代表例: 20260523_190500(bias_changed,confidence_jump, exec=33, wait=43) / 20260521_010500(attention_gap_crossed,attention_score_crossed, exec=32, wait=61) / 20260526_110500(attention_bias_changed, exec=15, wait=64)
- 現行watch再計算: 20260523_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260521_010500=>watch/entry_zone_not_reached/rr=1.30 / 20260526_110500=>ready/inside_entry_zone_with_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=47.1%, 平均MFE=5.92, 平均MAE=6.72 (n=34)
- transition: 勝率=37.5%, 平均MFE=7.96, 平均MAE=9.70 (n=8) / データ不足 8/30
- volatile: 勝率=100.0%, 平均MFE=6.31, 平均MAE=0.23 (n=1) / データ不足 1/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=46.5%, 平均MFE=6.31, 平均MAE=7.12 (n=43)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=33.3%, 平均MFE=6.50, 平均MAE=5.08 (n=3) / データ不足 3/30
- RISKY_ENTRY: 勝率=55.6%, 平均MFE=8.36, 平均MAE=4.94 (n=9) / データ不足 9/30
- SWEEP_WAIT: 勝率=50.0%, 平均MFE=6.09, 平均MAE=7.79 (n=16) / データ不足 16/30
- NO_TRADE_CANDIDATE: 勝率=40.0%, 平均MFE=5.27, 平均MAE=8.12 (n=15) / データ不足 15/30

### bias別件数・勝率
- long: 勝率=33.3% (n=15) / データ不足 15/30
- short: 勝率=53.6% (n=28) / データ不足 28/30

### bias別 direction 正誤
- long: correct=4, wrong=9, unclear=2 / wrong_rate=60.0% (n=15)
- short: correct=11, wrong=13, unclear=4 / wrong_rate=46.4% (n=28)

### 成績指標
- 全体勝率: 46.5%
- 平均MFE(signal_based): 6.31
- 平均MAE(signal_based): 7.12
- 平均MFE(entry_ready_based): 9.66
- 平均MAE(entry_ready_based): 2.27
- TP1先行率: 46.5%

### 通知品質
- A: 通知して良かった = 20件
- B: 通知したが微妙 = 23件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- lower_liquidity_close: wrong_rate=63.6% (wrong=7/11)
- major_support_rejection: wrong_rate=60.0% (wrong=3/5)
- resistance_to_support_retest_confirmed: wrong_rate=58.3% (wrong=7/12)
- resistance_to_support_flip: wrong_rate=58.3% (wrong=7/12)
- failed_breakout_down_reversal: wrong_rate=57.1% (wrong=4/7)
- ask_wall_close: wrong_rate=57.1% (wrong=4/7)
- trend_flip_confirmed_up: wrong_rate=55.6% (wrong=5/9)
- trend_flip_confirmed_down: wrong_rate=54.5% (wrong=6/11)
- short_into_major_support: wrong_rate=50.0% (wrong=18/36)
- bid_wall_close: wrong_rate=50.0% (wrong=8/16)
- long_into_major_resistance: wrong_rate=48.6% (wrong=17/35)
- support_to_resistance_retest_confirmed: wrong_rate=48.0% (wrong=12/25)
- support_to_resistance_flip: wrong_rate=48.0% (wrong=12/25)
- upper_liquidity_close: wrong_rate=47.8% (wrong=11/23)
- sweep_incomplete: wrong_rate=46.4% (wrong=13/28)
- short_cover_risk: wrong_rate=45.5% (wrong=5/11)
- trend_flip_early_down: wrong_rate=43.8% (wrong=7/16)
- orderbook_ask_heavy: wrong_rate=42.9% (wrong=3/7)
- major_resistance_rejection: wrong_rate=37.5% (wrong=6/16)
- orderbook_bid_heavy: wrong_rate=33.3% (wrong=4/12)
- long_flush_exhaustion: wrong_rate=28.6% (wrong=4/14)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 5件
- direction_execution_conflict の主な理由: confidence_below_min=2件, near_entry_zone_waiting_trigger=2件, entry_zone_not_reached=1件
- direction_execution_conflict の主な risk_flags: sweep_incomplete=5件, upper_liquidity_close=5件, support_to_resistance_retest_confirmed=5件
- rr_sweep_recheck_wait: 3件
- attention_rr_sweep_recheck_wait: 3件
- suppress_reason の内訳: attention_rr_sweep_recheck_wait=3件, rr_sweep_recheck_wait=3件, bias_wait=2件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 1件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 43
- 本有効件数: 2
- 参考ログ件数: 41
- 平均 risk_percent_applied: 0.50
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 50.00
- 平均 position_size_usd: 3000.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 100.0%
- 平均 timeout_hours: 12.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 8件
- phase1_observation_gate=blocked: 35件
- 観測タイプ: setup_watch_learning=8件
- 観測候補全体: 8件 / 勝率=12.5% / TP1先行=12.5% / 近似PF=0.71 / 平均MFE=5.12 / 平均MAE=7.17
- setup_watch_learning: 8件 / 勝率=12.5% / TP1先行=12.5% / 近似PF=0.71 / 平均MFE=5.12 / 平均MAE=7.17
- 代表例: 20260525_120500, 20260525_040500, 20260525_020500, 20260523_200500, 20260523_190500
- 主な観測ブロック理由: confidence_below_min=32件, no_trade_candidate=15件, setup_not_observable=2件, watch_conditions_not_met=1件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 8件
- 観測タイプ: setup_watch_learning=8件
- 状態: observing=8件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 12.5%
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
- 記録あり: 43件
- primary_state: early_down=16件, confirmed_down=11件, confirmed_up=9件, early_up=4件, near_major_resistance=3件
- flags: short_into_major_support=36件, long_into_major_resistance=35件, support_to_resistance_flip=25件, support_to_resistance_retest_confirmed=25件, major_resistance_rejection=16件, trend_flip_early_down=16件, resistance_to_support_flip=12件, resistance_to_support_retest_confirmed=12件
- trend_state: early_down=16件, confirmed_down=11件, confirmed_up=9件, early_up=4件
- 下方向反転系: 27件 / 勝率=51.9% / wrong_rate=48.1%
- 下方向反転系 平均MFE24h=7.21 / 平均MAE24h=5.79
- 代表例: 20260526_150500, 20260526_110500, 20260526_050500, 20260525_190500, 20260525_120500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 43件
- 主なブロック理由: phase1_inactive=41件, setup_not_ready=41件, no_trade_flags_present=36件, wait_pressure_too_high=25件, execution_shadow_too_low=19件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 43件
- opportunity_gate=pass: 14件
- paper_positions 記録: 14件
- 紙ポジション状態: closed=14件
- 紙ポジション終了状態: sl_hit=8件, missed_opportunity=5件, tp2_hit=1件
- 紙実行候補タイプ: setup_watch_learning=8件, market_map_opportunity=6件
- opportunity_type 別 closed:
  - market_map_opportunity: 6件 / 勝率=16.7% / 平均R=1.10 / 簡易PF=7.60
  - setup_watch_learning: 8件 / 勝率=0.0% / 平均R=-0.71 / 簡易PF=0.19
- missed_opportunity: 5件
- missed代表例: 20260525_190500, 20260524_150500, 20260522_180500
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 5/5件

### risk_flags 有効性比較
- bid_wall_close: negative_rate=93.8% (n=16)
- lower_liquidity_close: negative_rate=90.9% (n=11)
- trend_flip_confirmed_down: negative_rate=90.9% (n=11)
- major_resistance_rejection: negative_rate=87.5% (n=16)
- upper_liquidity_close: negative_rate=87.0% (n=23)
- long_into_major_resistance: negative_rate=85.7% (n=35)
- resistance_to_support_retest_confirmed: negative_rate=83.3% (n=12)
- resistance_to_support_flip: negative_rate=83.3% (n=12)
- sweep_incomplete: negative_rate=82.1% (n=28)
- short_cover_risk: negative_rate=81.8% (n=11)
- short_into_major_support: negative_rate=80.6% (n=36)
- support_to_resistance_retest_confirmed: negative_rate=76.0% (n=25)
- support_to_resistance_flip: negative_rate=76.0% (n=25)
- orderbook_bid_heavy: negative_rate=75.0% (n=12)
- long_flush_exhaustion: negative_rate=71.4% (n=14)
- trend_flip_early_down: negative_rate=68.8% (n=16)
