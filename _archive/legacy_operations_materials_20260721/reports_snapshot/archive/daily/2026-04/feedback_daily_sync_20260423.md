# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 28 件です。近似PF は 0.79、全体勝率は 67.9% でした。
- 事後評価では「待つ判断に使えた」が最も多く、13 件でした。
- 平均の役立ち度は 3.56 / 5 でした。
- 根拠整合の入力率は 57.1%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「速報で方向/実行不整合が継続」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-16 04:05 〜 2026-04-21 20:05
- 総観測件数: 28
- データ品質の内訳: ok=28
- 近似PF: 0.79

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=11件, entry_zone_not_reached=7件, rr_below_min=6件, inside_entry_zone_with_trigger=3件, near_entry_zone_waiting_trigger=1件
- rr_below_min 代表例: 20260417_090500(invalid/RISKY_ENTRY, dir=87, exec=21, wait=70, MFE24h=13.43, MAE24h=3.71, outcome=win) / 20260416_170500(watch/SWEEP_WAIT, dir=37, exec=0, wait=100, MFE24h=12.11, MAE24h=0.78, outcome=win)
- confidence_below_min 代表例: 20260421_080500(invalid/NO_TRADE_CANDIDATE, dir=61, exec=5, wait=100, MFE24h=12.70, MAE24h=6.78, outcome=win) / 20260418_030500(invalid/NO_TRADE_CANDIDATE, dir=60, exec=14, wait=74, MFE24h=10.80, MAE24h=0.00, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 13件
- 価値が低かった: 2件
- 見送り判断に使えた: 1件
- 平均の役立ち度: 3.56 / 5
- 値動きの主因の入力率: 57.1%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 57.1% / 整合率: 100.0%
- SL評価: SL が狭すぎた=3件, SL は妥当=11件, SL が広すぎた=2件
- TP評価: TP は妥当=8件, TP が遠すぎた=5件, TP が近すぎた=3件
- 4時間足評価: 妥当=5件, 弱い=2件, 一部弱い=9件
- 1時間足評価: 一部弱い=14件, 妥当=2件
- 15分足評価: 弱い=5件, 一部弱い=4件, 妥当=7件
### 改善アクション
- 分類: 入口条件を調整=11件, 通知文面を調整=3件, 観測継続=2件
- 重要度: 中=11件, 高=5件
- 高優先の代表例:
  - 20260420_060500: 入口条件を調整 / 転換帯では上側流動性回収後の再下落確認（15分足の戻り失敗）をエントリー必須条件に追加する。
  - 20260420_040500: 通知文面を調整 / 件名と冒頭で「監視専用・新規エントリー非推奨」を固定表示し、下方向バイアス単独で執行想起される文面を抑制する。
  - 20260418_110745: 通知文面を調整 / 件名と冒頭で「監視専用・新規エントリー非推奨」を先頭固定し、上方向バイアス表現より待機条件を前に出す。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=171 / backlog=44 / AI済み=127 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-04-21T18:36:49.527257Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 速報で方向/実行不整合が継続
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

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=66.7%, 平均MFE=5.42, 平均MAE=6.25 (n=24) / データ不足 24/30
- transition: 勝率=50.0%, 平均MFE=1.35, 平均MAE=10.78 (n=2) / データ不足 2/30
- uptrend: 勝率=100.0%, 平均MFE=6.59, 平均MAE=6.67 (n=2) / データ不足 2/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=67.9%, 平均MFE=5.22, 平均MAE=6.60 (n=28) / データ不足 28/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=4.77, 平均MAE=6.57 (n=2) / データ不足 2/30
- RISKY_ENTRY: 勝率=75.0%, 平均MFE=6.19, 平均MAE=5.19 (n=8) / データ不足 8/30
- SWEEP_WAIT: 勝率=61.5%, 平均MFE=4.49, 平均MAE=7.36 (n=13) / データ不足 13/30
- NO_TRADE_CANDIDATE: 勝率=60.0%, 平均MFE=5.71, 平均MAE=6.93 (n=5) / データ不足 5/30

### bias別件数・勝率
- long: 勝率=68.0% (n=25) / データ不足 25/30
- short: 勝率=66.7% (n=3) / データ不足 3/30

### bias別 direction 正誤
- long: correct=7, wrong=14, unclear=4 / wrong_rate=56.0% (n=25)
- short: correct=1, wrong=2, unclear=0 / wrong_rate=66.7% (n=3)

### 成績指標
- 全体勝率: 67.9%
- 平均MFE(signal_based): 5.22
- 平均MAE(signal_based): 6.60
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 67.9%

### 通知品質
- A: 通知して良かった = 19件
- B: 通知したが微妙 = 9件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- long_flush_exhaustion: wrong_rate=63.6% (wrong=7/11)
- sweep_incomplete: wrong_rate=60.9% (wrong=14/23)
- orderbook_ask_heavy: wrong_rate=58.3% (wrong=7/12)
- lower_liquidity_close: wrong_rate=57.1% (wrong=12/21)
- ask_wall_close: wrong_rate=40.0% (wrong=2/5)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 2件
- direction_execution_conflict の主な理由: entry_zone_not_reached=2件
- direction_execution_conflict の主な risk_flags: ask_wall_close=2件, lower_liquidity_close=2件, sweep_incomplete=2件
- suppress_reason の内訳: no_material_change=5件, cooldown_active=2件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 10件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 28
- 本有効件数: 0
- 参考ログ件数: 28
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 14件
- phase1_observation_gate=blocked: 14件
- 観測タイプ: setup_watch_learning=8件, direction_rr_learning=6件
- 観測候補全体: 14件 / 勝率=85.7% / TP1先行=85.7% / 近似PF=1.05 / 平均MFE=6.03 / 平均MAE=5.74
- direction_rr_learning: 6件 / 勝率=100.0% / TP1先行=100.0% / 近似PF=2.08 / 平均MFE=8.69 / 平均MAE=4.17
- setup_watch_learning: 8件 / 勝率=75.0% / TP1先行=75.0% / 近似PF=0.58 / 平均MFE=4.03 / 平均MAE=6.92
- 代表例: 20260421_110500, 20260420_190500, 20260420_150501, 20260420_060500, 20260420_040500
- 主な観測ブロック理由: confidence_below_min=11件, no_trade_candidate=5件, watch_conditions_not_met=3件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 14件
- 観測タイプ: setup_watch_learning=8件, direction_rr_learning=6件
- 状態: observing=14件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 62.5%
- 代表例: 20260421_110500, 20260420_190500, 20260420_150501, 20260420_060500, 20260420_040500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 24件
- 主なブロック理由: phase1_inactive=24件, setup_not_ready=24件, wait_pressure_too_high=20件, execution_shadow_too_low=12件, no_trade_flags_present=3件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 24件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 3/3件

### risk_flags 有効性比較
- sweep_incomplete: negative_rate=82.6% (n=23)
- long_flush_exhaustion: negative_rate=81.8% (n=11)
- lower_liquidity_close: negative_rate=76.2% (n=21)
- orderbook_ask_heavy: negative_rate=66.7% (n=12)
