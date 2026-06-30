# MINI_CODEX_RULES

## Purpose

Codex 5.4-mini medium 向けの最小運用ルールです。

## Default task shape

- 1 から 3 個の edit files を基本にする
- task は小さく、機械的にする
- 何を変えるかは task 内で明示する

## File limit

- edit files が 5 個を超えるなら明示的な authorization が必要
- file limit を超える task は `BLOCKED` にする

## Read rule

- broad repo exploration をしない
- task で指定された file と必要最小限の nearby file だけ読む
- missing required file があれば `BLOCKED`

## Edit rule

- Edit に列挙された file だけ編集する
- source/runtime/generated files は Edit に明示されたときだけ触る
- clean, archive, move, delete, refactor は明示要求がない限りしない

## Test rule

- task で指定された最小限の check だけ実行する
- task に test がなければ追加しない

## Commit rule

- local commit は checks が通った後にだけ行う
- commit message は task に従う

## Push rule

- `CHECKPOINT_PUSH` 以外では push しない
- old runtime execution repo には触らない

## Stop rule

- required file が missing なら `BLOCKED`
- judgment が必要なら、task に rule が埋め込まれていない限り `BLOCKED`
- broad repo inspection が必要なら `BLOCKED`
- product / trading / safety judgment が必要なら `BLOCKED`

## Report rule

- compact report は短くする
- 該当 file, test, commit, push のみを簡潔に書く

## Forbidden work

- broad repo exploration
- design judgment
- cleaning, archiving, moving, deleting, refactoring without explicit request
- push outside `CHECKPOINT_PUSH`
- old runtime execution repo touching outside `RUNTIME_PULL_HANDOFF`
- source/runtime/generated edits outside explicit Edit

## Good task examples

- `NEXT_ACTION.md` の current summary だけを更新する
- `PROMPTS.md` の 1 つの template を差し替える
- `REPO_MAP.md` に 1 行 anchor を足す

## Bad task examples

- repo 全体の再設計をする
- どの candidate を archive するかを Codex が判断する
- push 先を推測して実行する
- old runtime execution repo を勝手に触る
