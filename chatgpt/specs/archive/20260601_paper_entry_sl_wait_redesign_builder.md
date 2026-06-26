# paper_entry_sl_wait_redesign builder 正式化仕様

更新日: 2026-06-01 JST
対象ブランチ: `ver02.6-v2`

## 目的

`paper_entry_sl_wait_redesign` report を正式 builder / CLI 化する。  
既存の `運用資料/reports/analysis/paper_entry_sl_wait_redesign_20260526.md` は有効な診断材料だが、専用 CLI がないため、daily-sync や paper_opportunity_diagnostics と同じ導線で再生成できない。  
次回実装では `tools/log_feedback.py` に builder と CLI を追加し、最新 paper_positions / ai_post_reviews / shadow_log を使って再生成できるようにする。

## 背景

`NEXT_TASK.md` では、次の論点として以下が残っている。

- paper_entry_sl_wait_redesign builder の正式化要否
- B/C 単独 soft risk の collateral damage
- entry / wait / price-distance 再設計
- high wait / low execution / long / trend_flip_confirmed_up の弱さ
- MFE/MAE/RR 欠落の明示

quality_guard_effectiveness では guard 条件変更の前に、entered/non-entered を分離した。  
次は entry / wait / SL 側の診断を正式 report builder にし、設計判断の材料を毎回更新できる状態にする。

## 実装対象

`tools/log_feedback.py` に以下を追加する。

- `build_paper_entry_sl_wait_redesign_report(...)`
- CLI subcommand: `build-paper-entry-sl-wait-redesign-report`
- alias: `--paper-entry-sl-wait-redesign`

## 入力

既存 builder 群と同じ流儀で以下を読む。

- `logs/csv/paper_positions.csv`
- `logs/csv/shadow_log.csv`
- `logs/csv/ai_post_reviews.csv` または既存 AI review 読み込み関数
- `date_from` / `date_to` を受け取れるようにする
- `output_md` を受け取れるようにする

## 出力先

デフォルト出力:

`運用資料/reports/analysis/paper_entry_sl_wait_redesign_YYYYMMDD.md`

`YYYYMMDD` は `date_to` がある場合は `date_to`、ない場合は実行日基準。

## report 必須セクション

既存 `paper_entry_sl_wait_redesign_20260526.md` の構造を維持しつつ、少なくとも以下を出力する。

1. 概要
   - 対象 paper_positions 件数
   - closed 件数
   - market_map_opportunity 件数
   - exit_status 内訳
   - 勝率 / 平均R / 簡易PF
2. 判断
   - SL 偏重
   - high wait
   - low execution
   - long 側の弱さ
   - trend_flip_confirmed_up の弱さ
   - entry 発火 / SL/TP / wait 抑制のどれを優先すべきか
3. exit_status 別
4. confidence / execution / wait 帯別
   - direction<60 / direction>=60
   - execution<24 / execution>=24
   - wait>=60 / wait<60
   - wait<40 / 40<=wait<60 / 60<=wait<80 / wait>=80
   - execution<20 / 20<=execution<35 / 35<=execution<50
5. setup reason 別
6. side 別
   - long
   - short
7. market_map flag 別
8. opportunity reason 別
9. SL失敗分類
   - late_wait_sl
   - trend_flip_long_sl
   - other_sl
10. AI事後評価サマリー
   - review coverage
   - verdict
   - sl_eval
   - tp_eval
   - tf_15m_eval
   - action_class
   - priority
   - high priority examples
11. AI事後評価 subset
   - long
   - wait>=60
   - execution<24
   - trend_flip_confirmed_up
12. proposal
   - suppress_long_high_wait
   - suppress_trend_flip_up_strong
   - require_execution_for_high_wait
   - delay_entry_on_sweep_wait
   - widen_sl_for_noise
   - delay_entry_from_ai_review
13. AI事後評価の裏付け
14. 不足データ
   - `mfe_atr` 欠落件数
   - `mae_atr` 欠落件数
   - `rr_estimate` 欠落件数
15. 弱い代表例
   - signal_id / exit_status / side / setup / flags / direction / execution / wait / R
16. 次に触る候補
   - `src/trade/opportunity_gate.py`
   - `src/trade/paper_position.py`
   - `src/analysis/market_map.py`
   - `tools/log_feedback.py`

## 追加する判断ルール

report には実装判断ではなく、設計判断用の分類だけを出す。

- `high_wait_sl_risk`
  - wait>=60 かつ sl_hit が多い群
- `low_execution_sl_risk`
  - execution<24 かつ sl_hit が多い群
- `long_side_sl_risk`
  - side=long かつ sl_hit が多い群
- `trend_flip_up_sl_risk`
  - trend_flip_confirmed_up を含み sl_hit が多い群
- `sl_too_tight_review_risk`
  - AI review で sl_eval=too_tight が多い群
- `entry_delay_review_risk`
  - AI review で too_early または tf_15m_eval=poor が多い群

これらは report 表示のみ。  
gate 条件や score 変更には使わない。

## テスト要件

`tests/test_log_feedback.py` に以下を追加すること。

- builder が report 文字列を返す
- `## 判断` が出る
- `## SL失敗分類` が出る
- `## AI事後評価サマリー` が出る
- `## proposal` が出る
- `high_wait_sl_risk` が出る
- `low_execution_sl_risk` が出る
- `trend_flip_up_sl_risk` が出る
- `mfe_atr` / `mae_atr` / `rr_estimate` 欠落件数が出る
- CLI subcommand が動く
- `--paper-entry-sl-wait-redesign` alias が動く

## 検証コマンド

```bash
./.venv312/bin/python -m unittest tests.test_log_feedback
./.venv312/bin/python -m unittest tests.test_phase1_trade_plans tests.test_log_feedback
./.venv312/bin/python tools/log_feedback.py --paper-entry-sl-wait-redesign
./.venv312/bin/python tools/log_feedback.py --report-hub
git diff --check
```

## 完了条件

- paper_entry_sl_wait_redesign report を CLI で再生成できる
- report hub に最新 paper_entry_sl_wait_redesign が反映される
- 既存 report builder / CLI alias を壊していない
- gate 判定条件は変更していない
- active spec は実装後に archive へ移動する
- `NEXT_TASK.md` と `report_hub_latest.md` を必要最小限更新する
