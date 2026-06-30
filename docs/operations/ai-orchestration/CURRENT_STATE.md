# CURRENT_STATE

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- no API keys
- no private/account/order endpoints
- human decides manually

## Current focus

- MCP-primary orchestration baseline is established
- this repo is now the current source of truth
- runtime pull handoff is not needed unless user explicitly reopens it
- app/product work has resumed
- dashboard parity is complete
- checkpoint push was reported successful
- current product-quality phase is evidence / intraperiod / win-rate diagnostics
- automatic trading remains out of scope

## Current known status

- public HTML / notification mail / local dashboard は同じ判断ソースを維持する方針
- intraperiod review, operator status, safe config schema audit, operator triage summary, integrated evidence overview は既存 docs 上で accepted milestone として扱われている
- 診断は report-only の post-hoc support に留め、major turn 確定や自動売買許可には使わない

## Current operational blocker

- MCP working repo と old runtime execution repo の 2 つが存在し、混同すると unsafe

## Current repo-operation mode

- MCP repo is source of truth
- ChatGPT verifies via AFROG_MCP_Business
- GitHub is not routine review path
- Codex prompts should be compact and diff-based inside same thread
- commit only at meaningful boundaries
- TASK_LEDGER / handoff docs are not updated every task

## Procedure note

- checkpoint push procedure is now documented
- runtime pull handoff is closed unless explicitly reopened
- no routine push remains the default

## Minimal record policy

- source/runtime/generated/logs/private/order boundaries stay explicit
- response.txt は最小限の compact report にする
- 大きな節目以外での逐次メモはしない

## Default avoid list

- `.venv312/`
- `logs/`
- generated CSV / report / HTML
- full `TASK_LEDGER.md`
