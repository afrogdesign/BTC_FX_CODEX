# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 26 件です。近似PF は 0.96、全体勝率は 53.8% でした。
- 事後評価では「待つ判断に使えた」が最も多く、18 件でした。
- 平均の役立ち度は 3.65 / 5 でした。
- 根拠整合の入力率は 69.2%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「SL が狭すぎるケースが多い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-28 09:05 〜 2026-05-04 01:05
- 総観測件数: 26
- データ品質の内訳: ok=26
- 近似PF: 0.96

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=12件, near_entry_zone_waiting_trigger=7件, entry_zone_not_reached=5件, inside_entry_zone_with_trigger=2件
- confidence_below_min 代表例: 20260503_160500(invalid/NO_TRADE_CANDIDATE, dir=49, exec=5, wait=100, MFE24h=17.74, MAE24h=4.26, outcome=win) / 20260503_140500(watch/SWEEP_WAIT, dir=52, exec=20, wait=80, MFE24h=16.79, MAE24h=4.12, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 18件
- 見送り判断に使えた: 2件
- 平均の役立ち度: 3.65 / 5
- 値動きの主因の入力率: 76.9%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 69.2% / 整合率: 100.0%
- SL評価: SL は妥当=11件, SL が狭すぎた=9件
- TP評価: TP は妥当=15件, TP が遠すぎた=4件, TP が近すぎた=1件
- 4時間足評価: 一部弱い=13件, 妥当=5件, 弱い=2件
- 1時間足評価: 一部弱い=17件, 妥当=1件, 弱い=2件
- 15分足評価: 一部弱い=6件, 弱い=7件, 妥当=7件
### 改善アクション
- 分類: 入口条件を調整=16件, 通知文面を調整=2件, 観測継続=2件
- 重要度: 中=11件, 高=8件, 低=1件
- 高優先の代表例:
  - 20260501_220500: 入口条件を調整 / 15分足で78,260-78,339上抜け定着または78,128流動性掃除後の出来高反発をエントリー条件として明文化する。
  - 20260501_140500: 入口条件を調整 / 15分足のロング優勢判定を、4時間足レジスタンス直上では無効化して短期逆張り警戒を優先する。
  - 20260501_060500: 入口条件を調整 / 15分足で77,211上抜け後の出来高確認または77,072割れ後の反発確認を必須化し、臨界帯では先行通知のみで執行判定を遅らせる。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=230 / backlog=55 / AI済み=175 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-05-03T18:36:17.540116Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. SL が狭すぎるケースが多い
   理由: sl_eval=too_tight が 9/20 件 (45.0%)
   主に触る場所: src/analysis/rr.py
2. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 7/20 件 (35.0%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
3. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 5/5 件 (100.0%)
   主に触る場所: config.py, src/analysis/position_risk.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 5件
- 主な通知理由: attention_gap_crossed=2件, bias_changed=2件, attention_bias_changed=1件
- 代表例: 20260428_120500(bias_changed,confidence_jump, exec=38, wait=51) / 20260428_220500(attention_gap_crossed, exec=30, wait=40) / 20260428_000500(bias_changed, exec=27, wait=61)
- 現行watch再計算: 20260428_120500=>ready/inside_entry_zone_with_trigger/rr=4.91 / 20260428_220500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260428_000500=>watch/near_entry_zone_waiting_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=71.4%, 平均MFE=10.70, 平均MAE=4.87 (n=7) / データ不足 7/30
- transition: 勝率=47.4%, 平均MFE=4.42, 平均MAE=6.92 (n=19) / データ不足 19/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=53.8%, 平均MFE=6.11, 平均MAE=6.37 (n=26) / データ不足 26/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=60.0%, 平均MFE=3.22, 平均MAE=7.26 (n=5) / データ不足 5/30
- RISKY_ENTRY: 勝率=50.0%, 平均MFE=11.13, 平均MAE=5.42 (n=4) / データ不足 4/30
- SWEEP_WAIT: 勝率=30.0%, 平均MFE=5.72, 平均MAE=7.07 (n=10) / データ不足 10/30
- NO_TRADE_CANDIDATE: 勝率=85.7%, 平均MFE=5.87, 平均MAE=5.27 (n=7) / データ不足 7/30

### bias別件数・勝率
- long: 勝率=60.0% (n=15) / データ不足 15/30
- short: 勝率=45.5% (n=11) / データ不足 11/30

### bias別 direction 正誤
- long: correct=6, wrong=7, unclear=2 / wrong_rate=46.7% (n=15)
- short: correct=4, wrong=6, unclear=1 / wrong_rate=54.5% (n=11)

### 成績指標
- 全体勝率: 53.8%
- 平均MFE(signal_based): 6.11
- 平均MAE(signal_based): 6.37
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 56.0%

### 通知品質
- A: 通知して良かった = 14件
- B: 通知したが微妙 = 12件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- upper_liquidity_close: wrong_rate=54.5% (wrong=6/11)
- bid_wall_close: wrong_rate=50.0% (wrong=3/6)
- sweep_incomplete: wrong_rate=47.4% (wrong=9/19)
- orderbook_bid_heavy: wrong_rate=42.9% (wrong=3/7)
- short_cover_risk: wrong_rate=33.3% (wrong=2/6)
- lower_liquidity_close: wrong_rate=20.0% (wrong=2/10)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 1件
- direction_execution_conflict の主な理由: entry_zone_not_reached=1件
- direction_execution_conflict の主な risk_flags: long_flush_exhaustion=1件, lower_liquidity_close=1件, orderbook_ask_heavy=1件
- rr_sweep_recheck_wait: 1件
- attention_rr_sweep_recheck_wait: 1件
- suppress_reason の内訳: watch_sweep_recheck_wait=8件, no_material_change=4件, attention_rr_sweep_recheck_wait=1件
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
- 観測候補全体: 13件 / 勝率=38.5% / TP1先行=41.7% / 近似PF=0.57 / 平均MFE=4.37 / 平均MAE=7.65
- setup_watch_learning: 13件 / 勝率=38.5% / TP1先行=41.7% / 近似PF=0.57 / 平均MFE=4.37 / 平均MAE=7.65
- 代表例: 20260503_040500, 20260502_230500, 20260502_160500, 20260501_160500, 20260501_140500
- 主な観測ブロック理由: confidence_below_min=12件, no_trade_candidate=7件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 13件
- 観測タイプ: setup_watch_learning=13件
- 状態: observing=13件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 38.5%
- 代表例: 20260503_040500, 20260502_230500, 20260502_160500, 20260501_160500, 20260501_140500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### Phase 1B 昇格候補
- confidence_watch_learning 候補: 0件
- 扱い: `trade_execution_gate=pass` ではないが、限定条件付きで Phase 1B 候補へ昇格を検討する母集団

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 26件
- 主なブロック理由: phase1_inactive=26件, setup_not_ready=26件, wait_pressure_too_high=13件, execution_shadow_too_low=11件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 26件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 1/1件

### risk_flags 有効性比較
- upper_liquidity_close: negative_rate=72.7% (n=11)
- sweep_incomplete: negative_rate=63.2% (n=19)
- lower_liquidity_close: negative_rate=40.0% (n=10)
