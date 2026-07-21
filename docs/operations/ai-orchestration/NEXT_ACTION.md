# NEXT_ACTION

- current_work_id: `BTCFX-20260721-MACRO-STRUCTURE-RUNTIME-SERVICE-ENABLE-FIX-02`
- mode: `RUNTIME_TASK`
- branch: `Ver04-v3`; confirm from local git before execution
- current_head_locator: `a9b3d46` (state commit pending)
- runtime_implementation_commit: `690c014`
- archived_spec: `chatgpt/specs/archive/20260721_macro_structure_runtime_service_enable.md`
- status: M-OPS4 accepted; M-OPS5 is the next separate source task
- target_label: `com.afrog.btc-macro-structure`
- push: none

## Current action

Define the separate M-OPS5 autonomous health/status source task. Do not repeat the accepted M-OPS4 runtime review or live run without a documented reopening trigger.

## Established root cause

The launchd service, schedule, public fetch, M-OPS1, and M-OPS2 operated correctly.

The live M-OPS1 snapshot legitimately publishes optional unavailable references as empty dictionaries, including `next_upside_target`, `next_downside_target`, and `nearest_reliable_resistance` when structure is insufficient.

M-OPS3 currently rejects an empty dictionary as `zone_evidence_invalid` before recognizing it as an absent optional reference.

Required semantics:

- optional nearest/target/obstruction reference values `None`, blank, `none`, `insufficient`, and `{}` are absent and not rendered;
- a non-empty partial object remains malformed and fails closed;
- every displayed high/medium support/resistance zone remains strictly validated;
- no M-OPS1 reliability, lifecycle, role, or geometry semantics change.

## Runtime status correction

When a later pipeline step fails, preserve identifiers and statuses from earlier successful steps in `macro_structure_service_last_result.json`.

At minimum, an operator-step failure after successful snapshot/history must retain snapshot run ID, snapshot ID, history ID, snapshot result, history result, stale, continuity, and data-quality status.

## Validation and activation

After the focused source fix:

1. run matching M-OPS3 and runtime-wrapper tests;
2. run one deterministic fixture using M-OPS1-style empty optional references;
3. commit the source fix locally;
4. install the unchanged committed target plist;
5. bootstrap only `com.afrog.btc-macro-structure` once;
6. verify the existing six-time primary-repo contract;
7. kickstart exactly once;
8. verify one complete M-OPS1 → M-OPS2 → M-OPS3 success and matching artifacts;
9. on success archive the M-OPS4 spec and mark M-OPS4 accepted / M-OPS5 next;
10. on failure rollback only the target and do not repeat the live run.

## FIX-02 accepted result

- source fix: `a9b3d46`;
- runtime implementation: `690c014`;
- target: `com.afrog.btc-macro-structure`, primary repo, schedule `01:10`, `05:10`, `09:10`, `13:10`, `17:10`, `21:10` JST;
- one bootstrap and one kickstart succeeded;
- latest snapshot: `run_bc49b15e01e3c2d49d64` / `macro_snapshot_bc49b15e01e3c2d49d64`;
- latest history: `history_e0fa3fd0ebc25b781c5f`;
- latest operator: `operator_128b44f88c8a1e02b350`;
- result: snapshot `insufficient`, history `ok`, stale `current`, continuity `continuous`, data quality `ok`;
- safety: report-only, no private actual-trade input, no automatic order;
- M-OPS5 is next; do not repeat M-OPS4 review or runtime run without a documented reopening trigger.

## Safety

- report-only
- no automatic order
- no mail or notification integration
- no private/account/position/order endpoint
- no other LaunchAgent mutation
- no M5/M6
- no version promotion
- no push
