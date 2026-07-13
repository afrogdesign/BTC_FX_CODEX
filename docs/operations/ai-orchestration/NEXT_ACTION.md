# NEXT_ACTION

- current_work_id: `BTCFX-20260713-OPERATOR-ACTION-JAPANESE-UI-REDESIGN`
- mode: `BOUNDED_CODEX`
- task_type: `PUBLIC DETAIL HTML DISPLAY / JAPANESE UI REDESIGN`
- branch: `Ver04-v2`
- active_spec: `chatgpt/specs/active/20260713_operator_action_japanese_ui_redesign.md`
- human_approval: received

## Goal

Public detail HTMLの次の2ブロックを、承認済みデザインへ変更する。

1. 現在の行動方針
2. 現在の売買判断

内部変数のような英語tokenを主要表示から外し、ロング・ショートの優先度、15分足確認、様子見、追いかけ禁止、新規見送り・保護確認を自然な日本語で即座に理解できる表示にする。

## Allowed source scope

- `src/notification/detail_page.py`
- `tests/test_notification_detail_page.py`

## Required behavior

- `SHORT B_CHECK_15M`、`C_WATCH_ZONE`、`15M: late`、`1H: wait`、`4H: wait`を主要表示へ出さない
- dynamic internal values are preserved; visible labels use deterministic Japanese mappings
- primary side is visually emphasized
- Long / Short cards and timeframe chips are readable at a glance
- A/B/C/STOP guide and plan detail labels use clear Japanese
- late/no-chase visibly says `追いかけ禁止`
- entry zone, invalidation, TP1 and TP2 values remain unchanged
- report-only safety wording remains visible

## Validation

```bash
./.venv312/bin/python -m unittest tests.test_notification_detail_page
git diff --check
```

One existing-fixture local render smoke is allowed if needed.

## Runtime boundary

- source/test/local commit only
- pushなし
- runtime restartなし
- historical artifact regenerationなし
- mail送信なし
- notification behavior変更なし
- scoring、gate、threshold、classifier、API、account、position、order変更なし

## After implementation

ChatGPTがdiffとtargeted test結果をreviewする。runtime applyはreview後の別承認taskとする。
