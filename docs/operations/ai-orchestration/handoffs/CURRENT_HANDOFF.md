# Current Handoff

last_updated: 2026-06-23
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v4`
canonical_working_dir: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
current_commit: fc730ea1c425abfd9e7aa0f3e9d27ddafde88208
latest_reviewed_baseline: fc730ea1c425abfd9e7aa0f3e9d27ddafde88208

## State

Current handoff reflects the accepted Ver03-v4 manual action surface/mail milestone sequence and the accepted intraperiod milestone sequence 188/189/191/192/195/197 plus the human-readable current manual-delivery progress board update. There is no active handoff. The safety boundary remains report-only / not FORMAL_GO / no automatic order / human decides manually.

## Safety Boundary

- Report-only.
- Not `FORMAL_GO`.
- No automatic order.
- No API keys.
- No private, account, or order endpoints.
- No runtime restart.
- No `paper_positions.csv` integration unless explicitly approved.

## Next Decision

Continue with local/report-only operator tooling, diagnostics, and evidence-based accuracy using the intraperiod review workflow. Daily-sync wiring, exchange fetch, trading logic changes, private/order endpoints, runtime behavior, notification sending, and paper_positions.csv remain out of scope.

## Deferred Follow-up / Post-build Check

- CLI/API key configuration may have changed.
- Verification is intentionally deferred until after current build work.
- no API key value reading
- no secret printing
- no private/account/order endpoint calls
- no live trading
- no order placement
- Verification later should be configuration/dry-run/docs only.

## Evidence

Historical accepted task details live in git/GitHub, `docs/operations/ai-orchestration/TASK_LEDGER.md`, and `docs/operations/ai-orchestration/CONTROL.md` when needed.
Integrated roadmap: `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`.
Accepted Ver03-v4 surface sequence: `BTCFX-20260623-181-V4-PUBLIC-HTML-MANUAL-ACTION-CHECKLIST`; `BTCFX-20260623-183-V4-LOCAL-DASHBOARD-ACTION-SURFACE-ALIGNMENT`; `BTCFX-20260623-184-V4-LOCAL-DASHBOARD-CHECKLIST-READY-GATE`; `BTCFX-20260623-186-V4-MAIL-MANUAL-ACTION-CHECKLIST`.
Accepted intraperiod sequence: `BTCFX-20260623-188-V4-INTRAPERIOD-TP2-DEEPER-TARGET-CLASSIFICATION`; `BTCFX-20260623-189-V4-INTRAPERIOD-OUTCOME-CSV-CLI`; `BTCFX-20260623-191-V4-INTRAPERIOD-REPORT-OPERATOR-WIRING`; `BTCFX-20260623-192-V4-INTRAPERIOD-LOCAL-REVIEW-CLI`; `BTCFX-20260623-195-V4-INTRAPERIOD-REVIEW-STDOUT-JSON`.
Local/report-only intraperiod operator review now has `build-active-plan-intraperiod-outcomes`, `build-active-plan-intraperiod-review`, `build-active-plan-intraperiod-review --stdout-json`, app contract exposure for `active_plan_intraperiod_review.v1`, and Ver03-v4 intraperiod report guidance. Stdout JSON exposes report-only safety flags and does not allow exchange fetch, daily-sync wiring, secret reading, automatic orders, or FORMAL_GO.
Accepted E2E: `BTCFX-20260623-156-CURRENT-APP-REFRESH-STDOUT-JSON-E2E-REVIEW` passed in a tempdir using `refresh-current-manual-delivery-app --stdout-json` and `check-current-manual-delivery-app-ready --stdout-json`.
Accepted work: `BTCFX-20260623-158-CURRENT-APP-INTEGRATION-CONTRACT` added `describe-current-manual-delivery-app-contract --stdout-json`; `BTCFX-20260623-159-PROGRESS-BOARD-CURRENT-APP-INTEGRATION` updated the progress board for the accepted app integration state; `BTCFX-20260623-161-PROGRESS-BOARD-HUMAN-READABILITY` made the board easier for humans to read and aligned the numbering.
Clean checkpoint: `22a35fb08410d260bca3cc92d00622aaf622cb01` preceded the readability update; current reviewed baseline for this roadmap is `6d263631cc08461d168824fc80410d9d54fbfd32`.
Canonical app/operator path: single-command app integration `refresh-current-manual-delivery-app --stdout-json`; read-side check `check-current-manual-delivery-app-ready --stdout-json`; contract introspection `describe-current-manual-delivery-app-contract --stdout-json`; smallest stable read file `local/manual_delivery_handoff/app-snapshot.json`; validator/status file `local/manual_delivery_handoff/app-snapshot-status.json`; progress board `運用資料/進捗/Ver03-v1_進捗ボード_20260607.html`; roadmap `docs/operations/strategy/VER03_V4_INTEGRATED_TRADING_SYSTEM_PLAN.md`.
