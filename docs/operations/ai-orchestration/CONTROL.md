# AI Orchestration Control

last_updated: 2026-07-11
repo: `afrogdesign/BTC_FX_CODEX`
primary_mcp_working_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
frozen_old_runtime_execution_repo: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
branch_source_rule: `read from git status --short --branch and CURRENT_STATE.md, not from chat history`

## Current State

- repo-local orchestration default is MCP primary
- normal Codex task is local edit + local validation + local commit + compact report
- routine GitHub push is outside default scope unless checkpoint is explicitly requested
- old runtime execution repo must not be edited, run, inspected, or synced in normal MCP tasks
- current product objective is practical human-operated BTC manual trading support
- Ver04-v2 source/runtime observation posture remains in effect
- display/report-label work is runtime-applied
- notification sending behavior remains unchanged
- Phase4 tuning remains blocked
- manual trading practicality plan and AI execution route are now active planning sources
- planning route approval does not authorize scoring, gate, threshold, notification, or runtime changes
- P7 shadow surface is complete, checkpointed and runtime-applied
- P8 evidence pipeline implementation is complete; operating evidence collection uses the bounded cycle runner under the approved P8/P9 operating doctrine
- P8 daily cycle wrapper and canonical launchd plist are repo-implemented; runtime installation remains a separate approved task
- Operator relative balance meter commit `4b33ed6` is runtime-applied in the primary repo; existing static pages remain unchanged and future generated detail pages contain the display-only meter

## Current Objective

Build a practical human-operated BTC manual trading support system.

```text
notification mail を受け取った人間が、
15分足を確認し、
攻めの姿勢で勝てる manual trading support system を作る。
```

Immediate planning objective:

```text
厳格なA候補の品質を維持する。
B候補で人間が15分足確認できる実践機会を増やす。
C候補で未到達scenarioを監視する。
STOPで新規停止・利確・撤退を支援する。
候補行をscenarioへ圧縮する。
actual trade ground truthでproxyを補正する。
```

## Active planning route

Read in this order for manual trading practicality work:

1. `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
2. `docs/operations/ai-orchestration/MANUAL_TRADING_PRACTICALITY_EXECUTION_ROUTE_20260710.md`
3. `docs/operations/strategy/MANUAL_TRADING_PRACTICALITY_IMPROVEMENT_PLAN_20260710.md`
4. `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
5. `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
6. `docs/operations/ai-orchestration/PHASE4_SELF_IMPROVEMENT_CONTROL_PLAN_20260707.md`

## Current practicality decision

The system already has strong candidate generation and safety logic.

The current deficiency is primarily the conversion from internal candidates into practical human actions, together with scenario deduplication and actual-trade calibration.

Approved planning model:

- `A_FORMAL`: retain current strict formal candidate quality
- `B_CHECK_15M`: conditional candidate requiring human 15m confirmation
- `C_WATCH_ZONE`: monitor zone and promotion condition
- `STOP_OR_EXIT`: stop new entry and prioritize exit / take-profit / protection

These labels are an operator action layer only.

They do not replace or relax:

- `trade_execution_gate`
- `phase1b_lite_gate`
- `opportunity_gate`
- current no-trade safety logic

## Safety Boundary

- Report-only.
- Not `FORMAL_GO`.
- No automatic order.
- No API keys.
- No private/account/order endpoints.
- No runtime restart during normal product work.
- No notification send behavior change without explicit approval.
- No raw exchange export commit.
- No `paper_positions.csv` integration unless explicitly approved.
- Public HTML / mail / dashboard must not diverge in trading logic.
- Human decides manually.

## Hard product prohibitions

- Do not relax `trade_execution_gate`.
- Do not change `phase1b_lite_gate` without explicit human approval.
- Do not relax `opportunity_gate` without explicit human approval.
- Do not increase `paper_orders planned` as an objective.
- Do not restore `trend_flip_confirmed_up` to strong evaluation without evidence.
- Do not promote Phase 1B formally without approval.
- Do not treat candidate rows as independent scenarios.
- Do not mix unresolved / no_ohlcv rows into win-loss claims.
- Do not convert review cues into entry rules.
- Do not tune from a single example.

## Active spec rule

- Check `chatgpt/specs/active/` before implementation.
- If active spec is empty, do not implement source.
- Create one next-phase active spec only.
- If an active spec exists, treat it as the implementation source of truth.
- If the active spec conflicts with current planning route or state, create a spec-correction task instead of implementing.
- Archive completed specs.

## Current phase route

```text
P1 actual trade importer spec
→ P2 importer implementation
→ P3 actual trade to signal/scenario linking
→ P4 coverage and scenario normalization
→ P5 offline A/B/C/STOP classifier
→ P6 historical replay
→ P7 shadow surface
→ P8 human manual trial
→ P9 evidence-backed tuning review
```

One task must cover one phase or one narrow subtask only.

## Current next task

```text
BTCFX-20260711-MTP-P8-EVIDENCE-PIPELINE
```

Mode:

```text
BOUNDED_CODEX
```

Task type:

```text
P8 SOURCE IMPLEMENTATION / REPORT-ONLY
```

State:

- automatic market-path evaluation and actual-trade evidence joining are approved by the P8/P9 operating specification
- human input remains limited to ambiguous or intent-dependent exceptions
- no production classifier, gate, threshold, notification, runtime, or order behavior is authorized to change
- P9 remains proposal-first and requires explicit human approval

## Validation Rules

- Task-specific minimal validation only.
- Docs-only changes: `git diff --check`.
- Python code changes: targeted `./.venv312/bin/python -m unittest <tests>`.
- CLI/report builder changes: relevant CLI/report validation only.
- Repeated status checks are not implied.
- Exchange export import work must be local-file only and must not call exchange APIs.
- Raw exchange files must not be committed.

## Operation Mode

- default fixed-scope implementation mode: `BOUNDED_CODEX`
- ChatGPT decides scope and writes the next exact task
- Codex performs implementation and validation only
- ChatGPT executable Codex prompts start with `AUTO_SEND`
- `HUMAN_CHECK` means stop before issuing an executable prompt
- local commit is allowed when checks pass
- push is checkpoint-only unless explicitly requested
- normal tasks avoid orchestration doc updates unless posture, next action, safety, or route actually changes

## Phase4 relation

- Phase4 post-deployment observation continues
- display/report-label implementation remains complete
- no scoring, gate, threshold, trading logic, or notification trigger changes are authorized
- new practicality planning route does not override Phase4 human approval gates
- actual trade ground truth and scenario normalization are prerequisites for evidence-backed tuning

## Evidence reminders

- strict `ENTRY_OK` proxy showed high but small-sample quality
- broader `RISKY_ENTRY` / `SWEEP_WAIT` sets contain possible manual-review opportunities
- Active Plan candidate rows greatly exceed strict main candidates
- candidate rows contain substantial duplication and are not independent opportunities
- `no_ohlcv` / unresolved coverage remains a major blocker
- short and long must be evaluated separately
- long active limit retest requires stronger location and defense-zone review

## Completed History

- P6 manual operator historical replay accepted at checkpoint `e870bd8`; spec archived
- P7 manual operator shadow surface accepted, checkpointed and runtime-applied; spec archived

- post-eval asset health audit completed
- daily proxy evaluator implemented and tested
- Ver04 runtime deployment and display/report-label work completed
- judgment self-review and Phase4 observation route established
- manual trading practicality improvement plan created
- manual trading practicality AI execution route created

## Deferred follow-up

- importer implementation after P1 spec approval
- actual trade linking after importer stabilization
- scenario normalization after linking contract is clear
- offline A/B/C/STOP classifier after coverage work
- P8 evidence-pipeline implementation is complete; operating evidence collection follows the approved doctrine and archived implementation spec; P9 tuning still requires explicit product/safety approval
- production tuning only after adequate ground truth and explicit human approval


---

## P8 completion control update — 2026-07-11

- P8 evidence-pipeline source implementation is complete and accepted.
- Accepted commit chain: `850ab24` -> `759370b` -> `29e0a39` -> `0397fa8`.
- The completed spec is archived at `chatgpt/specs/archive/20260711_manual_operator_trial_evidence_pipeline.md`.
- `chatgpt/specs/active/` is intentionally empty except for `.gitkeep`.
- Current operating mode is `HUMAN_CHECK`, not source implementation.
- Daily P8 automation is runtime-applied through `com.afrog.btc-p8-operating-cycle`; first manual cycle succeeded and scheduled-cycle verification is pending.
- P9 remains blocked until deterministic readiness evidence exists and the human explicitly approves a proposal.
- P9 readiness never authorizes automatic application or production mutation.
- No production classifier, gate, threshold, notification, runtime, API, account, or order behavior changed during P8.

Current next work ID:

```text
BTCFX-20260711-MTP-P8-OPERATING-EVIDENCE-COLLECTION
```

Safety remains:

```text
report-only / not FORMAL_GO / no automatic order / human decides manually

The operator hero layout hotfix (`129cbba`) is runtime-applied in the primary repo at `2026-07-11T19:12:16+0900` with replacement PID `18822` running. Long non-executable labels use the `WAIT` hero token; the relative balance meter is unchanged, static pages were not regenerated, and no manual mail or notification cycle was triggered. P8 evidence collection continues and P9 remains evidence-gated.
```


---

## 2026-07-12 control update — turning / volatility precursor replay

- P8 daily automation completed its first scheduled 11:30 JST cycle successfully and its active spec is archived.
- P8-ISSUE-008 is now collecting evidence for late or absent turning / volatility precursor alerts.
- active spec: `chatgpt/specs/active/20260712_turning_volatility_precursor_replay.md`
- current work ID: `BTCFX-20260712-P8-TURNING-VOLATILITY-PRECURSOR-REPLAY`
- mode: `BOUNDED_CODEX`
- task class: deterministic offline replay only
- required comparison: current notifications versus symmetric Long/Short precursor policies
- required metrics: large-move recall, precision, lead time, false-warning burden, whipsaw, Long/Short split, regime/phase split, validation window
- pinned case: signal `20260711_220501`, used as a regression example but not as sole tuning evidence
- no production scoring, market-map, classifier, threshold, gate, notification, mail, runtime, API, account, or order behavior change is authorized
- P9 remains blocked; an eligible replay result authorizes only a separate human-approved proposal
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## 2026-07-12 corrected turning precursor replay

- corrected replay completed once after discarding all pre-correction metrics
- 2,872 signal rows; 28 independent realized opportunities; Combined 238 episodes / 26 resolved
- Combined validation has 6 resolved episodes (UP 0 / DOWN 6) and fails proposal eligibility; recommendation remains `continue_shadow_collection`
- pinned 07:05 case was caught before the move; actual-backed count is 0
- next posture: HUMAN_CHECK / ChatGPT review
- no production scoring, market-map, gate, notification, mail, runtime, API, account, or order behavior changed


## 2026-07-12 turning precursor daily shadow control

- corrected precursor replay commit `9f4f6a1` is accepted as offline evidence only
- pinned 07:05 case was caught before the move
- evidence does not authorize live notification behavior
- Combined validation is one-sided (`UP=0`, `DOWN=6`) and validation false rate is 0.666667
- actual-backed count is 0
- current recommendation is `continue_shadow_collection`
- active spec: `chatgpt/specs/active/20260712_turning_precursor_daily_shadow_collection.md`
- next implementation is opt-in and disabled by default
- one existing public OHLCV fetch must be reused; no second fetch
- installed launchd invocation, schedule, notification and mail behavior remain unchanged
- runtime enablement requires a separate explicit human-approved task
- P8 continues; P9 remains blocked
- safety remains report-only / not FORMAL_GO / no automatic order / human decides manually
## 2026-07-12 opt-in precursor shadow integration

- source integration is bounded-validated; the feature remains disabled in the installed daily schedule
- one core P8 cycle and one auxiliary precursor shadow reused the same public OHLCV fetch
- validation is one-sided (UP=0, DOWN=6), recommendation remains `continue_shadow_collection`, and actual-backed count is 0
- next posture: `HUMAN_CHECK` / runtime-enable proposal review
- no production scoring, gate, threshold, notification, mail, runtime, API, account, order, or automatic tuning change occurred

## 2026-07-12 — Approved runtime boundary for precursor shadow

- HUMAN approval received to enable daily turning precursor shadow collection.
- Only `com.afrog.btc-p8-operating-cycle` may be changed.
- Only ProgramArguments addition allowed: `--include-turning-precursor-shadow`.
- Keep 11:30 JST schedule, primary repo paths, stdout/stderr, no RunAtLoad, and no KeepAlive.
- Back up the installed plist once, commit and push before runtime replacement, then bootout/bootstrap this label only.
- Do not manually execute the P8 cycle during apply.
- Do not restart `com.afrog.btc-monitor` or change mail/notification behavior.
- First normal scheduled cycle is the acceptance checkpoint.

## 2026-07-12 — P8 precursor shadow launchd diagnosis boundary

- repository source is ahead through pushed commit `72d1733`
- installed target plist is rolled back and shadow flag is disabled
- target label `com.afrog.btc-p8-operating-cycle` is unloaded
- next task is target-only read-mostly launchd diagnosis
- do not repeat bootstrap without collecting exact domain, registration, path, permission, ACL, xattr and launchd-log evidence
- one repair/bootstrap attempt is allowed only for a deterministic target-local cause
- no other LaunchAgent, normal monitor, notification, mail, scoring, gate, API, account or order behavior may change
## 2026-07-12 turning precursor shadow runtime boundary

- runtime enablement completed for `com.afrog.btc-p8-operating-cycle` only
- stale GUI-domain registration was cleared with a target-only bootout; committed plist is registered with the shadow flag once
- daily schedule remains 11:30 JST and all paths remain in the primary repo
- first normal scheduled cycle is the acceptance event; no manual P8 cycle, mail, notification, monitor restart, or other LaunchAgent operation occurred
- report-only / not FORMAL_GO / no automatic order / no automatic tuning; P9 remains blocked


---

## 2026-07-20 control refresh

This section supersedes the older `Current next task` block above.

- current work ID: `BTCFX-20260720-MTP-P8-OPERATING-EVIDENCE-COLLECTION`
- mode: `OBSERVE`
- active spec: none
- Japanese operator-action UI source and runtime artifact acceptance are complete
- current monitor evidence extends through signal `20260720_090500`; current process identity was not directly queried
- scheduled P8 cycle `20260720` completed successfully with 86 resolved, 8 unresolved and 0 no-OHLCV rows
- turning precursor shadow remains report-only with recommendation `continue_shadow_collection`
- actual-backed episode count remains 0 and P9 readiness remains false / false
- no source, runtime, notification or tuning task is currently authorized
- next action is continued automatic evidence collection and exception-only review
- safety remains report-only / not FORMAL_GO / no automatic order / human decides manually


---

## 2026-07-20 control update — macro structure / volatility evidence

- human live-trading feedback identifies higher-timeframe location and reliable support/resistance as the next product priority
- current structural priority remains a useful trend vote but is not a full range-location or volatility-expansion model
- new plan: `docs/operations/strategy/MACRO_STRUCTURE_VOLATILITY_SELF_IMPROVEMENT_PLAN_20260720.md`
- active spec: `chatgpt/specs/active/20260720_macro_structure_volatility_evidence_layer.md`
- current work ID: `BTCFX-20260720-MACRO-STRUCTURE-VOLATILITY-EVIDENCE-SPEC`
- mode: `HUMAN_CHECK`
- next implementation, if approved, is M1 offline evidence only
- no production structural-priority, Big Chance, HTML, scoring, gate, threshold, notification, mail, runtime, API, account, position, or order change is authorized
- normal monitor and P8 daily evidence collection continue unchanged
- safety remains report-only / not FORMAL_GO / no automatic order / human decides manually

## 2026-07-20 macro structure improvement implementation authorization

- current_work_id: `BTCFX-20260720-MACRO-STRUCTURE-VOLATILITY-EVIDENCE-IMPLEMENTATION`
- mode: `CODEX_EXEC`
- current active spec: `chatgpt/specs/active/20260720_macro_structure_volatility_evidence_layer.md`
- M1 source implementation is human-authorized.
- broader thread milestone is M5 shadow/self-improvement completion, but each phase requires ChatGPT acceptance and a separate bounded active spec.
- M1 must remain offline, deterministic, event-time, report-only, and must not edit production analysis, UI, notification, mail, runtime, scoring, gates, classifiers, or thresholds.
- the thread must stop before M6 runtime apply or any automatic production adoption.
- normal monitor and daily P8 operation continue unchanged during implementation.
- report-only / not FORMAL_GO / no automatic order / human decides manually.


## 2026-07-20 M1 research-backed scope correction

- current work remains `BTCFX-20260720-MACRO-STRUCTURE-VOLATILITY-EVIDENCE-IMPLEMENTATION`
- source implementation is authorized only under the corrected active-spec Section 23
- mandatory foundation: reliable 1H/4H structural levels, lifecycle, and prior-only reliability
- expansion risk and direction are separate outputs
- compression is a state variable, not proof of imminent expansion
- midpoint/equilibrium is optional exploratory context only
- order-flow, aggressive-side, depth, liquidity, repeated-test, rejection, break, acceptance, and reclaim evidence must remain independently inspectable
- missing microstructure inputs fail closed
- no production structural-priority, Big Chance, HTML, score, gate, threshold, notification, mail, or runtime change in M1
- next phases still require separate active specs and ChatGPT acceptance
- report-only / not FORMAL_GO / no automatic order / human decides manually


---

## 2026-07-21 M1 acceptance / M2 control update

- accepted M1 commit: `663288b`
- archived M1 spec: `chatgpt/specs/archive/20260720_macro_structure_volatility_evidence_layer.md`
- current active spec: `chatgpt/specs/active/20260721_macro_structure_p8_auxiliary_shadow.md`
- current work ID: `BTCFX-20260721-MACRO-STRUCTURE-P8-AUXILIARY-SHADOW`
- mode: `CODEX_EXEC`
- M1 acceptance covers deterministic offline macro evidence only
- M2 scope is an optional, disabled-by-default P8 auxiliary shadow
- M2 may reuse the core validated 15-minute OHLCV and fetch bounded public 1-hour and 4-hour OHLCV through the accepted fetcher
- M2 must preserve core P8 and turning-shadow success independently from macro-shadow failure
- no installed flag, plist, schedule, runtime, notification, mail, production analysis, scoring, gate, threshold, classifier, API, account, position, or order change is authorized
- M3 remains blocked until M2 source implementation and ChatGPT acceptance
- report-only / not FORMAL_GO / no automatic order / human decides manually


---

## 2026-07-21 M2 macro shadow acceptance control

- accepted M2 commit: `8aee427`
- archived M2 spec: `chatgpt/specs/archive/20260721_macro_structure_p8_auxiliary_shadow.md`
- active spec: none
- current mode: `OBSERVE`
- current work ID: `BTCFX-20260721-MACRO-STRUCTURE-P8-SHADOW-COLLECTION`
- bounded result: macro shadow `success`, 124 events, 94 levels, 33 independent opportunities
- recommendation: `continue_shadow_collection`
- M3 remains blocked pending sufficient accumulated evidence, a separate active spec, and human approval
- future bounded Codex work should default to `GPT-5.4-mini Medium`, use the active spec as source of truth, and add only missing regression coverage
- acceptance blockers must be separated from non-blocking improvement candidates; successful targeted validation must not be repeated without need
- no runtime enablement, notification, mail, production analysis, scoring, gate, threshold, classifier, API, account, position, order, or automatic-tuning change is authorized
- report-only / not `FORMAL_GO` / no automatic order / human decides manually


---

## 2026-07-21 M3 authorization

- M2 source commit `8aee427` and acceptance-doc commit `c2eed44` are accepted.
- The user authorized continuous progression through the remaining macro phases, subject to each active spec and safety boundary.
- current work ID: `BTCFX-20260721-MACRO-NEXT-REGIME-OFFLINE-SHADOW`
- active spec: `chatgpt/specs/active/20260721_macro_next_regime_offline_shadow.md`
- mode: `CODEX_EXEC`
- M3 is offline replay only and keeps the production Big Chance evaluator unchanged.
- M4 and M5 require later separate active specs after preceding acceptance.
- M6 remains a human-reviewed bounded runtime proposal; no automatic production adoption is authorized.
- no notification, mail, scoring, gate, threshold, classifier, runtime, API, account, position, or order change is authorized in M3.
- safety remains report-only / not FORMAL_GO / no automatic order / human decides manually.


---

## 2026-07-21 M3 acceptance and M4 control boundary

- accepted M3 implementation head: `4f97a55`
- accepted M3 specification is archived
- active specification: `chatgpt/specs/active/20260721_macro_operator_hierarchy_render_shadow.md`
- current mode: `CODEX_EXEC`
- current objective: deterministic local chart-first hierarchy comparison
- M3 recommendation remains `continue_shadow_collection`; no policy promotion is authorized
- M4 may create only local self-contained HTML/JSON/Markdown shadow artifacts
- M4 must exclude future outcomes from view construction and retain unavailable evidence explicitly
- production detail page, notification, mail, daily wrapper, scoring, thresholds, gates, classifiers, deploy, runtime, APIs, accounts, positions, and orders are outside scope
- M5 cannot start until ChatGPT accepts M4 source and bounded artifact

---

## 2026-07-21 M3 FIX-04 control correction

- prior M3 acceptance and M4 activation are withdrawn pending validation-window review
- current work ID: `BTCFX-20260721-MACRO-NEXT-REGIME-OFFLINE-SHADOW-FIX-04`
- active spec: `chatgpt/specs/active/20260721_macro_next_regime_offline_shadow.md`
- M4 is an inactive preserved draft and implementation is not authorized
- current recommendation remains `continue_shadow_collection`
- FIX-04 is offline/report-only only; no production, runtime, notification, mail, scoring, gate, threshold, classifier, API, account, position, or order change is authorized


---

## 2026-07-21 M3 final acceptance / M4 control update

- accepted M3 head: `3ae30f4`
- accepted M3 spec: `chatgpt/specs/archive/20260721_macro_next_regime_offline_shadow.md`
- accepted M3 scope: offline, deterministic, report-only next-regime comparison
- accepted bounded evidence: 124 events, 12 candidate episodes, 46 baseline episodes, 7 eligible JST dates
- primary proposal-gate horizon: `3h`
- M3 recommendation: `continue_shadow_collection`
- M3 does not authorize production Big Chance, notification, mail, scoring, thresholds, gates, classifiers, runtime, APIs, accounts, positions, or orders
- active M4 spec: `chatgpt/specs/active/20260721_macro_operator_hierarchy_render_shadow.md`
- M4 authorization is local render-only hierarchy shadow; live UI deployment is not authorized
- current next work ID: `BTCFX-20260721-MACRO-OPERATOR-HIERARCHY-RENDER-SHADOW`


---

## M3 FIX-05 directive — eligible-date burden and validation quality

- active work: `BTCFX-20260721-MACRO-NEXT-REGIME-OFFLINE-SHADOW-FIX-05`
- active spec: `chatgpt/specs/active/20260721_macro_next_regime_offline_shadow.md`
- preserved M4 base: commit `5574a2e`
- preserved M4 draft: `chatgpt/specs/archive/20260721_macro_operator_hierarchy_render_shadow_draft.md`

Directive:

- pass explicit eligible-event JST date sets into M3 burden metrics
- use common denominators for candidate and baseline
- include zero-episode eligible dates
- include no-episode eligible validation rows in data-quality gating
- keep 3H as the primary gate horizon
- do not change policy semantics, thresholds, production, runtime, notification, mail, or orders
- do not start M4 FIX-01 or M5 before ChatGPT accepts FIX-05


## M3 FIX-05 acceptance and M4 FIX-01 control — 2026-07-21

- M3 FIX-05 accepted as offline/report-only only.
- accepted M3 head reported: `d576862`
- accepted M3 recommendation: `continue_shadow_collection`
- active spec: `chatgpt/specs/active/20260721_macro_operator_hierarchy_render_shadow.md`
- current work: `BTCFX-20260721-MACRO-OPERATOR-HIERARCHY-RENDER-SHADOW-FIX-01`
- preserved M4 implementation base: `5574a2e`
- M4 acceptance: pending
- M5: not started
- live UI deployment: prohibited
- production notification, mail, scoring, thresholds, gates, classifiers, runtime, APIs, accounts, positions, and orders: unchanged
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually
