# Side-Aware MTF Wait-Only and Priority Contract Fix

## Metadata

- work_id: `BTCFX-20260712-P8-SIDE-AWARE-MTF-WAIT-ONLY-PRIORITY-FIX`
- status: active
- parent_commits: `2e6cde5`, `eaa4733`, `114d07e`, `75b6413`
- scope: final contract correction for side-specific wait-only handling and B-candidate primary ordering
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## 1. Review findings

The real 13:05 and 14:05 previews now satisfy their pinned acceptance cases. Final source review found two remaining implementation mismatches against the approved specification.

### 1.1 Wait-only bypass

Current behavior can keep a side as `B_CHECK_15M` from zone-only activation even when that side has an exact side-specific `wait_only` blocker and no fresh trigger.

Also, when the blocked side is the current primary setup, the implementation stops it before checking a matching 15M trigger. This prevents the approved exception where a genuine matching 15M trigger or previous opposite-stop crossing may preserve `B_CHECK_15M` while keeping `side_wait_only` visible.

Required behavior:

- exact side-specific wait-only flag affects only its named side,
- without fresh trigger:
  - current invalid/stressed primary side -> `STOP_OR_EXIT`,
  - otherwise zone-only B -> `C_WATCH_ZONE`,
- with matching 15M trigger or previous opposite-stop crossing:
  - `B_CHECK_15M` may remain,
  - `side_wait_only` remains visible,
  - late/no-chase still applies.

### 1.2 B-candidate ordering mismatch

The approved order is:

1. fresh `follow_through`,
2. fresh `triggered`,
3. `late`,
4. `armed`,
5. `watch`.

Current state priority ranks `late` above `follow_through` and `triggered`. When a late candidate and a newly triggered opposite candidate have equal trigger strength, the late candidate may incorrectly remain primary.

Required behavior:

- genuine fresh follow-through outranks late,
- genuine fresh triggered outranks late,
- late outranks armed/watch,
- preserve the real 14:05 case where Short is late and Long is only armed.

## 2. Allowed edits

- `src/analysis/side_aware_mtf_action.py`
- `tests/test_side_aware_mtf_action.py`
- `tests/test_side_aware_mtf_action_integration.py` only if necessary
- this spec, moved to archive after validation
- `docs/operations/ai-orchestration/NEXT_ACTION.md`
- `docs/operations/ai-orchestration/P8_P9_ISSUE_REGISTER.md` for concise completion evidence

Do not edit scoring, market-map generation, existing gates, notification trigger, email sender, detail-page rendering, deploy, config, launchd, runtime, or the frozen old repo.

## 3. Required implementation

### 3.1 Fresh trigger definition

For wait-only exception and primary ranking, fresh trigger evidence is only:

- matching `signals_15m`,
- previous opposite-side stop/invalidation crossing,
- matching 1H + 15M follow-through.

Zone activation, semantic transition direction, and true opposite-thesis invalidation are arming evidence, not fresh trigger evidence.

### 3.2 Wait-only handling

For the exact named side:

- if `side_wait_only` and no fresh trigger:
  - if that side is the current invalid/stressed primary setup, return `STOP_OR_EXIT`,
  - otherwise any zone-only or directional-only `B_CHECK_15M` must degrade to `C_WATCH_ZONE` / `watch`,
- if `side_wait_only` and fresh trigger exists:
  - preserve `B_CHECK_15M`,
  - preserve `triggered` or `follow_through` lifecycle before late conversion,
  - include `side_wait_only` reason code.

The opposite side must remain independent.

### 3.3 Primary ordering

For the same action class `B_CHECK_15M`, apply:

- `follow_through` > `triggered` > `late` > `armed` > `watch`.

A late candidate may retain trigger evidence internally, but its lifecycle rank must not outrank a genuinely fresh triggered/follow-through opposite side.

Preserve:

- 13:05: Short armed is primary because Long is STOP,
- 14:05: Short late is primary because Long is only armed.

## 4. Required tests

Add direct tests that fail under the reviewed current implementation:

1. wait-only + zone-only + non-primary side -> `C_WATCH_ZONE`, not B,
2. wait-only + matching 15M trigger -> B triggered,
3. wait-only + previous opposite-stop crossing -> B triggered,
4. wait-only affects only the named side,
5. current invalid/stressed primary + wait-only + no fresh trigger -> STOP,
6. fresh triggered side outranks a genuinely late opposite B candidate with equal trigger strength,
7. fresh follow-through side outranks a genuinely late opposite B candidate,
8. mirrored Long and Short ordering,
9. 13:05 real artifact unchanged,
10. 14:05 real artifact unchanged with visible no-chase headline.

Tests must construct a true late opposite candidate rather than only asserting a triggered side in isolation.

## 5. Validation

Run only:

```bash
./.venv312/bin/python -m unittest tests.test_side_aware_mtf_action tests.test_side_aware_mtf_action_integration
```

Run bounded previews for:

- `logs/signals/20260712_040500.json`
- `logs/signals/20260712_050500.json` with 13:05 as previous

Write preview output only under `local/side_aware_mtf_preview/` and do not commit it.

Finally:

```bash
git diff --check
```

Do not run the monitor, fetch market data, send mail, modify source logs, or restart runtime.

## 6. Completion

- all direct contract tests pass,
- pinned previews remain accepted,
- active spec is archived,
- one local commit is created,
- no push,
- no runtime application.
