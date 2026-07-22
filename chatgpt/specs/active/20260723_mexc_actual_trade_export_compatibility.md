# MEXC Actual Trade Export Compatibility Active Spec

## Metadata

- work_id: `P9-MEXC-IMPORT-COMPAT-20260723`
- created_at: `2026-07-23`
- status: active / implementation authorized
- task_type: bounded compatibility adapter
- baseline_branch: `Ver04-v4`
- baseline_head: `038b8b6843f9546bc084256dfb215eed923f820c`
- working_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- safety: report-only / not `FORMAL_GO` / no automatic order / human-decided trades

---

## 1. Objective

最新MEXC先物exportを、既存のcanonical actual trade importerへ安全に取り込める互換形式として認識する。

このtaskは既存importerの意味、canonical schema、conflict policyを変更しない。実import、episode生成、signal linkage、P9 readiness判断は別taskとする。

---

## 2. Accepted diagnostic evidence

`P9-MEXC-IMPORT-DRYRUN-20260723`の書込みなし診断で次を確認した。

- branch / HEADはbaselineと一致
- trade / order / positionの最新3ファイルはbasenameで一意認識
- 旧3ファイルを含め、各category 2ファイルを認識
- 全workbookのselected sheetは`Sheet1`
- canonical outputsは実行前後で不変
- unsupported補助xlsxは3category入力に含まれない
- order historyはrequired header差分で2 workbookともfail closed
- trade / positionは`unknown_direction`と`malformed_numeric`でrow reject
- raw row値、UID、価格、数量、損益はreportへ出していない

Diagnostic conclusion:

```text
header_alias_spec_required + row_normalization_spec_required
```

---

## 3. Scope

Allowed implementation files:

```text
src/feedback/manual_actual_trade_importer.py
tests/test_mexc_actual_trade_importer.py
```

ChatGPT-authored task records, stage-only when unchanged:

```text
chatgpt/specs/active/20260723_mexc_actual_trade_export_compatibility.md
docs/operations/ai-orchestration/NEXT_ACTION.md
```

`tools/log_feedback.py` may be edited only if required to expose bounded, non-sensitive summary counters. CLI command names and arguments must not change.

No other source, test, runtime, notification, macro, mail, public-delivery, gate, threshold, scoring, or classifier file is in scope.

---

## 4. Header compatibility contract

Header normalization occurs before required-column validation.

Only the following exact order-history aliases are authorized:

| observed header | canonical semantic header |
|---|---|
| `約定数量 (枚)` | `約定数量` |
| `取引手数料` | `手数料` |

Rules:

- old canonical headers remain accepted unchanged
- matching is exact after existing whitespace trimming only
- fuzzy matching, partial matching, positional mapping, translated guessing, and column-index fallback are prohibited
- `約定数量 (トークン)` and `約定数量 (金額)` must not substitute for canonical `約定数量`
- `手数料支払い暗号資産` is an optional unknown column for order history and may remain ignored; do not change canonical order output semantics in this task
- if canonical and alias headers both map to the same semantic field in one workbook, fail closed with stable `ambiguous_header_alias`
- unknown columns remain ignored
- any other missing required semantic field remains `missing_required_column`

---

## 5. Direction normalization contract

Codex may inspect distinct failing direction tokens locally to implement a finite exact allowlist, but must not print or report raw tokens or row values.

An alias may be accepted only when the token itself explicitly and unambiguously denotes one of these existing canonical meanings:

```text
long
short
buy
sell
open long
close long
open short
close short
```

Rules:

- preserve the existing `(side, transaction_side, position_action)` meanings
- use literal exact aliases after trim and case normalization only
- no fuzzy matching, substring guessing, language-model inference, positional inference, or numeric-code inference
- do not infer open/close from PnL, status, timestamps, quantity, order type, or surrounding rows
- do not infer long/short from buy/sell alone
- if a token contains changing numeric decoration, leverage, or other mixed semantics that cannot be represented by a finite explicit allowlist without guessing, leave it rejected and report only the bounded reason count
- unknown values remain fail closed

---

## 6. Numeric normalization contract

Codex may inspect the failing field names and value shapes locally, but must not print or report raw values.

A normalization is allowed only when it is presentation cleanup that preserves the exact numeric magnitude and sign.

Allowed principles:

- keep existing comma removal and full-width sign normalization
- permit an exact, field-specific suffix/prefix cleanup only when the removed token is an explicit unit or asset presentation attached to that same numeric field
- the remaining token must parse as a finite `Decimal`
- no unit conversion
- no percentage conversion
- no multiplication or division by contract size
- no sign inversion
- no absolute-value conversion except the existing fee non-negative storage rule
- no mapping of missing sentinels to zero
- an explicit missing sentinel may map to empty only for an already-optional canonical numeric field; required numeric fields remain rejected
- ambiguous mixed text remains `malformed_numeric`

Fee, realized PnL, price, and quantity semantics must not be inferred from another row or another category.

---

## 7. Privacy and raw-data boundary

Hard requirements:

- raw exchange xlsx remains untracked and uncommitted
- do not copy raw exports
- do not create fixtures from real rows
- tests use synthetic minimal xlsx only
- no raw UID in source, tests, stdout, report, exception, or commit
- no raw row values in report
- no price, quantity, fee, realized PnL, or account-specific value in report
- source may contain only generic header names and finite categorical aliases required for compatibility
- do not read `.env`, secrets, API keys, private/account/order endpoints
- do not access the frozen runtime repo

---

## 8. Observable behavior

After implementation:

1. Old synthetic format continues to pass all existing focused tests.
2. New order headers pass required-column validation through the exact alias map.
3. Ambiguous duplicate semantic headers fail closed with `ambiguous_header_alias`.
4. Explicitly supported direction aliases normalize to the existing canonical tuple.
5. Explicitly supported numeric presentation formats normalize without changing magnitude or sign.
6. Unknown or ambiguous values remain rejected with stable reason codes.
7. Dry-run never changes canonical outputs or the issues CSV.
8. Default conflict policy remains `reject`.
9. Duplicate and logical-key behavior remains unchanged.
10. Filename classification and unsupported supplementary-file behavior remain unchanged.

Bounded summary metadata may add category/reason counters when needed, but must not include source row values.

---

## 9. Validation budget

Run exactly the smallest required validation:

```text
.venv312/bin/python -m unittest tests.test_mexc_actual_trade_importer
```

Then run the real-data command exactly once after code changes:

```text
.venv312/bin/python tools/log_feedback.py import-manual-actual-trades --input-dir docs/mexc_csv --dry-run --stdout-json
```

Finally run task-scoped diff validation:

```text
git diff --check -- src/feedback/manual_actual_trade_importer.py tests/test_mexc_actual_trade_importer.py tools/log_feedback.py chatgpt/specs/active/20260723_mexc_actual_trade_export_compatibility.md docs/operations/ai-orchestration/NEXT_ACTION.md
```

Do not run:

- full suite
- repeated dry-run
- actual import
- episode builder
- signal linker
- ground-truth report
- macro/runtime/notification/mail/public checks
- frozen runtime commands

---

## 10. Dry-run decision contract

Implementation is `done` when:

- no workbook-level header error remains
- `missing_categories=[]`
- all six recognized category files are read from `Sheet1`
- at least one row is safely accepted from each category
- canonical outputs are verified unchanged
- no conflict is hidden or automatically replaced
- remaining rejected rows, if any, are limited to values that remain ambiguous under this spec and are reported only by category/reason counts

Implementation is `partial` when safe exact adapters are complete but ambiguous values remain rejected.

Implementation is `blocked` when semantic compatibility would require guessing, unit conversion, sign reinterpretation, or product/trading judgment.

A dry-run conflict under default `reject` is not an adapter failure. Report it separately and stop before actual import.

---

## 11. Commit boundary

- stage only task files
- never stage raw xlsx or generated canonical CSV
- local commit required for a completed or materially useful partial adapter
- push: none
- ChatGPT performs final source/test/CLI review and decides whether actual import may be authorized
