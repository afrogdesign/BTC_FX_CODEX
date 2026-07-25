# AI Decisions

## DEC-20260725-015: Canonical actual evidence and generation boundaries

### Decision

- canonical actual input is provided; actual episodes and links are generated at 149/149.
- `DEC-20260721-012`の「actual inputとepisode/linkが存在しない」という部分をsupersedeする。旧decisionは当時のsnapshotとして履歴に残す。
- Product P9（`program=P`, `phase=P9`）はactual不存在ではなくevidence sufficiency不足により未承認である。
- P8 daily healthとP9 cumulative readinessを分離する。
- classifier/method versionを跨ぐ単純比較・単純合算を禁止し、version別segmentを保持する。version不明は`legacy_unversioned`とする。
- Product P9とMacro `program=M` M5/M6 proposal engine（既存module `macro_p9_proposal_engine.v1`）を区別する。
- safetyはreport-only / human-decided / no automatic tuning / no automatic orderとする。

### Consequences

Eligible actual rowsは2（high 0、medium 2）に留まり、P9開始、FORMAL_GO、production tuning、phase promotionは承認されない。P8 cycle成功はP9 readinessを自動的にtrueにしない。

## DEC-20260608-001: Ver03-v2 begins with AI operation anchors

Date: 2026-06-08
Status: accepted
Related work: BTCFX-20260608-048

### Decision

Ver03-v2 starts by rebuilding ChatGPT / Codex / future-agent operation anchors before returning to trading-system implementation.

### Reason

The previous workflow became too expensive because each Codex task repeated long context, created many detailed logs, and required frequent placeholder hash updates.

The new workflow fixes this by placing stable context in repository files:

- `AGENTS.md`
- `docs/operations/ai-orchestration/CONTROL.md`
- `docs/operations/ai-orchestration/TASK_LEDGER.md`
- `docs/operations/ai-orchestration/PROMPTS.md`

### Consequences

- Codex prompts should become short.
- Codex reports should be compact.
- ChatGPT must confirm repository state before issuing tasks.
- Product implementation resumes after the AI operation anchors are stable.

## DEC-20260608-002: First Ver03-v2 implementation target is Active Plan intraperiod outcome specification

Date: 2026-06-08
Status: accepted
Related work: BTCFX-20260608-051

### Decision

After AI orchestration anchors and NEXT_TASK simplification, Ver03-v2 should resume product work by specifying Active Plan intraperiod outcomes before writing source code.

### Reason

The roadmap shows that the current candidate outcome coverage is still insufficient because it does not verify intraperiod high/low, entry zone reach, TP/SL first touch, or MFE/MAE.

The next useful step is to freeze the specification before implementing helper functions, tests, builder logic, and CLI wiring.

### Consequences

- Do not implement source code in 051.
- Next task 052 is a docs/spec task.
- daily-sync connection remains out of scope until helper, test, and builder layers are stable.


## DEC-20260721-003: Orchestration records use one-purpose current files

Date: 2026-07-21
Status: accepted
Related work: record navigation optimization

### Decision

The orchestration record system is split by responsibility:

- `CURRENT_STATE.md` stores only accepted current state and active blockers
- `NEXT_ACTION.md` stores exactly one current task
- `CONTROL.md` stores stable operating and safety rules
- `MILESTONES.md` stores accepted major checkpoints only
- `TASK_LEDGER.md` remains search-only historical detail
- active implementation detail remains in `chatgpt/specs/active/`

Verbose pre-optimization versions are preserved under `history/record-optimization-20260721/`.

### Reason

The previous current files accumulated chronological logs and contradictory next-task sections. This increased startup reading, duplicated facts, and made stale text appear current.

### Consequences

- startup follows `START_HERE` → `CURRENT_STATE` → `NEXT_ACTION` → active spec
- completed task history is not appended to current files
- acceptance replaces current state instead of adding another current-state section
- Codex prompts may refer to repo-local current files instead of repeating long context


## DEC-20260721-004: AI routing uses three canonical layers

Date: 2026-07-21
Status: accepted

### Decision

The canonical AI route is reduced to:

1. `AGENTS.md` for Codex worker boundaries
2. `START_HERE.md` for role-aware startup routing
3. `AI_WORKFLOW.md` for ChatGPT analysis, Codex execution, review, and acceptance

`CURRENT_STATE.md`, `NEXT_ACTION.md`, and the active spec supply current task state. Legacy prompt documents remain compatibility pointers only.

### Reason

The previous flow repeated the same mode, prompt, safety, validation, and reporting rules across `AGENTS.md`, `PROMPTS.md`, `MINI_CODEX_RULES.md`, `PROMPT_PREFLIGHT_CHECKLIST.md`, resume docs, and commander prompts. Same-thread Codex tasks also reread stable context unnecessarily.

### Consequences

- fresh contexts use the canonical startup route
- same-thread work is delta-only
- ChatGPT separates direct MCP work, bounded Codex work, and spec-first work before prompting
- Codex no longer rereads stable docs for every FIX
- acceptance-critical source/tests/artifacts are reviewed once per changed area
- legacy prompt filenames are not independent sources of truth


## DEC-20260721-005: Project initial prompt has one canonical source

Date: 2026-07-21
Status: accepted

### Decision

Use `docs/operations/ai-orchestration/INITIAL_PROMPT.md` as the only canonical ChatGPT Project initial prompt. Keep `CHATGPT_COMMANDER_PROMPT.md` as a compatibility pointer only.

### Reason

Maintaining startup, commander, prompt-template, and workflow rules in multiple files caused drift and forced unnecessary rereads. The project prompt should establish only the objective, repo boundary, role split, conditional read route, task classification, review posture, record discipline, and safety baseline. Detailed execution belongs in `AI_WORKFLOW.md`.

### Consequences

- Project settings copy from `INITIAL_PROMPT.md`.
- Current Work IDs and phase history never enter the project prompt.
- Same-thread work remains delta-only.
- `START_HERE.md` routes repo reads after the project prompt is applied.
- `CHATGPT_COMMANDER_PROMPT.md` does not carry independent rules.


## DEC-20260721-006: Separate implementation validation from heavy acceptance validation

### Decision

ChatGPT owns validation design and decides whether real-data acceptance execution is necessary. Codex owns implementation mechanics and lightweight development validation inside the allowed scope.

The default flow is:

```text
Codex implementation pass
→ ChatGPT MCP review gate
→ explicit heavy acceptance run only when still necessary
→ acceptance transition
```

### Reason

Combining implementation debugging with multi-candidate, multi-date, repeated full replay caused avoidable credit use, long-running command loops, interrupted runs, and new bugs introduced while optimizing validation itself.

### Consequences

- Codex may autonomously design helpers, caches, fixtures, and execution order without changing the accepted contract.
- Implementation tasks default to matching tests, small deterministic fixture/smoke, and task-scoped diff check.
- Full bundles, more than 10 replay/evaluation units, long background runs, and second complete replay require explicit ChatGPT authorization.
- ChatGPT reviews source, tests, CLI, and artifacts through MCP before authorizing heavy validation.
- One full acceptance run is the default maximum.
- Failed heavy validation is reported and returned to ChatGPT; Codex does not enter an open-ended edit/replay loop.


## DEC-20260721-007: Codex tasks move to versioned manifests after A1–A3

Date: 2026-07-21
Status: accepted design direction
Related work: post-M5 AI orchestration simplification

### Decision

Replace long hand-written Codex execution prompts with a repo-local, versioned JSON task manifest, a short deterministic launcher prompt, and a machine-validated JSON report.

Adopt the route in bounded phases:

```text
A1 schema / validator / renderer
→ A2 low-risk pilot
→ A3 canonical routing activation
→ optional A4 CWT integration
```

Implementation and heavy acceptance remain separate manifests. CWT remains execution transport and does not own scope or acceptance.

### Reason

Long prompts repeatedly carried stable safety rules, state, implementation requirements, validation budgets, dirty-tree rules, and report schemas. This increased context use, contradictions, thread handoff cost, and Codex micromanagement.

### Consequences

- A1 starts only after the current AI orchestration docs checkpoint.
- A1 does not include replay redesign, persistent cache, CWT integration, runtime, production, M6, or trading-policy changes.
- new active specs use stable contract clause IDs where practical.
- rendered prompts remain short and do not expand active-spec prose.
- implementation manifests cannot authorize heavy validation.
- acceptance manifests cannot repair source and default to one exact heavy run.
- the manual prompt route remains available until A3 is accepted.


## DEC-20260721-008: One master plan and three clearly separated routes

Date: 2026-07-21
Status: accepted documentation direction
Related work: plan and AI navigation consolidation

### Decision

Use `MASTER_PLAN.md` as the single overall planning entrypoint.

Separate the repository's planning routes as follows:

```text
Product / P route = main system-development axis
Macro / M route = supporting market-structure and operator-decision axis
AI / A route = completed operations experiment
```

Canonical supporting routes are:

- `PRODUCT_IMPLEMENTATION_ROUTE.md`
- `docs/operations/strategy/MACRO_IMPLEMENTATION_ROUTE.md`
- `AI_OPERATIONS_STATUS.md`

`DEC-20260721-007` is superseded where it proposed making manifest/JSON routing the normal path. A1 tooling remains optional strict tooling. A3 remains archived and A4 is not planned.

### Reason

Four months of work left multiple generations of product plans, phase routes, task notes, smoke reports, compatibility pointers, and AI-orchestration designs in the same navigation layer. New AI contexts could follow an older P1 start instruction or the superseded A3 route instead of the accepted P8/M5 state.

The repo needs one current architecture map, while retaining accepted specs, research basis, and useful implementation evidence.

### Consequences

- new planning contexts read `MASTER_PLAN.md`
- Product planning follows the current P8/P9 state rather than restarting P1
- M6 remains evidence-gated and unauthorized
- A1/A2 remain accepted history; A3/A4 are not active backlog
- superseded plan documents move to explicit archive directories
- history, archive, handoffs, and `TASK_LEDGER.md` are non-default reads
- compact prompt and compact report remain the normal route
- no new orchestration framework task is created without a task-specific material-evidence reason

## DEC-20260721-009: Generated reports use `local/reports/`

### Decision

The active generated-report root is `local/reports/`.

The former top-level `運用資料/` directory is retired and must not be recreated as an active settings, planning, progress, or report root.

### Rationale

- `local/` is already the repo boundary for generated, private, report-only, and uncommitted assets.
- The old directory mixed active output contracts with obsolete settings, plans, work logs, progress records, and historical reports.
- A single English path avoids locale-dependent shell and integration handling and makes generated-output ownership explicit.

### Migration result

- active source、tools、scripts、tests use `local/reports/`
- tracked historical reports are under `_archive/legacy_operations_materials_20260721/reports_snapshot/`
- old operations-management materials are under `_archive/legacy_operations_materials_20260721/`
- no fallback、symlink、or dual-write to the former path is permitted
- reported implementation commit locator: `3db0399`

### Supersedes

Any earlier instruction treating `運用資料/ChatGPTプロジェクト設定.md`、`運用資料/NEXT_TASK.md`、`運用資料/開発ロードマップ.md`、or `運用資料/reports/` as an active source of truth.

## DEC-20260721-010: Ver04-v3 cleanup line and Ver05 gate

Decision:

- create `Ver04-v3` as the repository-structure and documentation-consolidation line
- commit the current cleanup work on `Ver04-v3`
- do not treat repository cleanup itself as Product or Macro feature promotion
- reserve `Ver05` for the point at which an M6 proposal passes its evidence gate, receives explicit human approval, is implemented and validated, and is accepted by ChatGPT

Reason:

The repository has undergone a material structural cleanup that deserves a clean branch boundary, while M1–M5 acceptance alone does not represent completed runtime adoption of the Macro plan. Version promotion must reflect accepted behavior, not only planning or offline tooling.

## DEC-20260721-011: Active repository paths are separated from history

Date: 2026-07-21
Status: accepted directory model
Related work: Ver04-v3 repository cleanup

### Decision

Keep current work in a small set of purpose-specific areas:

- application and validation: `src/`, `tools/`, `scripts/`, `tests/`
- AI control: `docs/operations/ai-orchestration/`
- Product/Macro design: `docs/operations/strategy/`
- current operator runbook: `docs/operations/manual-preview/`
- implementation contracts and optional strict tooling: `chatgpt/specs/`, `chatgpt/tasks/`, `chatgpt/templates/`
- generated local artifacts: `local/`

Store completed or superseded material only under `_archive/`, `docs/operations/history/`, orchestration `history/`, strategy `archive/`, or `chatgpt/specs/archive/`.

Retire duplicate routes including the former top-level operations directory, `Branch_Command/`, `chatgpt/analysis/`, the old deploy directory, the handoff mirror, and standalone compatibility prompt files.

### Reason

Several generations of plans, task records, runbooks, reports, compatibility pointers, and generated outputs were mixed into current navigation. This caused stale version labels and obsolete next-task instructions to appear active.

### Consequences

- new AI contexts use only `AGENTS.md` and `START_HERE.md` initially
- README files describe directory role rather than historical operating state
- history is preserved but is never a default read path
- current state is not duplicated into handoff or compatibility files
- removed directories are not recreated
- Product, trading, runtime, notification, and safety behavior are unchanged by this cleanup


## DEC-20260721-012: P actual-evidence readiness is a no-repeat review boundary

Date: 2026-07-21
Status: accepted

Decision:

- P1–P8 implementation and the actual-evidence readiness route are accepted.
- P9 remains blocked because the canonical private MEXC Trade History / Order History / Position History batch has not been supplied.
- The absence of `manual_actual_*`, episode, and signal-link CSVs is an input-availability blocker, not an evaluator defect.
- A new AI must report this accepted blocker from `CURRENT_STATE.md` and `NEXT_ACTION.md` instead of repeating the importer, episode-builder, linker, and P8 readiness review.

The review may be reopened only when:

1. a complete private export batch appears under the ignored canonical input path;
2. relevant importer/linker/evaluator source or tests change;
3. a new artifact contradicts the recorded state; or
4. the user explicitly requests re-verification.

Reason:

The accepted code and contracts have already been reviewed. Repeating the same review consumes time and Codex credit without changing the blocking fact.


## DEC-20260721-013: M5 evidence refresh precedes any M6 implementation

Date: 2026-07-21
Status: accepted planning decision

Decision:

- M5 source implementation is complete and accepted; it is not reopened merely because the accepted run selected no winner.
- The next M work is an evidence refresh after a gate-relevant input change, using the accepted engine and proposal space.
- M6 may begin only after M5 identifies one proposal-eligible challenger and the user explicitly approves one bounded proposal.
- M6 source-only shadow, bounded validation, human adoption, and runtime apply are separate tasks.
- Runtime, notification, mail, gate, threshold, scoring, and production adoption are never bundled into the M6 source task.

Canonical plan:

- `docs/operations/strategy/M5_M6_EXECUTION_PLAN_20260721.md`

Reason:

This preserves fail-closed evidence integrity, prevents an unsupported M6 promotion, and avoids rewriting an already accepted M5 engine.


## DEC-20260721-014: Autonomous macro operation is the primary M completion lane

Date: 2026-07-21
Status: accepted planning decision

### Decision

The controlling purpose of the M route is autonomous public-data higher-timeframe structure operation, not waiting for an M5 winner.

The primary M completion lane is:

```text
M-OPS1 current macro snapshot and daily local report
→ M-OPS2 chronological reliability continuity
→ M-OPS3 chart-first operator artifact
→ M-OPS4 separately approved runtime/schedule enablement
→ M-OPS5 autonomous health and stale-data status
```

M5/M6 is a secondary improvement and adoption lane:

```text
accumulated accepted evidence
→ periodic bounded M5 refresh
→ optional one-candidate M6 proposal
→ explicit human approval and separate adoption tasks
```

Private actual-trade evidence is not a prerequisite for public-market support/resistance identity, lifecycle, reliability, current structural location, target/obstruction, local artifact generation, or chronological collection.

M5 `winner=none` / `continue_shadow_collection` does not block M-OPS1–M-OPS3 and does not justify leaving the accepted macro capability disabled.

`DEC-20260721-013` remains valid for the M5-to-M6 sequence, but is superseded where it made M5 refresh the overall current M action.

Canonical plan:

- `docs/operations/strategy/MACRO_AUTONOMOUS_OPERATION_PLAN_20260721.md`

Current active implementation contract:

- `chatgpt/specs/active/20260721_macro_autonomous_structure_daily_operation.md`

### Reason

M1–M4 already provide deterministic level construction, prior-only reliability, public-data auxiliary execution, next-regime separation, and chart-first rendering. The missing product value is operational connection: a maintained current snapshot, chronological reliability history, operator artifact, and separately approved report-only runtime cadence.

Routing the project to M5 evidence waiting before this connection is complete confuses improvement selection with normal product operation and incorrectly makes private trade evidence appear necessary for market-structure understanding.

### Consequences

- new AI contexts must report the autonomous M objective and follow the M-OPS plan;
- `NEXT_ACTION.md` selects M-OPS work while an unfinished M-OPS phase exists;
- no M5 refresh is run during M-OPS1 source implementation;
- M-OPS source work may use accepted public data and requires no recurring human input;
- installed runtime/schedule, live delivery, production policy, and M6 adoption remain separately human-approved;
- support/resistance confidence must fail closed to `insufficient` when evidence is weak, stale, discontinuous, or not prior-only;
- autonomous calculation never becomes automatic order permission.
