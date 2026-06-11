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

## Latest Manual Delivery Source Resolver

- Use `resolve-latest-manual-delivery-source-files` as Step 1 before JSON generation when you want the current local source paths first.
- It reduces manual file-path selection before the JSON template or bundle steps.
- It stays local/report-only and does not fetch, rebuild, regenerate, notify, trade, or send anything.
- Keep the same safety boundary: report-only, not FORMAL_GO, no automatic order, ACTIVE_* guidance only, human must decide manually.

## Latest Manual Delivery Input JSON Seed

- Use `write-latest-manual-delivery-input-json --output-json <path>` as Step 2 after the source resolver and before local bundle generation.
- It removes manual JSON bootstrapping, but the resulting JSON still requires human review before any later local bundle step.
- It does not infer trade approval or FORMAL_GO.
- Keep the same safety boundary: report-only, not FORMAL_GO, no automatic order, human must decide manually, no external notification integration.

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

## One-Command Local Manual Delivery Bundle From JSON + CSV

- Use `write-latest-active-plan-manual-delivery-files-from-json --input-json <path> --output-dir <path> --auto-pending-caveat-from-csv` when you want a one-command local bundle path.
- This removes the manual caveat copy/paste step by deriving `pending_caveat` from the existing intraperiod outcomes CSV.
- The output is still local files only, and the generated bundle remains `subject.txt`, `body.txt`, `checklist.txt`, `package.txt`, and `README.txt`.
- Keep the same safety boundary: report-only, not FORMAL_GO, no automatic order, human must decide manually, no external notification integration.

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
