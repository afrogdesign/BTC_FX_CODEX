# RUNTIME_PULL_HANDOFF

## Purpose

MCP working repo の checkpoint push から old runtime execution repo の pull handoff への流れを定義します。
実行はしません。

## Runtime repo path

`/Users/marupro/CODEX/01_active/BTC_FX_CODEX/btc_monitor`

## Relationship to MCP working repo

- 実際の execution files がまだ参照する repo
- 通常の editing target ではない
- checkpoint push の後にだけ更新対象になる

## Preconditions

- MCP working repo 側で reviewed checkpoint push が完了している
- human が pull handoff を明示している
- 対象 branch と pull 先が明確

## Human confirmation required

- pull を始める前に human 確認が必要
- 自動化で勝手に pull しない

## Pull handoff steps

- checkpoint push の対象 commit を確認する
- runtime repo 側で pull 対象 branch を確認する
- human 確認後に別 task として pull を実施する

## What Codex must not do by default

- runtime restart をしない
- launch をしない
- daily-sync をしない
- notification sending をしない
- trading execution をしない
- secret を読まない
- runtime repo を通常 task で編集しない

## Stop conditions

- pull target が曖昧
- branch が曖昧
- human confirmation がない
- runtime action が必要になる
- checkpoint push が未完了

## Report format

- `WORK_ID`
- `STATUS`
- `CHANGED`
- `TESTS`
- `COMMIT`
- `PUSH`
- `NOTES`
