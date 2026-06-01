# quality guard 初回反映評価 20260601

## 1. まず結論

- daily-sync では quality guard が新規候補に対して強く効いている。
- `market_map opportunity` の `26件 -> 4件` は、紙候補をかなり絞れていることを示す。
- ただし抑制率が高いため、機会損失の有無は counterfactual で確認する必要がある。
- `paper_opportunity_diagnostics_20260601.md` の `quality guard blocked=0件` や `guard該当 closed sl_hit=0件` は、guard 成功の証拠ではない。
- 既存 `paper_positions` 保持仕様と集計母集団の違いを考慮して解釈する必要がある。
- 今回は guard 条件を変更しない。

## 2. 集計対象の違い

- `feedback_daily_sync_20260601.md` は、今回同期期間で新しく観測された shadow / paper 候補を主対象にしている。
- `paper_opportunity_diagnostics_20260601.md` は、`paper_positions.csv` の累積 closed 履歴 `491件` を主対象にしている。
- daily-sync の `quality guard blocked=15件` は、新規候補の時点で guard が効いた件数として読める。
- diagnostics 側の `market_map candidate before/after guard: 263件 -> 107件` は、累積 closed 母集団に対する flag ベースの後追い集計として読むべきで、daily-sync の新規観測件数と直接比較しない。

## 3. daily-sync の quality guard 集計

`feedback_daily_sync_20260601.md` の集計は以下。

- `quality guard blocked=15件`
- `require_execution_for_high_wait=13件`
- `suppress_long_high_wait=5件`
- `suppress_trend_flip_up_strong=4件`
- `market_map opportunity before/after guard: 26件 -> 4件`

解釈は明確で、今回同期期間の新規候補に対して quality guard が強く効いている。特に `wait>=60` と `execution<24` の組み合わせが最頻で、長時間待ちと低 execution を紙候補化しない設計意図はそのまま反映されている。

## 4. paper_opportunity_diagnostics の quality guard 集計

`paper_opportunity_diagnostics_20260601.md` の集計は以下。

- `paper_positions target=494件 / closed=491件`
- `quality guard blocked=0件`
- `market_map candidate before/after guard: 263件 -> 107件`
- `closed sl_hit=207件`
- `quality guard 該当 closed sl_hit=0件`

ここで見るべきなのは、diagnostics が「今の guard 実装後に blocked された新規候補」ではなく、「既存 closed 履歴に残っている paper_positions」を母集団としている点である。したがって `blocked=0件` は guard が不要だったことを示さない。

`263件 -> 107件` は、累積 closed 母集団に対して見たとき、guard に抵触しそうな `market_map` 系候補が相当量含まれていたことを示す。daily-sync の `26件 -> 4件` より母集団が大きく、期間も広いため、同じ意味の件数ではない。

## 5. 件数差の解釈

件数差は、まず母集団差として扱うのが妥当である。

- daily-sync: 今回同期期間の新規観測中心
- diagnostics: `paper_positions.csv` の累積 closed 履歴中心

この違いにより、daily-sync では `quality guard blocked=15件` が見え、diagnostics では `quality guard blocked=0件` でも不整合とは限らない。既存 closed 行には、guard 実装後の `opportunity_reasons` が後付けで保存されないため、closed 台帳だけを見ても blocked 痕跡が出ない構造があり得る。

その一方で、`market_map opportunity 26件 -> 4件` と `market_map candidate 263件 -> 107件` は方向として整合している。どちらも、guard が `market_map` 起点の候補をかなり絞ることを示している。

## 6. guard 該当 closed sl_hit=0件の注意点

`guard該当 closed sl_hit=0件` は、guard が `sl_hit` を完全に防いだ証拠ではない。

既存 `paper_positions.csv` の closed 行には、guard 実装後の `opportunity_reasons` が後付けされない可能性がある。そのため、`closed sl_hit=207件` に対して `guard該当 closed sl_hit=0件` だった点は、既存 `paper_positions` 保持仕様と、レポート側の集計母集団の違いを含めて解釈する必要がある。

この数字だけを見て `guard は十分効いた`、または逆に `guard は不要` と結論づけるのは誤りである。

## 7. counterfactual_quality_guard の必要性

既存 closed 履歴に対して、`paper_positions.csv` と `shadow_log.csv` を `signal_id` で突き合わせ、guard 条件を後付け再計算した。

## counterfactual_quality_guard

- closed 全体件数: `491件`
- closed `sl_hit` 件数: `207件`
- closed `tp2_hit` 件数: `26件`
- closed `missed_opportunity` 件数: `123件`
- counterfactual guard 該当件数: `225件`
- counterfactual guard 該当 `sl_hit` 件数: `98件`
- counterfactual guard 該当 `tp2_hit` 件数: `6件`
- counterfactual guard 該当 `missed_opportunity` 件数: `23件`
- counterfactual guard 非該当 `sl_hit` 件数: `109件`
- counterfactual guard 非該当 `tp2_hit` 件数: `20件`
- counterfactual guard 非該当 `missed_opportunity` 件数: `100件`

reason 別の重なりは以下。

- `require_execution_for_high_wait=200件`
- `suppress_long_high_wait=130件`
- `suppress_trend_flip_up_strong=12件`

この counterfactual は後付け再計算であり、実運用結果ではない。ただし、`guard該当 closed sl_hit=0件` のような保存仕様依存の見え方を補正するには有効である。抑制対象 `225件` の中に `sl_hit=98件` が含まれる一方で、`tp2_hit=6件` と `missed_opportunity=23件` も含まれるため、guard は損失抑制だけでなく機会損失も持つ可能性がある。

今回は report builder の大きな追加実装までは行わず、まず評価レポート上で解釈を固定するのが妥当である。

## 8. 次に ChatGPT が判断する論点

1. counterfactual `225件` のうち `sl_hit=98件` をどう評価するか。guard の抑制価値はあるが、`tp2_hit=6件` と `missed_opportunity=23件` の機会損失を許容するかを判断する必要がある。
2. `require_execution_for_high_wait=200件` が支配的であるため、今後は `wait` と `execution` の閾値自体を再調整するか、それとも現状維持で追観測するかを決める必要がある。
3. `paper_entry_sl_wait_redesign` は builder 不在のままなので、次回は `counterfactual_quality_guard` と同じ系統の builder として正式化するかを判断する必要がある。

## 9. counterfactual reason組み合わせ別 outcome

`A=require_execution_for_high_wait`、`B=suppress_long_high_wait`、`C=suppress_trend_flip_up_strong` として、closed `491件` を後付け再計算した。

| group | count | sl_hit | sl_hit_rate | tp2_hit | tp2_hit_rate | missed_opportunity | missed_rate | timeout | entry_not_reached | avg_R | memo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A only | 89 | 81 | 91.0% | 4 | 4.5% | 4 | 4.5% | 0 | 0 | -0.72 | 高 wait と低 execution の単独該当。失敗寄りが強い。 |
| B only | 18 | 1 | 5.6% | 1 | 5.6% | 9 | 50.0% | 0 | 7 | 5.37 | long + high wait 単独。sl より missed / 未到達巻き込みが大きい。 |
| C only | 6 | 2 | 33.3% | 0 | 0.0% | 4 | 66.7% | 0 | 0 | 0.53 | trend flip up 単独。件数が少なく断定しない。 |
| A+B | 106 | 8 | 7.5% | 1 | 0.9% | 6 | 5.7% | 2 | 89 | 16.07 | high wait + low execution に long が重なる群。entry_not_reached が支配的。 |
| A+C | 0 | 0 | n/a | 0 | n/a | 0 | n/a | 0 | 0 | n/a | 該当なし。 |
| B+C | 1 | 1 | 100.0% | 0 | 0.0% | 0 | 0.0% | 0 | 0 | -1.00 | 件数 1 のため判断材料としては弱い。 |
| A+B+C | 5 | 5 | 100.0% | 0 | 0.0% | 0 | 0.0% | 0 | 0 | -0.60 | 3 条件重複。件数は少ないが失敗は強い。 |
| guard該当全体 | 225 | 98 | 43.6% | 6 | 2.7% | 23 | 10.2% | 2 | 96 | 7.71 | 後付け guard 対象全体。 |
| guard非該当全体 | 266 | 109 | 41.0% | 20 | 7.5% | 100 | 37.6% | 17 | 20 | 1.11 | non-guard 群。missed と tp2 の比率が高い。 |
| closed全体 | 491 | 207 | 42.2% | 26 | 5.3% | 123 | 25.1% | 19 | 116 | 4.13 | closed 全母集団。 |

整合チェック:

- `A only + B only + C only + A+B + A+C + B+C + A+B+C = 225件`
- guard 該当 `sl_hit=98件`
- guard 該当 `tp2_hit=6件`
- guard 該当 `missed_opportunity=23件`

`avg_R` は `paper_positions.csv` の `realized_r` を用いた。`entry_not_reached` や `missed_opportunity` にも台帳上の R 値が入るため、純粋な約定後損益だけを表す列ではない。

## 10. precision / collateral damage

- guard該当の `sl_hit_rate` は `43.6%`。
- guard非該当の `sl_hit_rate` は `41.0%`。
- closed全体の `sl_hit_rate` は `42.2%`。
- guard該当の `tp2_hit_rate` は `2.7%`。
- guard該当の `missed_opportunity_rate` は `10.2%`。

reason組み合わせ別の見え方は次の通り。

- 最も `sl_hit_rate` が高い group は `B+C` と `A+B+C` の `100.0%` だが、件数は `1件` と `5件` なので断定評価には使わない。
- 件数を伴って最も `sl_hit_rate` が高いのは `A only` の `91.0%` で、`require_execution_for_high_wait` 単独は guard として有望な形を示す。
- `tp2_hit` と `missed_opportunity` を多く巻き込むのは `B only` と `C only` で、特に `B only` は `missed_rate=50.0%`、`entry_not_reached=7件`、`C only` は `missed_rate=66.7%` だった。long 側単独抑制は閾値や条件分割の再考余地がある。
- `A+B` は `sl_hit_rate` 自体は低いが、`entry_not_reached=89件` が支配的で、high wait と low execution と long が重なる群は「悪い損切りを止めた」というより「候補化そのものを遅らせる」性質が強い。

暫定解釈は以下。

- `A only` は、失敗率が高く collateral damage が比較的小さいため、現状維持を支持する材料がある。
- `B only` と `C only` は、`sl_hit` 抑制よりも `missed_opportunity` や未到達の巻き込みが目立つため、次回 ChatGPT が `閾値維持 / 閾値調整 / guard分割` を判断する材料として扱う。
- この分解は、guard条件を即時変更するためのものではない。次回 ChatGPT が、`require_execution_for_high_wait` の維持・緩和・分割を判断するための材料である。
