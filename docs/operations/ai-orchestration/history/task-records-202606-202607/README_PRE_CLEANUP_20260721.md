# AI Orchestration

This directory contains the current plan entrypoints, accepted state, AI execution rules, and historical records for `btc_monitor`.

## Canonical navigation

```text
ChatGPT Project prompt: INITIAL_PROMPT.md
→ AGENTS.md
→ START_HERE.md
→ MASTER_PLAN.md when planning or selecting work
→ CURRENT_STATE.md / NEXT_ACTION.md when current state is needed
→ one target route or active spec
```

## Canonical files

| File | Responsibility |
|---|---|
| `INITIAL_PROMPT.md` | ChatGPT Project initial prompt source |
| `START_HERE.md` | shortest role-aware entrypoint |
| `MASTER_PLAN.md` | overall product plan and Product/Macro/AI relationship |
| `PRODUCT_IMPLEMENTATION_ROUTE.md` | current Product/P route |
| `AI_OPERATIONS_STATUS.md` | conclusion of the A operations experiment |
| `AI_WORKFLOW.md` | ChatGPT/Codex execution, review, and acceptance process |
| `CONTROL.md` | stable safety、git、runtime、validation controls |
| `CURRENT_STATE.md` | accepted current state and blocker |
| `NEXT_ACTION.md` | exactly one current task |
| `MILESTONES.md` | major accepted checkpoints |
| `DECISIONS.md` | durable decisions and supersession records |
| `REPO_MAP.md` | repository navigation map |
| `TASK_LEDGER.md` | historical Work ID lookup only |

Macro route:

`docs/operations/strategy/MACRO_IMPLEMENTATION_ROUTE.md`

Current implementation contract:

`chatgpt/specs/active/`

## Current plan summary

```text
Product / P route: main system axis
- P1〜P7 accepted
- P8 accepted and collecting evidence
- P9 blocked pending evidence and human approval

Macro / M route: supporting axis
- M1〜M5 accepted
- M6 unauthorized

AI / A route: completed operations experiment
- A1/A2 accepted
- A3 superseded
- A4 not planned
```

## Default reading rule

New AI contexts read only `AGENTS.md` and `START_HERE.md` first. `MASTER_PLAN.md` is added for planning or next-task selection.

Do not broadly scan old reports, history, archive, handoffs, or the full task ledger.

## Normal execution route

```text
compact prompt
→ one bounded implementation
→ matching tests / small fixture
→ compact report
→ ChatGPT MCP review
```

Manifest and JSON-report tooling is optional strict tooling. It is not the default route.

## Archive structure

- `history/plan-archive-20260721/`: superseded planning and A-route design documents
- `history/record-optimization-20260721/`: pre-optimization current-record copies
- `history/ai-routing-optimization-20260721/`: pre-optimization AI routing copies
- `docs/operations/strategy/archive/`: superseded high-level product and macro plans
- `chatgpt/specs/archive/`: accepted or superseded implementation contracts

Historical documents do not override canonical current files.

## Compatibility files

`PROMPTS.md`, `MINI_CODEX_RULES.md`, `PROMPT_PREFLIGHT_CHECKLIST.md`, `CHATGPT_COMMANDER_PROMPT.md`, and `RESUME.md` preserve old entry paths only. They are not independent sources of truth and should not be read together.

## Update discipline

During normal implementation or FIX:

- do not append task history to current files
- do not update stable controls unless rules changed
- do not add a milestone for routine work

At acceptance or a real posture change:

1. archive the active spec
2. update `CURRENT_STATE.md`
3. replace `NEXT_ACTION.md` with one current task
4. update `CONTROL.md` only when stable rules changed
5. add a milestone only for a major checkpoint


## Legacy operations records

Completed 2026-07-01〜02 repository-switch、runtime-handoff、launchd、deployment、rollback、and verification records are under:

`history/legacy-ops-20260701/`

Use `CHECKPOINT_RUNBOOK.md` and `RUNTIME_PULL_HANDOFF.md` for current operations. Do not reuse historical branch、commit、PID、or deployment assumptions without current verification.
