# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 21 件です。近似PF は 0.78、全体勝率は 61.9% でした。
- 事後評価では「待つ判断に使えた」が最も多く、10 件でした。
- 平均の役立ち度は 3.67 / 5 でした。
- 根拠整合の入力率は 61.9%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「ENTRY_OK が甘め」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-06 18:05 〜 2026-05-12 01:05
- 総観測件数: 21
- データ品質の内訳: ok=21
- 近似PF: 0.78

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=9件, entry_zone_not_reached=6件, near_entry_zone_waiting_trigger=4件, inside_entry_zone_with_trigger=2件
- confidence_below_min 代表例: 20260509_120501(watch/SWEEP_WAIT, dir=55, exec=21, wait=62, MFE24h=8.90, MAE24h=1.46, outcome=win) / 20260510_220500(watch/SWEEP_WAIT, dir=68, exec=12, wait=93, MFE24h=8.49, MAE24h=1.24, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 10件
- 見送り判断に使えた: 4件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.67 / 5
- 値動きの主因の入力率: 71.4%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 61.9% / 整合率: 100.0%
- SL評価: SL が狭すぎた=4件, SL は妥当=11件
- TP評価: TP は妥当=9件, TP が近すぎた=1件, TP が遠すぎた=5件
- 4時間足評価: 一部弱い=9件, 妥当=5件, 弱い=1件
- 1時間足評価: 一部弱い=12件, 妥当=3件
- 15分足評価: 弱い=5件, 妥当=7件, 一部弱い=3件
### 改善アクション
- 分類: 通知文面を調整=5件, 入口条件を調整=8件, 観測継続=2件
- 重要度: 高=5件, 中=10件
- 高優先の代表例:
  - 20260510_160500: 通知文面を調整 / WATCH通知では件名・本文からENTRY_OK連想を外し、未成立（価格到達待ち）を先頭固定で明記する。
  - 20260507_130500: 通知文面を調整 / 方向バイアス強調より先に「執行不可（WAIT）」を件名冒頭へ固定し、ENTRY_OK表現を監視専用文言に置換する。
  - 20260507_090500: 通知文面を調整 / 「高め本通知」でも執行不可の監視局面は件名先頭に「エントリー非推奨（待機）」を固定表示する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=261 / backlog=54 / AI済み=207 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-05-11T18:35:59.435758Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. ENTRY_OK が甘め
   理由: ENTRY_OK の poor_entry が 3/4 件 (75.0%)
   主に触る場所: config.py, src/analysis/position_risk.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 1件
- 主な通知理由: bias_changed=1件, confidence_jump=1件
- 代表例: 20260510_190500(bias_changed,confidence_jump, exec=34, wait=58)
- 現行watch再計算: 20260510_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=90.9%, 平均MFE=6.81, 平均MAE=3.31 (n=11) / データ不足 11/30
- transition: 勝率=33.3%, 平均MFE=2.90, 平均MAE=6.90 (n=3) / データ不足 3/30
- uptrend: 勝率=28.6%, 平均MFE=2.13, 平均MAE=9.87 (n=7) / データ不足 7/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=61.9%, 平均MFE=4.69, 平均MAE=6.01 (n=21) / データ不足 21/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=75.0%, 平均MFE=4.01, 平均MAE=7.84 (n=4) / データ不足 4/30
- RISKY_ENTRY: 勝率=0.0%, 平均MFE=4.03, 平均MAE=9.11 (n=4) / データ不足 4/30
- SWEEP_WAIT: 勝率=100.0%, 平均MFE=5.98, 平均MAE=4.19 (n=6) / データ不足 6/30
- NO_TRADE_CANDIDATE: 勝率=57.1%, 平均MFE=4.36, 平均MAE=4.75 (n=7) / データ不足 7/30

### bias別件数・勝率
- long: 勝率=61.9% (n=21) / データ不足 21/30

### bias別 direction 正誤
- long: correct=11, wrong=8, unclear=2 / wrong_rate=38.1% (n=21)

### 成績指標
- 全体勝率: 61.9%
- 平均MFE(signal_based): 4.69
- 平均MAE(signal_based): 6.01
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 61.9%

### 通知品質
- A: 通知して良かった = 13件
- B: 通知したが微妙 = 8件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- orderbook_ask_heavy: wrong_rate=42.9% (wrong=3/7)
- ask_wall_close: wrong_rate=40.0% (wrong=4/10)
- sweep_incomplete: wrong_rate=36.4% (wrong=4/11)
- lower_liquidity_close: wrong_rate=31.2% (wrong=5/16)
- short_cover_risk: wrong_rate=14.3% (wrong=1/7)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 0件
- suppress_reason の内訳: bias_wait=3件, confidence_below_long_min=3件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 7件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 21
- 本有効件数: 0
- 参考ログ件数: 21
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 10件
- phase1_observation_gate=blocked: 11件
- 観測タイプ: setup_watch_learning=9件, confidence_watch_learning=1件
- 観測候補全体: 10件 / 勝率=50.0% / TP1先行=50.0% / 近似PF=0.52 / 平均MFE=4.34 / 平均MAE=8.36
- setup_watch_learning: 9件 / 勝率=44.4% / TP1先行=44.4% / 近似PF=0.47 / 平均MFE=4.05 / 平均MAE=8.68
- confidence_watch_learning: 1件 / 勝率=100.0% / TP1先行=100.0% / 近似PF=1.26 / 平均MFE=6.95 / 平均MAE=5.50
- 代表例: 20260511_160500, 20260511_120500, 20260510_190500, 20260510_160500, 20260509_212745
- 主な観測ブロック理由: confidence_below_min=8件, no_trade_candidate=7件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 10件
- 観測タイプ: setup_watch_learning=9件, confidence_watch_learning=1件
- 状態: observing=10件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 55.6%
- 代表例: 20260511_160500, 20260511_120500, 20260510_190500, 20260510_160500, 20260509_212745
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### Phase 1B 昇格候補
- confidence_watch_learning 候補: 1件
- prelabel: SWEEP_WAIT=1件
- 勝率=100.0% / TP1先行=100.0% / 近似PF=1.26
- 平均 direction=60.0 / 平均 execution=22.0 / 平均 wait=76.8
- 平均MFE=6.95 / 平均MAE=5.50
- 代表例: 20260509_212745
- 扱い: `trade_execution_gate=pass` ではないが、限定条件付きで Phase 1B 候補へ昇格を検討する母集団

### counter_long_short_watch
- 候補件数: 0件
- 扱い: ロング監視の失敗初動をショート観測候補として切り出す Phase 1A 母集団

### failed_breakout_down_reversal
- 件数: 0件
- 扱い: breakout_up が効かず大きく下落した watch 群の失敗型を継続追跡する

### market_map
- 記録あり: 0件
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 21件
- 主なブロック理由: phase1_inactive=21件, setup_not_ready=21件, wait_pressure_too_high=11件, execution_shadow_too_low=9件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 21件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 1/1件

### risk_flags 有効性比較
- sweep_incomplete: negative_rate=81.8% (n=11)
- lower_liquidity_close: negative_rate=75.0% (n=16)
- ask_wall_close: negative_rate=70.0% (n=10)
