# Resume Protocol

last_updated: 2026-06-23
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v4`
canonical_working_dir: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`

## Purpose

This is the low-cost, repo-local restart entrypoint for new ChatGPT or Codex threads.
Use it before trusting chat history.

## Fixed Read Order

After `cd /Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`, these repo-relative paths are valid and should be read in this order:

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/RESUME.md`
3. `docs/operations/ai-orchestration/CONTROL.md`
4. `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`
5. `docs/operations/ai-orchestration/PROMPTS.md`
6. `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md`
7. `docs/operations/ai-orchestration/TASK_LEDGER.md` only as needed, preferably the latest rows

`docs/operations/ai-orchestration/INITIAL_PROMPT.md` is the stable paste-in prompt for a brand-new thread.

## CONTROL.md Semantics

- `current_commit` means the latest ChatGPT-reviewed baseline.
- `current_commit` may intentionally lag branch HEAD.
- A `current_commit` / branch HEAD lag alone is not a BLOCK condition.
- The repo正本 overrides chat history.
- The current next task must come from `CONTROL.md`, not chat memory.
- `CONTROL.md` should stay lightweight: current state, current objective, safety boundary, validation rules, and next action only, not a full task history.
- `TASK_LEDGER.md` is a human-facing work index, not the source of truth for commit history; git/GitHub and the compact report are the commit evidence.

## Ver03-v4 Strategy Guard

- public HTML is the current main manual-trading UI.
- notification mail is the triage / entry point.
- local dashboard / app surface is the confirmation and future automation surface.
- all three surfaces share one source of truth and must stay aligned.
- when in doubt about direction, read `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md` after `CONTROL.md`.

## Low-Cost Modes

- `CHATGPT_ONLY`: use when ChatGPT should handle review, scope selection, or design judgment without spending Codex credits.
- `LIGHT_CODEX`: use when the scope is fixed and only a small local edit is needed.
- `NORMAL_CODEX`: use for fixed-scope edit/test/commit/push work.
- `SYNC`: use only at checkpoints to batch-update reviewed metadata; do not run after every task.
- `HANDOFF`: use at thread migration, context overload, major milestone, or explicit handoff; do not update `CURRENT_HANDOFF.md` for every task.
- Keep orchestration metadata lightweight: normal tasks should not trigger `CONTROL.md`, `TASK_LEDGER.md`, or `CURRENT_HANDOFF.md` updates.
- Update `CURRENT_HANDOFF.md` only for active handoff conditions such as partial, blocked, thread migration, context overload, major milestone, or explicit handoff.
- Keep the logical separation intact without a physical split: orchestration docs stay under `docs/operations/ai-orchestration/`, while project source stays under `src/`, `tools/`, `tests/`, `scripts/`, and related runtime directories.

## Outbox Reporting

- If Codex has local filesystem access, write the final compact report to `/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt` for every task type and outcome, including `NEXT`, `FIX`, `SYNC`, `HANDOFF`, `REVIEW_ONLY`, `BLOCKED`, `done`, `partial`, `failed`, resume checks, metadata checks, and no-commit checks.
- Also write the final compact report to: `/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt` whenever Codex has local filesystem access.
- If the thread is ChatGPT-only and does not have local filesystem access, this file write is not required.
- Keep this rule even when the task only confirms repo state or reports `READY`, `BLOCKED`, or `NEEDS_REVIEW`.

## When to Use Codex

- Use Codex when the task has a fixed scope and explicit file list.
- Use Codex when the work is local, repo-bound, and can be validated with narrow commands.
- Use Codex when you need edits, tests, commit, or push.

## When Not to Use Codex

- Do not use Codex for broad repository exploration.
- Do not use Codex when product scope, priority, or design judgment is still unresolved.
- Do not use Codex when the task would need files outside the fixed scope.

## Blocking

- Stop with `BLOCKED <WORK_ID>: <one specific question>` if the repo context is contradictory, overloaded, or ambiguous enough that a safe narrow edit is not possible.
- Report `BLOCKED` rather than guessing when files outside the approved scope would be required.
- The current next task must still be taken from `CONTROL.md`.
