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

## Local Manual Delivery Inbox

- Use `write-latest-manual-delivery-local-inbox --input-json <path> --bundle-dir <path> --output-md <path>` as Step 3 after the source resolver and JSON seed.
- It summarizes the local JSON plus bundle files for human review.
- It does not send, notify, fetch, rebuild, trade, or approve anything.
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

## One-Command Local Manual Delivery Flow

- Use `write-latest-manual-delivery-local-flow --output-dir <path>` as the next product step after the reviewed and E2E-verified local manual-delivery flow.
- It generates `source-files.txt`, `manual-delivery-input.json`, `bundle/subject.txt`, `bundle/body.txt`, `bundle/checklist.txt`, `bundle/package.txt`, `bundle/README.txt`, and `inbox.md` under one local output directory.
- It also writes `manifest.json` for local app/operator consumption.
- Review that `manifest.json` with `summarize-manual-delivery-local-flow-manifest --manifest-json <output-dir>/manifest.json` when you want a deterministic local operator summary.
- Add `--output-json <path>` to that manifest review command when you want a machine-readable local app/operator review output.
- It reduces manual steps, but it still does not send, notify, fetch, rebuild, trade, or approve anything.
- Keep the same safety boundary: report-only, not FORMAL_GO, no automatic order, ACTIVE_* guidance only, human must decide manually, no external notification integration.

## One-Command Local Manual Delivery Review Package

- Use `write-latest-manual-delivery-review-package --output-dir <path>` when you want the local flow plus `review/manifest-summary.md` and `review/manifest-review.json` in one report-only command.
- It is the app/operator one-command local review package and keeps the same safety boundary: report-only, not FORMAL_GO, no automatic order, ACTIVE_* guidance only, human must decide manually, no external notification integration.
- Use `write-current-manual-delivery-handoff` as the recommended app/operator handoff command when you want the stable default `local/manual_delivery_handoff` package, pointer, status, human gate, and handoff status outputs in one run.
- Use `write-latest-manual-delivery-local-handoff --handoff-dir <path>` when you want the same stable handoff layout under a custom directory.
- Treat `human-gate.json` as the smallest report-only, human-review-only gate file for app/operator handoff.
- Use `summarize-current-manual-delivery-handoff` as the default app/operator read-side status command.
- Use `self-check-current-manual-delivery-handoff` as the final local E2E confidence command after the write and read commands.
- Use `summarize-current-manual-delivery-handoff-self-check` as the app/operator read-side validator for `self-check.json`.
- Validate the stable handoff with `summarize-manual-delivery-local-handoff --handoff-dir <path>` before handing it to the app/operator side.
- Add `--write-handoff-status` when you want one command to create and validate `handoff-status.md` and `handoff-status.json` for the same stable handoff.
- Add `--write-local-handoff` when you want that one command to also write `review/latest-pointer.json`, `review/latest-status.md`, and `review/latest-status.json` as the recommended local app/operator handoff mode.
- Add `--latest-pointer-json <path>` when you want one optional local app/operator handoff file that points to `manifest.json`, `review/manifest-summary.md`, and `review/manifest-review.json`.
- Add `--latest-status-md <path>` and `--latest-status-json <path>` when you want the same one-command package to also emit validated latest status handoff files for local app/operator use.
- Validate that pointer with `summarize-latest-manual-delivery-pointer --latest-pointer-json <path>` before handing it off.
- Use `write-current-manual-delivery-app-state` as the smallest app-facing read model after self-check validation, and `summarize-current-manual-delivery-app-state --stdout-json` as the app/operator read-side validator for `app-state.json`.
- Use `refresh-current-manual-delivery-app --stdout-json` as the single-command app integration mode; it refreshes the current handoff, re-checks readiness, writes the stable app-snapshot plus app-snapshot-status outputs, and prints the ready gate as deterministic JSON without compact lines.
- Use `check-current-manual-delivery-app-ready --stdout-json` as the read-side check after `refresh-current-manual-delivery-app`; it reads `app-snapshot-status.json` and prints the ready gate as deterministic JSON without compact lines.
- Use `describe-current-manual-delivery-app-contract --stdout-json` as the app integration contract introspection command; it prints the stable contract for the current app path as deterministic JSON.
- Use `write-current-manual-delivery-app-dashboard` as the local app/operator visual surface; it renders the current validated snapshot/status as static HTML with no JS or network.
- Add `--write-app-dashboard` to `refresh-current-manual-delivery-app` when you want that same refresh to also write `app-dashboard.html` alongside the snapshot/status outputs.
- Use `export-current-manual-delivery-app-surface` as the recommended local app/operator surface export; it writes `index.html`, `app-dashboard.html`, `app-ready.json`, `app-contract.json`, `app-snapshot.json`, and `app-snapshot-status.json` under `local/manual_delivery_app_surface`.
- Use `describe-current-manual-delivery-app-contract --stdout-json` when you want the current app integration contract to include the local app surface bundle paths and commands for app integration.
- Add `--export-app-surface --app-surface-dir <path>` to `refresh-current-manual-delivery-app` when you want that same refresh to also write the bundle in one run.
- Use `refresh-current-manual-delivery-app-state` as the recommended one-command app-facing refresh; it writes self-check, app-state, and app-state-status outputs in one run.
- Use `check-current-manual-delivery-app-state-ready --stdout-json` as the smallest final app/operator readiness check after refresh; it validates `app-state-status.json` and prints the minimal ready gate as deterministic JSON.
- Use `refresh-and-check-current-manual-delivery-app-state` as the app-facing readiness builder; it refreshes the current handoff and writes the ready-check outputs in one run.
- Use `refresh-current-manual-delivery-app-snapshot` as the recommended final app/operator one-command path; it refreshes the current handoff, re-checks readiness, and writes the stable app-snapshot pair in one run.
- Add `--write-app-snapshot-status` when you want that same one-command refresh to also validate and write `app-snapshot-status.md` and `app-snapshot-status.json`.
- Use `write-current-manual-delivery-app-snapshot` as the single small stable app/operator read file after refresh-and-check or refresh-and-snapshot; it combines the ready-check and app-state into one snapshot pair.
- Use `summarize-current-manual-delivery-app-snapshot --stdout-json` as the app/operator read-side validator for `app-snapshot.json`; it prints deterministic JSON only.
- It does not send, notify, fetch, rebuild, trade, or approve anything.

### Source Freshness Guard

- Use `--source-stale-after-hours <hours>` with the one-command local manual delivery flow when you want local file freshness checked before manual use.
- It uses local file mtimes only.
- It marks missing or stale sources as `source_readiness=review_required_missing_or_stale_source`.
- It does not fetch, rebuild, send, notify, trade, or approve anything.
- Keep the same safety boundary: report-only, not FORMAL_GO, no automatic order, ACTIVE_* guidance only, human must decide manually, no external notification integration.

### Actionability Shadow Ledger Opt-in

- The default `write-latest-manual-delivery-local-flow --output-dir <path>` command remains unchanged when no additional Actionability shadow flag is supplied.
- Add `--write-actionability-shadow-decision` when you want the same local-flow command to append one evaluation-only Actionability shadow ledger row from the generated `manual-delivery-input.json`.
- The default output path is `logs/csv/active_plan_shadow_decisions.csv`.
- Optional flags are `--actionability-shadow-output-csv <path>`, `--actionability-shadow-final-outcome <value>`, `--actionability-shadow-notes <text>`, and `--actionability-shadow-summary-output-md <path>`.
- Use `--actionability-shadow-summary-output-md <path>` together with `--write-actionability-shadow-decision` when you want the same run to append the shadow row and write a local Markdown summary of the resulting shadow CSV.
- When the shadow row is written, `inbox.md` records the shadow CSV path and safety-only review link; when the summary is also written, `inbox.md` records the summary path too.
- Example:
  `./.venv312/bin/python tools/log_feedback.py write-latest-manual-delivery-local-flow --output-dir local/manual_delivery --write-actionability-shadow-decision --actionability-shadow-final-outcome pending --actionability-shadow-summary-output-md local/manual_delivery/actionability-shadow-summary.md`
- Keep the same boundary: report-only, not FORMAL_GO, no automatic order, no paper_positions.csv integration, and no send/notify/fetch/rebuild/trade/approve behavior.
- Generated CSV output must not be committed unless explicitly approved.

## Actionability Shadow Decision Summary

- Use `summarize-actionability-shadow-decisions --input-csv <path>` to review a shadow ledger CSV without recomputing actionability.
- Add `--output-md <path>` when you want the same Markdown written to a file and a compact `actionability_shadow_summary_output_md=<path>` line on stdout.
- The summary includes the title, safety boundary, total row count, and counts by `actionability_label`, `human_action`, `active_plan_label`, `final_outcome`, and `source_readiness`.
- Missing or blank values are rendered deterministically as `UNKNOWN`.
- The command reads only the shadow ledger CSV schema and does not touch `paper_positions.csv`.

## Actionability shadow operator review protocol

- Use the already documented tmpdir/local-flow path to generate or locate the Actionability shadow CSV.
- Run `summarize-actionability-shadow-decisions --input-csv <path>` on that shadow CSV.
- Review the counts by `actionability_label`, `human_action`, `active_plan_label`, `final_outcome`, and `source_readiness`.
- Treat `ACTIVE_*` as operator guidance only, not FORMAL_GO.
- Record human observations only in `notes` and `final_outcome` in the shadow/evaluation artifact, not in `paper_positions.csv`.
- Stop review if `source_readiness` is stale/missing or if the summary implies any automatic order/action.
- Safety boundary: `report-only, not FORMAL_GO, no automatic order, human decides manually`.

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
- The Actionability shadow ledger is evaluation-only and must remain separate from `paper_positions.csv`.
- This workflow does not send email, Gmail, webhook, Slack, LINE, Discord, cron, launchd, clipboard, or any external notification.
- This workflow does not run daily-sync, report hub generation, runtime, deploy, trading, API keys, private endpoints, or `paper_positions.csv` changes.
