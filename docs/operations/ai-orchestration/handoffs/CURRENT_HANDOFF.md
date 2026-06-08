# Current Handoff

last_updated: 2026-06-09
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v2`
current_commit: `e57b101`

## Objective

BTCFX-20260608-055A updates the ChatGPT/Codex thread handoff before builder work resumes.

This handoff now records the MBAM4 SMB working-directory and execution policy before the next builder task starts.
The mandatory Codex response rule is that the final compact report must also be written to `/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt` as `response.txt`.

## Current state

- Ver03-v1 was fixed at `e3506e4 Rebuild Ver03-v1 planning folder`.
- Ver03-v2 was started at `6ec1da1 Start Ver03-v2 branch`.
- Product planning folder was rebuilt.
- AI orchestration anchor files are in place.
- `BTCFX-20260608-053` is complete at `cd0e07f Fix active plan intraperiod edge cases`.
- `BTCFX-20260608-054` is the policy task that documents the MBAM4 SMB working-directory and execution policy.
- `BTCFX-20260608-055A` is the handoff task that refreshes this thread before the builder task starts.
- `NEXT_TASK.md` remains the human-facing entry.

## Machine roles and paths

- Codex edits from MBAM4 using the SMB-mounted iMac repository path.
- MBAM4 working directory: `/Volumes/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- iMac repository path: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- These two paths point to the same repository data via SMB.
- The iMac is canonical for the repository body, runtime, deployment, logs, and execution.
- Default tests and execution should run on the iMac via `ssh marupro@192.168.50.51`.
- Do not use `imac` or `imac.afrog.jp` as SSH targets.
- Pure unit tests may run on MBAM4 only when they are independent of runtime state, deployment paths, logs, APIs, or iMac-only files.
- Do not run runtime processes unless explicitly instructed.
- For NEXT, FIX, SYNC, and HANDOFF tasks, write the final compact report to `/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt` exactly as `response.txt`.

## Important constraints

- No live trading.
- No exchange API keys.
- No secrets.
- No runtime restart unless explicitly requested.
- Codex must not make product design decisions.
- Codex reports should be compact.

## Recent work

| Work ID | Status | Commit | Summary |
|---|---|---|---|
| BTCFX-20260608-046 | done | `e3506e4` | Rebuilt Ver03-v1 planning folder |
| BTCFX-20260608-047 | done | `6ec1da1` | Started Ver03-v2 branch |
| BTCFX-20260608-048 | done | `b904e13` | Add AI orchestration anchors |
| BTCFX-20260608-049 | done | `943fe55` | Sync AI orchestration state |
| BTCFX-20260608-053 | done | `cd0e07f` | Implemented active plan intraperiod evaluator helper and fixed edge cases |
| BTCFX-20260608-054 | done | `82be32b` | Documented MBAM4 SMB working-directory and execution policy |
| BTCFX-20260608-054-FIX | done | `46f7bfb` | Completed policy metadata and added the response output rule |
| BTCFX-20260608-055A | done | `e57b101` | Updated the thread handoff before builder work |

## Next prompt for Codex

```text
NEXT BTCFX-20260608-055
Goal: Implement the builder for `active_plan_candidate_intraperiod_outcomes.csv`.
Read: docs/specs/active-plan-intraperiod-outcomes.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Edit: src/trade/active_plan_intraperiod.py, tests/test_active_plan_candidate_intraperiod_outcomes.py, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Test: git diff --check
Stop: if source code changes are needed
Report: compact
```
