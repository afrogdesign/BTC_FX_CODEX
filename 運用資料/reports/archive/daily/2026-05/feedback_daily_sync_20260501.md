# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 22 件です。近似PF は 1.19、全体勝率は 50.0% でした。
- 事後評価では「待つ判断に使えた」が最も多く、13 件でした。
- 平均の役立ち度は 3.53 / 5 でした。
- 根拠整合の入力率は 68.2%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「速報で方向/実行不整合が継続」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-04-24 22:05 〜 2026-04-30 01:05
- 総観測件数: 22
- データ品質の内訳: ok=22
- 近似PF: 1.19

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=14件, near_entry_zone_waiting_trigger=3件, entry_zone_not_reached=3件, inside_entry_zone_with_trigger=2件
- confidence_below_min 代表例: 20260426_040500(watch/SWEEP_WAIT, dir=45, exec=14, wait=90, MFE24h=24.76, MAE24h=0.00, outcome=win) / 20260426_090500(invalid/RISKY_ENTRY, dir=60, exec=24, wait=74, MFE24h=13.63, MAE24h=5.40, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 13件
- 価値が低かった: 2件
- 平均の役立ち度: 3.53 / 5
- 値動きの主因の入力率: 68.2%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 68.2% / 整合率: 100.0%
- SL評価: SL は妥当=10件, SL が狭すぎた=5件
- TP評価: TP は妥当=10件, TP が遠すぎた=4件, TP が近すぎた=1件
- 4時間足評価: 一部弱い=8件, 妥当=7件
- 1時間足評価: 一部弱い=14件, 妥当=1件
- 15分足評価: 妥当=7件, 一部弱い=3件, 弱い=5件
### 改善アクション
- 分類: 入口条件を調整=10件, 観測継続=2件, 通知文面を調整=1件, リスク設計を調整=2件
- 重要度: 中=9件, 低=2件, 高=4件
- 高優先の代表例:
  - 20260428_000500: 通知文面を調整 / 件名の「上方向バイアス」単独強調をやめ、15分足逆行優勢とWAIT理由を同列表示に修正する。
  - 20260426_200500: 入口条件を調整 / 15分足はレジスタンス帯内のロング発火を禁止し、下側流動性回収後の再奪回確認を必須条件にする。
  - 20260426_150500: 入口条件を調整 / 15分足で上側流動性スイープ完了を必須条件にして、逆張りショートの発火を後ろへずらす。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=213 / backlog=54 / AI済み=159 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-04-29T18:36:01.018803Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 4 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 4件
- 主な通知理由: attention_gap_crossed=2件, bias_changed=2件, attention_score_crossed=1件
- 代表例: 20260428_120500(bias_changed,confidence_jump, exec=38, wait=51) / 20260428_220500(attention_gap_crossed, exec=30, wait=40) / 20260428_000500(bias_changed, exec=27, wait=61)
- 現行watch再計算: 20260428_120500=>ready/inside_entry_zone_with_trigger/rr=4.91 / 20260428_220500=>watch/near_entry_zone_waiting_trigger/rr=1.30 / 20260428_000500=>watch/near_entry_zone_waiting_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=53.3%, 平均MFE=9.53, 平均MAE=5.07 (n=15) / データ不足 15/30
- transition: 勝率=42.9%, 平均MFE=5.30, 平均MAE=10.65 (n=7) / データ不足 7/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=50.0%, 平均MFE=8.18, 平均MAE=6.85 (n=22) / データ不足 22/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=100.0%, 平均MFE=9.38, 平均MAE=8.57 (n=2) / データ不足 2/30
- RISKY_ENTRY: 勝率=100.0%, 平均MFE=13.63, 平均MAE=5.40 (n=1) / データ不足 1/30
- SWEEP_WAIT: 勝率=38.5%, 平均MFE=7.08, 平均MAE=5.72 (n=13) / データ不足 13/30
- NO_TRADE_CANDIDATE: 勝率=50.0%, 平均MFE=9.26, 平均MAE=8.97 (n=6) / データ不足 6/30

### bias別件数・勝率
- long: 勝率=57.1% (n=14) / データ不足 14/30
- short: 勝率=37.5% (n=8) / データ不足 8/30

### bias別 direction 正誤
- long: correct=8, wrong=5, unclear=1 / wrong_rate=35.7% (n=14)
- short: correct=3, wrong=4, unclear=1 / wrong_rate=50.0% (n=8)

### 成績指標
- 全体勝率: 50.0%
- 平均MFE(signal_based): 8.18
- 平均MAE(signal_based): 6.85
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 50.0%

### 通知品質
- A: 通知して良かった = 11件
- B: 通知したが微妙 = 11件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- bid_wall_close: wrong_rate=60.0% (wrong=3/5)
- orderbook_bid_heavy: wrong_rate=50.0% (wrong=3/6)
- long_flush_exhaustion: wrong_rate=42.9% (wrong=3/7)
- upper_liquidity_close: wrong_rate=42.9% (wrong=3/7)
- sweep_incomplete: wrong_rate=42.1% (wrong=8/19)
- lower_liquidity_close: wrong_rate=36.4% (wrong=4/11)
- ask_wall_close: wrong_rate=16.7% (wrong=1/6)
- orderbook_ask_heavy: wrong_rate=14.3% (wrong=1/7)

### 直近12時間速報
- 対象件数: 12件
- direction_execution_conflict: 4件
- direction_execution_conflict の主な理由: confidence_below_min=4件
- direction_execution_conflict の主な risk_flags: sweep_incomplete=4件, upper_liquidity_close=4件, orderbook_bid_heavy=3件
- suppress_reason の内訳: confidence_below_short_min=9件, watch_sweep_recheck_wait=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 0件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 22
- 本有効件数: 0
- 参考ログ件数: 22
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 7件
- phase1_observation_gate=blocked: 15件
- 観測タイプ: setup_watch_learning=7件
- 観測候補全体: 7件 / 勝率=42.9% / TP1先行=42.9% / 近似PF=0.86 / 平均MFE=6.61 / 平均MAE=7.68
- setup_watch_learning: 7件 / 勝率=42.9% / TP1先行=42.9% / 近似PF=0.86 / 平均MFE=6.61 / 平均MAE=7.68
- 代表例: 20260429_160500, 20260429_100500, 20260428_220500, 20260428_120500, 20260428_000500
- 主な観測ブロック理由: confidence_below_min=14件, no_trade_candidate=6件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 7件
- 観測タイプ: setup_watch_learning=7件
- 状態: observing=7件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 28.6%
- 代表例: 20260429_160500, 20260429_100500, 20260428_220500, 20260428_120500, 20260428_000500
- 扱い: 実行候補ではなく、方向・待機条件・仮想SL/TPの検証ログ

### Phase 1B 昇格候補
- confidence_watch_learning 候補: 1件
- prelabel: SWEEP_WAIT=1件
- 勝率=0.0% / TP1先行=0.0% / 近似PF=0.12
- 平均 direction=58.0 / 平均 execution=22.0 / 平均 wait=76.8
- 平均MFE=0.67 / 平均MAE=5.38
- 代表例: 20260424_130500
- 扱い: `trade_execution_gate=pass` ではないが、限定条件付きで Phase 1B 候補へ昇格を検討する母集団

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 22件
- 主なブロック理由: phase1_inactive=22件, setup_not_ready=22件, wait_pressure_too_high=16件, execution_shadow_too_low=12件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 22件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 1/1件

### risk_flags 有効性比較
- lower_liquidity_close: negative_rate=72.7% (n=11)
- sweep_incomplete: negative_rate=68.4% (n=19)
