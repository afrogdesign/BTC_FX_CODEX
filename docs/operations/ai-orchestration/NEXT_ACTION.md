# NEXT_ACTION

- current_work_id: `M-DELIVERY1`
- mode: `BOUNDED_CODEX`
- branch: `Ver04-v4`
- accepted_checkpoint: `475ae4d`
- active_spec: `chatgpt/specs/active/20260722_macro_structure_public_mail_delivery.md`
- canonical_plan: `docs/operations/strategy/MACRO_VISUAL_STRUCTURE_PRODUCT_PLAN_20260722.md`
- status: implementation complete; pending ChatGPT acceptance
- push: none

## Current action

Review the fixed public-URL delivery path for already-approved notification emails.

```text
local/reports/macro_structure/operator/latest.html
→ validate M-ENTRY1 available/unavailable state
→ publish unchanged bytes through existing SSH + rsync host
→ atomic remote rename to macro-structure/latest.html
→ append one fixed HTTPS link and health state to the existing email body
```

## Fixed public endpoint

```text
https://server.afrog.jp/btc-monitor/notifications/macro-structure/latest.html
```

It is derived from:

```text
<NOTIFICATION_HTML_PUBLIC_BASE_URL>/macro-structure/latest.html
```

## Fixed implementation boundaries

- reuse existing `NOTIFICATION_HTML_*` transport configuration
- enable only when `NOTIFICATION_HTML_ENABLED=true`
- use default source `local/reports/macro_structure/operator/latest.html`
- allow source override only through `MACRO_STRUCTURE_FIXED_ENTRY_PATH`
- validate regular non-symlink UTF-8 M-ENTRY1 HTML before any remote command
- distinguish available and unavailable fixed-entry states
- publish to a remote temporary file, then atomically rename to `latest.html`
- do not rewrite the source HTML
- append one plain-text macro URL block immediately before existing `send_email`
- keep the existing detail-page URL block
- keep existing `should_notify`, notification kind, subject, suppression, and resend behavior
- publication failure must not suppress an email already approved by existing logic
- no URL is claimed when remote final rename fails

## Required result states

```text
published
 disabled
source_unavailable
failed
```

Use only stable error codes. Do not expose local paths, remote paths, SSH host/key, stdout, stderr, exception text, or secrets.

## User-visible acceptance

Available:

```text
【4H大局チャート（公開URL）】
https://server.afrog.jp/btc-monitor/notifications/macro-structure/latest.html
状態: available / cutoff JST=... / stale=... / continuity=... / data_quality=...
固定URLの存在は鮮度を保証しません。時刻と状態を確認してください。
```

Unavailable:

```text
【4H大局チャート（公開URL）】
https://server.afrog.jp/btc-monitor/notifications/macro-structure/latest.html
状態: unavailable
今回の完全な最新画面は公開されていません。リンク先の利用不可表示を確認してください。
```

Failure or disabled:

- do not append a public URL
- append at most one compact stable-code status line
- continue the existing approved email send

## Validation budget

- focused publisher tests
- focused `run_cycle` mail-body integration tests
- existing notification detail tests
- one no-network/no-send deterministic smoke with mocked subprocess and captured email body
- task-scoped `git diff --check`

Do not run:

- real email send
- real SSH or rsync
- full test suite
- full replay
- network fetch
- runtime service or LaunchAgent
- background processes
- repeated health checks

## Explicit exclusions

- no notification threshold, cadence, subject, or duplicate-suppression changes
- no analytical model changes
- no M-ENTRY1 identity changes
- no private/account/order endpoint
- no automatic order
- no frozen runtime access without an explicit `RUNTIME_TASK`

## Transition

After implementation, ChatGPT reviews changed source, matching tests, command construction, email body, result metadata, scope, and safety. Acceptance completes M-DELIVERY1 in the primary repo. Installed runtime activation remains a separate explicit `RUNTIME_TASK` boundary.
