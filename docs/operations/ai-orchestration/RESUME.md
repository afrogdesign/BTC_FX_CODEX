# Resume Protocol

last_updated: 2026-07-02
repo: `afrogdesign/BTC_FX_CODEX`
primary_mcp_working_dir: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
frozen_old_runtime_execution_repo: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
branch_source: `read from repo state and CONTROL.md, not from old chat history`

## Purpose

これは new ChatGPT / Codex / future AI agent の low-cost, repo-local restart entrypoint です。
chat history を信じる前に使います。

## Current product objective

現時点の product objective は次。

```text
notification mail を受け取った人間が、
15分足を確認し、
攻めの姿勢で勝てる manual trading support system を作る。
```

Automatic trading is later-stage only.

Ver03-v4 は prior baseline / history、Ver04-v1 が active product branch です。

## Tiered read model

### Tier 0 / always

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/START_HERE.md`

### Tier 1 / state needed

1. `docs/operations/ai-orchestration/CURRENT_STATE.md`
2. `docs/operations/ai-orchestration/NEXT_ACTION.md`
3. `docs/operations/ai-orchestration/CONTROL.md`

### Tier 2 / by task type only

- product route:
  - `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
  - `docs/operations/strategy/VER04_V1_INTEGRATED_PRODUCT_PLAN.md`
  - `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
  - `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
- Codex prompt work:
  - `docs/operations/ai-orchestration/PROMPTS.md`
  - `docs/operations/ai-orchestration/MINI_CODEX_RULES.md`
  - `docs/operations/ai-orchestration/PROMPT_PREFLIGHT_CHECKLIST.md`
- checkpoint:
  - `docs/operations/ai-orchestration/CHECKPOINT_RUNBOOK.md`
- runtime pull handoff:
  - `docs/operations/ai-orchestration/RUNTIME_PULL_HANDOFF.md`
- accepted history:
  - `docs/operations/ai-orchestration/MILESTONES.md`
- handoff only:
  - `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md`
- specific historical lookup only:
  - `docs/operations/ai-orchestration/TASK_LEDGER.md` by search / latest rows only

`docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md` は explicit handoff / migration / blocked / partial / context-overload situations のときだけ読む。
`docs/operations/ai-orchestration/TASK_LEDGER.md` は historical lookup 専用で、default restart read ではない。

## Current operational posture

- Ver04-v1 runtime deployment complete / reflected active
- post-deployment observation
- notification sending behavior unchanged
- no immediate implementation unless observation finds an issue or user explicitly requests implementation

## Product backlog next candidate

- `BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER`

## Completed history

- post-eval asset health audit completed
- daily proxy evaluator implemented
- implementation readiness package created
- Ver04-v1 runtime deployment complete

## Strategy guard

- public HTML is the current main manual-trading UI
- notification mail is the triage / entry point
- local dashboard / app surface is the confirmation and future automation foundation
- all three surfaces share one source of truth and must stay aligned
- mail / public HTML / dashboard must not produce different trading logic
- direction and execution permission must be separated
- `ACTIVE_*` labels are not `FORMAL_GO`
- actual human trades must not be mixed into `paper_positions.csv` unless explicitly approved

## Repo split rule

- MCP/Codex normal orchestration tasks use the MCP working repo
- runtime execution repo exists separately and must not be edited, run, or inspected during normal MCP orchestration/product tasks
- runtime execution repo should receive updates later by GitHub pull after a clean checkpoint branch/push from the MCP working repo
- normal MCP task does not require routine GitHub push
- push is reserved for explicit checkpoint tasks
- default avoid list includes `.venv312/`, `logs/`, generated outputs, raw exchange exports, and full `TASK_LEDGER.md`

## CONTROL.md semantics

- `CONTROL.md` should stay lightweight: current state, objective, safety boundary, validation rules, and next decision
- durable accepted history belongs in `MILESTONES.md`
- active product route belongs in `PRODUCT_IMPLEMENTATION_ROUTE.md`
- the current next task belongs in `NEXT_ACTION.md`

## Low-cost modes

- `CHATGPT_ONLY`: use when ChatGPT should handle review, scope selection, or design judgment without spending Codex credits
- `REVIEW_ONLY`: use for fixed-scope audits that should not edit source code
- `LIGHT_CODEX`: use when the scope is fixed and only a small local edit is needed
- `BOUNDED_CODEX`: default implementation mode for fixed-scope source/test/docs work
- `NORMAL_CODEX`: use when the task needs slightly wider local implementation/validation scope than `BOUNDED_CODEX`
- `CHECKPOINT_PUSH`: use only when a meaningful checkpoint branch/push is explicitly requested
- `SYNC`: use only at checkpoints to batch-update reviewed metadata
- `HANDOFF`: use at thread migration, context overload, major milestone, or explicit handoff

## BOUNDED_CODEX rules

- ChatGPT decides product / safety / scope first
- Codex may perform bounded local inspection within named files, nearby helpers, matching tests, and current diff/status
- Codex stops for:
  - broad repo exploration
  - product judgment
  - safety judgment
  - runtime / mail / API / order / private endpoint changes

## Outbox reporting

- If Codex has local filesystem access, write the final compact report to `/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt` for every task type and outcome
- If the thread is ChatGPT-only and does not have local filesystem access, this file write is not required

## When to use Codex

- Use Codex when the task has a fixed scope and explicit file list
- Use Codex when the work is local, repo-bound, and can be validated with narrow commands
- Use Codex when you need edits, tests, commit, or checkpoint preparation

## When not to use Codex

- Do not use Codex for broad repository exploration
- Do not use Codex when product scope, priority, or design judgment is still unresolved
- Do not use Codex when the task would need files outside the fixed scope

## Blocking

- Stop with `BLOCKED <WORK_ID>: <one specific question>` if the repo context is contradictory, overloaded, or ambiguous enough that a safe narrow edit is not possible
- Report `BLOCKED` rather than guessing when files outside the approved scope would be required
