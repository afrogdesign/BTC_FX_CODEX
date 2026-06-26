# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 26 件です。近似PF は 0.68、全体勝率は 53.8% でした。
- 事後評価では「待つ判断に使えた」が最も多く、19 件でした。
- 平均の役立ち度は 3.75 / 5 でした。
- 根拠整合の入力率は 73.1%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「SL が狭すぎるケースが多い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-27 05:05 〜 2026-05-03 01:05
- 総観測件数: 26
- データ品質の内訳: ok=26
- 近似PF: 0.68

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=14件, near_entry_zone_waiting_trigger=6件, entry_zone_not_reached=4件, inside_entry_zone_with_trigger=2件
- confidence_below_min 代表例: 20260501_100500(invalid/RISKY_ENTRY, dir=56, exec=24, wait=74, MFE24h=12.51, MAE24h=0.80, outcome=win) / 20260426_200500(invalid/NO_TRADE_CANDIDATE, dir=58, exec=2, wait=100, MFE24h=8.29, MAE24h=11.60, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 19件
- 見送り判断に使えた: 1件
- 平均の役立ち度: 3.75 / 5
- 値動きの主因の入力率: 76.9%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 73.1% / 整合率: 100.0%
- SL評価: SL が狭すぎた=8件, SL は妥当=12件
- TP評価: TP は妥当=15件, TP が遠すぎた=4件, TP が近すぎた=1件
- 4時間足評価: 一部弱い=12件, 妥当=7件, 弱い=1件
- 1時間足評価: 一部弱い=19件, 弱い=1件
- 15分足評価: 弱い=6件, 妥当=9件, 一部弱い=5件
### 改善アクション
- 分類: 入口条件を調整=14件, 通知文面を調整=2件, 観測継続=3件, リスク設計を調整=1件
- 重要度: 中=11件, 高=7件, 低=2件
- 高優先の代表例:
  - 20260501_140500: 入口条件を調整 / 15分足のロング優勢判定を、4時間足レジスタンス直上では無効化して短期逆張り警戒を優先する。
  - 20260501_060500: 入口条件を調整 / 15分足で77,211上抜け後の出来高確認または77,072割れ後の反発確認を必須化し、臨界帯では先行通知のみで執行判定を遅らせる。
  - 20260429_210500: 入口条件を調整 / 4時間足サポート帯ど真ん中では逆張り方向の発火を抑制し、15分足でスイープ完了確認後のみ再判定に絞る。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=226 / backlog=55 / AI済み=171 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-05-02T18:36:02.688047Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. SL が狭すぎるケースが多い
   理由: sl_eval=too_tight が 8/20 件 (40.0%)
   主に触る場所: src/analysis/rr.py
2. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 4/4 件 (100.0%)
   主に触る場所: config.py, src/analysis/position_risk.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 2 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 5件
- 主な通知理由: attention_gap_crossed=2件, bias_changed=2件, attention_bias_changed=1件
- 代表例: 20260428_120500(bias_changed,confidence_jump, exec=38, wait=51) / 20260428_220500(attention_gap_crossed, exec=30, wait=40) / 20260428_000500(bias_changed, exec=27, wait=61)
- 現行watch再計算: 20260428_120500=>ready/inside_entry_zone_with_trigger/rr=4.91 / 20260428_220500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260428_000500=>watch/near_entry_zone_waiting_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=71.4%, 平均MFE=5.17, 平均MAE=6.30 (n=7) / データ不足 7/30
- transition: 勝率=47.4%, 平均MFE=4.42, 平均MAE=6.92 (n=19) / データ不足 19/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=53.8%, 平均MFE=4.62, 平均MAE=6.75 (n=26) / データ不足 26/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=75.0%, 平均MFE=2.82, 平均MAE=7.63 (n=4) / データ不足 4/30
- RISKY_ENTRY: 勝率=33.3%, 平均MFE=8.23, 平均MAE=6.85 (n=3) / データ不足 3/30
- SWEEP_WAIT: 勝率=33.3%, 平均MFE=4.38, 平均MAE=6.69 (n=12) / データ不足 12/30
- NO_TRADE_CANDIDATE: 勝率=85.7%, 平均MFE=4.52, 平均MAE=6.31 (n=7) / データ不足 7/30

### bias別件数・勝率
- long: 勝率=64.3% (n=14) / データ不足 14/30
- short: 勝率=41.7% (n=12) / データ不足 12/30

### bias別 direction 正誤
- long: correct=6, wrong=6, unclear=2 / wrong_rate=42.9% (n=14)
- short: correct=4, wrong=7, unclear=1 / wrong_rate=58.3% (n=12)

### 成績指標
- 全体勝率: 53.8%
- 平均MFE(signal_based): 4.62
- 平均MAE(signal_based): 6.75
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 56.0%

### 通知品質
- A: 通知して良かった = 14件
- B: 通知したが微妙 = 12件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- bid_wall_close: wrong_rate=57.1% (wrong=4/7)
- upper_liquidity_close: wrong_rate=54.5% (wrong=6/11)
- orderbook_bid_heavy: wrong_rate=50.0% (wrong=4/8)
- sweep_incomplete: wrong_rate=45.0% (wrong=9/20)
- short_cover_risk: wrong_rate=40.0% (wrong=2/5)
- lower_liquidity_close: wrong_rate=20.0% (wrong=2/10)
- orderbook_ask_heavy: wrong_rate=20.0% (wrong=1/5)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 2件
- direction_execution_conflict の主な理由: confidence_below_min=2件
- direction_execution_conflict の主な risk_flags: lower_liquidity_close=2件, sweep_incomplete=1件, ask_wall_close=1件
- suppress_reason の内訳: confidence_below_long_min=8件, bias_wait=2件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 9件

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
- phase1_observation_gate=pass: 11件
- phase1_observation_gate=blocked: 15件
- 観測タイプ: setup_watch_learning=11件
- 観測候補全体: 11件 / 勝率=36.4% / TP1先行=40.0% / 近似PF=0.35 / 平均MFE=2.92 / 平均MAE=8.41
- setup_watch_learning: 11件 / 勝率=36.4% / TP1先行=40.0% / 近似PF=0.35 / 平均MFE=2.92 / 平均MAE=8.41
- 代表例: 20260502_160500, 20260501_160500, 20260501_140500, 20260430_220500, 20260430_080500
- 主な観測ブロック理由: confidence_below_min=14件, no_trade_candidate=7件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 11件
- 観測タイプ: setup_watch_learning=11件
- 状態: observing=11件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 36.4%
- 代表例: 20260502_160500, 20260501_160500, 20260501_140500, 20260430_220500, 20260430_080500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### Phase 1B 昇格候補
- confidence_watch_learning 候補: 0件
- 扱い: `trade_execution_gate=pass` ではないが、限定条件付きで Phase 1B 候補へ昇格を検討する母集団

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 26件
- 主なブロック理由: phase1_inactive=26件, setup_not_ready=26件, wait_pressure_too_high=14件, execution_shadow_too_low=11件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 26件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 1/1件

### risk_flags 有効性比較
- upper_liquidity_close: negative_rate=72.7% (n=11)
- sweep_incomplete: negative_rate=60.0% (n=20)
- lower_liquidity_close: negative_rate=40.0% (n=10)
