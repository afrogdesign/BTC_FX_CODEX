# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 13 件です。近似PF は 1.22、全体勝率は 76.9% でした。
- 事後評価では「待つ判断に使えた」が最も多く、9 件でした。
- 平均の役立ち度は 3.69 / 5 でした。
- 根拠整合の入力率は 69.2%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「ENTRY_OK と setup invalid の整合性崩れ」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-03 18:05 〜 2026-04-08 13:05
- 総観測件数: 13
- データ品質の内訳: ok=13
- 近似PF: 1.22

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 9件
- 見送り判断に使えた: 2件
- 通知が早すぎた: 2件
- 平均の役立ち度: 3.69 / 5
- 値動きの主因の入力率: 84.6%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 69.2% / 整合率: 100.0%
- SL評価: SL が広すぎた=3件, SL が狭すぎた=3件, SL は妥当=6件
- TP評価: TP が近すぎた=10件, TP が遠すぎた=1件, TP は妥当=1件
- 4時間足評価: 妥当=6件, 一部弱い=6件
- 1時間足評価: 一部弱い=8件, 弱い=1件, 妥当=3件
- 15分足評価: 弱い=3件, 妥当=5件, 一部弱い=4件

## 5. 改善候補
1. ENTRY_OK と setup invalid の整合性崩れ
   理由: 期間内で ENTRY_OK + invalid が 13 件あります
   主に触る場所: main.py, src/analysis/confidence.py, src/analysis/position_risk.py
2. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 11 件あります
   主に触る場所: tools/log_feedback.py
3. TP が近すぎるケースが多い
   理由: tp_eval=too_close が 10/12 件 (83.3%)
   主に触る場所: src/analysis/rr.py, src/trade/exit_manager.py

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- downtrend: 勝率=50.0%, 平均MFE=1.80, 平均MAE=3.25 (n=4) / データ不足 4/30
- range: 勝率=100.0%, 平均MFE=5.42, 平均MAE=20.93 (n=2) / データ不足 2/30
- transition: 勝率=85.7%, 平均MFE=10.78, 平均MAE=3.11 (n=7) / データ不足 7/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=76.9%, 平均MFE=7.19, 平均MAE=5.89 (n=13) / データ不足 13/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=33.3%, 平均MFE=3.71, 平均MAE=6.14 (n=3) / データ不足 3/30
- SWEEP_WAIT: 勝率=88.9%, 平均MFE=7.11, 平均MAE=6.42 (n=9) / データ不足 9/30
- NO_TRADE_CANDIDATE: 勝率=100.0%, 平均MFE=18.44, 平均MAE=0.35 (n=1) / データ不足 1/30

### bias別件数・勝率
- long: 勝率=100.0% (n=6) / データ不足 6/30
- short: 勝率=57.1% (n=7) / データ不足 7/30

### bias別 direction 正誤
- long: correct=5, wrong=0, unclear=1 / wrong_rate=0.0% (n=6)
- short: correct=3, wrong=4, unclear=0 / wrong_rate=57.1% (n=7)

### 成績指標
- 全体勝率: 76.9%
- 平均MFE(signal_based): 7.19
- 平均MAE(signal_based): 5.89
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 76.9%

### 通知品質
- A: 通知して良かった = 10件
- B: 通知したが微妙 = 3件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- upper_liquidity_close: wrong_rate=80.0% (wrong=4/5)
- sweep_incomplete: wrong_rate=25.0% (wrong=2/8)
- lower_liquidity_close: wrong_rate=0.0% (wrong=0/6)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 11件
- ENTRY_OK + invalid: 1件
- countertrend_long_cluster: 11件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 13
- 本有効件数: 0
- 参考ログ件数: 13
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### risk_flags 有効性比較
- 比較対象となる risk_flag はまだありません
