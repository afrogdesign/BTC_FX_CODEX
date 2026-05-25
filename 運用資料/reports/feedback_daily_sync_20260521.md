# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 39 件です。近似PF は 0.91、全体勝率は 64.1% でした。
- 事後評価では「待つ判断に使えた」が最も多く、15 件でした。
- 平均の役立ち度は 3.62 / 5 でした。
- 根拠整合の入力率は 53.8%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「速報で方向/実行不整合が継続」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-14 04:05 〜 2026-05-20 02:05
- 総観測件数: 39
- データ品質の内訳: ok=39
- 近似PF: 0.91

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=27件, entry_zone_not_reached=7件, near_entry_zone_waiting_trigger=3件, inside_entry_zone_with_trigger=2件
- confidence_below_min 代表例: 20260516_060500(watch/SWEEP_WAIT, dir=51, exec=18, wait=59, MFE24h=14.77, MAE24h=0.00, outcome=win) / 20260517_140501(watch/SWEEP_WAIT, dir=66, exec=26, wait=54, MFE24h=14.13, MAE24h=2.49, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 15件
- 見送り判断に使えた: 5件
- 価値が低かった: 2件
- 通知が早すぎた: 1件
- 通知が遅すぎた: 1件
- 平均の役立ち度: 3.62 / 5
- 値動きの主因の入力率: 61.5%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 53.8% / 整合率: 100.0%
- SL評価: SL は妥当=18件, SL が狭すぎた=6件
- TP評価: TP は妥当=14件, TP が近すぎた=4件, TP が遠すぎた=6件
- 4時間足評価: 妥当=7件, 一部弱い=17件
- 1時間足評価: 一部弱い=16件, 妥当=5件, 弱い=3件
- 15分足評価: 一部弱い=10件, 妥当=8件, 弱い=6件
### 改善アクション
- 分類: 入口条件を調整=18件, 観測継続=4件, 対応なし=1件, 通知文面を調整=1件
- 重要度: 中=16件, 低=3件, 高=5件
- 高優先の代表例:
  - 20260518_000500: 入口条件を調整 / 15分足で戻り待ち未達のまま加速した場合に追随エントリーを許可する代替条件を追加する。
  - 20260517_140501: 入口条件を調整 / 15分足で上側流動性回収と再失速確認が出るまでエントリー無効を明示し、発火条件を厳格化する。
  - 20260517_010500: 入口条件を調整 / 15分足で再検討帯到達後の反転確定（上値抑制＋出来高減衰）を発火必須条件にして先行通知を減らす。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=319 / backlog=76 / AI済み=243 / human_override=0
- 今回の同期: created=8 / reused=0 / request_failed=0 / daily_cap=8
- 最終AI評価: 2026-05-19T18:37:12.181298Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 2 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 1件
- 主な通知理由: agreement_changed=1件, bias_changed=1件, confidence_jump=1件
- 代表例: 20260519_120500(agreement_changed,bias_changed, exec=25, wait=48)
- 現行watch再計算: 20260519_120500=>watch/entry_zone_not_reached/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=83.3%, 平均MFE=7.43, 平均MAE=4.17 (n=12) / データ不足 12/30
- transition: 勝率=55.6%, 平均MFE=4.89, 平均MAE=7.15 (n=27) / データ不足 27/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=64.1%, 平均MFE=5.67, 平均MAE=6.23 (n=39)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=11.55, 平均MAE=6.09 (n=1) / データ不足 1/30
- RISKY_ENTRY: 勝率=80.0%, 平均MFE=5.38, 平均MAE=5.37 (n=10) / データ不足 10/30
- SWEEP_WAIT: 勝率=53.3%, 平均MFE=6.19, 平均MAE=6.22 (n=15) / データ不足 15/30
- NO_TRADE_CANDIDATE: 勝率=61.5%, 平均MFE=4.84, 平均MAE=6.91 (n=13) / データ不足 13/30

### bias別件数・勝率
- long: 勝率=46.2% (n=13) / データ不足 13/30
- short: 勝率=73.1% (n=26) / データ不足 26/30

### bias別 direction 正誤
- long: correct=3, wrong=6, unclear=4 / wrong_rate=46.2% (n=13)
- short: correct=15, wrong=7, unclear=4 / wrong_rate=26.9% (n=26)

### 成績指標
- 全体勝率: 64.1%
- 平均MFE(signal_based): 5.67
- 平均MAE(signal_based): 6.23
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 64.1%

### 通知品質
- A: 通知して良かった = 25件
- B: 通知したが微妙 = 14件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- failed_breakout_up_reversal: wrong_rate=66.7% (wrong=6/9)
- trend_flip_confirmed_up: wrong_rate=66.7% (wrong=4/6)
- orderbook_bid_heavy: wrong_rate=62.5% (wrong=5/8)
- long_flush_exhaustion: wrong_rate=57.1% (wrong=4/7)
- lower_liquidity_close: wrong_rate=50.0% (wrong=5/10)
- major_support_rejection: wrong_rate=46.2% (wrong=6/13)
- trend_flip_confirmed_down: wrong_rate=42.9% (wrong=6/14)
- short_cover_risk: wrong_rate=40.0% (wrong=4/10)
- sweep_incomplete: wrong_rate=38.7% (wrong=12/31)
- support_to_resistance_flip: wrong_rate=38.1% (wrong=8/21)
- support_to_resistance_retest_confirmed: wrong_rate=38.1% (wrong=8/21)
- ask_wall_close: wrong_rate=37.5% (wrong=3/8)
- orderbook_ask_heavy: wrong_rate=37.5% (wrong=3/8)
- short_into_major_support: wrong_rate=35.3% (wrong=12/34)
- long_into_major_resistance: wrong_rate=32.1% (wrong=9/28)
- resistance_to_support_flip: wrong_rate=28.6% (wrong=4/14)
- resistance_to_support_retest_confirmed: wrong_rate=28.6% (wrong=4/14)
- failed_breakout_down_reversal: wrong_rate=20.0% (wrong=2/10)
- major_resistance_rejection: wrong_rate=18.8% (wrong=3/16)
- bid_wall_close: wrong_rate=18.2% (wrong=2/11)
- trend_flip_early_down: wrong_rate=18.2% (wrong=2/11)
- upper_liquidity_close: wrong_rate=17.4% (wrong=4/23)
- trend_flip_early_up: wrong_rate=16.7% (wrong=1/6)
- cvd_bullish_divergence: wrong_rate=16.7% (wrong=1/6)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 2件
- direction_execution_conflict の主な理由: confidence_below_min=2件
- direction_execution_conflict の主な risk_flags: cvd_bearish_divergence=2件, sweep_incomplete=2件, upper_liquidity_close=2件
- suppress_reason の内訳: confidence_below_short_min=7件, bias_wait=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 0件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 39
- 本有効件数: 0
- 参考ログ件数: 39
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 6件
- phase1_observation_gate=blocked: 33件
- 観測タイプ: setup_watch_learning=6件
- 観測候補全体: 6件 / 勝率=66.7% / TP1先行=66.7% / 近似PF=0.59 / 平均MFE=4.11 / 平均MAE=7.00
- setup_watch_learning: 6件 / 勝率=66.7% / TP1先行=66.7% / 近似PF=0.59 / 平均MFE=4.11 / 平均MAE=7.00
- 代表例: 20260519_170500, 20260519_120500, 20260519_020500, 20260517_010500, 20260514_160500
- 主な観測ブロック理由: confidence_below_min=27件, no_trade_candidate=13件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 6件
- 観測タイプ: setup_watch_learning=6件
- 状態: observing=6件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 66.7%
- 代表例: 20260519_170500, 20260519_120500, 20260519_020500, 20260517_010500, 20260514_160500
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
- primary_state: confirmed_down=14件, early_down=11件, early_up=6件, confirmed_up=6件, near_major_support=1件
- flags: short_into_major_support=34件, long_into_major_resistance=28件, support_to_resistance_flip=21件, support_to_resistance_retest_confirmed=21件, major_resistance_rejection=16件, resistance_to_support_flip=14件, resistance_to_support_retest_confirmed=14件, trend_flip_confirmed_down=14件
- trend_state: confirmed_down=14件, early_down=11件, early_up=6件, confirmed_up=6件
- 下方向反転系: 25件 / 勝率=64.0% / wrong_rate=32.0%
- 下方向反転系 平均MFE24h=6.72 / 平均MAE24h=5.70
- 代表例: 20260519_170500, 20260519_120500, 20260519_100500, 20260519_070500, 20260519_020500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 39件
- 主なブロック理由: phase1_inactive=39件, setup_not_ready=39件, execution_shadow_too_low=19件, wait_pressure_too_high=14件, no_trade_flags_present=9件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 39件
- opportunity_gate=pass: 18件
- paper_positions 記録: 18件
- 紙ポジション状態: closed=18件
- 紙ポジション終了状態: sl_hit=10件, missed_opportunity=7件, timeout=1件
- 紙実行候補タイプ: market_map_opportunity=12件, setup_watch_learning=6件
- opportunity_type 別 closed:
  - market_map_opportunity: 12件 / 勝率=0.0% / 平均R=0.04 / 簡易PF=1.08
  - setup_watch_learning: 6件 / 勝率=0.0% / 平均R=0.18 / 簡易PF=1.72
- missed_opportunity: 7件
- missed代表例: 20260518_130500, 20260518_000500, 20260517_140501
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 4/4件

### risk_flags 有効性比較
- short_cover_risk: negative_rate=80.0% (n=10)
- lower_liquidity_close: negative_rate=80.0% (n=10)
- trend_flip_confirmed_down: negative_rate=78.6% (n=14)
- sweep_incomplete: negative_rate=74.2% (n=31)
- resistance_to_support_flip: negative_rate=71.4% (n=14)
- resistance_to_support_retest_confirmed: negative_rate=71.4% (n=14)
- failed_breakout_down_reversal: negative_rate=70.0% (n=10)
- major_support_rejection: negative_rate=69.2% (n=13)
- major_resistance_rejection: negative_rate=68.8% (n=16)
- long_into_major_resistance: negative_rate=67.9% (n=28)
- short_into_major_support: negative_rate=67.6% (n=34)
- support_to_resistance_flip: negative_rate=66.7% (n=21)
- support_to_resistance_retest_confirmed: negative_rate=66.7% (n=21)
- trend_flip_early_down: negative_rate=63.6% (n=11)
- upper_liquidity_close: negative_rate=60.9% (n=23)
- bid_wall_close: negative_rate=54.5% (n=11)
