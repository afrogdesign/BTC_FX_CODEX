# AI Orchestration Control

last_updated: 2026-06-09
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v2`
current_commit: `e57b101`
note: `current_commit` is the latest ChatGPT-reviewed baseline and may intentionally lag the latest commit by one task.
project_key: `BTCFX`

---

## 1. Current objective

BTCFX-20260608-055A updates the thread handoff in `CURRENT_HANDOFF.md` before builder work resumes.

BTCFX-20260608-054 is complete, and its fix commit is `82be32b Document iMac SMB working directory policy`.

BTCFX-20260608-054-FIX is complete, and its fix commit is `46f7bfb Add Codex response outbox rule`.

BTCFX-20260608-053 is complete, and its fix commit is `cd0e07f Fix active plan intraperiod edge cases`.

The next builder task after this policy update is BTCFX-20260608-055.

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

### 2.1 Machine roles and paths

- Codex edits from MBAM4 using the SMB-mounted iMac repository path.
- MBAM4 working directory: `/Volumes/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- iMac repository path: `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- These two paths point to the same repository data via SMB.
- The iMac is canonical for the repository body, runtime, deployment, logs, and execution.
- Default tests and execution should run on the iMac via `ssh marupro@192.168.50.51`.
- Do not use `imac` or `imac.afrog.jp` as SSH targets.
- Pure unit tests may run on MBAM4 only when they are independent of runtime state, deployment paths, logs, APIs, or iMac-only files.
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
| BTCFX-20260608-055A | done | Update CURRENT_HANDOFF.md for ChatGPT/Codex thread handoff before builder work | Ver03-v2 | `e57b101` | Handoff refresh before builder task |

---

## 7. Next recommended task

```text
NEXT BTCFX-20260608-055
Goal: Implement the builder for `active_plan_candidate_intraperiod_outcomes.csv`.
Read: docs/specs/active-plan-intraperiod-outcomes.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Edit: src/trade/active_plan_intraperiod.py, tests/test_active_plan_candidate_intraperiod_outcomes.py, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Test: `git diff --check`
Stop: if source code changes are needed beyond the builder and its tests
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
