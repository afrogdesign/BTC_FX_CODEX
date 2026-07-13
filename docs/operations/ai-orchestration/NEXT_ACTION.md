# NEXT_ACTION

- current_work_id: `BTCFX-20260713-OPERATOR-ACTION-JAPANESE-UI-GENERIC-UNKNOWN-SIDE-FIX`
- mode: `BOUNDED_CODEX`
- task_type: `FINAL DISPLAY-ONLY FAIL-CLOSED CORRECTION`
- branch: `Ver04-v2`
- parent_commit: `95b56e7`
- active_spec: `chatgpt/specs/active/20260713_operator_action_japanese_ui_redesign.md`

## Review result

The B_CHECK_15M unknown-side headline is corrected:

```text
方向判定待ち：15分足を確認
```

Known Long and Short B headlines remain correct.

One generic non-B fail-closed defect remains.

Current generic branch:

```python
headline = f"{side_name}優先：{_operator_action_label(primary_class)}"
```

For unknown or malformed side this can render:

```text
判定待ち優先：<action label>
```

An unknown side must not use `優先` or imply a selected direction.

## Exact next action

Change only the generic non-B headline selection:

- known `long` or `short`: preserve current side-priority wording
- unknown / empty / malformed side: `方向判定待ち：<日本語action label>`

Add a targeted unknown-side regression test using `C_WATCH_ZONE` or `A_FORMAL` so the generic branch is exercised. Do not use `STOP_OR_EXIT` as the sole fixture because STOP has a dedicated headline branch.

Preserve:

- all B_CHECK_15M headline behavior
- STOP semantics
- Japanese side labels
- no-chase behavior
- HTML escaping
- entry / invalidation / TP values
- report-only safety wording

## Validation

```bash
./.venv312/bin/python -m unittest tests.test_notification_detail_page
git diff --check
```

## Runtime boundary

- source/test/local commit only
- pushなし
- runtime restartなし
- historical artifact regenerationなし
- mail・notification behavior変更なし
- score、gate、threshold、classifier、API、account、position、order変更なし

Runtime apply remains blocked until this final correction is reviewed and accepted.
