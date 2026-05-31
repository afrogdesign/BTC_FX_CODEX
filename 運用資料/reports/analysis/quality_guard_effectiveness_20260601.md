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
