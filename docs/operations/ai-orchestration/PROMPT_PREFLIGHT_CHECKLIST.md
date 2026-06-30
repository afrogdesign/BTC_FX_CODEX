# PROMPT_PREFLIGHT_CHECKLIST

## Purpose

ChatGPT が Codex prompt を出す前に、形が崩れていないかを確認する。

## Required prompt fields

- Work ID
- Goal
- Read
- Edit
- Do
- Tests
- Commit policy
- Stop conditions
- Report

旧来の長い `Do not edit` / `Codex model constraint` / `response.txt rules` の毎回フル記載は不要にする。
ただし危険境界がある task では、Read / Edit / Stop の中で明示する。

## Size check

- 1 から 3 edit files を優先する
- 5 個を超える edit files は explicit authorization が必要
- broad repo inspection はしない
- scope が不明なら送らない
- Codex judgment が必要なら、送る前に ChatGPT 側で決める

## Read/Edit boundary check

- Read は task に必要な file だけにする
- Edit は明示された file だけにする
- source, runtime, generated file は Edit に明示されている場合だけ触る

## Push/Pull check

- normal task は `Do not push` を明記する
- push は `CHECKPOINT_PUSH` だけで許可する
- pull は `RUNTIME_PULL_HANDOFF` だけで許可する
- push/pull target が曖昧なら止める

## Runtime repo check

- old runtime execution repo は通常 task で触らない
- `RUNTIME_PULL_HANDOFF` 以外では触らない

## Safety check

- product / trading / safety judgment が残っていないか確認する
- judgment が残るなら、送る前に ChatGPT が解決する

## Mini Codex check

- Codex 5.4-mini medium 向けには小さい task にする
- 機械的な edit を優先する
- broad exploration を避ける

## Stop / HUMAN_CHECK triggers

- required field が missing
- task scope が unclear
- push / pull / runtime repo が unresolved
- product judgment が unresolved
- safety judgment が unresolved
- task が oversized

## Final output checklist

- task が malformed でない
- task が oversized でない
- push / pull / runtime repo が明確
- HUMAN_CHECK が必要なら先に止める
