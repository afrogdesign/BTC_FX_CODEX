# AI Orchestration Control

last_updated: 2026-06-08
repo: `afrogdesign/BTC_FX_CODEX`
branch: `Ver03-v2`
current_commit: `b904e13`
note: `current_commit` is the latest ChatGPT-reviewed baseline and may intentionally lag the latest commit by one task.
project_key: `BTCFX`

---

## 1. Current objective

Ver03-v2 begins by rebuilding AI operation anchors before returning to trading-system implementation.

The immediate goal is to make ChatGPT / Codex / future agents use stable repository files instead of long repeated prompts.

---

## 2. Current constraints

- ChatGPT is commander, planner, and reviewer.
- Codex is implementation worker.
- Codex must not make design decisions.
- Codex must not perform broad repository exploration unless explicitly requested.
- Codex should read only files named in the task.
- Real order APIs, exchange API keys, secrets, and live trading are out of scope.
- Runtime monitor restart is out of scope unless explicitly requested.

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

---

## 7. Next recommended task

```text
NEXT BTCFX-20260608-051
Goal: Decide the first Ver03-v2 implementation task after AI anchors and NEXT_TASK are stable.
Read: `docs/operations/ai-orchestration/CONTROL.md`, `docs/operations/ai-orchestration/REPO_MAP.md`, `運用資料/NEXT_TASK.md`, `運用資料/計画/README.md`
Edit: `docs/operations/ai-orchestration/CONTROL.md`, `docs/operations/ai-orchestration/TASK_LEDGER.md`
Test: `git diff --check`
Stop: if source code changes are needed
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
