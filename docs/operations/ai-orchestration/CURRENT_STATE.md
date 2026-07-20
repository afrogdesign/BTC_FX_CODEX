# CURRENT_STATE

last_updated: 2026-07-11

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- no API keys
- no private/account/order endpoints
- no runtime restart during normal product work
- no raw exchange export commit
- no `paper_positions.csv` integration unless explicitly approved
- human decides manually

## Current product focus

Current focus has moved from generic evidence / intraperiod / win-rate diagnostics to the Ver04-v2 manual-trading observation loop.
Ver04-v1 self-review / run-fingerprint checkpoint is complete, and Ver04-v2 is the active source working branch.

Primary objective:

```text
notification mail を受け取った人間が、
15分足を確認し、
攻めの姿勢で勝てる manual trading support system を作る。
```

Automatic trading remains out of scope and later-stage only.

Ver03-v4 is prior baseline/history; Ver04-v1 is the prior active product branch.
Ver04-v2 is the current active source working branch for follow-on observation/review work.

## Current Phase4 self-improvement route

- source-of-truth route now includes `docs/operations/ai-orchestration/PHASE4_SELF_IMPROVEMENT_CONTROL_PLAN_20260707.md`
- recent Phase4 analysis / cue design / display planning is complete
- display/report-label-only implementation is complete
- commit `d2beafe` is pushed and runtime-applied
- active process path is `/Users/marupro/CODEX/100_MCP_Server/btc_monitor/main.py`
- no-send/render-only smoke passed
- no scoring / gate / threshold / trading logic / notification trigger changes were made
- human approval is required before any future implementation beyond display labels
- Phase4 tuning remains blocked

## Current operational posture

- Ver04-v2 runtime deployment is complete and reflected active.
- display/report-label-only implementation `d2beafe` is runtime-applied.
- First post-deploy normal notification observation passed for signal `20260705_050500`.
- Value Defense observation snapshot source now includes `attack_review_flags`.
- Existing snapshot backfill / upgrade path exists for previously published observations.
- latest local observation `20260706_030500` has been backfilled with `self_review_readiness` and `attack_review_flags`.
- Immediate posture is post-deployment observation / review only.
- Notification sending behavior remains unchanged.
- No immediate implementation is required unless observation finds an issue.
- Next strategic design focus is Big Chance / Failed Thesis Layer.
- guiding principle: failed thesis is opportunity.
- Next major design target is VALUE-DEFENSE-ENTRY-LAYER.
- Ver04-v2 VALUE-DEFENSE-ENTRY-LAYER Phase1-3 are complete and production-applied:
  - Phase1: report-only payload attached to `build_setup`
  - Phase2: detail HTML surface added
  - Phase3: judgment self-review dimensions added

## Current source-of-truth route

- `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
- `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
- `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
- `docs/operations/strategy/VER04_V1_INTEGRATED_PRODUCT_PLAN.md`

## Current design status

- Ver04-v1 integrated product plan is the active high-level plan.
- Self-improvement loop final design is now the active product route.
- Manual 15m win definition is the companion definition for evaluation semantics.
- Ver03-v4 remains the prior baseline/history.
- Product docs now define daily proxy / weekly review / biweekly ground truth loops.

## Current known status

- public HTML / notification mail / local dashboard は同じ判断ソースを維持する方針。
- notification mail is triage / entry point, not an order instruction.
- public HTML report is the current main manual-trading UI.
- local dashboard / app surface is confirmation and future automation foundation.
- diagnostic and post-evaluation remain report-only support.
- major turn / turning point diagnostics do not authorize manual or automatic entry.
- No restart / launchd action is required for the completed deployment.
- operator-facing version/mode labels are retired.
- public label is `BTCFX Manual Trading Report`.
- path slug is `manual-trading`.
- first observed notification/detail HTML used `logs/notifications_html/manual-trading/attention/20260705_050500.html` and `/manual-trading/attention/20260705_050500.html`.
- public/operator label check passed with no visible VerXX / `[CLI]` / `[API]` leakage in the subject/path surface.
- future verification should use commit hash, process path, generated_at, and report_fingerprint, not VerXX labels or SYSTEM_LABEL.
- breakout / inversion zones now have a report-only momentum confirmation layer for continuation / counter-bias risk visibility.
- report-only MACD indicator/scoring support is implemented, and report-only intraperiod breakout/breakdown alert candidate generation is implemented.
- live extra intraperiod mail sending is not enabled.
- notification sending behavior remains unchanged.
- executable Codex prompts emitted by ChatGPT should start with `AUTO_SEND`; `HUMAN_CHECK` means stop before emitting an executable prompt and consult the human.
- the project is now in a required post-deployment observation gate for the intraperiod / MACD buildout.
- this gate is mandatory before any live extra 15-minute sending decision.
- observation checklist: HTML/page usability, `15分足 早期注意` timing, MACD wording usefulness, actual chart movement match, counter-bias loss reduction, safety boundary visibility.
- actual judgment time and post-judgment self-review must be connected in the next design step.
- deterministic report-only judgment self-review link is now completed.
- normal notifications / generated HTML can be reviewed against self-review evidence when generated intraperiod inputs are available.
- judgment self-review now also carries deterministic review bucket / severity / human-review-required / improvement-focus fields for later human review.
- judgment self-review now also exposes a deterministic sanitized human review queue for quick row-level follow-up.
- judgment self-review now also exposes a deterministic rollup digest for operator next-action review.
- judgment self-review now also exposes a deterministic change-readiness gate to avoid premature tuning.
- judgment self-review now supports explicit `late` classification when late evidence is present.
- judgment self-review now includes deterministic run metadata and fingerprints for later report comparison.
- controlled runtime restart completed for the current Ver04-v2 production apply.
- active process path is `/Users/marupro/CODEX/100_MCP_Server/btc_monitor/main.py`.
- deployed process after restart was pid `46203` started `2026-07-06 15:47:09 JST`.
- Ver04-v2 VALUE-DEFENSE-ENTRY-LAYER is runtime-applied and running on runtime_head `1099a1ae8169f9b1d39d501e46597349a7c13475`.
- Value Defense UI rendered with real data and the reusable local observation snapshot tool was added as a report-only helper.
- `tools/build_value_defense_observation_snapshot.py` was added in commit `fb7a32f12deb94e699a9f57636c7c8ebc7137faa`.
- GitHub DNS / SSH reachability issue was operationally mitigated by local MCP source fallback; OS/network config was not changed.
- Phase4 scoring / gate tuning is blocked until future notified observation evidence exists and the human explicitly approves.
- display/report-label-only work is complete; tuning remains blocked.
- operator-facing version/mode labels are retired; public subject/title/path no longer needs VerXX or API/CLI updates and runtime verification should rely on commit hash, process path, generated_at, and report_fingerprint.
- safety boundary remains report-only / not FORMAL_GO / no automatic order / human decides manually.

## Followup notification lifecycle

- followup notification lifecycle is implemented, tested, checkpoint-pushed, and runtime-applied
- implementation commit is `b4f0089`
- runtime path remained the primary repo path
- current posture remains observation / review only
- compact email triage body is now used on the actual CLI runtime path as well
- the earlier compact body change was preview/API-oriented only; runtime CLI now uses the same compact body
- compact CLI email wording has been polished; safety boundary is canonical and paper-candidate heading only appears for pass/planned
- HTML reflection fix applied for Big Chance anchor and human-facing safety boundary display
- Big Chance / Failed Thesis Layer runtime apply is complete.
- implementation commit is `76e8b302078ff1d7fae9ed1abc4b581e247540b6`.
- replay artifact for `20260706_100500` has been generated for the failure-case review.
- no live Big Chance notification trigger was added.
- no scoring / gate / threshold tuning was performed.
- `invalidated` Big Chance candidates must be shown as replayed / expired, not as active top-priority opportunities.
- Phase4 remains blocked until future observation evidence and explicit human approval.

## Current operational blocker

- MCP working repo と old runtime execution repo の 2 つが存在し、混同すると unsafe。
- actual exchange export contains private account/trade info and must remain local/generated, not source-controlled.

## Current repo-operation mode

- MCP repo is source of truth.
- ChatGPT verifies via AFROG_MCP_Business.
- GitHub is not routine review path.
- Codex prompts should be compact and diff-based inside same thread.
- commit only at meaningful boundaries.
- TASK_LEDGER / handoff docs are not updated every task.

## Product backlog next candidate

- `BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER`
- Start this after observation or when the user explicitly requests implementation.
- `BTCFX-20260702-VER04-V1-INTRAPERIOD-LIVE-SEND-DECISION` only if the user explicitly approves live extra notification sending behavior.

## Completed history

- post-eval asset health audit completed
- daily proxy evaluator implemented
- implementation readiness package created
- Ver04-v2 runtime deployment complete

## Default avoid list

- `.venv312/`
- `logs/` unless explicitly scoped for audit
- generated CSV / report / HTML
- raw exchange exports under `local/manual_trade_imports/`
- full `TASK_LEDGER.md`


## Planning route update — 2026-07-10

The user approved direct documentation and AI routing for the manual trading practicality improvement plan.

New active planning sources:

- `docs/operations/ai-orchestration/MANUAL_TRADING_PRACTICALITY_EXECUTION_ROUTE_20260710.md`
- `docs/operations/strategy/MANUAL_TRADING_PRACTICALITY_IMPROVEMENT_PLAN_20260710.md`

Current planning decision:

- retain the strict formal candidate path as `A_FORMAL`
- add future report-only/manual-review layers `B_CHECK_15M`, `C_WATCH_ZONE`, and `STOP_OR_EXIT`
- do not relax existing gates
- normalize candidate rows into scenario lifecycle before changing notification volume
- connect actual trade ground truth before evidence-backed production tuning

This planning update does not change runtime behavior, scoring, gates, thresholds, notification triggers, or live mail sending.

This earlier preparation task is complete; the P2 importer hardening and archive transition are recorded below.


---

## 2026-07-10 importer-plan correction

Repo inspection confirmed that the actual-trade importer, manual trade linker, and ground-truth report already exist as early implementations. The active route is corrected accordingly.

Completed preparation:

- created `chatgpt/specs/active/20260710_manual_actual_trade_importer.md`
- selected `local/manual_trade_imports/YYYYMMDD/` as the canonical private input path
- added `local/manual_trade_imports/` to `.gitignore`
- defined deterministic merge/idempotency/conflict behavior
- preserved report-only / not FORMAL_GO / human-decided boundaries
- separated exchange ground truth from later human decision-event ground truth

The P2 implementation and validation were completed in the bounded Codex task recorded below; the next active phase is P3 linkage and ground-truth pipeline design.


---

## 2026-07-10 P2 completion and P3 activation

Manual actual trade importer hardening is complete and reviewed.

Reviewed capabilities:

- canonical `import-manual-actual-trades` command with legacy alias
- strict three-category workbook validation
- privacy-safe UID and filename handling
- deterministic file, batch, source-row, logical-key, row fingerprints
- merge/idempotency and corrected-export conflict handling
- process-level transactional replacement with rollback
- compact safe workbook failure handling
- dry-run planning fields and category-level worksheet counts
- downstream linker/report compatibility tests preserved

Reported local commits:

```text
d8ce83b
01746c1
c9b7715
```

Reported targeted validation:

```text
35 tests passed
targeted git diff --check passed
push: none
```

The P2 spec was archived to:

```text
chatgpt/specs/archive/20260710_manual_actual_trade_importer.md
```

New active P3 spec:

```text
chatgpt/specs/active/20260710_manual_trade_linkage_ground_truth_pipeline.md
```

P3 design correction:

- `manual_actual_trades.csv` is fill-level evidence, not human trade count
- position lifecycle is the preferred primary link target
- episode-level performance must be separated from fill-level monetary totals
- buy/sell must not be silently interpreted as long/short without position-action evidence
- only high/medium signal links may contribute to actual-backed aggregate comparison
- exchange exports cannot prove human intent, skip, watch, avoided loss, or missed opportunity

Current exact next task:

```text
BTCFX-20260710-MTP-LINKAGE-PIPELINE-SPEC-CHECKPOINT
```

This is a docs-only Git validation and commit task. P3 source implementation remains blocked until the new active spec is committed and reviewed.


---

## 2026-07-10 P3 completion and P4 activation

Manual trade linkage and ground-truth pipeline P3 is complete and reviewed.

Completed capabilities:

- hardened importer v2 input validation
- deterministic position-backed manual trade episodes
- unresolved and ambiguous association coverage
- signal linkage v2 with pre-entry eligibility, confidence bands, and tie handling
- fail-closed signal classification and input validation
- episode-level performance separated from fill-level monetary evidence
- high/medium actual-backed descriptive aggregation only
- atomic generated output replacement
- v2 CLI routes for episodes, links, and ground-truth report

Reported local commits:

```text
d7083bb
2a66c56
d5736ac
5988a87
```

Reported targeted validation:

```text
48 tests passed
targeted git diff --check passed
push: none
```

Archived P3 spec:

```text
chatgpt/specs/archive/20260710_manual_trade_linkage_ground_truth_pipeline.md
```

New active P4 spec:

```text
chatgpt/specs/active/20260710_manual_scenario_coverage_decision_events.md
```

P4 separates:

```text
scenario evidence
proxy market-path outcome
human decision/action
```

P4 does not implement A/B/C/STOP classification, production threshold changes, notification behavior changes, or runtime changes.

Current exact next task:

```text
BTCFX-20260710-MTP-SCENARIO-COVERAGE-DECISION-SPEC-CHECKPOINT
```


---

## 2026-07-10 P2 completion and P3 activation

Manual actual trade importer hardening is complete and reviewed.

Reviewed capabilities:

- canonical `import-manual-actual-trades` command with legacy alias
- strict three-category workbook validation
- privacy-safe UID and filename handling
- deterministic file, batch, source-row, logical-key, row fingerprints
- merge/idempotency and corrected-export conflict handling
- process-level transactional replacement with rollback
- compact safe workbook failure handling
- dry-run planning fields and category-level worksheet counts
- downstream linker/report compatibility tests preserved

Reported local commits:

```text
d8ce83b
01746c1
c9b7715
```

Reported targeted validation:

```text
35 tests passed
targeted git diff --check passed
push: none
```

The P2 spec was archived to:

```text
chatgpt/specs/archive/20260710_manual_actual_trade_importer.md
```

New active P3 spec:

```text
chatgpt/specs/active/20260710_manual_trade_linkage_ground_truth_pipeline.md
```

P3 design correction:

- `manual_actual_trades.csv` is fill-level evidence, not human trade count
- position lifecycle is the preferred primary link target
- episode-level performance must be separated from fill-level monetary totals
- buy/sell must not be silently interpreted as long/short without position-action evidence
- only high/medium signal links may contribute to actual-backed aggregate comparison
- exchange exports cannot prove human intent, skip, watch, avoided loss, or missed opportunity

Current exact next task:

```text
BTCFX-20260710-MTP-LINKAGE-PIPELINE-SPEC-CHECKPOINT
```

This is a docs-only Git validation and commit task. P3 source implementation remains blocked until the new active spec is committed and reviewed.


---

## 2026-07-10 P4 completion and P5 activation

P4 scenario normalization and manual decision-event infrastructure is complete and reviewed.

Reviewed capabilities:

- deterministic scenario identity and event identity
- candidate-to-scenario compression with explicit ambiguous grouping
- terminal-boundary and lifecycle handling
- detailed OHLCV coverage diagnosis
- append-only manual decision events with correction semantics
- effective decision coverage metrics
- deterministic JSON and Markdown coverage reports
- transactional output replacement and rollback
- compact CLI routes with expected error handling

Reported local commits reviewed through:

```text
106042937a39fff495d14de219eb1728038cc7f8
```

Reported targeted validation:

```text
101 tests passed
targeted git diff --check passed
push: none
```

Archived P4 spec:

```text
chatgpt/specs/archive/20260710_manual_scenario_coverage_decision_events.md
```

New active P5 spec:

```text
chatgpt/specs/active/20260710_manual_operator_classifier_offline.md
```

P5 design boundary:

- event-time offline classification only
- no hindsight outcome leakage
- output classes are `A_FORMAL`, `B_CHECK_15M`, `C_WATCH_ZONE`, and `STOP_OR_EXIT`
- existing gate results are retained and not recomputed
- thresholds are CLI/report comparison values, not production settings
- long and short use separate hypotheses
- no notification, gate, runtime, or order behavior changes

Current exact next task:

```text
BTCFX-20260710-MTP-OFFLINE-CLASSIFIER-SPEC-CHECKPOINT
```

This is a docs-only checkpoint before P5 source implementation.

---

## 2026-07-10 P5 completion and P6 activation

P5 offline operator classifier was completed and accepted by ChatGPT source review.

Reported completion commit:

```text
57d6151
```

Reported targeted validation:

```text
123 tests passed
targeted git diff --check passed
push: none
```

The P5 spec is archived at:

```text
chatgpt/specs/archive/20260710_manual_operator_classifier_offline.md
```

The active P6 source of truth is:

```text
chatgpt/specs/active/20260710_manual_operator_historical_replay.md
```

P6 remains offline/report-only and is not connected to production gates, notifications, runtime, APIs, or orders. P6 source implementation is complete and accepted.

P6 was subsequently implemented, accepted, and archived as recorded in the P6 completion section below.

---

## 2026-07-10 P6 completion

P6 historical replay implementation accepted at checkpoint `e870bd8`.

- reported targeted validation: `142 tests passed`
- P6 replay test methods: `19`
- event-time scenario-deduplicated policy replay
- `CURRENT_STRICT` / `A_ONLY` / `A_PLUS_B` / `A_PLUS_B_PLUS_C_OBSERVE` / `STOP_OVERLAY`
- C observation-only and STOP separate from entry policy
- selected-event proxy outcomes
- deterministic human decision attribution
- eligible closed actual-trade evidence
- per-policy monetary metrics
- deterministic CSV / JSON / Markdown transaction
- no production, runtime, notification, API, account, order, gate, scoring, or threshold changes
- archived P6 spec: `chatgpt/specs/archive/20260710_manual_operator_historical_replay.md`

---

## 2026-07-10 P7 completion and runtime apply

P7 is complete at accepted checkpoint `74047f1` (`74047f14bceb4644ec3ab86eb5d0e5c23d97541c`). Implementation commit was `dec4cb0` with acceptance correction `74047f1`; reported targeted validation passed with `74 tests`, and render-only smoke passed.

- primary repo is the active runtime path: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- existing launchd label: `com.afrog.btc-monitor`
- controlled restart completed; replacement PID `18923` was verified at apply time, not as a permanent runtime identity
- zero new Traceback / Exception / ERROR / fatal findings
- no live mail or notification artifact was created by validation
- archived spec: `chatgpt/specs/archive/20260710_manual_operator_shadow_surface.md`

P7 changed only the existing public detail HTML shadow surface. Production gate, scoring, threshold, notification, runtime, API, account, and order behavior were unchanged; the posture remains report-only and human-decided.

P7 is complete. P8 evidence-pipeline implementation is complete and accepted; operating evidence collection follows the approved automatic-evaluation doctrine and the archived implementation spec. P8 remains report-only / not `FORMAL_GO` / human-decided; no production behavior is changed.


---

## 2026-07-11 P8 evidence pipeline completion and operating transition

P8 evidence-pipeline implementation is complete and accepted.

Accepted commit chain:

```text
850ab24
759370b
29e0a39
0397fa8
```

Reported final validation:

```text
80 directly affected tests passed
P8 acceptance module: 23 tests
git diff --check: pass
push: none
```

Accepted capabilities:

- deterministic trial facts from P4/P5/P6 evidence
- P6 market outcome kept separate from P8 comparison status
- eligible high/medium actual trade episode evidence
- exception-only human review queue
- global no-trade STOP versus opposite-side P5 B/C counterfactual measurement
- unique-episode actual counts
- reproducibility fingerprints and method versions
- initial and practical P9 readiness fields
- atomic outputs, rollback, dry-run, deterministic rerun, and privacy-safe summaries

Archived P8 implementation spec:

```text
chatgpt/specs/archive/20260711_manual_operator_trial_evidence_pipeline.md
```

Current posture:

- P8 source implementation is complete
- P8 operating evidence collection is active
- `chatgpt/specs/active/` is empty except for `.gitkeep`
- P9 implementation has not started
- P9 remains evidence-gated and human-approved
- readiness is proposal eligibility only, not production authorization
- production classifier, gates, thresholds, notification behavior, runtime, API, account, and order behavior remain unchanged
- safety remains report-only / not `FORMAL_GO` / no automatic order / human decides manually

Current next work is corrected P8 operating evidence collection through the deterministic operating-cycle runner. No tuning is authorized from a single case.

## 2026-07-11 P8 operating-cycle runner

The single-cycle runner is implemented and locally smoke-validated. It uses the current candidate source, referenced signal context, fresh 15-minute OHLCV, accepted P4/P5/P8 functions, identity checks, manifest fingerprints, and an atomic all-output transaction. P8 evidence collection remains active and P9 remains blocked.

- command: `run-p8-operating-cycle`
- corrected baseline smoke: 206 candidate rows, 108 signals, 97 trial facts, 84 resolved, no-OHLCV 0
- ISSUE-001 qualified rows: 45; initial/practical P9 readiness: false/false
- first baseline remains diagnostic-only; corrected baseline is the current operating baseline
- no production classifier, gate, scoring, threshold, notification, runtime, API, account, order, or automatic-tuning behavior changed

Final runner acceptance record: implementation commit `9bee53a` is accepted; 26 operating-cycle, 25 P5, 23 P8, and 43 directly affected P4/intraperiod tests passed (117 combined). Generated smoke outputs remain local and uncommitted. Future cycles use `run-p8-operating-cycle`; P8 collection remains active and P9 remains blocked.

## 2026-07-11 P8 daily cycle automation

Repo-side daily automation is implemented and committed, but not installed or bootstrapped. `tools/run_p8_daily_cycle.py` invokes the accepted `run-p8-operating-cycle` once per JST date, writes date-scoped evidence and compact atomic latest status, and fails closed on incomplete actual episode/link pairs. The canonical plist schedules 11:30 JST; runtime apply is a separate task. P9 remains blocked and no automatic tuning is enabled.

## 2026-07-11 first P8 baseline (input-lineage diagnostic)

The first local generated-evidence baseline completed successfully, but it is retained as an input-lineage diagnostic only and is not tuning-valid. P4/P5/P8 outputs were generated without source, runtime, notification, or order changes.

- trial facts: 364 rows; resolved 22; unresolved 6; no-OHLCV 336
- scenario-deduplicated count: 364
- classes: `A_FORMAL=0`, `B_CHECK_15M=0`, `C_WATCH_ZONE=0`, `STOP_OR_EXIT=364`
- sides: `Long=200`, `Short=164`
- comparison: `aligned=12`, `too_defensive=10`, `too_aggressive=0`, `wrong_side=0`
- eligible actual rows: 0; unique actual episodes: 0; review queue: 10
- ISSUE-001 qualified rows: 0; opposite-side counterfactual B: 0; C: 0
- P9 initial readiness: false; practical readiness: false; validation window: not established
- maximum evaluated event timestamp: `2026-07-10T15:05:00.672704Z`

The five requested recent signals were absent from this older scenario-deduplicated fact set. The later corrected baseline below establishes that the absence was a candidate-lineage and OHLCV-freshness diagnostic, not a signal disappearance. This single baseline does not authorize tuning or P9.

## 2026-07-11 corrected P8 operating baseline

The first corrected run used the current candidate source, public 15-minute OHLCV, and an unmodified structured-major-level signal context. The preceding attempt stopped safely because P5 incorrectly validated structured support/resistance objects as scalar Decimals; commits `00c227d` and `0bd5d76` corrected validation and identity normalization without changing classification decisions, thresholds, gates, or scoring.

- candidate slice: 206 rows across 108 signals; OHLCV `2026-07-05T19:45:00+00:00` through `2026-07-11T00:15:00+00:00`
- outcome input: resolved TP/SL 181; pending 7; other unresolved 18; no-OHLCV 0
- scenario-deduplicated trial facts: 97; resolved 84; unresolved 13; no-OHLCV 0
- classes: `A_FORMAL=0`, `B_CHECK_15M=0`, `C_WATCH_ZONE=1`, `STOP_OR_EXIT=96`
- sides: `Long=48`, `Short=49`; comparison: `aligned=43`, `too_defensive=41`, `too_aggressive=0`, `wrong_side=0`
- eligible actual rows: 0; unique actual episodes: 0; review queue: 41
- ISSUE-001: 45 qualified proxy rows; counterfactual B 10; C 35; not eligible 46
- P9 initial readiness: false; practical readiness: false; validation window: not established
- maximum evaluated event timestamp: `2026-07-10T21:05:00.688162Z`

All five requested recent signals exist in candidate and scenario-event evidence. Where a signal was matched into an earlier scenario, the selected fact records that scenario's deterministic representative rather than treating the later signal as missing. P8 operating evidence collection remains active; P9 remains blocked and no tuning is authorized.

## 2026-07-11 P8 daily runtime apply

`com.afrog.btc-p8-operating-cycle` is installed and loaded in the primary iMac GUI domain with the daily 11:30 JST trigger. One manual proxy-only cycle succeeded: 206 candidates, 80 resolved, 13 unresolved, 2 no-OHLCV, 94 STOP and 1 C rows, ISSUE-001 44, review queue 39, and P9 readiness false/false. Generated evidence remains local and uncommitted. Scheduled-cycle verification and the 11:45 JST AI review remain pending; P9 is blocked and no production behavior changed.

## 2026-07-11 operator relative balance meter runtime apply

The display-only relative LONG/SHORT balance meter from implementation commit `4b33ed6` was applied to the active primary runtime at `2026-07-11T18:21:58+0900`; replacement PID `16144` is running under `com.afrog.btc-monitor`. Existing static HTML was not regenerated. Future generated detail pages contain the meter. No manual mail, notification cycle, classifier, gate, threshold, scoring, notification behavior, or order behavior changed. P8 evidence collection continues and P9 remains evidence-gated.

## 2026-07-11 operator hero layout hotfix runtime apply

The display-only hero layout fix from implementation commit `129cbba` was applied at `2026-07-11T19:12:16+0900` in the active primary repo `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`; replacement PID `18822` is running under `com.afrog.btc-monitor`. The non-executable execution label now renders as the compact hero token `WAIT`, while the full label remains in normal context text. The relative balance meter is unchanged, existing static HTML remains unchanged, and no manual mail or notification cycle was triggered. No notification behavior, scoring, classifier, gate, threshold, or order behavior changed. P8 evidence collection continues and P9 remains evidence-gated.


## 2026-07-12 P8 scheduled-cycle verification and turning-precursor investigation

The first scheduled P8 daily cycle completed successfully at 11:30 JST.

- candidate rows: 207
- candidate signals: 107
- scenarios: 84
- resolved: 74
- unresolved: 10
- no-OHLCV: 0
- review queue: 38
- ISSUE-001 qualified rows: 38
- P9 readiness: false / false
- errors: none

The completed daily-automation spec is archived at:

```text
chatgpt/specs/archive/20260711_p8_daily_operating_cycle_automation.md
```

A new P8 investigation is active for a missed turning / volatility precursor case observed at 2026-07-12 07:05 JST. The system correctly blocked formal execution but did not provide an early opposite-side chart-check warning before a material move.

Active spec:

```text
chatgpt/specs/active/20260712_turning_volatility_precursor_replay.md
```

The next task is deterministic offline replay only. It compares current notifications with symmetric Long/Short precursor hypotheses and measures lead time, large-move recall, false-warning burden, whipsaw, regime/phase splits, and validation-window results.

No scoring, market-map, classifier, threshold, gate, notification, mail, runtime, API, account, or order behavior is authorized to change. P9 remains blocked. Safety remains report-only / not FORMAL_GO / no automatic order / human decides manually.

## 2026-07-12 corrected turning / volatility precursor replay

The corrected replay discarded all pre-correction metrics and completed one public-OHLCV run after policy, episode, continuity, opportunity-denominator, and validation fixes.

- 2,872 signal rows; 28 independent realized-move opportunities; 2,194 precursor episodes
- current notification baseline: 637 episodes; independent large-move recall 0.392857
- Combined: 238 episodes / 26 resolved; precision 0.307692; independent recall 0.214286; false rate 0.384615; opposite rate 0.192308; whipsaw 0.115385; median lead 69.9885 minutes
- Combined validation: 6 resolved (UP 0 / DOWN 6); precision 0.333333; recall 0.5; false rate 0.666667; opposite rate 0; median lead 77.4875 minutes
- validation established, pinned case caught before move, exclusion gate pass, actual-backed count 0
- recommendation: `continue_shadow_collection`; P9 remains blocked and HUMAN_CHECK / ChatGPT review is next
- archived spec: `chatgpt/specs/archive/20260712_turning_volatility_precursor_replay.md`
- no production scoring, market-map, gate, notification, mail, runtime, API, account, or order behavior changed


## 2026-07-12 turning precursor replay acceptance and next shadow phase

The corrected turning / volatility precursor replay is accepted at commit `9f4f6a1`. All pre-correction metrics are invalid and discarded.

Corrected evidence shows that the pinned 07:05 missed-turn case is detectable offline, but the Combined policy is not ready for live notification use: overall recall is below the current notification baseline, validation has only six resolved Combined episodes, validation UP count is zero, validation false rate is 0.666667, and actual-backed count is zero. Recommendation remains `continue_shadow_collection`.

A new active spec now defines opt-in daily shadow collection:

```text
chatgpt/specs/active/20260712_turning_precursor_daily_shadow_collection.md
```

The next source task will reuse the existing daily P8 public OHLCV fetch and write date-scoped precursor evidence. The feature must remain disabled by default and must not modify launchd, schedule, mail, notifications, scoring, market-map, gates, thresholds, runtime, APIs, accounts, or orders. P8 collection continues and P9 remains blocked.
## 2026-07-12 opt-in turning precursor daily shadow completion

- opt-in shadow integration is implemented and bounded-validated through the P8 operating-cycle runner
- core cycle and precursor shadow succeeded with one reused public OHLCV fetch; signal slice 127, precursor episodes 175, resolved 26, realized opportunities 28
- Combined recall 0.25, precision 0.307692, false rate 0.384615, opposite rate 0.192308, whipsaw 0.115385, median lead 69.9885 minutes
- validation is established but one-sided (UP=0, DOWN=6); recommendation remains `continue_shadow_collection`; actual-backed count is 0
- installed daily schedule remains unchanged and the feature is disabled by default
- archived spec: `chatgpt/specs/archive/20260712_turning_precursor_daily_shadow_collection.md`
- P8 evidence collection continues; P9 remains blocked; runtime enablement requires separate HUMAN_CHECK approval
- no production scoring, notification, mail, launchd, runtime, API, account, order, or automatic-tuning behavior changed

## 2026-07-12 — Turning precursor shadow runtime enable approved

Human explicitly approved enabling the already validated turning precursor shadow in the installed daily P8 LaunchAgent.

- approved work: `BTCFX-20260712-P8-TURNING-PRECURSOR-SHADOW-RUNTIME-ENABLE`
- active spec: `chatgpt/specs/active/20260712_turning_precursor_shadow_runtime_enable.md`
- target label: `com.afrog.btc-p8-operating-cycle`
- intended change: add `--include-turning-precursor-shadow` exactly once
- schedule remains 11:30 JST
- source baseline: commit `f39375f`
- no manual P8 cycle during apply
- first normal scheduled cycle is the runtime acceptance event
- notification, mail, scoring, market map, thresholds, gates, UI, normal monitor runtime, API, account, and order behavior remain unchanged

## 2026-07-12 — Turning precursor shadow runtime enable partial / rollback

- source/runtime-enable commit `72d1733` is pushed to `origin/Ver04-v2`
- repository plist contains `--include-turning-precursor-shadow`
- repository tests and plist lint passed
- target `launchctl bootstrap gui/<uid>` failed with `Input/output error`
- target-only rollback restored the original installed plist SHA-256 `bfbf6020567ca957a7bb5d204e22cdc61217875f9c7206f8a3a248e62890e0a7`
- target label remains unloaded and installed shadow flag remains disabled
- normal monitor, notification, mail, scoring, gates and schedule were not changed
- active spec remains open pending bounded launchd registration diagnosis
## 2026-07-12 turning precursor shadow runtime enable

- source/runtime-enable commit: `72d1733`; origin matches local
- root cause was a stale registration of `com.afrog.btc-p8-operating-cycle` in the GUI domain after rollback
- target-only bootout and diagnostic re-registration resolved the state; committed shadow-enabled plist is now registered
- installed plist SHA-256: `843185cf3a8c4ba6c70f154c4566ec5b544146ecb466d7a8592cf0499403b92c`
- backup retained at `/Users/marupro/Library/LaunchAgents/_btc_monitor_backup_20260712_turning_shadow/com.afrog.btc-p8-operating-cycle.plist`
- loaded contract: primary repo paths, shadow flag exactly once, daily 11:30 JST, unchanged stdout/stderr
- first normal 11:30 JST shadow-enabled cycle remains pending; no manual P8 cycle was run
- P8 evidence collection continues; P9 remains blocked; no notification, mail, monitor, scoring, gate, threshold, API, account, order, or other LaunchAgent change
## 2026-07-12 side-aware MTF runtime apply

- accepted source commit `b805439` is applied to the existing primary monitor runtime
- target-only restart replaced PID `64053` with PID `82099`; launchd state remains running
- runtime path: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- future generated detail HTML and CSV rows now use side-aware action output; historical artifacts were not regenerated
- monitor.err delta contained no Traceback, Exception, fatal, or ERROR findings
- no score, gate, notification trigger, mail, schedule, API, account, position, or order behavior changed
- P8 evidence remains report-only; P9 remains evidence-gated

## 2026-07-12 structural-priority runtime apply

- accepted source commit `9a32e42` applied at `2026-07-12T17:18:21+09:00`; target-only kickstart replaced PID `659` with PID `15029` and state remains running
- primary runtime path remains `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- top meter uses 4H 75% / 1H 25% structural priority, bounded to 10–90 with a 45–55 neutral band; turning-watch and structural/15M alignment remain separate
- tactical scores remain independent short-term execution scores and side-aware 15-minute action, zones, SL, TP1, TP2 and no-chase remain unchanged
- future naturally generated HTML/CSV rows use the new output; historical artifacts were not regenerated
- monitor.err remained 0 bytes with no restart error; no scoring, gate, notification, mail, schedule, API or order behavior changed


---

## 2026-07-12 current checkpoint correction

- structural-priority source commit `9a32e42` is deployed to the active primary monitor runtime
- runtime apply completed at `2026-07-12T17:18:21+09:00`
- runtime path is `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- the first naturally generated normal post-apply signal remains the acceptance event
- latest inspected signal `20260712_080500` was generated at `2026-07-12T17:05:00.635403+09:00`, before the apply, and is not an acceptance sample
- no manual cycle, additional restart, historical regeneration, or tuning is authorized
- safety remains report-only / not `FORMAL_GO` / no automatic order / human decides manually


## 2026-07-13 operator-action Japanese UI source acceptance

The public detail HTML redesign for the operator-action and current trading-decision blocks is accepted by ChatGPT MCP source review through Codex-reported commit `03ec916`.

- primary visible wording is Japanese rather than raw action/state tokens
- known Long / Short B headlines remain directional
- unknown-side B and generic non-B headlines fail closed without implying Long or Short
- STOP remains `新規見送り・保護確認`
- no-chase wording is not duplicated
- matching regression assertions are present
- Codex reported the targeted notification detail-page unittest and `git diff --check` passed
- implementation spec archived to `chatgpt/specs/archive/20260713_operator_action_japanese_ui_redesign.md`
- runtime apply has not been performed and requires separate explicit human approval
- no notification, mail, classifier, score, gate, threshold, API, account, position or order behavior changed


---

## 2026-07-14 structural-priority acceptance

- first post-apply normal cycle: `20260712_090501`, `2026-07-12T18:05:01.094661+09:00`; not notified, so no detail HTML
- first complete CSV / signal / HTML sample: `20260712_100500`, `2026-07-12T19:05:00.322398+09:00`
- structural priority: Long 43 / Short 57; side `short`; strength `slight`; label `Short やや優勢`
- turning: `short / confirmed`; alignment: `countertrend`
- side-aware primary action: `LONG B_CHECK_15M / armed`; Short: `STOP_OR_EXIT / invalidated`
- CSV check passed: required structural and side-aware fields, 10–90 points, lower-case strength, no pre-apply `Short priority` wording in the acceptance row
- HTML check passed: structural heading, Japanese direction heading, 4H 75% / 1H 25% note, structural points and label, turning, alignment, side-aware action, short-term scores, entry zones, SL, TP1, and TP2
- later natural late sample `20260713_020500` displayed `追いかけ禁止`
- no source defect found; no tuning is authorized from one case


---

## 2026-07-14 operator-action Japanese UI runtime apply

Human deployment report:

- target: `com.afrog.btc-monitor`
- old PID: `15029`; replacement PID: `90160`
- execution path: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- UI source: commit `03ec916`
- no mail send, manual cycle, or other-service operation
- no post-restart `monitor.err` addition reported

Directly verified through AFROG MCP:

- `logs/runtime/startup_status.json` records PID `90160`, timezone `Asia/Tokyo`, and startup timestamp `2026-07-14T00:57:07.931511+09:00`
- the first scheduled post-restart cycle completed naturally as signal `20260713_160500` at `2026-07-14T01:05:00.662420+09:00`
- that cycle was `signal_tier=normal`, `was_notified=false`, and `detail_page_status=disabled`

Assessment:

- replacement startup and continued scheduled execution are confirmed
- the first post-restart cycle produced no notification HTML, so the Japanese UI runtime rendering is not yet artifact-accepted
- wait for the first naturally notified post-restart detail HTML; do not run a manual cycle or regenerate historical artifacts
- runtime remains report-only / not FORMAL_GO / no automatic order / human decides manually


---

## 2026-07-20 current operational refresh

Direct AFROG MCP verification:

- `chatgpt/specs/active/` is empty except for `.gitkeep`; no source implementation task is active
- normal monitor artifacts continue through signal `20260720_090500` at `2026-07-20T18:05:00.302090+09:00`; that latest inspected cycle was non-notified
- a current notified main artifact exists for signal `20260720_080500` at `2026-07-20T17:05:00.912813+09:00`
- generated HTML: `logs/notifications_html/manual-trading/main/20260720_080500.html`
- Japanese operator-action runtime rendering is accepted from natural artifacts:
  - directional Japanese headline and Long / Short cards are present
  - timeframe chips and A / B / C / STOP guide are Japanese
  - safety wording, entry zones, invalidation, TP1 and TP2 are preserved
  - `SHORT B_CHECK_15M` is absent from the primary UI of the inspected main artifact
  - natural late follow-up `20260720_070500` displays `追いかけ禁止`; the duplicate form `追いかけ禁止 / 追いかけ禁止` is absent
- `monitor.err` and `p8_daily_cycle.launchd.err` are currently zero bytes
- `logs/runtime/startup_status.json` still records the 2026-07-14 startup PID `90160`; this is a startup record, not a newly verified current process identity
- `logs/runtime/monitor.pid` contains an older inconsistent value, so it is not used as current runtime evidence

Latest P8 scheduled evidence cycle:

- report date: `20260720`; status: success; finished `2026-07-20T11:30:03.866119+09:00`
- 212 candidate rows / 114 signals / 94 scenarios; 86 resolved / 8 unresolved / 0 no-OHLCV
- class output: `STOP_OR_EXIT=94`; comparison: aligned 50 / too defensive 36
- ISSUE-001 qualified rows: 45; counterfactual B 6 / C 39
- turning precursor shadow is enabled and succeeded; recommendation remains `continue_shadow_collection`
- turning precursor validation remains thin and asymmetric: UP 1 / DOWN 4; actual-backed count 0
- actual input status is missing; eligible actual episodes 0
- P9 initial and practical readiness remain false; no tuning is authorized

Assessment:

- Japanese UI runtime acceptance is complete
- P8 automatic report-only evidence collection is operating normally
- no source defect or immediate Codex task is identified
- current posture returns to normal observation and evidence collection
- safety remains report-only / not FORMAL_GO / no automatic order / human decides manually


---

## 2026-07-20 macro structure / volatility product-design activation

Human live-trading feedback confirms that the current notification HTML is useful, especially the 15-minute chart with Entry / SL / TP and the Big Chance block as an approximate next-regime cue. The main usability and prediction gap is now more specific:

- the current structural-priority score is useful as a trend vote but does not show a complete higher-timeframe market location
- the operator needs reliable broad support/resistance, range edges, midpoint/equilibrium, and expected travel to the next major level
- repeated large moves around broad structural midpoint conditions are not directly represented in the current replay contract
- current tactical direction and later next-regime risk need separate explicit forecasts
- the large operator-action block is difficult to scan; its redesign is deferred until the underlying macro evidence is improved

New strategy plan:

```text
docs/operations/strategy/MACRO_STRUCTURE_VOLATILITY_SELF_IMPROVEMENT_PLAN_20260720.md
```

New active specification:

```text
chatgpt/specs/active/20260720_macro_structure_volatility_evidence_layer.md
```

The planned route is:

```text
M1 offline macro structure / reliable-level / midpoint / expansion evidence
→ M2 optional P8 auxiliary shadow
→ M3 Big Chance next-regime contract
→ M4 chart-first operator hierarchy shadow UI
→ M5 bounded P9 champion/challenger proposal engine
→ M6 separate human-reviewed runtime proposal
```

No source, scoring, gate, threshold, notification, mail, runtime, API, account, position, or order behavior changed during this planning update. M1 remains report-only and implementation requires a separate bounded approval/task.


## 2026-07-20 macro-structure research correction

The M1 plan was corrected before source implementation.

User clarification:

- midpoint-driven expansion was a personal hypothesis, not a confident product requirement
- reliable higher-timeframe support/resistance remains mandatory
- the design should use stronger research and measurable mechanisms for directional pressure and large moves

Research review established:

- support/resistance can contain predictive information, but level quality varies and must be measured
- clustered orders provide a plausible mechanism for reversal near levels and momentum after crossing
- order-flow imbalance and market depth are relevant to short-horizon price impact
- realized volatility is persistent and regime dependent
- low volatility does not guarantee immediate expansion
- Bitcoin jump evidence supports order-flow imbalance, aggressive participation, and spread/liquidity conditions as auxiliary precursors in the studied sample
- all transfer to MEXC BTC_USDT requires local event-time walk-forward validation

Created:

- `docs/operations/strategy/MACRO_STRUCTURE_RESEARCH_BASIS_20260720.md`

Updated:

- parent macro-structure plan with a reliable-level-first correction
- active M1 spec with precedence Section 23
- `NEXT_ACTION.md` for corrected Codex execution

Corrected M1 doctrine:

```text
reliable structural levels
→ reliability history
→ structural location
→ volatility state
→ pressure / imbalance evidence
→ rejection, break, acceptance, or reclaim activation
→ next reliable target
→ outcome evaluation
```

Midpoint/equilibrium is optional and cannot independently determine direction or expansion.

No source, scoring, gate, notification, mail, runtime, API, account, position, or order behavior changed in this correction.


---

## 2026-07-21 M1 macro evidence acceptance and M2 activation

M1 macro structure / volatility evidence is accepted after ChatGPT source and focused-test review through reported commit `663288b`.

Accepted M1 capabilities:

- event-time confirmed 1H/4H structural levels
- stable level identity and role-aware lifecycle
- prior-only reliability history
- separate volatility state, expansion risk, directional activation, and reliable target
- independent realized-move opportunities
- same-opportunity policy comparison and chronological validation
- event-time policy episode deduplication
- fail-closed missed-move diagnosis
- deterministic atomic five-output replay

Reported final validation:

- macro replay tests: 26 passed
- macro CLI tests: 4 passed
- bounded FIX-10 replay: passed
- `git diff --check`: passed

M1 remains offline and report-only. No production scoring, gate, threshold, classifier, Big Chance, structural-priority, HTML, notification, mail, runtime, API, account, position, or order behavior changed.

Archived M1 spec:

```text
chatgpt/specs/archive/20260720_macro_structure_volatility_evidence_layer.md
```

New active M2 spec:

```text
chatgpt/specs/active/20260721_macro_structure_p8_auxiliary_shadow.md
```

M2 is an optional, disabled-by-default P8 auxiliary shadow integration. It may collect date-scoped macro evidence but may not change the installed schedule, plist, runtime, notifications, mail, production analysis, scoring, gates, thresholds, classifiers, APIs, accounts, positions, or orders.

Current next task:

```text
BTCFX-20260721-MACRO-STRUCTURE-P8-AUXILIARY-SHADOW
```

Safety remains report-only / not FORMAL_GO / no automatic order / human decides manually.


---

## 2026-07-21 M2 macro-structure auxiliary shadow acceptance

M2 is accepted at source commit `8aee427`.

- archived spec: `chatgpt/specs/archive/20260721_macro_structure_p8_auxiliary_shadow.md`
- the optional macro shadow remains disabled by default
- context rows are used only for event-time episode continuity
- published events, levels, counts, metrics, splits, dates, diagnostics, gates, and denominators are performance-only
- the fresh bounded wrapper run succeeded with 124 events, 94 levels, and 33 independent opportunities
- wrapper status, cycle manifest, and cycle summary agreed on macro shadow `success`
- recommendation remains `continue_shadow_collection`
- generated artifacts remain local and uncommitted
- M3 has not started; no active spec is open
- no runtime, launchd, notification, mail, production analysis, scoring, gate, threshold, classifier, API, account, position, or order behavior changed
- safety remains report-only / not `FORMAL_GO` / no automatic order / human decides manually


---

## 2026-07-21 M3 accepted; M4 render shadow active

- M3 accepted implementation head: `4f97a55`
- accepted M3 spec: `chatgpt/specs/archive/20260721_macro_next_regime_offline_shadow.md`
- accepted bounded replay: 124 events / 58 policy episodes
- recommendation remains `continue_shadow_collection`
- candidate and frozen Big Chance baseline are independent
- obstruction, family conflict, schema, reference, and missing evidence boundaries fail closed
- complete pre-outcome episode identity, multi-horizon metrics, required splits, chronological validation, and atomic outputs are accepted
- production Big Chance, notification, mail, scoring, gates, runtime, APIs, accounts, positions, and orders remain unchanged
- active phase: M4 local operator hierarchy render shadow
- active spec: `chatgpt/specs/active/20260721_macro_operator_hierarchy_render_shadow.md`
- M4 is render-only and does not authorize live UI deployment

---

## 2026-07-21 M3 validation-window correction pending

- the prior M3/M4 transition is withdrawn pending `BTCFX-20260721-MACRO-NEXT-REGIME-OFFLINE-SHADOW-FIX-04` review
- active spec: `chatgpt/specs/active/20260721_macro_next_regime_offline_shadow.md`
- M3 remains offline, report-only, and its recommendation remains `continue_shadow_collection`
- M4 is preserved only as inactive draft `chatgpt/specs/archive/20260721_macro_operator_hierarchy_render_shadow_draft.md`; implementation has not started
- FIX-04 covers eligible-event JST validation dates, candidate-only concentration, and explicit 3H primary gate reporting
- no runtime, production, notification, mail, scoring, gate, threshold, classifier, API, account, position, or order behavior changed
