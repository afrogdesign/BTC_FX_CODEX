# Structural Priority Review Fix — Active Specification

## Metadata

- work_id: `BTCFX-20260712-P8-STRUCTURAL-PRIORITY-REVIEW-FIX`
- parent_commit: `9c9a631`
- phase: P8 manual-trading display correction
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## Goal

Complete the accepted 4H/1H structural-priority design without changing production scoring, thresholds, gates, notification behavior, mail, runtime, APIs, positions, or orders.

The numeric audit and the 4H 75% / 1H 25% formula are accepted. This task fixes review defects in qualitative strength, turning-conflict precedence, CSV semantics, integration-order evidence, and bounded preview validation.

## Review findings

### 1. Qualitative strength contract is missing

The approved specification requires these stable strength buckets based on the winning-side structural points:

- no structural evidence: `insufficient`
- 50–55: `neutral`
- 56–64: `slight`
- 65–74: `clear`
- 75–84: `strong`
- 85–90: `very_strong`

The current module returns only a generic `priority_label`. Add an explicit `strength` field. Preserve the continuous points and the 45–55 inclusive neutral-primary band.

The visible HTML label must be Japanese and must distinguish:

- `判定材料不足`
- `中立`
- `中立圏（Long寄り）`
- `中立圏（Short寄り）`
- `Long やや優勢 / 明確優勢 / 強い優勢 / 非常に強い優勢`
- mirrored Short labels

Internal stable tokens remain lowercase English.

### 2. Confirmed turning evidence must outrank opposite early evidence

Current behavior classifies any evidence on both sides as `mixed / early`. This causes the 14:05 regression case to become mixed/early even though Short has confirmed flip/retest evidence and Long has only an early support-rejection warning.

Use exact-token deterministic precedence:

1. both sides have confirmed evidence -> `mixed / confirmed`
2. one side has confirmed evidence -> that side / `confirmed`, even if the opposite side has early evidence
3. no confirmed evidence and both sides have early evidence -> `mixed / early`
4. no confirmed evidence and one side has early evidence -> that side / `early`
5. no evidence -> `none / none`

Retain all exact matched `reason_codes`. Do not use substring matching.

Expected regression:

- 13:05: turning `long / confirmed`
- 14:05: turning `short / confirmed`, not mixed/early
- 15:05: turning `short / confirmed`

### 3. CSV strength semantics are incorrect

`structural_priority_strength` must record the stable `strength` token, not the human-readable `priority_label`.

Keep the existing columns. Do not rewrite historical rows. Missing structural output still writes blanks.

### 4. Bounded preview did not validate the side-aware execution layer

The committed preview summaries contain `side_aware_action: null`, and the 14:05 HTML does not contain `追いかけ禁止`. Therefore the reported preview did not prove that the structural meter coexists with the accepted 15M action lifecycle.

Regenerate the bounded local preview by recomputing in canonical order:

1. attach side-aware action using the bounded previous signal when required
2. attach structural priority
3. render the detail HTML

Required preview acceptance:

13:05 (`20260712_040500`):
- structural 47 / 53
- structural primary side empty
- structural strength `neutral`
- visible `中立圏（Short寄り）`
- turning `long / confirmed`
- side-aware Short `B_CHECK_15M / armed`
- tactical context primary side `short`
- alignment `neutral`

14:05 (`20260712_050500`, previous = 040500):
- structural 47 / 53
- structural strength `neutral`
- turning `short / confirmed`
- side-aware Short `B_CHECK_15M / late`
- HTML visibly contains `追いかけ禁止`
- tactical context primary side `short`
- alignment `neutral`

15:05 (`20260712_060500`, previous = 050500):
- structural 47 / 53
- structural strength `neutral`
- turning `short / confirmed`
- tactical scores remain 0 / 68
- side-aware output is present; do not require a specific lifecycle unless existing accepted logic deterministically supplies it
- alignment remains neutral inside the structural neutral band

The preview must not special-case signal IDs.

### 5. Canonical integration order must be proven

The production result must attach `side_aware_mtf_action` before `structural_priority`, so `structural_priority.tactical_context` is populated from the real execution action.

Add a focused integration test that exercises the canonical attachment order and proves:

- side-aware execution primary side and action class are present in `tactical_context`
- structural attachment does not overwrite tactical scores, bias, side-aware action, gates, or setup state

## Preserved formula and parameters

Do not change:

```text
net_4h = clamp((long_4h - short_4h) / 53, -1, 1)
net_1h = clamp((long_1h - short_1h) / 12, -1, 1)
weighted_net = 0.75 * net_4h + 0.25 * net_1h
long_points = round(clamp(50 + 40 * weighted_net, 10, 90))
short_points = 100 - long_points
```

Do not change any config parameter reviewed in the parent task.

## Allowed edit

- `src/analysis/structural_priority.py`
- `main.py` only if canonical attachment order is not already correct
- `src/storage/csv_logger.py`
- `src/notification/detail_page.py`
- `tests/test_structural_priority.py`
- `tests/test_structural_priority_integration.py`
- `tests/test_csv_logger_active_plan.py`
- `tests/test_notification_detail_page.py`
- this active spec, moved to archive after success
- `docs/operations/ai-orchestration/NEXT_ACTION.md`
- `docs/operations/ai-orchestration/P8_P9_ISSUE_REGISTER.md` for concise completion evidence

## Prohibited edit

- `src/analysis/scoring.py`
- `config.py`
- market-map generation
- Active Plan generation
- execution/opportunity/phase gates
- notification trigger or email sender
- deploy, launchd, runtime schedule
- API/account/order code
- frozen old runtime repo

## Validation

Run only:

```text
./.venv312/bin/python -m unittest tests.test_structural_priority tests.test_structural_priority_integration tests.test_csv_logger_active_plan tests.test_notification_detail_page
```

Regenerate bounded local previews only under:

```text
local/structural_priority_preview/
```

Do not commit preview output. Do not publish HTML, send mail, fetch market data, run the monitor, modify historical signals/CSV rows, or restart runtime.

Finally run:

```text
git diff --check
```

## Completion

Complete when:

- strength buckets are implemented and mirrored
- 14:05 confirmed Short turning outranks opposite early Long evidence
- CSV logs the stable strength token
- canonical attachment order is tested
- preview summaries contain non-null side-aware actions
- 14:05 HTML contains `追いかけ禁止`
- tactical scores and side-aware lifecycle remain unchanged
- targeted tests and diff check pass
- active spec is archived
- one local commit is created
- no push and no runtime apply occur

## Bounded completion record

- qualitative strength tokens: `insufficient`, `neutral`, `slight`, `clear`, `strong`, `very_strong`; Japanese labels are rendered for each mirrored side.
- turning precedence: confirmed evidence wins over opposite early evidence; both confirmed/early remain mixed with the corresponding strength.
- CSV `structural_priority_strength` now records the stable lowercase structural token.
- canonical previews regenerated in attachment order: side-aware action first, structural priority second, HTML last.
- 040500: 47/53, neutral, Long confirmed turning, Short armed/not_late.
- 050500: 47/53, neutral, Short confirmed turning, Short late/late_no_chase, visible `追いかけ禁止`.
- 060500: 47/53, neutral, Short confirmed turning, non-null side-aware action, tactical scores 0/68 retained.
- targeted tests: 59 passed; no production behavior changed.
