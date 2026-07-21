# NEXT_ACTION

- current_work_id: `BTCFX-20260722-MACRO-STRUCTURE-HEALTH-RUNTIME-INTEGRATION`
- mode: `RUNTIME_TASK`
- branch: `Ver04-v3`; confirm from local git before execution
- implementation_base: `dac7e8f`
- active_spec: `chatgpt/specs/active/20260722_macro_structure_health_runtime_integration.md`
- installed_target: `com.afrog.btc-macro-structure`
- status: human approved
- push: none

## Current action

Connect completed M-OPS5 health generation to the existing M-OPS4 wrapper.

Required:

1. keep the existing M-OPS1 → M-OPS2 → M-OPS3 pipeline and six-time schedule unchanged;
2. atomically finalize the runtime status first;
3. invoke `check-macro-structure-health` once for every completed success or failure cycle;
4. publish health artifacts under `local/reports/macro_structure/health/`;
5. keep health generation separate from the canonical runtime `steps` list;
6. do not rewrite the runtime status after health generation;
7. preserve core exit semantics and safety boundaries;
8. perform one focused implementation commit and one bounded launchd-triggered acceptance run.

Do not add a new LaunchAgent, schedule, fetch, mail, notification, private input, policy, or order path.
