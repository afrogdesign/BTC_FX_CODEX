# CURRENT_STATE

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- no API keys
- no private/account/order endpoints
- human decides manually

## Current focus

- まず MCP primary 前提の AI orchestration を軽く安全にする
- その後、evidence-based accuracy diagnostics に戻る

## Current known status

- public HTML / notification mail / local dashboard は同じ判断ソースを維持する方針
- intraperiod review, operator status, safe config schema audit, operator triage summary, integrated evidence overview は既存 docs 上で accepted milestone として扱われている
- 診断は report-only の post-hoc support に留め、major turn 確定や自動売買許可には使わない

## Current operational blocker

- MCP working repo と old runtime execution repo の 2 つが存在し、混同すると unsafe

## Current repo-operation mode

- MCP primary
- no routine GitHub push
- checkpoint push only
- runtime repo pull later

## Procedure note

- checkpoint push procedure is now documented
- runtime pull handoff is separate and explicit
- no routine push remains the default

## Default avoid list

- `.venv312/`
- `logs/`
- generated CSV / report / HTML
- full `TASK_LEDGER.md`
