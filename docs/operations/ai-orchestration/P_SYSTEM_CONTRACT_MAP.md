# P System Contract Map

更新日: 2026-07-25
対象: WP0 現行実装のread-only contract inventory

## Authority vocabulary

`formal_execution`は正式な実行候補の保守的な許可だけを表す。`display`は表示・判断補助、`notification`は通知送信判断、`offline_evaluation`は履歴評価、`qualitative_only`は説明・補助文脈である。複数scopeは、同じ値が複数の利用目的を持つのではなく、明示した範囲に限って使うことを示す。

## Contract inventory

| field / contract | authoritative owner | producer | version | consumers | authority scope | current lifecycle | duplicate / legacy / ambiguity notes | evidence path |
|---|---|---|---|---|---|---|---|---|
| score / `long_display_score`, `short_display_score`, `score_gap` | scoring | `compute_scores` | `legacy_unversioned` | bias、setup、gate、report | display | active | scoreはconfidence、shadow、priority points、AI confidenceと同義ではない | `src/analysis/scoring.py`; `main.py:786` |
| confidence / direction・execution・wait shadow | scoring / signal context | `compute_scores` and main result assembly | `legacy_unversioned` | setup、formal gate、P5 comparison | display, formal_execution, offline_evaluation | active | machine confidence系を単一confidenceへ潰さない | `src/analysis/scoring.py`; `src/trade/execution_gate.py` |
| Market Map | market-map builder | `build_market_map` | `v1` | scoring、setup、operator decision、display | display | active | Macro構造入力とは別owner。flagsとlevelsの意味を混同しない | `src/analysis/market_map.py:434-553` |
| setup / RR | RR/setup builder | `build_setup`, `choose_primary_setup` | `legacy_unversioned` | activation、execution、plan | formal_execution, display | active | setup readinessはexecution許可そのものではない | `src/analysis/rr.py`; `main.py:1170-1206` |
| Phase1 activation | activation | `determine_phase1_activation` | `legacy_unversioned` | execution gate、observation context | formal_execution, display | active | watchは`watch_reference_only`でありformal laneの置換ではない | `src/trade/activation.py:6-27` |
| trade execution gate | execution gate | `determine_trade_execution_gate` | `legacy_unversioned` | order-adjacent report、operator decision、P5 fields | formal_execution | active | 現行formal execution候補の唯一のgate authority。他gateは置換不可 | `src/trade/execution_gate.py:13-41`; `main.py:1248` |
| observation gate | observation gate | `determine_phase1_observation_gate` | `legacy_unversioned` | opportunity、operator surface | display, offline_evaluation | active | formal gateの置換ではない | `src/trade/observation_gate.py:90-170` |
| phase1b lite gate | phase1b evaluator | `determine_phase1b_lite_gate` | `legacy_unversioned` | opportunity、shadow/report | display, offline_evaluation | active | lite opportunity lane。formal executionを許可しない | `src/trade/phase1b_lite.py:32-87` |
| opportunity gate | opportunity aggregator | `determine_opportunity_gate` | `legacy_unversioned` | display、P5/P8 evidence | display, offline_evaluation | active | execution/phase1b/observationの結果を分類するがformal gateを置換しない | `src/trade/opportunity_gate.py:147-254` |
| Active Trade Plan | active-plan builder | `build_active_trade_plan` | `active_trade_plan_v1` | side-aware、HTML、operator surface | display, formal_execution | active | 計画情報。単独では実行許可ではない | `src/trade/active_plan.py:407`; `main.py:1312` |
| side-aware MTF | side-aware action | `evaluate_side_aware_mtf_action` | `side_aware_mtf_action.v1` | structural priority、operator decision、display | display | active | Long/Short別の表示・行動補助。formal gateの置換ではない | `src/analysis/side_aware_mtf_action.py:8-9,161-202` |
| structural priority | structural priority | `build_structural_priority` | `structural_priority.v1` | operator decision、display | display | active | priority pointsはscoreやconfidenceではない | `src/analysis/structural_priority.py:122-178` |
| operator decision | operator decision | `build_operator_decision` | `operator_decision.v1` | HTML、operator surface | display | active | gate resultを表示判断へ束ねる。注文許可ではない | `src/analysis/operator_decision.py:6-46`; `main.py:1336-1338` |
| notification trigger | notification trigger | `should_notify` | `legacy_unversioned` | mail/report dispatch | notification | active | notification authorityは`should_notify`系。AI advice/newsではない | `src/notification/trigger.py:157-294`; `main.py:1342` |
| AI advice | advice provider | `request_ai_advice` | `legacy_unversioned` (`ADVICE_VARIANT`のみ別定数) | qualitative display | qualitative_only | active | gate、score、notification trigger、orderを変更しない | `src/ai/advice.py`; `main.py:1355-1386` |
| news context | news context builder | `build_web_news_context_status` / `request_web_news_context` | `legacy_unversioned` | qualitative display、AI advice context | qualitative_only | active | notify確定後の任意補助。deterministic authorityではない | `src/ai/news_context.py`; `main.py:1355` |
| P5 classifier | manual operator classifier | `build_manual_operator_classifier` | `manual_operator_classifier.v4` | offline reports、P8 evidence | offline_evaluation | active | A/B/C/STOPはP5 offline taxonomy。production gateを再計算しない | `src/feedback/manual_operator_classifier.py:23-26,472-522` |
| P6 historical replay | historical replay | `build_manual_operator_historical_replay` | `manual_operator_historical_replay.v1` | offline policy comparison | offline_evaluation | accepted | classifier/method versionを跨ぐ単純合算・比較は禁止 | `src/feedback/manual_operator_historical_replay.py:23-24,280-336` |
| P8 operating/evidence cycle | operating cycle + trial evidence | `run_p8_operating_cycle` / `build_manual_operator_trial_evidence` | `manual_operator_operating_cycle.v1`; `manual_operator_trial_evidence.v1` | daily health、evidence report | offline_evaluation | active | daily healthは1 cycleの入力・lineage・成功可否。累積P9 readinessではない | `src/feedback/manual_operator_operating_cycle.py:30-32,406-493`; `src/feedback/manual_operator_trial_evidence.py:26-28,526` |
| Product P9 readiness/proposal boundary | Product evidence/readiness report | `build_manual_operator_trial_evidence` | `legacy_unversioned` readiness payload | human review only | offline_evaluation | active / not approved | Product routeは`program=P`, `phase=P9`。initial/practicalとも現状false | `src/feedback/manual_operator_trial_evidence.py:522-526` |
| Macro auxiliary input | Macro structure input/replay chain | macro structure builders and public OHLCV path | source-specific; absent common version is `legacy_unversioned` | Macro reports、P8 shadow | display, offline_evaluation | active | Market Mapとowner・authorityを分離。Product P9とは別route | `src/feedback/macro_structure_daily_operation.py`; `src/feedback/macro_structure_volatility_replay.py` |
| Macro proposal engine | Macro proposal engine | `run_macro_p9_proposal_engine` | `macro_p9_proposal_engine.v1` | Macro M5/M6 proposal report | offline_evaluation | active / shadow only | `program=M`のM5/M6 improvement proposal。Product `P/P9`ではない | `src/feedback/macro_p9_proposal_engine.py:18-22,685-838` |

## Non-substitutability rules

- `trade_execution_gate`だけが現行formal execution候補の権限を持つ。observation、phase1b、opportunity、side-aware MTF、operator decisionは置換しない。
- `active_trade_plan_v1`は計画情報であり、単独では実行許可ではない。
- `side_aware_mtf_action.v1`、`structural_priority.v1`、`operator_decision.v1`はreport/display層である。
- notification authorityは`should_notify`系であり、AI adviceやnews contextは`qualitative_only`である。
- P5のA/B/C/STOPとside-aware MTFのA/B/C/STOP表示は、類似語でもgenerationとauthorityが異なる。
- `legacy_unversioned`は欠落versionを推測せず記録した値であり、新旧evidenceの比較資格を与えない。

## Lifecycle

`active`は現在認可され未完了の作業契約、`accepted`は実装/evidenceを受理済み、`completed`は作業系列終了、`superseded`は新しい正本に置換済みを表す。archive/historyは履歴であり、current truthを上書きしない。

## Safety boundary

report-only / human-decided / no automatic tuning / no automatic phase promotion / no automatic order。source、gate、threshold、classifier、notification、runtime、mailはWP0で変更していない。

## P operational evidence acceptance locator

FIX2 implementation `1224a31f1126bdc17564192193e00a8224ee927e` produced the report-only current evidence bundle at `local/reports/p_evidence/p_current_generation/latest/` and the P8/P9 v2 shadow at `local/reports/p8_daily_v2/wp5_wp6_acceptance_20260724_fix2/`. The selected snapshot policy is `latest_accepted_snapshot_as_of_cutoff`; the cycle-derived cutoff is `2026-07-24T02:15:00Z`, and source HEAD resolution was automatic. Current P9 v2 is `baseline_available` with frozen proposal thresholds and frozen validation cohort still missing. Formal headline impact uses selected classification snapshots only; the formal gate remains unchanged and unapproved. All evidence is descriptive, `automatic_causal_claims=0`, `causality_status=not_claimed`, and `canonical_link_replacement=false`.
