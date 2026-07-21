# quality guard 有効性

## counterfactual_quality_guard

- 目的: `paper_positions.csv` と `shadow_log.csv` を `signal_id` で突き合わせ、closed 母集団に対して quality guard 条件を後付け再計算する。
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-06-07
- closed 全体件数: `376件`
- joined closed 件数: `376件`
- missing_shadow_join: `0件`

| group | count | sl_hit | sl_hit_rate | tp2_hit | tp2_hit_rate | missed_opportunity | missed_rate | timeout | entry_not_reached | avg_R | memo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A only | 24 | 16 | 66.7% | 4 | 16.7% | 4 | 16.7% | 0 | 0 | 0.03 | 高 wait と低 execution の単独該当。失敗寄りが強い。 |
| B only | 12 | 1 | 8.3% | 1 | 8.3% | 9 | 75.0% | 0 | 1 | 1.11 | long + high wait 単独。sl より missed / 未到達巻き込みを確認する。 |
| C only | 2 | 1 | 50.0% | 0 | 0.0% | 1 | 50.0% | 0 | 0 | 0.15 | trend flip up 単独。件数が少ない場合は断定しない。 |
| A+B | 14 | 8 | 57.1% | 1 | 7.1% | 3 | 21.4% | 2 | 0 | -0.18 | high wait + low execution に long が重なる群。未到達巻き込みを確認する。 |
| A+C | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0.0% | 0 | 0 | 0.00 | A と C の重複。件数が少ない場合は断定しない。 |
| B+C | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0.0% | 0 | 0 | 0.00 | B と C の重複。件数が少ない場合は断定しない。 |
| A+B+C | 5 | 5 | 100.0% | 0 | 0.0% | 0 | 0.0% | 0 | 0 | -0.60 | 3 条件重複。件数が少ない場合は断定しない。 |
| guard該当全体 | 57 | 31 | 54.4% | 6 | 10.5% | 17 | 29.8% | 2 | 1 | 0.16 | 後付け guard 対象全体。 |
| guard非該当全体 | 319 | 114 | 35.7% | 26 | 8.2% | 149 | 46.7% | 20 | 10 | 0.57 | 後付け guard 非該当全体。 |
| closed全体 | 376 | 145 | 38.6% | 32 | 8.5% | 166 | 44.1% | 22 | 11 | 0.51 | closed 全母集団。 |

## entered / non-entered split

| group | count | entered_count | entered_sl_hit | entered_sl_hit_rate | entered_tp2_hit | entered_tp2_hit_rate | entered_timeout | entered_avg_R | non_entered_count | missed_opportunity | entry_not_reached | non_entered_avg_R | judgement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A only | 24 | 20 | 16 | 80.0% | 4 | 20.0% | 0 | -0.22 | 4 | 4 | 0 | 1.30 | monitor |
| B only | 12 | 2 | 1 | 50.0% | 1 | 50.0% | 0 | 0.70 | 10 | 9 | 1 | 1.19 | insufficient_n |
| C only | 2 | 1 | 1 | 100.0% | 0 | 0.0% | 0 | -1.00 | 1 | 1 | 0 | 1.30 | insufficient_n |
| A+B | 14 | 11 | 8 | 72.7% | 1 | 9.1% | 2 | -0.58 | 3 | 3 | 0 | 1.30 | blocker_candidate |
| A+C | 0 | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0.00 | 0 | 0 | 0 | 0.00 | insufficient_n |
| B+C | 0 | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0.00 | 0 | 0 | 0 | 0.00 | insufficient_n |
| A+B+C | 5 | 5 | 5 | 100.0% | 0 | 0.0% | 0 | -0.60 | 0 | 0 | 0 | 0.00 | insufficient_n |
| guard該当全体 | 57 | 39 | 31 | 79.5% | 6 | 15.4% | 2 | -0.34 | 18 | 17 | 1 | 1.24 | blocker_candidate |
| guard非該当全体 | 319 | 160 | 114 | 71.2% | 26 | 16.2% | 20 | -0.10 | 159 | 149 | 10 | 1.25 | monitor |
| closed全体 | 376 | 199 | 145 | 72.9% | 32 | 16.1% | 22 | -0.14 | 177 | 166 | 11 | 1.25 | monitor |

注記:
- `avg_R` は `paper_positions.csv` の `realized_r` を使う。
- `entry_not_reached` や `missed_opportunity` にも `realized_r` が入る可能性があり、純粋な約定後損益だけではない。
- `avg_R` は従来互換の全 `exit_status` 混在値。
- quality guard の blocker 判断では `entered_avg_R` を主判断に使う。
- `non_entered_avg_R` は参考値であり、約定後損益として扱わない。

## interpretation
- `judgement` は `insufficient_n > defer_due_to_non_entered_mix > blocker_candidate` の優先順で判定し、未該当は `monitor` とする。
- `A only` は失敗率が高く、hard blocker 維持を検討する材料。
- `B only` / `C only` は missed / 未到達の巻き込みを必ず見る。
- `B+C` や `A+B+C` は件数が少ない場合、断定しない。
- counterfactual は後付け再計算であり、実運用結果ではない。
- この report は guard 条件を即時変更するためのものではない。
