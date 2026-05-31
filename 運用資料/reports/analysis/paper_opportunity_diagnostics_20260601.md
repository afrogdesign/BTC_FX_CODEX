# 紙実行候補 entry/wait 診断

- 対象 paper_positions: 504件
- closed: 499件 / opportunity_type: setup_watch_learning=209件, direction_rr_learning=169件, market_map_opportunity=115件, confidence_watch_sweep_lite=5件, formal_execution_candidate=1件
- closed 全体: 勝率=5.4% / 平均R=4.07 / 簡易PF=11.89 / 終了=sl_hit=211件, missed_opportunity=125件, entry_not_reached=116件, tp2_hit=27件, timeout=20件
- market_map_opportunity: 115件 / 勝率=9.6% / 平均R=0.39 / 簡易PF=2.15 / 終了=sl_hit=54件, missed_opportunity=42件, tp2_hit=11件, timeout=8件
- その他 opportunity: 384件 / 勝率=4.2% / 平均R=5.18 / 簡易PF=14.47

## 判断
- 主な失敗は missed より SL 側に寄っており、入口を広げるより entry 発火または SL/TP 条件の精査を優先する。
- `support_to_resistance_flip` などの flag 自体は有効でも、紙ポジション化する entry / wait 条件がまだ粗い。
- quality guard blocked: 198件 / 理由=require_execution_for_high_wait+suppress_long_high_wait=124件, require_execution_for_high_wait=69件, require_execution_for_high_wait+suppress_long_high_wait+suppress_trend_flip_up_strong=5件
- hard_quality_blocked: 198件 / 理由=require_execution_for_high_wait+suppress_long_high_wait=124件, require_execution_for_high_wait=69件, require_execution_for_high_wait+suppress_long_high_wait+suppress_trend_flip_up_strong=5件
- soft_quality_risk: 22件 / 理由=soft_risk:suppress_long_high_wait=15件, soft_risk:suppress_trend_flip_up_strong=6件, soft_risk:suppress_long_high_wait+suppress_trend_flip_up_strong=1件
- market_map candidate before/after guard: 266件 -> 115件
- market_map candidate before/after hard guard: 266件 -> 115件
- closed sl_hit: 211件 / quality guard 該当 closed sl_hit: 12件

## exit_status 別
- tp2_hit: 11件 / 勝率=100.0% / 平均R=2.40 / 簡易PF=0.00 / 終了=tp2_hit=11件
- sl_hit: 54件 / 勝率=0.0% / 平均R=-0.70 / 簡易PF=0.00 / 終了=sl_hit=54件
- timeout: 8件 / 勝率=0.0% / 平均R=0.26 / 簡易PF=2.87 / 終了=timeout=8件
- missed_opportunity: 42件 / 勝率=0.0% / 平均R=1.30 / 簡易PF=0.00 / 終了=missed_opportunity=42件

## confidence 帯別
- direction<60: 32件 / 勝率=6.2% / 平均R=0.25 / 簡易PF=1.55 / 終了=sl_hit=15件, missed_opportunity=14件, tp2_hit=2件, timeout=1件
- direction>=60: 83件 / 勝率=10.8% / 平均R=0.44 / 簡易PF=2.52 / 終了=sl_hit=39件, missed_opportunity=28件, tp2_hit=9件, timeout=7件
- execution<24: 77件 / 勝率=7.8% / 平均R=0.12 / 簡易PF=1.29 / 終了=sl_hit=45件, missed_opportunity=19件, timeout=7件, tp2_hit=6件
- execution>=24: 38件 / 勝率=13.2% / 平均R=0.94 / 簡易PF=6.70 / 終了=missed_opportunity=23件, sl_hit=9件, tp2_hit=5件, timeout=1件
- wait>=60: 40件 / 勝率=15.0% / 平均R=-0.10 / 簡易PF=0.84 / 終了=sl_hit=28件, tp2_hit=6件, missed_opportunity=5件, timeout=1件
- wait<60: 75件 / 勝率=6.7% / 平均R=0.65 / 簡易PF=4.44 / 終了=missed_opportunity=37件, sl_hit=26件, timeout=7件, tp2_hit=5件

## wait 帯別
- wait<40: 1件 / 勝率=0.0% / 平均R=1.30 / 簡易PF=0.00 / 終了=missed_opportunity=1件
- 40<=wait<60: 74件 / 勝率=6.8% / 平均R=0.64 / 簡易PF=4.35 / 終了=missed_opportunity=36件, sl_hit=26件, timeout=7件, tp2_hit=5件
- 60<=wait<80: 33件 / 勝率=18.2% / 平均R=0.06 / 簡易PF=1.10 / 終了=sl_hit=22件, tp2_hit=6件, missed_opportunity=5件
- wait>=80: 7件 / 勝率=0.0% / 平均R=-0.84 / 簡易PF=0.00 / 終了=sl_hit=6件, timeout=1件

## execution 帯別
- execution<20: 51件 / 勝率=5.9% / 平均R=0.00 / 簡易PF=1.00 / 終了=sl_hit=33件, missed_opportunity=10件, timeout=5件, tp2_hit=3件
- 20<=execution<35: 60件 / 勝率=13.3% / 平均R=0.66 / 簡易PF=3.45 / 終了=missed_opportunity=28件, sl_hit=21件, tp2_hit=8件, timeout=3件
- 35<=execution<50: 4件 / 勝率=0.0% / 平均R=1.30 / 簡易PF=0.00 / 終了=missed_opportunity=4件

## setup reason 別
- confidence_below_min: 92件 / 勝率=8.7% / 平均R=0.41 / 簡易PF=2.18 / 終了=sl_hit=41件, missed_opportunity=38件, tp2_hit=8件, timeout=5件
- entry_zone_not_reached: 7件 / 勝率=0.0% / 平均R=0.09 / 簡易PF=1.21 / 終了=sl_hit=4件, missed_opportunity=2件, timeout=1件
- inside_entry_zone_with_trigger: 6件 / 勝率=16.7% / 平均R=0.15 / 簡易PF=1.45 / 終了=sl_hit=4件, tp2_hit=1件, timeout=1件
- near_entry_zone_waiting_trigger: 10件 / 勝率=20.0% / 平均R=0.57 / 簡易PF=3.86 / 終了=sl_hit=5件, missed_opportunity=2件, tp2_hit=2件, timeout=1件

## side 別
- long: 19件 / 勝率=10.5% / 平均R=-0.36 / 簡易PF=0.47 / 終了=sl_hit=15件, tp2_hit=2件, timeout=1件, missed_opportunity=1件
- short: 96件 / 勝率=9.4% / 平均R=0.54 / 簡易PF=2.97 / 終了=missed_opportunity=41件, sl_hit=39件, tp2_hit=9件, timeout=7件

## market_map flag 別
- short_into_major_support: 101件 / 勝率=8.9% / 平均R=0.30 / 簡易PF=1.82 / 終了=sl_hit=51件, missed_opportunity=33件, tp2_hit=9件, timeout=8件
- support_to_resistance_flip: 81件 / 勝率=9.9% / 平均R=0.62 / 簡易PF=3.41 / 終了=missed_opportunity=38件, sl_hit=30件, tp2_hit=8件, timeout=5件
- support_to_resistance_retest_confirmed: 80件 / 勝率=10.0% / 平均R=0.62 / 簡易PF=3.34 / 終了=missed_opportunity=37件, sl_hit=30件, tp2_hit=8件, timeout=5件
- long_into_major_resistance: 78件 / 勝率=9.0% / 平均R=0.11 / 簡易PF=1.28 / 終了=sl_hit=47件, missed_opportunity=17件, timeout=7件, tp2_hit=7件
- trend_flip_confirmed_down: 51件 / 勝率=11.8% / 平均R=0.52 / 簡易PF=2.63 / 終了=sl_hit=21件, missed_opportunity=20件, tp2_hit=6件, timeout=4件
- major_resistance_rejection: 46件 / 勝率=10.9% / 平均R=0.05 / 簡易PF=1.10 / 終了=sl_hit=29件, missed_opportunity=8件, tp2_hit=5件, timeout=4件
- trend_flip_early_down: 45件 / 勝率=6.7% / 平均R=0.39 / 簡易PF=2.16 / 終了=sl_hit=21件, missed_opportunity=19件, tp2_hit=3件, timeout=2件
- major_support_rejection: 31件 / 勝率=3.2% / 平均R=0.50 / 簡易PF=2.74 / 終了=missed_opportunity=16件, sl_hit=11件, timeout=3件, tp2_hit=1件
- failed_breakout_down_reversal: 31件 / 勝率=12.9% / 平均R=0.01 / 簡易PF=1.02 / 終了=sl_hit=20件, missed_opportunity=4件, tp2_hit=4件, timeout=3件
- resistance_to_support_flip: 30件 / 勝率=10.0% / 平均R=-0.08 / 簡易PF=0.84 / 終了=sl_hit=20件, missed_opportunity=4件, timeout=3件, tp2_hit=3件
- resistance_to_support_retest_confirmed: 30件 / 勝率=10.0% / 平均R=-0.08 / 簡易PF=0.84 / 終了=sl_hit=20件, missed_opportunity=4件, timeout=3件, tp2_hit=3件
- failed_breakout_up_reversal: 16件 / 勝率=6.2% / 平均R=0.54 / 簡易PF=2.73 / 終了=missed_opportunity=8件, sl_hit=6件, tp2_hit=1件, timeout=1件
- trend_flip_early_up: 10件 / 勝率=10.0% / 平均R=0.34 / 簡易PF=2.21 / 終了=sl_hit=5件, missed_opportunity=3件, tp2_hit=1件, timeout=1件
- trend_flip_confirmed_up: 9件 / 勝率=11.1% / 平均R=-0.26 / 簡易PF=0.53 / 終了=sl_hit=7件, timeout=1件, tp2_hit=1件

## opportunity reason 別
- market_map:support_to_resistance_flip: 81件 / 勝率=9.9% / 平均R=0.62 / 簡易PF=3.41 / 終了=missed_opportunity=38件, sl_hit=30件, tp2_hit=8件, timeout=5件
- market_map:failed_breakout_down_reversal: 31件 / 勝率=12.9% / 平均R=0.01 / 簡易PF=1.02 / 終了=sl_hit=20件, missed_opportunity=4件, tp2_hit=4件, timeout=3件
- market_map:resistance_to_support_flip: 30件 / 勝率=10.0% / 平均R=-0.08 / 簡易PF=0.84 / 終了=sl_hit=20件, missed_opportunity=4件, timeout=3件, tp2_hit=3件
- soft_risk:suppress_long_high_wait: 1件 / 勝率=100.0% / 平均R=2.40 / 簡易PF=0.00 / 終了=tp2_hit=1件
- soft_risk:suppress_long_high_wait+suppress_trend_flip_up_strong: 1件 / 勝率=100.0% / 平均R=2.40 / 簡易PF=0.00 / 終了=tp2_hit=1件
- soft_risk:suppress_trend_flip_up_strong: 1件 / 勝率=0.0% / 平均R=-1.00 / 簡易PF=0.00 / 終了=sl_hit=1件

## SL失敗分類
- late_wait_sl: 20件 / 平均R=-0.90 / 簡易PF=0.00 / 平均MFE=0.00 / 平均MAE=0.00 / 代表=20260525_070500, 20260525_030500, 20260524_230500
- trend_flip_long_sl: 10件 / 平均R=-0.70 / 簡易PF=0.00 / 平均MFE=0.00 / 平均MAE=0.00 / 代表=20260523_210500, 20260522_030500, 20260517_180500
- other_sl: 24件 / 平均R=-0.54 / 簡易PF=0.00 / 平均MFE=0.00 / 平均MAE=0.00 / 代表=20260531_150500, 20260530_100500, 20260530_010500

## AI事後評価サマリー
- review coverage: 40/115件
- review source: ai=40件
- verdict: useful_wait=28件, useful_entry=1件, too_early=2件, too_late=1件, low_value=3件, useful_skip=5件
- sl_eval: good=24件, too_tight=14件, too_loose=2件
- tp_eval: good=22件, too_close=7件, too_far=11件
- tf_15m_eval: good=15件, mixed=11件, poor=14件
- action_class: tune_entry=29件, watch=6件, tune_text=3件, none=1件, tune_risk=1件
- priority: medium=24件, low=4件, high=12件
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
- review coverage: 22/77件
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

## proposal
- suppress_long_high_wait: long かつ wait>=60 は 17件 / 平均R=-0.34 / 簡易PF=0.51 のため、紙候補でも一段抑制候補。
- suppress_trend_flip_up_strong: 上方向転換系は 19件 / 平均R=0.06 / 勝率=10.5% のため、強評価へ戻さない候補。
- require_execution_for_high_wait: wait>=60 群は execution 下限強化候補。対象 40件 / 平均 execution=18.5 / 平均R=-0.10。
- delay_entry_on_sweep_wait: SWEEP_WAIT の弱い終了が 73件あるため、即 entry ではなく再確認待ちへ寄せる候補。
- widen_sl_for_noise: `sl_eval=too_tight` が 14件あるため、短期ノイズで刈られにくい SL 幅へ再設計候補。
- delay_entry_from_ai_review: `too_early` または `tf_15m_eval=poor` が 15件あり、entry 発火遅延または15分足条件見直し候補。

## AI事後評価の裏付け
- AI裏付け: `sl_eval=too_tight` が 14件あり、SL幅再設計の裏付けがある。
- AI裏付け: `too_early=2件` / `tf_15m_eval=poor=14件` で、発火遅延または15分足条件見直し候補。

## 不足データ
- MFE/MAE 判定: `mfe_atr` が 115件で欠落
- MFE/MAE 判定: `mae_atr` が 115件で欠落
- RR 判定: `rr_estimate` が 115件で欠落

## 弱い代表例
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
- 20260525_030500: sl_hit / side=short / setup=near_entry_zone_waiting_trigger / flags=long_into_major_resistance,short_into_major_support,support_to_resistance_flip,support_to_resistance_retest_confirmed,trend_flip_confirmed_down / dir=90.0 / exec=18.0 / wait=67.2 / R=-1.00
- 20260524_230500: sl_hit / side=short / setup=confidence_below_min / flags=long_into_major_resistance,short_into_major_support,failed_breakout_down_reversal,major_resistance_rejection,trend_flip_confirmed_down / dir=77.0 / exec=18.0 / wait=75.2 / R=-1.00

## 次に触る候補
- src/trade/opportunity_gate.py
- src/trade/paper_position.py
- src/analysis/market_map.py
- tools/log_feedback.py
