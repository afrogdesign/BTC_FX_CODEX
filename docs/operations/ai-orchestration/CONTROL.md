# AI Orchestration Control

last_updated: 2026-06-23
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v3`
project_key: `BTCFX`
current_commit: 3fe19d47f0248053f7952bd20f3cb70bbd57c4a1
note: `current_commit` is the latest ChatGPT-accepted baseline and may intentionally lag branch HEAD. That lag alone is not a BLOCK condition.

---

## Current State

Current reviewed baseline is the current manual-delivery app refresh path E2E confirmation after the Actionability shadow runbook baseline and REVIEW_ONLY E2E confirmation.

## Current Objective

Choose the next product step after the reviewed current manual-delivery app refresh path E2E confirmation.

## Safety Boundary

- Report-only.
- Not `FORMAL_GO`.
- No automatic order.
- No API keys.
- No private, account, or order endpoints.
- No runtime restart.
- No `paper_positions.csv` integration unless explicitly approved.

## Validation Rules

- Docs-only changes: `git diff --check`.
- Python code changes: targeted `./.venv312/bin/python -m unittest <tests>`.
- CLI/report builder changes: relevant CLI/report validation only.
- Every task: `git status --short --branch`.

## Next Decision

Choose the next product step after the reviewed Actionability shadow runbook baseline and REVIEW_ONLY E2E confirmation.

## Evidence Note

Historical accepted task details live in git/GitHub and `docs/operations/ai-orchestration/TASK_LEDGER.md` when needed.
Accepted E2E: `BTCFX-20260622-150-CURRENT-MANUAL-DELIVERY-APP-E2E-REVIEW` passed in a tempdir using `refresh-current-manual-delivery-app` and `check-current-manual-delivery-app-ready`.
Canonical app/operator path: `refresh-current-manual-delivery-app` -> `check-current-manual-delivery-app-ready`; stable read file `local/manual_delivery_handoff/app-snapshot.json`; validator/status file `local/manual_delivery_handoff/app-snapshot-status.json`.
