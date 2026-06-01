# quality_guard_effectiveness metric split 仕様

更新日: 2026-06-01 JST
対象ブランチ: `ver02.6-v2`

## 目的

`quality_guard_effectiveness` report の `avg_R` 解釈を安全にする。  
現状の `avg_R` は `entry_not_reached` / `missed_opportunity` を含むため、純粋な約定後損益と混同しやすい。  
次回実装では `entered subset` と `non-entered subset` を分離する。

## 背景

`運用資料/reports/analysis/quality_guard_effectiveness_20260601.md` では、  
`A only` は `sl_hit_rate=88.9%`、`avg_R=-0.65` で hard blocker 維持材料。  
一方、`A+B` は `entry_not_reached=43件` を多く含み `avg_R=14.23` になっており、現行 `avg_R` のままでは guard 評価に使いにくい。  
そのため、`exit_status` 別・`entered / non-entered` 別に評価軸を分ける。

## 実装対象

`tools/log_feedback.py` の `build_quality_guard_effectiveness_report` 系のみ。  
`trade_execution_gate` / `phase1b_lite_gate` / `opportunity_gate` の判定条件は変更しない。

## 追加する集計

既存 A/B/C group table は維持する。  
そのうえで、以下の補助指標を追加する。

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

`entered subset` は以下だけとする。

- `sl_hit`
- `tp2_hit`
- `timeout`

`non-entered subset` は以下だけとする。

- `missed_opportunity`
- `entry_not_reached`

## 追加する判定メモ

group ごとに `judgement` を出す。

- `blocker_candidate`
  - `count >= 10`
  - `entered_count >= 10`
  - `entered_sl_hit_rate >= 70%`
  - `entered_avg_R <= -0.30`
- `defer_due_to_non_entered_mix`
  - `non_entered_count / count >= 50%`
  - または `entry_not_reached / count >= 40%`
- `insufficient_n`
  - `count < 10`
  - または `entered_count < 10`

複数該当する場合は、`insufficient_n > defer_due_to_non_entered_mix > blocker_candidate` の順に優先する。

## report 出力要件

`quality_guard_effectiveness` report に以下を追加する。

1. `## entered / non-entered split`
2. group 別 table
3. `judgement` の説明
4. `avg_R` は `entered_avg_R` を主判断に使うこと
5. `non_entered_avg_R` は参考値であり、約定後損益として扱わないこと
6. counterfactual は後付け再計算であり、実運用結果ではないこと

## テスト要件

`tests/test_log_feedback.py` に以下を追加する。

- `entered / non-entered split` が出力される
- `entry_not_reached` が `entered_avg_R` に混ざらない
- `missed_opportunity` が `entered_avg_R` に混ざらない
- `A only` が `blocker_candidate` になり得る
- `A+B` のように `non-entered` が多い group は `defer_due_to_non_entered_mix` になり得る
- 件数不足 group は `insufficient_n` になる
- 既存 CLI alias は壊さない

## 検証コマンド

```bash
./.venv312/bin/python -m unittest tests.test_log_feedback
./.venv312/bin/python tools/log_feedback.py --quality-guard-effectiveness
./.venv312/bin/python tools/log_feedback.py --report-hub
git diff --check
```

## 完了条件

- `quality_guard_effectiveness` report が `entered / non-entered` を分離している
- 既存 group table は消えていない
- gate 判定条件は変更していない
- active spec は実装後に archive へ移動する
- `NEXT_TASK.md` と `report_hub_latest.md` を必要最小限更新する
