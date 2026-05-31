# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 39 件です。近似PF は 1.20、全体勝率は 61.5% でした。
- 事後評価では「待つ判断に使えた」が最も多く、20 件でした。
- 平均の役立ち度は 3.52 / 5 でした。
- 根拠整合の入力率は 74.4%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=2 件、phase1_active=true=2 件です。
- 判定: Phase 1 の本有効確認を進めてよい (phase1_active=true の実データが出ているため、正式指標の観測を優先する)

## 2. 今回の対象
- 集計期間: 2026-05-23 13:05 〜 2026-05-28 20:05
- 総観測件数: 39
- データ品質の内訳: ok=39
- 近似PF: 1.20

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 2
- `phase1_active=true` 件数: 2
- 判定: Phase 1 の本有効確認を進めてよい
- 補足: phase1_active=true の実データが出ているため、正式指標の観測を優先する
- TP1 到達率: 50.0%
- `tp1_hit_first=false` 率: 50.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 100.0%
- ready阻害理由: confidence_below_min=22件, near_entry_zone_waiting_trigger=8件, entry_zone_not_reached=6件, inside_entry_zone_with_trigger=1件
- confidence_below_min 代表例: 20260527_130500(invalid/NO_TRADE_CANDIDATE, dir=68, exec=11, wait=78, MFE24h=18.16, MAE24h=0.00, outcome=win) / 20260525_190500(watch/SWEEP_WAIT, dir=66, exec=28, wait=59, MFE24h=15.65, MAE24h=4.85, outcome=win)
- 直近の観測対象:
  - 2026-05-24 06:05 / 20260523_210500 / setup=ready / phase1_active=True / outcome=loss
  - 2026-05-23 23:05 / 20260523_140500 / setup=ready / phase1_active=True / outcome=win

## 4. AI事後評価サマリー
- 待つ判断に使えた: 20件
- 見送り判断に使えた: 7件
- 価値が低かった: 2件
- 通知が早すぎた: 1件
- 入る判断に使えた: 1件
- 平均の役立ち度: 3.52 / 5
- レビュー source: ai=31件
- 値動きの主因の入力率: 79.5%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 74.4% / 整合率: 100.0%
- SL評価: SL は妥当=19件, SL が広すぎた=2件, SL が狭すぎた=10件
- TP評価: TP が遠すぎた=10件, TP は妥当=16件, TP が近すぎた=5件
- 4時間足評価: 一部弱い=24件, 妥当=5件, 弱い=2件
- 1時間足評価: 一部弱い=23件, 妥当=7件, 弱い=1件
- 15分足評価: 弱い=12件, 一部弱い=9件, 妥当=10件
### 改善アクション
- 分類: 通知文面を調整=3件, 入口条件を調整=21件, 観測継続=6件, 出口設計を調整=1件
- 重要度: 高=9件, 中=20件, 低=2件
- 高優先の代表例:
  - 20260527_160500: 通知文面を調整 / 件名の「上方向バイアス」を弱め、先頭に「エントリー禁止・待機専用」を固定表示して誤読を防ぐ。
  - 20260526_150500: 入口条件を調整 / 15分足で支持帯直下の再ブレイク条件を追加し、NO_TRADE固定を緩めて段階的にショート許可する。
  - 20260525_190500: 入口条件を調整 / 15分足で上側流動性スイープ後の再失速をエントリー条件に追加し、WAIT解除を1段早める。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=382 / backlog=67 / AI済み=315 / human_override=0
- 今回の同期: created=8 / reused=0 / request_failed=0 / daily_cap=8
- 最終AI評価: 2026-05-28T18:37:12.188439Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 12/31 件 (38.7%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 5/6 件 (83.3%)
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
- range: 勝率=57.6%, 平均MFE=6.77, 平均MAE=6.11 (n=33)
- transition: 勝率=80.0%, 平均MFE=9.08, 平均MAE=5.33 (n=5) / データ不足 5/30
- volatile: 勝率=100.0%, 平均MFE=6.31, 平均MAE=0.23 (n=1) / データ不足 1/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=61.5%, 平均MFE=7.05, 平均MAE=5.86 (n=39)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=66.7%, 平均MFE=8.38, 平均MAE=3.79 (n=6) / データ不足 6/30
- RISKY_ENTRY: 勝率=57.1%, 平均MFE=7.01, 平均MAE=6.07 (n=7) / データ不足 7/30
- SWEEP_WAIT: 勝率=63.6%, 平均MFE=7.71, 平均MAE=5.46 (n=11) / データ不足 11/30
- NO_TRADE_CANDIDATE: 勝率=60.0%, 平均MFE=6.06, 平均MAE=6.89 (n=15) / データ不足 15/30

### bias別件数・勝率
- long: 勝率=44.4% (n=9) / データ不足 9/30
- short: 勝率=66.7% (n=30)

### bias別 direction 正誤
- long: correct=2, wrong=6, unclear=1 / wrong_rate=66.7% (n=9)
- short: correct=12, wrong=13, unclear=5 / wrong_rate=43.3% (n=30)

### 成績指標
- 全体勝率: 61.5%
- 平均MFE(signal_based): 7.05
- 平均MAE(signal_based): 5.86
- 平均MFE(entry_ready_based): 9.66
- 平均MAE(entry_ready_based): 2.27
- TP1先行率: 61.5%

### 通知品質
- A: 通知して良かった = 24件
- B: 通知したが微妙 = 15件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- trend_flip_confirmed_up: wrong_rate=83.3% (wrong=5/6)
- lower_liquidity_close: wrong_rate=71.4% (wrong=5/7)
- resistance_to_support_retest_confirmed: wrong_rate=71.4% (wrong=5/7)
- resistance_to_support_flip: wrong_rate=71.4% (wrong=5/7)
- long_into_major_resistance: wrong_rate=50.0% (wrong=12/24)
- bid_wall_close: wrong_rate=50.0% (wrong=9/18)
- trend_flip_confirmed_down: wrong_rate=50.0% (wrong=6/12)
- short_cover_risk: wrong_rate=50.0% (wrong=5/10)
- short_into_major_support: wrong_rate=46.4% (wrong=13/28)
- failed_breakout_down_reversal: wrong_rate=42.9% (wrong=3/7)
- upper_liquidity_close: wrong_rate=42.3% (wrong=11/26)
- support_to_resistance_retest_confirmed: wrong_rate=41.7% (wrong=10/24)
- support_to_resistance_flip: wrong_rate=40.0% (wrong=10/25)
- sweep_incomplete: wrong_rate=37.5% (wrong=9/24)
- major_resistance_rejection: wrong_rate=33.3% (wrong=4/12)
- long_flush_exhaustion: wrong_rate=33.3% (wrong=3/9)
- trend_flip_early_down: wrong_rate=31.2% (wrong=5/16)
- orderbook_bid_heavy: wrong_rate=28.6% (wrong=4/14)
- major_support_rejection: wrong_rate=28.6% (wrong=2/7)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 3件
- direction_execution_conflict の主な理由: near_entry_zone_waiting_trigger=1件, entry_zone_not_reached=1件, inside_entry_zone_with_trigger=1件
- direction_execution_conflict の主な risk_flags: sweep_incomplete=3件, upper_liquidity_close=3件, short_into_major_support=3件
- rr_sweep_recheck_wait: 2件
- attention_rr_sweep_recheck_wait: 2件
- suppress_reason の内訳: watch_sweep_recheck_wait=7件, no_material_change=5件, attention_rr_sweep_recheck_wait=2件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 0件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 39
- 本有効件数: 2
- 参考ログ件数: 37
- 平均 risk_percent_applied: 0.50
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 50.00
- 平均 position_size_usd: 3000.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 100.0%
- 平均 timeout_hours: 12.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 12件
- phase1_observation_gate=blocked: 27件
- 観測タイプ: setup_watch_learning=12件
- 観測候補全体: 12件 / 勝率=50.0% / TP1先行=50.0% / 近似PF=1.66 / 平均MFE=8.14 / 平均MAE=4.90
- setup_watch_learning: 12件 / 勝率=50.0% / TP1先行=50.0% / 近似PF=1.66 / 平均MFE=8.14 / 平均MAE=4.90
- 代表例: 20260528_070500, 20260528_040500, 20260528_010500, 20260527_190500, 20260527_080500
- 主な観測ブロック理由: confidence_below_min=22件, no_trade_candidate=15件, setup_not_observable=2件, watch_conditions_not_met=1件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 12件
- 観測タイプ: setup_watch_learning=12件
- 状態: observing=12件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 33.3%
- 代表例: 20260528_070500, 20260528_040500, 20260528_010500, 20260527_190500, 20260527_080500
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
- 記録あり: 39件
- primary_state: early_down=16件, confirmed_down=12件, confirmed_up=6件, near_major_resistance=2件, early_up=2件
- flags: short_into_major_support=28件, support_to_resistance_flip=25件, long_into_major_resistance=24件, support_to_resistance_retest_confirmed=24件, trend_flip_early_down=16件, major_resistance_rejection=12件, trend_flip_confirmed_down=12件, failed_breakout_down_reversal=7件
- trend_state: early_down=16件, confirmed_down=12件, confirmed_up=6件, early_up=2件
- 下方向反転系: 28件 / 勝率=64.3% / wrong_rate=39.3%
- 下方向反転系 平均MFE24h=7.56 / 平均MAE24h=5.18
- 代表例: 20260528_110500, 20260528_050500, 20260528_040500, 20260528_010500, 20260527_220500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 39件
- 主なブロック理由: phase1_inactive=37件, setup_not_ready=37件, no_trade_flags_present=28件, wait_pressure_too_high=21件, execution_shadow_too_low=12件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 39件
- opportunity_gate=pass: 17件
- paper_positions 記録: 17件
- 紙ポジション状態: closed=17件
- 紙ポジション終了状態: sl_hit=8件, missed_opportunity=7件, tp2_hit=2件
- 紙実行候補タイプ: setup_watch_learning=12件, market_map_opportunity=5件
- opportunity_type 別 closed:
  - market_map_opportunity: 5件 / 勝率=20.0% / 平均R=1.52 / 簡易PF=0.00
  - setup_watch_learning: 12件 / 勝率=8.3% / 平均R=0.03 / 簡易PF=1.05
- missed_opportunity: 7件
- missed代表例: 20260528_070500, 20260528_040500, 20260528_010500
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 5/5件

### risk_flags 有効性比較
- trend_flip_confirmed_down: negative_rate=91.7% (n=12)
- bid_wall_close: negative_rate=88.9% (n=18)
- long_into_major_resistance: negative_rate=87.5% (n=24)
- support_to_resistance_flip: negative_rate=80.0% (n=25)
- support_to_resistance_retest_confirmed: negative_rate=79.2% (n=24)
- short_into_major_support: negative_rate=78.6% (n=28)
- upper_liquidity_close: negative_rate=76.9% (n=26)
- major_resistance_rejection: negative_rate=75.0% (n=12)
- orderbook_bid_heavy: negative_rate=71.4% (n=14)
- sweep_incomplete: negative_rate=70.8% (n=24)
- short_cover_risk: negative_rate=70.0% (n=10)
- trend_flip_early_down: negative_rate=68.8% (n=16)
