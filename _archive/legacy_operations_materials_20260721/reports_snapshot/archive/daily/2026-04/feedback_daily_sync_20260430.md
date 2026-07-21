# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 26 件です。近似PF は 1.34、全体勝率は 46.2% でした。
- 事後評価では「待つ判断に使えた」が最も多く、19 件でした。
- 平均の役立ち度は 3.50 / 5 でした。
- 根拠整合の入力率は 84.6%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「SL が狭すぎるケースが多い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-23 13:05 〜 2026-04-29 12:05
- 総観測件数: 26
- データ品質の内訳: ok=26
- 近似PF: 1.34

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=13件, near_entry_zone_waiting_trigger=7件, inside_entry_zone_with_trigger=3件, entry_zone_not_reached=3件
- confidence_below_min 代表例: 20260426_040500(watch/SWEEP_WAIT, dir=45, exec=14, wait=90, MFE24h=24.76, MAE24h=0.00, outcome=win) / 20260426_090500(invalid/RISKY_ENTRY, dir=60, exec=24, wait=74, MFE24h=13.63, MAE24h=5.40, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 19件
- 価値が低かった: 2件
- 通知が遅すぎた: 1件
- 平均の役立ち度: 3.50 / 5
- 値動きの主因の入力率: 84.6%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 84.6% / 整合率: 100.0%
- SL評価: SL は妥当=14件, SL が狭すぎた=8件
- TP評価: TP は妥当=15件, TP が遠すぎた=5件, TP が近すぎた=2件
- 4時間足評価: 一部弱い=11件, 妥当=11件
- 1時間足評価: 一部弱い=19件, 妥当=3件
- 15分足評価: 妥当=10件, 一部弱い=4件, 弱い=8件
### 改善アクション
- 分類: 入口条件を調整=14件, 観測継続=3件, 通知文面を調整=3件, リスク設計を調整=2件
- 重要度: 中=10件, 低=3件, 高=9件
- 高優先の代表例:
  - 20260428_000500: 通知文面を調整 / 件名の「上方向バイアス」単独強調をやめ、15分足逆行優勢とWAIT理由を同列表示に修正する。
  - 20260426_200500: 入口条件を調整 / 15分足はレジスタンス帯内のロング発火を禁止し、下側流動性回収後の再奪回確認を必須条件にする。
  - 20260426_150500: 入口条件を調整 / 15分足で上側流動性スイープ完了を必須条件にして、逆張りショートの発火を後ろへずらす。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=210 / backlog=51 / AI済み=159 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-04-29T18:36:01.018803Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. SL が狭すぎるケースが多い
   理由: sl_eval=too_tight が 8/22 件 (36.4%)
   主に触る場所: src/analysis/rr.py
2. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 8/22 件 (36.4%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
3. NO_TRADE_CANDIDATE が強すぎる
   理由: skip_too_strict が 4/7 件 (57.1%)
   主に触る場所: config.py, src/analysis/position_risk.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 6件
- 主な通知理由: confidence_jump=4件, bias_changed=2件, prelabel_improved=2件
- 代表例: 20260428_120500(bias_changed,confidence_jump, exec=38, wait=51) / 20260423_100500(confidence_jump,prelabel_improved, exec=35, wait=32) / 20260428_220500(attention_gap_crossed, exec=30, wait=40)
- 現行watch再計算: 20260428_120500=>ready/inside_entry_zone_with_trigger/rr=4.91 / 20260423_100500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260428_220500=>watch/near_entry_zone_waiting_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=53.3%, 平均MFE=9.53, 平均MAE=5.07 (n=15) / データ不足 15/30
- transition: 勝率=25.0%, 平均MFE=6.89, 平均MAE=9.85 (n=4) / データ不足 4/30
- uptrend: 勝率=42.9%, 平均MFE=3.00, 平均MAE=3.96 (n=7) / データ不足 7/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=46.2%, 平均MFE=7.37, 平均MAE=5.51 (n=26) / データ不足 26/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=17.07, 平均MAE=0.01 (n=1) / データ不足 1/30
- RISKY_ENTRY: 勝率=100.0%, 平均MFE=7.88, 平均MAE=5.25 (n=2) / データ不足 2/30
- SWEEP_WAIT: 勝率=25.0%, 平均MFE=6.32, 平均MAE=5.62 (n=16) / データ不足 16/30
- NO_TRADE_CANDIDATE: 勝率=71.4%, 平均MFE=8.23, 平均MAE=6.10 (n=7) / データ不足 7/30

### bias別件数・勝率
- long: 勝率=52.6% (n=19) / データ不足 19/30
- short: 勝率=28.6% (n=7) / データ不足 7/30

### bias別 direction 正誤
- long: correct=9, wrong=8, unclear=2 / wrong_rate=42.1% (n=19)
- short: correct=2, wrong=4, unclear=1 / wrong_rate=57.1% (n=7)

### 成績指標
- 全体勝率: 46.2%
- 平均MFE(signal_based): 7.37
- 平均MAE(signal_based): 5.51
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 46.2%

### 通知品質
- A: 通知して良かった = 12件
- B: 通知したが微妙 = 14件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- bid_wall_close: wrong_rate=60.0% (wrong=3/5)
- orderbook_bid_heavy: wrong_rate=60.0% (wrong=3/5)
- upper_liquidity_close: wrong_rate=50.0% (wrong=3/6)
- lower_liquidity_close: wrong_rate=43.8% (wrong=7/16)
- sweep_incomplete: wrong_rate=42.9% (wrong=9/21)
- long_flush_exhaustion: wrong_rate=33.3% (wrong=3/9)
- orderbook_ask_heavy: wrong_rate=27.3% (wrong=3/11)
- ask_wall_close: wrong_rate=25.0% (wrong=2/8)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 4件
- direction_execution_conflict の主な理由: near_entry_zone_waiting_trigger=2件, confidence_below_min=2件
- direction_execution_conflict の主な risk_flags: sweep_incomplete=4件, orderbook_bid_heavy=3件, upper_liquidity_close=3件
- suppress_reason の内訳: confidence_below_short_min=3件, watch_sweep_recheck_wait=2件, no_material_change=2件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 2件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 26
- 本有効件数: 0
- 参考ログ件数: 26
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 7件
- phase1_observation_gate=blocked: 19件
- 観測タイプ: setup_watch_learning=7件
- 観測候補全体: 7件 / 勝率=28.6% / TP1先行=28.6% / 近似PF=1.13 / 平均MFE=6.83 / 平均MAE=6.05
- setup_watch_learning: 7件 / 勝率=28.6% / TP1先行=28.6% / 近似PF=1.13 / 平均MFE=6.83 / 平均MAE=6.05
- 代表例: 20260428_220500, 20260428_120500, 20260428_000500, 20260426_050500, 20260425_160500
- 主な観測ブロック理由: confidence_below_min=13件, no_trade_candidate=7件, watch_conditions_not_met=3件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 7件
- 観測タイプ: setup_watch_learning=7件
- 状態: observing=7件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 14.3%
- 代表例: 20260428_220500, 20260428_120500, 20260428_000500, 20260426_050500, 20260425_160500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### Phase 1B 昇格候補
- confidence_watch_learning 候補: 1件
- prelabel: SWEEP_WAIT=1件
- 勝率=0.0% / TP1先行=0.0% / 近似PF=0.12
- 平均 direction=58.0 / 平均 execution=22.0 / 平均 wait=76.8
- 平均MFE=0.67 / 平均MAE=5.38
- 代表例: 20260424_130500
- 扱い: `trade_execution_gate=pass` ではないが、限定条件付きで Phase 1B 候補へ昇格を検討する母集団

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 26件
- 主なブロック理由: phase1_inactive=26件, setup_not_ready=26件, wait_pressure_too_high=16件, execution_shadow_too_low=15件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 26件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 2/2件

### risk_flags 有効性比較
- lower_liquidity_close: negative_rate=81.2% (n=16)
- sweep_incomplete: negative_rate=76.2% (n=21)
- orderbook_ask_heavy: negative_rate=72.7% (n=11)
