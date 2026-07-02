# MINI_CODEX_RULES

## Purpose

Codex 5.4-mini medium 向けの最小運用ルールです。

## Lightweight workflow

- ChatGPT が MCP で repo 確認、設計、対象 file 特定を担う
- Codex は単なる text editor ではなく、固定スコープの実装と検証を行ってよい
- Codex は指定範囲内で local inspection、local edit、validation、必要時 commit に集中する
- 同じ Codex thread 内では既知前提を繰り返さず、差分指示でよい
- 巨大な禁止事項リストより、task に関係する境界だけを明示する

## BOUNDED_CODEX

- `BOUNDED_CODEX` は既定の implementation mode
- 許可される local inspection:
  - task で許可された read files
  - task で許可された edit files
  - current diff / status
  - allowed file 内の nearby helpers
  - function / CLI / module 名に対応する matching tests
- broad repo exploration はしない
- fixed-scope source / test / docs work を優先する

## Scope control

- missing required file があれば `BLOCKED`
- edit outside allowed files が必要なら `BLOCKED`
- clean、archive、move、delete、refactor は明示要求がない限りしない
- product judgment が必要なら `BLOCKED`
- safety judgment が必要なら `BLOCKED`

## Test and commit

- task で指定された最小限の check だけ実行する
- task に test がなければ追加しない
- commit は毎 task 必須ではない
- commit は `source/test変更`、`一区切りの docs 整理`、`人間に残すべき状態変更` のときだけ
- `TASK_LEDGER` / `CURRENT_HANDOFF` の逐次更新は通常不要

## Hard safety boundary

- `CHECKPOINT_PUSH` 以外では push しない
- old runtime execution repo には触らない
- push / pull / runtime action が必要なら明示されていない限り止める
- API / secrets / private endpoint / order execution は扱わない
- generated / private / raw data を commit しない

## Report

- response.txt は compact report だけ
- 該当 file、test、commit、push を簡潔に書く

## Stop rule

- required file が missing なら `BLOCKED`
- broad repo inspection が必要なら `BLOCKED`
- product / trading / safety judgment が必要なら `BLOCKED`
- runtime repo、API、secrets、order、private endpoint が要るなら `BLOCKED`

## Good task examples

- `NEXT_ACTION.md` の current summary だけを更新する
- `PROMPTS.md` の 1 つの template を差し替える
- matching test を 1 つだけ追加する

## Bad task examples

- repo 全体の再設計をする
- どの candidate を archive するかを Codex が判断する
- push 先を推測して実行する
- old runtime execution repo を勝手に触る
