# NEXT_ACTION

- current_work_id: `BTCFX-20260722-MACRO-STRUCTURE-HEALTH-RUNTIME-INTEGRATION`
- mode: `RUNTIME_TASK`
- branch: `Ver04-v3`; confirm from local git before execution
- implementation_base: `aec7587`
- active_spec: `chatgpt/specs/active/20260722_macro_structure_health_runtime_integration.md`
- installed_target: `com.afrog.btc-macro-structure`
- status: partial — core live cycle succeeded; health published `inconsistent`
- push: none

## Current action

Review the one bounded runtime result after the compatibility fix; M-OPS5 runtime integration is not accepted yet.

Required:

1. keep the existing M-OPS1 → M-OPS2 → M-OPS3 pipeline and six-time schedule unchanged;
2. atomically finalize the runtime status first;
3. invoke `check-macro-structure-health` once for every completed success or failure cycle;
4. publish health artifacts under `local/reports/macro_structure/health/`;
5. keep health generation separate from the canonical runtime `steps` list;
6. do not rewrite the runtime status after health generation;
7. preserve core exit semantics and safety boundaries;
8. do not repeat the consumed kickstart without explicit new runtime authorization.

Observed blocker:

- health artifact `health_c710b453824f8669ca86` returned `snapshot_latest_symbol_mismatch` because the accepted M-OPS1 latest pointer omitted `symbol`; immutable snapshot evidence contained `BTC_USDT`
- compatibility fix: `0dbe9d0`
- core runtime IDs: `run_e9aa2c2554a7e471d97b`, `history_c235747e652ec548ab5e`, `operator_c415a6b130916ffb851f`

Do not add a new LaunchAgent, schedule, fetch, mail, notification, private input, policy, or order path.
