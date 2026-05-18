# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 39 件です。近似PF は 0.68、全体勝率は 59.0% でした。
- 事後評価では「待つ判断に使えた」が最も多く、14 件でした。
- 平均の役立ち度は 3.30 / 5 でした。
- 根拠整合の入力率は 51.3%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-18 12:05 〜 2026-04-24 01:05
- 総観測件数: 39
- データ品質の内訳: ok=39
- 近似PF: 0.68

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: entry_zone_not_reached=17件, confidence_below_min=11件, near_entry_zone_waiting_trigger=8件, inside_entry_zone_with_trigger=3件
- confidence_below_min 代表例: 20260421_080500(invalid/NO_TRADE_CANDIDATE, dir=61, exec=5, wait=100, MFE24h=12.70, MAE24h=6.78, outcome=win) / 20260418_030500(invalid/NO_TRADE_CANDIDATE, dir=60, exec=14, wait=74, MFE24h=10.80, MAE24h=0.00, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 14件
- 通知が早すぎた: 2件
- 価値が低かった: 2件
- 通知が遅すぎた: 1件
- 見送り判断に使えた: 1件
- 平均の役立ち度: 3.30 / 5
- 値動きの主因の入力率: 51.3%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 51.3% / 整合率: 100.0%
- SL評価: SL が狭すぎた=4件, SL は妥当=16件
- TP評価: TP は妥当=12件, TP が近すぎた=3件, TP が遠すぎた=5件
- 4時間足評価: 妥当=7件, 一部弱い=11件, 弱い=2件
- 1時間足評価: 一部弱い=19件, 妥当=1件
- 15分足評価: 弱い=8件, 一部弱い=5件, 妥当=7件
### 改善アクション
- 分類: 入口条件を調整=13件, 通知文面を調整=4件, 観測継続=3件
- 重要度: 高=9件, 中=11件
- 高優先の代表例:
  - 20260422_140500: 入口条件を調整 / 15分足は再検討帯未到達時にロング成立扱いを外し、通知文面も「待機専用」を先頭固定にする。
  - 20260422_080500: 入口条件を調整 / 15分足で再検討帯未到達でも、抵抗帯再奪回＋出来高増加時に追随エントリーを許可する分岐を追加する。
  - 20260421_110500: 入口条件を調整 / 15分足で下側流動性回収完了と反発確定を満たすまで通知ランクを監視止まりに固定する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=190 / backlog=55 / AI済み=135 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-04-23T18:36:55.050080Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 8/20 件 (40.0%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. NO_TRADE_CANDIDATE が強すぎる
   理由: skip_too_strict が 4/11 件 (36.4%)
   主に触る場所: config.py, src/analysis/position_risk.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 3 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 14件
- 主な通知理由: prelabel_improved=12件, status_upgraded=9件, confidence_jump=6件
- 代表例: 20260418_090500(prelabel_improved,status_upgraded, exec=37, wait=69) / 20260422_050500(confidence_jump,prelabel_improved, exec=35, wait=24) / 20260423_100500(confidence_jump,prelabel_improved, exec=35, wait=32)
- 現行watch再計算: 20260418_090500=>watch/entry_zone_not_reached/rr=1.54 / 20260422_050500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260423_100500=>watch/near_entry_zone_waiting_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=61.1%, 平均MFE=4.30, 平均MAE=7.35 (n=18) / データ不足 18/30
- transition: 勝率=80.0%, 平均MFE=6.50, 平均MAE=4.80 (n=5) / データ不足 5/30
- uptrend: 勝率=50.0%, 平均MFE=3.35, 平均MAE=5.17 (n=16) / データ不足 16/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=59.0%, 平均MFE=4.19, 平均MAE=6.13 (n=39)

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=4.77, 平均MAE=6.57 (n=2) / データ不足 2/30
- RISKY_ENTRY: 勝率=75.0%, 平均MFE=3.57, 平均MAE=5.39 (n=8) / データ不足 8/30
- SWEEP_WAIT: 勝率=44.4%, 平均MFE=3.67, 平均MAE=6.79 (n=18) / データ不足 18/30
- NO_TRADE_CANDIDATE: 勝率=63.6%, 平均MFE=5.39, 平均MAE=5.50 (n=11) / データ不足 11/30

### bias別件数・勝率
- long: 勝率=58.3% (n=36)
- short: 勝率=66.7% (n=3) / データ不足 3/30

### bias別 direction 正誤
- long: correct=11, wrong=20, unclear=5 / wrong_rate=55.6% (n=36)
- short: correct=1, wrong=2, unclear=0 / wrong_rate=66.7% (n=3)

### 成績指標
- 全体勝率: 59.0%
- 平均MFE(signal_based): 4.19
- 平均MAE(signal_based): 6.13
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 59.0%

### 通知品質
- A: 通知して良かった = 23件
- B: 通知したが微妙 = 16件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- short_cover_risk: wrong_rate=71.4% (wrong=5/7)
- long_flush_exhaustion: wrong_rate=66.7% (wrong=6/9)
- cvd_bearish_divergence: wrong_rate=66.7% (wrong=4/6)
- orderbook_ask_heavy: wrong_rate=60.0% (wrong=12/20)
- lower_liquidity_close: wrong_rate=56.7% (wrong=17/30)
- sweep_incomplete: wrong_rate=56.7% (wrong=17/30)
- ask_wall_close: wrong_rate=30.8% (wrong=4/13)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 3件
- direction_execution_conflict の主な理由: confidence_below_min=3件
- direction_execution_conflict の主な risk_flags: lower_liquidity_close=3件, sweep_incomplete=3件, orderbook_ask_heavy=2件
- suppress_reason の内訳: confidence_below_long_min=10件, bias_wait=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 10件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 39
- 本有効件数: 0
- 参考ログ件数: 39
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 15件
- phase1_observation_gate=blocked: 24件
- 観測タイプ: setup_watch_learning=15件
- 観測候補全体: 15件 / 勝率=73.3% / TP1先行=73.3% / 近似PF=0.59 / 平均MFE=3.47 / 平均MAE=5.93
- setup_watch_learning: 15件 / 勝率=73.3% / TP1先行=73.3% / 近似PF=0.59 / 平均MFE=3.47 / 平均MAE=5.93
- 代表例: 20260423_150500, 20260423_100500, 20260422_230500, 20260422_210500, 20260422_140500
- 主な観測ブロック理由: no_trade_candidate=11件, confidence_below_min=11件, watch_conditions_not_met=7件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 15件
- 観測タイプ: setup_watch_learning=15件
- 状態: observing=15件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 66.7%
- 代表例: 20260423_150500, 20260423_100500, 20260422_230500, 20260422_210500, 20260422_140500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 39件
- 主なブロック理由: phase1_inactive=39件, setup_not_ready=39件, execution_shadow_too_low=20件, wait_pressure_too_high=19件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 39件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 3/3件

### risk_flags 有効性比較
- lower_liquidity_close: negative_rate=80.0% (n=30)
- sweep_incomplete: negative_rate=80.0% (n=30)
- orderbook_ask_heavy: negative_rate=80.0% (n=20)
- ask_wall_close: negative_rate=53.8% (n=13)
