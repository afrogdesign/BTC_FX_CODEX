# M-STATS1 Runtime Shadow Deployment

## Metadata

- work_id: `BTCFX-20260722-VER04-V4-M-STATS1-RUNTIME-SHADOW`
- mode: `RUNTIME_TASK`
- approved_by: human explicit deployment approval on 2026-07-22
- primary_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- expected_branch: `Ver04-v4`
- accepted core runtime source locator: `bc61478`
- accepted M-STATS1 FIX1 report locator: `68ed430`
- runtime-shadow report locator: `c4d9a4a`
- target label: `com.afrog.btc-macro-structure`
- safety: report-only / human decides manually / no automatic order

## Goal

Enable accepted M-STATS1 as an automatically executed, local-only shadow auxiliary of the existing macro service.

```text
snapshot -> history -> operator
                     -> local scenario outcome stats shadow
                     -> existing health generation
```

M-STATS1 must not be added to the notification monitor, operator latest page, public publication, email, fixed public URL, gates, thresholds, scores, classifiers, or order behavior.

## Runtime contract

1. Keep the accepted core pipeline order unchanged: snapshot, history, operator.
2. Run scenario outcome stats only after all three core steps succeed.
3. Use the accepted CLI:
   `tools/build_macro_structure_scenario_outcome_stats.py`.
4. Default input:
   `local/reports/macro_structure/operator`.
5. Default output:
   `local/reports/macro_structure/scenario_stats`.
6. The stats auxiliary is non-blocking:
   - its failure must not change a successful core service result or exit code;
   - it must not suppress existing health generation;
   - it must preserve its prior complete artifact and latest pointer through the accepted fail-closed publisher.
7. Persist one privacy-safe `scenario_stats_generation` object in the atomic runtime status:
   - `attempted`
   - `status`: `published`, `failed`, or `not_run`
   - `artifact_id` when published
   - `evidence_strength` when published
   - `mature_row_count` when published
   - `source_artifact_count` and `excluded_artifact_count` when published
   - stable `error_code` when failed or not run
8. Do not include stdout, stderr, exception text, absolute paths, raw artifacts, market payloads, or secrets in runtime status.
9. If the core pipeline fails, stats is `not_run` with a stable reason.
10. Dry-run shows the stats command and output root but performs no fetch, subprocess, artifact, or status write.
11. Existing health behavior and core status semantics remain unchanged.
12. No plist or schedule edit is required. The loaded target already points to the primary repo wrapper.

## Repository files

Allowed edits:

- `tools/run_macro_structure_service.py`
- `tests/test_run_macro_structure_service.py`
- `tools/build_macro_structure_scenario_outcome_stats.py` only if a compact success/failure contract adjustment is necessary
- `tests/test_macro_structure_scenario_outcome_stats.py` only for that CLI adjustment
- this active spec only for a factual implementation note

Do not edit scenario generation, structural-event generation, operator rendering, notification, mail, publication, plist, schedule, gates, thresholds, scores, or classifiers.

## Validation

Run once:

- `.venv312/bin/python -m unittest tests.test_run_macro_structure_service tests.test_macro_structure_scenario_outcome_stats`
- `.venv312/bin/python tools/run_macro_structure_service.py --dry-run`
- one small deterministic stats fixture smoke
- task-scoped `git diff --check`

No full suite, broad replay, mail, notification, SSH, rsync, HTTP, frozen-repo command, or duplicate runtime run.

## Runtime apply

After a local task commit:

1. Verify the loaded target exists in `gui/$(id -u)` and still uses the primary repo Python, wrapper, and WorkingDirectory.
2. Do not bootout, bootstrap, reload, recopy, or modify the installed plist.
3. If the target is currently running or does not match the primary contract, stop without kickstart.
4. Record the pre-kickstart runtime status identity or timestamp.
5. Kickstart `com.afrog.btc-macro-structure` exactly once, without `-k`.
6. Perform one bounded verification of the new runtime result and local M-STATS1 artifact.
7. Verify:
   - core status remains success;
   - snapshot/history/operator still succeed;
   - `scenario_stats_generation.status` is `published`;
   - output evidence is allowed to remain `insufficient`;
   - existing health generation still executes;
   - no notification, email, public publication, or unrelated LaunchAgent action occurred.
8. Do not retry kickstart if execution or verification fails. Report the exact bounded result.

## Acceptance

Accepted on 2026-07-22 after direct AFROG_Business_MCP review.

- runtime status finished at `2026-07-22T08:21:57.814589+00:00`
- core status: `success`
- snapshot/history/operator steps: success
- operator artifact: `operator_9db15ecade825fb21568`
- stats status: `published`
- stats artifact: `ef3dc500f1368a83912e`
- stats evidence: `insufficient`
- mature rows: `0`
- valid source artifacts: `4`
- excluded legacy/incompatible artifacts: `8`
- immutable JSON/CSV/Markdown/manifest and byte-identical `latest.json` were directly verified
- health generation published `health_5330bd8fad66b16a07d6` with state `healthy`
- report-only, private-input false, and automatic-order false were preserved
- no notification, mail, public-publication, plist, schedule, or unrelated LaunchAgent change was found in the reviewed implementation route
- exactly one bounded runtime activation was reported; no repeat live verification is authorized
- commit object access remains unavailable through the safe public workspace; `c4d9a4a` is retained as a report locator
