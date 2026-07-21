# NEXT_ACTION

- current_work_id: `BTCFX-20260721-MACRO-STRUCTURE-RUNTIME-SERVICE-ENABLE`
- mode: `RUNTIME_TASK`
- branch: `Ver04-v3`; confirm from local git before execution
- accepted_base: `09330b9`
- active_spec: `chatgpt/specs/active/20260721_macro_structure_runtime_service_enable.md`
- status: explicitly approved for implementation and installed service activation
- target_label: `com.afrog.btc-macro-structure`
- push: none

## Current action

Implement and activate M-OPS4 as one bounded report-only LaunchAgent.

The user explicitly authorized installed runtime/schedule inspection and change on 2026-07-21.

Connect accepted operations in this order:

```text
public 15m / 1h / 4h OHLCV
→ run-macro-structure-daily
→ run-macro-structure-history
→ render-macro-structure-operator
```

## Accepted source state

- M-OPS1 accepted at `89bd338`
- M-OPS2 accepted at `dea0e33`
- M-OPS3 accepted at `09330b9`

Do not reopen their analysis, reliability, history, chart, or publication semantics without a concrete command-breaking contradiction.

## Runtime target

New target only:

- label: `com.afrog.btc-macro-structure`
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- wrapper: `tools/run_macro_structure_service.py`
- repository plist: `deploy/com.afrog.btc-macro-structure.plist`
- installed plist: `~/Library/LaunchAgents/com.afrog.btc-macro-structure.plist`
- compact status: `logs/runtime/macro_structure_service_last_result.json`

Schedule in JST:

- 01:10
- 05:10
- 09:10
- 13:10
- 17:10
- 21:10

No RunAtLoad or KeepAlive.

## Execution boundary

This approved task may:

1. inspect installed matching LaunchAgents and the frozen repo read-only;
2. implement the dedicated public-data runtime wrapper;
3. add the target-only repository plist and focused tests;
4. commit the implementation locally;
5. back up only an existing target plist;
6. boot out/bootstrap/kickstart only the target label;
7. perform one bounded launchd-triggered live-public-data run;
8. verify fresh M-OPS1, M-OPS2, and M-OPS3 artifacts;
9. record rollback and runtime state.

Do not edit or run source/tests in the frozen runtime repo. The new service must point to the primary repo.

## Required safety

- report-only
- no automatic order
- no private/account/position/order endpoint
- no mail or notification integration
- no production gate, threshold, scoring, classifier, or policy change
- no existing monitor, P8, review-form, feedback, or AI-post-review service change
- no M5/M6
- no version promotion

## Acceptance path

After Codex reports completion, ChatGPT reviews:

- wrapper source;
- focused tests;
- plist contract;
- installed target contract;
- target-only backup/rollback evidence;
- launchd result status;
- latest snapshot/history/operator artifacts;
- scope and safety.

If accepted:

```text
M-OPS4 accepted
→ define M-OPS5 autonomous health/stale-status source task
```

## No-repeat boundary

Do not repeat M-OPS1–M-OPS3 implementation or acceptance review unless source changes or a contradictory artifact appears.

Do not repeatedly bootstrap or kickstart an unchanged failed target. Collect the exact target-specific cause, perform at most one bounded rollback, and report partial/blocked.
