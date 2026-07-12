# Side-Aware MTF Trigger Priority Final Fix

## Metadata

- work_id: `BTCFX-20260712-P8-SIDE-AWARE-MTF-TRIGGER-PRIORITY-FINAL-FIX`
- status: active
- parent_commits: `2e6cde5`, `eaa4733`, `114d07e`
- scope: final deterministic lifecycle and primary-selection correction
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## 1. Review finding

The pinned 13:05 and moved 14:05 previews now satisfy their direct acceptance cases, and exact semantic direction matching plus visible no-chase wording are present.

A final source review found three contract gaps:

1. A genuine `triggered` candidate can still lose to an opposite `late` candidate when both have the same current `trigger_strength`, because `late` has the higher state rank.
2. `previous_opposite_stop_crossed` is defined as trigger evidence but currently leaves a non-late candidate in `armed` unless `signals_15m` also matches.
3. A true directional thesis invalidation is computed but is not itself included in activation after readiness-only invalid reasons were separated.

A side-specific wait-only blocker must also degrade only its own side and must not be bypassed merely because that side is not the current primary setup. An explicit invalidation cross or matching 15M trigger may override the wait-only posture, while a zone-only activation may not.

## 2. Goal

Complete the lifecycle and primary-selection contract without changing scoring, market-map generation, formal gates, notification triggers, mail behavior, runtime, or order behavior.

## 3. Required behavior

### 3.1 Fresh trigger classification

Create an explicit deterministic fresh-trigger signal for each side.

Fresh trigger evidence includes:

- matching `signals_15m`,
- previous opposite-side invalidation/stop crossed by current price,
- matching 1H and 15M follow-through.

A transition or market-map directional state may arm a candidate, but by itself is not a fresh 15M trigger.

Lifecycle:

- 1H + 15M match: `follow_through`
- 15M match: `triggered`
- previous opposite stop crossed: `triggered`
- directional/zone evidence without fresh trigger: `armed`
- progress at or above 0.70 converts an otherwise actionable side to `late`

Keep a separate internal rank or field that remembers whether a late action came from a fresh trigger or only older directional support.

### 3.2 Primary selection

Within `B_CHECK_15M`:

1. fresh `follow_through`
2. fresh `triggered`
3. `late`
4. `armed`
5. `watch`

A genuine fresh opposite trigger must outrank a merely late side.

Preserve the accepted 14:05 artifact where:

- Short is `late`,
- Long is only zone/directional `armed`,
- Short remains primary.

Mirror the behavior for Long and Short.

### 3.3 True thesis invalidation

Readiness-only reasons must not activate the opposite side:

- `confidence_below_min`
- `setup_not_ready`
- `entry_zone_not_reached`
- `near_entry_zone_waiting_trigger`
- `rr_below_min`

A true directional invalidation reason, such as an explicit thesis invalidation/expiry that is not readiness-only, may activate the supported opposite side as `B_CHECK_15M / armed`.

Use a clear reason code such as `opposite_thesis_invalid`.

### 3.4 Side-specific wait-only

Evaluate exact flag tokens independently:

- `long_at_major_resistance_wait_only`
- `long_at_major_support_wait_only`
- `short_at_major_resistance_wait_only`
- `short_at_major_support_wait_only`

A wait-only blocker affects only the named side.

Without fresh trigger or explicit opposite-stop crossing:

- zone-only B activation must be degraded to `C_WATCH_ZONE`, or
- the side may be `STOP_OR_EXIT` when it is the currently invalid/stressed primary thesis.

With matching 15M trigger or explicit opposite-stop crossing:

- the side may remain `B_CHECK_15M`,
- retain `side_wait_only` as a visible warning,
- late/no-chase rules still apply.

## 4. Acceptance

### Pinned 13:05

Using `logs/signals/20260712_040500.json`:

- Long = `STOP_OR_EXIT`
- Short = `B_CHECK_15M`
- Short state = `armed`
- primary side = `short`
- chase = `not_late`

### Moved 14:05

Using `logs/signals/20260712_050500.json` with 13:05 as previous:

- Short = `B_CHECK_15M`
- Short state = `late`
- primary side = `short`
- chase is `late_no_chase` or `tp1_reached_no_chase`
- headline contains `追いかけ禁止`

### Fresh-trigger priority

Construct mirrored synthetic cases where:

- one side is late from older transition/zone support,
- the opposite side gets a new matching 15M trigger.

The newly triggered side must be primary.

Repeat with 1H + 15M follow-through.

### Previous-cross lifecycle

Construct non-late mirrored cases where current price crosses the previous opposite stop.

The supported side must be:

- `B_CHECK_15M`
- `triggered`
- fresh-trigger ranked

### Thesis invalidation

- readiness-only invalidity does not activate the opposite side,
- true thesis invalidation does activate a supported opposite side as armed.

### Wait-only

- zone-only activation plus own-side wait-only does not remain B,
- matching 15M trigger or previous opposite-stop crossing may override to B,
- the opposite side is unaffected.

## 5. Allowed edits

- `src/analysis/side_aware_mtf_action.py`
- `tests/test_side_aware_mtf_action.py`
- `tests/test_side_aware_mtf_action_integration.py` only if necessary
- this spec, moved to archive after validation
- `docs/operations/ai-orchestration/NEXT_ACTION.md`
- `docs/operations/ai-orchestration/P8_P9_ISSUE_REGISTER.md` for concise completion evidence only

Do not edit UI, scoring, market-map generation, gates, trigger, mail sender, deploy, config, launchd, runtime, or the frozen old repo.

## 6. Validation

Run only:

```bash
./.venv312/bin/python -m unittest tests.test_side_aware_mtf_action tests.test_side_aware_mtf_action_integration
```

Run bounded previews for 13:05 and 14:05 under `local/side_aware_mtf_preview/`.

Do not run the monitor, send mail, fetch market data, or modify existing logs.

Finally:

```bash
git diff --check
```

## 7. Completion

- all acceptance cases pass,
- active spec moves to archive,
- one local commit is created,
- no push,
- no runtime restart.
