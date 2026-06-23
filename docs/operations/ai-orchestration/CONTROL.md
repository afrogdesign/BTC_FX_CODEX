# AI Orchestration Control

last_updated: 2026-06-23
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v3`
project_key: `BTCFX`
current_commit: cc6f0a9f9029843a9eeab08b8dd533d2f988b92d
note: `current_commit` is the latest ChatGPT-accepted baseline and may intentionally lag branch HEAD. That lag alone is not a BLOCK condition.

---

## Current State

Current reviewed baseline is the human-readable current manual-delivery progress board update after the current manual-delivery app stdout-json E2E confirmation.

## Current Objective

Choose the next product step after the reviewed current manual-delivery app readability update clean checkpoint.

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

Choose the next product step after the reviewed current manual-delivery app readability update clean checkpoint.

## Evidence Note

Historical accepted task details live in git/GitHub and `docs/operations/ai-orchestration/TASK_LEDGER.md` when needed.
Accepted E2E: `BTCFX-20260623-156-CURRENT-APP-REFRESH-STDOUT-JSON-E2E-REVIEW` passed in a tempdir using `refresh-current-manual-delivery-app --stdout-json` and `check-current-manual-delivery-app-ready --stdout-json`.
Accepted work: `BTCFX-20260623-158-CURRENT-APP-INTEGRATION-CONTRACT` added `describe-current-manual-delivery-app-contract --stdout-json`; `BTCFX-20260623-159-PROGRESS-BOARD-CURRENT-APP-INTEGRATION` updated the progress board for the accepted app integration state; `BTCFX-20260623-161-PROGRESS-BOARD-HUMAN-READABILITY` made the board easier for humans to read and aligned the numbering.
Clean checkpoint: `22a35fb08410d260bca3cc92d00622aaf622cb01` preceded the readability update; current reviewed baseline is `cc6f0a9f9029843a9eeab08b8dd533d2f988b92d`.
Canonical app/operator path: single-command app integration `refresh-current-manual-delivery-app --stdout-json`; read-side check `check-current-manual-delivery-app-ready --stdout-json`; contract introspection `describe-current-manual-delivery-app-contract --stdout-json`; stable read file `local/manual_delivery_handoff/app-snapshot.json`; validator/status file `local/manual_delivery_handoff/app-snapshot-status.json`; progress board `運用資料/進捗/Ver03-v1_進捗ボード_20260607.html`.
