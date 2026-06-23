# Current Handoff

last_updated: 2026-06-23
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v3`
canonical_working_dir: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
current_commit: cc6f0a9f9029843a9eeab08b8dd533d2f988b92d
latest_reviewed_baseline: cc6f0a9f9029843a9eeab08b8dd533d2f988b92d

## State

Current handoff reflects the human-readable current manual-delivery progress board update. There is no active handoff.

## Safety Boundary

- Report-only.
- Not `FORMAL_GO`.
- No automatic order.
- No API keys.
- No private, account, or order endpoints.
- No runtime restart.
- No `paper_positions.csv` integration unless explicitly approved.

## Next Decision

Choose the next product step after the reviewed current manual-delivery app readability update clean checkpoint, either by migrating to a new ChatGPT thread from repo正本 or by continuing product/app surface work.

## Evidence

Historical accepted task details live in git/GitHub, `docs/operations/ai-orchestration/TASK_LEDGER.md`, and `docs/operations/ai-orchestration/CONTROL.md` when needed.
Accepted E2E: `BTCFX-20260623-156-CURRENT-APP-REFRESH-STDOUT-JSON-E2E-REVIEW` passed in a tempdir using `refresh-current-manual-delivery-app --stdout-json` and `check-current-manual-delivery-app-ready --stdout-json`.
Accepted work: `BTCFX-20260623-158-CURRENT-APP-INTEGRATION-CONTRACT` added `describe-current-manual-delivery-app-contract --stdout-json`; `BTCFX-20260623-159-PROGRESS-BOARD-CURRENT-APP-INTEGRATION` updated the progress board for the accepted app integration state; `BTCFX-20260623-161-PROGRESS-BOARD-HUMAN-READABILITY` made the board easier for humans to read and aligned the numbering.
Clean checkpoint: `22a35fb08410d260bca3cc92d00622aaf622cb01` preceded the readability update; current reviewed baseline is `cc6f0a9f9029843a9eeab08b8dd533d2f988b92d`.
Canonical app/operator path: single-command app integration `refresh-current-manual-delivery-app --stdout-json`; read-side check `check-current-manual-delivery-app-ready --stdout-json`; contract introspection `describe-current-manual-delivery-app-contract --stdout-json`; smallest stable read file `local/manual_delivery_handoff/app-snapshot.json`; validator/status file `local/manual_delivery_handoff/app-snapshot-status.json`; progress board `運用資料/進捗/Ver03-v1_進捗ボード_20260607.html`.
