# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 40 件です。近似PF は 1.13、全体勝率は 52.5% でした。
- 事後評価では「待つ判断に使えた」が最も多く、21 件でした。
- 平均の役立ち度は 3.53 / 5 でした。
- 根拠整合の入力率は 72.5%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=2 件、phase1_active=true=2 件です。
- 判定: Phase 1 の本有効確認を進めてよい (phase1_active=true の実データが出ているため、正式指標の観測を優先する)

## 2. 今回の対象
- 集計期間: 2026-05-22 05:05 〜 2026-05-28 01:05
- 総観測件数: 40
- データ品質の内訳: ok=40
- 近似PF: 1.13

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 2
- `phase1_active=true` 件数: 2
- 判定: Phase 1 の本有効確認を進めてよい
- 補足: phase1_active=true の実データが出ているため、正式指標の観測を優先する
- TP1 到達率: 50.0%
- `tp1_hit_first=false` 率: 50.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 100.0%
- ready阻害理由: confidence_below_min=28件, near_entry_zone_waiting_trigger=7件, inside_entry_zone_with_trigger=2件, entry_zone_not_reached=1件
- confidence_below_min 代表例: 20260522_140500(invalid/RISKY_ENTRY, dir=45, exec=35, wait=48, MFE24h=23.21, MAE24h=0.00, outcome=win) / 20260527_130500(invalid/NO_TRADE_CANDIDATE, dir=68, exec=11, wait=78, MFE24h=18.16, MAE24h=0.00, outcome=win)
- 直近の観測対象:
  - 2026-05-24 06:05 / 20260523_210500 / setup=ready / phase1_active=True / outcome=loss
  - 2026-05-23 23:05 / 20260523_140500 / setup=ready / phase1_active=True / outcome=win

## 4. AI事後評価サマリー
- 待つ判断に使えた: 21件
- 見送り判断に使えた: 8件
- 価値が低かった: 2件
- 通知が早すぎた: 2件
- 入る判断に使えた: 1件
- 平均の役立ち度: 3.53 / 5
- レビュー source: ai=34件
- 値動きの主因の入力率: 85.0%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 72.5% / 整合率: 100.0%
- SL評価: SL が広すぎた=3件, SL は妥当=18件, SL が狭すぎた=13件
- TP評価: TP は妥当=16件, TP が近すぎた=7件, TP が遠すぎた=11件
- 4時間足評価: 妥当=6件, 一部弱い=26件, 弱い=2件
- 1時間足評価: 一部弱い=26件, 妥当=6件, 弱い=2件
- 15分足評価: 弱い=14件, 妥当=10件, 一部弱い=10件
### 改善アクション
- 分類: 入口条件を調整=27件, 観測継続=3件, 出口設計を調整=1件, 通知文面を調整=2件, 対応なし=1件
- 重要度: 高=12件, 中=20件, 低=2件
- 高優先の代表例:
  - 20260526_150500: 入口条件を調整 / 15分足で支持帯直下の再ブレイク条件を追加し、NO_TRADE固定を緩めて段階的にショート許可する。
  - 20260525_190500: 入口条件を調整 / 15分足で上側流動性スイープ後の再失速をエントリー条件に追加し、WAIT解除を1段早める。
  - 20260525_020500: 入口条件を調整 / 15分足で上側流動性回収後の再失速確定（戻り高値切り下げ＋出来高条件）まで発火を遅らせる。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=374 / backlog=67 / AI済み=307 / human_override=0
- 今回の同期: created=8 / reused=0 / request_failed=0 / daily_cap=8
- 最終AI評価: 2026-05-27T18:37:18.008337Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 14/34 件 (41.2%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. SL が狭すぎるケースが多い
   理由: sl_eval=too_tight が 13/34 件 (38.2%)
   主に触る場所: src/analysis/rr.py
3. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 3/4 件 (75.0%)
   主に触る場所: config.py, src/analysis/position_risk.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 2件
- 主な通知理由: attention_bias_changed=1件, bias_changed=1件, confidence_jump=1件
- 代表例: 20260523_190500(bias_changed,confidence_jump, exec=33, wait=43) / 20260526_110500(attention_bias_changed, exec=15, wait=64)
- 現行watch再計算: 20260523_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260526_110500=>ready/inside_entry_zone_with_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=51.7%, 平均MFE=7.94, 平均MAE=6.94 (n=29) / データ不足 29/30
- transition: 勝率=50.0%, 平均MFE=8.14, 平均MAE=8.05 (n=10) / データ不足 10/30
- volatile: 勝率=100.0%, 平均MFE=6.31, 平均MAE=0.23 (n=1) / データ不足 1/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=52.5%, 平均MFE=7.95, 平均MAE=7.05 (n=40)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=50.0%, 平均MFE=11.31, 平均MAE=4.23 (n=4) / データ不足 4/30
- RISKY_ENTRY: 勝率=55.6%, 平均MFE=10.30, 平均MAE=4.97 (n=9) / データ不足 9/30
- SWEEP_WAIT: 勝率=50.0%, 平均MFE=7.01, 平均MAE=8.71 (n=12) / データ不足 12/30
- NO_TRADE_CANDIDATE: 勝率=53.3%, 平均MFE=6.39, 平均MAE=7.72 (n=15) / データ不足 15/30

### bias別件数・勝率
- long: 勝率=33.3% (n=12) / データ不足 12/30
- short: 勝率=60.7% (n=28) / データ不足 28/30

### bias別 direction 正誤
- long: correct=3, wrong=8, unclear=1 / wrong_rate=66.7% (n=12)
- short: correct=12, wrong=12, unclear=4 / wrong_rate=42.9% (n=28)

### 成績指標
- 全体勝率: 52.5%
- 平均MFE(signal_based): 7.95
- 平均MAE(signal_based): 7.05
- 平均MFE(entry_ready_based): 9.66
- 平均MAE(entry_ready_based): 2.27
- TP1先行率: 52.5%

### 通知品質
- A: 通知して良かった = 21件
- B: 通知したが微妙 = 19件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- trend_flip_confirmed_up: wrong_rate=83.3% (wrong=5/6)
- resistance_to_support_retest_confirmed: wrong_rate=75.0% (wrong=6/8)
- resistance_to_support_flip: wrong_rate=75.0% (wrong=6/8)
- lower_liquidity_close: wrong_rate=70.0% (wrong=7/10)
- failed_breakout_down_reversal: wrong_rate=57.1% (wrong=4/7)
- trend_flip_confirmed_down: wrong_rate=54.5% (wrong=6/11)
- long_into_major_resistance: wrong_rate=53.6% (wrong=15/28)
- major_support_rejection: wrong_rate=50.0% (wrong=3/6)
- short_into_major_support: wrong_rate=47.1% (wrong=16/34)
- bid_wall_close: wrong_rate=47.1% (wrong=8/17)
- support_to_resistance_retest_confirmed: wrong_rate=44.0% (wrong=11/25)
- upper_liquidity_close: wrong_rate=43.5% (wrong=10/23)
- support_to_resistance_flip: wrong_rate=42.3% (wrong=11/26)
- sweep_incomplete: wrong_rate=40.0% (wrong=10/25)
- short_cover_risk: wrong_rate=40.0% (wrong=4/10)
- orderbook_ask_heavy: wrong_rate=40.0% (wrong=2/5)
- major_resistance_rejection: wrong_rate=38.5% (wrong=5/13)
- trend_flip_early_down: wrong_rate=35.3% (wrong=6/17)
- long_flush_exhaustion: wrong_rate=33.3% (wrong=4/12)
- orderbook_bid_heavy: wrong_rate=33.3% (wrong=4/12)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 3件
- direction_execution_conflict の主な理由: confidence_below_min=2件, entry_zone_not_reached=1件
- direction_execution_conflict の主な risk_flags: sweep_incomplete=3件, upper_liquidity_close=3件, long_into_major_resistance=3件
- suppress_reason の内訳: confidence_below_short_min=5件, no_material_change=3件, watch_sweep_recheck_wait=2件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 0件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 40
- 本有効件数: 2
- 参考ログ件数: 38
- 平均 risk_percent_applied: 0.50
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 50.00
- 平均 position_size_usd: 3000.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 100.0%
- 平均 timeout_hours: 12.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 9件
- phase1_observation_gate=blocked: 31件
- 観測タイプ: setup_watch_learning=9件
- 観測候補全体: 9件 / 勝率=22.2% / TP1先行=22.2% / 近似PF=1.58 / 平均MFE=9.54 / 平均MAE=6.06
- setup_watch_learning: 9件 / 勝率=22.2% / TP1先行=22.2% / 近似PF=1.58 / 平均MFE=9.54 / 平均MAE=6.06
- 代表例: 20260527_080500, 20260527_060500, 20260525_120500, 20260525_040500, 20260525_020500
- 主な観測ブロック理由: confidence_below_min=28件, no_trade_candidate=15件, setup_not_observable=2件, watch_conditions_not_met=1件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 9件
- 観測タイプ: setup_watch_learning=9件
- 状態: observing=9件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 11.1%
- 代表例: 20260527_080500, 20260527_060500, 20260525_120500, 20260525_040500, 20260525_020500
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
- primary_state: early_down=17件, confirmed_down=11件, confirmed_up=6件, near_major_resistance=3件, early_up=3件
- flags: short_into_major_support=34件, long_into_major_resistance=28件, support_to_resistance_flip=26件, support_to_resistance_retest_confirmed=25件, trend_flip_early_down=17件, major_resistance_rejection=13件, trend_flip_confirmed_down=11件, resistance_to_support_flip=8件
- trend_state: early_down=17件, confirmed_down=11件, confirmed_up=6件, early_up=3件
- 下方向反転系: 28件 / 勝率=57.1% / wrong_rate=42.9%
- 下方向反転系 平均MFE24h=8.99 / 平均MAE24h=5.63
- 代表例: 20260527_160500, 20260527_130500, 20260527_080500, 20260527_060500, 20260527_000500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 40件
- 主なブロック理由: phase1_inactive=38件, setup_not_ready=38件, no_trade_flags_present=33件, wait_pressure_too_high=22件, execution_shadow_too_low=16件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 40件
- opportunity_gate=pass: 14件
- paper_positions 記録: 14件
- 紙ポジション状態: closed=14件
- 紙ポジション終了状態: sl_hit=9件, missed_opportunity=4件, tp2_hit=1件
- 紙実行候補タイプ: setup_watch_learning=9件, market_map_opportunity=5件
- opportunity_type 別 closed:
  - market_map_opportunity: 5件 / 勝率=20.0% / 平均R=1.52 / 簡易PF=0.00
  - setup_watch_learning: 9件 / 勝率=0.0% / 平均R=-0.78 / 簡易PF=0.00
- missed_opportunity: 4件
- missed代表例: 20260526_220500, 20260525_190500, 20260524_150500
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 7/7件

### risk_flags 有効性比較
- trend_flip_confirmed_down: negative_rate=90.9% (n=11)
- lower_liquidity_close: negative_rate=90.0% (n=10)
- long_into_major_resistance: negative_rate=89.3% (n=28)
- bid_wall_close: negative_rate=88.2% (n=17)
- major_resistance_rejection: negative_rate=84.6% (n=13)
- long_flush_exhaustion: negative_rate=83.3% (n=12)
- upper_liquidity_close: negative_rate=82.6% (n=23)
- short_into_major_support: negative_rate=79.4% (n=34)
- support_to_resistance_flip: negative_rate=76.9% (n=26)
- sweep_incomplete: negative_rate=76.0% (n=25)
- support_to_resistance_retest_confirmed: negative_rate=76.0% (n=25)
- orderbook_bid_heavy: negative_rate=75.0% (n=12)
- trend_flip_early_down: negative_rate=70.6% (n=17)
- short_cover_risk: negative_rate=70.0% (n=10)
