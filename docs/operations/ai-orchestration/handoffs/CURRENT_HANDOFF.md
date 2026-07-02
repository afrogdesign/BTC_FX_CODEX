# Current Handoff

last_updated: 2026-07-02
repo: afrogdesign/BTC_FX_CODEX
branch: Ver04-v1
canonical_working_dir: /Users/marupro/CODEX/100_MCP_Server/btc_monitor
active_handoff: none

## Current operational posture

- Ver04-v1 runtime deployment complete / reflected active
- post-deployment observation
- notification sending behavior unchanged
- no immediate implementation unless observation finds an issue or user explicitly requests implementation

## Product backlog next candidate

- BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER

## Safety boundary

- report-only
- not FORMAL_GO
- no automatic order
- no API keys/secrets
- no private/account/order endpoints
- no runtime restart unless explicitly approved
- no notification sending behavior change unless explicitly approved
- no raw exchange export commit
- no paper_positions.csv integration unless explicitly approved
- human decides manually

## Source of truth

- START_HERE.md
- CURRENT_STATE.md
- NEXT_ACTION.md
- CONTROL.md
- PRODUCT_IMPLEMENTATION_ROUTE.md
- MILESTONES.md

## Historical handoff archive

- HISTORICAL_VER03_V4_HANDOFF_20260624.md

## Rule

CURRENT_HANDOFF.md is read only for explicit handoff, migration, blocked, partial, or context-overload situations.
It is not a default startup read.
