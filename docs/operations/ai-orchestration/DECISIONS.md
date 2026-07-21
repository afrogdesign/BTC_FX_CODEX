# AI Decisions

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
