# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 33 件です。近似PF は 1.45、全体勝率は 60.6% でした。
- 事後評価では「待つ判断に使えた」が最も多く、15 件でした。
- 平均の役立ち度は 3.23 / 5 でした。
- 根拠整合の入力率は 66.7%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-21 18:05 〜 2026-04-27 08:05
- 総観測件数: 33
- データ品質の内訳: ok=33
- 近似PF: 1.45

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: entry_zone_not_reached=14件, confidence_below_min=8件, near_entry_zone_waiting_trigger=8件, inside_entry_zone_with_trigger=3件
- confidence_below_min 代表例: 20260426_040500(watch/SWEEP_WAIT, dir=45, exec=14, wait=90, MFE24h=24.76, MAE24h=0.00, outcome=win) / 20260426_090500(invalid/RISKY_ENTRY, dir=60, exec=24, wait=74, MFE24h=13.63, MAE24h=5.40, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 15件
- 価値が低かった: 2件
- 通知が遅すぎた: 2件
- 通知が早すぎた: 2件
- 見送り判断に使えた: 1件
- 平均の役立ち度: 3.23 / 5
- 値動きの主因の入力率: 66.7%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 66.7% / 整合率: 100.0%
- SL評価: SL が狭すぎた=9件, SL は妥当=13件
- TP評価: TP は妥当=14件, TP が近すぎた=4件, TP が遠すぎた=4件
- 4時間足評価: 一部弱い=11件, 妥当=11件
- 1時間足評価: 一部弱い=18件, 妥当=3件, 弱い=1件
- 15分足評価: 弱い=11件, 妥当=7件, 一部弱い=4件
### 改善アクション
- 分類: 入口条件を調整=16件, リスク設計を調整=1件, 通知文面を調整=3件, 観測継続=2件
- 重要度: 高=12件, 中=8件, 低=2件
- 高優先の代表例:
  - 20260426_150500: 入口条件を調整 / 15分足で上側流動性スイープ完了を必須条件にして、逆張りショートの発火を後ろへずらす。
  - 20260426_050500: 入口条件を調整 / 15分足で抵抗上抜け後の継続型エントリー条件を追加し、押し目未到達でも取り逃しを減らす。
  - 20260423_180500: 入口条件を調整 / 15分足で流動性回収後に見送りから執行へ切り替える再エントリー条件を明確化する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=202 / backlog=51 / AI済み=151 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-04-27T18:36:41.077213Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 11/22 件 (50.0%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. SL が狭すぎるケースが多い
   理由: sl_eval=too_tight が 9/22 件 (40.9%)
   主に触る場所: src/analysis/rr.py
3. NO_TRADE_CANDIDATE が強すぎる
   理由: skip_too_strict が 4/11 件 (36.4%)
   主に触る場所: config.py, src/analysis/position_risk.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 9件
- 主な通知理由: prelabel_improved=8件, status_upgraded=8件, confidence_jump=4件
- 代表例: 20260422_050500(confidence_jump,prelabel_improved, exec=35, wait=24) / 20260423_100500(confidence_jump,prelabel_improved, exec=35, wait=32) / 20260422_090501(prelabel_improved,status_upgraded, exec=28, wait=35)
- 現行watch再計算: 20260422_050500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260423_100500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260422_090501=>watch/entry_zone_not_reached/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=61.5%, 平均MFE=11.12, 平均MAE=5.57 (n=13) / データ不足 13/30
- transition: 勝率=100.0%, 平均MFE=9.94, 平均MAE=0.81 (n=3) / データ不足 3/30
- uptrend: 勝率=52.9%, 平均MFE=3.29, 平均MAE=4.92 (n=17) / データ不足 17/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=60.6%, 平均MFE=6.98, 平均MAE=4.81 (n=33)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=12.55, 平均MAE=4.47 (n=2) / データ不足 2/30
- RISKY_ENTRY: 勝率=100.0%, 平均MFE=6.59, 平均MAE=3.85 (n=5) / データ不足 5/30
- SWEEP_WAIT: 勝率=40.0%, 平均MFE=6.01, 平均MAE=4.88 (n=15) / データ不足 15/30
- NO_TRADE_CANDIDATE: 勝率=63.6%, 平均MFE=7.47, 平均MAE=5.19 (n=11) / データ不足 11/30

### bias別件数・勝率
- long: 勝率=62.5% (n=32)
- short: 勝率=0.0% (n=1) / データ不足 1/30

### bias別 direction 正誤
- long: correct=15, wrong=14, unclear=3 / wrong_rate=43.8% (n=32)
- short: correct=0, wrong=1, unclear=0 / wrong_rate=100.0% (n=1)

### 成績指標
- 全体勝率: 60.6%
- 平均MFE(signal_based): 6.98
- 平均MAE(signal_based): 4.81
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 60.6%

### 通知品質
- A: 通知して良かった = 20件
- B: 通知したが微妙 = 13件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- cvd_bearish_divergence: wrong_rate=57.1% (wrong=4/7)
- lower_liquidity_close: wrong_rate=48.0% (wrong=12/25)
- sweep_incomplete: wrong_rate=44.0% (wrong=11/25)
- short_cover_risk: wrong_rate=42.9% (wrong=3/7)
- orderbook_ask_heavy: wrong_rate=38.9% (wrong=7/18)
- long_flush_exhaustion: wrong_rate=28.6% (wrong=2/7)
- ask_wall_close: wrong_rate=20.0% (wrong=3/15)

### 直近12時間速報
- 対象件数: 10件
- direction_execution_conflict: 3件
- direction_execution_conflict の主な理由: confidence_below_min=3件
- direction_execution_conflict の主な risk_flags: sweep_incomplete=3件, cvd_bearish_divergence=2件, orderbook_bid_heavy=2件
- suppress_reason の内訳: bias_wait=5件, confidence_below_long_min=2件, confidence_below_short_min=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 3件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 33
- 本有効件数: 0
- 参考ログ件数: 33
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 11件
- phase1_observation_gate=blocked: 22件
- 観測タイプ: setup_watch_learning=11件
- 観測候補全体: 11件 / 勝率=72.7% / TP1先行=72.7% / 近似PF=1.48 / 平均MFE=6.16 / 平均MAE=4.17
- setup_watch_learning: 11件 / 勝率=72.7% / TP1先行=72.7% / 近似PF=1.48 / 平均MFE=6.16 / 平均MAE=4.17
- 代表例: 20260426_050500, 20260425_160500, 20260423_150500, 20260423_100500, 20260422_230500
- 主な観測ブロック理由: no_trade_candidate=11件, confidence_below_min=8件, watch_conditions_not_met=6件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 11件
- 観測タイプ: setup_watch_learning=11件
- 状態: observing=11件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 63.6%
- 代表例: 20260426_050500, 20260425_160500, 20260423_150500, 20260423_100500, 20260422_230500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 33件
- 主なブロック理由: phase1_inactive=33件, setup_not_ready=33件, execution_shadow_too_low=20件, wait_pressure_too_high=16件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 33件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 4/4件

### risk_flags 有効性比較
- lower_liquidity_close: negative_rate=80.0% (n=25)
- orderbook_ask_heavy: negative_rate=72.2% (n=18)
- sweep_incomplete: negative_rate=72.0% (n=25)
- ask_wall_close: negative_rate=60.0% (n=15)
