# Macro Structure Runtime Delivery Completion

## Metadata

- work_id: `BTCFX-20260722-VER04-V4-M-RUNTIME-DELIVERY-COMPLETION`
- mode: `RUNTIME_TASK`
- status: audit-confirmed corrective work required
- primary_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- frozen_runtime_repo: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- accepted_primary_checkpoint: `9409551`
- safety: report-only / no automatic order / human decides manually

## Audit findings

Primary implementation tests passed, but the end-to-end installed path is not complete.

### Blocking finding 1: scheduled operator invocation omits 4H input

`tools/run_macro_structure_service.py::_build_commands()` fetches and stages 4H OHLCV but invokes `render-macro-structure-operator` with only `--ohlcv-15m-csv`.

Consequences:

- M-VIS1 4H-first rendering is not produced by the scheduled service;
- M-LINE1, M-EVENT1, and M-HYP1 are not produced by the scheduled service;
- M-ENTRY1 does not publish the fixed `latest.html`, because it is intentionally enabled only by an explicit valid 4H invocation;
- the existing operator `latest.json` can advance while the fixed entry remains absent.

Direct evidence on 2026-07-22:

- runtime staged a 4H fingerprint;
- operator command did not consume it;
- `local/reports/macro_structure/operator/latest.html` was absent;
- current operator `latest.json` had no 4H fingerprint/model fields.

### Blocking finding 2: health does not prove delivery readiness

The current health artifact can report `healthy` or `healthy_insufficient` while the fixed M-ENTRY1 `latest.html` is absent and the scheduled operator lacks 4H output.

For this task, runtime acceptance must explicitly verify fixed-entry readiness. Changing the accepted health-state algorithm is not required unless a small matching check is necessary; do not broaden M-OPS5 without evidence.

### Blocking finding 3: live notification process is not using M-DELIVERY1

M-DELIVERY1 is accepted only in the primary repo. The installed notification process still uses the frozen runtime repo and has not received the accepted publisher/config/main integration.

### Blocking finding 4: cross-repo source path

The macro LaunchAgent writes the fixed entry in the primary repo. A relative default in the frozen notification repo would resolve under the frozen repo and miss the real file.

The installed notification config must use this exact absolute non-secret path:

```text
/Users/marupro/CODEX/100_MCP_Server/btc_monitor/local/reports/macro_structure/operator/latest.html
```

### Blocking finding 5: no real delivery proof

No real SSH, rsync, public HTTPS retrieval, or SMTP verification has yet proved the installed path.

### Contract finding 6: entry-ID parsing is not state-scoped

The M-DELIVERY1 parser still uses one broad entry-ID regex over the whole HTML. The accepted FIX contract required state-specific extraction from the current available or unavailable fixed-entry section, with duplicate/ambiguous current IDs rejected.

### Repository-state finding 7

`CURRENT_STATE.md` and `NEXT_ACTION.md` were edited after commit `9409551`; the accepted checkpoint does not contain the final state transition. The current completion wording is also inaccurate until this task succeeds.

## Objective

Complete the installed chain:

```text
primary scheduled 15m/1h/4h inputs
→ operator receives explicit 15m and 4H CSVs
→ 4H-first operator + line/event/scenario models
→ atomic primary latest.html
→ frozen installed notification reads the exact primary latest.html
→ existing SSH + rsync public host
→ public macro-structure/latest.html
→ future approved notification emails append the fixed URL block
→ one controlled non-trading verification email proves SMTP delivery
```

## Primary-repo source correction

Update `tools/run_macro_structure_service.py` so the operator command contains both:

```text
--ohlcv-15m-csv <latest/ohlcv_15m.csv>
--ohlcv-4h-csv <latest/ohlcv_4h.csv>
```

Requirements:

- use the same staged 4H file already fetched for the cycle;
- do not fetch a second 4H dataset;
- preserve M-OPS1 → M-OPS2 → M-OPS3 order;
- preserve schedule, lock, health invocation, and report-only safety;
- capture from successful operator output when present:
  - `latest_entry_status`
  - `latest_entry_id`
  - `latest_entry_method_version`
- expose these as privacy-safe runtime status fields;
- do not expose absolute paths.

Add focused runtime tests proving:

- operator receives the same staged 4H file as M-OPS1;
- operator receives both explicit 15m and 4H arguments;
- no second fetch occurs;
- successful operator result preserves latest-entry fields;
- a fixture-backed operator invocation with valid 4H input produces `latest.html`.

## State-scoped M-DELIVERY1 parsing

In `src/notification/macro_structure_public_delivery.py`:

- isolate the current section first;
- available entry ID is extracted only from `id="fixed-latest-entry"`;
- unavailable entry ID is extracted only from `id="fixed-latest-entry-unavailable"`;
- exactly one non-empty current entry ID is required;
- duplicate or ambiguous current IDs fail with `macro_public_source_invalid`;
- historical artifact text outside the current section must not affect current metadata.

Keep the accepted available/unavailable markers, immutable staging, fixed URL, `mv -f`, disabled behavior, and stable errors unchanged.

## Transport argument hardening

Because SSH remote command arguments are interpreted by the remote shell, validate the configured host and remote root conservatively.

Required:

- host must not begin with `-` and must contain only a conservative user/host character set;
- remote root must remain absolute, have no `..`, and contain only safe path characters used by the accepted deployed path;
- build the rsync remote-shell string with safe quoting such as `shlex.join`;
- known accepted values must continue to pass;
- unsafe metacharacters fail with `macro_public_transport_config_invalid`;
- do not change the existing detail-page publisher in this task unless a shared helper is demonstrably required.

## Frozen-runtime deployment

This task is explicitly authorized to inspect, edit, test, and run the frozen runtime repo only for M-DELIVERY1 activation.

Before changes:

1. record branch, HEAD, and `git status --short --branch` for both repos;
2. identify the actual installed notification LaunchAgent/program path;
3. confirm whether it points to the frozen repo;
4. preserve unrelated dirty changes;
5. do not reset, restore, checkout, clean, or stash apply/pop/drop;
6. do not print `.env`, secrets, SMTP credentials, API keys, or recipient addresses.

Apply the minimal accepted M-DELIVERY1 changes to the frozen repo:

- `src/notification/macro_structure_public_delivery.py`
- minimal `main.py` integration
- minimal `config.py` support for `MACRO_STRUCTURE_FIXED_ENTRY_PATH`
- matching focused tests where practical

Do not copy unrelated primary code or overwrite the entire frozen `main.py` without a reviewed minimal diff.

Installed non-secret config:

- ensure `MACRO_STRUCTURE_FIXED_ENTRY_PATH` resolves exactly to the primary fixed-entry path above;
- ensure `NOTIFICATION_HTML_ENABLED` is true for the installed process, because the user explicitly authorized public URL mail delivery;
- edit only those keys without displaying or rewriting unrelated secret values;
- preserve `.env` permissions;
- never commit `.env`.

## Runtime activation and verification budget

### Primary macro service

- verify `com.afrog.btc-macro-structure` is loaded and points to the primary repo;
- no plist or schedule change is expected;
- kickstart this target exactly once after the primary fix is committed;
- wait a bounded period for one new runtime status;
- no unchanged retry.

Require:

- core runtime success;
- operator command consumed explicit 4H input;
- operator latest contains a 4H fingerprint/model;
- fixed `local/reports/macro_structure/operator/latest.html` exists as a regular non-symlink file;
- fixed entry is either truthful `available` or truthful `unavailable`;
- for acceptance, an `available` entry is required unless current public data causes a deterministic documented operator failure that cannot be safely corrected in scope.

### Public publication

Perform exactly one real publisher invocation using the installed frozen config and the primary fixed-entry source.

Require:

- result status `published`;
- fixed URL:
  `https://server.afrog.jp/btc-monitor/notifications/macro-structure/latest.html`;
- no raw SSH/rsync output in persisted or reported metadata;
- one bounded HTTPS GET may verify that the URL is reachable and contains the same current entry ID and required safety/freshness markers;
- do not repeatedly poll.

### Email verification

Send exactly one controlled verification email to the already configured `MAIL_TO` using the existing SMTP sender.

Subject:

```text
[BTCFX] 4H macro public URL runtime verification
```

Body:

- use the accepted `format_macro_structure_email_block()` output;
- add one line stating this is a runtime verification, not a trading signal;
- include `report-only / no automatic order / human decides manually`;
- do not include secrets, recipient address, local paths, remote paths, host, key, stdout, stderr, or exception text;
- do not fabricate a market notification;
- do not create a persistent new trigger or schedule.

The normal `run_cycle` integration must remain the mechanism for future approved notification emails.

## Acceptance criteria

This task is complete only when all are true:

1. primary runtime wrapper passes explicit 4H CSV to the operator;
2. focused primary tests pass;
3. primary service produces a current available fixed `latest.html` after one kickstart;
4. frozen notification runtime contains the minimal accepted M-DELIVERY1 integration;
5. frozen installed config points to the primary fixed entry;
6. normal notification suppression, subject, recipient, thresholds, and one-send behavior are unchanged;
7. one real public publication succeeds;
8. one bounded public retrieval confirms current entry ID and safety/freshness markers;
9. one controlled verification email is sent successfully;
10. no automatic order, private/account/order endpoint, or unrelated LaunchAgent change occurs;
11. primary and frozen task files are committed locally, excluding `.env` and generated artifacts;
12. state docs truthfully distinguish source commits, installed runtime activation, and live verification.

## Rollback

If frozen source validation, primary kickstart, public publication, or SMTP verification fails:

- do not repeat an unchanged live command;
- do not alter other LaunchAgents;
- preserve previous remote `latest.html` through atomic publication behavior;
- restore only task-touched frozen source/config from a target-specific backup or task commit when the new code is unsafe;
- do not erase diagnostics;
- report the exact blocker and whether future normal notification emails are using the new integration.

## Allowed primary files

- `tools/run_macro_structure_service.py`
- `tests/test_run_macro_structure_service.py`
- `src/notification/macro_structure_public_delivery.py`
- `tests/test_macro_structure_public_delivery.py`
- this active spec
- `docs/operations/ai-orchestration/CURRENT_STATE.md`
- `docs/operations/ai-orchestration/NEXT_ACTION.md`
- one concise runtime record under `docs/operations/runtime/`

## Allowed frozen files

- `src/notification/macro_structure_public_delivery.py`
- `main.py`
- `config.py`
- focused matching tests
- `.env` only for the two authorized non-secret keys, never committed

## Prohibited

- automatic orders;
- private/account/position/order endpoints;
- threshold, gate, score, classifier, or signal-policy changes;
- recipient changes;
- schedule changes;
- new LaunchAgent;
- a second macro kickstart;
- repeated SSH/rsync/SMTP/public-URL attempts without changed cause;
- full replay or parameter search;
- push;
- secret display or commit.

