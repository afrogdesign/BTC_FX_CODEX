# フィードバック分析レポート (weekly)

## 1. まず結論
- 今回の完了データは 29 件です。近似PF は 0.81、全体勝率は 51.7% でした。
- 事後評価では「待つ判断に使えた」が最も多く、15 件でした。
- 平均の役立ち度は 3.67 / 5 でした。
- 根拠整合の入力率は 58.6%、整合した比率は 100.0% でした。
- 今回の改善候補の最上位は「15分足の執行価格精度が弱い」です。
- Phase 1 判定では ready=0 件、phase1_active=true=0 件です。
- 判定: Phase 1 の本有効待ち (ready / phase1_active ともに未検出のため、通知観測を継続する)

## 2. 今回の対象
- 集計期間: 2026-05-07 17:05 〜 2026-05-13 14:05
- 総観測件数: 29
- データ品質の内訳: ok=29
- 近似PF: 0.81

## 3. Phase 1 判定サマリー
- `primary_setup_status=ready` 件数: 0
- `phase1_active=true` 件数: 0
- 判定: Phase 1 の本有効待ち
- 補足: ready / phase1_active ともに未検出のため、通知観測を継続する
- TP1 到達率: 0.0%
- `tp1_hit_first=false` 率: 0.0%
- `expired` 率: 0.0%
- `max_size_capped` 発生率: 0.0%
- ready阻害理由: confidence_below_min=18件, entry_zone_not_reached=7件, inside_entry_zone_with_trigger=2件, near_entry_zone_waiting_trigger=2件
- confidence_below_min 代表例: 20260512_210500(watch/SWEEP_WAIT, dir=56, exec=23, wait=59, MFE24h=11.27, MAE24h=3.61, outcome=win) / 20260512_190501(watch/SWEEP_WAIT, dir=75, exec=18, wait=75, MFE24h=9.15, MAE24h=3.02, outcome=win)

## 4. 人のレビュー要約 / AI事後評価
- 待つ判断に使えた: 15件
- 見送り判断に使えた: 2件
- 通知が早すぎた: 1件
- 平均の役立ち度: 3.67 / 5
- 値動きの主因の入力率: 62.1%
- エントリー寄り誤読の入力率: 0.0% / 誤読あり率: 0.0%
- 根拠整合の入力率: 58.6% / 整合率: 100.0%
- SL評価: SL が狭すぎた=6件, SL は妥当=12件
- TP評価: TP は妥当=10件, TP が遠すぎた=7件, TP が近すぎた=1件
- 4時間足評価: 一部弱い=8件, 妥当=9件, 弱い=1件
- 1時間足評価: 一部弱い=17件, 妥当=1件
- 15分足評価: 弱い=10件, 一部弱い=4件, 妥当=4件
### 改善アクション
- 分類: 入口条件を調整=11件, 出口設計を調整=4件, 通知文面を調整=3件
- 重要度: 高=4件, 中=14件
- 高優先の代表例:
  - 20260512_170500: 入口条件を調整 / 15分足で再検討帯到達後の反転確認（高値切り下げ＋出来高維持）を発火条件に追加し、到達だけで監視強度を上げない。
  - 20260510_160500: 通知文面を調整 / WATCH通知では件名・本文からENTRY_OK連想を外し、未成立（価格到達待ち）を先頭固定で明記する。
  - 20260507_130500: 通知文面を調整 / 方向バイアス強調より先に「執行不可（WAIT）」を件名冒頭へ固定し、ENTRY_OK表現を監視専用文言に置換する。
### AI事後評価 health
- 状態: backlogあり
- 候補件数: eligible=274 / backlog=59 / AI済み=215 / human_override=0
- 今回の同期: created=4 / reused=0 / request_failed=0 / daily_cap=4
- 最終AI評価: 2026-05-13T18:36:12.834674Z / 最終エラー: 2026-04-19T18:40:01.705120Z

## 5. 改善候補
1. 15分足の執行価格精度が弱い
   理由: tf_15m_eval=poor が 10/18 件 (55.6%)
   主に触る場所: src/analysis/rr.py, src/notification/detail_page.py
2. TP が遠すぎるケースが多い
   理由: tp_eval=too_far が 7/18 件 (38.9%)
   主に触る場所: src/analysis/rr.py, src/trade/exit_manager.py
3. SWEEP_WAIT が厳しめ
   理由: wait_too_strict が 4/10 件 (40.0%)
   主に触る場所: src/analysis/position_risk.py

補助集計:
- sweep_incomplete を含む watch 系通知済み履歴: 1件
- 主な通知理由: bias_changed=1件, confidence_jump=1件
- 代表例: 20260510_190500(bias_changed,confidence_jump, exec=34, wait=58)
- 現行watch再計算: 20260510_190500=>watch/near_entry_zone_waiting_trigger/rr=1.30

## 6. 技術集計

### regime別件数・勝率・平均MFE・平均MAE
- range: 勝率=66.7%, 平均MFE=6.22, 平均MAE=5.07 (n=21) / データ不足 21/30
- transition: 勝率=33.3%, 平均MFE=2.90, 平均MAE=6.90 (n=3) / データ不足 3/30
- uptrend: 勝率=0.0%, 平均MFE=0.66, 平均MAE=9.71 (n=5) / データ不足 5/30

### signal_tier別件数・勝率・平均MFE・平均MAE
- normal: 勝率=51.7%, 平均MFE=4.92, 平均MAE=6.06 (n=29) / データ不足 29/30

### prelabel別件数・勝率・平均MFE・平均MAE
- ENTRY_OK: 勝率=50.0%, 平均MFE=4.09, 平均MAE=7.61 (n=4) / データ不足 4/30
- RISKY_ENTRY: 勝率=0.0%, 平均MFE=3.09, 平均MAE=8.72 (n=7) / データ不足 7/30
- SWEEP_WAIT: 勝率=90.0%, 平均MFE=6.22, 平均MAE=4.87 (n=10) / データ不足 10/30
- NO_TRADE_CANDIDATE: 勝率=50.0%, 平均MFE=5.30, 平均MAE=4.44 (n=8) / データ不足 8/30

### bias別件数・勝率
- long: 勝率=52.0% (n=25) / データ不足 25/30
- short: 勝率=50.0% (n=4) / データ不足 4/30

### bias別 direction 正誤
- long: correct=13, wrong=11, unclear=1 / wrong_rate=44.0% (n=25)
- short: correct=0, wrong=3, unclear=1 / wrong_rate=75.0% (n=4)

### 成績指標
- 全体勝率: 51.7%
- 平均MFE(signal_based): 4.92
- 平均MAE(signal_based): 6.06
- 平均MFE(entry_ready_based): 0.00
- 平均MAE(entry_ready_based): 0.00
- TP1先行率: 51.7%

### 通知品質
- A: 通知して良かった = 15件
- B: 通知したが微妙 = 14件
- C: 通知しなかったが本当は良かった = 0件
- D: 通知しなかったので正解 = 0件

### risk flag 群別 wrong rate
- orderbook_ask_heavy: wrong_rate=57.1% (wrong=4/7)
- sweep_incomplete: wrong_rate=45.0% (wrong=9/20)
- lower_liquidity_close: wrong_rate=42.9% (wrong=9/21)
- ask_wall_close: wrong_rate=41.7% (wrong=5/12)
- short_into_major_support: wrong_rate=40.0% (wrong=2/5)
- long_into_major_resistance: wrong_rate=40.0% (wrong=2/5)
- short_cover_risk: wrong_rate=16.7% (wrong=1/6)

### 直近12時間速報
- 対象件数: 10件
- direction_execution_conflict: 1件
- direction_execution_conflict の主な理由: near_entry_zone_waiting_trigger=1件
- direction_execution_conflict の主な risk_flags: bid_wall_close=1件, long_flush_exhaustion=1件, sweep_incomplete=1件
- suppress_reason の内訳: watch_sweep_recheck_wait=3件, confidence_below_short_min=2件, bias_wait=1件
- ENTRY_OK + invalid: 0件
- countertrend_long_cluster: 0件

### Phase 1 計画ログ
- Phase 1 計画付き件数: 29
- 本有効件数: 0
- 参考ログ件数: 29
- 平均 risk_percent_applied: 0.00
- 連敗時平均 risk_percent_applied: 0.00
- 平均 planned_risk_usd: 0.00
- 平均 position_size_usd: 0.00
- 平均 loss_streak_at_entry: 0.00
- max_size_capped 発生率: 0.0%
- 平均 timeout_hours: 0.00

### Phase 1 観測 gate
- phase1_observation_gate=pass: 10件
- phase1_observation_gate=blocked: 19件
- 観測タイプ: setup_watch_learning=9件, confidence_watch_learning=1件
- 観測候補全体: 10件 / 勝率=30.0% / TP1先行=30.0% / 近似PF=0.55 / 平均MFE=4.10 / 平均MAE=7.45
- setup_watch_learning: 9件 / 勝率=22.2% / TP1先行=22.2% / 近似PF=0.49 / 平均MFE=3.79 / 平均MAE=7.66
- confidence_watch_learning: 1件 / 勝率=100.0% / TP1先行=100.0% / 近似PF=1.26 / 平均MFE=6.95 / 平均MAE=5.50
- 代表例: 20260512_170500, 20260512_070501, 20260512_040500, 20260511_160500, 20260511_120500
- 主な観測ブロック理由: confidence_below_min=17件, no_trade_candidate=8件

### Phase 1A 観測紙トレード
- observation_paper_orders observing: 10件
- 観測タイプ: setup_watch_learning=9件, confidence_watch_learning=1件
- 状態: observing=10件
- gate pass だが観測紙トレード未記録: 0件
- setup_watch_learning の entry_zone_not_reached 率: 55.6%
- 代表例: 20260512_170500, 20260512_070501, 20260512_040500, 20260511_160500, 20260511_120500
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
- 記録あり: 5件
- primary_state: confirmed_down=3件, confirmed_up=1件, early_up=1件
- flags: long_into_major_resistance=5件, short_into_major_support=5件, support_to_resistance_flip=3件, support_to_resistance_retest_confirmed=3件, trend_flip_confirmed_down=3件, resistance_to_support_flip=2件, resistance_to_support_retest_confirmed=2件, failed_breakout_down_reversal=2件
- trend_state: confirmed_down=3件, confirmed_up=1件, early_up=1件
- 下方向反転系: 3件 / 勝率=66.7% / wrong_rate=66.7%
- 下方向反転系 平均MFE24h=11.15 / 平均MAE24h=2.82
- 代表例: 20260513_020500, 20260512_210500, 20260512_190501
- 扱い: レジサポ実体、役割転換、失敗ブレイクの新判定を後追い検証する

### 紙トレード準備
- trade_execution_gate=pass: 0件
- trade_execution_gate=blocked: 29件
- 主なブロック理由: phase1_inactive=29件, setup_not_ready=29件, wait_pressure_too_high=18件, execution_shadow_too_low=14件
- paper_orders planned: 0件
- phase1_v1_shadow 記録付き: 29件
- tp_eval=too_close のうち shadow TP1 が現行TP1より遠い候補: 1/1件

### risk_flags 有効性比較
- lower_liquidity_close: negative_rate=85.7% (n=21)
- sweep_incomplete: negative_rate=85.0% (n=20)
- ask_wall_close: negative_rate=75.0% (n=12)
