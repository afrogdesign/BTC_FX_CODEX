# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 31 件です。近似PF は 0.87、全体勝率は 71.0% でした。
- 事後評価では「待つ判断に使えた」が最も多く、14 件でした。
- 平均の役立ち度は 3.44 / 5 でした。
- 根拠整合の入力率は 58.1%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「NO_TRADE_CANDIDATE が強すぎる」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-17 05:23 〜 2026-04-22 23:05
- 総観測件数: 31
- データ品質の内訳: ok=31
- 近似PF: 0.87

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: entry_zone_not_reached=12件, confidence_below_min=11件, near_entry_zone_waiting_trigger=3件, inside_entry_zone_with_trigger=3件, rr_below_min=2件
- rr_below_min 代表例: 20260417_090500(invalid/RISKY_ENTRY, dir=87, exec=21, wait=70, MFE24h=13.43, MAE24h=3.71, outcome=win) / 20260416_202320(invalid/RISKY_ENTRY, dir=62, exec=11, wait=94, MFE24h=9.14, MAE24h=2.78, outcome=win)
- confidence_below_min 代表例: 20260421_080500(invalid/NO_TRADE_CANDIDATE, dir=61, exec=5, wait=100, MFE24h=12.70, MAE24h=6.78, outcome=win) / 20260418_030500(invalid/NO_TRADE_CANDIDATE, dir=60, exec=14, wait=74, MFE24h=10.80, MAE24h=0.00, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 14件
- 価値が低かった: 2件
- 通知が早すぎた: 1件
- 見送り判断に使えた: 1件
- 平均の役立ち度: 3.44 / 5
- 値動きの主因の入力率: 58.1%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 58.1% / 整合率: 100.0%
- SL評価: SL が狭すぎた=4件, SL は妥当=13件, SL が広すぎた=1件
- TP評価: TP は妥当=9件, TP が近すぎた=4件, TP が遠すぎた=5件
- 4時間足評価: 一部弱い=12件, 妥当=4件, 弱い=2件
- 1時間足評価: 一部弱い=16件, 妥当=2件
- 15分足評価: 弱い=6件, 一部弱い=4件, 妥当=8件
### 改善アクション
- 分類: 入口条件を調整=11件, 通知文面を調整=4件, 観測継続=3件
- 重要度: 高=8件, 中=10件
- 高優先の代表例:
  - 20260421_110500: 入口条件を調整 / 15分足で下側流動性回収完了と反発確定を満たすまで通知ランクを監視止まりに固定する。
  - 20260421_090500: 通知文面を調整 / 件名と冒頭で「監視継続・未エントリー」を先頭固定し、上方向バイアス表現より待機条件を先に表示する。
  - 20260421_080500: 入口条件を調整 / 15分足で流動性回収後の再侵入条件を明文化し、WAIT固定で上抜け初動を取り逃がさない発火条件に調整する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=179 / backlog=48 / AI済み=131 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-04-22T18:37:04.007972Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. NO_TRADE_CANDIDATE が強すぎる
   理由: skip_too_strict が 3/8 件 (37.5%)
   主に触る場所: config.py, src/analysis/position_risk.py
2. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 2 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- RISKY_ENTRY + rr_below_min かつ execution>=20: 1件 / 平均 execution=21.0 / 平均 wait=70.4
- RISKY_ENTRY + rr_below_min の主な risk_flags: sweep_incomplete=1件
- RR再調整候補: 20260417_090500(exec=21, dir=87, wait=70, MFE24h=13.43, MAE24h=3.71, outcome=win)
- 現行RR再計算: 20260417_090500=>watch/entry_zone_not_reached/rr=1.30
- sweep_incomplete を含む RISKY_ENTRY + rr_below_min の通知済み履歴: 2件
- 主な通知理由: confidence_jump=1件, prelabel_improved=1件, attention_gap_crossed=1件
- 代表例: 20260417_090500(confidence_jump,prelabel_improved, exec=21, wait=70) / 20260416_202320(attention_gap_crossed, exec=11, wait=94)
- sweep_incomplete を含む watch 系通知済み履歴: 10件
- 主な通知理由: prelabel_improved=9件, status_upgraded=6件, confidence_jump=4件
- 代表例: 20260418_090500(prelabel_improved,status_upgraded, exec=37, wait=69) / 20260422_050500(confidence_jump,prelabel_improved, exec=35, wait=24) / 20260420_060500(prelabel_improved, exec=35, wait=40)
- 現行watch再計算: 20260418_090500=>watch/entry_zone_not_reached/rr=1.54 / 20260422_050500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260420_060500=>watch/entry_zone_not_reached/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=61.9%, 平均MFE=4.77, 平均MAE=6.83 (n=21) / データ不足 21/30
- transition: 勝率=80.0%, 平均MFE=6.50, 平均MAE=4.80 (n=5) / データ不足 5/30
- uptrend: 勝率=100.0%, 平均MFE=6.11, 平均MAE=3.88 (n=5) / データ不足 5/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=71.0%, 平均MFE=5.27, 平均MAE=6.03 (n=31)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=4.77, 平均MAE=6.57 (n=2) / データ不足 2/30
- RISKY_ENTRY: 勝率=77.8%, 平均MFE=5.44, 平均MAE=4.95 (n=9) / データ不足 9/30
- SWEEP_WAIT: 勝率=58.3%, 平均MFE=4.26, 平均MAE=7.07 (n=12) / データ不足 12/30
- NO_TRADE_CANDIDATE: 勝率=75.0%, 平均MFE=6.71, 平均MAE=5.55 (n=8) / データ不足 8/30

### bias別件数・勝率
- long: 勝率=71.4% (n=28) / データ不足 28/30
- short: 勝率=66.7% (n=3) / データ不足 3/30

### bias別 direction 正誤
- long: correct=11, wrong=12, unclear=5 / wrong_rate=42.9% (n=28)
- short: correct=1, wrong=2, unclear=0 / wrong_rate=66.7% (n=3)

### 成績指標
- 全体勝率: 71.0%
- 平均MFE(signal_based): 5.27
- 平均MAE(signal_based): 6.03
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 71.0%

### 通知品質
- A: 通知して良かった = 22件
- B: 通知したが微妙 = 9件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- long_flush_exhaustion: wrong_rate=71.4% (wrong=5/7)
- short_cover_risk: wrong_rate=60.0% (wrong=3/5)
- sweep_incomplete: wrong_rate=48.0% (wrong=12/25)
- lower_liquidity_close: wrong_rate=45.5% (wrong=10/22)
- orderbook_ask_heavy: wrong_rate=45.5% (wrong=5/11)
- ask_wall_close: wrong_rate=20.0% (wrong=2/10)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 2件
- direction_execution_conflict の主な理由: inside_entry_zone_with_trigger=2件
- direction_execution_conflict の主な risk_flags: ask_wall_close=2件, lower_liquidity_close=2件, sweep_incomplete=2件
- suppress_reason の内訳: no_material_change=6件, cooldown_active=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 11件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 31
- 本有効件数: 0
- 参考ログ件数: 31
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 13件
- phase1_observation_gate=blocked: 18件
- 観測タイプ: setup_watch_learning=11件, direction_rr_learning=2件
- 観測候補全体: 13件 / 勝率=84.6% / TP1先行=84.6% / 近似PF=0.91 / 平均MFE=5.03 / 平均MAE=5.53
- direction_rr_learning: 2件 / 勝率=100.0% / TP1先行=100.0% / 近似PF=3.48 / 平均MFE=11.28 / 平均MAE=3.25
- setup_watch_learning: 11件 / 勝率=81.8% / TP1先行=81.8% / 近似PF=0.65 / 平均MFE=3.89 / 平均MAE=5.95
- 代表例: 20260422_140500, 20260422_090501, 20260422_050500, 20260422_030500, 20260421_110500
- 主な観測ブロック理由: confidence_below_min=11件, no_trade_candidate=8件, watch_conditions_not_met=4件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 13件
- 観測タイプ: setup_watch_learning=11件, direction_rr_learning=2件
- 状態: observing=13件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 72.7%
- 代表例: 20260422_140500, 20260422_090501, 20260422_050500, 20260422_030500, 20260421_110500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 31件
- 主なブロック理由: phase1_inactive=31件, setup_not_ready=31件, wait_pressure_too_high=21件, execution_shadow_too_low=15件, no_trade_flags_present=2件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 31件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 4/4件

### risk_flags 有効性比較
- sweep_incomplete: negative_rate=76.0% (n=25)
- lower_liquidity_close: negative_rate=72.7% (n=22)
- orderbook_ask_heavy: negative_rate=63.6% (n=11)
- ask_wall_close: negative_rate=40.0% (n=10)
