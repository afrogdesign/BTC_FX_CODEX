# CURRENT_STATE

last_updated: 2026-07-22

## Runtime delivery completion

- primary source commit: `bc61478` (`fix: complete macro runtime delivery chain`)
- frozen notification source commit: `3e75a2f` (`feat: activate macro public link in notifications`)
- primary branch: `Ver04-v4`; frozen branch: `Ver04-v2`
- macro LaunchAgent: existing `com.afrog.btc-macro-structure`, one authorized kickstart completed successfully
- existing JST schedule preserved: 01:10, 05:10, 09:10, 13:10, 17:10, 21:10
- current fixed entry ID: `59baf573aec7c90d3b3e`
- fixed entry status: `available`
- public publication: `published`
- public URL: `https://server.afrog.jp/btc-monitor/notifications/macro-structure/latest.html`
- bounded public HTTPS verification: HTTP 200 and current safety/freshness markers verified
- controlled SMTP verification: sent once successfully; recipient and SMTP values are not recorded
- frozen non-secret source path points to the primary fixed entry; `.env` is not committed
- safety: report-only / human-decided / no automatic order
- no private/account/position/order endpoint, threshold, recipient, cadence, or unrelated LaunchAgent change
- push: none

M-VIS1 through M-DELIVERY1 are operationally complete for the bounded runtime task. Future approved notifications retain the existing notification decision and one-send path while appending the fixed macro URL block.

Installed-runtime activation is recorded here only from the bounded verification above; no frozen-repo deployment beyond this M-DELIVERY1 scope was performed.
