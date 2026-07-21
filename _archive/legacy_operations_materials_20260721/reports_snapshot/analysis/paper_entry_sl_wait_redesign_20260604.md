# 紙実行候補 entry/wait 診断

- 対象 paper_positions: 362件
- フィルタ: date_from=2026-04-18
- フィルタ: date_to=2026-06-04
- closed: 357件 / opportunity_type: setup_watch_learning=234件, market_map_opportunity=117件, confidence_watch_sweep_lite=5件, formal_execution_candidate=1件
- closed 全体: 勝率=8.7% / 平均R=0.48 / 簡易PF=2.43 / 終了=missed_opportunity=150件, sl_hit=143件, tp2_hit=31件, timeout=22件, entry_not_reached=11件
- market_map_opportunity: 117件 / 勝率=9.4% / 平均R=0.37 / 簡易PF=2.05 / 終了=sl_hit=56件, missed_opportunity=42件, tp2_hit=11件, timeout=8件
- その他 opportunity: 240件 / 勝率=8.3% / 平均R=0.53 / 簡易PF=2.64

## 判断
- 主な失敗は missed より SL 側に寄っており、入口を広げるより entry 発火または SL/TP 条件の精査を優先する。
- `support_to_resistance_flip` などの flag 自体は有効でも、紙ポジション化する entry / wait 条件がまだ粗い。
- quality guard blocked: 505件 / 理由=require_execution_for_high_wait+suppress_long_high_wait=305件, require_execution_for_high_wait=172件, require_execution_for_high_wait+suppress_long_high_wait+suppress_trend_flip_up_strong=28件
- hard_quality_blocked: 505件 / 理由=require_execution_for_high_wait+suppress_long_high_wait=305件, require_execution_for_high_wait=172件, require_execution_for_high_wait+suppress_long_high_wait+suppress_trend_flip_up_strong=28件
- soft_quality_risk: 14件 / 理由=soft_risk:suppress_long_high_wait=12件, soft_risk:suppress_trend_flip_up_strong=2件
- market_map candidate before/after guard: 323件 -> 117件
- market_map candidate before/after hard guard: 323件 -> 117件
- closed sl_hit: 143件 / quality guard 該当 closed sl_hit: 16件

## exit_status 別
- tp2_hit: 11件 / 勝率=100.0% / 平均R=2.40 / 簡易PF=0.00 / 終了=tp2_hit=11件
- sl_hit: 56件 / 勝率=0.0% / 平均R=-0.71 / 簡易PF=0.00 / 終了=sl_hit=56件
- timeout: 8件 / 勝率=0.0% / 平均R=0.26 / 簡易PF=2.87 / 終了=timeout=8件
- missed_opportunity: 42件 / 勝率=0.0% / 平均R=1.30 / 簡易PF=0.00 / 終了=missed_opportunity=42件

## confidence 帯別
- direction<60: 32件 / 勝率=6.2% / 平均R=0.25 / 簡易PF=1.55 / 終了=sl_hit=15件, missed_opportunity=14件, tp2_hit=2件, timeout=1件
- direction>=60: 85件 / 勝率=10.6% / 平均R=0.41 / 簡易PF=2.33 / 終了=sl_hit=41件, missed_opportunity=28件, tp2_hit=9件, timeout=7件
- execution<24: 79件 / 勝率=7.6% / 平均R=0.09 / 簡易PF=1.21 / 終了=sl_hit=47件, missed_opportunity=19件, timeout=7件, tp2_hit=6件
- execution>=24: 38件 / 勝率=13.2% / 平均R=0.94 / 簡易PF=6.70 / 終了=missed_opportunity=23件, sl_hit=9件, tp2_hit=5件, timeout=1件
- wait>=60: 40件 / 勝率=15.0% / 平均R=-0.10 / 簡易PF=0.84 / 終了=sl_hit=28件, tp2_hit=6件, missed_opportunity=5件, timeout=1件
- wait<60: 77件 / 勝率=6.5% / 平均R=0.61 / 簡易PF=3.89 / 終了=missed_opportunity=37件, sl_hit=28件, timeout=7件, tp2_hit=5件

## wait 帯別
- wait<40: 1件 / 勝率=0.0% / 平均R=1.30 / 簡易PF=0.00 / 終了=missed_opportunity=1件
- 40<=wait<60: 76件 / 勝率=6.6% / 平均R=0.60 / 簡易PF=3.81 / 終了=missed_opportunity=36件, sl_hit=28件, timeout=7件, tp2_hit=5件
- 60<=wait<80: 33件 / 勝率=18.2% / 平均R=0.06 / 簡易PF=1.10 / 終了=sl_hit=22件, tp2_hit=6件, missed_opportunity=5件
- wait>=80: 7件 / 勝率=0.0% / 平均R=-0.84 / 簡易PF=0.00 / 終了=sl_hit=6件, timeout=1件

## execution 帯別
- execution<20: 53件 / 勝率=5.7% / 平均R=-0.04 / 簡易PF=0.92 / 終了=sl_hit=35件, missed_opportunity=10件, timeout=5件, tp2_hit=3件
- 20<=execution<35: 60件 / 勝率=13.3% / 平均R=0.66 / 簡易PF=3.45 / 終了=missed_opportunity=28件, sl_hit=21件, tp2_hit=8件, timeout=3件
- 35<=execution<50: 4件 / 勝率=0.0% / 平均R=1.30 / 簡易PF=0.00 / 終了=missed_opportunity=4件

## setup reason 別
- confidence_below_min: 93件 / 勝率=8.6% / 平均R=0.40 / 簡易PF=2.11 / 終了=sl_hit=42件, missed_opportunity=38件, tp2_hit=8件, timeout=5件
- entry_zone_not_reached: 7件 / 勝率=0.0% / 平均R=0.09 / 簡易PF=1.21 / 終了=sl_hit=4件, missed_opportunity=2件, timeout=1件
- inside_entry_zone_with_trigger: 7件 / 勝率=14.3% / 平均R=-0.02 / 簡易PF=0.96 / 終了=sl_hit=5件, tp2_hit=1件, timeout=1件
- near_entry_zone_waiting_trigger: 10件 / 勝率=20.0% / 平均R=0.57 / 簡易PF=3.86 / 終了=sl_hit=5件, missed_opportunity=2件, tp2_hit=2件, timeout=1件

## side 別
- long: 19件 / 勝率=10.5% / 平均R=-0.36 / 簡易PF=0.47 / 終了=sl_hit=15件, tp2_hit=2件, timeout=1件, missed_opportunity=1件
- short: 98件 / 勝率=9.2% / 平均R=0.51 / 簡易PF=2.76 / 終了=sl_hit=41件, missed_opportunity=41件, tp2_hit=9件, timeout=7件

## market_map flag 別
- short_into_major_support: 103件 / 勝率=8.7% / 平均R=0.28 / 簡易PF=1.73 / 終了=sl_hit=53件, missed_opportunity=33件, tp2_hit=9件, timeout=8件
- support_to_resistance_flip: 83件 / 勝率=9.6% / 平均R=0.58 / 簡易PF=3.11 / 終了=missed_opportunity=38件, sl_hit=32件, tp2_hit=8件, timeout=5件
- support_to_resistance_retest_confirmed: 82件 / 勝率=9.8% / 平均R=0.58 / 簡易PF=3.05 / 終了=missed_opportunity=37件, sl_hit=32件, tp2_hit=8件, timeout=5件
- long_into_major_resistance: 80件 / 勝率=8.8% / 平均R=0.09 / 簡易PF=1.20 / 終了=sl_hit=49件, missed_opportunity=17件, timeout=7件, tp2_hit=7件
- trend_flip_confirmed_down: 51件 / 勝率=11.8% / 平均R=0.52 / 簡易PF=2.63 / 終了=sl_hit=21件, missed_opportunity=20件, tp2_hit=6件, timeout=4件
- trend_flip_early_down: 47件 / 勝率=6.4% / 平均R=0.33 / 簡易PF=1.91 / 終了=sl_hit=23件, missed_opportunity=19件, tp2_hit=3件, timeout=2件
- major_resistance_rejection: 46件 / 勝率=10.9% / 平均R=0.05 / 簡易PF=1.10 / 終了=sl_hit=29件, missed_opportunity=8件, tp2_hit=5件, timeout=4件
- major_support_rejection: 32件 / 勝率=3.1% / 平均R=0.45 / 簡易PF=2.47 / 終了=missed_opportunity=16件, sl_hit=12件, timeout=3件, tp2_hit=1件
- failed_breakout_down_reversal: 31件 / 勝率=12.9% / 平均R=0.01 / 簡易PF=1.02 / 終了=sl_hit=20件, missed_opportunity=4件, tp2_hit=4件, timeout=3件
- resistance_to_support_flip: 30件 / 勝率=10.0% / 平均R=-0.08 / 簡易PF=0.84 / 終了=sl_hit=20件, missed_opportunity=4件, timeout=3件, tp2_hit=3件
- resistance_to_support_retest_confirmed: 30件 / 勝率=10.0% / 平均R=-0.08 / 簡易PF=0.84 / 終了=sl_hit=20件, missed_opportunity=4件, timeout=3件, tp2_hit=3件
- failed_breakout_up_reversal: 17件 / 勝率=5.9% / 平均R=0.45 / 簡易PF=2.27 / 終了=missed_opportunity=8件, sl_hit=7件, tp2_hit=1件, timeout=1件
- trend_flip_early_up: 10件 / 勝率=10.0% / 平均R=0.34 / 簡易PF=2.21 / 終了=sl_hit=5件, missed_opportunity=3件, tp2_hit=1件, timeout=1件
- trend_flip_confirmed_up: 9件 / 勝率=11.1% / 平均R=-0.26 / 簡易PF=0.53 / 終了=sl_hit=7件, timeout=1件, tp2_hit=1件

## opportunity reason 別
- market_map:support_to_resistance_flip: 83件 / 勝率=9.6% / 平均R=0.58 / 簡易PF=3.11 / 終了=missed_opportunity=38件, sl_hit=32件, tp2_hit=8件, timeout=5件
- market_map:failed_breakout_down_reversal: 31件 / 勝率=12.9% / 平均R=0.01 / 簡易PF=1.02 / 終了=sl_hit=20件, missed_opportunity=4件, tp2_hit=4件, timeout=3件
- market_map:resistance_to_support_flip: 30件 / 勝率=10.0% / 平均R=-0.08 / 簡易PF=0.84 / 終了=sl_hit=20件, missed_opportunity=4件, timeout=3件, tp2_hit=3件
- soft_risk:suppress_long_high_wait: 1件 / 勝率=100.0% / 平均R=2.40 / 簡易PF=0.00 / 終了=tp2_hit=1件
- soft_risk:suppress_long_high_wait+suppress_trend_flip_up_strong: 1件 / 勝率=100.0% / 平均R=2.40 / 簡易PF=0.00 / 終了=tp2_hit=1件
- soft_risk:suppress_trend_flip_up_strong: 1件 / 勝率=0.0% / 平均R=-1.00 / 簡易PF=0.00 / 終了=sl_hit=1件

## SL失敗分類
- late_wait_sl: 20件 / 平均R=-0.90 / 簡易PF=0.00 / 平均MFE=0.00 / 平均MAE=0.00 / 代表=20260525_070500, 20260525_030500, 20260524_230500
- trend_flip_long_sl: 10件 / 平均R=-0.70 / 簡易PF=0.00 / 平均MFE=0.00 / 平均MAE=0.00 / 代表=20260523_210500, 20260522_030500, 20260517_180500
- other_sl: 26件 / 平均R=-0.58 / 簡易PF=0.00 / 平均MFE=0.00 / 平均MAE=0.00 / 代表=20260601_000500, 20260531_220501, 20260531_150500

## AI事後評価サマリー
- review coverage: 41/117件
- review source: ai=41件
- verdict: useful_wait=29件, useful_entry=1件, too_early=2件, too_late=1件, low_value=3件, useful_skip=5件
- sl_eval: too_tight=15件, good=24件, too_loose=2件
- tp_eval: good=23件, too_close=7件, too_far=11件
- tf_15m_eval: poor=15件, good=15件, mixed=11件
- action_class: tune_entry=30件, watch=6件, tune_text=3件, none=1件, tune_risk=1件
- priority: medium=25件, low=4件, high=12件
- high priority examples:
  - 20260525_190500: tune_entry / 15分足で上側流動性スイープ後の再失速をエントリー条件に追加し、WAIT解除を1段早める。
  - 20260523_210500: tune_text / 「ENTRY_OK/執行可」と「実弾不可・待機」を同時表示しない文面に統一し、待機専用通知として明確化する。
  - 20260518_000500: tune_entry / 15分足で戻り待ち未達のまま加速した場合に追随エントリーを許可する代替条件を追加する。

## AI事後評価: long
- review coverage: 12/19件
- review source: ai=12件
- verdict: useful_wait=8件, useful_entry=1件, useful_skip=3件
- sl_eval: good=10件, too_loose=1件, too_tight=1件
- tp_eval: good=3件, too_far=7件, too_close=2件
- tf_15m_eval: good=8件, poor=2件, mixed=2件
- action_class: watch=1件, tune_text=2件, tune_entry=9件
- priority: medium=9件, high=3件
- high priority examples:
  - 20260523_210500: tune_text / 「ENTRY_OK/執行可」と「実弾不可・待機」を同時表示しない文面に統一し、待機専用通知として明確化する。
  - 20260513_050501: tune_entry / 15分足で直上レジスタンス滞在時はロング通知を遅延し、明確な上抜け定着確認後のみ候補化する。
  - 20260513_010500: tune_entry / レンジかつ15分足逆行シグナル時はロング方向スコアを抑制し、WAIT優先で方向表示を中立寄りに補正する。

## AI事後評価: wait>=60
- review coverage: 14/40件
- review source: ai=14件
- verdict: useful_wait=9件, useful_entry=1件, useful_skip=3件, low_value=1件
- sl_eval: good=9件, too_loose=2件, too_tight=3件
- tp_eval: good=5件, too_close=2件, too_far=7件
- tf_15m_eval: good=8件, poor=4件, mixed=2件
- action_class: watch=2件, tune_entry=10件, tune_risk=1件, tune_text=1件
- priority: medium=11件, high=3件
- high priority examples:
  - 20260513_110500: tune_entry / SWEEP待ち条件を緩和し、15分足で下方向ブレイク継続時はwatchから段階的に実行許可へ切り替える。
  - 20260513_050501: tune_entry / 15分足で直上レジスタンス滞在時はロング通知を遅延し、明確な上抜け定着確認後のみ候補化する。
  - 20260513_010500: tune_entry / レンジかつ15分足逆行シグナル時はロング方向スコアを抑制し、WAIT優先で方向表示を中立寄りに補正する。

## AI事後評価: execution<24
- review coverage: 22/79件
- review source: ai=22件
- verdict: useful_wait=17件, low_value=2件, useful_skip=3件
- sl_eval: good=13件, too_tight=8件, too_loose=1件
- tp_eval: good=13件, too_far=7件, too_close=2件
- tf_15m_eval: good=10件, poor=5件, mixed=7件
- action_class: tune_entry=14件, none=1件, tune_risk=1件, watch=4件, tune_text=2件
- priority: medium=14件, low=3件, high=5件
- high priority examples:
  - 20260516_060500: tune_entry / 15分足で下抜け再加速が出た時はSWEEP待ちを緩和し、段階的にエントリー許可する条件へ修正する。
  - 20260513_190500: tune_text / 「高め本通知」でも執行不可時は件名先頭に「見送り専用」を固定表示して誤エントリー解釈を防ぐ。
  - 20260513_110500: tune_entry / SWEEP待ち条件を緩和し、15分足で下方向ブレイク継続時はwatchから段階的に実行許可へ切り替える。

## AI事後評価: trend_flip_confirmed_up
- review coverage: 10/19件
- review source: ai=10件
- verdict: useful_wait=6件, useful_entry=1件, useful_skip=3件
- sl_eval: good=8件, too_loose=1件, too_tight=1件
- tp_eval: good=3件, too_far=5件, too_close=2件
- tf_15m_eval: good=6件, poor=2件, mixed=2件
- action_class: watch=1件, tune_text=1件, tune_entry=8件
- priority: medium=7件, high=3件
- high priority examples:
  - 20260523_210500: tune_text / 「ENTRY_OK/執行可」と「実弾不可・待機」を同時表示しない文面に統一し、待機専用通知として明確化する。
  - 20260513_050501: tune_entry / 15分足で直上レジスタンス滞在時はロング通知を遅延し、明確な上抜け定着確認後のみ候補化する。
  - 20260513_010500: tune_entry / レンジかつ15分足逆行シグナル時はロング方向スコアを抑制し、WAIT優先で方向表示を中立寄りに補正する。


## 設計判断ラベル
- high_wait_sl_risk: triggered / wait>=60 sl_hit=28件 / total=40件
- low_execution_sl_risk: triggered / execution<24 sl_hit=47件 / total=79件
- long_side_sl_risk: triggered / side=long sl_hit=15件 / total=19件
- trend_flip_up_sl_risk: triggered / trend_flip_confirmed_up sl_hit=7件 / total=9件
- sl_too_tight_review_risk: triggered / sl_eval=too_tight 15件
- entry_delay_review_risk: triggered / too_early or tf_15m_eval=poor 16件

## entry recheck reason impact

| group | count | entered_count | sl_hit | sl_hit_rate | tp2_hit | tp2_hit_rate | timeout | missed_opportunity | entry_not_reached | avg_R | judgement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| entry_recheck_required_high_wait | 0 | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0.00 | insufficient_n |
| entry_recheck_required_low_execution | 0 | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0.00 | insufficient_n |
| entry_recheck_required_short_low_execution | 0 | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0.00 | insufficient_n |
| entry_recheck_required_long_weakness | 0 | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0.00 | insufficient_n |
| entry_recheck_required_trend_flip_up | 0 | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0.00 | insufficient_n |
| price_distance_missing | 0 | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0.00 | insufficient_n |
| entry_recheck_any | 0 | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0.00 | insufficient_n |
| entry_recheck_none | 117 | 75 | 56 | 74.7% | 11 | 14.7% | 8 | 42 | 0 | 0.37 | risk_confirmed |
| market_map_opportunity 全体 | 117 | 75 | 56 | 74.7% | 11 | 14.7% | 8 | 42 | 0 | 0.37 | risk_confirmed |

### interpretation
- entry recheck reason は paper candidate 品質改善のための抑制理由であり、実弾 gate ではない。
- trade_execution_gate / phase1b_lite_gate は変更しない。
- price_distance_missing は非blocking reason として扱う。
- B/C 単独 soft risk は hard blocker 化しない。
- trend_flip_confirmed_up は強評価へ戻さない。
- この集計は次の再設計判断材料であり、即 Phase 1B 昇格材料ではない。


## entry recheck counterfactual impact

| group | count | entered_count | sl_hit | sl_hit_rate | tp2_hit | tp2_hit_rate | timeout | missed_opportunity | entry_not_reached | avg_R | judgement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| entry_recheck_required_high_wait | 13 | 12 | 11 | 91.7% | 0 | 0.0% | 1 | 1 | 0 | -0.73 | risk_confirmed |
| entry_recheck_required_low_execution | 55 | 41 | 34 | 82.9% | 4 | 9.8% | 3 | 14 | 0 | 0.04 | risk_confirmed |
| entry_recheck_required_short_low_execution | 44 | 35 | 28 | 80.0% | 3 | 8.6% | 4 | 9 | 0 | 0.08 | risk_confirmed |
| entry_recheck_required_long_weakness | 0 | 0 | 0 | 0.0% | 0 | 0.0% | 0 | 0 | 0 | 0.00 | insufficient_n |
| entry_recheck_required_trend_flip_up | 7 | 7 | 6 | 85.7% | 1 | 14.3% | 0 | 0 | 0 | -0.23 | insufficient_n |
| price_distance_missing | 17 | 13 | 9 | 69.2% | 2 | 15.4% | 2 | 4 | 0 | 0.37 | monitor_only |
| entry_recheck_any | 76 | 57 | 45 | 78.9% | 6 | 10.5% | 6 | 19 | 0 | 0.12 | risk_confirmed |
| entry_recheck_none | 41 | 18 | 11 | 61.1% | 5 | 27.8% | 2 | 23 | 0 | 0.83 | collateral_damage_risk |
| market_map_opportunity 全体 | 117 | 75 | 56 | 74.7% | 11 | 14.7% | 8 | 42 | 0 | 0.37 | risk_confirmed |

### interpretation
- このセクションは counterfactual であり、過去実行時に実際に出た reason ではない。
- logged impact が 0件でも、counterfactual impact で過去候補への影響を評価する。
- entry recheck reason は paper candidate 品質改善のための抑制理由であり、実弾 gate ではない。
- trade_execution_gate / phase1b_lite_gate は変更しない。
- price_distance_missing は非blocking reason として扱う。
- B/C 単独 soft risk は hard blocker 化しない。
- trend_flip_confirmed_up は強評価へ戻さない。
- この集計は Phase 1B 昇格材料ではなく、次の再設計判断材料。


## entry recheck collateral damage breakdown

- 対象: counterfactual `entry_recheck_none` group
- rows: `41件`

### side

| group | count | entered_count | sl_hit | sl_hit_rate | tp2_hit | tp2_hit_rate | missed_opportunity | missed_rate | timeout | avg_R | judgement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| short | 38 | 15 | 9 | 60.0% | 4 | 26.7% | 23 | 60.5% | 2 | 0.86 | collateral_damage_risk |
| long | 3 | 3 | 2 | 66.7% | 1 | 33.3% | 0 | 0.0% | 0 | 0.47 | insufficient_n |

### wait band

| group | count | entered_count | sl_hit | sl_hit_rate | tp2_hit | tp2_hit_rate | missed_opportunity | missed_rate | timeout | avg_R | judgement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 40<=wait<60 | 39 | 17 | 11 | 64.7% | 4 | 23.5% | 22 | 56.4% | 2 | 0.77 | collateral_damage_risk |
| wait<40 | 1 | 0 | 0 | 0.0% | 0 | 0.0% | 1 | 100.0% | 0 | 1.30 | insufficient_n |
| 60<=wait<80 | 1 | 1 | 0 | 0.0% | 1 | 100.0% | 0 | 0.0% | 0 | 2.40 | insufficient_n |

### execution band

| group | count | entered_count | sl_hit | sl_hit_rate | tp2_hit | tp2_hit_rate | missed_opportunity | missed_rate | timeout | avg_R | judgement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 20<=execution<35 | 38 | 18 | 11 | 61.1% | 5 | 27.8% | 20 | 52.6% | 2 | 0.79 | collateral_damage_risk |
| 35<=execution<50 | 3 | 0 | 0 | 0.0% | 0 | 0.0% | 3 | 100.0% | 0 | 1.30 | insufficient_n |

### primary_setup_reason

| group | count | entered_count | sl_hit | sl_hit_rate | tp2_hit | tp2_hit_rate | missed_opportunity | missed_rate | timeout | avg_R | judgement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| confidence_below_min | 39 | 16 | 10 | 62.5% | 4 | 25.0% | 23 | 59.0% | 2 | 0.83 | collateral_damage_risk |
| inside_entry_zone_with_trigger | 2 | 2 | 1 | 50.0% | 1 | 50.0% | 0 | 0.0% | 0 | 0.70 | insufficient_n |

### market_map_flags

| group | count | entered_count | sl_hit | sl_hit_rate | tp2_hit | tp2_hit_rate | missed_opportunity | missed_rate | timeout | avg_R | judgement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| short_into_major_support | 32 | 15 | 9 | 60.0% | 4 | 26.7% | 17 | 53.1% | 2 | 0.77 | collateral_damage_risk |
| support_to_resistance_retest_confirmed | 31 | 10 | 6 | 60.0% | 3 | 30.0% | 21 | 67.7% | 1 | 0.99 | collateral_damage_risk |
| support_to_resistance_flip | 31 | 10 | 6 | 60.0% | 3 | 30.0% | 21 | 67.7% | 1 | 0.99 | collateral_damage_risk |
| trend_flip_confirmed_down | 19 | 8 | 5 | 62.5% | 2 | 25.0% | 11 | 57.9% | 1 | 0.73 | collateral_damage_risk |
| long_into_major_resistance | 19 | 13 | 8 | 61.5% | 3 | 23.1% | 6 | 31.6% | 2 | 0.53 | collateral_damage_risk |
| trend_flip_early_down | 18 | 7 | 4 | 57.1% | 2 | 28.6% | 11 | 61.1% | 1 | 0.96 | collateral_damage_risk |
| major_resistance_rejection | 14 | 9 | 5 | 55.6% | 2 | 22.2% | 5 | 35.7% | 2 | 0.59 | collateral_damage_risk |
| failed_breakout_down_reversal | 11 | 8 | 4 | 50.0% | 2 | 25.0% | 3 | 27.3% | 2 | 0.52 | collateral_damage_risk |
| major_support_rejection | 10 | 3 | 3 | 100.0% | 0 | 0.0% | 7 | 70.0% | 0 | 0.71 | collateral_damage_risk |
| resistance_to_support_retest_confirmed | 9 | 7 | 4 | 57.1% | 2 | 28.6% | 2 | 22.2% | 1 | 0.46 | collateral_damage_risk |
| resistance_to_support_flip | 9 | 7 | 4 | 57.1% | 2 | 28.6% | 2 | 22.2% | 1 | 0.46 | collateral_damage_risk |
| failed_breakout_up_reversal | 5 | 0 | 0 | 0.0% | 0 | 0.0% | 5 | 100.0% | 0 | 1.30 | collateral_damage_risk |
| trend_flip_early_up | 3 | 2 | 1 | 50.0% | 1 | 50.0% | 1 | 33.3% | 0 | 1.23 | insufficient_n |
| trend_flip_confirmed_up | 1 | 1 | 1 | 100.0% | 0 | 0.0% | 0 | 0.0% | 0 | -1.00 | insufficient_n |

### side + wait band

| group | count | entered_count | sl_hit | sl_hit_rate | tp2_hit | tp2_hit_rate | missed_opportunity | missed_rate | timeout | avg_R | judgement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| short | 40<=wait<60 | 37 | 15 | 9 | 60.0% | 4 | 26.7% | 22 | 59.5% | 2 | 0.84 | collateral_damage_risk |
| long | 40<=wait<60 | 2 | 2 | 2 | 100.0% | 0 | 0.0% | 0 | 0.0% | 0 | -0.50 | insufficient_n |
| short | wait<40 | 1 | 0 | 0 | 0.0% | 0 | 0.0% | 1 | 100.0% | 0 | 1.30 | insufficient_n |
| long | 60<=wait<80 | 1 | 1 | 0 | 0.0% | 1 | 100.0% | 0 | 0.0% | 0 | 2.40 | insufficient_n |

### side + execution band

| group | count | entered_count | sl_hit | sl_hit_rate | tp2_hit | tp2_hit_rate | missed_opportunity | missed_rate | timeout | avg_R | judgement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| short | 20<=execution<35 | 35 | 15 | 9 | 60.0% | 4 | 26.7% | 20 | 57.1% | 2 | 0.82 | collateral_damage_risk |
| short | 35<=execution<50 | 3 | 0 | 0 | 0.0% | 0 | 0.0% | 3 | 100.0% | 0 | 1.30 | insufficient_n |
| long | 20<=execution<35 | 3 | 3 | 2 | 66.7% | 1 | 33.3% | 0 | 0.0% | 0 | 0.47 | insufficient_n |

### setup reason + execution band

| group | count | entered_count | sl_hit | sl_hit_rate | tp2_hit | tp2_hit_rate | missed_opportunity | missed_rate | timeout | avg_R | judgement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| confidence_below_min | 20<=execution<35 | 36 | 16 | 10 | 62.5% | 4 | 25.0% | 20 | 55.6% | 2 | 0.79 | collateral_damage_risk |
| confidence_below_min | 35<=execution<50 | 3 | 0 | 0 | 0.0% | 0 | 0.0% | 3 | 100.0% | 0 | 1.30 | insufficient_n |
| inside_entry_zone_with_trigger | 20<=execution<35 | 2 | 2 | 1 | 50.0% | 1 | 50.0% | 0 | 0.0% | 0 | 0.70 | insufficient_n |

## proposal
- suppress_long_high_wait: long かつ wait>=60 は 17件 / 平均R=-0.34 / 簡易PF=0.51 のため、紙候補でも一段抑制候補。
- suppress_trend_flip_up_strong: 上方向転換系は 19件 / 平均R=0.06 / 勝率=10.5% のため、強評価へ戻さない候補。
- require_execution_for_high_wait: wait>=60 群は execution 下限強化候補。対象 40件 / 平均 execution=18.5 / 平均R=-0.10。
- delay_entry_on_sweep_wait: SWEEP_WAIT の弱い終了が 75件あるため、即 entry ではなく再確認待ちへ寄せる候補。
- widen_sl_for_noise: `sl_eval=too_tight` が 15件あるため、短期ノイズで刈られにくい SL 幅へ再設計候補。
- delay_entry_from_ai_review: `too_early` または `tf_15m_eval=poor` が 16件あり、entry 発火遅延または15分足条件見直し候補。

## AI事後評価の裏付け
- AI裏付け: `sl_eval=too_tight` が 15件あり、SL幅再設計の裏付けがある。
- AI裏付け: `too_early=2件` / `tf_15m_eval=poor=15件` で、発火遅延または15分足条件見直し候補。

## 不足データ
- MFE/MAE 判定: `mfe_atr` が 117件で欠落
- MFE/MAE 判定: `mae_atr` が 117件で欠落
- RR 判定: `rr_estimate` が 117件で欠落

## 弱い代表例
- 20260601_000500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_up_reversal,major_support_rejection,trend_flip_early_down / dir=76.0 / exec=18.0 / wait=59.2 / R=-1.00
- 20260531_220501: sl_hit / side=short / setup=inside_entry_zone_with_trigger / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_early_down / dir=100.0 / exec=18.0 / wait=51.2 / R=-1.00
- 20260531_150500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,support_to_resistance_flip,support_to_resistance_retest_confirmed,major_resistance_rejection,trend_flip_early_down / dir=65.0 / exec=33.0 / wait=51.2 / R=0.00
- 20260530_100500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_confirmed_down / dir=70.0 / exec=23.0 / wait=59.2 / R=-1.00
- 20260530_010500: sl_hit / side=short / setup=entry_zone_not_reached / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_early_down / dir=100.0 / exec=18.0 / wait=51.2 / R=0.00
- 20260529_210500: timeout / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,major_resistance_rejection,major_support_rejection,trend_flip_confirmed_up / dir=72.0 / exec=23.0 / wait=43.2 / R=0.27
- 20260529_200500: timeout / side=short / setup=near_entry_zone_waiting_trigger / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_early_down / dir=100.0 / exec=15.0 / wait=56.0 / R=0.31
- 20260529_060500: sl_hit / side=short / setup=inside_entry_zone_with_trigger / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_early_up / dir=100.0 / exec=18.0 / wait=51.2 / R=0.00
- 20260529_040500: sl_hit / side=short / setup=entry_zone_not_reached / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / dir=100.0 / exec=15.0 / wait=56.0 / R=-1.00
- 20260528_220500: missed_opportunity / side=short / setup=confidence_below_min / flags=resistance_to_support_flip,resistance_to_support_retest_confirmed,trend_flip_early_up / dir=55.0 / exec=33.0 / wait=43.2 / R=1.30
- 20260528_170500: timeout / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,resistance_to_support_flip,resistance_to_support_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_confirmed_down / dir=70.0 / exec=28.0 / wait=51.2 / R=-0.25
- 20260527_220500: missed_opportunity / side=short / setup=confidence_below_min / flags=support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_up_reversal,major_support_rejection,trend_flip_early_down / dir=65.0 / exec=30.0 / wait=48.0 / R=1.30
- 20260527_030500: missed_opportunity / side=short / setup=confidence_below_min / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_early_down / dir=66.0 / exec=18.0 / wait=59.2 / R=1.30
- 20260527_010500: missed_opportunity / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,failed_breakout_up_reversal,major_support_rejection,trend_flip_early_down / dir=59.0 / exec=23.0 / wait=51.2 / R=1.30
- 20260526_220500: missed_opportunity / side=short / setup=confidence_below_min / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_early_down / dir=67.0 / exec=28.0 / wait=43.2 / R=1.30
- 20260526_170500: missed_opportunity / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,major_support_rejection,trend_flip_early_down / dir=61.0 / exec=23.0 / wait=59.2 / R=1.30
- 20260526_120500: missed_opportunity / side=short / setup=confidence_below_min / flags=short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_early_down / dir=56.0 / exec=18.0 / wait=59.2 / R=1.30
- 20260526_080500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,major_resistance_rejection,failed_breakout_up_reversal,major_support_rejection,trend_flip_early_down / dir=50.0 / exec=18.0 / wait=59.2 / R=-1.00
- 20260525_190500: missed_opportunity / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_early_down / dir=66.0 / exec=28.0 / wait=59.2 / R=1.30
- 20260525_070500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_early_down / dir=84.0 / exec=18.0 / wait=75.2 / R=-1.00

## 次に触る候補
- src/trade/opportunity_gate.py
- src/trade/paper_position.py
- src/analysis/market_map.py
- tools/log_feedback.py
