# Post-Eval Surface Alignment Plan 2026-07-02

## Purpose

Align post-eval recommendation status across public HTML, local dashboard/app surface, and notification mail.
Keep all surfaces report-only and single-source.
Public HTML already has the first display-only reflection, so this plan treats that contract as the current baseline.

## Completed History

- MEXC actual trade importer
- Actual trade to signal linker
- Biweekly ground truth report
- Post-eval recommendation engine
- Public HTML Post-Eval Recommendation Status section
- Local dashboard/app-surface Post-Eval Recommendation Status
- App-ready ready-gate contract validation

## Current Accepted Payload Contract

The compact payload contract already used by the public HTML surface is the reference shape:

- `schema_version`
- `report_date`
- `report_path`
- `output_csv_path`
- `candidate_count`
- `top_recommendation_codes`
- `priority_counts`
- `confidence_counts`
- `safety_boundary`
- `note`
- `human_approval_required` / `required_human_approval`

## Surface Alignment Target

### Public HTML

- Already displays compact report-only recommendation metadata when present.
- Hidden when absent.
- Safe degradation on malformed payload.

### Local Dashboard / App Surface

- Implemented as the same compact status, not raw candidate rows.
- It does not execute `tools/log_feedback.py` from dashboard rendering.
- It does not read private/generated CSV unless an existing refresh/export command explicitly provides compact data.

### Notification Mail

- Should remain an entry point, not a full report.
- Future implementation may add one compact status line or link/reference only after human approval.
- No sending behavior change in this planning phase.
- No production wording change in this task.
- Mail body changes remain deferred and require explicit approval.

## Single-Source Doctrine

- The same compact `post_eval_recommendations` payload should feed public HTML, dashboard/app surface, and mail summary when approved.
- Do not create separate trading logic per surface.
- Do not recompute recommendation ranking inside surface renderers.

## Safety and Privacy Constraints

- No API calls.
- No secrets.
- No private/account/order endpoints.
- No automatic orders.
- No runtime restart.
- No generated or raw exchange export commit.
- No `source_uid_hash`, `UID`, account-like identifiers, raw rows, SMTP details, API key names, or private/order strings in surfaces.
- HTML/text must escape or sanitize payload values.
- Human approval is required before wording/config/threshold/gate/runtime changes.

## Recommended Next Implementation

- `BTCFX-20260702-POST-EVAL-MAIL-SURFACE-PLAN`
- Goal: define the approval-gated mail-surface direction for compact post-eval reflection without implementing mail body changes.
- Keep mail as an entry point, not a full report, and defer any body/sending changes to a later explicit-approval task.

## Deferred Tasks

- Mail summary compact status reflection
- Mail body implementation after explicit approval
- End-to-end generated report wiring
- Any production wording changes

## Stop Conditions For Future Implementation

- If dashboard/mail integration requires executing recommendation generation during render.
- If it requires reading raw MEXC exports.
- If it requires sending mail or changing send behavior.
- If it requires secrets/private endpoints/runtime changes.
- If generated/private data would need to be committed.

## Updated Baseline

- Public HTML Post-Eval Recommendation Status is implemented.
- Local dashboard/app-surface Post-Eval Recommendation Status is implemented.
- App-ready ready-gate contract validation is implemented.
- Compact `post_eval_recommendations` remains report-only and human-approved.
- Mail body changes remain deferred and require explicit approval.
- End-to-end payload handoff is the next planning target.
