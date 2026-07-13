# NEXT_ACTION

- current_work_id: `BTCFX-20260713-OPERATOR-ACTION-JAPANESE-UI-REVIEW-FIX`
- mode: `BOUNDED_CODEX_FIX`
- task_type: `PUBLIC DETAIL HTML DISPLAY / REVIEW CORRECTION`
- branch: `Ver04-v2`
- parent_commit: `93c301a`
- active_spec: `chatgpt/specs/active/20260713_operator_action_japanese_ui_redesign.md`

## Review result

The first Japanese UI implementation is not yet accepted.

MCP source review confirmed four display defects:

1. `STOP_OR_EXIT` can be displayed as `監視のみ`, weakening the required `新規見送り・保護確認` meaning.
2. The shadow/detail cards still visibly render raw `LONG` / `SHORT` side labels instead of `ロング` / `ショート`.
3. Unknown or empty side values are treated as Short rather than failing closed to `判定待ち`.
4. A late no-chase state can display `追いかけ禁止` twice in the same hero status.

## Exact next action

Correct only the display helpers, target render functions, and matching tests in:

- `src/notification/detail_page.py`
- `tests/test_notification_detail_page.py`

Required results:

- `STOP_OR_EXIT` side card visibly says `新規見送り・保護確認`
- primary side labels in the redesigned shadow/detail block use `ロング` / `ショート`
- unknown side displays `判定待ち`
- `追いかけ禁止` appears once in the late/no-chase hero status
- all existing numeric values and safety wording remain unchanged

## Validation

```bash
./.venv312/bin/python -m unittest tests.test_notification_detail_page
git diff --check
```

## Boundary

- display/test correction only
- no classifier, score, gate, threshold, entry, SL, TP, notification, mail, runtime, launchd, API, account, position, or order change
- no push
- no runtime apply
- active spec remains active until ChatGPT accepts the corrected diff
