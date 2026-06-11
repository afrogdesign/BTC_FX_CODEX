# Ver03-v2 notification manual delivery boundary

## Purpose
- Define a future manual delivery workflow boundary after the accepted report-only notification preview CLI output review.
- This is docs-only.
- This does not approve implementation.
- This does not approve email sending, daily-sync, runtime, deploy, notification service integration, or trading integration.

## Approved Current Baseline
- The preview body is report-only.
- It is not FORMAL_GO.
- It is not an automatic order.
- ACTIVE_* remains guidance only.
- Pending or unresolved outcomes reduce confidence.
- A human must inspect the detailed report and market context and decide manually.

## Allowed Future Manual Delivery Workflow
- A human may run the existing local preview CLI manually.
- A human may inspect stdout or an explicitly chosen local text output file.
- A human may manually copy text from terminal or local text file.
- A human may manually paste the text into an external app outside repo automation.
- The external app choice and actual send/post/share action must remain a human action outside Codex/repo automation.
- The repo may document a checklist for manual delivery, but must not automate the delivery.
- The repo may allow a local generated preview text file when explicitly requested, but that file must remain local and uncommitted unless a later task explicitly approves a committed review fixture.

## Required Human Checks Before Any Manual Delivery
- Confirm report-only wording is visible.
- Confirm not FORMAL_GO is visible.
- Confirm no automatic order wording is visible.
- Confirm ACTIVE_* guidance-only wording is visible.
- Confirm pending caveat is visible.
- Confirm detail report path is visible.
- Confirm symbol, timeframe, and data freshness are visible.
- Confirm entry, TP, SL, and timeout are visible.
- Confirm the human has inspected the detailed report or intentionally chosen not to trade.
- Confirm no automatic trade or order action will be taken from the message.

## Prohibited Behavior
- Email sending implementation.
- SMTP.
- Gmail API.
- Webhook delivery.
- Slack, LINE, Discord, or other notification service integration.
- Cron.
- launchd.
- Scheduled delivery.
- Daily-sync integration.
- Runtime or deploy integration.
- `main.py`.
- `run_cycle`.
- Clipboard automation such as `pbcopy`.
- Auto-opening mail clients, browsers, or messaging apps.
- Address book or contact lookup automation.
- API keys or secrets.
- Exchange, private, account, or order endpoints.
- Live trading.
- Automatic orders.
- `paper_positions.csv` integration.
- Evaluator semantic changes.
- Trading logic changes.
- Generated CSV, report, or preview commits.

## Future Implementation Gate
- Any future manual-delivery support implementation must be a separate approved task.
- It must remain preview-only and manual-output-only unless a later boundary explicitly changes that.
- It must use explicit local inputs only.
- It must not fetch market data.
- It must not regenerate reports.
- It must not run builders.
- It must not run daily-sync, report hub, runtime, or deploy.
- It must include targeted tests if source code changes.
- It must keep generated preview output uncommitted.
- It must require a separate boundary review and explicit approval before any actual email or delivery integration.

## Not Approved by This Document
- No email sending.
- No scheduled delivery.
- No notification-service integration.
- No runtime/deploy integration.
- No trading integration.
- No automatic order flow.
- No approval to connect ACTIVE_* to `paper_positions.csv`.

## Conservative Next Step
- Review this manual delivery boundary before any implementation.
- Do not proceed directly to email sending implementation.
- Do not proceed to daily-sync, runtime/deploy, notification-service, or trading integration.
