# CLEANUP_AUDIT

## Purpose

cleanup 候補を安全に分類し、後で archive しやすいものを見分ける。

## Rules

- Level 0: mark only
- Level 1: move clearly legacy docs into `legacy/`
- Level 2: archive old docs after human approval
- Level 3: delete generated or environment files only with explicit human approval
- この task では level action を実行しない

## Archive-later candidates

- `docs/operations/ai-orchestration/legacy/*`

## Keep-as-reference candidates

- `chatgpt/analysis/*`
- `chatgpt/specs/archive/*`
- `docs/operations/ai-orchestration/TASK_LEDGER.md`

## Never-auto-delete candidates

- `.venv312/`
- `logs/`

## Review-later candidates

- `docs/operations/deploy/Ver03-v2_*`
- generated CSV/report/HTML outputs
- `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md`

## Explicitly out of scope

- `/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`
- source code
- runtime behavior
- push / pull / runtime actions

## Next recommended cleanup task

- `BTCFX-20260630-ORCHESTRATION-MINI-CODEX-HARDENING`
- Goal: Harden prompt templates and runbooks for Codex 5.4-mini medium by making tasks more mechanical, smaller, and less judgment-heavy.
