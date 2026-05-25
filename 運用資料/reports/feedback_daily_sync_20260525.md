# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 39 件です。近似PF は 0.98、全体勝率は 51.3% でした。
- 事後評価では「待つ判断に使えた」が最も多く、25 件でした。
- 平均の役立ち度は 3.72 / 5 でした。
- 根拠整合の入力率は 71.8%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「SL が狭すぎるケースが多い」です。
- Phase 1 判定では ready=1 件、phase1_active=true=1 件です。
- 判定: Phase 1 の本有効確認を進めてよい (phase1_active=true の実データが出ているため、正式指標の観測を優先する)

## 2. 今回の対象
- 集計期間: 2026-05-18 09:05 〜 2026-05-24 00:05
- 総観測件数: 39
- データ品質の内訳: ok=39
- 近似PF: 0.98

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 1
- `phase1_active=true` 件数: 1
- 判定: Phase 1 の本有効確認を進めてよい
- 補足: phase1_active=true の実データが出ているため、正式指標の観測を優先する
- TP1 到達率: 100.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 100.0%
- ready阻害理由: confidence_below_min=29件, entry_zone_not_reached=4件, near_entry_zone_waiting_trigger=3件, inside_entry_zone_with_trigger=2件
- confidence_below_min 代表例: 20260522_140500(invalid/RISKY_ENTRY, dir=45, exec=35, wait=48, MFE24h=23.21, MAE24h=0.00, outcome=win) / 20260522_060500(invalid/RISKY_ENTRY, dir=61, exec=29, wait=42, MFE24h=17.65, MAE24h=0.72, outcome=win)
- 直近の観測対象:
  - 2026-05-23 23:05 / 20260523_140500 / setup=ready / phase1_active=True / outcome=win

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 25件
- 見送り判断に使えた: 4件
- 通知が早すぎた: 2件
- 通知が遅すぎた: 1件
- 平均の役立ち度: 3.72 / 5
- 値動きの主因の入力率: 82.1%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 71.8% / 整合率: 100.0%
- SL評価: SL は妥当=16件, SL が狭すぎた=15件, SL が広すぎた=1件
- TP評価: TP が近すぎた=4件, TP は妥当=19件, TP が遠すぎた=9件
- 4時間足評価: 一部弱い=23件, 妥当=9件
- 1時間足評価: 一部弱い=25件, 弱い=3件, 妥当=4件
- 15分足評価: 一部弱い=10件, 妥当=14件, 弱い=8件
### 改善アクション
- 分類: 入口条件を調整=25件, 観測継続=5件, リスク設計を調整=1件, 対応なし=1件
- 重要度: 中=20件, 高=8件, 低=4件
- 高優先の代表例:
  - 20260522_070500: 入口条件を調整 / 15分足の発火条件を「主要レジスタンス直下の上方向バイアス」では抑制し、方向表示も中立寄りに補正する。
  - 20260522_060500: 入口条件を調整 / 15分足の発火条件を見直し、短期ロング示唆と下方向バイアスが衝突した場合は通知を遅延して再判定する。
  - 20260522_010500: 入口条件を調整 / 15分足で再失速確定（高値切り下げ＋出来高/CVD追随）を満たすまで通知を遅らせ、即時逆行を避ける。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=347 / backlog=72 / AI済み=275 / human_override=0
- 今回の同期: created=8 / reused=0 / request_failed=0 / daily_cap=8
- 最終AI評価: 2026-05-23T18:37:20.724314Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. SL が狭すぎるケースが多い
   理由: sl_eval=too_tight が 15/32 件 (46.9%)
   主に触る場所: src/analysis/rr.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 3件
- 主な通知理由: bias_changed=2件, confidence_jump=2件, attention_gap_crossed=1件
- 代表例: 20260521_010500(attention_gap_crossed,attention_score_crossed, exec=32, wait=61) / 20260519_190500(bias_changed,confidence_jump, exec=25, wait=48) / 20260519_120500(agreement_changed,bias_changed, exec=25, wait=48)
- 現行watch再計算: 20260521_010500=>watch/entry_zone_not_reached/rr=1.30 / 20260519_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260519_120500=>watch/entry_zone_not_reached/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=59.3%, 平均MFE=6.33, 平均MAE=5.35 (n=27) / データ不足 27/30
- transition: 勝率=33.3%, 平均MFE=4.68, 平均MAE=7.32 (n=12) / データ不足 12/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=51.3%, 平均MFE=5.82, 平均MAE=5.95 (n=39)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=11.68, 平均MAE=1.93 (n=2) / データ不足 2/30
- RISKY_ENTRY: 勝率=62.5%, 平均MFE=8.32, 平均MAE=4.04 (n=8) / データ不足 8/30
- SWEEP_WAIT: 勝率=46.7%, 平均MFE=5.22, 平均MAE=6.30 (n=15) / データ不足 15/30
- NO_TRADE_CANDIDATE: 勝率=42.9%, 平均MFE=4.21, 平均MAE=7.25 (n=14) / データ不足 14/30

### bias別件数・勝率
- long: 勝率=38.5% (n=13) / データ不足 13/30
- short: 勝率=57.7% (n=26) / データ不足 26/30

### bias別 direction 正誤
- long: correct=4, wrong=6, unclear=3 / wrong_rate=46.2% (n=13)
- short: correct=14, wrong=7, unclear=5 / wrong_rate=26.9% (n=26)

### 成績指標
- 全体勝率: 51.3%
- 平均MFE(signal_based): 5.82
- 平均MAE(signal_based): 5.95
- 平均MFE(entry_ready_based): 17.97
- 平均MAE(entry_ready_based): 0.17
- TP1先行率: 51.3%

### 通知品質
- A: 通知して良かった = 20件
- B: 通知したが微妙 = 19件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- failed_breakout_up_reversal: wrong_rate=60.0% (wrong=3/5)
- ask_wall_close: wrong_rate=57.1% (wrong=4/7)
- lower_liquidity_close: wrong_rate=55.6% (wrong=5/9)
- failed_breakout_down_reversal: wrong_rate=50.0% (wrong=3/6)
- trend_flip_early_up: wrong_rate=50.0% (wrong=3/6)
- major_support_rejection: wrong_rate=50.0% (wrong=3/6)
- orderbook_bid_heavy: wrong_rate=38.5% (wrong=5/13)
- major_resistance_rejection: wrong_rate=38.5% (wrong=5/13)
- short_into_major_support: wrong_rate=38.2% (wrong=13/34)
- long_into_major_resistance: wrong_rate=36.7% (wrong=11/30)
- trend_flip_confirmed_down: wrong_rate=36.4% (wrong=4/11)
- support_to_resistance_flip: wrong_rate=34.8% (wrong=8/23)
- support_to_resistance_retest_confirmed: wrong_rate=34.8% (wrong=8/23)
- sweep_incomplete: wrong_rate=34.5% (wrong=10/29)
- resistance_to_support_retest_confirmed: wrong_rate=33.3% (wrong=4/12)
- resistance_to_support_flip: wrong_rate=33.3% (wrong=4/12)
- short_cover_risk: wrong_rate=33.3% (wrong=3/9)
- trend_flip_confirmed_up: wrong_rate=33.3% (wrong=2/6)
- trend_flip_early_down: wrong_rate=28.6% (wrong=4/14)
- orderbook_ask_heavy: wrong_rate=28.6% (wrong=2/7)
- upper_liquidity_close: wrong_rate=27.3% (wrong=6/22)
- bid_wall_close: wrong_rate=25.0% (wrong=3/12)
- long_flush_exhaustion: wrong_rate=20.0% (wrong=2/10)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 0件
- suppress_reason の内訳: confidence_below_short_min=4件, bias_wait=2件, confidence_below_long_min=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 0件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 39
- 本有効件数: 1
- 参考ログ件数: 38
- 平均 risk_percent_applied: 0.50
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 50.00
- 平均 position_size_usd: 3000.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 100.0%
- 平均 timeout_hours: 12.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 8件
- phase1_observation_gate=blocked: 31件
- 観測タイプ: setup_watch_learning=8件
- 観測候補全体: 8件 / 勝率=37.5% / TP1先行=37.5% / 近似PF=0.98 / 平均MFE=5.37 / 平均MAE=5.46
- setup_watch_learning: 8件 / 勝率=37.5% / TP1先行=37.5% / 近似PF=0.98 / 平均MFE=5.37 / 平均MAE=5.46
- 代表例: 20260523_040500, 20260522_010500, 20260521_010500, 20260520_070500, 20260519_190500
- 主な観測ブロック理由: confidence_below_min=29件, no_trade_candidate=14件, setup_not_observable=1件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 8件
- 観測タイプ: setup_watch_learning=8件
- 状態: observing=8件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 37.5%
- 代表例: 20260523_040500, 20260522_010500, 20260521_010500, 20260520_070500, 20260519_190500
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
- primary_state: early_down=14件, confirmed_down=11件, early_up=6件, confirmed_up=6件, near_major_resistance=1件
- flags: short_into_major_support=34件, long_into_major_resistance=30件, support_to_resistance_flip=23件, support_to_resistance_retest_confirmed=23件, trend_flip_early_down=14件, major_resistance_rejection=13件, resistance_to_support_flip=12件, resistance_to_support_retest_confirmed=12件
- trend_state: early_down=14件, confirmed_down=11件, early_up=6件, confirmed_up=6件
- 下方向反転系: 25件 / 勝率=52.0% / wrong_rate=32.0%
- 下方向反転系 平均MFE24h=6.48 / 平均MAE24h=4.73
- 代表例: 20260523_150500, 20260523_050500, 20260522_180500, 20260522_140500, 20260522_070500
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 39件
- 主なブロック理由: phase1_inactive=38件, setup_not_ready=38件, no_trade_flags_present=34件, wait_pressure_too_high=20件, execution_shadow_too_low=17件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 39件
- opportunity_gate=pass: 17件
- paper_positions 記録: 17件
- 紙ポジション状態: closed=17件
- 紙ポジション終了状態: sl_hit=9件, missed_opportunity=6件, tp2_hit=1件, timeout=1件
- 紙実行候補タイプ: market_map_opportunity=9件, setup_watch_learning=8件
- opportunity_type 別 closed:
  - market_map_opportunity: 9件 / 勝率=11.1% / 平均R=0.51 / 簡易PF=2.53
  - setup_watch_learning: 8件 / 勝率=0.0% / 平均R=-0.24 / 簡易PF=0.58
- missed_opportunity: 6件
- missed代表例: 20260522_180500, 20260521_140500, 20260521_010500
- 24h超の pending: 0件
- opportunity pass だが paper_positions 未記録: 0件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 4/4件

### risk_flags 有効性比較
- resistance_to_support_retest_confirmed: negative_rate=83.3% (n=12)
- resistance_to_support_flip: negative_rate=83.3% (n=12)
- trend_flip_confirmed_down: negative_rate=81.8% (n=11)
- major_resistance_rejection: negative_rate=76.9% (n=13)
- long_into_major_resistance: negative_rate=76.7% (n=30)
- bid_wall_close: negative_rate=75.0% (n=12)
- orderbook_bid_heavy: negative_rate=69.2% (n=13)
- sweep_incomplete: negative_rate=69.0% (n=29)
- upper_liquidity_close: negative_rate=68.2% (n=22)
- short_into_major_support: negative_rate=67.6% (n=34)
- support_to_resistance_flip: negative_rate=65.2% (n=23)
- support_to_resistance_retest_confirmed: negative_rate=65.2% (n=23)
- long_flush_exhaustion: negative_rate=60.0% (n=10)
- trend_flip_early_down: negative_rate=57.1% (n=14)
