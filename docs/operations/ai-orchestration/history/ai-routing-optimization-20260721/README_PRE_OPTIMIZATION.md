# AI Orchestration Records

このdirectoryは、現在地・次作業・運用規則・履歴を分離して管理します。

## 最短導線

```text
START_HERE.md
→ CURRENT_STATE.md
→ NEXT_ACTION.md
→ chatgpt/specs/active/<current spec>
```

`CONTROL.md` は運用判断が必要な場合だけ読みます。

## 正本の分担

| File | 書く内容 | 書かない内容 | 更新時点 |
|---|---|---|---|
| `START_HERE.md` | 最短読取順、repo境界、安全入口 | phase履歴、個別task詳細 | 導線変更時のみ |
| `CURRENT_STATE.md` | 受理済み状態、active phase、blocker | 長い時系列ログ | acceptance・重要状態変更時 |
| `NEXT_ACTION.md` | 現在のWork IDを1件だけ | 完了済みtask、候補task一覧 | task切替時 |
| `CONTROL.md` | stableな役割、安全、git、validation規則 | current task履歴 | 規則変更時のみ |
| `MILESTONES.md` | 受理済みの大きな節目 | FIX単位の経過、未受理結果 | phase acceptance時 |
| `DECISIONS.md` | product・設計上の重要判断 | 実装ログ | 判断確定時 |
| `TASK_LEDGER.md` | 重要Work IDの検索用記録 | 毎回のaccept/status-only task | 必要なcheckpointのみ |
| `handoffs/CURRENT_HANDOFF.md` | thread・担当交代の一時引継ぎ | 常時参照する現在地 | handoff時のみ |

## Active spec

- 詳細な実装契約は `chatgpt/specs/active/` に1件だけ置く。
- acceptance前のFIX履歴はactive spec内の短いfactual noteへ記録する。
- acceptance後は `chatgpt/specs/archive/` へ移す。
- active specと`NEXT_ACTION.md`が矛盾する場合は実装を止める。

## 更新ルール

### 通常のsource task

更新しない:

- `CURRENT_STATE.md`
- `CONTROL.md`
- `MILESTONES.md`
- `TASK_LEDGER.md`

必要ならactive specへ短い事実だけ追記します。

### Acceptance

1. active specをarchive
2. `CURRENT_STATE.md`を更新
3. `NEXT_ACTION.md`を次の1件へ置換
4. routeや制御が変わる場合だけ`CONTROL.md`を更新
5. 大きなphase完了だけ`MILESTONES.md`へ追加

### Important decision

`DECISIONS.md`へ、Decision / Reason / Consequencesだけを追加します。

## 履歴の扱い

- commit・diff・test結果の正本はgitとcompact report。
- `TASK_LEDGER.md`は全文読取せず、Work IDやsymbolで限定検索する。
- 古い詳細版は `history/record-optimization-20260721/` に保存している。
- 同じ事実を複数のcurrent fileへ重複記録しない。

## Current task pointer

現在の作業は常に `NEXT_ACTION.md` を参照します。
