# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 38 件です。近似PF は 0.76、全体勝率は 57.9% でした。
- 事後評価では「待つ判断に使えた」が最も多く、15 件でした。
- 平均の役立ち度は 3.41 / 5 でした。
- 根拠整合の入力率は 39.5%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-09 10:05 〜 2026-05-15 01:05
- 総観測件数: 38
- データ品質の内訳: ok=38
- 近似PF: 0.76

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=21件, entry_zone_not_reached=11件, inside_entry_zone_with_trigger=3件, near_entry_zone_waiting_trigger=3件
- confidence_below_min 代表例: 20260513_110500(watch/SWEEP_WAIT, dir=58, exec=18, wait=67, MFE24h=15.38, MAE24h=0.00, outcome=win) / 20260514_050500(invalid/RISKY_ENTRY, dir=65, exec=28, wait=43, MFE24h=13.24, MAE24h=1.11, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 15件
- 価値が低かった: 1件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.41 / 5
- 値動きの主因の入力率: 44.7%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 39.5% / 整合率: 100.0%
- SL評価: SL は妥当=12件, SL が狭すぎた=5件
- TP評価: TP が遠すぎた=6件, TP は妥当=10件, TP が近すぎた=1件
- 4時間足評価: 一部弱い=7件, 妥当=10件
- 1時間足評価: 弱い=2件, 一部弱い=15件
- 15分足評価: 弱い=12件, 一部弱い=3件, 妥当=2件
### 改善アクション
- 分類: 入口条件を調整=12件, 出口設計を調整=4件, 通知文面を調整=1件
- 重要度: 高=6件, 中=11件
- 高優先の代表例:
  - 20260513_163400: 入口条件を調整 / 15分足で79,202明確上抜け時はショート監視を即失効にする条件を追加する
  - 20260513_120500: 入口条件を調整 / 15分足で再エントリー帯未到達でも初動ブレイク追随を許可する分岐条件を追加する。
  - 20260513_110500: 入口条件を調整 / SWEEP待ち条件を緩和し、15分足で下方向ブレイク継続時はwatchから段階的に実行許可へ切り替える。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=288 / backlog=69 / AI済み=219 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-05-14T18:36:15.070374Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 12/17 件 (70.6%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. TP が遠すぎるケースが多い
   理由: tp_eval=too_far が 6/17 件 (35.3%)
   主に触る場所: src/analysis/rr.py, src/trade/exit_manager.py
3. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 3/5 件 (60.0%)
   主に触る場所: config.py, src/analysis/position_risk.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 1件
- 主な通知理由: bias_changed=1件, confidence_jump=1件
- 代表例: 20260510_190500(bias_changed,confidence_jump, exec=34, wait=58)
- 現行watch再計算: 20260510_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=56.5%, 平均MFE=6.69, 平均MAE=6.43 (n=23) / データ不足 23/30
- transition: 勝率=75.0%, 平均MFE=4.74, 平均MAE=9.16 (n=12) / データ不足 12/30
- uptrend: 勝率=0.0%, 平均MFE=1.10, 平均MAE=7.87 (n=3) / データ不足 3/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=57.9%, 平均MFE=5.63, 平均MAE=7.40 (n=38)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=60.0%, 平均MFE=5.75, 平均MAE=6.14 (n=5) / データ不足 5/30
- RISKY_ENTRY: 勝率=36.4%, 平均MFE=4.06, 平均MAE=9.42 (n=11) / データ不足 11/30
- SWEEP_WAIT: 勝率=84.6%, 平均MFE=6.24, 平均MAE=6.50 (n=13) / データ不足 13/30
- NO_TRADE_CANDIDATE: 勝率=44.4%, 平均MFE=6.61, 平均MAE=6.96 (n=9) / データ不足 9/30

### bias別件数・勝率
- long: 勝率=56.0% (n=25) / データ不足 25/30
- short: 勝率=61.5% (n=13) / データ不足 13/30

### bias別 direction 正誤
- long: correct=13, wrong=10, unclear=2 / wrong_rate=40.0% (n=25)
- short: correct=6, wrong=6, unclear=1 / wrong_rate=46.2% (n=13)

### 成績指標
- 全体勝率: 57.9%
- 平均MFE(signal_based): 5.63
- 平均MAE(signal_based): 7.40
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 57.9%

### 通知品質
- A: 通知して良かった = 22件
- B: 通知したが微妙 = 16件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- trend_flip_confirmed_down: wrong_rate=50.0% (wrong=4/8)
- cvd_bearish_divergence: wrong_rate=50.0% (wrong=3/6)
- sweep_incomplete: wrong_rate=45.8% (wrong=11/24)
- lower_liquidity_close: wrong_rate=45.0% (wrong=9/20)
- orderbook_ask_heavy: wrong_rate=44.4% (wrong=4/9)
- support_to_resistance_retest_confirmed: wrong_rate=41.7% (wrong=5/12)
- support_to_resistance_flip: wrong_rate=41.7% (wrong=5/12)
- upper_liquidity_close: wrong_rate=40.0% (wrong=4/10)
- trend_flip_confirmed_up: wrong_rate=40.0% (wrong=2/5)
- long_flush_exhaustion: wrong_rate=40.0% (wrong=2/5)
- long_into_major_resistance: wrong_rate=38.9% (wrong=7/18)
- ask_wall_close: wrong_rate=36.4% (wrong=4/11)
- short_into_major_support: wrong_rate=33.3% (wrong=5/15)
- major_resistance_rejection: wrong_rate=33.3% (wrong=2/6)
- major_support_rejection: wrong_rate=33.3% (wrong=2/6)
- resistance_to_support_flip: wrong_rate=28.6% (wrong=2/7)
- resistance_to_support_retest_confirmed: wrong_rate=28.6% (wrong=2/7)
- short_cover_risk: wrong_rate=28.6% (wrong=2/7)
- orderbook_bid_heavy: wrong_rate=20.0% (wrong=1/5)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 1件
- direction_execution_conflict の主な理由: confidence_below_min=1件
- direction_execution_conflict の主な risk_flags: bid_wall_close=1件, short_cover_risk=1件, sweep_incomplete=1件
- suppress_reason の内訳: confidence_below_long_min=5件, confidence_below_short_min=4件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 7件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 38
- 本有効件数: 0
- 参考ログ件数: 38
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 13件
- phase1_observation_gate=blocked: 25件
- 観測タイプ: setup_watch_learning=12件, confidence_watch_learning=1件
- 観測候補全体: 13件 / 勝率=46.2% / TP1先行=46.2% / 近似PF=0.55 / 平均MFE=4.55 / 平均MAE=8.26
- setup_watch_learning: 12件 / 勝率=41.7% / TP1先行=41.7% / 近似PF=0.51 / 平均MFE=4.35 / 平均MAE=8.49
- confidence_watch_learning: 1件 / 勝率=100.0% / TP1先行=100.0% / 近似PF=1.26 / 平均MFE=6.95 / 平均MAE=5.50
- 代表例: 20260514_160500, 20260514_080500, 20260513_163400, 20260513_120500, 20260513_100500
- 主な観測ブロック理由: confidence_below_min=20件, no_trade_candidate=9件, watch_conditions_not_met=1件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 13件
- 観測タイプ: setup_watch_learning=12件, confidence_watch_learning=1件
- 状態: observing=13件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 66.7%
- 代表例: 20260514_160500, 20260514_080500, 20260513_163400, 20260513_120500, 20260513_100500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### Phase 1B 昇格候補
- confidence_watch_learning 候補: 1件
- prelabel: SWEEP_WAIT=1件
- 勝率=100.0% / TP1先行=100.0% / 近似PF=1.26
- 平均 direction=60.0 / 平均 execution=22.0 / 平均 wait=76.8
- 平均MFE=6.95 / 平均MAE=5.50
- 代表例: 20260509_212745
- 扱い: `trade_execution_gate=pass` ではないが、限定条件付きで Phase 1B 候補へ昇格を検討する母集団

### counter_long_short_watch
- 候補件数: 0件
- 扱い: ロング監視の失敗初動をショート観測候補として切り出す Phase 1A 母集団

### failed_breakout_down_reversal
- 件数: 0件
- 扱い: breakout_up が効かず大きく下落した watch 群の失敗型を継続追跡する

### market_map
- 記録あり: 19件
- primary_state: confirmed_down=8件, confirmed_up=5件, early_down=4件, early_up=2件
- flags: long_into_major_resistance=18件, short_into_major_support=15件, support_to_resistance_flip=12件, support_to_resistance_retest_confirmed=12件, trend_flip_confirmed_down=8件, resistance_to_support_flip=7件, resistance_to_support_retest_confirmed=7件, major_resistance_rejection=6件
- trend_state: confirmed_down=8件, confirmed_up=5件, early_down=4件, early_up=2件
- 下方向反転系: 12件 / 勝率=66.7% / wrong_rate=41.7%
- 下方向反転系 平均MFE24h=8.02 / 平均MAE24h=7.63
- 代表例: 20260514_110500, 20260514_080500, 20260514_030500, 20260513_210500, 20260513_190500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 38件
- 主なブロック理由: phase1_inactive=38件, setup_not_ready=38件, wait_pressure_too_high=20件, execution_shadow_too_low=18件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 38件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 1/1件

### risk_flags 有効性比較
- lower_liquidity_close: negative_rate=85.0% (n=20)
- sweep_incomplete: negative_rate=83.3% (n=24)
- upper_liquidity_close: negative_rate=70.0% (n=10)
- long_into_major_resistance: negative_rate=66.7% (n=18)
- support_to_resistance_retest_confirmed: negative_rate=66.7% (n=12)
- support_to_resistance_flip: negative_rate=66.7% (n=12)
- ask_wall_close: negative_rate=63.6% (n=11)
- short_into_major_support: negative_rate=60.0% (n=15)
