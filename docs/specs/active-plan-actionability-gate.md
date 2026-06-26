# Active Plan Actionability Gate

Purpose: reduce human review load while preserving the BTCFX Ver03-v3 safety boundary.

## Product Decision

The next Ver03-v3 product step is Actionability Gate / Human Load Reducer.

The system should classify each Active Plan candidate before human review so that the human only inspects candidates that are actionable or require review.

This is not an automatic trading gate. It is report-only triage.

## Safety Boundary

- report-only
- not FORMAL_GO
- no automatic order
- ACTIVE_* guidance only
- human must decide manually
- no external notification integration
- no clipboard/address-book integration
- no paper_positions.csv integration
- no runtime/deploy/trading/API key/private endpoint changes
- CLI mode must not silently fall back to OpenAI API
- API usage requires explicit AI_API_USAGE_ALLOWED
- post-review API fallback is gated by AI_POST_REVIEW_API_FALLBACK_ENABLED

## Classification Labels

The gate should classify each candidate into exactly one of:

- AUTO_REJECT
- REVIEW_REQUIRED
- ACTIONABLE_COPY_READY
- NO_ACTION

## Classification Meaning

AUTO_REJECT:
The candidate should not require normal human review because one or more deterministic rejection conditions are present.

REVIEW_REQUIRED:
The candidate may be useful, but one or more uncertainty or safety conditions require human inspection.

ACTIONABLE_COPY_READY:
The candidate passed deterministic checks and may be prepared for manual copy/paste review. This is still not FORMAL_GO and not an automatic order.

NO_ACTION:
No practical action candidate is present.

## Initial Deterministic Inputs

The first version should use only existing report/local evidence where available:

- source_readiness
- source freshness state
- intraperiod outcome coverage
- pending caveat severity
- entry touched / not touched evidence
- TP before SL evidence when available
- SL before TP evidence when available
- timeout evidence when available
- MFE / MAE when available
- risk-reward after conservative fee/slippage buffer when available
- stale or duplicate signal evidence when available
- Active Plan label
- side
- entry condition
- TP plan
- SL or invalidation
- timeout or wait limit

## Initial AUTO_REJECT Conditions

Classify as AUTO_REJECT when any of the following are true:

- source_readiness is review_required_missing_or_stale_source
- required local source files are missing
- candidate timestamp is outside the available OHLCV window
- entry was not touched and the plan depends on entry touch
- pending coverage is too high for the candidate to be trusted without fresh evidence
- TP/SL/timeout cannot be evaluated from available evidence and the plan requires that evidence
- estimated reward/risk is below the configured minimum after conservative fee/slippage buffer
- candidate is stale relative to the configured review window
- duplicate candidate has already been reviewed for the same market context

## Initial REVIEW_REQUIRED Conditions

Classify as REVIEW_REQUIRED when none of the AUTO_REJECT conditions apply, but any of the following are true:

- source freshness is valid but near the stale threshold
- pending rows are concentrated in recent windows
- entry evidence exists but TP/SL ordering is ambiguous
- MFE/MAE indicates high adverse excursion
- volatility regime appears unsafe or unusually wide
- Active Plan label is counter-trend or counter-scalp
- required human context is missing from the manual-delivery JSON
- caveat text indicates coverage or timing uncertainty

## Initial ACTIONABLE_COPY_READY Conditions

Classify as ACTIONABLE_COPY_READY only when all of the following are true:

- source_readiness is ready
- required local source files are present
- candidate timestamp is inside the evidence window
- entry condition has supporting evidence or does not require touch evidence
- no AUTO_REJECT condition is present
- no REVIEW_REQUIRED condition is present
- safety boundary text is preserved
- output remains manual copy/paste only
- human must still make the final decision

## Initial NO_ACTION Conditions

Classify as NO_ACTION when:

- Active Plan result is NO_ACTION
- no usable candidate exists
- the system cannot produce a practical plan without inventing missing trade context

## Required Output Fields

Future implementation should eventually expose:

- actionability_label
- actionability_reasons
- human_action
- source_readiness
- evidence_summary
- safety_summary

Allowed human_action values:

- do_nothing
- review_only
- manual_copy_review

## Future Shadow Ledger Boundary

A later task may add a separate shadow decision CSV, for example:

`logs/csv/active_plan_shadow_decisions.csv`

This must remain separate from paper_positions.csv.

The shadow ledger is for evaluating whether candidates would have performed well. It must not be used as an order ledger.

## Explicit Non-Goals

This specification does not authorize:

- automatic orders
- live trading
- paper_positions.csv integration
- private/account/order endpoint access
- exchange API key access
- external notification integration
- Gmail/SMTP/Slack/LINE/Discord/webhook integration
- clipboard or address-book integration
- runtime restart
- deploy changes
- daily-sync execution
- report hub regeneration
- generated artifact commits

## Acceptance Criteria For This Docs Task

- The specification exists at docs/specs/active-plan-actionability-gate.md.
- TASK_LEDGER.md records BTCFX-20260612-123-ACTIONABILITY-GATE-DESIGN.
- The task remains docs-only.
- git diff --check passes.
- No generated artifact is committed.
- No source code or tests are changed.
