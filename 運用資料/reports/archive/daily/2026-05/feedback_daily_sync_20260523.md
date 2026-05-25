# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 37 件です。近似PF は 1.23、全体勝率は 59.5% でした。
- 事後評価では「待つ判断に使えた」が最も多く、18 件でした。
- 平均の役立ち度は 3.63 / 5 でした。
- 根拠整合の入力率は 67.6%、整合した比率は 100.0% でした。
- 目立った改善候補はまだ確定していません。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-16 06:05 〜 2026-05-21 23:05
- 総観測件数: 37
- データ品質の内訳: ok=37
- 近似PF: 1.23

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=27件, entry_zone_not_reached=6件, near_entry_zone_waiting_trigger=3件, inside_entry_zone_with_trigger=1件
- confidence_below_min 代表例: 20260516_060500(watch/SWEEP_WAIT, dir=51, exec=18, wait=59, MFE24h=14.77, MAE24h=0.00, outcome=win) / 20260517_140501(watch/SWEEP_WAIT, dir=66, exec=26, wait=54, MFE24h=14.13, MAE24h=2.49, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 18件
- 見送り判断に使えた: 5件
- 価値が低かった: 2件
- 通知が早すぎた: 1件
- 通知が遅すぎた: 1件
- 平均の役立ち度: 3.63 / 5
- 値動きの主因の入力率: 73.0%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 67.6% / 整合率: 100.0%
- SL評価: SL は妥当=20件, SL が狭すぎた=7件
- TP評価: TP は妥当=16件, TP が遠すぎた=7件, TP が近すぎた=4件
- 4時間足評価: 一部弱い=18件, 妥当=9件
- 1時間足評価: 一部弱い=19件, 妥当=5件, 弱い=3件
- 15分足評価: 妥当=8件, 一部弱い=13件, 弱い=6件
### 改善アクション
- 分類: 観測継続=4件, 入口条件を調整=22件, 対応なし=1件
- 重要度: 低=5件, 高=7件, 中=15件
- 高優先の代表例:
  - 20260520_090500: 入口条件を調整 / 15分足で再失速確定（高値切り下げ＋出来高条件）を満たすまで通知を待機寄りに固定する。
  - 20260519_190500: 入口条件を調整 / 15分足で主要サポート直上のときはshort方向スコア上限を抑え、上側スイープ確認前は中立寄り表示に補正する。
  - 20260519_020500: 入口条件を調整 / 15分足で上側流動性回収後の再拒否確定を発火必須にし、臨界帯では通知を待機専用に固定する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=334 / backlog=75 / AI済み=259 / human_override=0
- 今回の同期: created=8 / reused=0 / request_failed=0 / daily_cap=8
- 最終AI評価: 2026-05-21T18:37:15.536573Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
- まだ改善候補を絞れるだけのデータがありません

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 3件
- 主な通知理由: bias_changed=2件, confidence_jump=2件, attention_gap_crossed=1件
- 代表例: 20260521_010500(attention_gap_crossed,attention_score_crossed, exec=32, wait=61) / 20260519_190500(bias_changed,confidence_jump, exec=25, wait=48) / 20260519_120500(agreement_changed,bias_changed, exec=25, wait=48)
- 現行watch再計算: 20260521_010500=>watch/entry_zone_not_reached/rr=1.30 / 20260519_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260519_120500=>watch/entry_zone_not_reached/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=64.0%, 平均MFE=5.76, 平均MAE=4.39 (n=25) / データ不足 25/30
- transition: 勝率=50.0%, 平均MFE=5.01, 平均MAE=4.74 (n=12) / データ不足 12/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=59.5%, 平均MFE=5.52, 平均MAE=4.50 (n=37)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=8.47, 平均MAE=4.90 (n=2) / データ不足 2/30
- RISKY_ENTRY: 勝率=60.0%, 平均MFE=2.40, 平均MAE=5.66 (n=5) / データ不足 5/30
- SWEEP_WAIT: 勝率=62.5%, 平均MFE=6.13, 平均MAE=4.16 (n=16) / データ不足 16/30
- NO_TRADE_CANDIDATE: 勝率=50.0%, 平均MFE=5.50, 平均MAE=4.42 (n=14) / データ不足 14/30

### bias別件数・勝率
- long: 勝率=50.0% (n=10) / データ不足 10/30
- short: 勝率=63.0% (n=27) / データ不足 27/30

### bias別 direction 正誤
- long: correct=2, wrong=4, unclear=4 / wrong_rate=40.0% (n=10)
- short: correct=14, wrong=7, unclear=6 / wrong_rate=25.9% (n=27)

### 成績指標
- 全体勝率: 59.5%
- 平均MFE(signal_based): 5.52
- 平均MAE(signal_based): 4.50
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 59.5%

### 通知品質
- A: 通知して良かった = 22件
- B: 通知したが微妙 = 15件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- failed_breakout_up_reversal: wrong_rate=50.0% (wrong=3/6)
- ask_wall_close: wrong_rate=42.9% (wrong=3/7)
- trend_flip_confirmed_up: wrong_rate=42.9% (wrong=3/7)
- orderbook_ask_heavy: wrong_rate=42.9% (wrong=3/7)
- orderbook_bid_heavy: wrong_rate=41.7% (wrong=5/12)
- trend_flip_confirmed_down: wrong_rate=41.7% (wrong=5/12)
- short_cover_risk: wrong_rate=41.7% (wrong=5/12)
- major_support_rejection: wrong_rate=37.5% (wrong=3/8)
- short_into_major_support: wrong_rate=34.4% (wrong=11/32)
- sweep_incomplete: wrong_rate=33.3% (wrong=10/30)
- support_to_resistance_flip: wrong_rate=33.3% (wrong=7/21)
- support_to_resistance_retest_confirmed: wrong_rate=33.3% (wrong=7/21)
- lower_liquidity_close: wrong_rate=33.3% (wrong=2/6)
- long_into_major_resistance: wrong_rate=31.0% (wrong=9/29)
- major_resistance_rejection: wrong_rate=28.6% (wrong=4/14)
- resistance_to_support_flip: wrong_rate=25.0% (wrong=3/12)
- resistance_to_support_retest_confirmed: wrong_rate=25.0% (wrong=3/12)
- upper_liquidity_close: wrong_rate=24.0% (wrong=6/25)
- long_flush_exhaustion: wrong_rate=20.0% (wrong=1/5)
- trend_flip_early_down: wrong_rate=16.7% (wrong=2/12)
- bid_wall_close: wrong_rate=16.7% (wrong=2/12)
- failed_breakout_down_reversal: wrong_rate=16.7% (wrong=1/6)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 1件
- direction_execution_conflict の主な理由: confidence_below_min=1件
- direction_execution_conflict の主な risk_flags: ask_wall_close=1件, lower_liquidity_close=1件, sweep_incomplete=1件
- suppress_reason の内訳: bias_wait=4件, confidence_below_short_min=2件, multiple_no_trade_flags=2件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 2件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 37
- 本有効件数: 0
- 参考ログ件数: 37
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 7件
- phase1_observation_gate=blocked: 30件
- 観測タイプ: setup_watch_learning=7件
- 観測候補全体: 7件 / 勝率=57.1% / TP1先行=57.1% / 近似PF=0.76 / 平均MFE=3.90 / 平均MAE=5.13
- setup_watch_learning: 7件 / 勝率=57.1% / TP1先行=57.1% / 近似PF=0.76 / 平均MFE=3.90 / 平均MAE=5.13
- 代表例: 20260521_010500, 20260520_070500, 20260519_190500, 20260519_170500, 20260519_120500
- 主な観測ブロック理由: confidence_below_min=27件, no_trade_candidate=14件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 7件
- 観測タイプ: setup_watch_learning=7件
- 状態: observing=7件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 57.1%
- 代表例: 20260521_010500, 20260520_070500, 20260519_190500, 20260519_170500, 20260519_120500
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
- 記録あり: 37件
- primary_state: confirmed_down=12件, early_down=12件, confirmed_up=7件, early_up=4件, near_major_support=1件
- flags: short_into_major_support=32件, long_into_major_resistance=29件, support_to_resistance_flip=21件, support_to_resistance_retest_confirmed=21件, major_resistance_rejection=14件, trend_flip_confirmed_down=12件, resistance_to_support_flip=12件, resistance_to_support_retest_confirmed=12件
- trend_state: confirmed_down=12件, early_down=12件, confirmed_up=7件, early_up=4件
- 下方向反転系: 24件 / 勝率=58.3% / wrong_rate=29.2%
- 下方向反転系 平均MFE24h=6.55 / 平均MAE24h=3.43
- 代表例: 20260521_140500, 20260521_110500, 20260521_070500, 20260521_050500, 20260520_210500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 37件
- 主なブロック理由: phase1_inactive=37件, setup_not_ready=37件, no_trade_flags_present=23件, wait_pressure_too_high=16件, execution_shadow_too_low=15件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 37件
- opportunity_gate=pass: 16件
- paper_positions 記録: 16件
- 紙ポジション状態: closed=16件
- 紙ポジション終了状態: missed_opportunity=8件, sl_hit=7件, timeout=1件
- 紙実行候補タイプ: market_map_opportunity=9件, setup_watch_learning=7件
- opportunity_type 別 closed:
  - market_map_opportunity: 9件 / 勝率=0.0% / 平均R=0.39 / 簡易PF=2.17
  - setup_watch_learning: 7件 / 勝率=0.0% / 平均R=0.20 / 簡易PF=1.55
- missed_opportunity: 8件
- missed代表例: 20260521_140500, 20260521_010500, 20260520_070500
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 4/4件

### risk_flags 有効性比較
- resistance_to_support_flip: negative_rate=91.7% (n=12)
- resistance_to_support_retest_confirmed: negative_rate=91.7% (n=12)
- trend_flip_confirmed_down: negative_rate=83.3% (n=12)
- short_cover_risk: negative_rate=83.3% (n=12)
- long_into_major_resistance: negative_rate=75.9% (n=29)
- orderbook_bid_heavy: negative_rate=75.0% (n=12)
- sweep_incomplete: negative_rate=73.3% (n=30)
- short_into_major_support: negative_rate=71.9% (n=32)
- major_resistance_rejection: negative_rate=71.4% (n=14)
- upper_liquidity_close: negative_rate=68.0% (n=25)
- support_to_resistance_flip: negative_rate=66.7% (n=21)
- support_to_resistance_retest_confirmed: negative_rate=66.7% (n=21)
- bid_wall_close: negative_rate=66.7% (n=12)
- trend_flip_early_down: negative_rate=58.3% (n=12)
