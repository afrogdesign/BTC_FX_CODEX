# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 23 件です。近似PF は 2.29、全体勝率は 78.3% でした。
- 事後評価では「待つ判断に使えた」が最も多く、15 件でした。
- 平均の役立ち度は 3.50 / 5 でした。
- 根拠整合の入力率は 82.6%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-01 07:05 〜 2026-05-06 18:05
- 総観測件数: 23
- データ品質の内訳: ok=23
- 近似PF: 2.29

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: entry_zone_not_reached=14件, confidence_below_min=6件, near_entry_zone_waiting_trigger=2件, inside_entry_zone_with_trigger=1件
- confidence_below_min 代表例: 20260503_160500(invalid/NO_TRADE_CANDIDATE, dir=49, exec=5, wait=100, MFE24h=17.74, MAE24h=4.26, outcome=win) / 20260503_140500(watch/SWEEP_WAIT, dir=52, exec=20, wait=80, MFE24h=16.79, MAE24h=4.12, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 15件
- 価値が低かった: 2件
- 見送り判断に使えた: 2件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.50 / 5
- 値動きの主因の入力率: 87.0%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 82.6% / 整合率: 100.0%
- SL評価: SL は妥当=14件, SL が狭すぎた=6件
- TP評価: TP が近すぎた=5件, TP は妥当=13件, TP が遠すぎた=2件
- 4時間足評価: 妥当=12件, 一部弱い=7件, 弱い=1件
- 1時間足評価: 一部弱い=16件, 妥当=3件, 弱い=1件
- 15分足評価: 弱い=11件, 妥当=3件, 一部弱い=6件
### 改善アクション
- 分類: 入口条件を調整=18件, 通知文面を調整=1件, 観測継続=1件
- 重要度: 高=9件, 中=10件, 低=1件
- 高優先の代表例:
  - 20260505_170500: 入口条件を調整 / 15分足のWAIT条件を緩和し、レジスタンス直上の継続買いを取りこぼさない再入場トリガーを追加する。
  - 20260505_100500: 入口条件を調整 / 15分足で上抜け継続時の追随エントリー条件を追加し、再検討帯未到達でも機会損失を減らす。
  - 20260504_090500: 入口条件を調整 / 15分足で流動性スイープ完了と再検討帯反発確認を満たすまで通知ランクを抑制する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=241 / backlog=54 / AI済み=187 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-05-06T18:36:13.091334Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 11/20 件 (55.0%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 4/6 件 (66.7%)
   主に触る場所: config.py, src/analysis/position_risk.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 3 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 2件
- 主な通知理由: bias_changed=1件, confidence_jump=1件, attention_bias_changed=1件
- 代表例: 20260501_160500(attention_bias_changed, exec=25, wait=64) / 20260503_200500(bias_changed,confidence_jump, exec=20, wait=48)
- 現行watch再計算: 20260501_160500=>watch/entry_zone_not_reached/rr=1.30 / 20260503_200500=>watch/entry_zone_not_reached/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=80.0%, 平均MFE=13.37, 平均MAE=4.00 (n=5) / データ不足 5/30
- transition: 勝率=57.1%, 平均MFE=5.23, 平均MAE=4.32 (n=7) / データ不足 7/30
- uptrend: 勝率=90.9%, 平均MFE=8.50, 平均MAE=3.25 (n=11) / データ不足 11/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=78.3%, 平均MFE=8.56, 平均MAE=3.74 (n=23) / データ不足 23/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=83.3%, 平均MFE=5.47, 平均MAE=4.65 (n=6) / データ不足 6/30
- RISKY_ENTRY: 勝率=60.0%, 平均MFE=10.54, 平均MAE=4.34 (n=5) / データ不足 5/30
- SWEEP_WAIT: 勝率=66.7%, 平均MFE=12.53, 平均MAE=4.07 (n=3) / データ不足 3/30
- NO_TRADE_CANDIDATE: 勝率=88.9%, 平均MFE=8.20, 平均MAE=2.69 (n=9) / データ不足 9/30

### bias別件数・勝率
- long: 勝率=81.8% (n=22) / データ不足 22/30
- short: 勝率=0.0% (n=1) / データ不足 1/30

### bias別 direction 正誤
- long: correct=12, wrong=6, unclear=4 / wrong_rate=27.3% (n=22)
- short: correct=0, wrong=1, unclear=0 / wrong_rate=100.0% (n=1)

### 成績指標
- 全体勝率: 78.3%
- 平均MFE(signal_based): 8.56
- 平均MAE(signal_based): 3.74
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 81.8%

### 通知品質
- A: 通知して良かった = 18件
- B: 通知したが微妙 = 5件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- short_cover_risk: wrong_rate=33.3% (wrong=3/9)
- sweep_incomplete: wrong_rate=31.2% (wrong=5/16)
- lower_liquidity_close: wrong_rate=18.8% (wrong=3/16)
- orderbook_ask_heavy: wrong_rate=11.1% (wrong=1/9)
- ask_wall_close: wrong_rate=11.1% (wrong=1/9)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 3件
- direction_execution_conflict の主な理由: near_entry_zone_waiting_trigger=2件, entry_zone_not_reached=1件
- direction_execution_conflict の主な risk_flags: lower_liquidity_close=3件, sweep_incomplete=3件, ask_wall_close=1件
- rr_sweep_recheck_wait: 1件
- attention_rr_sweep_recheck_wait: 1件
- suppress_reason の内訳: cooldown_active=2件, watch_sweep_recheck_wait=2件, no_material_change=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 9件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 23
- 本有効件数: 0
- 参考ログ件数: 23
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 11件
- phase1_observation_gate=blocked: 12件
- 観測タイプ: setup_watch_learning=11件
- 観測候補全体: 11件 / 勝率=72.7% / TP1先行=80.0% / 近似PF=1.49 / 平均MFE=7.45 / 平均MAE=4.99
- setup_watch_learning: 11件 / 勝率=72.7% / TP1先行=80.0% / 近似PF=1.49 / 平均MFE=7.45 / 平均MAE=4.99
- 代表例: 20260506_090500, 20260505_120500, 20260505_010500, 20260504_020500, 20260503_200500
- 主な観測ブロック理由: no_trade_candidate=9件, confidence_below_min=6件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 11件
- 観測タイプ: setup_watch_learning=11件
- 状態: observing=11件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 81.8%
- 代表例: 20260506_090500, 20260505_120500, 20260505_010500, 20260504_020500, 20260503_200500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### Phase 1B 昇格候補
- confidence_watch_learning 候補: 0件
- 扱い: `trade_execution_gate=pass` ではないが、限定条件付きで Phase 1B 候補へ昇格を検討する母集団

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 23件
- 主なブロック理由: phase1_inactive=23件, setup_not_ready=23件, execution_shadow_too_low=10件, wait_pressure_too_high=10件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 23件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 5/5件

### risk_flags 有効性比較
- sweep_incomplete: negative_rate=43.8% (n=16)
- lower_liquidity_close: negative_rate=37.5% (n=16)
