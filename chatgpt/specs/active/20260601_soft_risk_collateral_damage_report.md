# B/C soft risk collateral damage report 仕様

## 目的

B/C 単独 soft risk の collateral damage を評価する report builder / CLI を追加する。  
quality guard 条件そのものは変更しない。

## 背景

`quality_guard_effectiveness_20260601.md` では、`B only` / `C only` / `A+B` などが `insufficient_n` や non-entered 混在の影響を受け、hard 化判断に十分な材料が不足している。  
`paper_entry_sl_wait_redesign_20260601.md` では high wait / low execution / long / trend flip up などのリスクラベルが出ているが、B/C 単独 soft risk を hard blocker 化すると `tp2_hit` や `missed_opportunity` の巻き込みが増える懸念がある。  
このため、B/C 単独 soft risk の collateral damage を専用 report で評価する。

## 実装対象

`tools/log_feedback.py` に以下を追加する。

- `build_soft_risk_collateral_damage_report(...)`
- CLI subcommand: `build-soft-risk-collateral-damage-report`
- alias: `--soft-risk-collateral-damage`

## 入力

既存 builder 群と同じ流儀で以下を読む。

- `logs/csv/paper_positions.csv`
- `logs/csv/shadow_log.csv`
- `date_from` / `date_to`
- `output_md`

## 出力先

デフォルト出力:

- `運用資料/reports/analysis/soft_risk_collateral_damage_YYYYMMDD.md`

`YYYYMMDD` は `date_to` がある場合は `date_to`、ない場合は実行日基準。

## 分析対象 group

- `B only` (`suppress_long_high_wait` のみ)
- `C only` (`suppress_trend_flip_up_strong` のみ)
- `B+C` (`suppress_long_high_wait` + `suppress_trend_flip_up_strong`)
- `A+B`
- `A+C`
- `A+B+C`
- `B/C soft risk 全体` (B or C を含み、A を含まない group)
- `A hard 含み全体` (A を含む group)
- `guard非該当全体`
- `closed全体`

A/B/C 定義:

- A = `require_execution_for_high_wait`
- B = `suppress_long_high_wait`
- C = `suppress_trend_flip_up_strong`

## report 必須セクション

1. 概要
- `closed` 全体件数
- joined `closed` 件数
- `missing_shadow_join`
- `B/C soft risk` 対象件数
- `A hard` 含み件数

2. group table
- `group`
- `count`
- `entered_count`
- `entered_sl_hit`
- `entered_sl_hit_rate`
- `entered_tp2_hit`
- `entered_tp2_hit_rate`
- `entered_timeout`
- `entered_avg_R`
- `non_entered_count`
- `missed_opportunity`
- `entry_not_reached`
- `non_entered_avg_R`
- `collateral_damage_score`
- `judgement`

3. collateral_damage_score

参考値として以下の意図で計算する。

- `tp2_hit` 巻き込みが多いほど上げる
- `missed_opportunity` 巻き込みが多いほど上げる
- `entry_not_reached` は collateral damage として弱めに扱う
- `entered_sl_hit_rate` が高いほど下げる

実装式は単純式でよい。例:

`collateral_damage_score = tp2_hit * 2 + missed_opportunity + entry_not_reached * 0.25 - entered_sl_hit * 0.5`

4. judgement

group ごとに以下のいずれかを出す。

- `harden_candidate`
- `keep_soft`
- `monitor_only`
- `avoid_hardening`

判定条件:

- `harden_candidate`
- `count >= 10`
- `entered_count >= 10`
- `entered_sl_hit_rate >= 70%`
- `collateral_damage_score <= 0`

- `keep_soft`
- `count >= 10`
- `collateral_damage_score > 0`

- `monitor_only`
- `count < 10`
- または `entered_count < 10`

- `avoid_hardening`
- `tp2_hit_rate >= 20%`
- または `missed_opportunity / count >= 40%`

優先順位:

- `monitor_only > avoid_hardening > keep_soft > harden_candidate`

5. representative examples

各 group から最大 5 件を出す。項目:

- `signal_id`
- `exit_status`
- `side`
- `setup`
- `flags`
- `direction`
- `execution`
- `wait`
- `realized_r`

6. interpretation

以下を明記する。

- B/C 単独 soft risk は現時点では hard blocker 化しない。
- この report は guard 条件変更のための材料であり、即時変更ではない。
- `missed_opportunity` / `entry_not_reached` は約定後損益ではない。
- `trend_flip_confirmed_up` は強評価へ戻さない。
- `trade_execution_gate` / `phase1b_lite_gate` / `opportunity_gate` は変更しない。

## report hub

`report_hub_latest.md` に以下の on-demand report を追加または更新する。

- 名称: `soft risk collateral damage`
- latest: `運用資料/reports/analysis/soft_risk_collateral_damage_YYYYMMDD.md`
- purpose: B/C 単独 soft risk の hard blocker 化による巻き込み被害を評価する。

## テスト要件

`tests/test_log_feedback.py` に以下を追加する。

- builder が report 文字列を返す
- `B only` が出る
- `C only` が出る
- `B+C` が出る
- `B/C soft risk 全体` が出る
- `collateral_damage_score` が出る
- `judgement` が出る
- `keep_soft` が出るケース
- `monitor_only` が出るケース
- `avoid_hardening` が出るケース
- representative examples が出る
- CLI subcommand が動く
- `--soft-risk-collateral-damage` alias が動く

## 検証コマンド

- `./.venv312/bin/python -m unittest tests.test_log_feedback`
- `./.venv312/bin/python -m unittest tests.test_phase1_trade_plans tests.test_log_feedback`
- `./.venv312/bin/python tools/log_feedback.py --soft-risk-collateral-damage`
- `./.venv312/bin/python tools/log_feedback.py --report-hub`
- `git diff --check`

## 完了条件

- `soft_risk_collateral_damage` report を CLI で再生成できる
- report hub に latest が反映される
- B/C 単独 soft risk の collateral damage が group 別に見える
- gate 判定条件は変更していない
- active spec は実装後に archive へ移動する
- `NEXT_TASK.md` と `report_hub_latest.md` を必要最小限更新する
