# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 25 件です。近似PF は 2.18、全体勝率は 88.0% でした。
- 事後評価では「入る判断に使えた」が最も多く、7 件でした。
- 平均の役立ち度は 3.75 / 5 でした。
- 根拠整合の入力率は 28.0%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「ENTRY_OK と setup invalid の整合性崩れ」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-05 19:05 〜 2026-04-11 00:05
- 総観測件数: 25
- データ品質の内訳: ok=25
- 近似PF: 2.18

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
- 入る判断に使えた: 7件
- 待つ判断に使えた: 6件
- 通知が早すぎた: 2件
- 見送り判断に使えた: 1件
- 平均の役立ち度: 3.75 / 5
- 値動きの主因の入力率: 36.0%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 28.0% / 整合率: 100.0%

## 5. 改善候補
1. ENTRY_OK と setup invalid の整合性崩れ
   理由: 期間内で ENTRY_OK + invalid が 14 件あります
   主に触る場所: main.py, src/analysis/confidence.py, src/analysis/position_risk.py
2. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 12 件あります
   主に触る場所: tools/log_feedback.py
3. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 5/5 件 (100.0%)
   主に触る場所: config.py, src/analysis/position_risk.py

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=100.0%, 平均MFE=3.97, 平均MAE=37.43 (n=1) / データ不足 1/30
- transition: 勝率=100.0%, 平均MFE=10.37, 平均MAE=2.65 (n=7) / データ不足 7/30
- uptrend: 勝率=82.4%, 平均MFE=7.78, 平均MAE=2.34 (n=17) / データ不足 17/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=88.0%, 平均MFE=8.35, 平均MAE=3.83 (n=25) / データ不足 25/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=80.0%, 平均MFE=6.69, 平均MAE=4.08 (n=5) / データ不足 5/30
- RISKY_ENTRY: 勝率=100.0%, 平均MFE=4.98, 平均MAE=2.19 (n=1) / データ不足 1/30
- SWEEP_WAIT: 勝率=88.9%, 平均MFE=8.44, 平均MAE=4.04 (n=18) / データ不足 18/30
- NO_TRADE_CANDIDATE: 勝率=100.0%, 平均MFE=18.44, 平均MAE=0.35 (n=1) / データ不足 1/30

### bias別件数・勝率
- long: 勝率=87.5% (n=24) / データ不足 24/30
- short: 勝率=100.0% (n=1) / データ不足 1/30

### bias別 direction 正誤
- long: correct=10, wrong=5, unclear=9 / wrong_rate=20.8% (n=24)
- short: correct=1, wrong=0, unclear=0 / wrong_rate=0.0% (n=1)

### 成績指標
- 全体勝率: 88.0%
- 平均MFE(signal_based): 8.35
- 平均MAE(signal_based): 3.83
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 88.0%

### 通知品質
- A: 通知して良かった = 22件
- B: 通知したが微妙 = 3件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- short_cover_risk: wrong_rate=28.6% (wrong=2/7)
- sweep_incomplete: wrong_rate=22.2% (wrong=4/18)
- orderbook_ask_heavy: wrong_rate=20.0% (wrong=2/10)
- lower_liquidity_close: wrong_rate=18.2% (wrong=4/22)
- ask_wall_close: wrong_rate=15.4% (wrong=2/13)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 12件
- ENTRY_OK + invalid: 1件
- countertrend_long_cluster: 10件

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

### risk_flags 有効性比較
- orderbook_ask_heavy: negative_rate=60.0% (n=10)
- lower_liquidity_close: negative_rate=59.1% (n=22)
- sweep_incomplete: negative_rate=55.6% (n=18)
- ask_wall_close: negative_rate=38.5% (n=13)
