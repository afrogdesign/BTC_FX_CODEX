# quality guard 有効性

## counterfactual_quality_guard

- 目的: `paper_positions.csv` と `shadow_log.csv` を `signal_id` で突き合わせ、closed 母集団に対して quality guard 条件を後付け再計算する。
- closed 全体件数: `505件`
- joined closed 件数: `505件`
- missing_shadow_join: `0件`

| group | count | sl_hit | sl_hit_rate | tp2_hit | tp2_hit_rate | missed_opportunity | missed_rate | timeout | entry_not_reached | avg_R | memo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A only | 45 | 40 | 88.9% | 3 | 6.7% | 2 | 4.4% | 0 | 0 | -0.65 | 高 wait と低 execution の単独該当。失敗寄りが強い。 |
| B only | 15 | 1 | 6.7% | 1 | 6.7% | 9 | 60.0% | 0 | 4 | 3.97 | long + high wait 単独。sl より missed / 未到達巻き込みを確認する。 |
| C only | 6 | 2 | 33.3% | 0 | 0.0% | 4 | 66.7% | 0 | 0 | 0.53 | trend flip up 単独。件数が少ない場合は断定しない。 |
| A+B | 56 | 7 | 12.5% | 1 | 1.8% | 4 | 7.1% | 1 | 43 | 14.23 | high wait + low execution に long が重なる群。未到達巻き込みを確認する。 |
| A+C | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0.0% | 0 | 0 | 0.00 | A と C の重複。件数が少ない場合は断定しない。 |
| B+C | 1 | 0 | 0.0% | 1 | 100.0% | 0 | 0.0% | 0 | 0 | 2.40 | B と C の重複。件数が少ない場合は断定しない。 |
| A+B+C | 3 | 3 | 100.0% | 0 | 0.0% | 0 | 0.0% | 0 | 0 | -0.67 | 3 条件重複。件数が少ない場合は断定しない。 |
| guard該当全体 | 126 | 53 | 42.1% | 6 | 4.8% | 19 | 15.1% | 1 | 47 | 6.59 | 後付け guard 対象全体。 |
| guard非該当全体 | 379 | 163 | 43.0% | 21 | 5.5% | 106 | 28.0% | 20 | 69 | 3.16 | 後付け guard 非該当全体。 |
| closed全体 | 505 | 216 | 42.8% | 27 | 5.3% | 125 | 24.8% | 21 | 116 | 4.01 | closed 全母集団。 |

## entered / non-entered split

| group | count | entered_count | entered_sl_hit | entered_sl_hit_rate | entered_tp2_hit | entered_tp2_hit_rate | entered_timeout | entered_avg_R | non_entered_count | missed_opportunity | entry_not_reached | non_entered_avg_R | judgement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A only | 45 | 43 | 40 | 93.0% | 3 | 7.0% | 0 | -0.74 | 2 | 2 | 0 | 1.30 | blocker_candidate |
| B only | 15 | 2 | 1 | 50.0% | 1 | 50.0% | 0 | 0.70 | 13 | 9 | 4 | 4.47 | insufficient_n |
| C only | 6 | 2 | 2 | 100.0% | 0 | 0.0% | 0 | -1.00 | 4 | 4 | 0 | 1.30 | insufficient_n |
| A+B | 56 | 9 | 7 | 77.8% | 1 | 11.1% | 1 | -0.50 | 47 | 4 | 43 | 17.05 | insufficient_n |
| A+C | 0 | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0.00 | 0 | 0 | 0 | 0.00 | insufficient_n |
| B+C | 1 | 1 | 0 | 0.0% | 1 | 100.0% | 0 | 2.40 | 0 | 0 | 0 | 0.00 | insufficient_n |
| A+B+C | 3 | 3 | 3 | 100.0% | 0 | 0.0% | 0 | -0.67 | 0 | 0 | 0 | 0.00 | insufficient_n |
| guard該当全体 | 126 | 60 | 53 | 88.3% | 6 | 10.0% | 1 | -0.61 | 66 | 19 | 47 | 13.14 | defer_due_to_non_entered_mix |
| guard非該当全体 | 379 | 204 | 163 | 79.9% | 21 | 10.3% | 20 | -0.38 | 175 | 106 | 69 | 7.28 | blocker_candidate |
| closed全体 | 505 | 264 | 216 | 81.8% | 27 | 10.2% | 21 | -0.43 | 241 | 125 | 116 | 8.88 | blocker_candidate |

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
