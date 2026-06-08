# AI Orchestration Control

last_updated: 2026-06-09
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v2`
current_commit: `d7c38073b75d1faa7868146288b5a69cf2c76356`
note: `current_commit` is the latest ChatGPT-reviewed baseline and may intentionally lag the latest pushed commit by one or more tasks.
project_key: `BTCFX`

---

## 1. Current objective

BTCFX-20260608-072 proves the Ver03-v2 Active Plan intraperiod verification path can escape `no_ohlcv` with a minimal local OHLCV sample.

BTCFX-20260608-070 prepares an exact-path cleanup/archive plan for BTCFX Ver03-v2 generated diagnostics without deleting files, but that archive step is deferred until the OHLCV sample/run task is complete.

BTCFX-20260608-069 defines the generated output lifecycle policy for BTCFX Ver03-v2 report-only diagnostics.

BTCFX-20260608-067 adds the daily-sync output review for BTCFX Ver03-v2 report-only diagnostics after subject label migration.

BTCFX-20260608-066 applies the approved BTCFX Ver03-v2 email subject prefix migration without runtime behavior changes.

BTCFX-20260608-064-FIX fixes stale daily-sync wording in the Ver03-v2 intraperiod diagnostics report.

BTCFX-20260608-060 prepares a temporary Ver03-v2 execution/deploy entrypoint and BTCFX Ver03-v2 label audit.

BTCFX-20260608-060-FIX aligns the temporary Ver03-v2 report hub output path.

BTCFX-20260608-061 captured a temporary Ver03-v2 execution review with a report hub path failure.

BTCFX-20260608-061-FIX fixes the temporary Ver03-v2 execution report hub path and reruns the diagnostic entrypoint.

BTCFX-20260608-062 is complete, and its decision-prep commit is `f150951 Prepare Ver03-v2 next boundary decision`.

BTCFX-20260608-063 is complete, and its implementation commit is `856e945 Add Ver03-v2 execution preflight checks`.

BTCFX-20260608-064 is complete, and its implementation commit is `fa86c67 Wire Ver03-v2 intraperiod diagnostics into daily sync`.

BTCFX-20260608-064-FIX is complete, and its fix commit is `d615247 Fix Ver03-v2 intraperiod daily sync wording`.

BTCFX-20260608-066 is complete, and its implementation commit is `497ffc8 Apply Ver03-v2 email subject prefix`.

BTCFX-20260608-065 is complete, and its audit commit is `0c6ff38 Audit Ver03-v2 email and report labels`.

BTCFX-20260608-058 adds Markdown report wiring for `logs/csv/active_plan_candidate_intraperiod_outcomes.csv`.

BTCFX-20260608-057 wires the Active Plan intraperiod outcome builder into `tools/log_feedback.py`.

BTCFX-20260609-056 is complete, and its fix commit is `447b0c6 Replace split workflow with local iMac-only workflow`.

BTCFX-20260608-055 is complete, and its implementation commit is `8eecd4e Implement active plan intraperiod outcome builder`.

BTCFX-20260608-057 is complete, and its implementation commit is `1d23850 Wire active plan intraperiod outcome CLI`.

BTCFX-20260609-059 is complete, and its sync commit is `1372f1e Sync AI orchestration metadata rules`.

BTCFX-20260608-058 is complete, and its implementation commit is `7f6d880 Add active plan intraperiod outcome report`.

BTCFX-20260608-060 is complete, and its implementation commit is `a7ea8d3 Prepare Ver03-v2 execution entrypoint`.

BTCFX-20260608-055B is complete, and its fix commit is `4ea589f Document SMB file access and iMac SSH git workflow`.

BTCFX-20260608-055A is complete, and its fix commit is `6bc8ac8 Update CURRENT_HANDOFF.md for ChatGPT/Codex thread handoff before builder work`.

BTCFX-20260608-054-FIX is complete, and its fix commit is `46f7bfb Add Codex response outbox rule`.

BTCFX-20260608-053 is complete, and its fix commit is `cd0e07f Fix active plan intraperiod edge cases`.

The next recommended task after BTCFX-20260608-072 is the safe local OHLCV supply or manual import workflow design task, not archive.

The active deliverable is `docs/operations/deploy/Ver03-v2_OHLCV_SAMPLE_RUN_20260609.md`.

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
| BTCFX-20260608-058 | done | Add Markdown report wiring for Active Plan intraperiod outcome CSV | Ver03-v2 | `7f6d880` | Report wiring only; no builder changes |
| BTCFX-20260609-059 | done | Sync AI orchestration metadata rules | Ver03-v2 | `1372f1e` | AI orchestration metadata rule sync |
| BTCFX-20260608-060 | done | Prepare temporary Ver03-v2 execution/deploy entrypoint and BTCFX Ver03-v2 label audit | Ver03-v2 | `a7ea8d3` | Temporary diagnostic entrypoint and label audit |
| BTCFX-20260608-060-FIX | done | Align temporary Ver03-v2 report hub output path | Ver03-v2 | `06f4bc5` | Report hub output path alignment |
| BTCFX-20260608-061 | partial | Capture temporary Ver03-v2 execution review facts | Ver03-v2 | `87890fa` | Execution failed during report hub step; facts captured |
| BTCFX-20260608-061-FIX | done | Fix temporary Ver03-v2 execution report hub path and rerun | Ver03-v2 | `3dc6cf4` | Temporary execution path fixed and rerun succeeded |
| BTCFX-20260608-062 | done | Prepare next boundary decision for Ver03-v2 temporary execution results | Ver03-v2 | `f150951` | Decision-prep document for next integration boundary |
| BTCFX-20260608-063 | done | Add preflight checks for Ver03-v2 manual diagnostic execution | Ver03-v2 | `856e945` | Preflight checks and warning summaries added |
| BTCFX-20260608-064 | done | Wire Ver03-v2 intraperiod report generation into daily-sync as report-only diagnostics | Ver03-v2 | `fa86c67` | Report-only daily-sync diagnostics wired |
| BTCFX-20260608-064-FIX | done | Fix stale daily-sync wording in Ver03-v2 intraperiod diagnostics report | Ver03-v2 | `d615247` | Report wording updated to report-only daily-sync diagnostics |
| BTCFX-20260608-065 | done | Audit BTCFX Ver03-v2 email and report label migration without runtime behavior changes | Ver03-v2 | `0c6ff38` | Label audit for future migration boundaries |
| BTCFX-20260608-066 | done | Apply BTCFX Ver03-v2 prefix to the approved email subject builder | Ver03-v2 | `497ffc8` | Email subject prefix migration only |
| BTCFX-20260608-067 | done | Add daily-sync output review for BTCFX Ver03-v2 report-only diagnostics after subject label migration | Ver03-v2 | `e4a9a65` | Daily-sync output review for report-only diagnostics |
| BTCFX-20260608-068 | done | Capture controlled daily-sync review facts with AI review creation disabled | Ver03-v2 | `pending_review` | Controlled daily-sync review facts captured with AI review creation disabled |
| BTCFX-20260608-069 | done | Define generated output lifecycle policy for Ver03-v2 report-only diagnostics | Ver03-v2 | `d7c3807` | Generated output lifecycle policy for report-only diagnostics |
| BTCFX-20260609-SYNC | done | Batch-sync reviewed pending_review metadata after accepted Ver03-v2 orchestration tasks | Ver03-v2 | `pending_review` | Reviewed metadata synced through BTCFX-20260608-069 |
| BTCFX-20260608-070 | done | Prepare exact-path cleanup/archive plan for Ver03-v2 generated diagnostics without deleting files | Ver03-v2 | `pending_review` | Exact-path cleanup/archive plan for generated diagnostics |
| BTCFX-20260608-071 | done | Lock a purpose-specific OHLCV input contract view for Ver03-v2 intraperiod verification | Ver03-v2 | `pending_review` | Safe contract view for local OHLCV input and preflight-only review |
| BTCFX-20260608-072 | done | Prove the Ver03-v2 Active Plan intraperiod verification path can escape `no_ohlcv` with a minimal local OHLCV sample | Ver03-v2 | `pending_review` | Minimal local OHLCV sample run reached non-`no_ohlcv` outcomes |

---

## 7. Next recommended task

```text
NEXT BTCFX-20260608-073
Goal: Define a safe local OHLCV supply or manual import workflow for Ver03-v2 intraperiod verification.
Read: docs/operations/deploy/Ver03-v2_OHLCV_SAMPLE_RUN_20260609.md, docs/operations/deploy/Ver03-v2_OHLCV_INPUT_CONTRACT_20260609.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Edit: docs/operations/deploy/Ver03-v2_OHLCV_MANUAL_IMPORT_20260609.md, docs/operations/ai-orchestration/CONTROL.md, docs/operations/ai-orchestration/TASK_LEDGER.md
Test: `git diff --check`
Stop: if external OHLCV fetch, API keys, runtime restart, main.py, run_cycle, live trading, automatic order execution, evaluator semantics changes, or paper_positions.csv integration are required
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
