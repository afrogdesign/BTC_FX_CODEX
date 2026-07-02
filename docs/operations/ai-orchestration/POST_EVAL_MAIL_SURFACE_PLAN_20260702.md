# Post-Eval Mail Surface Plan 2026-07-02

## Purpose

Define the approval-gated mail-surface direction for compact `post_eval_recommendations` reflection.
Mail remains an entry point, not a full report.
This plan does not implement mail body changes or send-behavior changes.

## Completed Baseline

- Public HTML Post-Eval Recommendation Status is implemented.
- Local dashboard/app-surface Post-Eval Recommendation Status is implemented.
- App-ready ready-gate contract validation is implemented.
- Compact `post_eval_recommendations` remains report-only and human-approved.

## Current Contract Reference

The same compact payload contract remains the source of truth:

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

## Mail Surface Direction

- Mail is an entry point, not a full report.
- Future mail reflection may be one compact status line and/or a link/reference only.
- Any implementation requires explicit human approval in a later task.
- No sending behavior change in this task.
- No production wording, config, threshold, gate, or runtime change in this task.
- The source must be the same compact `post_eval_recommendations` payload.
- Mail rendering must not execute the recommendation engine.
- Mail rendering must not read raw rows, `source_uid_hash`, `UID`, account-like identifiers, API key names, SMTP details, private/order strings, or script/fetch-like unsafe strings.

## Safety Boundary

- report-only
- not FORMAL_GO
- no automatic order
- human decides manually
- no API calls
- no secrets
- no private/account/order endpoints
- no runtime restart
- no notification sending behavior change
- no mail body implementation in this task
- no raw exchange export commit
- no paper_positions.csv integration unless explicitly approved

## Deferred Tasks

- Mail summary compact status reflection
- Mail body implementation after explicit approval
- End-to-end generated report wiring
- Any production wording changes

## Stop Conditions

- If mail integration requires executing recommendation generation during render.
- If it requires reading raw MEXC exports or generated post-eval markdown/CSV.
- If it requires sending mail or changing send behavior.
- If it requires secrets/private endpoints/runtime changes.
- If generated/private data would need to be committed.

## Recommended Next Implementation

- `BTCFX-20260702-POST-EVAL-MAIL-SURFACE-IMPLEMENTATION`
- Goal: reflect the same compact post-eval status in mail with approval gating, only after explicit approval, and without changing send behavior or production wording in the planning phase.
- Keep the mail body deferred until that approval-gated task starts.
