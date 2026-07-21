# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 40 件です。近似PF は 1.04、全体勝率は 55.0% でした。
- 事後評価では「待つ判断に使えた」が最も多く、25 件でした。
- 平均の役立ち度は 3.73 / 5 でした。
- 根拠整合の入力率は 70.0%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「SL が狭すぎるケースが多い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-17 07:05 〜 2026-05-22 23:05
- 総観測件数: 40
- データ品質の内訳: ok=40
- 近似PF: 1.04

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=30件, entry_zone_not_reached=6件, inside_entry_zone_with_trigger=2件, near_entry_zone_waiting_trigger=2件
- confidence_below_min 代表例: 20260522_140500(invalid/RISKY_ENTRY, dir=45, exec=35, wait=48, MFE24h=23.21, MAE24h=0.00, outcome=win) / 20260522_060500(invalid/RISKY_ENTRY, dir=61, exec=29, wait=42, MFE24h=17.65, MAE24h=0.72, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 25件
- 見送り判断に使えた: 2件
- 通知が早すぎた: 1件
- 通知が遅すぎた: 1件
- 価値が低かった: 1件
- 平均の役立ち度: 3.73 / 5
- 値動きの主因の入力率: 75.0%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 70.0% / 整合率: 100.0%
- SL評価: SL が狭すぎた=15件, SL は妥当=15件
- TP評価: TP は妥当=21件, TP が遠すぎた=7件, TP が近すぎた=2件
- 4時間足評価: 一部弱い=22件, 妥当=8件
- 1時間足評価: 妥当=6件, 一部弱い=22件, 弱い=2件
- 15分足評価: 妥当=13件, 弱い=9件, 一部弱い=8件
### 改善アクション
- 分類: 入口条件を調整=23件, 観測継続=5件, リスク設計を調整=1件, 対応なし=1件
- 重要度: 中=20件, 低=4件, 高=6件
- 高優先の代表例:
  - 20260520_090500: 入口条件を調整 / 15分足で再失速確定（高値切り下げ＋出来高条件）を満たすまで通知を待機寄りに固定する。
  - 20260519_190500: 入口条件を調整 / 15分足で主要サポート直上のときはshort方向スコア上限を抑え、上側スイープ確認前は中立寄り表示に補正する。
  - 20260519_020500: 入口条件を調整 / 15分足で上側流動性回収後の再拒否確定を発火必須にし、臨界帯では通知を待機専用に固定する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=342 / backlog=75 / AI済み=267 / human_override=0
- 今回の同期: created=8 / reused=0 / request_failed=0 / daily_cap=8
- 最終AI評価: 2026-05-22T18:37:17.954530Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. SL が狭すぎるケースが多い
   理由: sl_eval=too_tight が 15/30 件 (50.0%)
   主に触る場所: src/analysis/rr.py
2. 反発示唆の過大評価
   理由: countertrend_long_cluster の wrong が 6/10 件 (60.0%)
   主に触る場所: src/analysis/confidence.py, src/analysis/position_risk.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 2 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 3件
- 主な通知理由: bias_changed=2件, confidence_jump=2件, attention_gap_crossed=1件
- 代表例: 20260521_010500(attention_gap_crossed,attention_score_crossed, exec=32, wait=61) / 20260519_190500(bias_changed,confidence_jump, exec=25, wait=48) / 20260519_120500(agreement_changed,bias_changed, exec=25, wait=48)
- 現行watch再計算: 20260521_010500=>watch/entry_zone_not_reached/rr=1.30 / 20260519_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260519_120500=>watch/entry_zone_not_reached/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=64.3%, 平均MFE=6.36, 平均MAE=4.92 (n=28) / データ不足 28/30
- transition: 勝率=33.3%, 平均MFE=4.68, 平均MAE=7.32 (n=12) / データ不足 12/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=55.0%, 平均MFE=5.86, 平均MAE=5.64 (n=40)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=8.47, 平均MAE=4.90 (n=2) / データ不足 2/30
- RISKY_ENTRY: 勝率=62.5%, 平均MFE=8.32, 平均MAE=4.04 (n=8) / データ不足 8/30
- SWEEP_WAIT: 勝率=52.9%, 平均MFE=5.13, 平均MAE=6.53 (n=17) / データ不足 17/30
- NO_TRADE_CANDIDATE: 勝率=46.2%, 平均MFE=4.90, 平均MAE=5.58 (n=13) / データ不足 13/30

### bias別件数・勝率
- long: 勝率=41.7% (n=12) / データ不足 12/30
- short: 勝率=60.7% (n=28) / データ不足 28/30

### bias別 direction 正誤
- long: correct=3, wrong=6, unclear=3 / wrong_rate=50.0% (n=12)
- short: correct=15, wrong=7, unclear=6 / wrong_rate=25.0% (n=28)

### 成績指標
- 全体勝率: 55.0%
- 平均MFE(signal_based): 5.86
- 平均MAE(signal_based): 5.64
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 55.0%

### 通知品質
- A: 通知して良かった = 22件
- B: 通知したが微妙 = 18件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- failed_breakout_up_reversal: wrong_rate=66.7% (wrong=4/6)
- major_support_rejection: wrong_rate=57.1% (wrong=4/7)
- lower_liquidity_close: wrong_rate=50.0% (wrong=4/8)
- ask_wall_close: wrong_rate=50.0% (wrong=3/6)
- orderbook_bid_heavy: wrong_rate=45.5% (wrong=5/11)
- trend_flip_confirmed_up: wrong_rate=42.9% (wrong=3/7)
- orderbook_ask_heavy: wrong_rate=42.9% (wrong=3/7)
- trend_flip_confirmed_down: wrong_rate=41.7% (wrong=5/12)
- short_into_major_support: wrong_rate=38.2% (wrong=13/34)
- sweep_incomplete: wrong_rate=34.4% (wrong=11/32)
- long_into_major_resistance: wrong_rate=34.4% (wrong=11/32)
- support_to_resistance_flip: wrong_rate=33.3% (wrong=8/24)
- support_to_resistance_retest_confirmed: wrong_rate=33.3% (wrong=8/24)
- resistance_to_support_flip: wrong_rate=33.3% (wrong=4/12)
- resistance_to_support_retest_confirmed: wrong_rate=33.3% (wrong=4/12)
- short_cover_risk: wrong_rate=33.3% (wrong=4/12)
- failed_breakout_down_reversal: wrong_rate=28.6% (wrong=2/7)
- major_resistance_rejection: wrong_rate=26.7% (wrong=4/15)
- long_flush_exhaustion: wrong_rate=25.0% (wrong=2/8)
- upper_liquidity_close: wrong_rate=20.8% (wrong=5/24)
- trend_flip_early_down: wrong_rate=20.0% (wrong=3/15)
- bid_wall_close: wrong_rate=18.2% (wrong=2/11)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 2件
- direction_execution_conflict の主な理由: confidence_below_min=2件
- direction_execution_conflict の主な risk_flags: bid_wall_close=2件, orderbook_bid_heavy=2件, sweep_incomplete=2件
- suppress_reason の内訳: confidence_below_short_min=5件, bias_wait=2件, no_material_change=2件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 1件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 40
- 本有効件数: 0
- 参考ログ件数: 40
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 8件
- phase1_observation_gate=blocked: 32件
- 観測タイプ: setup_watch_learning=8件
- 観測候補全体: 8件 / 勝率=50.0% / TP1先行=50.0% / 近似PF=1.04 / 平均MFE=5.12 / 平均MAE=4.90
- setup_watch_learning: 8件 / 勝率=50.0% / TP1先行=50.0% / 近似PF=1.04 / 平均MFE=5.12 / 平均MAE=4.90
- 代表例: 20260522_010500, 20260521_010500, 20260520_070500, 20260519_190500, 20260519_170500
- 主な観測ブロック理由: confidence_below_min=30件, no_trade_candidate=13件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 8件
- 観測タイプ: setup_watch_learning=8件
- 状態: observing=8件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 50.0%
- 代表例: 20260522_010500, 20260521_010500, 20260520_070500, 20260519_190500, 20260519_170500
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
- 記録あり: 40件
- primary_state: early_down=15件, confirmed_down=12件, confirmed_up=7件, early_up=4件, near_major_resistance=1件
- flags: short_into_major_support=34件, long_into_major_resistance=32件, support_to_resistance_flip=24件, support_to_resistance_retest_confirmed=24件, trend_flip_early_down=15件, major_resistance_rejection=15件, resistance_to_support_flip=12件, resistance_to_support_retest_confirmed=12件
- trend_state: early_down=15件, confirmed_down=12件, confirmed_up=7件, early_up=4件
- 下方向反転系: 27件 / 勝率=55.6% / wrong_rate=29.6%
- 下方向反転系 平均MFE24h=7.29 / 平均MAE24h=3.87
- 代表例: 20260522_140500, 20260522_070500, 20260522_060500, 20260522_010500, 20260521_200500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 40件
- 主なブロック理由: phase1_inactive=40件, setup_not_ready=40件, no_trade_flags_present=30件, wait_pressure_too_high=18件, execution_shadow_too_low=16件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 40件
- opportunity_gate=pass: 17件
- paper_positions 記録: 17件
- 紙ポジション状態: closed=17件
- 紙ポジション終了状態: sl_hit=9件, missed_opportunity=7件, timeout=1件
- 紙実行候補タイプ: market_map_opportunity=9件, setup_watch_learning=8件
- opportunity_type 別 closed:
  - market_map_opportunity: 9件 / 勝率=0.0% / 平均R=0.13 / 簡易PF=1.30
  - setup_watch_learning: 8件 / 勝率=0.0% / 平均R=0.05 / 簡易PF=1.11
- missed_opportunity: 7件
- missed代表例: 20260521_140500, 20260521_010500, 20260520_070500
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 2/2件

### risk_flags 有効性比較
- resistance_to_support_flip: negative_rate=91.7% (n=12)
- resistance_to_support_retest_confirmed: negative_rate=91.7% (n=12)
- trend_flip_confirmed_down: negative_rate=83.3% (n=12)
- short_cover_risk: negative_rate=83.3% (n=12)
- long_into_major_resistance: negative_rate=75.0% (n=32)
- major_resistance_rejection: negative_rate=73.3% (n=15)
- orderbook_bid_heavy: negative_rate=72.7% (n=11)
- sweep_incomplete: negative_rate=71.9% (n=32)
- short_into_major_support: negative_rate=70.6% (n=34)
- bid_wall_close: negative_rate=63.6% (n=11)
- upper_liquidity_close: negative_rate=62.5% (n=24)
- support_to_resistance_flip: negative_rate=62.5% (n=24)
- support_to_resistance_retest_confirmed: negative_rate=62.5% (n=24)
- trend_flip_early_down: negative_rate=53.3% (n=15)
