# Current Handoff

last_updated: 2026-06-11
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v3`
current_commit: `8c3ae39e2b6e6fdbcd1d0e4c1ddba82410feddb6`
latest_branch_head: `1ccbf583d8160fd70490432aac29fcc5bf2b53e2`

## Objective

BTCFX-20260611-RESUME-PROTOCOL-FIX corrects the resume protocol handoff head metadata after the resume protocol branch checkpoint.

This handoff records the reviewed baseline after BTCFX-20260610-098, BTCFX-20260610-098-REVIEW, BTCFX-20260610-099-SYNC, and the resume protocol branch checkpoint.
The stable restart entrypoints are `docs/operations/ai-orchestration/RESUME.md` and `docs/operations/ai-orchestration/INITIAL_PROMPT.md`.

## Current state

- BTCFX-20260610-098 is complete at `8c3ae39 Add manual delivery checklist output`.
- BTCFX-20260610-098-REVIEW was REVIEW_ONLY and confirmed the checklist output.
- BTCFX-20260610-099-SYNC is complete at `d2b93f2 Sync reviewed baseline after manual checklist review`.
- BTCFX-20260611-RESUME-PROTOCOL was pushed at `1ccbf58 Add low-cost universal resume protocol`.
- `CONTROL.md` now points at the resume protocol task and keeps the next product step deferred for review.
- Repo-relative paths such as `AGENTS.md` and `docs/operations/ai-orchestration/RESUME.md` are valid after `cd /Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`.

## Constraints

- ChatGPT is commander, planner, design judge, and reviewer.
- Codex is implementation/edit/test/commit/push worker.
- Codex must not make product or design decisions.
- Do not edit source code, tests, generated reports, or generated previews for this resume protocol task.
- Do not run fetch, builder reruns, report regeneration, daily-sync, report hub generation, runtime/deploy, `main.py`, or `run_cycle`.
- Do not access API keys, secrets, private/account/order endpoints, live trading, automatic orders, or `paper_positions.csv`.
- Do not add email, SMTP, Gmail, webhook, Slack, LINE, Discord, cron, launchd, clipboard, address-book, or notification service integration.
- `current_commit` may lag branch HEAD, and that lag alone is not BLOCK.
- The current next task must come from `CONTROL.md`, not chat memory.

## Next task

```text
NEXT BTCFX-20260610-099-SYNC-REVIEW
Goal: Review the reviewed-baseline metadata sync before choosing the next product step.
Read: docs/operations/ai-orchestration/RESUME.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md, docs/operations/ai-orchestration/PROMPTS.md, docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md
Edit: none
Test: none
Stop: if the repo state is contradictory or if a design decision outside the metadata sync is required
Report: compact
```
