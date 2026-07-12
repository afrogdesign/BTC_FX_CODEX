# NEXT_ACTION

- current_work_id: `BTCFX-20260712-P8-TURNING-PRECURSOR-SHADOW-RUNTIME-ENABLE`
- mode: `RUNTIME_TASK`
- task_type: `P8 REPORT-ONLY SHADOW RUNTIME ENABLE`
- human_approval: explicit approval received on 2026-07-12

## Current state

The opt-in daily turning precursor shadow integration is implemented at commit `f39375f` and bounded validation passed.

Current runtime posture:

- launchd label: `com.afrog.btc-p8-operating-cycle`
- schedule: daily 11:30 JST
- installed shadow flag: not yet enabled
- notification/mail behavior: unchanged
- P9: blocked
- recommendation: `continue_shadow_collection`

## Current exact next action

Apply the approved runtime specification:

```text
chatgpt/specs/active/20260712_turning_precursor_shadow_runtime_enable.md
```

The only intended runtime change is adding:

```text
--include-turning-precursor-shadow
```

to `com.afrog.btc-p8-operating-cycle` ProgramArguments.

Repository plist, focused test, commit, push, one installed-plist backup, bootout/bootstrap of this label only, and loaded-contract verification are included in one bounded runtime task.

Do not manually start a P8 cycle during the apply task. The first normal 11:30 JST scheduled cycle is the runtime acceptance event.

## After runtime apply

HUMAN_CHECK after the first normal scheduled cycle:

- core P8 status success
- turning precursor shadow status success
- date-scoped shadow outputs present
- no second OHLCV fetch
- no mail or notification change

## Prohibited

- no scoring, market-map, threshold, gate, notification, mail, UI, or order change
- no normal monitor restart
- no other LaunchAgent change
- no frozen old runtime repo access
- no private/account/order endpoint
- no automatic order

## Safety

report-only / not FORMAL_GO / no automatic order / human decides manually
