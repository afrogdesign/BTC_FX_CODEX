# NEXT_ACTION

- current_work_id: `BTCFX-20260713-OPERATOR-ACTION-JAPANESE-UI-UNKNOWN-SIDE-FIX`
- mode: `BOUNDED_CODEX`
- task_type: `DISPLAY-ONLY FAIL-CLOSED CORRECTION`
- branch: `Ver04-v2`
- parent_commit: `a6e7dea`
- active_spec: `chatgpt/specs/active/20260713_operator_action_japanese_ui_redesign.md`

## Review result

The first review fix corrected:

- STOP card semantics
- Japanese side labels
- unknown-side label fallback
- duplicate no-chase wording

One display defect remains.

For `primary_action_class=B_CHECK_15M` with an unknown or empty `primary_side`, the headline currently becomes:

```text
判定待ち優先：15分足で押し目を確認
```

This is not fail-closed because `押し目` implies a Long-side assumption.

## Exact next action

Change only the headline selection logic so unknown or empty side does not imply either Long or Short.

Required unknown-side headline:

```text
方向判定待ち：15分足を確認
```

or an equivalent neutral Japanese phrase with no `押し目`, `戻り`, `ロング`, `ショート`, or `優先` wording.

Preserve:

- known Long headline
- known Short headline
- all action/state payload values
- report-only safety wording
- no-chase behavior
- entry / invalidation / TP values

Add a targeted regression test that rejects the current `判定待ち優先：15分足で押し目を確認` output.

## Validation

```bash
./.venv312/bin/python -m unittest tests.test_notification_detail_page
git diff --check
```

## Runtime boundary

- source/test/local commit only
- no push
- no runtime restart
- no historical artifact regeneration
- no mail or notification behavior change
- no score, gate, threshold, classifier, API, account, position or order change
