# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 25 件です。近似PF は 1.37、全体勝率は 68.0% でした。
- 事後評価では「待つ判断に使えた」が最も多く、14 件でした。
- 平均の役立ち度は 3.63 / 5 でした。
- 根拠整合の入力率は 76.0%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-02 07:05 〜 2026-05-07 22:05
- 総観測件数: 25
- データ品質の内訳: ok=25
- 近似PF: 1.37

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: entry_zone_not_reached=15件, near_entry_zone_waiting_trigger=5件, confidence_below_min=4件, inside_entry_zone_with_trigger=1件
- confidence_below_min 代表例: 20260503_160500(invalid/NO_TRADE_CANDIDATE, dir=49, exec=5, wait=100, MFE24h=17.74, MAE24h=4.26, outcome=win) / 20260503_140500(watch/SWEEP_WAIT, dir=52, exec=20, wait=80, MFE24h=16.79, MAE24h=4.12, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 14件
- 見送り判断に使えた: 2件
- 価値が低かった: 2件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.63 / 5
- 値動きの主因の入力率: 76.0%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 76.0% / 整合率: 100.0%
- SL評価: SL は妥当=13件, SL が狭すぎた=6件
- TP評価: TP は妥当=13件, TP が近すぎた=5件, TP が遠すぎた=1件
- 4時間足評価: 一部弱い=7件, 妥当=12件
- 1時間足評価: 一部弱い=16件, 妥当=3件
- 15分足評価: 妥当=3件, 弱い=10件, 一部弱い=6件
### 改善アクション
- 分類: 観測継続=2件, 通知文面を調整=2件, 入口条件を調整=15件
- 重要度: 中=9件, 高=9件, 低=1件
- 高優先の代表例:
  - 20260506_090500: 通知文面を調整 / 件名と冒頭で「方向バイアス」と「執行判断（待機/逆側条件成立）」を分離し、エントリー推奨と誤読されない文面に修正する。
  - 20260505_170500: 入口条件を調整 / 15分足のWAIT条件を緩和し、レジスタンス直上の継続買いを取りこぼさない再入場トリガーを追加する。
  - 20260505_100500: 入口条件を調整 / 15分足で上抜け継続時の追随エントリー条件を追加し、再検討帯未到達でも機会損失を減らす。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=248 / backlog=57 / AI済み=191 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-05-07T18:35:59.816828Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 10/19 件 (52.6%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 8 件あります
   主に触る場所: tools/log_feedback.py
3. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 4/6 件 (66.7%)
   主に触る場所: config.py, src/analysis/position_risk.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 1件
- 主な通知理由: bias_changed=1件, confidence_jump=1件
- 代表例: 20260503_200500(bias_changed,confidence_jump, exec=20, wait=48)
- 現行watch再計算: 20260503_200500=>watch/entry_zone_not_reached/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=80.0%, 平均MFE=13.37, 平均MAE=4.00 (n=5) / データ不足 5/30
- transition: 勝率=66.7%, 平均MFE=3.73, 平均MAE=4.78 (n=3) / データ不足 3/30
- uptrend: 勝率=64.7%, 平均MFE=6.10, 平均MAE=5.80 (n=17) / データ不足 17/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=68.0%, 平均MFE=7.27, 平均MAE=5.32 (n=25) / データ不足 25/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=66.7%, 平均MFE=5.47, 平均MAE=5.82 (n=6) / データ不足 6/30
- RISKY_ENTRY: 勝率=50.0%, 平均MFE=7.41, 平均MAE=6.42 (n=4) / データ不足 4/30
- SWEEP_WAIT: 勝率=100.0%, 平均MFE=13.71, 平均MAE=6.73 (n=3) / データ不足 3/30
- NO_TRADE_CANDIDATE: 勝率=66.7%, 平均MFE=6.51, 平均MAE=4.35 (n=12) / データ不足 12/30

### bias別件数・勝率
- long: 勝率=68.0% (n=25) / データ不足 25/30

### bias別 direction 正誤
- long: correct=11, wrong=9, unclear=5 / wrong_rate=36.0% (n=25)

### 成績指標
- 全体勝率: 68.0%
- 平均MFE(signal_based): 7.27
- 平均MAE(signal_based): 5.32
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 68.0%

### 通知品質
- A: 通知して良かった = 17件
- B: 通知したが微妙 = 8件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- short_cover_risk: wrong_rate=36.4% (wrong=4/11)
- ask_wall_close: wrong_rate=33.3% (wrong=4/12)
- sweep_incomplete: wrong_rate=31.2% (wrong=5/16)
- long_flush_exhaustion: wrong_rate=28.6% (wrong=2/7)
- lower_liquidity_close: wrong_rate=27.8% (wrong=5/18)
- orderbook_ask_heavy: wrong_rate=27.3% (wrong=3/11)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 8件
- direction_execution_conflict の主な理由: confidence_below_min=7件, near_entry_zone_waiting_trigger=1件
- direction_execution_conflict の主な risk_flags: lower_liquidity_close=8件, sweep_incomplete=8件, short_cover_risk=5件
- rr_sweep_recheck_wait: 1件
- attention_rr_sweep_recheck_wait: 1件
- suppress_reason の内訳: confidence_below_long_min=8件, attention_rr_sweep_recheck_wait=1件, no_material_change=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 11件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 25
- 本有効件数: 0
- 参考ログ件数: 25
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 12件
- phase1_observation_gate=blocked: 13件
- 観測タイプ: setup_watch_learning=12件
- 観測候補全体: 12件 / 勝率=66.7% / TP1先行=66.7% / 近似PF=1.13 / 平均MFE=7.23 / 平均MAE=6.39
- setup_watch_learning: 12件 / 勝率=66.7% / TP1先行=66.7% / 近似PF=1.13 / 平均MFE=7.23 / 平均MAE=6.39
- 代表例: 20260507_130500, 20260507_090500, 20260507_070500, 20260507_050501, 20260506_090500
- 主な観測ブロック理由: no_trade_candidate=12件, confidence_below_min=4件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 12件
- 観測タイプ: setup_watch_learning=12件
- 状態: observing=12件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 75.0%
- 代表例: 20260507_130500, 20260507_090500, 20260507_070500, 20260507_050501, 20260506_090500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### Phase 1B 昇格候補
- confidence_watch_learning 候補: 0件
- 扱い: `trade_execution_gate=pass` ではないが、限定条件付きで Phase 1B 候補へ昇格を検討する母集団

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 25件
- 主なブロック理由: phase1_inactive=25件, setup_not_ready=25件, execution_shadow_too_low=13件, wait_pressure_too_high=10件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 25件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 5/5件

### risk_flags 有効性比較
- orderbook_ask_heavy: negative_rate=54.5% (n=11)
- sweep_incomplete: negative_rate=50.0% (n=16)
- ask_wall_close: negative_rate=50.0% (n=12)
- short_cover_risk: negative_rate=45.5% (n=11)
- lower_liquidity_close: negative_rate=44.4% (n=18)
