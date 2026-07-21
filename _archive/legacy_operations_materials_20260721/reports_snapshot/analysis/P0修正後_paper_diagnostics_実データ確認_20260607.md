# 紙実行候補 entry/wait 診断

- 成績の主指標は filled-only です。`missed_opportunity` と `entry_not_reached` は未約定系として別集計します。
- 既存互換のため `realized_r` は残していますが、gate / score 判断では filled-only を優先します。

- 対象 paper_positions: 570件
- closed: 564件 / opportunity_type: setup_watch_learning=272件, direction_rr_learning=169件, market_map_opportunity=117件, confidence_watch_sweep_lite=5件, formal_execution_candidate=1件
- closed 全体: 564件 / all=564件 / filled=279件 / filled勝率=11.5% / filled平均R=-0.37 / filled簡易PF=0.47 / missed=169件 / entry_not_reached=116件 / 終了=sl_hit=222件, missed_opportunity=169件, entry_not_reached=116件, tp2_hit=32件, timeout=25件
- market_map_opportunity: 117件 / all=117件 / filled=75件 / filled勝率=14.7% / filled平均R=-0.15 / filled簡易PF=0.72 / missed=42件 / entry_not_reached=0件 / 終了=sl_hit=56件, missed_opportunity=42件, tp2_hit=11件, timeout=8件
- その他 opportunity: 447件 / all=447件 / filled=204件 / filled勝率=10.3% / filled平均R=-0.45 / filled簡易PF=0.41

## 判断
- 主な失敗は missed より SL 側に寄っており、入口を広げるより entry 発火または SL/TP 条件の精査を優先する。
- `support_to_resistance_flip` などの flag 自体は有効でも、紙ポジション化する entry / wait 条件がまだ粗い。
- quality guard blocked: 915件 / 理由=require_execution_for_high_wait+suppress_long_high_wait=555件, require_execution_for_high_wait=332件, require_execution_for_high_wait+suppress_long_high_wait+suppress_trend_flip_up_strong=28件
- hard_quality_blocked: 915件 / 理由=require_execution_for_high_wait+suppress_long_high_wait=555件, require_execution_for_high_wait=332件, require_execution_for_high_wait+suppress_long_high_wait+suppress_trend_flip_up_strong=28件
- soft_quality_risk: 17件 / 理由=soft_risk:suppress_long_high_wait=15件, soft_risk:suppress_trend_flip_up_strong=2件
- market_map candidate before/after guard: 368件 -> 117件
- market_map candidate before/after hard guard: 368件 -> 117件
- closed sl_hit: 222件 / quality guard 該当 closed sl_hit: 16件

## exit_status 別
- tp2_hit: 11件 / all=11件 / filled=11件 / filled勝率=100.0% / filled平均R=2.40 / filled簡易PF=0.00 / missed=0件 / entry_not_reached=0件 / 終了=tp2_hit=11件
- sl_hit: 56件 / all=56件 / filled=56件 / filled勝率=0.0% / filled平均R=-0.71 / filled簡易PF=0.00 / missed=0件 / entry_not_reached=0件 / 終了=sl_hit=56件
- timeout: 8件 / all=8件 / filled=8件 / filled勝率=0.0% / filled平均R=0.26 / filled簡易PF=2.87 / missed=0件 / entry_not_reached=0件 / 終了=timeout=8件
- missed_opportunity: 42件 / all=42件 / filled=0件 / filled勝率=0.0% / filled平均R=0.00 / filled簡易PF=0.00 / missed=42件 / entry_not_reached=0件 / 終了=missed_opportunity=42件

## confidence 帯別
- direction<60: 32件 / all=32件 / filled=18件 / filled勝率=11.1% / filled平均R=-0.56 / filled簡易PF=0.32 / missed=14件 / entry_not_reached=0件 / 終了=sl_hit=15件, missed_opportunity=14件, tp2_hit=2件, timeout=1件
- direction>=60: 85件 / all=85件 / filled=57件 / filled勝率=15.8% / filled平均R=-0.03 / filled簡易PF=0.94 / missed=28件 / entry_not_reached=0件 / 終了=sl_hit=41件, missed_opportunity=28件, tp2_hit=9件, timeout=7件
- execution<24: 79件 / all=79件 / filled=60件 / filled勝率=10.0% / filled平均R=-0.29 / filled簡易PF=0.50 / missed=19件 / entry_not_reached=0件 / 終了=sl_hit=47件, missed_opportunity=19件, timeout=7件, tp2_hit=6件
- execution>=24: 38件 / all=38件 / filled=15件 / filled勝率=33.3% / filled平均R=0.38 / filled簡易PF=1.92 / missed=23件 / entry_not_reached=0件 / 終了=missed_opportunity=23件, sl_hit=9件, tp2_hit=5件, timeout=1件
- wait>=60: 40件 / all=40件 / filled=35件 / filled勝率=17.1% / filled平均R=-0.30 / filled簡易PF=0.58 / missed=5件 / entry_not_reached=0件 / 終了=sl_hit=28件, tp2_hit=6件, missed_opportunity=5件, timeout=1件
- wait<60: 77件 / all=77件 / filled=40件 / filled勝率=12.5% / filled平均R=-0.03 / filled簡易PF=0.93 / missed=37件 / entry_not_reached=0件 / 終了=missed_opportunity=37件, sl_hit=28件, timeout=7件, tp2_hit=5件

## wait 帯別
- wait<40: 1件 / all=1件 / filled=0件 / filled勝率=0.0% / filled平均R=0.00 / filled簡易PF=0.00 / missed=1件 / entry_not_reached=0件 / 終了=missed_opportunity=1件
- 40<=wait<60: 76件 / all=76件 / filled=40件 / filled勝率=12.5% / filled平均R=-0.03 / filled簡易PF=0.93 / missed=36件 / entry_not_reached=0件 / 終了=missed_opportunity=36件, sl_hit=28件, timeout=7件, tp2_hit=5件
- 60<=wait<80: 33件 / all=33件 / filled=28件 / filled勝率=21.4% / filled平均R=-0.16 / filled簡易PF=0.76 / missed=5件 / entry_not_reached=0件 / 終了=sl_hit=22件, tp2_hit=6件, missed_opportunity=5件
- wait>=80: 7件 / all=7件 / filled=7件 / filled勝率=0.0% / filled平均R=-0.84 / filled簡易PF=0.00 / missed=0件 / entry_not_reached=0件 / 終了=sl_hit=6件, timeout=1件

## execution 帯別
- execution<20: 53件 / all=53件 / filled=43件 / filled勝率=7.0% / filled平均R=-0.35 / filled簡易PF=0.40 / missed=10件 / entry_not_reached=0件 / 終了=sl_hit=35件, missed_opportunity=10件, timeout=5件, tp2_hit=3件
- 20<=execution<35: 60件 / all=60件 / filled=32件 / filled勝率=25.0% / filled平均R=0.11 / filled簡易PF=1.21 / missed=28件 / entry_not_reached=0件 / 終了=missed_opportunity=28件, sl_hit=21件, tp2_hit=8件, timeout=3件
- 35<=execution<50: 4件 / all=4件 / filled=0件 / filled勝率=0.0% / filled平均R=0.00 / filled簡易PF=0.00 / missed=4件 / entry_not_reached=0件 / 終了=missed_opportunity=4件

## setup reason 別
- confidence_below_min: 93件 / all=93件 / filled=55件 / filled勝率=14.5% / filled平均R=-0.23 / filled簡易PF=0.62 / missed=38件 / entry_not_reached=0件 / 終了=sl_hit=42件, missed_opportunity=38件, tp2_hit=8件, timeout=5件
- entry_zone_not_reached: 7件 / all=7件 / filled=5件 / filled勝率=0.0% / filled平均R=-0.39 / filled簡易PF=0.34 / missed=2件 / entry_not_reached=0件 / 終了=sl_hit=4件, missed_opportunity=2件, timeout=1件
- inside_entry_zone_with_trigger: 7件 / all=7件 / filled=7件 / filled勝率=14.3% / filled平均R=-0.02 / filled簡易PF=0.96 / missed=0件 / entry_not_reached=0件 / 終了=sl_hit=5件, tp2_hit=1件, timeout=1件
- near_entry_zone_waiting_trigger: 10件 / all=10件 / filled=8件 / filled勝率=25.0% / filled平均R=0.39 / filled簡易PF=2.56 / missed=2件 / entry_not_reached=0件 / 終了=sl_hit=5件, missed_opportunity=2件, tp2_hit=2件, timeout=1件

## side 別
- long: 19件 / all=19件 / filled=18件 / filled勝率=11.1% / filled平均R=-0.45 / filled簡易PF=0.37 / missed=1件 / entry_not_reached=0件 / 終了=sl_hit=15件, tp2_hit=2件, timeout=1件, missed_opportunity=1件
- short: 98件 / all=98件 / filled=57件 / filled勝率=15.8% / filled平均R=-0.06 / filled簡易PF=0.88 / missed=41件 / entry_not_reached=0件 / 終了=sl_hit=41件, missed_opportunity=41件, tp2_hit=9件, timeout=7件

## market_map flag 別
- short_into_major_support: 103件 / all=103件 / filled=70件 / filled勝率=12.9% / filled平均R=-0.20 / filled簡易PF=0.63 / missed=33件 / entry_not_reached=0件 / 終了=sl_hit=53件, missed_opportunity=33件, tp2_hit=9件, timeout=8件
- support_to_resistance_flip: 83件 / all=83件 / filled=45件 / filled勝率=17.8% / filled平均R=-0.02 / filled簡易PF=0.96 / missed=38件 / entry_not_reached=0件 / 終了=missed_opportunity=38件, sl_hit=32件, tp2_hit=8件, timeout=5件
- support_to_resistance_retest_confirmed: 82件 / all=82件 / filled=45件 / filled勝率=17.8% / filled平均R=-0.02 / filled簡易PF=0.96 / missed=37件 / entry_not_reached=0件 / 終了=missed_opportunity=37件, sl_hit=32件, tp2_hit=8件, timeout=5件
- long_into_major_resistance: 80件 / all=80件 / filled=63件 / filled勝率=11.1% / filled平均R=-0.24 / filled簡易PF=0.56 / missed=17件 / entry_not_reached=0件 / 終了=sl_hit=49件, missed_opportunity=17件, timeout=7件, tp2_hit=7件
- trend_flip_confirmed_down: 51件 / all=51件 / filled=31件 / filled勝率=19.4% / filled平均R=0.02 / filled簡易PF=1.03 / missed=20件 / entry_not_reached=0件 / 終了=sl_hit=21件, missed_opportunity=20件, tp2_hit=6件, timeout=4件
- trend_flip_early_down: 47件 / all=47件 / filled=28件 / filled勝率=10.7% / filled平均R=-0.33 / filled簡易PF=0.46 / missed=19件 / entry_not_reached=0件 / 終了=sl_hit=23件, missed_opportunity=19件, tp2_hit=3件, timeout=2件
- major_resistance_rejection: 46件 / all=46件 / filled=38件 / filled勝率=13.2% / filled平均R=-0.22 / filled簡易PF=0.61 / missed=8件 / entry_not_reached=0件 / 終了=sl_hit=29件, missed_opportunity=8件, tp2_hit=5件, timeout=4件
- major_support_rejection: 32件 / all=32件 / filled=16件 / filled勝率=6.2% / filled平均R=-0.40 / filled簡易PF=0.36 / missed=16件 / entry_not_reached=0件 / 終了=missed_opportunity=16件, sl_hit=12件, timeout=3件, tp2_hit=1件
- failed_breakout_down_reversal: 31件 / all=31件 / filled=27件 / filled勝率=14.8% / filled平均R=-0.18 / filled簡易PF=0.68 / missed=4件 / entry_not_reached=0件 / 終了=sl_hit=20件, missed_opportunity=4件, tp2_hit=4件, timeout=3件
- resistance_to_support_flip: 30件 / all=30件 / filled=26件 / filled勝率=11.5% / filled平均R=-0.29 / filled簡易PF=0.49 / missed=4件 / entry_not_reached=0件 / 終了=sl_hit=20件, missed_opportunity=4件, timeout=3件, tp2_hit=3件
- resistance_to_support_retest_confirmed: 30件 / all=30件 / filled=26件 / filled勝率=11.5% / filled平均R=-0.29 / filled簡易PF=0.49 / missed=4件 / entry_not_reached=0件 / 終了=sl_hit=20件, missed_opportunity=4件, timeout=3件, tp2_hit=3件
- failed_breakout_up_reversal: 17件 / all=17件 / filled=9件 / filled勝率=11.1% / filled平均R=-0.31 / filled簡易PF=0.54 / missed=8件 / entry_not_reached=0件 / 終了=missed_opportunity=8件, sl_hit=7件, tp2_hit=1件, timeout=1件
- trend_flip_early_up: 10件 / all=10件 / filled=7件 / filled勝率=14.3% / filled平均R=-0.07 / filled簡易PF=0.84 / missed=3件 / entry_not_reached=0件 / 終了=sl_hit=5件, missed_opportunity=3件, tp2_hit=1件, timeout=1件
- trend_flip_confirmed_up: 9件 / all=9件 / filled=9件 / filled勝率=11.1% / filled平均R=-0.26 / filled簡易PF=0.53 / missed=0件 / entry_not_reached=0件 / 終了=sl_hit=7件, timeout=1件, tp2_hit=1件

## opportunity reason 別
- market_map:support_to_resistance_flip: 83件 / all=83件 / filled=45件 / filled勝率=17.8% / filled平均R=-0.02 / filled簡易PF=0.96 / missed=38件 / entry_not_reached=0件 / 終了=missed_opportunity=38件, sl_hit=32件, tp2_hit=8件, timeout=5件
- market_map:failed_breakout_down_reversal: 31件 / all=31件 / filled=27件 / filled勝率=14.8% / filled平均R=-0.18 / filled簡易PF=0.68 / missed=4件 / entry_not_reached=0件 / 終了=sl_hit=20件, missed_opportunity=4件, tp2_hit=4件, timeout=3件
- market_map:resistance_to_support_flip: 30件 / all=30件 / filled=26件 / filled勝率=11.5% / filled平均R=-0.29 / filled簡易PF=0.49 / missed=4件 / entry_not_reached=0件 / 終了=sl_hit=20件, missed_opportunity=4件, timeout=3件, tp2_hit=3件
- soft_risk:suppress_long_high_wait: 1件 / all=1件 / filled=1件 / filled勝率=100.0% / filled平均R=2.40 / filled簡易PF=0.00 / missed=0件 / entry_not_reached=0件 / 終了=tp2_hit=1件
- soft_risk:suppress_long_high_wait+suppress_trend_flip_up_strong: 1件 / all=1件 / filled=1件 / filled勝率=100.0% / filled平均R=2.40 / filled簡易PF=0.00 / missed=0件 / entry_not_reached=0件 / 終了=tp2_hit=1件
- soft_risk:suppress_trend_flip_up_strong: 1件 / all=1件 / filled=1件 / filled勝率=0.0% / filled平均R=-1.00 / filled簡易PF=0.00 / missed=0件 / entry_not_reached=0件 / 終了=sl_hit=1件

## SL失敗分類
- late_wait_sl: 20件 / filled平均R=-0.90 / filled簡易PF=0.00 / 平均MFE=0.00 / 平均MAE=0.00 / 代表=20260525_070500, 20260525_030500, 20260524_230500
- trend_flip_long_sl: 10件 / filled平均R=-0.70 / filled簡易PF=0.00 / 平均MFE=0.00 / 平均MAE=0.00 / 代表=20260523_210500, 20260522_030500, 20260517_180500
- other_sl: 26件 / filled平均R=-0.58 / filled簡易PF=0.00 / 平均MFE=0.00 / 平均MAE=0.00 / 代表=20260601_000500, 20260531_220501, 20260531_150500

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

## proposal
- suppress_long_high_wait: long かつ wait>=60 は 17件 / filled平均R=-0.44 / filled簡易PF=0.40 のため、紙候補でも一段抑制候補。
- suppress_trend_flip_up_strong: 上方向転換系は 19件 / filled平均R=-0.17 / filled勝率=12.5% のため、強評価へ戻さない候補。
- require_execution_for_high_wait: wait>=60 群は execution 下限強化候補。対象 40件 / 平均 execution=18.5 / filled平均R=-0.30。
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

## P0補足集計

- data_status: `available`
- paper_positions rows: 570
- closed rows: 564
- filled rows: 279
- non-entered rows: 285
- missed_opportunity rows: 169
- entry_not_reached rows: 116
- exit_status counts: {'sl_hit': 222, 'missed_opportunity': 169, 'timeout': 25, 'tp2_hit': 32, 'entry_not_reached': 116}

### filled-only stats
- filled win rate: 11.5%
- filled avg R: -0.37
- filled PF: 0.47

### all closed stats for compatibility
- all closed win rate: 5.7%
- all closed avg R: 3.71
- all closed PF: 11.57

### counter_long_short_watch
- counter_long_short_watch rows: 0
- counter side counts: {}
- counter position_status counts: {}
- counter examples: none
- raw logs/csv: not committed
