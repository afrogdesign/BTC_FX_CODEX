# Side-Aware MTF Wait-Only Conditional Fix

## Metadata

- work_id: `BTCFX-20260712-P8-SIDE-AWARE-MTF-WAIT-ONLY-CONDITIONAL-FIX`
- status: active
- parent_commit: `5d23001`
- scope: one bounded wait-only degradation defect and regression tests
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## Review finding

Commit `5d23001` corrected lifecycle ordering and most wait-only behavior. One contract defect remains in `src/analysis/side_aware_mtf_action.py`.

Current behavior degrades a non-fresh-trigger wait-only side to `C_WATCH_ZONE` only when:

```text
counter_scalp_status != conditional
```

That exception is not part of the approved contract. A side with an exact wait-only blocker, no matching 15M signal, and no previous opposite-stop crossing must not remain `B_CHECK_15M` merely because its Active Plan counter-scalp status is `conditional`.

## Required behavior

For the exact named side:

- fresh trigger means matching `signals_15m` or previous opposite-side stop/invalidation crossing,
- without a fresh trigger:
  - if it is the current invalid/stressed primary side, keep `STOP_OR_EXIT`,
  - otherwise degrade any zone-only, transition-only, 1H-only, opposite-thesis-invalid, or conditional counter-scalp `B_CHECK_15M` to `C_WATCH_ZONE / watch`,
- with a fresh trigger:
  - `B_CHECK_15M` may remain,
  - matching 15M or previous crossing produces `triggered`,
  - matching 1H + 15M produces `follow_through`,
- retain `side_wait_only` in reason codes,
- never affect the opposite side.

Do not change the accepted real cases:

### 13:05

- Long `STOP_OR_EXIT`
- Short `B_CHECK_15M / armed`
- primary Short
- `not_late`

### 14:05

- Short `B_CHECK_15M / late`
- primary Short
- visible `追いかけ禁止`

## Allowed edits

- `src/analysis/side_aware_mtf_action.py`
- `tests/test_side_aware_mtf_action.py`
- this spec, moved to archive after validation
- `docs/operations/ai-orchestration/NEXT_ACTION.md`
- `docs/operations/ai-orchestration/P8_P9_ISSUE_REGISTER.md` for concise completion evidence

Do not edit scoring, market-map, gates, Active Plan generation, notification triggers, mail, runtime, deploy, config, launchd, or the frozen old repo.

## Tests

Add direct mirrored regression tests where:

1. the affected side is not the primary side,
2. the exact side-specific wait-only flag is present,
3. the side plan is inside its zone,
4. `counter_scalp_status = conditional`,
5. there is no matching 15M signal and no previous stop crossing,
6. expected result is `C_WATCH_ZONE / watch`, not `B_CHECK_15M`.

Also retain tests proving:

- matching 15M can remain `B_CHECK_15M / triggered`,
- previous opposite-stop crossing can remain `B_CHECK_15M / triggered`,
- 13:05 and 14:05 real-artifact acceptance remains unchanged.

## Validation

Run only:

```bash
./.venv312/bin/python -m unittest tests.test_side_aware_mtf_action tests.test_side_aware_mtf_action_integration
```

Run bounded previews for 13:05 and 14:05 only under `local/side_aware_mtf_preview/`.

Then:

```bash
git diff --check
```

No runtime restart, production monitor cycle, mail, market-data fetch, or existing-log mutation.
