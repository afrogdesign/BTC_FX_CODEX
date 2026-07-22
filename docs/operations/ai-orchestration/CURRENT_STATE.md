# CURRENT_STATE

last_updated: 2026-07-22

## Current posture

- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- branch: `Ver04-v4`
- latest accepted source checkpoint: `9409551`
- push: none
- safety: report-only / human-decided / no automatic order
- canonical visual plan: `docs/operations/strategy/MACRO_VISUAL_STRUCTURE_PRODUCT_PLAN_20260722.md`

## Accepted source modules

- M-VIS1 source accepted
- M-LINE1 source accepted
- M-EVENT1 source accepted
- M-HYP1 source accepted
- M-ENTRY1 source accepted at `475ae4d`
- M-DELIVERY1 primary-repo source accepted at `9409551`

## Runtime re-audit result

The 2026-07-22 end-to-end audit found that source acceptance did not yet produce an operationally complete delivery chain.

### Blocking gap: scheduled operator lacks explicit 4H input

`tools/run_macro_structure_service.py` fetches and stages 4H OHLCV but its operator command passes only `--ohlcv-15m-csv`.

Observed consequences:

- scheduled operator output does not contain the M-VIS1 4H model;
- scheduled output does not contain the M-LINE1, M-EVENT1, or M-HYP1 models;
- M-ENTRY1 does not publish the fixed `latest.html` during the scheduled cycle;
- `local/reports/macro_structure/operator/latest.html` is currently absent;
- the current health artifact can still report `healthy_insufficient`, so health does not prove fixed-entry delivery readiness.

### Blocking gap: installed notification runtime

- the accepted M-DELIVERY1 integration exists only in the primary repo;
- the active notification process remains in the frozen runtime repo;
- no real SSH, rsync, public HTTPS retrieval, or SMTP verification has completed;
- a relative fixed-entry path in the frozen repo would resolve to the wrong local report root.

Required installed source path:

```text
/Users/marupro/CODEX/100_MCP_Server/btc_monitor/local/reports/macro_structure/operator/latest.html
```

### Additional contract gap

The M-DELIVERY1 entry-ID extraction remains broad rather than state-scoped to the current available or unavailable section. This must be corrected before live activation.

## Corrective active specification

- `chatgpt/specs/active/20260722_macro_structure_runtime_delivery_completion.md`
- work ID: `BTCFX-20260722-VER04-V4-M-RUNTIME-DELIVERY-COMPLETION`
- mode: `RUNTIME_TASK`
- user authorization: explicit

## Product status

```text
M-VIS1 through M-DELIVERY1 source implementation — accepted
installed 4H generation — incomplete
fixed latest.html generation on schedule — incomplete
public URL live publication — incomplete
notification email live integration — incomplete
```

The M plan must not be described as operationally complete until the corrective runtime task satisfies its acceptance criteria.

## Current selected action

One bounded RUNTIME_TASK must:

1. pass the staged 4H CSV to the scheduled operator;
2. prove current fixed `latest.html` generation;
3. deploy the minimal M-DELIVERY1 integration to the frozen notification runtime;
4. configure the frozen runtime to read the primary fixed entry;
5. perform one real public publication and one controlled verification email;
6. preserve all safety, notification-decision, subject, recipient, threshold, and schedule boundaries.
