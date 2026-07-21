# Ver02.6-v2 MBP2020 Frozen Runner Migration Record

## Purpose

MBP2020 is a frozen comparison runner for the final Ver02.6-v2 line.

It is a temporary substitute / baseline until Ver03 becomes fully operational.

It is separated from iMac Ver03 development.

It is not an auto-trading system.

It is not permitted to send live orders.

## Scope

- Source branch: `ver02.6-v2`
- Observed source reference commit: `fd783c1f390a31b9ecf5a06a7dd9f1c59fad0a73`
- Runner host: `AFROG-MBP2020.local`
- Runner IP: `192.168.1.38`
- Runner path: `/Users/marupro/CODEX/BTC_FX_CODEX_ver02_6_v2/btc_monitor`
- LaunchAgent label: `com.afrog.btc-monitor-ver021`
- Entrypoint: `main.py`
- Python path: `.venv312_prod/bin/python`
- Comparison role: legacy Ver02.6-v2 frozen baseline

## Local operational differences from upstream ver02.6-v2

Local email subject prefix patch:

- MBP2020 emails start with `💻`
- implemented locally in `src/notification/email_sender.py`
- idempotent prefix behavior
- does not change trading decision logic

Clean logs start:

- imported iMac-era `logs/` moved to:
  `logs_imported_from_imac_before_clean_start_20260609_141320`
- new active `logs/` created for MBP2020-only accumulation

HTML publish configuration:

- MBP2020 generates local HTML under `logs/notifications_html`
- MacPro publishes static HTML
- MacPro host: `192.168.1.39`
- MacPro web root: `/Volumes/AFROG_Storage/site_BOX`
- public base URL:
  `https://8f.afrog.jp/btc-monitor-mbp2020/notifications`

SSH:

- MBP2020 can publish via SSH key to MacPro
- key material is intentionally not recorded here

## Verified facts

- MBP2020 launchd runner was running
- API reachability confirmed:
  - Binance spot time: `200`
  - Binance futures time: `200`
  - MEXC ping: `200`
  - MEXC 15m kline: `200`
- `2026-06-09 14:05 JST` cycle succeeded before log cleanup:
  - heartbeat updated
  - last_result updated
  - CSV files updated
  - email sent
  - subject prefix `💻` confirmed in inbox
- HTML probe publish succeeded:
  - probe file:
    `mbp2020_publish_probe_20260609_142820.html`
  - published path:
    `/Volumes/AFROG_Storage/site_BOX/btc-monitor-mbp2020/notifications/ver02-6-v2/probe/mbp2020_publish_probe_20260609_142820.html`
  - verified URL:
    `https://8f.afrog.jp/btc-monitor-mbp2020/notifications/ver02-6-v2/probe/mbp2020_publish_probe_20260609_142820.html`
  - result: `200 OK`
- `server.afrog.jp` was not used because it points to a different public surface

## Later verification

After clean logs start, later verify the next `:05` cycle:

- new heartbeat
- new last_result
- new CSV outputs
- email subject still starts with `💻`
- email body contains the `8f.afrog.jp` HTML detail link
- published HTML opens
- no fatal traceback in `monitor.err`

This later check is intentionally not part of this documentation task.

## Operational boundaries

- Do not use this MBP2020 runner for Ver03-v2 development.
- Do not pull or mutate it as part of normal Ver03 work.
- Do not mix MBP2020 clean logs with iMac historical logs.
- Do not treat Active Plan or Ver02 outputs as automatic trading permission.
- No live order execution is allowed.

## Completion statement

The MBP2020 frozen Ver02.6-v2 runner migration is considered complete as of this record.

Remaining work is only later runtime observation, not migration setup.
