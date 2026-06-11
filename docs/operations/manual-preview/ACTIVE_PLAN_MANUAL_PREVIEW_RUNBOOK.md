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

## Manual Delivery Copy Package

- Use `write-latest-active-plan-manual-delivery-package` when you need a copy-ready subject/body/checklist package for human copy/paste only.
- This package is for manual handling only and does not perform email, Gmail, webhook, Slack, LINE, Discord, cron, launchd, clipboard, address-book, or any other external notification integration.
- Keep the same safety boundary: report-only, not FORMAL_GO, no automatic order, ACTIVE_* guidance only, human must decide manually.

## Manual Delivery Local File Bundle

- Use `write-latest-active-plan-manual-delivery-files --output-dir <path>` when you need explicit local files for manual copy/paste only.
- The bundle writes `subject.txt`, `body.txt`, `checklist.txt`, `package.txt`, and `README.txt` to the requested local directory.
- Generated files must not be committed unless explicitly approved.
- This bundle does not perform email, Gmail, webhook, Slack, LINE, Discord, cron, launchd, clipboard, address-book, or any other external notification integration.
- Keep the same safety boundary: report-only, not FORMAL_GO, no automatic order, ACTIVE_* guidance only, human must decide manually.

## Pending Coverage Caveat Diagnostic

- Use `format-active-plan-pending-coverage-caveat --total-outcome-rows <n> --resolved-rows <n> --pending-rows <n>` to generate a deterministic one-line caveat.
- Paste the output into `--pending-caveat` when running preview or delivery commands, or copy the same string into `pending_caveat` in JSON input.
- Keep the same safety boundary: report-only, not FORMAL_GO, no automatic order, ACTIVE_* guidance only, human must decide manually.

## Pending Coverage Caveat From CSV

- Use `format-active-plan-pending-coverage-caveat-from-csv --intraperiod-outcomes-path <csv>` to derive the same caveat from an existing intraperiod outcomes CSV.
- Paste the resulting line into `--pending-caveat` or copy it into the JSON `pending_caveat` field.
- Keep the same safety boundary: report-only, not FORMAL_GO, no automatic order, ACTIVE_* guidance only, human must decide manually.

## Operational Notes

- Generated preview files and generated reports must not be committed unless explicitly approved.
- This workflow does not send email, Gmail, webhook, Slack, LINE, Discord, cron, launchd, clipboard, or any external notification.
- This workflow does not run daily-sync, report hub generation, runtime, deploy, trading, API keys, private endpoints, or `paper_positions.csv` changes.
