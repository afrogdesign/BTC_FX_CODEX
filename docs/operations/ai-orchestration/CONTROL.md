# AI Orchestration Control

last_updated: 2026-06-23
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v4`
project_key: `BTCFX`
current_commit: 550be2fdafcdd80c72d9b21346711615d5995496
note: `current_commit` is the latest ChatGPT-accepted baseline and may intentionally lag branch HEAD. That lag alone is not a BLOCK condition.

---

## Current State

Current reviewed baseline is the accepted Ver03-v4 manual action surface/mail milestone sequence `BTCFX-20260623-181-V4-PUBLIC-HTML-MANUAL-ACTION-CHECKLIST`, `BTCFX-20260623-183-V4-LOCAL-DASHBOARD-ACTION-SURFACE-ALIGNMENT`, `BTCFX-20260623-184-V4-LOCAL-DASHBOARD-CHECKLIST-READY-GATE`, `BTCFX-20260623-186-V4-MAIL-MANUAL-ACTION-CHECKLIST`, and the accepted intraperiod milestone sequence `BTCFX-20260623-188-V4-INTRAPERIOD-TP2-DEEPER-TARGET-CLASSIFICATION`, `BTCFX-20260623-189-V4-INTRAPERIOD-OUTCOME-CSV-CLI`, `BTCFX-20260623-191-V4-INTRAPERIOD-REPORT-OPERATOR-WIRING`, `BTCFX-20260623-192-V4-INTRAPERIOD-LOCAL-REVIEW-CLI`, `BTCFX-20260623-195-V4-INTRAPERIOD-REVIEW-STDOUT-JSON`, `BTCFX-20260623-197-V4-APP-CONTRACT-INTRAPERIOD-REVIEW-JSON`, `BTCFX-20260623-199-V4-APP-SURFACE-CONTRACT-INTRAPERIOD-JSON-READY-GATE`, `BTCFX-20260623-201-V4-PUBLIC-HTML-INTRAPERIOD-JSON-CONTRACT-SURFACE`, and `BTCFX-20260623-202-V4-PUBLIC-HTML-INTRAPERIOD-JSON-MILESTONE-SYNC`, with the public HTML report, notification mail body, local dashboard HTML, app surface validation, intraperiod outcome tooling, manual-delivery app contract, and public HTML report surface sharing the manual action checklist boundary and same-bar TP2 classification boundary. Intraperiod tooling now has same-bar TP1+TP2 without SL classified as `tp2_first`, the local-file-only outcome CSV builder `build-active-plan-intraperiod-outcomes`, Ver03-v4 operator report guidance wired to that local CSV CLI, the one-shot local review CLI `build-active-plan-intraperiod-review` with machine-readable `--stdout-json` support, the app contract exposure for `build-active-plan-intraperiod-review --stdout-json` with `active_plan_intraperiod_review.v1` safety flags, and the public HTML report surface reflection for `intraperiod_review_stdout_json`. The app surface / ready gate now rejects missing or invalid `intraperiod_review_stdout_json` contract exposure and requires the accepted local/report-only safety flags: `local/report-only`, no exchange fetch, no daily-sync wiring, no secret/API key reading, and the safety flags that prevent FORMAL_GO / automatic orders / secret reading. The safety boundary remains report-only / not FORMAL_GO / no automatic order / human decides manually.

## Current Objective

Develop the BTC trading system through the three aligned surfaces: public HTML report, notification mail, and local dashboard / app surface.

## Safety Boundary

- Report-only.
- Not `FORMAL_GO`.
- No automatic order.
- No API keys.
- No private, account, or order endpoints.
- No runtime restart.
- No `paper_positions.csv` integration unless explicitly approved.
- Public HTML / mail / dashboard must not diverge in trading logic.

## Validation Rules

- Docs-only changes: `git diff --check`.
- Python code changes: targeted `./.venv312/bin/python -m unittest <tests>`.
- CLI/report builder changes: relevant CLI/report validation only.
- Every task: `git status --short --branch`.

## Next Decision

Continue with local/report-only operator tooling, diagnostics, and evidence-based accuracy using the intraperiod review workflow, app contract exposure, and public HTML report surface, without daily-sync wiring, exchange fetch, trading logic changes, notification sending, runtime changes, report regeneration, or automation safety changes.

## Deferred Follow-up / Post-build Check

- CLI/API key configuration may have changed.
- Verification is intentionally deferred until after current build work.
- Future validation must not read or print API key values.
- Future validation must inspect configuration names, CLI/env var wiring, dry-run/safe error behavior, and documentation consistency only.
- Future validation must not call private/account/order endpoints, place orders, run live trading, or expose secrets.

## Evidence Note

Historical accepted task details live in git/GitHub and `docs/operations/ai-orchestration/TASK_LEDGER.md` when needed.
Accepted Ver03-v4 surface sequence: `BTCFX-20260623-181-V4-PUBLIC-HTML-MANUAL-ACTION-CHECKLIST`; `BTCFX-20260623-183-V4-LOCAL-DASHBOARD-ACTION-SURFACE-ALIGNMENT`; `BTCFX-20260623-184-V4-LOCAL-DASHBOARD-CHECKLIST-READY-GATE`; `BTCFX-20260623-186-V4-MAIL-MANUAL-ACTION-CHECKLIST`; `BTCFX-20260623-197-V4-APP-CONTRACT-INTRAPERIOD-REVIEW-JSON`; `BTCFX-20260623-201-V4-PUBLIC-HTML-INTRAPERIOD-JSON-CONTRACT-SURFACE`.
Accepted intraperiod sequence: `BTCFX-20260623-188-V4-INTRAPERIOD-TP2-DEEPER-TARGET-CLASSIFICATION`; `BTCFX-20260623-189-V4-INTRAPERIOD-OUTCOME-CSV-CLI`; `BTCFX-20260623-191-V4-INTRAPERIOD-REPORT-OPERATOR-WIRING`; `BTCFX-20260623-192-V4-INTRAPERIOD-LOCAL-REVIEW-CLI`; `BTCFX-20260623-195-V4-INTRAPERIOD-REVIEW-STDOUT-JSON`; `BTCFX-20260623-199-V4-APP-SURFACE-CONTRACT-INTRAPERIOD-JSON-READY-GATE`.
Visible local/report-only intraperiod path: `build-active-plan-intraperiod-outcomes`; `build-active-plan-intraperiod-review`; `build-active-plan-intraperiod-review --stdout-json`; Ver03-v4 intraperiod report guidance; app contract exposure for `active_plan_intraperiod_review.v1`; app surface / ready gate validation for `intraperiod_review_stdout_json`; public HTML report reflection for the accepted intraperiod JSON contract surface.
Accepted E2E: `BTCFX-20260623-156-CURRENT-APP-REFRESH-STDOUT-JSON-E2E-REVIEW` passed in a tempdir using `refresh-current-manual-delivery-app --stdout-json` and `check-current-manual-delivery-app-ready --stdout-json`.
Accepted work: `BTCFX-20260623-158-CURRENT-APP-INTEGRATION-CONTRACT` added `describe-current-manual-delivery-app-contract --stdout-json`; `BTCFX-20260623-159-PROGRESS-BOARD-CURRENT-APP-INTEGRATION` updated the progress board for the accepted app integration state; `BTCFX-20260623-161-PROGRESS-BOARD-HUMAN-READABILITY` made the board easier for humans to read and aligned the numbering.
Clean checkpoint: `22a35fb08410d260bca3cc92d00622aaf622cb01` preceded the readability update; current reviewed baseline for this roadmap is `6d263631cc08461d168824fc80410d9d54fbfd32`.
Canonical app/operator path: single-command app integration `refresh-current-manual-delivery-app --stdout-json`; read-side check `check-current-manual-delivery-app-ready --stdout-json`; contract introspection `describe-current-manual-delivery-app-contract --stdout-json`; stable read file `local/manual_delivery_handoff/app-snapshot.json`; validator/status file `local/manual_delivery_handoff/app-snapshot-status.json`; progress board `運用資料/進捗/Ver03-v1_進捗ボード_20260607.html`; integrated roadmap `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`.
