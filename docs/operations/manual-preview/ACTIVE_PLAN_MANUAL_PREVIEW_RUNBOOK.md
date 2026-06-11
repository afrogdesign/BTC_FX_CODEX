# Active Plan Manual Preview Runbook

Purpose: report-only human manual trading support preview.

## Safety Boundary

- report-only
- not FORMAL_GO
- no automatic order
- ACTIVE_* guidance only
- human must decide manually

## Workflow

1. Generate an editable JSON template.
   - Use `write-latest-active-plan-manual-preview --print-input-json-template` to inspect the template on stdout.
   - Use `write-latest-active-plan-manual-preview --write-input-json-template <path>` to write the same template to a local file.
2. Edit the JSON manually.
   - Fill in the required preview fields and, if needed, set `detail_report_path`.
   - Do not change the safety boundary.
3. Generate the stdout preview from JSON.
   - Run `write-latest-active-plan-manual-preview --input-json <path>`.
   - The command may resolve the latest intraperiod report automatically when `detail_report_path` is omitted.
4. Optionally write the preview to a local file.
   - Add `--output-path <path>` when you need a saved preview.

## Operational Notes

- Generated preview files and generated reports must not be committed unless explicitly approved.
- This workflow does not send email, Gmail, webhook, Slack, LINE, Discord, cron, launchd, clipboard, or any external notification.
- This workflow does not run daily-sync, report hub generation, runtime, deploy, trading, API keys, private endpoints, or `paper_positions.csv` changes.
