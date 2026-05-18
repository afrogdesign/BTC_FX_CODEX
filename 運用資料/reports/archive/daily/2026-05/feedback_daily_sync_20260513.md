# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 25 件です。近似PF は 0.66、全体勝率は 48.0% でした。
- 事後評価では「待つ判断に使えた」が最も多く、13 件でした。
- 平均の役立ち度は 3.72 / 5 でした。
- 根拠整合の入力率は 64.0%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「TP が遠すぎるケースが多い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-07 00:05 〜 2026-05-12 22:05
- 総観測件数: 25
- データ品質の内訳: ok=25
- 近似PF: 0.66

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=11件, entry_zone_not_reached=6件, near_entry_zone_waiting_trigger=5件, inside_entry_zone_with_trigger=3件
- confidence_below_min 代表例: 20260509_120501(watch/SWEEP_WAIT, dir=55, exec=21, wait=62, MFE24h=8.90, MAE24h=1.46, outcome=win) / 20260510_220500(watch/SWEEP_WAIT, dir=68, exec=12, wait=93, MFE24h=8.49, MAE24h=1.24, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 13件
- 見送り判断に使えた: 4件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.72 / 5
- 値動きの主因の入力率: 72.0%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 64.0% / 整合率: 100.0%
- SL評価: SL は妥当=14件, SL が狭すぎた=4件
- TP評価: TP が遠すぎた=9件, TP は妥当=8件, TP が近すぎた=1件
- 4時間足評価: 妥当=8件, 一部弱い=9件, 弱い=1件
- 1時間足評価: 一部弱い=15件, 妥当=3件
- 15分足評価: 弱い=8件, 妥当=7件, 一部弱い=3件
### 改善アクション
- 分類: 出口設計を調整=4件, 通知文面を調整=4件, 入口条件を調整=8件, 観測継続=2件
- 重要度: 中=14件, 高=4件
- 高優先の代表例:
  - 20260510_160500: 通知文面を調整 / WATCH通知では件名・本文からENTRY_OK連想を外し、未成立（価格到達待ち）を先頭固定で明記する。
  - 20260507_130500: 通知文面を調整 / 方向バイアス強調より先に「執行不可（WAIT）」を件名冒頭へ固定し、ENTRY_OK表現を監視専用文言に置換する。
  - 20260507_090500: 通知文面を調整 / 「高め本通知」でも執行不可の監視局面は件名先頭に「エントリー非推奨（待機）」を固定表示する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=266 / backlog=55 / AI済み=211 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-05-12T18:38:37.780706Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. TP が遠すぎるケースが多い
   理由: tp_eval=too_far が 9/18 件 (50.0%)
   主に触る場所: src/analysis/rr.py, src/trade/exit_manager.py
2. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 8/18 件 (44.4%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
3. 速報で方向/実行不整合が継続
   理由: 直近12時間で direction_execution_conflict が 2 件あります
   主に触る場所: tools/log_feedback.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 1件
- 主な通知理由: bias_changed=1件, confidence_jump=1件
- 代表例: 20260510_190500(bias_changed,confidence_jump, exec=34, wait=58)
- 現行watch再計算: 20260510_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=76.9%, 平均MFE=6.22, 平均MAE=3.83 (n=13) / データ不足 13/30
- transition: 勝率=33.3%, 平均MFE=2.90, 平均MAE=6.90 (n=3) / データ不足 3/30
- uptrend: 勝率=11.1%, 平均MFE=1.50, 平均MAE=9.61 (n=9) / データ不足 9/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=48.0%, 平均MFE=4.12, 平均MAE=6.28 (n=25) / データ不足 25/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=66.7%, 平均MFE=3.77, 平均MAE=8.39 (n=3) / データ不足 3/30
- RISKY_ENTRY: 勝率=0.0%, 平均MFE=3.23, 平均MAE=8.56 (n=6) / データ不足 6/30
- SWEEP_WAIT: 勝率=85.7%, 平均MFE=5.53, 平均MAE=4.56 (n=7) / データ不足 7/30
- NO_TRADE_CANDIDATE: 勝率=44.4%, 平均MFE=3.75, 平均MAE=5.38 (n=9) / データ不足 9/30

### bias別件数・勝率
- long: 勝率=48.0% (n=25) / データ不足 25/30

### bias別 direction 正誤
- long: correct=11, wrong=13, unclear=1 / wrong_rate=52.0% (n=25)

### 成績指標
- 全体勝率: 48.0%
- 平均MFE(signal_based): 4.12
- 平均MAE(signal_based): 6.28
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 48.0%

### 通知品質
- A: 通知して良かった = 12件
- B: 通知したが微妙 = 13件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- orderbook_ask_heavy: wrong_rate=62.5% (wrong=5/8)
- ask_wall_close: wrong_rate=53.8% (wrong=7/13)
- sweep_incomplete: wrong_rate=50.0% (wrong=7/14)
- lower_liquidity_close: wrong_rate=47.6% (wrong=10/21)
- short_cover_risk: wrong_rate=16.7% (wrong=1/6)

### 直近12時間速報
- 対象件数: 10件
- direction_execution_conflict: 2件
- direction_execution_conflict の主な理由: entry_zone_not_reached=1件, confidence_below_min=1件
- direction_execution_conflict の主な risk_flags: short_cover_risk=2件, short_into_major_support=2件, long_into_major_resistance=2件
- suppress_reason の内訳: confidence_below_long_min=4件, attention_cooldown_active=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 6件

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
- phase1_observation_gate=pass: 11件
- phase1_observation_gate=blocked: 14件
- 観測タイプ: setup_watch_learning=10件, confidence_watch_learning=1件
- 観測候補全体: 11件 / 勝率=36.4% / TP1先行=36.4% / 近似PF=0.45 / 平均MFE=3.80 / 平均MAE=8.40
- setup_watch_learning: 10件 / 勝率=30.0% / TP1先行=30.0% / 近似PF=0.40 / 平均MFE=3.49 / 平均MAE=8.69
- confidence_watch_learning: 1件 / 勝率=100.0% / TP1先行=100.0% / 近似PF=1.26 / 平均MFE=6.95 / 平均MAE=5.50
- 代表例: 20260512_070501, 20260512_040500, 20260511_160500, 20260511_120500, 20260510_190500
- 主な観測ブロック理由: confidence_below_min=10件, no_trade_candidate=9件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 11件
- 観測タイプ: setup_watch_learning=10件, confidence_watch_learning=1件
- 状態: observing=11件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 40.0%
- 代表例: 20260512_070501, 20260512_040500, 20260511_160500, 20260511_120500, 20260510_190500
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
- trade_execution_gate=blocked: 25件
- 主なブロック理由: phase1_inactive=25件, setup_not_ready=25件, wait_pressure_too_high=14件, execution_shadow_too_low=12件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 25件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 1/1件

### risk_flags 有効性比較
- sweep_incomplete: negative_rate=85.7% (n=14)
- lower_liquidity_close: negative_rate=81.0% (n=21)
- ask_wall_close: negative_rate=76.9% (n=13)
