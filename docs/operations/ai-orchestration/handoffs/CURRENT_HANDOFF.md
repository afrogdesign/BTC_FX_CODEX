# Current Handoff

last_updated: 2026-06-11
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v3`
current_commit: `53e00d381087e4ac9be78bb5ae7cdd66d867aeba`
latest_reviewed_baseline: `53e00d381087e4ac9be78bb5ae7cdd66d867aeba`

## Objective

BTCFX-20260611-089-LATEST-INTRAPERIOD-PREVIEW-LINK, BTCFX-20260611-090-LATEST-INTRAPERIOD-PREVIEW-E2E-REVIEW, BTCFX-20260611-091-PREVIEW-LINK-BASELINE-SYNC, BTCFX-20260611-092-PRACTICAL-MANUAL-PREVIEW, BTCFX-20260611-093-LATEST-MANUAL-PREVIEW-SHORTCUT, BTCFX-20260611-094-MANUAL-PREVIEW-JSON-INPUT, and BTCFX-20260611-095-MANUAL-PREVIEW-OPERATING-PACKAGE are accepted or REVIEW_ONLY as noted; BTCFX-20260611-097-MANUAL-DELIVERY-COPY-PACKAGE and BTCFX-20260611-098-MANUAL-DELIVERY-FILE-BUNDLE are accepted; this handoff records the reviewed-baseline metadata for the accepted Ver03-v3 manual-delivery file bundle HEAD.

This handoff records the reviewed baseline after BTCFX-20260610-098, BTCFX-20260610-098-REVIEW, BTCFX-20260610-099-SYNC, BTCFX-20260610-099-SYNC-REVIEW, BTCFX-20260611-RESUME-FINAL-SYNC, the resume protocol branch checkpoint, and the final metadata sync.
The stable restart entrypoints are `docs/operations/ai-orchestration/RESUME.md` and `docs/operations/ai-orchestration/INITIAL_PROMPT.md`.

Safety boundary remains report-only, not FORMAL_GO, no automatic order, ACTIVE_* guidance only, human must decide manually, no external notification integration, no clipboard/address-book integration, no paper_positions.csv integration, and no runtime/deploy/trading/API key/private endpoint changes.

## Current state

- BTCFX-20260610-098 is complete at `8c3ae39 Add manual delivery checklist output`.
- BTCFX-20260610-098-REVIEW was REVIEW_ONLY and confirmed the checklist output.
- BTCFX-20260610-099-SYNC is complete at `d2b93f2 Sync reviewed baseline after manual checklist review`.
- BTCFX-20260610-099-SYNC-REVIEW passed and confirmed the reviewed-baseline metadata sync and resume protocol state.
- BTCFX-20260611-RESUME-PROTOCOL was pushed at `1ccbf58 Add low-cost universal resume protocol`.
- BTCFX-20260611-RESUME-FINAL-SYNC finalized the reviewed Ver03-v3 resume protocol metadata at `b8e3092 Finalize Ver03-v3 resume protocol metadata`.
- BTCFX-20260611-089-LATEST-INTRAPERIOD-PREVIEW-LINK is accepted at `b2f3de2 Link latest intraperiod report in notification preview`.
- BTCFX-20260611-090-LATEST-INTRAPERIOD-PREVIEW-E2E-REVIEW passed as REVIEW_ONLY and confirmed the preview-link guardrails.
- BTCFX-20260611-091-PREVIEW-LINK-BASELINE-SYNC recorded the reviewed preview-link baseline metadata sync.
- BTCFX-20260611-092-PRACTICAL-MANUAL-PREVIEW is accepted at `b63b92a Add practical manual preview mode`.
- BTCFX-20260611-093-LATEST-MANUAL-PREVIEW-SHORTCUT is accepted at `c835c6e Add latest manual preview shortcut`.
- BTCFX-20260611-094-MANUAL-PREVIEW-JSON-INPUT is accepted at `c2bef8d Add JSON input for latest manual preview`.
- BTCFX-20260611-095-MANUAL-PREVIEW-OPERATING-PACKAGE is accepted at `1ff74d1 Add manual preview operating package`.
- BTCFX-20260611-097-MANUAL-DELIVERY-COPY-PACKAGE is accepted at `d315782 Add manual delivery copy package`.
- BTCFX-20260611-098-MANUAL-DELIVERY-FILE-BUNDLE is accepted at `53e00d3 Add manual delivery file bundle`.
- `docs/operations/manual-preview/ACTIVE_PLAN_MANUAL_PREVIEW_RUNBOOK.md` captures the concise manual-preview and manual-delivery workflow, including `write-latest-active-plan-manual-delivery-package` and `write-latest-active-plan-manual-delivery-files`.
- `CONTROL.md` now records the reviewed manual-delivery file bundle baseline and defers the next step to STOP: choose the next product step from the reviewed manual-delivery file bundle baseline.
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
STOP: Choose next product step from the reviewed manual-delivery file bundle baseline.
```
