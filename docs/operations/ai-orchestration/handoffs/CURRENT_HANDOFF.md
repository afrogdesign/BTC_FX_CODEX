# Current Handoff

last_updated: 2026-06-11
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v3`
current_commit: `da032ed2f8591f2aa7de0f72aad0853253976672`
latest_branch_head: `da032ed2f8591f2aa7de0f72aad0853253976672`

## Objective

BTCFX-20260611-RESUME-FINAL-SYNC finalizes the reviewed Ver03-v3 resume protocol metadata after BTCFX-20260610-099-SYNC-REVIEW passed.

This handoff records the reviewed baseline after BTCFX-20260610-098, BTCFX-20260610-098-REVIEW, BTCFX-20260610-099-SYNC, BTCFX-20260610-099-SYNC-REVIEW, the resume protocol branch checkpoint, and the final metadata sync.
The stable restart entrypoints are `docs/operations/ai-orchestration/RESUME.md` and `docs/operations/ai-orchestration/INITIAL_PROMPT.md`.

## Current state

- BTCFX-20260610-098 is complete at `8c3ae39 Add manual delivery checklist output`.
- BTCFX-20260610-098-REVIEW was REVIEW_ONLY and confirmed the checklist output.
- BTCFX-20260610-099-SYNC is complete at `d2b93f2 Sync reviewed baseline after manual checklist review`.
- BTCFX-20260610-099-SYNC-REVIEW passed and confirmed the reviewed-baseline metadata sync and resume protocol state.
- BTCFX-20260611-RESUME-PROTOCOL was pushed at `1ccbf58 Add low-cost universal resume protocol`.
- `CONTROL.md` now records the reviewed resume baseline and defers the next step to a human/ChatGPT product-planning checkpoint.
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
STOP: Choose next product step from the reviewed Ver03-v3 resume baseline.
```
