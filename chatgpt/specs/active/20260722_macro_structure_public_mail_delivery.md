# M-DELIVERY1: Macro Structure Public URL Mail Delivery

- workstream: `M-DELIVERY1`
- schema_version: `macro_structure_public_delivery.v1`
- method_version: `macro_structure_public_delivery.v1`
- status: fixed by ChatGPT; implementation pending
- branch: `Ver04-v4`
- accepted predecessor: M-ENTRY1 at `475ae4d`

## 1. Purpose

Publish the accepted M-ENTRY1 fixed HTML entry through the existing notification HTML host and append its public URL to notification email bodies that the existing system has already decided to send.

User flow:

```text
accepted local M-ENTRY1 latest.html
→ validate fixed-entry status and safety
→ atomically publish to the existing public host
→ append one stable public URL block to an already-approved notification email
→ recipient opens the 4H-first macro screen
→ recipient checks 15m and decides manually
```

This remains report-only. It does not create an order, trading permission, or a new notification trigger.

## 2. Existing infrastructure to reuse

Reuse the existing notification HTML configuration and transport:

- `NOTIFICATION_HTML_ENABLED`
- `NOTIFICATION_HTML_PUBLIC_BASE_URL`
- `NOTIFICATION_HTML_REMOTE_SSH_HOST`
- `NOTIFICATION_HTML_REMOTE_SSH_KEY`
- `NOTIFICATION_HTML_REMOTE_DIR`
- SSH with `IdentitiesOnly=yes`, `BatchMode=yes`, and bounded timeout
- rsync over SSH
- the existing `run_cycle` email-send path and `should_notify` decision

Do not add a hosting provider, web framework, daemon, API, credential, or secret.

## 3. Fixed local and public locations

Local source default:

```text
local/reports/macro_structure/operator/latest.html
```

Config key:

```text
MACRO_STRUCTURE_FIXED_ENTRY_PATH
```

The default is the relative path above. Relative paths resolve under `base_dir`. Absolute paths are allowed only when explicitly configured, but the source must still be a regular non-symlink file.

Stable public URL:

```text
<NOTIFICATION_HTML_PUBLIC_BASE_URL>/macro-structure/latest.html
```

With the accepted default:

```text
https://server.afrog.jp/btc-monitor/notifications/macro-structure/latest.html
```

Stable remote path:

```text
<NOTIFICATION_HTML_REMOTE_DIR>/macro-structure/latest.html
```

The public URL is fixed. Do not create a new URL per notification.

## 4. Enablement

M-DELIVERY1 is enabled only when:

```text
NOTIFICATION_HTML_ENABLED == true
```

No second production enable flag is required. This task has explicit user authorization.

When notification HTML is disabled:

- do not run SSH or rsync;
- do not modify the email body;
- return `macro_structure_public_status=disabled`;
- preserve all existing notification behavior.

## 5. Source validation

The source must be read before any remote command.

Required filesystem properties:

- exists;
- regular file;
- not a symlink;
- UTF-8;
- non-empty;
- maximum 5 MiB.

The document must be exactly one recognized M-ENTRY1 state.

### Available source

Must contain:

- `id="fixed-latest-entry"`
- `entry_status</b>: available`
- `macro_structure_latest_entry.v1`
- `source operator artifact ID`
- `source digest`
- `source cutoff UTC`
- `source cutoff JST`
- `source stale status`
- `source continuity status`
- `source data-quality status`
- `fixed entry availability does not imply current market freshness; verify cutoff and status`
- `id="chart-4h"`
- `id="structural-events"`
- `id="scenario-hypotheses"`
- `id="chart"`
- `report-only`
- `no automatic order`
- `human decides manually`

It must not contain `id="fixed-latest-entry-unavailable"`.

### Unavailable source

Must contain:

- `id="fixed-latest-entry-unavailable"`
- `Macro Structure Latest Entry Unavailable`
- `entry_status=unavailable`
- `macro_structure_latest_entry.v1`
- `no complete current entry was published for this attempt`
- `report-only`
- `no automatic order`
- `human decides manually`

It must not contain `id="fixed-latest-entry"` as an available section.

### Reject

Reject when both states or neither state is present.

Reject source text containing secret-value labels or unsafe transport material, including:

- `OPENAI_API_KEY`
- `SMTP_PASSWORD`
- PEM private-key markers
- `Authorization: Bearer`

Do not reject the accepted safety phrase `no automatic order`.

## 6. Normalized delivery model

The source validator returns a bounded model:

```json
{
  "schema_version": "macro_structure_public_delivery.v1",
  "method_version": "macro_structure_public_delivery.v1",
  "entry_status": "available | unavailable",
  "entry_id": "string",
  "source_sha256": "64 lowercase hex",
  "source_size_bytes": 0,
  "source_artifact_id": "string or empty",
  "source_digest": "string or empty",
  "cutoff_utc": "string or empty",
  "cutoff_jst": "string or empty",
  "stale_status": "string or empty",
  "continuity_status": "string or empty",
  "data_quality_status": "string or empty",
  "public_url": "https URL",
  "safety_boundary": "report-only / no automatic order / human decides manually"
}
```

For an unavailable entry, fields unavailable in the page remain empty. Do not infer them from an older operator pointer.

Parse only the fixed M-ENTRY1 labels. Escape or normalize values before including them in an email body. No raw HTML is inserted into email text.

## 7. Public URL and path safety

- `NOTIFICATION_HTML_PUBLIC_BASE_URL` must be an absolute `https://` URL.
- Strip one trailing slash before adding `/macro-structure/latest.html`.
- Reject credentials, fragments, queries, control characters, and protocol-relative forms.
- Remote host, key, and directory must be non-empty.
- Reject newlines and NUL in transport configuration.
- Remote directory must be absolute and must not contain `..` path components.
- Never expose the SSH host, key path, or remote filesystem path in the email body or returned public metadata.

Stable error codes:

- `macro_public_disabled`
- `macro_public_source_missing`
- `macro_public_source_unsafe`
- `macro_public_source_too_large`
- `macro_public_source_invalid_utf8`
- `macro_public_source_invalid`
- `macro_public_url_invalid`
- `macro_public_transport_config_invalid`
- `macro_public_publish_failed`

Do not use raw OS, SSH, or rsync stderr as an error code.

## 8. Atomic remote publication

Use no shell interpolation.

Required sequence:

1. Validate and read the complete local source bytes.
2. Compute SHA-256.
3. Create the remote directory:

```text
<remote_root>/macro-structure
```

4. rsync the local source to a deterministic temporary remote basename:

```text
.latest.<source_sha256 first 20>.tmp
```

5. On the remote host, atomically rename the temporary file to:

```text
latest.html
```

6. Return success only after the final rename succeeds.

Use argument arrays, `check=True`, text capture, and bounded timeout. Reuse the accepted SSH options from notification detail publication.

On failure:

- return `macro_public_publish_failed`;
- do not claim the public URL was updated;
- best-effort cleanup of the remote temporary file is allowed but must not hide the original stable failure;
- do not delete or truncate the previous remote `latest.html`;
- do not block the already-approved notification email from being sent.

The source bytes must be uploaded unchanged. Do not inject email-specific content into the public page.

## 9. Duplicate suppression

M-DELIVERY1 must not create any notification or resend trigger.

The existing `should_notify` result remains the sole decision for whether a new notification email is sent. Public publication runs only inside a cycle whose existing logic is already preparing an email.

Do not change:

- notification cadence;
- notification-kind selection;
- suppression reason codes;
- pending-email resend rules;
- subject generation;
- main/attention/followup thresholds.

The fixed public URL itself prevents per-email URL proliferation.

## 10. Email-body integration

Attempt macro public publication before the existing `send_email` call.

The existing detail-page block remains unchanged and may coexist with the macro block.

### Available publication success

Append exactly one plain-text block:

```text

【4H大局チャート（公開URL）】
<public_url>
状態: available / cutoff JST=<cutoff_jst> / stale=<stale_status> / continuity=<continuity_status> / data_quality=<data_quality_status>
固定URLの存在は鮮度を保証しません。時刻と状態を確認してください。
```

Empty status values display as `unknown`. The public URL must be the validated fixed HTTPS URL.

### Unavailable publication success

Append exactly one plain-text block:

```text

【4H大局チャート（公開URL）】
<public_url>
状態: unavailable
今回の完全な最新画面は公開されていません。リンク先の利用不可表示を確認してください。
```

Do not describe a historical success as current.

### Disabled, missing, invalid, or publication failure

Do not append a public URL.

Append at most one compact status line:

```text

【4H大局チャート】利用不可（<stable_error_code>）
```

This line is informational only. It does not change whether the existing email is sent.

### Body safety

- append at most once;
- no HTML tags;
- no SSH/config/local paths;
- no secrets;
- no raw subprocess output;
- no buy/sell, long/short recommendation added by this module;
- preserve report-only and human-decision meaning.

## 11. Result fields

Add bounded fields to the cycle result:

```text
macro_structure_public_method_version
macro_structure_public_status
macro_structure_public_url
macro_structure_public_entry_status
macro_structure_public_entry_id
macro_structure_public_source_sha256
macro_structure_public_error_code
```

Allowed statuses:

- `published`
- `disabled`
- `source_unavailable`
- `failed`

Rules:

- `published` means remote final rename succeeded, for either available or unavailable entry.
- URL is populated only for `published`.
- `entry_status` is `available` or `unavailable` only after valid source parsing.
- error code is empty on `published` and `disabled`.
- do not include local path, remote path, SSH host, SSH key, stdout, stderr, or exception text.

## 12. Failure boundaries

- Macro public publication failure must not suppress an email that existing logic had approved.
- Macro public publication success must not force an email that existing logic suppressed.
- Detail-page publication failure and macro publication failure are independent.
- Pending-email behavior remains unchanged.
- No automatic order.
- No private/account/order endpoint.
- No new market fetch.

## 13. Expected implementation shape

Preferred new module:

```text
src/notification/macro_structure_public_delivery.py
```

Responsibilities:

- resolve source path;
- validate M-ENTRY1 source;
- validate public/remote configuration;
- build normalized delivery model;
- run atomic remote publication through an injectable command runner;
- format the bounded email block;
- return stable metadata.

Integrate in `main.py` immediately before email body finalization and `send_email`.

Add the config default only:

```text
MACRO_STRUCTURE_FIXED_ENTRY_PATH=local/reports/macro_structure/operator/latest.html
```

Do not add credentials or host values.

## 14. Tests

Required focused tests:

1. Default source path resolves under `base_dir`.
2. Regular non-symlink available M-ENTRY1 source validates.
3. Unavailable M-ENTRY1 source validates.
4. Both/neither state fails closed.
5. Missing, symlink, oversized, invalid UTF-8, and secret-bearing source fail closed.
6. Available metadata is parsed and normalized.
7. Unavailable metadata does not borrow old-success values.
8. Public URL is exactly `<base>/macro-structure/latest.html`.
9. Non-HTTPS or unsafe URL fails closed.
10. Unsafe remote configuration fails closed.
11. Command sequence is mkdir → rsync temp → atomic remote rename.
12. No command uses `shell=True`.
13. Uploaded source bytes are unchanged.
14. rsync or rename failure returns only `macro_public_publish_failed`.
15. Failure does not claim a URL was published.
16. Available email block contains URL, cutoff, health states, and freshness warning once.
17. Unavailable email block is explicitly unavailable and contains no current-success claim.
18. Failure/disabled block contains no URL.
19. Existing detail-page URL block remains.
20. `run_cycle` appends the macro URL before calling `send_email` when publication succeeds.
21. `run_cycle` still sends the email when macro publication fails.
22. `run_cycle` does not call macro publication when existing notification logic suppresses sending.
23. Main, attention, and followup paths share the same fixed URL behavior.
24. Existing notification subjects, notify decisions, and send count remain unchanged.
25. Result fields contain no secret, local path, remote path, host, key, stdout, or stderr.
26. Existing notification detail tests continue passing.

No test may send email, contact SSH, rsync a real host, or access the network.

## 15. Bounded smoke

Use the current local M-ENTRY1 review source or a deterministic fixture. Inject a fake command runner and capture `send_email`.

Prove:

- source validates;
- public URL is the accepted server URL;
- three publication commands are built in the correct order;
- email body contains exactly one macro public URL block;
- no real network or email occurs;
- safety wording remains;
- no local/remote/secret material appears.

## 16. Scope exclusions

Do not change:

- M-VIS1, M-LINE1, M-EVENT1, M-HYP1, or M-ENTRY1 analytical behavior;
- operator artifact identity or digest;
- market-data fetches;
- notification decision thresholds or duplicate suppression;
- email subject logic;
- automatic-order behavior;
- exchange private/account/order endpoints;
- LaunchAgent or schedule;
- the frozen runtime repo without a separately explicit `RUNTIME_TASK`.

## 17. Acceptance

M-DELIVERY1 code acceptance requires:

- a valid M-ENTRY1 page is atomically published to the fixed existing HTTPS location;
- the notification email contains the fixed public URL and health state;
- unavailable state is not represented as a current successful screen;
- publication failure does not suppress an otherwise-approved email;
- no new notification trigger or duplicate email is introduced;
- no secret or infrastructure path is exposed;
- focused tests and one no-network/no-send smoke pass;
- report-only / no automatic order / human decides manually remain.

Primary-repo acceptance does not by itself authorize touching or deploying the frozen runtime repo. Runtime installation requires a separately explicit `RUNTIME_TASK`.