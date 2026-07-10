# AI Orchestration Control

last_updated: 2026-07-10
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
- P8 is pending human decision

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
BTCFX-20260710-MTP-P8-HUMAN-MANUAL-TRIAL-DECISION
```

Mode:

```text
HUMAN_CHECK
```

Task type:

```text
PRODUCT / TRADING / SAFETY DECISION
```

State:

- no executable Codex task is authorized yet
- no P8 source implementation is authorized
- no P8 active spec is created in this closeout
- human must first decide the bounded manual-trial contract
- P8 cannot introduce automatic orders
- live extra notification sending remains unapproved
- production gate or threshold tuning remains unapproved
- P8 must define how A/B/C/STOP observations and human actions are recorded without treating candidates as orders

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
- P8 human manual trial only after explicit product/safety approval and a new active spec
- production tuning only after adequate ground truth and explicit human approval
