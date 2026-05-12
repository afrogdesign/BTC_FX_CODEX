# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 29 件です。近似PF は 1.03、全体勝率は 51.7% でした。
- 事後評価では「待つ判断に使えた」が最も多く、17 件でした。
- 平均の役立ち度は 3.55 / 5 でした。
- 根拠整合の入力率は 65.5%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「SL が狭すぎるケースが多い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-26 07:05 〜 2026-05-02 01:05
- 総観測件数: 29
- データ品質の内訳: ok=29
- 近似PF: 1.03

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=16件, near_entry_zone_waiting_trigger=6件, entry_zone_not_reached=5件, inside_entry_zone_with_trigger=2件
- confidence_below_min 代表例: 20260426_040500(watch/SWEEP_WAIT, dir=45, exec=14, wait=90, MFE24h=24.76, MAE24h=0.00, outcome=win) / 20260426_090500(invalid/RISKY_ENTRY, dir=60, exec=24, wait=74, MFE24h=13.63, MAE24h=5.40, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 17件
- 価値が低かった: 2件
- 見送り判断に使えた: 1件
- 平均の役立ち度: 3.55 / 5
- 値動きの主因の入力率: 69.0%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 65.5% / 整合率: 100.0%
- SL評価: SL は妥当=13件, SL が狭すぎた=7件
- TP評価: TP は妥当=14件, TP が遠すぎた=4件, TP が近すぎた=2件
- 4時間足評価: 一部弱い=13件, 弱い=1件, 妥当=6件
- 1時間足評価: 一部弱い=18件, 弱い=1件, 妥当=1件
- 15分足評価: 妥当=8件, 弱い=7件, 一部弱い=5件
### 改善アクション
- 分類: 入口条件を調整=14件, 通知文面を調整=2件, 観測継続=3件, リスク設計を調整=1件
- 重要度: 中=11件, 高=7件, 低=2件
- 高優先の代表例:
  - 20260429_210500: 入口条件を調整 / 4時間足サポート帯ど真ん中では逆張り方向の発火を抑制し、15分足でスイープ完了確認後のみ再判定に絞る。
  - 20260429_100500: 通知文面を調整 / 件名と本文で「監視継続・未到達」を先頭固定し、ENTRY_OKや高信頼度の誤読を防ぐ文面に修正する。
  - 20260429_030500: 入口条件を調整 / 15分足で上側流動性スイープ完了と1時間足の戻り失速確認を必須化し、未確認時は通知を監視専用に固定する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=223 / backlog=56 / AI済み=167 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-05-01T18:36:05.278915Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. SL が狭すぎるケースが多い
   理由: sl_eval=too_tight が 7/20 件 (35.0%)
   主に触る場所: src/analysis/rr.py
2. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 7/20 件 (35.0%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 5 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 5件
- 主な通知理由: attention_gap_crossed=2件, bias_changed=2件, attention_bias_changed=1件
- 代表例: 20260428_120500(bias_changed,confidence_jump, exec=38, wait=51) / 20260428_220500(attention_gap_crossed, exec=30, wait=40) / 20260428_000500(bias_changed, exec=27, wait=61)
- 現行watch再計算: 20260428_120500=>ready/inside_entry_zone_with_trigger/rr=4.91 / 20260428_220500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260428_000500=>watch/near_entry_zone_waiting_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=66.7%, 平均MFE=10.39, 平均MAE=5.29 (n=12) / データ不足 12/30
- transition: 勝率=41.2%, 平均MFE=4.29, 平均MAE=7.53 (n=17) / データ不足 17/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=51.7%, 平均MFE=6.81, 平均MAE=6.61 (n=29) / データ不足 29/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=75.0%, 平均MFE=5.17, 平均MAE=6.47 (n=4) / データ不足 4/30
- RISKY_ENTRY: 勝率=50.0%, 平均MFE=9.58, 平均MAE=6.49 (n=4) / データ不足 4/30
- SWEEP_WAIT: 勝率=38.5%, 平均MFE=5.95, 平均MAE=6.17 (n=13) / データ不足 13/30
- NO_TRADE_CANDIDATE: 勝率=62.5%, 平均MFE=7.65, 平均MAE=7.43 (n=8) / データ不足 8/30

### bias別件数・勝率
- long: 勝率=62.5% (n=16) / データ不足 16/30
- short: 勝率=38.5% (n=13) / データ不足 13/30

### bias別 direction 正誤
- long: correct=9, wrong=6, unclear=1 / wrong_rate=37.5% (n=16)
- short: correct=4, wrong=8, unclear=1 / wrong_rate=61.5% (n=13)

### 成績指標
- 全体勝率: 51.7%
- 平均MFE(signal_based): 6.81
- 平均MAE(signal_based): 6.61
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 53.6%

### 通知品質
- A: 通知して良かった = 15件
- B: 通知したが微妙 = 14件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- bid_wall_close: wrong_rate=62.5% (wrong=5/8)
- upper_liquidity_close: wrong_rate=58.3% (wrong=7/12)
- orderbook_bid_heavy: wrong_rate=55.6% (wrong=5/9)
- sweep_incomplete: wrong_rate=45.8% (wrong=11/24)
- long_flush_exhaustion: wrong_rate=33.3% (wrong=2/6)
- lower_liquidity_close: wrong_rate=27.3% (wrong=3/11)
- orderbook_ask_heavy: wrong_rate=14.3% (wrong=1/7)
- ask_wall_close: wrong_rate=0.0% (wrong=0/5)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 5件
- direction_execution_conflict の主な理由: confidence_below_min=4件, inside_entry_zone_with_trigger=1件
- direction_execution_conflict の主な risk_flags: lower_liquidity_close=5件, sweep_incomplete=5件, orderbook_ask_heavy=3件
- rr_sweep_recheck_wait: 1件
- attention_rr_sweep_recheck_wait: 1件
- suppress_reason の内訳: confidence_below_long_min=10件, attention_rr_sweep_recheck_wait=1件, rr_sweep_recheck_wait=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 10件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 29
- 本有効件数: 0
- 参考ログ件数: 29
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 11件
- phase1_observation_gate=blocked: 18件
- 観測タイプ: setup_watch_learning=11件
- 観測候補全体: 11件 / 勝率=36.4% / TP1先行=40.0% / 近似PF=0.47 / 平均MFE=3.77 / 平均MAE=7.98
- setup_watch_learning: 11件 / 勝率=36.4% / TP1先行=40.0% / 近似PF=0.47 / 平均MFE=3.77 / 平均MAE=7.98
- 代表例: 20260501_160500, 20260501_140500, 20260430_220500, 20260430_080500, 20260429_180500
- 主な観測ブロック理由: confidence_below_min=16件, no_trade_candidate=8件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 11件
- 観測タイプ: setup_watch_learning=11件
- 状態: observing=11件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 36.4%
- 代表例: 20260501_160500, 20260501_140500, 20260430_220500, 20260430_080500, 20260429_180500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### Phase 1B 昇格候補
- confidence_watch_learning 候補: 0件
- 扱い: `trade_execution_gate=pass` ではないが、限定条件付きで Phase 1B 候補へ昇格を検討する母集団

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 29件
- 主なブロック理由: phase1_inactive=29件, setup_not_ready=29件, wait_pressure_too_high=18件, execution_shadow_too_low=13件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 29件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 2/2件

### risk_flags 有効性比較
- upper_liquidity_close: negative_rate=75.0% (n=12)
- sweep_incomplete: negative_rate=66.7% (n=24)
- lower_liquidity_close: negative_rate=63.6% (n=11)
