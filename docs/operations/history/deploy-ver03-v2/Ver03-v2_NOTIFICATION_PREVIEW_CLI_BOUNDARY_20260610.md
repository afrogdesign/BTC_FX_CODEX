# Ver03-v2 notification preview CLI boundary

## Purpose
- Define the approved boundary for a future minimal report-only notification preview CLI / manual-output path.
- The future path exists only to produce a human-readable report-only notification preview for human BTC trading decisions.
- It is not FORMAL_GO.
- It is not an automatic order.
- This document does not approve email sending, daily-sync, runtime, deploy, or trading integration.

## Allowed Future Manual-Output Behavior
- `stdout` preview output is allowed.
- An explicit local output text path may be allowed as a generated artifact.
- Any generated preview file must remain local and uncommitted unless a later task explicitly approves a committed review document.
- Manual human copy/paste from a terminal or local text file is allowed as a human action outside repo automation.
- The preview must visibly include report-only wording, not FORMAL_GO wording, no automatic order wording, ACTIVE_* guidance-only wording, a pending caveat, and a detail report path.

## Future CLI Input Boundary
- Inputs must be explicit and local.
- Inputs may only represent already-approved report / notification fields.
- No fetching, no builder rerun, and no report regeneration are allowed.
- No exchange, private, account, or order endpoint access is allowed.
- No secrets or API keys are allowed.
- No inference that changes evaluator semantics or trading logic is allowed.
- No `paper_positions.csv` integration is allowed.

## Prohibited Behavior
- Email sending.
- SMTP.
- Gmail.
- Webhook delivery.
- Cron.
- launchd.
- notification service integration.
- Clipboard automation such as `pbcopy`.
- Auto-opening mail clients or browsers for delivery.
- Daily-sync execution.
- Runtime or deploy integration.
- `main.py`.
- `run_cycle`.
- API keys, secrets, private/account/order endpoints.
- Live trading.
- Automatic orders.
- `paper_positions.csv` integration.
- Evaluator semantic changes.
- Trading logic changes.
- Generated CSV, report, or preview commits.

## Future Implementation Gate
- Future CLI implementation must be a separate approved task.
- Future implementation must include targeted tests.
- Future implementation must remain preview-only and manual-output-only.
- Any email delivery, daily-sync, runtime, deploy, or trading integration requires a later separate boundary review and explicit approval.

## Human Interpretation
- ACTIVE_* remains practical action guidance only.
- A human must still inspect the detailed report and market context and decide manually.
- Pending or unresolved outcomes must remain visible because they reduce confidence.
- The preview must never be phrased as permission for automatic trading.
