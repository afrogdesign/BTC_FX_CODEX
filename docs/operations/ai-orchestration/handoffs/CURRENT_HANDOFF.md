# Current Handoff

last_updated: 2026-06-09
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v2`
current_commit: `447b0c6`

## Objective

BTCFX-20260609-056 completes the workflow sync to an iMac-only local repository workflow.

This handoff now records that all repo work runs directly on the local iMac path before the next builder task starts.
The mandatory Codex response rule is that the final compact report must also be written to `/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt` as `response.txt`.

## Current state

- Ver03-v1 was fixed at `e3506e4 Rebuild Ver03-v1 planning folder`.
- Ver03-v2 was started at `6ec1da1 Start Ver03-v2 branch`.
- Product planning folder was rebuilt.
- AI orchestration anchor files are in place.
- `BTCFX-20260608-053` is complete at `cd0e07f Fix active plan intraperiod edge cases`.
- `BTCFX-20260608-054` is the policy task that documents the MBAM4 SMB working-directory and execution policy.
- `BTCFX-20260608-055A` is the handoff task that refreshes this thread before the builder task starts.
- `BTCFX-20260608-055B` is the policy task that documents SMB file access and iMac SSH git workflow.
- `BTCFX-20260609-056` is the sync task that replaces those split-workflow rules with a local iMac-only workflow.
- `NEXT_TASK.md` remains the human-facing entry.

## Machine roles and paths

- Canonical working directory: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- All file reading and editing must use the local iMac repository path.
- All tests, git commands, commit, push, and deployment/runtime operations must run on this iMac local repository.
- Do not use `/Volumes/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`.
- Do not use `/Volumes/marupro/claudeCode/BTC_FX_CODEX/btc_monitor`.
- Do not use `imac` or `imac.afrog.jp` as SSH targets.
- Do not use `ssh marupro@192.168.50.51` for normal repo work unless a task explicitly requires confirming the current machine state.
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
| BTCFX-20260608-055A | done | `6bc8ac8` | Updated the thread handoff before builder work |
| BTCFX-20260608-055B | done | `4ea589f` | Documented SMB file access and iMac SSH git workflow |
| BTCFX-20260609-056 | done | `447b0c6` | Replaced split MBAM4/SMB rules with local iMac-only workflow |

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
