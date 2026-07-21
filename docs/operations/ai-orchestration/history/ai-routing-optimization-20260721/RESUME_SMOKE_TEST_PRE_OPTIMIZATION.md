# RESUME_SMOKE_TEST

## Purpose

新しい ChatGPT / Codex thread が、MCP-primary の orchestration docs だけで安全に再開できるかを dry-run で確認する。

## Scope

- docs-only
- product files は触らない
- broad repo exploration はしない

## Smoke test checklist

| Check | Required evidence | Result | Notes |
|---|---|---|---|
| `START_HERE.md` identifies MCP primary repo path | `START_HERE.md` の repo doctrine | pass | `MCP/Codex primary working repo` が明記されている |
| `START_HERE.md` identifies old runtime execution repo path | `START_HERE.md` の repo doctrine | pass | old runtime execution repo が明記されている |
| `START_HERE.md` includes `MINI_CODEX_RULES.md` in the read flow when Codex is used | `START_HERE.md` の fixed low-cost read order | pass | Codex 用の read flow に含まれる |
| `START_HERE.md` includes `PROMPT_PREFLIGHT_CHECKLIST.md` for ChatGPT prompt creation | `START_HERE.md` の fixed low-cost read order | pass | ChatGPT 用の preflight 参照が含まれる |
| `CONTROL.md` says normal Codex task is local edit / validation / local commit / compact report | `CONTROL.md` の Current State / Operation Mode | pass | normal task の流れが一致している |
| `CONTROL.md` says push is reserved for CHECKPOINT_PUSH | `CONTROL.md` の Operation Mode | pass | push は checkpoint のみ |
| `PROMPTS.md` includes `MINI_CODEX_MEDIUM` | `PROMPTS.md` の mode sections | pass | 該当 section がある |
| `PROMPTS.md` includes `PROMPT_PREFLIGHT` | `PROMPTS.md` の mode sections | pass | 該当 section がある |
| `PROMPTS.md` includes `CHECKPOINT_PUSH` | `PROMPTS.md` の mode sections | pass | 該当 template がある |
| `PROMPTS.md` includes `RUNTIME_PULL_HANDOFF` | `PROMPTS.md` の mode sections | pass | 該当 template がある |
| `MINI_CODEX_RULES.md` says broad repo exploration is forbidden | `MINI_CODEX_RULES.md` の Forbidden work | pass | 明記されている |
| `MINI_CODEX_RULES.md` says design judgment should become BLOCKED | `MINI_CODEX_RULES.md` の Stop rule | pass | 判断は `BLOCKED` にする規則がある |
| `PROMPT_PREFLIGHT_CHECKLIST.md` includes required prompt fields | `PROMPT_PREFLIGHT_CHECKLIST.md` の Required prompt fields | pass | 全項目が列挙されている |
| `PROMPT_PREFLIGHT_CHECKLIST.md` defines AUTO_SEND allowed conditions | `PROMPT_PREFLIGHT_CHECKLIST.md` の AUTO_SEND allowed conditions | pass | 条件が列挙されている |
| `CHECKPOINT_RUNBOOK.md` says push target must not be inferred | `CHECKPOINT_RUNBOOK.md` の Branch / remote rule | pass | 推測禁止が明記されている |
| `RUNTIME_PULL_HANDOFF.md` says human confirmation is required before pull | `RUNTIME_PULL_HANDOFF.md` の Human confirmation required | pass | pull 前の human 確認が明記されている |
| `REPO_MAP.md` includes anchors for `MINI_CODEX_RULES.md`, `CHECKPOINT_RUNBOOK.md`, and `RUNTIME_PULL_HANDOFF.md` | `REPO_MAP.md` の AI operation anchors | pass | 3 anchors すべて含まれている |

## Resume path result

- pass
- `START_HERE.md` から `MINI_CODEX_RULES.md` と `PROMPT_PREFLIGHT_CHECKLIST.md` までの流れが揃っている

## Codex prompt safety result

- pass
- `PROMPTS.md` と `PROMPT_PREFLIGHT_CHECKLIST.md` により、サイズ・境界・HUMAN_CHECK 条件が明確

## Push/pull/runtime separation result

- pass
- `CHECKPOINT_RUNBOOK.md` と `RUNTIME_PULL_HANDOFF.md` で push / pull / runtime repo の分離が明確

## Mini Codex result

- pass
- `MINI_CODEX_RULES.md` により、Codex 5.4-mini medium 向けの mechanical task 前提が明確

## Issues found

- none

## Next recommendation

- ready_for_product_work
