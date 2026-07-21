# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 47 件です。近似PF は 0.73、全体勝率は 46.8% でした。
- 事後評価では「待つ判断に使えた」が最も多く、17 件でした。
- 平均の役立ち度は 3.65 / 5 でした。
- 根拠整合の入力率は 34.0%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-11 04:05 〜 2026-05-16 15:05
- 総観測件数: 47
- データ品質の内訳: ok=47
- 近似PF: 0.73

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=29件, entry_zone_not_reached=11件, near_entry_zone_waiting_trigger=4件, inside_entry_zone_with_trigger=3件
- confidence_below_min 代表例: 20260513_110500(watch/SWEEP_WAIT, dir=58, exec=18, wait=67, MFE24h=15.38, MAE24h=0.00, outcome=win) / 20260516_060500(watch/SWEEP_WAIT, dir=51, exec=18, wait=59, MFE24h=14.77, MAE24h=0.00, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 17件
- 見送り判断に使えた: 2件
- 価値が低かった: 1件
- 平均の役立ち度: 3.65 / 5
- 値動きの主因の入力率: 42.6%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 34.0% / 整合率: 100.0%
- SL評価: SL が狭すぎた=5件, SL は妥当=15件
- TP評価: TP は妥当=10件, TP が遠すぎた=9件, TP が近すぎた=1件
- 4時間足評価: 一部弱い=12件, 妥当=8件
- 1時間足評価: 一部弱い=16件, 弱い=3件, 妥当=1件
- 15分足評価: 妥当=6件, 弱い=10件, 一部弱い=4件
### 改善アクション
- 分類: 入口条件を調整=13件, 通知文面を調整=1件, 観測継続=2件, 出口設計を調整=4件
- 重要度: 中=14件, 高=6件
- 高優先の代表例:
  - 20260515_140500: 入口条件を調整 / 15分足で再ショート発火条件を厳格化し、主要サポート直上では通知を待機専用に固定する。
  - 20260513_163400: 入口条件を調整 / 15分足で79,202明確上抜け時はショート監視を即失効にする条件を追加する
  - 20260513_120500: 入口条件を調整 / 15分足で再エントリー帯未到達でも初動ブレイク追随を許可する分岐条件を追加する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=302 / backlog=75 / AI済み=227 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-05-16T18:36:08.322637Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 10/20 件 (50.0%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. TP が遠すぎるケースが多い
   理由: tp_eval=too_far が 9/20 件 (45.0%)
   主に触る場所: src/analysis/rr.py, src/trade/exit_manager.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 2 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 1件
- 主な通知理由: bias_changed=1件, confidence_jump=1件
- 代表例: 20260510_190500(bias_changed,confidence_jump, exec=34, wait=58)
- 現行watch再計算: 20260510_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=44.4%, 平均MFE=6.36, 平均MAE=7.23 (n=18) / データ不足 18/30
- transition: 勝率=53.8%, 平均MFE=5.21, 平均MAE=7.41 (n=26) / データ不足 26/30
- uptrend: 勝率=0.0%, 平均MFE=1.10, 平均MAE=7.87 (n=3) / データ不足 3/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=46.8%, 平均MFE=5.39, 平均MAE=7.37 (n=47)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=50.0%, 平均MFE=5.04, 平均MAE=5.36 (n=4) / データ不足 4/30
- RISKY_ENTRY: 勝率=42.9%, 平均MFE=4.79, 平均MAE=7.88 (n=14) / データ不足 14/30
- SWEEP_WAIT: 勝率=60.0%, 平均MFE=5.81, 平均MAE=7.67 (n=15) / データ不足 15/30
- NO_TRADE_CANDIDATE: 勝率=35.7%, 平均MFE=5.63, 平均MAE=7.12 (n=14) / データ不足 14/30

### bias別件数・勝率
- long: 勝率=33.3% (n=27) / データ不足 27/30
- short: 勝率=65.0% (n=20) / データ不足 20/30

### bias別 direction 正誤
- long: correct=10, wrong=12, unclear=5 / wrong_rate=44.4% (n=27)
- short: correct=10, wrong=9, unclear=1 / wrong_rate=45.0% (n=20)

### 成績指標
- 全体勝率: 46.8%
- 平均MFE(signal_based): 5.39
- 平均MAE(signal_based): 7.37
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 46.8%

### 通知品質
- A: 通知して良かった = 22件
- B: 通知したが微妙 = 25件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- failed_breakout_up_reversal: wrong_rate=62.5% (wrong=5/8)
- trend_flip_confirmed_down: wrong_rate=61.5% (wrong=8/13)
- trend_flip_confirmed_up: wrong_rate=57.1% (wrong=4/7)
- lower_liquidity_close: wrong_rate=52.2% (wrong=12/23)
- sweep_incomplete: wrong_rate=50.0% (wrong=17/34)
- orderbook_ask_heavy: wrong_rate=50.0% (wrong=6/12)
- long_flush_exhaustion: wrong_rate=50.0% (wrong=5/10)
- support_to_resistance_retest_confirmed: wrong_rate=47.4% (wrong=9/19)
- support_to_resistance_flip: wrong_rate=47.4% (wrong=9/19)
- major_support_rejection: wrong_rate=46.2% (wrong=6/13)
- ask_wall_close: wrong_rate=45.5% (wrong=5/11)
- short_cover_risk: wrong_rate=44.4% (wrong=4/9)
- bid_wall_close: wrong_rate=42.9% (wrong=3/7)
- cvd_bullish_divergence: wrong_rate=42.9% (wrong=3/7)
- short_into_major_support: wrong_rate=39.3% (wrong=11/28)
- long_into_major_resistance: wrong_rate=39.3% (wrong=11/28)
- orderbook_bid_heavy: wrong_rate=37.5% (wrong=3/8)
- upper_liquidity_close: wrong_rate=33.3% (wrong=5/15)
- resistance_to_support_retest_confirmed: wrong_rate=33.3% (wrong=4/12)
- resistance_to_support_flip: wrong_rate=33.3% (wrong=4/12)
- cvd_bearish_divergence: wrong_rate=33.3% (wrong=2/6)
- failed_breakout_down_reversal: wrong_rate=28.6% (wrong=2/7)
- major_resistance_rejection: wrong_rate=27.3% (wrong=3/11)
- trend_flip_early_up: wrong_rate=20.0% (wrong=1/5)
- trend_flip_early_down: wrong_rate=14.3% (wrong=1/7)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 2件
- direction_execution_conflict の主な理由: confidence_below_min=2件
- direction_execution_conflict の主な risk_flags: bid_wall_close=2件, sweep_incomplete=2件, upper_liquidity_close=2件
- rr_sweep_recheck_wait: 1件
- attention_rr_sweep_recheck_wait: 1件
- suppress_reason の内訳: confidence_below_short_min=7件, attention_rr_sweep_recheck_wait=1件, rr_sweep_recheck_wait=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 2件

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
- phase1_observation_gate=pass: 11件
- phase1_observation_gate=blocked: 36件
- 観測タイプ: setup_watch_learning=11件
- 観測候補全体: 11件 / 勝率=36.4% / TP1先行=36.4% / 近似PF=0.47 / 平均MFE=3.97 / 平均MAE=8.42
- setup_watch_learning: 11件 / 勝率=36.4% / TP1先行=36.4% / 近似PF=0.47 / 平均MFE=3.97 / 平均MAE=8.42
- 代表例: 20260514_160500, 20260514_080500, 20260513_163400, 20260513_120500, 20260513_100500
- 主な観測ブロック理由: confidence_below_min=29件, no_trade_candidate=14件, watch_conditions_not_met=1件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 11件
- 観測タイプ: setup_watch_learning=11件
- 状態: observing=11件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 63.6%
- 代表例: 20260514_160500, 20260514_080500, 20260513_163400, 20260513_120500, 20260513_100500
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
- 記録あり: 33件
- primary_state: confirmed_down=13件, confirmed_up=7件, early_down=7件, early_up=5件, near_major_resistance=1件
- flags: short_into_major_support=28件, long_into_major_resistance=28件, support_to_resistance_flip=19件, support_to_resistance_retest_confirmed=19件, major_support_rejection=13件, trend_flip_confirmed_down=13件, resistance_to_support_flip=12件, resistance_to_support_retest_confirmed=12件
- trend_state: confirmed_down=13件, confirmed_up=7件, early_down=7件, early_up=5件
- 下方向反転系: 20件 / 勝率=60.0% / wrong_rate=45.0%
- 下方向反転系 平均MFE24h=7.89 / 平均MAE24h=6.33
- 代表例: 20260516_060500, 20260515_230500, 20260515_140500, 20260515_100500, 20260515_060500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 47件
- 主なブロック理由: phase1_inactive=47件, setup_not_ready=47件, execution_shadow_too_low=27件, wait_pressure_too_high=25件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 47件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 1/1件

### risk_flags 有効性比較
- lower_liquidity_close: negative_rate=91.3% (n=23)
- long_flush_exhaustion: negative_rate=90.0% (n=10)
- sweep_incomplete: negative_rate=88.2% (n=34)
- trend_flip_confirmed_down: negative_rate=84.6% (n=13)
- major_support_rejection: negative_rate=84.6% (n=13)
- short_into_major_support: negative_rate=75.0% (n=28)
- long_into_major_resistance: negative_rate=75.0% (n=28)
- orderbook_ask_heavy: negative_rate=75.0% (n=12)
- resistance_to_support_retest_confirmed: negative_rate=75.0% (n=12)
- resistance_to_support_flip: negative_rate=75.0% (n=12)
- support_to_resistance_retest_confirmed: negative_rate=73.7% (n=19)
- support_to_resistance_flip: negative_rate=73.7% (n=19)
- upper_liquidity_close: negative_rate=73.3% (n=15)
- ask_wall_close: negative_rate=72.7% (n=11)
- major_resistance_rejection: negative_rate=72.7% (n=11)
