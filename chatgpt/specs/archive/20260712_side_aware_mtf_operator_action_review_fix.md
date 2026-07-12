# Side-Aware MTF Operator Action — Review Fix Specification

## Metadata

- work_id: `BTCFX-20260712-P8-SIDE-AWARE-MTF-OPERATOR-ACTION-REVIEW-FIX`
- parent_commit: `2e6cde5`
- status: review-fix approved
- scope: deterministic operator-action correction only
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## 1. Review finding

The pinned preview for `20260712_040500` is correct:

```text
Long = STOP_OR_EXIT
Short = B_CHECK_15M / armed
primary = Short
chase = not_late
```

The moved preview for `20260712_050500` exposes a directional regression:

```text
primary = LONG B_CHECK_15M
Short = STOP_OR_EXIT / invalidated
Short chase = late_no_chase
```

At that moved snapshot, market-map context is confirmed down and the previous Short opportunity has already consumed most of its entry-to-TP1 distance. The correct operator message is not a new Long opportunity. It is:

```text
Short direction remains the relevant completed/late move.
Do not chase.
Long must not be promoted solely because the current Short setup is invalid for confidence/readiness reasons.
```

## 2. Root causes to correct

1. `primary_setup_status=invalid` is treated as directional thesis invalidation even when `primary_setup_reason=confidence_below_min` or another execution/readiness reason.
2. Any invalid primary setup automatically activates the opposite side.
3. The specified activation group `inside existing side zone + concrete next_condition` is not implemented.
4. Directional values such as `up`, `down`, `early_down`, and `confirmed_down` are not normalized to Long/Short support.
5. JSON-list string flags are not normalized reliably.
6. Side-specific wait-only blockers are annotated but do not actually block or degrade their own side.
7. Previous-to-current crossing of the opposite side invalidation is not used as a deterministic trigger.

## 3. Required behavioral corrections

### 3.1 Distinguish setup readiness from thesis invalidation

Do not use generic `primary_setup_status=invalid` as sufficient opposite-side activation.

Execution/readiness reasons including the following are not directional thesis failures:

- `confidence_below_min`
- `setup_not_ready`
- `entry_zone_not_reached`
- `near_entry_zone_waiting_trigger`
- `rr_below_min`

They may stop or degrade that side as an entry candidate, but they must not automatically create a B candidate on the opposite side.

Opposite-thesis activation requires independent evidence such as:

- own stop/invalidation crossed,
- previous opposite stop crossed by current price,
- matching directional market-map/trend state,
- matching 1H or 15M signal,
- current price inside the side plan zone with a concrete `next_condition`.

### 3.2 Implement complete direction normalization

Normalize at least:

```text
long: long, buy, up, early_up, confirmed_up
short: short, sell, down, early_down, confirmed_down
```

Directional market-map/trend values must be usable as tactical support without changing the source fields.

### 3.3 Implement zone activation

When an existing side plan is `allowed` or `conditional`, current price is inside that plan zone, and `next_condition` is non-empty, the side may be `B_CHECK_15M / armed` even when discrete timeframe signals are `wait`.

This rule must preserve the pinned `20260712_040500` Short acceptance without relying on generic opposite-setup invalidation.

### 3.4 Previous invalidation crossing

Using `previous` and `current`:

- For Short, crossing below the previous Long stop/invalidation is a Short trigger candidate.
- For Long, crossing above the previous Short stop/invalidation is a Long trigger candidate.
- If entry-to-TP1 progress is at least `0.70`, retain directional relevance but set `state=late` and `chase_status=late_no_chase` or `tp1_reached_no_chase`.
- A late move must not be replaced by a new opposite-side B candidate without independent positive evidence for that opposite side.

### 3.5 Side-specific wait-only behavior

- `long_at_major_resistance_wait_only` blocks or degrades Long only.
- `short_at_major_support_wait_only` blocks or degrades Short only.
- These flags never become global fatal.
- The opposite side remains independently evaluable.

### 3.6 Flag parsing

Support:

- comma-separated strings,
- Python lists,
- JSON-list strings.

Normalization must be case-insensitive and strip brackets/quotes safely.

## 4. Acceptance assertions

### Pinned case

For current `logs/signals/20260712_040500.json`:

```text
long.action_class = STOP_OR_EXIT
short.action_class = B_CHECK_15M
short.state = armed
execution_context.primary_side = short
execution_context.primary_action_class = B_CHECK_15M
execution_context.chase_status = not_late
```

The Short reason codes must include zone/plan activation or equivalent independent evidence, not only generic opposite setup invalidity.

### Moved case

For current `logs/signals/20260712_050500.json` with previous `20260712_040500.json`:

```text
short.chase_status in {late_no_chase, tp1_reached_no_chase}
short.state = late
execution_context.primary_side = short
execution_context.primary_action_class = B_CHECK_15M
execution_context.primary_state = late
execution_context.chase_status in {late_no_chase, tp1_reached_no_chase}
```

Long must not be `B_CHECK_15M` solely because the Short setup has `primary_setup_status=invalid` with `primary_setup_reason=confidence_below_min`.

### Mirrored moved case

Create a mirrored deterministic fixture:

```text
Long move consumes at least 70 percent of entry-to-TP1 distance.
Short setup becomes invalid only for readiness/confidence.
```

Expected:

```text
primary_side = long
primary_action_class = B_CHECK_15M
primary_state = late
Long no-chase status retained
Short not promoted solely by Long readiness invalidity
```

### Boundary cases

Add tests for:

- JSON-list string flags,
- `early_down` and `confirmed_down` mapping to Short,
- `early_up` and `confirmed_up` mapping to Long,
- side-specific wait-only degradation,
- previous opposite-stop crossing,
- setup invalid due confidence does not imply opposite thesis invalid,
- pinned and moved real-artifact previews.

## 5. Allowed edits

- `src/analysis/side_aware_mtf_action.py`
- `tests/test_side_aware_mtf_action.py`
- `tests/test_side_aware_mtf_action_integration.py`
- narrowly matching detail-page test only if no-chase primary rendering requires a test correction
- this spec, moved to archive after completion
- `docs/operations/ai-orchestration/NEXT_ACTION.md` after successful completion
- `docs/operations/ai-orchestration/P8_P9_ISSUE_REGISTER.md` for concise fix evidence

Do not edit scoring, market-map, formal gates, notification trigger, mail sender, runtime, deploy, config, or frozen old runtime repo.

## 6. Validation

Run:

```bash
./.venv312/bin/python -m unittest tests.test_side_aware_mtf_action tests.test_side_aware_mtf_action_integration
```

Run the bounded previews again for:

```text
logs/signals/20260712_040500.json
logs/signals/20260712_050500.json with previous 040500
```

Write preview output only under `local/side_aware_mtf_preview/` and do not commit it.

Then:

```bash
git diff --check
```

Do not run the full suite. Do not restart runtime. Do not send mail. Do not fetch new market data.
