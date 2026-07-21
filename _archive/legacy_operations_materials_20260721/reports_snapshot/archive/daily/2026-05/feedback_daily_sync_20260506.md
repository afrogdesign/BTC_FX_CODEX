# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 26 件です。近似PF は 1.18、全体勝率は 57.7% でした。
- 事後評価では「待つ判断に使えた」が最も多く、18 件でした。
- 平均の役立ち度は 3.65 / 5 でした。
- 根拠整合の入力率は 69.2%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「SL が狭すぎるケースが多い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-29 07:05 〜 2026-05-04 18:05
- 総観測件数: 26
- データ品質の内訳: ok=26
- 近似PF: 1.18

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=10件, entry_zone_not_reached=9件, near_entry_zone_waiting_trigger=6件, inside_entry_zone_with_trigger=1件
- confidence_below_min 代表例: 20260503_160500(invalid/NO_TRADE_CANDIDATE, dir=49, exec=5, wait=100, MFE24h=17.74, MAE24h=4.26, outcome=win) / 20260503_140500(watch/SWEEP_WAIT, dir=52, exec=20, wait=80, MFE24h=16.79, MAE24h=4.12, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 18件
- 見送り判断に使えた: 2件
- 平均の役立ち度: 3.65 / 5
- 値動きの主因の入力率: 76.9%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 69.2% / 整合率: 100.0%
- SL評価: SL が狭すぎた=9件, SL は妥当=11件
- TP評価: TP は妥当=15件, TP が近すぎた=2件, TP が遠すぎた=3件
- 4時間足評価: 一部弱い=12件, 妥当=6件, 弱い=2件
- 1時間足評価: 一部弱い=15件, 妥当=3件, 弱い=2件
- 15分足評価: 弱い=9件, 一部弱い=7件, 妥当=4件
### 改善アクション
- 分類: 入口条件を調整=18件, 通知文面を調整=1件, 観測継続=1件
- 重要度: 中=12件, 高=8件
- 高優先の代表例:
  - 20260502_230500: 入口条件を調整 / 15分足で下側流動性回収後の反発確認条件を厳格化し、エントリー帯到達だけでは発火しないようにする。
  - 20260501_220500: 入口条件を調整 / 15分足で78,260-78,339上抜け定着または78,128流動性掃除後の出来高反発をエントリー条件として明文化する。
  - 20260501_140500: 入口条件を調整 / 15分足のロング優勢判定を、4時間足レジスタンス直上では無効化して短期逆張り警戒を優先する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=234 / backlog=55 / AI済み=179 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-05-04T18:36:09.595121Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. SL が狭すぎるケースが多い
   理由: sl_eval=too_tight が 9/20 件 (45.0%)
   主に触る場所: src/analysis/rr.py
2. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 9/20 件 (45.0%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
3. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 5/6 件 (83.3%)
   主に触る場所: config.py, src/analysis/position_risk.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 4件
- 主な通知理由: attention_gap_crossed=2件, bias_changed=1件, confidence_jump=1件
- 代表例: 20260428_220500(attention_gap_crossed, exec=30, wait=40) / 20260429_160500(attention_gap_crossed,attention_score_crossed, exec=25, wait=40) / 20260501_160500(attention_bias_changed, exec=25, wait=64)
- 現行watch再計算: 20260428_220500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260429_160500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260501_160500=>watch/entry_zone_not_reached/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=80.0%, 平均MFE=13.37, 平均MAE=4.00 (n=5) / データ不足 5/30
- transition: 勝率=47.1%, 平均MFE=4.59, 平均MAE=6.64 (n=17) / データ不足 17/30
- uptrend: 勝率=75.0%, 平均MFE=9.60, 平均MAE=5.65 (n=4) / データ不足 4/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=57.7%, 平均MFE=7.05, 平均MAE=5.98 (n=26) / データ不足 26/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=66.7%, 平均MFE=3.26, 平均MAE=6.96 (n=6) / データ不足 6/30
- RISKY_ENTRY: 勝率=50.0%, 平均MFE=11.13, 平均MAE=5.42 (n=4) / データ不足 4/30
- SWEEP_WAIT: 勝率=37.5%, 平均MFE=8.23, 平均MAE=6.49 (n=8) / データ不足 8/30
- NO_TRADE_CANDIDATE: 勝率=75.0%, 平均MFE=6.68, 平均MAE=5.00 (n=8) / データ不足 8/30

### bias別件数・勝率
- long: 勝率=66.7% (n=18) / データ不足 18/30
- short: 勝率=37.5% (n=8) / データ不足 8/30

### bias別 direction 正誤
- long: correct=7, wrong=8, unclear=3 / wrong_rate=44.4% (n=18)
- short: correct=2, wrong=6, unclear=0 / wrong_rate=75.0% (n=8)

### 成績指標
- 全体勝率: 57.7%
- 平均MFE(signal_based): 7.05
- 平均MAE(signal_based): 5.98
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 60.0%

### 通知品質
- A: 通知して良かった = 15件
- B: 通知したが微妙 = 11件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- upper_liquidity_close: wrong_rate=75.0% (wrong=6/8)
- orderbook_bid_heavy: wrong_rate=60.0% (wrong=3/5)
- sweep_incomplete: wrong_rate=52.6% (wrong=10/19)
- short_cover_risk: wrong_rate=50.0% (wrong=4/8)
- lower_liquidity_close: wrong_rate=25.0% (wrong=3/12)
- orderbook_ask_heavy: wrong_rate=20.0% (wrong=1/5)
- ask_wall_close: wrong_rate=16.7% (wrong=1/6)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 2件
- direction_execution_conflict の主な理由: near_entry_zone_waiting_trigger=1件, entry_zone_not_reached=1件
- direction_execution_conflict の主な risk_flags: ask_wall_close=2件, lower_liquidity_close=2件, orderbook_ask_heavy=1件
- suppress_reason の内訳: no_material_change=6件, watch_sweep_recheck_wait=3件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 12件

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
- phase1_observation_gate=pass: 13件
- phase1_observation_gate=blocked: 13件
- 観測タイプ: setup_watch_learning=13件
- 観測候補全体: 13件 / 勝率=53.8% / TP1先行=58.3% / 近似PF=0.85 / 平均MFE=5.86 / 平均MAE=6.90
- setup_watch_learning: 13件 / 勝率=53.8% / TP1先行=58.3% / 近似PF=0.85 / 平均MFE=5.86 / 平均MAE=6.90
- 代表例: 20260504_020500, 20260503_200500, 20260503_040500, 20260502_230500, 20260502_160500
- 主な観測ブロック理由: confidence_below_min=10件, no_trade_candidate=8件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 13件
- 観測タイプ: setup_watch_learning=13件
- 状態: observing=13件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 53.8%
- 代表例: 20260504_020500, 20260503_200500, 20260503_040500, 20260502_230500, 20260502_160500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### Phase 1B 昇格候補
- confidence_watch_learning 候補: 0件
- 扱い: `trade_execution_gate=pass` ではないが、限定条件付きで Phase 1B 候補へ昇格を検討する母集団

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 26件
- 主なブロック理由: phase1_inactive=26件, setup_not_ready=26件, execution_shadow_too_low=11件, wait_pressure_too_high=11件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 26件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 2/2件

### risk_flags 有効性比較
- sweep_incomplete: negative_rate=57.9% (n=19)
- lower_liquidity_close: negative_rate=41.7% (n=12)
