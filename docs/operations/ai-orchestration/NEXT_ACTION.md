# NEXT_ACTION

- current_work_id: `BTCFX-20260722-VER04-V4-M-RUNTIME-DELIVERY-COMPLETION`
- mode: `RUNTIME_TASK`
- branch: `Ver04-v4`
- accepted_source_checkpoint: `9409551`
- active_spec: `chatgpt/specs/active/20260722_macro_structure_runtime_delivery_completion.md`
- status: end-to-end audit found blocking runtime gaps; corrective task authorized
- push: none

## Required correction

### Primary scheduled macro service

The operator step must receive both staged files:

```text
--ohlcv-15m-csv local/runtime/macro_structure_inputs/latest/ohlcv_15m.csv
--ohlcv-4h-csv local/runtime/macro_structure_inputs/latest/ohlcv_4h.csv
```

Current evidence shows the 4H file is fetched but not passed to the operator. Therefore the scheduled service currently omits the 4H-first chart, trendlines/channels, structural events, scenarios, and fixed M-ENTRY1 `latest.html`.

### Installed notification runtime

The frozen runtime repo must receive the minimal accepted M-DELIVERY1 integration and use this exact non-secret source path:

```text
/Users/marupro/CODEX/100_MCP_Server/btc_monitor/local/reports/macro_structure/operator/latest.html
```

A relative path under the frozen repo is incorrect because the macro LaunchAgent writes reports in the primary repo.

### Live proof

Complete exactly one bounded sequence:

1. focused primary source/tests;
2. primary commit;
3. one existing macro LaunchAgent kickstart;
4. verify current available fixed `latest.html`;
5. minimal frozen source/config installation;
6. focused frozen no-send tests;
7. one real SSH/rsync publication;
8. one bounded public HTTPS verification;
9. one controlled non-trading SMTP verification email;
10. final primary/frozen local commits and factual runtime record.

## Additional required hardening

- state-scope current entry-ID extraction to the available/unavailable fixed-entry section;
- reject duplicate or ambiguous current entry IDs;
- conservatively validate SSH host and remote path arguments;
- preserve immutable validated-byte staging, atomic remote `mv -f`, disabled behavior, stable errors, and existing email decision logic.

## Safety boundaries

- no automatic order;
- no private/account/position/order endpoint;
- no threshold, gate, score, classifier, subject, recipient, or cadence change;
- no new LaunchAgent or schedule;
- no repeated unchanged live command;
- no secret display or commit;
- no push.

## Acceptance

Operational completion requires all of:

- scheduled 4H operator output;
- scheduled available fixed `latest.html`;
- frozen notification runtime reads the primary fixed entry;
- fixed public URL is reachable with the current entry ID;
- one controlled verification email is delivered;
- future approved notification emails retain one-send and suppression behavior.
