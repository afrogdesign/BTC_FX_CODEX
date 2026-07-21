# NEXT_ACTION

- current_work_id: `BTCFX-20260721-MACRO-STRUCTURE-RUNTIME-SERVICE-ENABLE-FIX-01`
- mode: `RUNTIME_TASK`
- branch: `Ver04-v3`; confirm from local git before execution
- accepted_source_base: `09330b9`
- implementation_commit: `690c014`
- current_head_locator: `80bcd59`
- active_spec: `chatgpt/specs/active/20260721_macro_structure_runtime_service_enable.md`
- status: blocked after one target-only repair, bootstrap, kickstart, and live acceptance attempt
- target_label: `com.afrog.btc-macro-structure`
- push: none

## Current action

Diagnose and repair the target-only `launchctl bootstrap` I/O failure without reopening the accepted wrapper, plist schedule, or M-OPS1–M-OPS3 semantics.

The initial activation attempt established:

- focused source and CLI tests passed;
- wrapper dry-run passed;
- repository plist lint passed;
- target did not previously exist;
- bootstrap returned an I/O error;
- kickstart was not performed;
- rollback removed the installed target plist;
- target remains unloaded;
- no live runtime status or new macro artifacts were produced.

## Required diagnosis before mutation

Collect target-specific evidence for:

1. GUI-domain registration and disabled state;
2. target plist ownership, mode, ACL, flags, and xattrs;
3. `~/Library/LaunchAgents` ownership and access;
4. primary Python, wrapper, working directory, and runtime log directory;
5. installed/repository plist byte identity and lint;
6. bounded launchd diagnostics mentioning the target label or plist.

## Repair boundary

Perform at most one evidence-based target repair and one subsequent bootstrap attempt.

Permitted target-only repairs:

- stale target bootout/removal;
- target plist ownership or mode correction;
- target-plist quarantine removal;
- required target log-directory creation;
- recopy of the committed repository plist.

Do not change the label, six-time schedule, source semantics, system timezone, another LaunchAgent, mail, notification, policy, private endpoints, or orders.

## Success path

If bootstrap succeeds:

1. verify loaded paths, schedule, logs, and no RunAtLoad/KeepAlive;
2. kickstart the target exactly once;
3. wait boundedly for one new runtime status;
4. verify successful M-OPS1 → M-OPS2 → M-OPS3 artifacts and safety flags;
5. archive the active spec;
6. mark M-OPS4 accepted and M-OPS5 next;
7. create one local state commit.

## Failure path

If no safe repair is established or repaired bootstrap/runtime acceptance fails:

- boot out only the target;
- remove the new installed plist because no prior target existed;
- leave the target unloaded;
- record exact diagnostic evidence and final state;
- do not repeat bootstrap or kickstart;
- keep M-OPS4 unaccepted.

## No-repeat and safety

- do not rerun implementation tests unless source changed;
- do not repeat an unchanged bootstrap;
- no other LaunchAgent mutation;
- no normal monitor or P8 restart;
- no frozen-repo edit or execution;
- report-only;
- no automatic order;
- no mail or notification integration;
- no private/account/position/order endpoint;
- no M5, M6, or version promotion.

## FIX-01 result

- target registration repair: bootstrap succeeded once after target-only recopy and normal ownership/mode correction;
- target runtime: one launchd-triggered run only;
- M-OPS1: success;
- M-OPS2: success;
- M-OPS3: failed closed with `zone_evidence_invalid`;
- rollback: target-only unload and removal of the new installed plist; target remains unloaded;
- concrete blocker: live M-OPS3 zone-evidence validation must be diagnosed in a separately authorized source-fix task;
- no second bootstrap, kickstart, live run, or unrelated LaunchAgent operation is authorized by this checkpoint.
