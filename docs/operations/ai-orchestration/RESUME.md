# Resume Protocol

last_updated: 2026-06-11
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v3`
canonical_working_dir: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`

## Purpose

This is the low-cost, repo-local restart entrypoint for new ChatGPT or Codex threads.
Use it before trusting chat history.

## Fixed Read Order

After `cd /Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`, these repo-relative paths are valid and should be read in this order:

1. `AGENTS.md`
2. `docs/operations/ai-orchestration/RESUME.md`
3. `docs/operations/ai-orchestration/CONTROL.md`
4. `docs/operations/ai-orchestration/PROMPTS.md`
5. `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md`
6. `docs/operations/ai-orchestration/TASK_LEDGER.md` only as needed, preferably the latest rows

`docs/operations/ai-orchestration/INITIAL_PROMPT.md` is the stable paste-in prompt for a brand-new thread.

## CONTROL.md Semantics

- `current_commit` means the latest ChatGPT-reviewed baseline.
- `current_commit` may intentionally lag branch HEAD.
- A `current_commit` / branch HEAD lag alone is not a BLOCK condition.
- The repo正本 overrides chat history.
- The current next task must come from `CONTROL.md`, not chat memory.

## Low-Cost Modes

- `CHATGPT_ONLY`: use when ChatGPT should handle review, scope selection, or design judgment without spending Codex credits.
- `LIGHT_CODEX`: use when the scope is fixed and only a small local edit is needed.
- `NORMAL_CODEX`: use for fixed-scope edit/test/commit/push work.
- `SYNC`: use only at checkpoints to batch-update reviewed metadata; do not run after every task.
- `HANDOFF`: use at thread migration, context overload, major milestone, or explicit handoff; do not update `CURRENT_HANDOFF.md` for every task.

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
