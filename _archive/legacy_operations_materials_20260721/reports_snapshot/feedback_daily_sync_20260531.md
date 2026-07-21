# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 41 件です。近似PF は 1.22、全体勝率は 63.4% でした。
- 事後評価では「待つ判断に使えた」が最も多く、22 件でした。
- 平均の役立ち度は 3.54 / 5 でした。
- 根拠整合の入力率は 80.5%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=1 件、phase1_active=true=1 件です。
- 判定: Phase 1 の本有効確認を進めてよい (phase1_active=true の実データが出ているため、正式指標の観測を優先する)

## 2. 今回の対象
- 集計期間: 2026-05-24 04:05 〜 2026-05-29 22:05
- 総観測件数: 41
- データ品質の内訳: ok=41
- 近似PF: 1.22

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 1
- `phase1_active=true` 件数: 1
- 判定: Phase 1 の本有効確認を進めてよい
- 補足: phase1_active=true の実データが出ているため、正式指標の観測を優先する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 100.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 100.0%
- ready阻害理由: confidence_below_min=23件, near_entry_zone_waiting_trigger=8件, entry_zone_not_reached=7件, inside_entry_zone_with_trigger=2件
- confidence_below_min 代表例: 20260527_130500(invalid/NO_TRADE_CANDIDATE, dir=68, exec=11, wait=78, MFE24h=18.16, MAE24h=0.00, outcome=win) / 20260525_190500(watch/SWEEP_WAIT, dir=66, exec=28, wait=59, MFE24h=15.65, MAE24h=4.85, outcome=win)
- 直近の観測対象:
  - 2026-05-24 06:05 / 20260523_210500 / setup=ready / phase1_active=True / outcome=loss

## 4. AI事後評価サマリー
- 待つ判断に使えた: 22件
- 見送り判断に使えた: 9件
- 価値が低かった: 2件
- 通知が遅すぎた: 1件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.54 / 5
- レビュー source: ai=35件
- 値動きの主因の入力率: 85.4%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 80.5% / 整合率: 100.0%
- SL評価: SL は妥当=23件, SL が狭すぎた=11件, SL が広すぎた=1件
- TP評価: TP は妥当=20件, TP が近すぎた=5件, TP が遠すぎた=10件
- 4時間足評価: 妥当=8件, 一部弱い=25件, 弱い=2件
- 1時間足評価: 一部弱い=28件, 妥当=7件
- 15分足評価: 妥当=10件, 弱い=15件, 一部弱い=10件
### 改善アクション
- 分類: 観測継続=7件, 入口条件を調整=24件, 通知文面を調整=3件, 出口設計を調整=1件
- 重要度: 中=21件, 高=12件, 低=2件
- 高優先の代表例:
  - 20260528_070500: 入口条件を調整 / 15分足で再検討帯未到達かつ直下サポート近接時はショート監視通知の発火を抑制する。
  - 20260528_010500: 入口条件を調整 / 15分足のショート発火条件を「スイープ必須」から段階化し、戻り売り再失速のみで入れる代替トリガーを追加する。
  - 20260527_190500: 入口条件を調整 / 15分足で再検討帯タッチ後の再下抜け確定（高値切り下げ＋出来高条件）をエントリー必須条件に追加する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=388 / backlog=65 / AI済み=323 / human_override=0
- 今回の同期: created=8 / reused=0 / request_failed=0 / daily_cap=8
- 最終AI評価: 2026-05-29T18:37:15.039689Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 15/35 件 (42.9%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 5/5 件 (100.0%)
   主に触る場所: config.py, src/analysis/position_risk.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 3 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 2件
- 主な通知理由: attention_bias_changed=1件, bias_changed=1件, confidence_jump=1件
- 代表例: 20260523_190500(bias_changed,confidence_jump, exec=33, wait=43) / 20260526_110500(attention_bias_changed, exec=15, wait=64)
- 現行watch再計算: 20260523_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260526_110500=>ready/inside_entry_zone_with_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- downtrend: 勝率=66.7%, 平均MFE=6.76, 平均MAE=6.00 (n=3) / データ不足 3/30
- range: 勝率=59.4%, 平均MFE=6.13, 平均MAE=5.48 (n=32)
- transition: 勝率=80.0%, 平均MFE=9.08, 平均MAE=5.33 (n=5) / データ不足 5/30
- volatile: 勝率=100.0%, 平均MFE=6.31, 平均MAE=0.23 (n=1) / データ不足 1/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=63.4%, 平均MFE=6.54, 平均MAE=5.37 (n=41)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=60.0%, 平均MFE=6.47, 平均MAE=4.52 (n=5) / データ不足 5/30
- RISKY_ENTRY: 勝率=50.0%, 平均MFE=6.48, 平均MAE=5.86 (n=10) / データ不足 10/30
- SWEEP_WAIT: 勝率=70.0%, 平均MFE=7.12, 平均MAE=4.95 (n=10) / データ不足 10/30
- NO_TRADE_CANDIDATE: 勝率=68.8%, 平均MFE=6.23, 平均MAE=5.60 (n=16) / データ不足 16/30

### bias別件数・勝率
- long: 勝率=42.9% (n=7) / データ不足 7/30
- short: 勝率=67.6% (n=34)

### bias別 direction 正誤
- long: correct=1, wrong=5, unclear=1 / wrong_rate=71.4% (n=7)
- short: correct=12, wrong=15, unclear=7 / wrong_rate=44.1% (n=34)

### 成績指標
- 全体勝率: 63.4%
- 平均MFE(signal_based): 6.54
- 平均MAE(signal_based): 5.37
- 平均MFE(entry_ready_based): 1.36
- 平均MAE(entry_ready_based): 4.38
- TP1先行率: 63.4%

### 通知品質
- A: 通知して良かった = 26件
- B: 通知したが微妙 = 15件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- trend_flip_confirmed_up: wrong_rate=83.3% (wrong=5/6)
- resistance_to_support_retest_confirmed: wrong_rate=71.4% (wrong=5/7)
- resistance_to_support_flip: wrong_rate=71.4% (wrong=5/7)
- lower_liquidity_close: wrong_rate=66.7% (wrong=4/6)
- trend_flip_confirmed_down: wrong_rate=61.5% (wrong=8/13)
- failed_breakout_up_reversal: wrong_rate=60.0% (wrong=3/5)
- short_cover_risk: wrong_rate=54.5% (wrong=6/11)
- bid_wall_close: wrong_rate=50.0% (wrong=9/18)
- short_into_major_support: wrong_rate=46.7% (wrong=14/30)
- long_into_major_resistance: wrong_rate=46.2% (wrong=12/26)
- major_support_rejection: wrong_rate=44.4% (wrong=4/9)
- support_to_resistance_retest_confirmed: wrong_rate=44.0% (wrong=11/25)
- support_to_resistance_flip: wrong_rate=42.3% (wrong=11/26)
- upper_liquidity_close: wrong_rate=41.4% (wrong=12/29)
- long_flush_exhaustion: wrong_rate=40.0% (wrong=4/10)
- cvd_bearish_divergence: wrong_rate=40.0% (wrong=2/5)
- sweep_incomplete: wrong_rate=38.5% (wrong=10/26)
- failed_breakout_down_reversal: wrong_rate=37.5% (wrong=3/8)
- orderbook_bid_heavy: wrong_rate=31.2% (wrong=5/16)
- trend_flip_early_down: wrong_rate=27.8% (wrong=5/18)
- major_resistance_rejection: wrong_rate=26.7% (wrong=4/15)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 3件
- direction_execution_conflict の主な理由: confidence_below_min=2件, entry_zone_not_reached=1件
- direction_execution_conflict の主な risk_flags: bid_wall_close=3件, long_flush_exhaustion=3件, sweep_incomplete=3件
- suppress_reason の内訳: confidence_below_short_min=5件, no_material_change=3件, bias_wait=2件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 2件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 41
- 本有効件数: 1
- 参考ログ件数: 40
- 平均 risk_percent_applied: 0.50
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 50.00
- 平均 position_size_usd: 3000.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 100.0%
- 平均 timeout_hours: 12.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 12件
- phase1_observation_gate=blocked: 29件
- 観測タイプ: setup_watch_learning=12件
- 観測候補全体: 12件 / 勝率=50.0% / TP1先行=50.0% / 近似PF=1.69 / 平均MFE=7.54 / 平均MAE=4.46
- setup_watch_learning: 12件 / 勝率=50.0% / TP1先行=50.0% / 近似PF=1.69 / 平均MFE=7.54 / 平均MAE=4.46
- 代表例: 20260529_050500, 20260528_070500, 20260528_040500, 20260528_010500, 20260527_190500
- 主な観測ブロック理由: confidence_below_min=23件, no_trade_candidate=16件, watch_conditions_not_met=1件, setup_not_observable=1件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 12件
- 観測タイプ: setup_watch_learning=12件
- 状態: observing=12件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 33.3%
- 代表例: 20260529_050500, 20260528_070500, 20260528_040500, 20260528_010500, 20260527_190500
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
- 記録あり: 41件
- primary_state: early_down=18件, confirmed_down=13件, confirmed_up=6件, near_major_resistance=3件, active_support=1件
- flags: short_into_major_support=30件, support_to_resistance_flip=26件, long_into_major_resistance=26件, support_to_resistance_retest_confirmed=25件, trend_flip_early_down=18件, major_resistance_rejection=15件, trend_flip_confirmed_down=13件, major_support_rejection=9件
- trend_state: early_down=18件, confirmed_down=13件, confirmed_up=6件
- 下方向反転系: 31件 / 勝率=64.5% / wrong_rate=41.9%
- 下方向反転系 平均MFE24h=7.35 / 平均MAE24h=4.60
- 代表例: 20260529_130500, 20260529_050500, 20260529_030500, 20260529_010500, 20260528_230500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 41件
- 主なブロック理由: phase1_inactive=40件, setup_not_ready=40件, no_trade_flags_present=31件, wait_pressure_too_high=20件, execution_shadow_too_low=12件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 41件
- opportunity_gate=pass: 16件
- paper_positions 記録: 16件
- 紙ポジション状態: closed=16件
- 紙ポジション終了状態: sl_hit=8件, missed_opportunity=7件, tp2_hit=1件
- 紙実行候補タイプ: setup_watch_learning=12件, market_map_opportunity=4件
- opportunity_type 別 closed:
  - market_map_opportunity: 4件 / 勝率=0.0% / 平均R=1.30 / 簡易PF=0.00
  - setup_watch_learning: 12件 / 勝率=8.3% / 平均R=0.03 / 簡易PF=1.05
- missed_opportunity: 7件
- missed代表例: 20260528_070500, 20260528_040500, 20260528_010500
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 5/5件

### risk_flags 有効性比較
- trend_flip_confirmed_down: negative_rate=92.3% (n=13)
- long_into_major_resistance: negative_rate=84.6% (n=26)
- bid_wall_close: negative_rate=83.3% (n=18)
- short_cover_risk: negative_rate=81.8% (n=11)
- support_to_resistance_flip: negative_rate=80.8% (n=26)
- short_into_major_support: negative_rate=80.0% (n=30)
- support_to_resistance_retest_confirmed: negative_rate=80.0% (n=25)
- long_flush_exhaustion: negative_rate=80.0% (n=10)
- upper_liquidity_close: negative_rate=75.9% (n=29)
- orderbook_bid_heavy: negative_rate=75.0% (n=16)
- major_resistance_rejection: negative_rate=73.3% (n=15)
- sweep_incomplete: negative_rate=73.1% (n=26)
- trend_flip_early_down: negative_rate=72.2% (n=18)
