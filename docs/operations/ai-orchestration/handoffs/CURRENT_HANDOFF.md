# Current Handoff

last_updated: 2026-06-13
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v3`
current_commit: ed5c91038c589576f4ddd359d61b7a6905e0eac5
latest_reviewed_baseline: ed5c91038c589576f4ddd359d61b7a6905e0eac5

## Objective

BTCFX-20260613-135-ACTIONABILITY-SHADOW-RUNBOOK is accepted at `ed5c91038c589576f4ddd359d61b7a6905e0eac5`; this handoff records the reviewed Actionability shadow runbook baseline on top of the one-command local manual-delivery flow, source freshness guard, CLI-only API fallback kill switch, Actionability Gate baseline, the separate Actionability shadow ledger writer, the JSON-driven shadow writer, and the local-flow opt-in shadow append path.

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
- BTCFX-20260611-100-PENDING-COVERAGE-CAVEAT-DIAGNOSTIC is accepted at `b771844 Add pending coverage caveat diagnostic`.
- BTCFX-20260611-101-PENDING-CAVEAT-MANUAL-DELIVERY-E2E-REVIEW passed as REVIEW_ONLY with no commit.
- BTCFX-20260611-103-PENDING-CAVEAT-FROM-INTRAPERIOD-CSV is accepted at `229752f Add pending caveat CSV helper`.
- BTCFX-20260611-106-ONE-COMMAND-MANUAL-DELIVERY-E2E-REVIEW passed as REVIEW_ONLY with no commit.
- BTCFX-20260611-108-LATEST-MANUAL-DELIVERY-SOURCE-RESOLVER is accepted at `5088e42538a60258edad86c00594ff79ad198e0b`.
- BTCFX-20260611-108-LATEST-MANUAL-DELIVERY-SOURCE-RESOLVER-FIX is accepted at `c15c6446b344d6388592d6cc05fe89f124f7eb85`.
- BTCFX-20260611-109-LATEST-MANUAL-DELIVERY-INPUT-JSON-SEED is accepted at `5347f2b49c8f89ebd12ebb15acab8c7c9439fa02`.
- BTCFX-20260611-110-LOCAL-MANUAL-DELIVERY-INBOX is accepted at `cdf5a78df8a3a353ed2ef3af12a9589bfccce785`.
- BTCFX-20260612-117-ONE-COMMAND-SOURCE-FRESHNESS-GUARD is accepted at `6d2490fc521bc952bd25835a2d954dacdffd34d9`.
- BTCFX-20260612-119-SOURCE-FRESHNESS-GUARD-E2E-REVIEW passed as REVIEW_ONLY with no commit and no repo file changes.
- BTCFX-20260612-121-CLI-ONLY-AUTO-API-FALLBACK-KILL-SWITCH is accepted at `eb57bf811c70dacc89651e597a1cc0f0b0682729`.
- BTCFX-20260612-121-CLI-ONLY-AUTO-API-FALLBACK-KILL-SWITCH-REVIEW-DIRTY-ALLOWED passed as REVIEW_ONLY with no commit and no new dirty files.
- BTCFX-20260612-124-ACTIONABILITY-GATE-V1 is accepted at `6347b3a52cf21bc72aaf3e4dbc1843e1a28f5fbe`.
- BTCFX-20260612-125-ACTIONABILITY-GATE-RUNTIME-EMAIL-V1 is accepted at `b8646c98e7ac3dad7c274a3474347862992bac02`.
- BTCFX-20260612-127-ACTIONABILITY-JA-EMAIL-LABELS is accepted at `47b3a170e4eb64374e3afab3f50ccdb3550b6ff0`.
- BTCFX-20260613-129-ACTIONABILITY-SHADOW-LEDGER-V1 is accepted at `2a549b139c4acb4ebd84748922de7b077611c510`.
- BTCFX-20260613-131-ACTIONABILITY-SHADOW-FROM-JSON-V1 is accepted at `d7a0bc76a6847e0e477c1f1180829eea9178ee57`.
- BTCFX-20260613-133-ACTIONABILITY-SHADOW-LOCAL-FLOW-OPTIN is accepted at `466f47a3b8af7e3ed59d58f03fd433a619daaf41`.
- BTCFX-20260613-135-ACTIONABILITY-SHADOW-RUNBOOK is accepted at `ed5c91038c589576f4ddd359d61b7a6905e0eac5`.
- BTCFX-20260613-137-ACTIONABILITY-SHADOW-LOCAL-FLOW-E2E-REVIEW passed as REVIEW_ONLY with no commit, no push, and no repo file changes.
- `write-latest-manual-delivery-local-flow` supports `--source-stale-after-hours`.
- `resolve-latest-manual-delivery-source-files` and `write-latest-manual-delivery-input-json` also support `--source-stale-after-hours`.
- Freshness is based only on local filesystem mtimes.
- CLI provider mode does not silently fall back to OpenAI API.
- API usage requires explicit `AI_API_USAGE_ALLOWED`.
- CLI failure returns `cli_failed`, and API disabled returns `api_disabled`.
- Post-review API fallback is gated by `AI_POST_REVIEW_API_FALLBACK_ENABLED`.
- Actionability Gate v1 fields are present in local manual-delivery JSON and inbox outputs.
- Runtime summary emails surface Actionability fields without changing notification send conditions or trading behavior.
- Runtime summary emails also show Japanese human-readable Actionability labels while preserving machine keys.
- The separate Actionability shadow decision ledger writer is present and remains isolated from `paper_positions.csv` and trading behavior.
- The JSON-driven Actionability shadow decision writer appends one row from `manual-delivery-input.json`, does not recompute actionability, and remains isolated from `paper_positions.csv` and trading behavior.
- The one-command local manual-delivery flow has a reviewed opt-in shadow append path; default local-flow stdout and behavior remain unchanged without the flag, and the opt-in path remains isolated from `paper_positions.csv` and trading behavior.
- The manual-preview runbook now documents the local-flow Actionability shadow opt-in path; generated shadow CSV output must not be committed unless explicitly approved, and the shadow ledger remains evaluation-only and separate from `paper_positions.csv`.
- The REVIEW_ONLY local-flow Actionability shadow E2E used a temporary directory outside the repo, verified tmpdir bundle outputs and shadow CSV generation, confirmed stdout emitted `actionability_shadow_output_csv`, confirmed the shadow row matched `manual-delivery-input.json` Actionability fields, preserved the report-only safety value plus `final_outcome` and `notes`, and used no `paper_positions.csv` path.
- No fetch / rebuild / notify / trade / approve behavior is involved.
- `docs/operations/manual-preview/ACTIVE_PLAN_MANUAL_PREVIEW_RUNBOOK.md` captures the concise manual-preview and manual-delivery workflow, including `write-latest-manual-delivery-local-flow`, `resolve-latest-manual-delivery-source-files`, `write-latest-manual-delivery-input-json`, `write-latest-active-plan-manual-delivery-files-from-json`, `write-latest-manual-delivery-local-inbox`, `format-active-plan-pending-coverage-caveat`, `format-active-plan-pending-coverage-caveat-from-csv`, `write-latest-active-plan-manual-delivery-package`, `write-latest-active-plan-manual-delivery-files`, and `write-latest-active-plan-manual-delivery-files-from-json`.
- `CONTROL.md` now records the reviewed Actionability shadow runbook baseline plus REVIEW_ONLY E2E confirmation and defers the next step to STOP: choose the next product step after the reviewed Actionability shadow runbook baseline and REVIEW_ONLY E2E confirmation.
- Repo-relative paths such as `AGENTS.md` and `docs/operations/ai-orchestration/RESUME.md` are valid after `cd /Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`.

## Constraints

- ChatGPT is commander, planner, design judge, and reviewer.
- Codex is implementation/edit/test/commit/push worker.
- Codex must not make product or design decisions.
- For the current STOP state, do not edit source code, tests, generated reports, generated previews, or generated manual-delivery artifacts unless the next task explicitly authorizes a narrow edit scope.
- Do not run fetch, builder reruns, report regeneration, daily-sync, report hub generation, runtime/deploy, `main.py`, or `run_cycle`.
- Do not access API keys, secrets, private/account/order endpoints, live trading, automatic orders, or `paper_positions.csv`.
- Do not add email, SMTP, Gmail, webhook, Slack, LINE, Discord, cron, launchd, clipboard, address-book, or notification service integration.
- `current_commit` may lag branch HEAD, and that lag alone is not BLOCK.
- The current next task must come from `CONTROL.md`, not chat memory.

## Next task

```text
STOP: Choose the next product step after the reviewed Actionability shadow runbook baseline and REVIEW_ONLY E2E confirmation.
```
