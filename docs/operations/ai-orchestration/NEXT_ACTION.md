# NEXT_ACTION

- current_work_id: `BTCFX-20260722-VER04-V4-M-STATS1-RUNTIME-SHADOW`
- mode: `RUNTIME_TASK`
- primary branch: `Ver04-v4`
- accepted runtime source locator: `bc61478`
- accepted M-STATS1 FIX1 report locator: `68ed430`
- active spec: `chatgpt/specs/active/20260722_macro_structure_scenario_stats_runtime_shadow.md`
- status: human-approved deployment pending implementation and one bounded runtime verification
- push: none

## Scope

- add accepted M-STATS1 as a non-blocking local shadow auxiliary after successful macro operator generation
- default output: `local/reports/macro_structure/scenario_stats`
- persist privacy-safe stats generation status in the macro runtime result
- preserve existing snapshot/history/operator and health behavior
- do not connect stats to notification, mail, public publication, operator latest page, gates, thresholds, scores, classifiers, or order behavior
- do not edit or reload the existing plist or schedule

After one local implementation commit, verify the loaded primary-repo target and perform exactly one target-only kickstart without `-k`. Do not retry a failed kickstart or perform another live verification action.
