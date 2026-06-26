# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 32 件です。近似PF は 0.98、全体勝率は 53.1% でした。
- 事後評価では「待つ判断に使えた」が最も多く、14 件でした。
- 平均の役立ち度は 3.60 / 5 でした。
- 根拠整合の入力率は 46.9%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-08 13:05 〜 2026-05-14 01:34
- 総観測件数: 32
- データ品質の内訳: ok=32
- 近似PF: 0.98

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=20件, entry_zone_not_reached=8件, inside_entry_zone_with_trigger=2件, near_entry_zone_waiting_trigger=2件
- confidence_below_min 代表例: 20260513_110500(watch/SWEEP_WAIT, dir=58, exec=18, wait=67, MFE24h=15.38, MAE24h=0.00, outcome=win) / 20260512_210500(watch/SWEEP_WAIT, dir=56, exec=23, wait=59, MFE24h=11.27, MAE24h=3.61, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 14件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.60 / 5
- 値動きの主因の入力率: 46.9%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 46.9% / 整合率: 100.0%
- SL評価: SL が狭すぎた=6件, SL は妥当=9件
- TP評価: TP は妥当=10件, TP が遠すぎた=4件, TP が近すぎた=1件
- 4時間足評価: 一部弱い=6件, 妥当=9件
- 1時間足評価: 一部弱い=15件
- 15分足評価: 弱い=9件, 一部弱い=4件, 妥当=2件
### 改善アクション
- 分類: 入口条件を調整=10件, 出口設計を調整=4件, 通知文面を調整=1件
- 重要度: 高=2件, 中=13件
- 高優先の代表例:
  - 20260512_170500: 入口条件を調整 / 15分足で再検討帯到達後の反転確認（高値切り下げ＋出来高維持）を発火条件に追加し、到達だけで監視強度を上げない。
  - 20260510_160500: 通知文面を調整 / WATCH通知では件名・本文からENTRY_OK連想を外し、未成立（価格到達待ち）を先頭固定で明記する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=280 / backlog=65 / AI済み=215 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-05-13T18:36:12.834674Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 9/15 件 (60.0%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. SL が狭すぎるケースが多い
   理由: sl_eval=too_tight が 6/15 件 (40.0%)
   主に触る場所: src/analysis/rr.py
3. SWEEP_WAIT が厳しめ
   理由: wait_too_strict が 5/12 件 (41.7%)
   主に触る場所: src/analysis/position_risk.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 1件
- 主な通知理由: bias_changed=1件, confidence_jump=1件
- 代表例: 20260510_190500(bias_changed,confidence_jump, exec=34, wait=58)
- 現行watch再計算: 20260510_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=60.0%, 平均MFE=6.64, 平均MAE=6.02 (n=25) / データ不足 25/30
- transition: 勝率=50.0%, 平均MFE=5.27, 平均MAE=5.24 (n=4) / データ不足 4/30
- uptrend: 勝率=0.0%, 平均MFE=1.10, 平均MAE=7.87 (n=3) / データ不足 3/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=53.1%, 平均MFE=5.95, 平均MAE=6.10 (n=32)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=60.0%, 平均MFE=5.75, 平均MAE=6.14 (n=5) / データ不足 5/30
- RISKY_ENTRY: 勝率=0.0%, 平均MFE=3.09, 平均MAE=10.09 (n=7) / データ不足 7/30
- SWEEP_WAIT: 勝率=83.3%, 平均MFE=6.54, 平均MAE=5.75 (n=12) / データ不足 12/30
- NO_TRADE_CANDIDATE: 勝率=50.0%, 平均MFE=7.71, 平均MAE=3.10 (n=8) / データ不足 8/30

### bias別件数・勝率
- long: 勝率=54.2% (n=24) / データ不足 24/30
- short: 勝率=50.0% (n=8) / データ不足 8/30

### bias別 direction 正誤
- long: correct=13, wrong=10, unclear=1 / wrong_rate=41.7% (n=24)
- short: correct=3, wrong=4, unclear=1 / wrong_rate=50.0% (n=8)

### 成績指標
- 全体勝率: 53.1%
- 平均MFE(signal_based): 5.95
- 平均MAE(signal_based): 6.10
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 53.1%

### 通知品質
- A: 通知して良かった = 17件
- B: 通知したが微妙 = 15件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- trend_flip_confirmed_down: wrong_rate=60.0% (wrong=3/5)
- cvd_bearish_divergence: wrong_rate=60.0% (wrong=3/5)
- orderbook_ask_heavy: wrong_rate=57.1% (wrong=4/7)
- long_into_major_resistance: wrong_rate=45.5% (wrong=5/11)
- sweep_incomplete: wrong_rate=42.9% (wrong=9/21)
- lower_liquidity_close: wrong_rate=42.9% (wrong=9/21)
- support_to_resistance_retest_confirmed: wrong_rate=42.9% (wrong=3/7)
- support_to_resistance_flip: wrong_rate=42.9% (wrong=3/7)
- upper_liquidity_close: wrong_rate=40.0% (wrong=2/5)
- ask_wall_close: wrong_rate=36.4% (wrong=4/11)
- short_into_major_support: wrong_rate=33.3% (wrong=3/9)
- short_cover_risk: wrong_rate=25.0% (wrong=2/8)

### 直近12時間速報
- 対象件数: 11件
- direction_execution_conflict: 3件
- direction_execution_conflict の主な理由: confidence_below_min=2件, inside_entry_zone_with_trigger=1件
- direction_execution_conflict の主な risk_flags: sweep_incomplete=3件, long_into_major_resistance=3件, short_into_major_support=3件
- suppress_reason の内訳: watch_sweep_recheck_wait=3件, no_material_change=2件, cooldown_active=2件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 2件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 32
- 本有効件数: 0
- 参考ログ件数: 32
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 11件
- phase1_observation_gate=blocked: 21件
- 観測タイプ: setup_watch_learning=10件, confidence_watch_learning=1件
- 観測候補全体: 11件 / 勝率=36.4% / TP1先行=36.4% / 近似PF=0.63 / 平均MFE=4.86 / 平均MAE=7.67
- setup_watch_learning: 10件 / 勝率=30.0% / TP1先行=30.0% / 近似PF=0.59 / 平均MFE=4.65 / 平均MAE=7.88
- confidence_watch_learning: 1件 / 勝率=100.0% / TP1先行=100.0% / 近似PF=1.26 / 平均MFE=6.95 / 平均MAE=5.50
- 代表例: 20260513_163400, 20260513_120500, 20260513_100500, 20260512_170500, 20260512_070501
- 主な観測ブロック理由: confidence_below_min=19件, no_trade_candidate=8件, watch_conditions_not_met=1件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 11件
- 観測タイプ: setup_watch_learning=10件, confidence_watch_learning=1件
- 状態: observing=11件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 60.0%
- 代表例: 20260513_163400, 20260513_120500, 20260513_100500, 20260512_170500, 20260512_070501
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
- 記録あり: 11件
- primary_state: confirmed_down=5件, confirmed_up=3件, early_down=2件, early_up=1件
- flags: long_into_major_resistance=11件, short_into_major_support=9件, support_to_resistance_flip=7件, support_to_resistance_retest_confirmed=7件, trend_flip_confirmed_down=5件, resistance_to_support_flip=4件, resistance_to_support_retest_confirmed=4件, major_resistance_rejection=3件
- trend_state: confirmed_down=5件, confirmed_up=3件, early_down=2件, early_up=1件
- 下方向反転系: 7件 / 勝率=57.1% / wrong_rate=42.9%
- 下方向反転系 平均MFE24h=11.50 / 平均MAE24h=3.17
- 代表例: 20260513_163400, 20260513_120500, 20260513_110500, 20260513_080500, 20260513_020500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 32件
- 主なブロック理由: phase1_inactive=32件, setup_not_ready=32件, wait_pressure_too_high=20件, execution_shadow_too_low=16件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 32件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 1/1件

### risk_flags 有効性比較
- sweep_incomplete: negative_rate=85.7% (n=21)
- lower_liquidity_close: negative_rate=85.7% (n=21)
- long_into_major_resistance: negative_rate=81.8% (n=11)
- ask_wall_close: negative_rate=72.7% (n=11)
