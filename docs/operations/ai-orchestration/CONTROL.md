# AI Orchestration Control

last_updated: 2026-06-24
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v4`
project_key: `BTCFX`
current_commit: 9a2b4fb2c6864ebea7c57013b5b32461cef4496b
note: `current_commit` is the latest ChatGPT-accepted baseline and may intentionally lag branch HEAD. That lag alone is not a BLOCK condition.

---

## Current State

Current reviewed baseline is the accepted Ver03-v4 manual action surface/mail milestone sequence `BTCFX-20260623-181-V4-PUBLIC-HTML-MANUAL-ACTION-CHECKLIST`, `BTCFX-20260623-183-V4-LOCAL-DASHBOARD-ACTION-SURFACE-ALIGNMENT`, `BTCFX-20260623-184-V4-LOCAL-DASHBOARD-CHECKLIST-READY-GATE`, `BTCFX-20260623-186-V4-MAIL-MANUAL-ACTION-CHECKLIST`, plus the accepted runtime/operator status milestone `BTCFX-20260623-216-V4-OPERATOR-STATUS-SHORTCUT`, the accepted operator status app contract / ready gate milestone `BTCFX-20260623-218-V4-APP-CONTRACT-OPERATOR-STATUS`, the accepted operator status diagnostics display milestone `BTCFX-20260623-221-V4-APP-SURFACE-OPERATOR-STATUS-DISPLAY`, the accepted operator status stdout JSON evidence milestone `BTCFX-20260623-223-V4-APP-SURFACE-OPERATOR-STATUS-STDOUT-JSON`, the accepted safe config schema audit CLI and app surface integration milestone, the accepted operator triage summary integrated-surface milestone, the accepted integrated_evidence_overview app/public/mail milestone, and the accepted integrated_evidence_overview operator hints milestone. The accepted intraperiod milestone sequence remains `BTCFX-20260623-188-V4-INTRAPERIOD-TP2-DEEPER-TARGET-CLASSIFICATION`, `BTCFX-20260623-189-V4-INTRAPERIOD-OUTCOME-CSV-CLI`, `BTCFX-20260623-191-V4-INTRAPERIOD-REPORT-OPERATOR-WIRING`, `BTCFX-20260623-192-V4-INTRAPERIOD-LOCAL-REVIEW-CLI`, `BTCFX-20260623-195-V4-INTRAPERIOD-REVIEW-STDOUT-JSON`, `BTCFX-20260623-197-V4-APP-CONTRACT-INTRAPERIOD-REVIEW-JSON`, `BTCFX-20260623-199-V4-APP-SURFACE-CONTRACT-INTRAPERIOD-JSON-READY-GATE`, `BTCFX-20260623-201-V4-PUBLIC-HTML-INTRAPERIOD-JSON-CONTRACT-SURFACE`, and `BTCFX-20260623-202-V4-PUBLIC-HTML-INTRAPERIOD-JSON-MILESTONE-SYNC`. The current manual-delivery app surface, app surface validation stdout JSON, public HTML report, notification mail (main and attention bodies), and dashboard now share `operator_triage_summary` and `integrated_evidence_overview` evidence, and alias lookup also supports `app_surface_validation`, `app_surface_validation_data`, `manual_delivery_app_surface_validation`, and `current_manual_delivery_app_surface_validation`. The public HTML report, notification mail body, local dashboard HTML, app surface validation, intraperiod outcome tooling, manual-delivery app contract, public HTML report surface, runtime startup observability, operator status CLI, and safe config schema audit CLI share the local/report-only boundary and same-bar TP2 classification boundary. Intraperiod tooling now has same-bar TP1+TP2 without SL classified as `tp2_first`, the local-file-only outcome CSV builder `build-active-plan-intraperiod-outcomes`, Ver03-v4 operator report guidance wired to that local CSV CLI, the one-shot local review CLI `build-active-plan-intraperiod-review` with machine-readable `--stdout-json` support, the app contract exposure for `build-active-plan-intraperiod-review --stdout-json` with `active_plan_intraperiod_review.v1` safety flags, the app contract / ready gate / dashboard / stdout JSON evidence for `safe_config_schema_audit`, the app contract / ready gate / stdout JSON evidence for `integrated_evidence_overview` ready-gate fields and missing/not-ready list fields, and the public HTML and notification mail reflections for `intraperiod_review_stdout_json`, `operator_status_diagnostic`, `safe_config_schema_audit`, `operator_triage_summary`, and `integrated_evidence_overview`. The app surface / ready gate now rejects missing or invalid `intraperiod_review_stdout_json` contract exposure and requires the accepted local/report-only safety flags: `local/report-only`, no exchange fetch, no daily-sync wiring, no secret/API key reading, and the safety flags that prevent FORMAL_GO / automatic orders / secret reading. The safety boundary remains report-only / not FORMAL_GO / no automatic order / human decides manually. The latest ChatGPT-reviewed baseline is now `9a2b4fb2c6864ebea7c57013b5b32461cef4496b`, and the current manual-delivery app dashboard now displays `integrated_evidence_overview` list fields (`evidence_keys`, `missing_evidence_keys`, `not_ready_evidence_keys`, `execution_required_keys`) from already-derived in-memory data only, rendering empty missing/not-ready/execution-required lists as `none` without executing diagnostics. The operator_triage_summary integrated-surface milestone is aligned across current manual-delivery app surface validation stdout JSON, public HTML, and notification mail, and alias lookup includes `app_surface_validation`, `app_surface_validation_data`, `manual_delivery_app_surface_validation`, and `current_manual_delivery_app_surface_validation`. The integrated_evidence_overview milestone is aligned across current manual-delivery app dashboard, current manual-delivery app surface validation stdout JSON, public HTML report, and notification mail main and attention bodies; it covers `intraperiod_review_stdout_json`, `operator_status_diagnostic`, `safe_config_schema_audit`, `operator_triage_summary`, and `manual_action_checklist_surface`, and it is rendered only when evidence is present. The integrated_evidence_overview operator hints milestone is now accepted and reflected across current manual-delivery app surface validation stdout JSON, current manual-delivery app dashboard, public HTML report, and notification mail main and attention bodies using existing safe integrated_evidence_overview fields only. The major turning point opportunity milestone is accepted and aligned across public HTML report, notification mail main/attention bodies, and the current manual-delivery app dashboard, using existing result/display/notification context or snapshot/status fields only. The major turning point diagnostic milestone is accepted and aligned across the Active Plan intraperiod outcomes markdown report, current manual-delivery app surface validation stdout JSON, current manual-delivery app dashboard, public HTML report, and notification mail main and attention bodies; it uses existing local active_plan_candidate_intraperiod_outcomes.csv fields only where generated and public/mail only reflect already-derived safe fields, classifies potential_missed_turn, potential_fakeout, bad_entry_timing, and inconclusive, and remains post-hoc diagnostic support only without confirming a major turn or authorizing manual or automatic entry.


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

Continue with local/report-only operator tooling, diagnostics, and evidence-based accuracy using the intraperiod review workflow, app contract exposure, public HTML report surface, and runtime/operator status diagnostics, without daily-sync wiring, exchange fetch, trading logic changes, notification sending, runtime changes, report regeneration, or automation safety changes.

## Deferred Follow-up / Post-build Check

- CLI/API key configuration may have changed.
- Verification is intentionally deferred until after current build work.
- Future validation must not read or print API key values.
- Future validation must inspect configuration names, CLI/env var wiring, dry-run/safe error behavior, and documentation consistency only.
- Future validation must not call private/account/order endpoints, place orders, run live trading, or expose secrets.

## Evidence Note

Historical accepted task details live in git/GitHub and `docs/operations/ai-orchestration/TASK_LEDGER.md` when needed. Major turning point diagnostic milestone evidence includes the local/report-only markdown diagnostic summary, current manual-delivery app surface validation stdout JSON and dashboard exposure, public HTML report reflection, and notification mail reflection; the diagnostic remains post-hoc support only and does not confirm a major turn or authorize manual or automatic entry.
Runtime/operator status milestone: runtime startup observability, public HTML runtime startup status section, `runtime_public_status.py` JSON/pretty/check modes, `operator_status.py` wrapper, app contract / ready gate exposure for `operator_status_diagnostic`, app surface display of `operator_status_diagnostic` from contract data, and app surface stdout-json evidence for `operator_status_diagnostic`.
Accepted Ver03-v4 surface sequence: `BTCFX-20260623-181-V4-PUBLIC-HTML-MANUAL-ACTION-CHECKLIST`; `BTCFX-20260623-183-V4-LOCAL-DASHBOARD-ACTION-SURFACE-ALIGNMENT`; `BTCFX-20260623-184-V4-LOCAL-DASHBOARD-CHECKLIST-READY-GATE`; `BTCFX-20260623-186-V4-MAIL-MANUAL-ACTION-CHECKLIST`; `BTCFX-20260623-197-V4-APP-CONTRACT-INTRAPERIOD-REVIEW-JSON`; `BTCFX-20260623-201-V4-PUBLIC-HTML-INTRAPERIOD-JSON-CONTRACT-SURFACE`; `BTCFX-20260623-221-V4-APP-SURFACE-OPERATOR-STATUS-DISPLAY`; `BTCFX-20260623-223-V4-APP-SURFACE-OPERATOR-STATUS-STDOUT-JSON`.
Accepted intraperiod sequence: `BTCFX-20260623-188-V4-INTRAPERIOD-TP2-DEEPER-TARGET-CLASSIFICATION`; `BTCFX-20260623-189-V4-INTRAPERIOD-OUTCOME-CSV-CLI`; `BTCFX-20260623-191-V4-INTRAPERIOD-REPORT-OPERATOR-WIRING`; `BTCFX-20260623-192-V4-INTRAPERIOD-LOCAL-REVIEW-CLI`; `BTCFX-20260623-195-V4-INTRAPERIOD-REVIEW-STDOUT-JSON`; `BTCFX-20260623-199-V4-APP-SURFACE-CONTRACT-INTRAPERIOD-JSON-READY-GATE`.
Visible local/report-only intraperiod path: `build-active-plan-intraperiod-outcomes`; `build-active-plan-intraperiod-review`; `build-active-plan-intraperiod-review --stdout-json`; Ver03-v4 intraperiod report guidance; app contract exposure for `active_plan_intraperiod_review.v1`; app surface / ready gate validation for `intraperiod_review_stdout_json`; public HTML report reflection for the accepted intraperiod JSON contract surface.
Accepted E2E: `BTCFX-20260623-156-CURRENT-APP-REFRESH-STDOUT-JSON-E2E-REVIEW` passed in a tempdir using `refresh-current-manual-delivery-app --stdout-json` and `check-current-manual-delivery-app-ready --stdout-json`.
Accepted work: `BTCFX-20260623-158-CURRENT-APP-INTEGRATION-CONTRACT` added `describe-current-manual-delivery-app-contract --stdout-json`; `BTCFX-20260623-159-PROGRESS-BOARD-CURRENT-APP-INTEGRATION` updated the progress board for the accepted app integration state; `BTCFX-20260623-161-PROGRESS-BOARD-HUMAN-READABILITY` made the board easier for humans to read and aligned the numbering.
Clean checkpoint: `22a35fb08410d260bca3cc92d00622aaf622cb01` preceded the readability update; current reviewed baseline for this roadmap is `6d263631cc08461d168824fc80410d9d54fbfd32`.
Canonical app/operator path: single-command app integration `refresh-current-manual-delivery-app --stdout-json`; read-side check `check-current-manual-delivery-app-ready --stdout-json`; contract introspection `describe-current-manual-delivery-app-contract --stdout-json`; stable read file `local/manual_delivery_handoff/app-snapshot.json`; validator/status file `local/manual_delivery_handoff/app-snapshot-status.json`; progress board `運用資料/進捗/Ver03-v1_進捗ボード_20260607.html`; integrated roadmap `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`.
