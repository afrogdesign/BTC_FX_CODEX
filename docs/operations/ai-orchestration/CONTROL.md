# AI Orchestration Control

last_updated: 2026-06-13
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v3`
current_commit: ed5c91038c589576f4ddd359d61b7a6905e0eac5
note: `current_commit` is the latest ChatGPT-reviewed baseline and may intentionally lag the actual branch HEAD or the latest pushed commit by one or more tasks. That mismatch alone is not a BLOCK condition.
project_key: `BTCFX`

---

## 1. Current objective

BTCFX-20260613-135-ACTIONABILITY-SHADOW-RUNBOOK is ChatGPT-reviewed and accepted at `ed5c91038c589576f4ddd359d61b7a6905e0eac5`; this sync records the reviewed Actionability shadow runbook baseline on top of the one-command local manual-delivery flow, source freshness guard, CLI-only API fallback kill switch, Actionability Gate baseline, the separate Actionability shadow ledger writer, the JSON-driven shadow writer, and the local-flow opt-in shadow append path.

BTCFX-20260612-121-CLI-ONLY-AUTO-API-FALLBACK-KILL-SWITCH-REVIEW-DIRTY-ALLOWED passed as REVIEW_ONLY with no commit and no new dirty files.

BTCFX-20260612-124-ACTIONABILITY-GATE-V1 added deterministic Actionability Gate v1 fields to local manual-delivery JSON and inbox outputs.

BTCFX-20260612-125-ACTIONABILITY-GATE-RUNTIME-EMAIL-V1 added Actionability Gate v1 fields to the runtime summary email body without changing send or trading behavior.

BTCFX-20260612-127-ACTIONABILITY-JA-EMAIL-LABELS added Japanese human-readable Actionability labels to runtime email bodies while preserving machine keys for logs and verification.

BTCFX-20260613-129-ACTIONABILITY-SHADOW-LEDGER-V1 added a separate Actionability shadow decision ledger writer for evaluation-only logging without touching `paper_positions.csv` or trading behavior.

BTCFX-20260613-131-ACTIONABILITY-SHADOW-FROM-JSON-V1 added a JSON-driven Actionability shadow decision writer that appends one row from `manual-delivery-input.json` without recomputing actionability or touching `paper_positions.csv`.

BTCFX-20260613-133-ACTIONABILITY-SHADOW-LOCAL-FLOW-OPTIN added an opt-in shadow ledger append path to the one-command local manual-delivery flow. Default local-flow behavior remains unchanged, and the opt-in path appends one row from the generated `manual-delivery-input.json`.

BTCFX-20260613-135-ACTIONABILITY-SHADOW-RUNBOOK documents the opt-in Actionability shadow ledger append path in the manual-preview runbook. Default local-flow behavior remains unchanged, generated shadow CSV output must not be committed unless explicitly approved, and the shadow ledger remains evaluation-only and separate from `paper_positions.csv`.

BTCFX-20260611-RESUME-FINAL-SYNC finalized the reviewed Ver03-v3 resume protocol metadata after BTCFX-20260610-099-SYNC-REVIEW passed.

The reviewed baseline now includes the one-command local manual-delivery flow, source freshness guard, CLI-only API fallback kill switch, deterministic Actionability Gate v1, runtime email Actionability fields, Japanese human-readable Actionability labels, the separate Actionability shadow decision ledger writer, the JSON-driven shadow decision writer, the local-flow opt-in shadow append path, and the reviewed runbook documentation for that opt-in path. CLI provider mode must not silently fall back to OpenAI API; API usage requires explicit `AI_API_USAGE_ALLOWED`; CLI failure returns `cli_failed`; API disabled returns `api_disabled`; post-review API fallback is gated by `AI_POST_REVIEW_API_FALLBACK_ENABLED`; Actionability output remains report-only triage, not FORMAL_GO, and no automatic order; all shadow writers remain isolated from `paper_positions.csv` and trading behavior; the JSON-driven writer appends from `manual-delivery-input.json` without recomputing actionability; the one-command local-flow default behavior remains unchanged unless the opt-in flag is supplied; generated shadow CSV output must not be committed unless explicitly approved; and the reviewed manual-preview runbook remains at `docs/operations/manual-preview/ACTIVE_PLAN_MANUAL_PREVIEW_RUNBOOK.md`.

Safety boundary remains report-only, not FORMAL_GO, no automatic order, ACTIVE_* guidance only, human must decide manually, no external notification integration, no clipboard/address-book integration, no paper_positions.csv integration, and no runtime/deploy/trading/API key/private endpoint changes.

BTCFX-20260610-CONTEXT-RULE and BTCFX-20260610-CONTEXT-RULE-FIX keep the reviewed baseline rules in place while this boundary is defined.

BTCFX-20260610-086 selected the conservative pending decision `PENDING_ACCEPT_WITH_CAVEAT_FOR_WIRING_BOUNDARY_DESIGN`.

BTCFX-20260608-070 prepares an exact-path cleanup/archive plan for BTCFX Ver03-v2 generated diagnostics without deleting files, but that archive step is deferred until the report review gate is complete.

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

Execution and deployment are paused until the automatic exchange/public market-data path is designed and approved.

Manual OHLCV work from BTCFX-20260608-071 to BTCFX-20260608-073 is fallback/reference only, not the operating path.

BTCFX-20260610-085 coverage review selected the conservative boundary `COVERAGE_NEEDS_PENDING_REASON_REVIEW`.

Coverage summary: 499 OHLCV rows, 88 outcome rows, all candidate timestamps inside the OHLCV window, and `pending` rows remain concentrated in recent rows.
Pending summary: 12 pending rows, 76 resolved rows, 11 recent unresolved windows, and 1 entry-not-touched-by-simple-range-check.

Report/daily-sync/runtime/deploy/trading were not run.

BTCFX-20260610-087 preserves the approved future boundary: public 15m OHLCV fetch-to-local diagnostic artifact, intraperiod outcome builder I/O, Markdown report generation, report-only daily-sync/report hub integration boundary, and human review gates before any runtime/deploy/trading work.

The active deliverable is the reviewed local manual-delivery flow baseline plus source freshness guard plus CLI-only API fallback kill switch plus Actionability Gate v1 email/manual-delivery surfacing plus the separate Actionability shadow ledger plus the JSON-driven shadow writer plus the local-flow opt-in shadow append path plus the reviewed runbook documentation for that opt-in path and their reviewed-baseline metadata sync.

The next recommended task is STOP: choose the next product step after the reviewed Actionability shadow runbook baseline.

MBP2020 has a completed frozen ver02.6-v2 comparison runner migration.

Detailed record is in `docs/operations/deploy/Ver02_6_v2_MBP2020_FROZEN_RUNNER_20260609.md`.

This does not change Ver03-v2 implementation scope or the BTCFX-20260608-078 boundary.

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
- If Codex has local filesystem access, the final compact report must also be written to `/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt` for every task type and outcome, including `NEXT`, `FIX`, `SYNC`, `HANDOFF`, `REVIEW_ONLY`, `BLOCKED`, no-commit review work, and resume checks.

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
| BTCFX-20260608-073 | done | Define a safe local OHLCV manual import workflow for Ver03-v2 intraperiod verification | Ver03-v2 | `pending_review` | Safe maintained-local OHLCV import workflow defined |
| BTCFX-20260608-074 | done | Re-align Ver03-v2 from manual/local OHLCV proof toward exchange-auto market data design before further execution, deployment, or script expansion | Ver03-v2 | `pending_review` | Docs-only auto market data replan; manual OHLCV downgraded to fallback/reference |
| BTCFX-20260608-075 | done | Define winning-trade criteria and required market information for Ver03-v2 Active Plan intraperiod verification before further execution or implementation | Ver03-v2 | `pending_review` | Docs-only winning-trade criteria and required market information defined |
| BTCFX-20260608-076 | done | Map required market information to existing exchange/public data sources and design the automatic fetch-to-local-diagnostic data flow before execution or implementation | Ver03-v2 | `pending_review` | Docs-only market-data source map and fetch-to-local-diagnostic design |
| BTCFX-20260608-077 | done | Define the exact safe implementation boundary for automatic public 15m OHLCV fetch-to-local-diagnostic output before implementation | Ver03-v2 | `pending_review` | Docs-only fetch-to-local-diagnostic boundary with review checkpoint |
| BTCFX-20260608-078 | done | Implement standalone automatic public 15m OHLCV fetch-to-local-diagnostic CSV tool | Ver03-v2 | `pending_review` | Mocked fetch-only tests; no real external fetch was run |
| BTCFX-20260610-080 | done | Record the first controlled real public 15m OHLCV fetch run for Ver03-v2 | Ver03-v2 | `pending_review` | Fetch succeeded with 499 rows; builder/report/daily-sync not run |
| BTCFX-20260610-081 | done | Record the first controlled intraperiod builder run using generated exchange-auto-public 15m OHLCV | Ver03-v2 | `pending_review` | Builder succeeded with 88 rows; non-`no_ohlcv` rows exist; report/daily-sync/runtime/deploy/trading not run |
| BTCFX-20260610-082 | done | Record the first controlled Markdown report generation from exchange-auto-public intraperiod outcomes | Ver03-v2 | `pending_review` | Report succeeded with 88 lines / 7327 chars; expected markers present; daily-sync/runtime/deploy/trading not run |
| BTCFX-20260610-083 | done | Review exchange-auto-public intraperiod report quality and candidate coverage | Ver03-v2 | `pending_review` | Conservative boundary selected: NEXT_MANUAL_REPORT_REVIEW; report quality clear; coverage includes pending bucket; wiring not run |
| BTCFX-20260610-084 | done | Provide a human-facing checklist for the generated exchange-auto-public intraperiod report | Ver03-v2 | `pending_review` | Checklist-only review gate; human selects REPORT_ACCEPT_FOR_WIRING_DESIGN / REPORT_NEEDS_WORDING_FIX / REPORT_NEEDS_COVERAGE_REVIEW / REPORT_HOLD |
| BTCFX-20260610-085 | done | Review candidate coverage and OHLCV window alignment for generated exchange-auto-public intraperiod artifacts | Ver03-v2 | `pending_review` | Conservative boundary selected: COVERAGE_NEEDS_PENDING_REASON_REVIEW; all candidate timestamps inside OHLCV window; pending rows concentrated in recent rows |
| BTCFX-20260610-086 | done | Review pending outcome reasons for generated exchange-auto-public intraperiod artifacts | Ver03-v2 | `c5e8dfb78ca0dbb5396d7ddbb8731e6106094120` | Conservative boundary selected: PENDING_ACCEPT_WITH_CAVEAT_FOR_WIRING_BOUNDARY_DESIGN; 11 recent unresolved windows and 1 entry-not-touched-by-simple-range-check |
| BTCFX-20260610-087 | done | Define docs-only wiring boundary design for Ver03-v2 exchange-auto-public intraperiod diagnostics | Ver03-v2 | `0f9282226e18103b0baead2d190bdc75416e390c` | Preserves heuristic pending categories, non-FORMAL_GO ACTIVE_* guidance, no automatic orders, and no paper_positions.csv integration yet |

---

## 7. Next recommended task

```text
STOP: Choose whether to run an end-to-end no-commit review of the local manual-delivery flow or choose the next product step.
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
