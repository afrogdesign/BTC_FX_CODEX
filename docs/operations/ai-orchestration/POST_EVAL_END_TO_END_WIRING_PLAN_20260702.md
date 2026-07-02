# Post-Eval End-to-End Wiring Plan 2026-07-02

## Purpose

Define the end-to-end compact `post_eval_recommendations` payload flow without changing code, runtime behavior, or mail sending behavior.
The recommendation engine produces the compact payload once, and approved handoff steps carry that payload into the app surface, ready gate, public HTML, and mail body.
The payload handoff contract is now implemented; this document keeps the remaining safe sequence explicit.
Surface renderers must consume already-provided compact payload only.
They must not execute the recommendation engine.
They must not read generated post-eval markdown/CSV directly.

## Intended Payload Flow

1. Recommendation engine produces compact `post_eval_recommendations` evidence.
2. An approved refresh/export/check step carries the compact payload into app snapshot / app contract / app-ready data.
3. Public HTML, dashboard/app surface, app-ready, and mail body reflect only the already-provided compact payload.
4. No surface renderer recomputes ranking or reads raw/generated report files.

## Payload Contract Boundaries

Allowed compact metadata only:

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

Not allowed in surface renderers:

- raw rows
- `source_uid_hash`
- `UID`
- account-like identifiers
- API key names
- SMTP details
- private/order strings
- `send_email`
- `Gmail`
- `smtp`
- script/fetch-like unsafe strings

## Intended Sequence

### 1. Payload Source Handoff Contract

- Implemented as a compact, sanitized handoff shape.
- Keep the engine output separate from all surface renderers.
- The handoff must be report-only, not FORMAL_GO, no automatic order, human decides manually.

### 2. CLI / Export Wiring

- Approved refresh/export/check steps carry the compact payload into app surface artifacts.
- No renderer should trigger generation on demand.
- No renderer should read generated post-eval markdown/CSV directly.

### 3. App Snapshot / Contract Verification

- Validate that app snapshot, app contract, and app-ready carry compact metadata only.
- Verify optional presence and safe malformed handling without making the payload mandatory for readiness.

### 4. Surface Smoke Tests

- Smoke-test public HTML, dashboard/app surface, app-ready, and mail body against the already-provided payload.
- Keep tests focused on display-only reflection and privacy-safe degradation.

### 5. Docs Update

- Sync the surface alignment plan, mail surface plan, and NEXT_ACTION after the wiring contract is settled.

## Deferred Items

- Runtime scheduling changes
- Notification sending behavior changes
- Production wording/config/threshold/gate changes
- Raw/generated/private data commits
- Trading logic changes
- API / private endpoint / order execution changes

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
- no mail body implementation in this plan
- no generated or raw exchange export commit

## Stop Conditions

- If the wiring requires executing recommendation generation during render.
- If the wiring requires reading raw MEXC exports or generated post-eval markdown/CSV directly.
- If the wiring requires changing send behavior or runtime scheduling.
- If the wiring requires secrets, private endpoints, order execution, or production wording changes.
- If generated/private data would need to be committed.

## Next Hand-off

- `BTCFX-20260702-POST-EVAL-EXPORT-WIRING`
- Goal: wire the approved compact payload into export/check paths so app-surface artifacts carry only sanitized metadata without renderer-side generation.
