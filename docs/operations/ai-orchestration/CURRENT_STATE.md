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
