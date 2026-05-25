# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 36 件です。近似PF は 1.13、全体勝率は 55.6% でした。
- 事後評価では「待つ判断に使えた」が最も多く、19 件でした。
- 平均の役立ち度は 3.64 / 5 でした。
- 根拠整合の入力率は 72.2%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「反発示唆の過大評価」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-15 04:05 〜 2026-05-20 22:05
- 総観測件数: 36
- データ品質の内訳: ok=36
- 近似PF: 1.13

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=26件, entry_zone_not_reached=6件, near_entry_zone_waiting_trigger=3件, inside_entry_zone_with_trigger=1件
- confidence_below_min 代表例: 20260516_060500(watch/SWEEP_WAIT, dir=51, exec=18, wait=59, MFE24h=14.77, MAE24h=0.00, outcome=win) / 20260517_140501(watch/SWEEP_WAIT, dir=66, exec=26, wait=54, MFE24h=14.13, MAE24h=2.49, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 19件
- 見送り判断に使えた: 5件
- 価値が低かった: 2件
- 通知が早すぎた: 1件
- 通知が遅すぎた: 1件
- 平均の役立ち度: 3.64 / 5
- 値動きの主因の入力率: 77.8%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 72.2% / 整合率: 100.0%
- SL評価: SL は妥当=19件, SL が狭すぎた=9件
- TP評価: TP が遠すぎた=8件, TP は妥当=16件, TP が近すぎた=4件
- 4時間足評価: 一部弱い=18件, 妥当=10件
- 1時間足評価: 一部弱い=20件, 妥当=5件, 弱い=3件
- 15分足評価: 妥当=8件, 一部弱い=13件, 弱い=7件
### 改善アクション
- 分類: 入口条件を調整=23件, 観測継続=3件, 対応なし=1件, 通知文面を調整=1件
- 重要度: 中=18件, 低=4件, 高=6件
- 高優先の代表例:
  - 20260519_020500: 入口条件を調整 / 15分足で上側流動性回収後の再拒否確定を発火必須にし、臨界帯では通知を待機専用に固定する。
  - 20260518_000500: 入口条件を調整 / 15分足で戻り待ち未達のまま加速した場合に追随エントリーを許可する代替条件を追加する。
  - 20260517_140501: 入口条件を調整 / 15分足で上側流動性回収と再失速確認が出るまでエントリー無効を明示し、発火条件を厳格化する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=324 / backlog=73 / AI済み=251 / human_override=0
- 今回の同期: created=8 / reused=0 / request_failed=0 / daily_cap=8
- 最終AI評価: 2026-05-20T18:36:56.729009Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 反発示唆の過大評価
   理由: countertrend_long_cluster の wrong が 6/10 件 (60.0%)
   主に触る場所: src/analysis/confidence.py, src/analysis/position_risk.py
2. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 2 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 2件
- 主な通知理由: bias_changed=2件, confidence_jump=2件, agreement_changed=1件
- 代表例: 20260519_190500(bias_changed,confidence_jump, exec=25, wait=48) / 20260519_120500(agreement_changed,bias_changed, exec=25, wait=48)
- 現行watch再計算: 20260519_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260519_120500=>watch/entry_zone_not_reached/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=80.0%, 平均MFE=6.96, 平均MAE=4.24 (n=15) / データ不足 15/30
- transition: 勝率=38.1%, 平均MFE=4.70, 平均MAE=5.56 (n=21) / データ不足 21/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=55.6%, 平均MFE=5.64, 平均MAE=5.01 (n=36)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=8.47, 平均MAE=4.90 (n=2) / データ不足 2/30
- RISKY_ENTRY: 勝率=66.7%, 平均MFE=5.12, 平均MAE=3.46 (n=6) / データ不足 6/30
- SWEEP_WAIT: 勝率=46.7%, 平均MFE=6.11, 平均MAE=5.56 (n=15) / データ不足 15/30
- NO_TRADE_CANDIDATE: 勝率=53.8%, 平均MFE=4.91, 平均MAE=5.12 (n=13) / データ不足 13/30

### bias別件数・勝率
- long: 勝率=36.4% (n=11) / データ不足 11/30
- short: 勝率=64.0% (n=25) / データ不足 25/30

### bias別 direction 正誤
- long: correct=1, wrong=6, unclear=4 / wrong_rate=54.5% (n=11)
- short: correct=13, wrong=7, unclear=5 / wrong_rate=28.0% (n=25)

### 成績指標
- 全体勝率: 55.6%
- 平均MFE(signal_based): 5.64
- 平均MAE(signal_based): 5.01
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 55.6%

### 通知品質
- A: 通知して良かった = 20件
- B: 通知したが微妙 = 16件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- trend_flip_confirmed_up: wrong_rate=80.0% (wrong=4/5)
- failed_breakout_up_reversal: wrong_rate=66.7% (wrong=6/9)
- orderbook_bid_heavy: wrong_rate=60.0% (wrong=6/10)
- long_flush_exhaustion: wrong_rate=57.1% (wrong=4/7)
- lower_liquidity_close: wrong_rate=55.6% (wrong=5/9)
- major_support_rejection: wrong_rate=54.5% (wrong=6/11)
- trend_flip_confirmed_down: wrong_rate=53.8% (wrong=7/13)
- ask_wall_close: wrong_rate=50.0% (wrong=3/6)
- orderbook_ask_heavy: wrong_rate=42.9% (wrong=3/7)
- short_cover_risk: wrong_rate=41.7% (wrong=5/12)
- sweep_incomplete: wrong_rate=40.0% (wrong=12/30)
- support_to_resistance_flip: wrong_rate=40.0% (wrong=8/20)
- support_to_resistance_retest_confirmed: wrong_rate=40.0% (wrong=8/20)
- short_into_major_support: wrong_rate=38.7% (wrong=12/31)
- long_into_major_resistance: wrong_rate=34.6% (wrong=9/26)
- resistance_to_support_flip: wrong_rate=33.3% (wrong=4/12)
- resistance_to_support_retest_confirmed: wrong_rate=33.3% (wrong=4/12)
- major_resistance_rejection: wrong_rate=20.0% (wrong=3/15)
- bid_wall_close: wrong_rate=20.0% (wrong=2/10)
- trend_flip_early_up: wrong_rate=20.0% (wrong=1/5)
- upper_liquidity_close: wrong_rate=18.2% (wrong=4/22)
- cvd_bullish_divergence: wrong_rate=16.7% (wrong=1/6)
- failed_breakout_down_reversal: wrong_rate=11.1% (wrong=1/9)
- trend_flip_early_down: wrong_rate=9.1% (wrong=1/11)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 2件
- direction_execution_conflict の主な理由: confidence_below_min=2件
- direction_execution_conflict の主な risk_flags: bid_wall_close=2件, orderbook_bid_heavy=2件, sweep_incomplete=2件
- suppress_reason の内訳: confidence_below_short_min=7件, confidence_below_long_min=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 2件

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
- phase1_observation_gate=pass: 6件
- phase1_observation_gate=blocked: 30件
- 観測タイプ: setup_watch_learning=6件
- 観測候補全体: 6件 / 勝率=50.0% / TP1先行=50.0% / 近似PF=0.92 / 平均MFE=4.29 / 平均MAE=4.68
- setup_watch_learning: 6件 / 勝率=50.0% / TP1先行=50.0% / 近似PF=0.92 / 平均MFE=4.29 / 平均MAE=4.68
- 代表例: 20260520_070500, 20260519_190500, 20260519_170500, 20260519_120500, 20260519_020500
- 主な観測ブロック理由: confidence_below_min=26件, no_trade_candidate=13件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 6件
- 観測タイプ: setup_watch_learning=6件
- 状態: observing=6件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 50.0%
- 代表例: 20260520_070500, 20260519_190500, 20260519_170500, 20260519_120500, 20260519_020500
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
- primary_state: confirmed_down=13件, early_down=11件, confirmed_up=5件, early_up=5件, near_major_support=1件
- flags: short_into_major_support=31件, long_into_major_resistance=26件, support_to_resistance_flip=20件, support_to_resistance_retest_confirmed=20件, major_resistance_rejection=15件, trend_flip_confirmed_down=13件, resistance_to_support_flip=12件, resistance_to_support_retest_confirmed=12件
- trend_state: confirmed_down=13件, early_down=11件, confirmed_up=5件, early_up=5件
- 下方向反転系: 24件 / 勝率=54.2% / wrong_rate=33.3%
- 下方向反転系 平均MFE24h=6.87 / 平均MAE24h=4.00
- 代表例: 20260520_130500, 20260520_090500, 20260520_020500, 20260519_190500, 20260519_170500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 36件
- 主なブロック理由: phase1_inactive=36件, setup_not_ready=36件, execution_shadow_too_low=16件, wait_pressure_too_high=15件, no_trade_flags_present=13件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 36件
- opportunity_gate=pass: 17件
- paper_positions 記録: 17件
- 紙ポジション状態: closed=17件
- 紙ポジション終了状態: sl_hit=10件, missed_opportunity=6件, timeout=1件
- 紙実行候補タイプ: market_map_opportunity=11件, setup_watch_learning=6件
- opportunity_type 別 closed:
  - market_map_opportunity: 11件 / 勝率=0.0% / 平均R=-0.07 / 簡易PF=0.87
  - setup_watch_learning: 6件 / 勝率=0.0% / 平均R=0.01 / 簡易PF=1.03
- missed_opportunity: 6件
- missed代表例: 20260520_070500, 20260518_130500, 20260518_000500
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 4/4件

### risk_flags 有効性比較
- resistance_to_support_flip: negative_rate=91.7% (n=12)
- resistance_to_support_retest_confirmed: negative_rate=91.7% (n=12)
- trend_flip_confirmed_down: negative_rate=84.6% (n=13)
- short_cover_risk: negative_rate=83.3% (n=12)
- major_support_rejection: negative_rate=81.8% (n=11)
- orderbook_bid_heavy: negative_rate=80.0% (n=10)
- long_into_major_resistance: negative_rate=76.9% (n=26)
- sweep_incomplete: negative_rate=76.7% (n=30)
- short_into_major_support: negative_rate=74.2% (n=31)
- support_to_resistance_flip: negative_rate=70.0% (n=20)
- support_to_resistance_retest_confirmed: negative_rate=70.0% (n=20)
- major_resistance_rejection: negative_rate=66.7% (n=15)
- upper_liquidity_close: negative_rate=63.6% (n=22)
- trend_flip_early_down: negative_rate=63.6% (n=11)
- bid_wall_close: negative_rate=60.0% (n=10)
