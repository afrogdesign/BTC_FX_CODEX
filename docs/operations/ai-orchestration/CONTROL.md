# AI Orchestration Control

last_updated: 2026-06-09
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v2`
current_commit: `8f0b18c`
note: `current_commit` is the latest ChatGPT-reviewed baseline and may intentionally lag the latest pushed commit by one or more tasks.
project_key: `BTCFX`

---

## 1. Current objective

BTCFX-20260608-060 prepares a temporary Ver03-v2 execution/deploy entrypoint and BTCFX Ver03-v2 label audit.

BTCFX-20260608-060-FIX aligns the temporary Ver03-v2 report hub output path.

BTCFX-20260608-061 captured a temporary Ver03-v2 execution review with a report hub path failure.

BTCFX-20260608-058 adds Markdown report wiring for `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`.

BTCFX-20260608-057 wires the Active Plan intraperiod outcome builder into `tools/log_feedback.py`.

BTCFX-20260609-056 is complete, and its fix commit is `447b0c6 Replace split workflow with local iMac-only workflow`.

BTCFX-20260608-055 is complete, and its implementation commit is `8eecd4e Implement active plan intraperiod outcome builder`.

BTCFX-20260608-057 is complete, and its implementation commit is `1d23850 Wire active plan intraperiod outcome CLI`.

BTCFX-20260609-059 is complete, and its sync commit is `pending_review`.

BTCFX-20260608-058 is complete, and its implementation commit is `pending_review`.

BTCFX-20260608-060 is complete, and its implementation commit is `pending_review`.

BTCFX-20260608-055B is complete, and its fix commit is `4ea589f Document SMB file access and iMac SSH git workflow`.

BTCFX-20260608-055A is complete, and its fix commit is `6bc8ac8 Update CURRENT_HANDOFF.md for ChatGPT/Codex thread handoff before builder work`.

BTCFX-20260608-054-FIX is complete, and its fix commit is `46f7bfb Add Codex response outbox rule`.

BTCFX-20260608-053 is complete, and its fix commit is `cd0e07f Fix active plan intraperiod edge cases`.

The next recommended task after BTCFX-20260608-060 is review of the temporary Ver03-v2 execution output and the daily-sync decision.

The active deliverable is `docs/specs/active-plan-intraperiod-outcomes.md`.

---

## 2. Current constraints

- ChatGPT is commander, planner, and reviewer.
- Codex is implementation worker.
- Codex must not make design decisions.
- Codex must not perform broad repository exploration unless explicitly requested.
- Codex should read only files named in the task.
- Real order APIs, exchange API keys, secrets, and live trading are out of scope.
- Runtime monitor restart is out of scope unless explicitly requested.
- Implementation tasks must not write their own final commit hash into `CONTROL.md` or `TASK_LEDGER.md`.
- While an implementation task is active, `TASK_LEDGER.md` should use `pending_review` for `Commit` and may use `reported` for `Push` after push.
- ChatGPT reviews GitHub after Codex reports, then later `SYNC` tasks batch-update reviewed commit metadata.
- Do not create a per-task `FIX` only to replace `pending_review` with the same task's commit hash.
- `BTCFX Ver03-v2` is the temporary label convention for deploy/runtime-facing labels, report titles, and email subject prefixes on this branch.

### 2.1 Machine roles and paths

- Canonical working directory: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- All file reading and editing must use the local iMac repository path.
- All tests, git commands, commit, push, and deployment/runtime operations must run on this iMac local repository.
- Codex must not use `/Volumes/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`.
- Codex must not use `/Volumes/marupro/claudeCode/BTC_FX_CODEX/btc_monitor`.
- Do not use `imac` or `imac.afrog.jp` as SSH targets.
- Do not use `ssh marupro@192.168.50.51` for normal repo work unless a task explicitly requires confirming the current machine state.
- Do not run runtime processes unless explicitly instructed.
- For NEXT, FIX, SYNC, and HANDOFF tasks, the final compact report must also be written to `/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt` exactly as `response.txt`.

---

## 3. Product direction

The BTC trading system should become practical for real market use.

Current staged direction:

1. Email-based human trading support.
2. Active Plan action guidance.
3. Candidate logging and diagnostics.
4. Intraperiod TP / SL / entry validation.
5. Paper verification.
6. Safety systems.
7. Future automated trading only after explicit permission.

---

## 4. Important files

| Area | Files | Notes |
|---|---|---|
| Product plan | `運用資料/計画/README.md` | Planning entry |
| Integrated plan | `運用資料/計画/00_Ver03-v1_統合再計画_20260608.md` | Product direction |
| Roadmap | `運用資料/計画/02_Ver03-v1_実装ロードマップ_20260608.md` | Implementation order |
| AI file design | `運用資料/計画/03_AI参照ファイル設計_20260608.md` | Source for this anchor design |
| Human task entry | `運用資料/NEXT_TASK.md` | Human-facing pointer |
| AI control | `docs/operations/ai-orchestration/CONTROL.md` | Current AI operating context |
| Task ledger | `docs/operations/ai-orchestration/TASK_LEDGER.md` | Work ID ledger |

---

## 5. Validation commands

| Scope | Command | When |
|---|---|---|
| Docs only | `git diff --check` | Markdown / docs changes |
| Targeted Python tests | `./.venv312/bin/python -m unittest <tests>` | Python code change |
| CLI report | `./.venv312/bin/python tools/log_feedback.py <args>` | Report builder change |
| Status | `git status --short --branch` | Every task |

---

## 6. Active work

| Work ID | Status | Goal | Branch | Commit | Notes |
|---|---|---|---|---|---|
| BTCFX-20260608-047 | done | Start Ver03-v2 branch | Ver03-v2 | `6ec1da1` | Branch start |
| BTCFX-20260608-048 | done | Add AI orchestration anchor files | Ver03-v2 | `b904e13` | AI orchestration anchors added |
| BTCFX-20260608-049 | done | Sync AI orchestration state | Ver03-v2 | `943fe55` | AI orchestration state synced |
| BTCFX-20260608-050 | done | Simplify NEXT_TASK.md to human-facing entry | Ver03-v2 | `90bfe9f` | NEXT_TASK.md simplified |
| BTCFX-20260608-051 | done | Record first Ver03-v2 implementation decision | Ver03-v2 | `29d3745` | Active Plan intraperiod outcome specification selected |
| BTCFX-20260608-052 | done | Draft Active Plan intraperiod outcome specification | Ver03-v2 | `4303d5b` | Active Plan intraperiod outcome specification drafted |
| BTCFX-20260608-053 | done | Implement helper functions and fixture tests for the Active Plan intraperiod outcome evaluator | Ver03-v2 | `cd0e07f` | Helper evaluator and edge-case fixes completed |
| BTCFX-20260608-054 | done | Document MBAM4 SMB working-directory and execution policy | Ver03-v2 | `82be32b` | This policy update |
| BTCFX-20260608-054-FIX | done | Complete MBAM4/iMac policy metadata and add mandatory Codex response output rule | Ver03-v2 | `46f7bfb` | Metadata correction and response rule |
| BTCFX-20260608-055A | done | Update CURRENT_HANDOFF.md for ChatGPT/Codex thread handoff before builder work | Ver03-v2 | `6bc8ac8` | Handoff refresh before builder task |
| BTCFX-20260608-055B | done | Document SMB file access and iMac SSH git workflow | Ver03-v2 | `4ea589f` | SMB read/write only; git/tests/commit/push on iMac via SSH |
| BTCFX-20260608-055 | done | Implement builder for Active Plan intraperiod outcome rows and CSV output | Ver03-v2 | `8eecd4e` | Builder layer only; no CLI/report wiring |
| BTCFX-20260609-056 | done | Replace split MBAM4/SMB workflow with iMac-only local workflow | Ver03-v2 | `447b0c6` | Docs-only workflow sync before builder task |
| BTCFX-20260608-057 | done | Wire Active Plan intraperiod outcome builder into `tools/log_feedback.py` CLI | Ver03-v2 | `1d23850` | CLI wiring only; evaluator semantics unchanged |
| BTCFX-20260608-058 | done | Add Markdown report wiring for Active Plan intraperiod outcome CSV | Ver03-v2 | `pending_review` | Report wiring only; no builder changes |
| BTCFX-20260609-059 | done | Sync AI orchestration metadata rules | Ver03-v2 | `pending_review` | AI orchestration metadata rule sync |
| BTCFX-20260608-060 | done | Prepare temporary Ver03-v2 execution/deploy entrypoint and BTCFX Ver03-v2 label audit | Ver03-v2 | `pending_review` | Temporary diagnostic entrypoint and label audit |
| BTCFX-20260608-060-FIX | done | Align temporary Ver03-v2 report hub output path | Ver03-v2 | `pending_review` | Report hub output path alignment |
| BTCFX-20260608-061 | partial | Capture temporary Ver03-v2 execution review facts | Ver03-v2 | `pending_review` | Execution failed during report hub step; facts captured |

---

## 7. Next recommended task

```text
NEXT BTCFX-20260608-062
Goal: Review BTCFX Ver03-v2 temporary execution results and decide the next integration boundary.
Read: docs/operations/deploy/Ver03-v2_EXECUTION_REVIEW_20260609.md, docs/operations/deploy/Ver03-v2_TEMP_EXECUTION.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Edit: docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md, and only explicitly scoped decision docs
Test: `git diff --check`
Stop: if runtime restart, live trading, API keys, automatic order execution, or daily-sync code changes are required
Report: compact
```

---

## 8. Do not do

- Do not modify trading logic during AI orchestration bootstrap.
- Do not restart runtime monitor.
- Do not run `main.py`.
- Do not run `run_cycle`.
- Do not access secrets or API keys.
- Do not create live trading functionality.

---

## 9. Open questions

| ID    | Question                                                                             | Owner           | Status |
| ----- | ------------------------------------------------------------------------------------ | --------------- | ------ |
| Q-001 | When should runtime monitor move from Ver03-v1/old state to Ver03-v2?                | human / ChatGPT | open   |
| Q-002 | Should NEXT_TASK.md be reduced to a human-facing pointer only?                       | human / ChatGPT | open   |
| Q-003 | Which task starts intraperiod validation implementation after AI anchors are stable? | ChatGPT         | open   |
