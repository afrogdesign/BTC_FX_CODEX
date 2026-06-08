# AI Task Ledger

| Work ID | Date | Status | Summary | Changed files | Validation | Commit | Push |
|---|---:|---|---|---|---|---|---|
| BTCFX-20260608-047 | 2026-06-08 | done | Started Ver03-v2 branch | `運用資料/計画/Ver03-v2_開始メモ_20260608.md`, `運用資料/NEXT_TASK.md`, `運用資料/作業ログ/BTCFX-20260608-047_branch_ver03_v2.md` | `git diff --check` pass | `6ec1da1` | yes |
| BTCFX-20260608-048 | 2026-06-08 | done | Add AI orchestration anchor files | `AGENTS.md`, `docs/operations/ai-orchestration/**`, `運用資料/NEXT_TASK.md` | `git diff --check` pass | `b904e13` | yes |
| BTCFX-20260608-049 | 2026-06-08 | done | Sync AI orchestration state | `docs/operations/ai-orchestration/CONTROL.md`, `docs/operations/ai-orchestration/TASK_LEDGER.md`, `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md`, `運用資料/作業ログ/BTCFX-20260608-047_branch_ver03_v2.md` | `git diff --check` pass | `943fe55` | yes |
| BTCFX-20260608-050 | 2026-06-08 | done | Simplified NEXT_TASK.md to human-facing entry | `運用資料/NEXT_TASK.md`, `docs/operations/ai-orchestration/CONTROL.md`, `docs/operations/ai-orchestration/TASK_LEDGER.md`, `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md` | `git diff --check` pass | `90bfe9f` | yes |
| BTCFX-20260608-051 | 2026-06-08 | done | Recorded first Ver03-v2 implementation decision | `docs/operations/ai-orchestration/CONTROL.md`, `docs/operations/ai-orchestration/TASK_LEDGER.md`, `docs/operations/ai-orchestration/DECISIONS.md` | `git diff --check` pass | `29d3745` | yes |
| BTCFX-20260608-052 | 2026-06-09 | done | Draft Active Plan intraperiod outcome specification | `docs/specs/active-plan-intraperiod-outcomes.md`, `docs/operations/ai-orchestration/CONTROL.md`, `docs/operations/ai-orchestration/TASK_LEDGER.md` | `git diff --check` pass | `4303d5b` | yes |
| BTCFX-20260608-053 | 2026-06-09 | done | Implemented active plan intraperiod evaluator helper and fixed edge cases | `src/trade/active_plan_intraperiod.py`, `tests/test_active_plan_intraperiod.py`, `docs/operations/ai-orchestration/CONTROL.md`, `docs/operations/ai-orchestration/TASK_LEDGER.md` | `git diff --check` pass | `cd0e07f` | yes |
| BTCFX-20260608-054 | 2026-06-09 | done | Documented MBAM4 SMB working-directory and execution policy | `AGENTS.md`, `docs/operations/ai-orchestration/CONTROL.md`, `docs/operations/ai-orchestration/TASK_LEDGER.md`, `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md` | `git diff --check` pass | `82be32b` | yes |
| BTCFX-20260608-054-FIX | 2026-06-09 | done | Completed MBAM4/iMac policy metadata and added mandatory Codex response output rule | `AGENTS.md`, `docs/operations/ai-orchestration/CONTROL.md`, `docs/operations/ai-orchestration/PROMPTS.md`, `docs/operations/ai-orchestration/TASK_LEDGER.md`, `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md` | `git diff --check` pass | `46f7bfb` | yes |
| BTCFX-20260608-055A | 2026-06-09 | done | Updated CURRENT_HANDOFF.md for ChatGPT/Codex thread handoff before builder work | `docs/operations/ai-orchestration/CONTROL.md`, `docs/operations/ai-orchestration/TASK_LEDGER.md`, `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md` | `git diff --check` pass | `6bc8ac8` | yes |
| BTCFX-20260608-055B | 2026-06-09 | done | Documented SMB file access and iMac SSH git workflow | `AGENTS.md`, `docs/operations/ai-orchestration/CONTROL.md`, `docs/operations/ai-orchestration/TASK_LEDGER.md`, `docs/operations/ai-orchestration/PROMPTS.md`, `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md` | `git diff --check` pass | `4ea589f` | yes |
| BTCFX-20260608-055 | 2026-06-09 | done | Implemented Active Plan intraperiod outcome row builder and thin CSV writer | `src/trade/active_plan_intraperiod.py`, `tests/test_active_plan_candidate_intraperiod_outcomes.py`, `docs/operations/ai-orchestration/CONTROL.md`, `docs/operations/ai-orchestration/TASK_LEDGER.md` | `./.venv312/bin/python -m unittest tests/test_active_plan_intraperiod.py tests/test_active_plan_candidate_intraperiod_outcomes.py` pass; `git diff --check` pass | `8eecd4e` | yes |
| BTCFX-20260609-056 | 2026-06-09 | done | Replaced the split MBAM4/SMB workflow with an iMac-only local repo workflow | `AGENTS.md`, `docs/operations/ai-orchestration/CONTROL.md`, `docs/operations/ai-orchestration/TASK_LEDGER.md`, `docs/operations/ai-orchestration/PROMPTS.md`, `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md` | `git status --short --branch` pass; `git diff --check` pass | `447b0c6` | yes |
| BTCFX-20260608-057 | 2026-06-09 | done | Wired Active Plan intraperiod outcome builder into the `tools/log_feedback.py` CLI | `tools/log_feedback.py`, `tests/test_log_feedback.py`, `docs/operations/ai-orchestration/CONTROL.md`, `docs/operations/ai-orchestration/TASK_LEDGER.md` | `./.venv312/bin/python -m unittest tests/test_active_plan_intraperiod.py tests/test_active_plan_candidate_intraperiod_outcomes.py tests/test_log_feedback.py` pass; `git diff --check` pass | `pending` | yes |

## Status definitions

| Status | Meaning |
|---|---|
| planned | Planned by ChatGPT |
| in_progress | Codex is working |
| done | Completed and pushed |
| partial | Partially completed |
| blocked | Waiting for decision |
| failed | Failed |
| superseded | Replaced by later work |
