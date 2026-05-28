# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 43 件です。近似PF は 0.86、全体勝率は 41.9% でした。
- 事後評価では「待つ判断に使えた」が最も多く、28 件でした。
- 平均の役立ち度は 3.75 / 5 でした。
- 根拠整合の入力率は 74.4%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「SL が狭すぎるケースが多い」です。
- Phase 1 判定では ready=2 件、phase1_active=true=2 件です。
- 判定: Phase 1 の本有効確認を進めてよい (phase1_active=true の実データが出ているため、正式指標の観測を優先する)

## 2. 今回の対象
- 集計期間: 2026-05-18 22:05 〜 2026-05-24 19:05
- 総観測件数: 43
- データ品質の内訳: ok=43
- 近似PF: 0.86

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 2
- `phase1_active=true` 件数: 2
- 判定: Phase 1 の本有効確認を進めてよい
- 補足: phase1_active=true の実データが出ているため、正式指標の観測を優先する
- TP1 到達率: 50.0%
- `tp1_hit_first=false` 率: 50.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 100.0%
- ready阻害理由: confidence_below_min=30件, near_entry_zone_waiting_trigger=5件, entry_zone_not_reached=4件, inside_entry_zone_with_trigger=2件
- confidence_below_min 代表例: 20260522_140500(invalid/RISKY_ENTRY, dir=45, exec=35, wait=48, MFE24h=23.21, MAE24h=0.00, outcome=win) / 20260522_060500(invalid/RISKY_ENTRY, dir=61, exec=29, wait=42, MFE24h=17.65, MAE24h=0.72, outcome=win)
- 直近の観測対象:
  - 2026-05-24 06:05 / 20260523_210500 / setup=ready / phase1_active=True / outcome=loss
  - 2026-05-23 23:05 / 20260523_140500 / setup=ready / phase1_active=True / outcome=win

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 28件
- 見送り判断に使えた: 5件
- 通知が早すぎた: 2件
- 入る判断に使えた: 1件
- 平均の役立ち度: 3.75 / 5
- 値動きの主因の入力率: 83.7%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 74.4% / 整合率: 100.0%
- SL評価: SL は妥当=19件, SL が広すぎた=2件, SL が狭すぎた=15件
- TP評価: TP が遠すぎた=11件, TP が近すぎた=4件, TP は妥当=21件
- 4時間足評価: 一部弱い=26件, 妥当=10件
- 1時間足評価: 一部弱い=27件, 妥当=5件, 弱い=4件
- 15分足評価: 弱い=9件, 妥当=16件, 一部弱い=11件
### 改善アクション
- 分類: 入口条件を調整=29件, 対応なし=1件, 観測継続=5件, リスク設計を調整=1件
- 重要度: 中=25件, 低=4件, 高=7件
- 高優先の代表例:
  - 20260522_070500: 入口条件を調整 / 15分足の発火条件を「主要レジスタンス直下の上方向バイアス」では抑制し、方向表示も中立寄りに補正する。
  - 20260522_060500: 入口条件を調整 / 15分足の発火条件を見直し、短期ロング示唆と下方向バイアスが衝突した場合は通知を遅延して再判定する。
  - 20260522_010500: 入口条件を調整 / 15分足で再失速確定（高値切り下げ＋出来高/CVD追随）を満たすまで通知を遅らせ、即時逆行を避ける。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=354 / backlog=71 / AI済み=283 / human_override=0
- 今回の同期: created=8 / reused=0 / request_failed=0 / daily_cap=8
- 最終AI評価: 2026-05-24T18:37:12.436767Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. SL が狭すぎるケースが多い
   理由: sl_eval=too_tight が 15/36 件 (41.7%)
   主に触る場所: src/analysis/rr.py
2. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 7 件あります
   主に触る場所: tools/log_feedback.py
3. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 3/4 件 (75.0%)
   主に触る場所: config.py, src/analysis/position_risk.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 4件
- 主な通知理由: bias_changed=3件, confidence_jump=3件, attention_gap_crossed=1件
- 代表例: 20260523_190500(bias_changed,confidence_jump, exec=33, wait=43) / 20260521_010500(attention_gap_crossed,attention_score_crossed, exec=32, wait=61) / 20260519_190500(bias_changed,confidence_jump, exec=25, wait=48)
- 現行watch再計算: 20260523_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260521_010500=>watch/entry_zone_not_reached/rr=1.30 / 20260519_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=45.2%, 平均MFE=5.77, 平均MAE=6.02 (n=31)
- transition: 勝率=33.3%, 平均MFE=4.68, 平均MAE=7.32 (n=12) / データ不足 12/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=41.9%, 平均MFE=5.47, 平均MAE=6.38 (n=43)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=50.0%, 平均MFE=6.22, 平均MAE=4.73 (n=4) / データ不足 4/30
- RISKY_ENTRY: 勝率=60.0%, 平均MFE=7.69, 平均MAE=4.55 (n=10) / データ不足 10/30
- SWEEP_WAIT: 勝率=40.0%, 平均MFE=4.88, 平均MAE=6.95 (n=15) / データ不足 15/30
- NO_TRADE_CANDIDATE: 勝率=28.6%, 平均MFE=4.29, 平均MAE=7.55 (n=14) / データ不足 14/30

### bias別件数・勝率
- long: 勝率=35.7% (n=14) / データ不足 14/30
- short: 勝率=44.8% (n=29) / データ不足 29/30

### bias別 direction 正誤
- long: correct=3, wrong=8, unclear=3 / wrong_rate=57.1% (n=14)
- short: correct=13, wrong=10, unclear=6 / wrong_rate=34.5% (n=29)

### 成績指標
- 全体勝率: 41.9%
- 平均MFE(signal_based): 5.47
- 平均MAE(signal_based): 6.38
- 平均MFE(entry_ready_based): 9.66
- 平均MAE(entry_ready_based): 2.27
- TP1先行率: 41.9%

### 通知品質
- A: 通知して良かった = 18件
- B: 通知したが微妙 = 25件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- lower_liquidity_close: wrong_rate=66.7% (wrong=6/9)
- ask_wall_close: wrong_rate=66.7% (wrong=4/6)
- trend_flip_early_up: wrong_rate=60.0% (wrong=3/5)
- major_support_rejection: wrong_rate=60.0% (wrong=3/5)
- trend_flip_confirmed_up: wrong_rate=50.0% (wrong=4/8)
- failed_breakout_down_reversal: wrong_rate=50.0% (wrong=3/6)
- trend_flip_early_down: wrong_rate=43.8% (wrong=7/16)
- resistance_to_support_flip: wrong_rate=42.9% (wrong=6/14)
- resistance_to_support_retest_confirmed: wrong_rate=42.9% (wrong=6/14)
- orderbook_bid_heavy: wrong_rate=42.9% (wrong=6/14)
- orderbook_ask_heavy: wrong_rate=42.9% (wrong=3/7)
- support_to_resistance_flip: wrong_rate=42.3% (wrong=11/26)
- support_to_resistance_retest_confirmed: wrong_rate=42.3% (wrong=11/26)
- long_into_major_resistance: wrong_rate=41.7% (wrong=15/36)
- short_into_major_support: wrong_rate=41.7% (wrong=15/36)
- short_cover_risk: wrong_rate=41.7% (wrong=5/12)
- sweep_incomplete: wrong_rate=40.0% (wrong=12/30)
- bid_wall_close: wrong_rate=40.0% (wrong=6/15)
- upper_liquidity_close: wrong_rate=33.3% (wrong=8/24)
- major_resistance_rejection: wrong_rate=33.3% (wrong=5/15)
- trend_flip_confirmed_down: wrong_rate=33.3% (wrong=4/12)
- long_flush_exhaustion: wrong_rate=30.0% (wrong=3/10)

### 直近12時間速報
- 対象件数: 11件
- direction_execution_conflict: 7件
- direction_execution_conflict の主な理由: confidence_below_min=6件, near_entry_zone_waiting_trigger=1件
- direction_execution_conflict の主な risk_flags: upper_liquidity_close=7件, long_into_major_resistance=7件, short_into_major_support=7件
- rr_sweep_recheck_wait: 1件
- attention_rr_sweep_recheck_wait: 1件
- suppress_reason の内訳: confidence_below_short_min=6件, no_material_change=2件, attention_rr_sweep_recheck_wait=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 0件

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
- phase1_observation_gate=pass: 10件
- phase1_observation_gate=blocked: 33件
- 観測タイプ: setup_watch_learning=10件
- 観測候補全体: 10件 / 勝率=30.0% / TP1先行=30.0% / 近似PF=0.66 / 平均MFE=4.34 / 平均MAE=6.54
- setup_watch_learning: 10件 / 勝率=30.0% / TP1先行=30.0% / 近似PF=0.66 / 平均MFE=4.34 / 平均MAE=6.54
- 代表例: 20260523_200500, 20260523_190500, 20260523_040500, 20260522_010500, 20260521_010500
- 主な観測ブロック理由: confidence_below_min=30件, no_trade_candidate=14件, setup_not_observable=2件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 10件
- 観測タイプ: setup_watch_learning=10件
- 状態: observing=10件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 30.0%
- 代表例: 20260523_200500, 20260523_190500, 20260523_040500, 20260522_010500, 20260521_010500
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
- primary_state: early_down=16件, confirmed_down=12件, confirmed_up=8件, early_up=5件, near_major_resistance=2件
- flags: long_into_major_resistance=36件, short_into_major_support=36件, support_to_resistance_flip=26件, support_to_resistance_retest_confirmed=26件, trend_flip_early_down=16件, major_resistance_rejection=15件, resistance_to_support_flip=14件, resistance_to_support_retest_confirmed=14件
- trend_state: early_down=16件, confirmed_down=12件, confirmed_up=8件, early_up=5件
- 下方向反転系: 28件 / 勝率=42.9% / wrong_rate=39.3%
- 下方向反転系 平均MFE24h=5.91 / 平均MAE24h=5.34
- 代表例: 20260524_080500, 20260524_000500, 20260523_200500, 20260523_190500, 20260523_150500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 43件
- 主なブロック理由: phase1_inactive=41件, setup_not_ready=41件, no_trade_flags_present=38件, wait_pressure_too_high=21件, execution_shadow_too_low=18件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 43件
- opportunity_gate=pass: 19件
- paper_positions 記録: 19件
- 紙ポジション状態: closed=19件
- 紙ポジション終了状態: sl_hit=12件, missed_opportunity=5件, tp2_hit=1件, timeout=1件
- 紙実行候補タイプ: setup_watch_learning=10件, market_map_opportunity=9件
- opportunity_type 別 closed:
  - market_map_opportunity: 9件 / 勝率=11.1% / 平均R=0.26 / 簡易PF=1.57
  - setup_watch_learning: 10件 / 勝率=0.0% / 平均R=-0.39 / 簡易PF=0.40
- missed_opportunity: 5件
- missed代表例: 20260522_180500, 20260521_140500, 20260521_010500
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 4/4件

### risk_flags 有効性比較
- bid_wall_close: negative_rate=86.7% (n=15)
- resistance_to_support_flip: negative_rate=85.7% (n=14)
- resistance_to_support_retest_confirmed: negative_rate=85.7% (n=14)
- short_cover_risk: negative_rate=83.3% (n=12)
- trend_flip_confirmed_down: negative_rate=83.3% (n=12)
- long_into_major_resistance: negative_rate=80.6% (n=36)
- major_resistance_rejection: negative_rate=80.0% (n=15)
- orderbook_bid_heavy: negative_rate=78.6% (n=14)
- sweep_incomplete: negative_rate=76.7% (n=30)
- short_into_major_support: negative_rate=75.0% (n=36)
- upper_liquidity_close: negative_rate=75.0% (n=24)
- support_to_resistance_flip: negative_rate=69.2% (n=26)
- support_to_resistance_retest_confirmed: negative_rate=69.2% (n=26)
- trend_flip_early_down: negative_rate=62.5% (n=16)
- long_flush_exhaustion: negative_rate=60.0% (n=10)
