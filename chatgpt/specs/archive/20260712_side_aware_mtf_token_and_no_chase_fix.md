# Side-Aware MTF Token Matching and No-Chase Display Fix

## Metadata

- work_id: `BTCFX-20260712-P8-SIDE-AWARE-MTF-TOKEN-NO-CHASE-FIX`
- status: active
- parent_commits: `2e6cde5`, `eaa4733`
- scope: deterministic direction normalization, primary selection safety, no-chase operator wording
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## 1. Review finding

The corrected 13:05 and 14:05 previews now preserve Short as the primary direction. A final source review found two remaining defects that must be fixed before runtime application:

1. `_matches_side()` uses raw substring matching for short tokens such as `up`. This can treat `support_to_resistance_confirmed` as Long evidence because the word `support` contains the substring `up`.
2. A late candidate exposes `chase_status=late_no_chase`, but the primary headline and detail-page hero do not explicitly say that chasing is prohibited.

A related selection guard is required: a genuinely triggered or follow-through opposite side must not always lose to a merely late candidate. Late should outrank only unsupported or weaker zone-watch/armed alternatives, not a real opposite trigger.

## 2. Goal

Make direction matching token-safe and semantic, make no-chase visible in the primary operator action, and preserve deterministic side-aware selection without changing scores, gates, notification triggers, mail behavior, runtime, or order behavior.

## 3. Allowed edits

- `src/analysis/side_aware_mtf_action.py`
- `src/notification/detail_page.py`
- `tests/test_side_aware_mtf_action.py`
- `tests/test_notification_detail_page.py`
- this active spec, moved to archive after validation
- `docs/operations/ai-orchestration/NEXT_ACTION.md`
- `docs/operations/ai-orchestration/P8_P9_ISSUE_REGISTER.md` for concise completion evidence only

Do not edit scoring, market-map generation, existing gates, notification trigger, email sender, deploy, config, launchd, runtime, or the frozen old repo.

## 4. Direction normalization contract

Do not use unrestricted substring matching.

Direct directional values are exact normalized tokens:

Long:

- `long`
- `buy`
- `up`
- `early_up`
- `confirmed_up`

Short:

- `short`
- `sell`
- `down`
- `early_down`
- `confirmed_down`

Recognize explicit semantic state/flag mappings without substring inference.

Long examples:

- `resistance_to_support_flip`
- `resistance_to_support_confirmed`
- `resistance_to_support_retest_confirmed`
- `trend_flip_early_up`
- `trend_flip_confirmed_up`
- `failed_breakout_up_reversal`
- `major_support_rejection`

Short examples:

- `support_to_resistance_flip`
- `support_to_resistance_confirmed`
- `support_to_resistance_retest_confirmed`
- `trend_flip_early_down`
- `trend_flip_confirmed_down`
- `failed_breakout_down_reversal`
- `major_resistance_rejection`

The exact token `support_to_resistance_confirmed` must not count as Long evidence merely because it contains the letters `up`.

Flag parsing must continue to support Python lists, comma-separated strings, pipe-separated strings, and JSON-list strings.

## 5. Side-specific wait-only matching

Match side-specific wait-only blockers by individual normalized flag token, not by combining substrings across the joined flag set.

Examples:

- `long_at_major_resistance_wait_only` affects Long only.
- `short_at_major_support_wait_only` affects Short only.

No unrelated `wait_only` token may combine with another flag to create a false blocker.

## 6. No-chase presentation

When primary `chase_status` is:

- `late_no_chase`
- `tp1_reached_no_chase`

then:

- execution headline must explicitly contain a no-chase statement,
- the detail-page hero must visibly show `追いかけ禁止`,
- directional validity may remain visible,
- no entry permission is created.

Expected moved-case headline meaning:

```text
SHORT B_CHECK_15M / LATE / 追いかけ禁止
```

Exact punctuation may vary, but the Japanese no-chase wording must be visible.

## 7. Primary selection guard

Within the same action class:

- `follow_through` and `triggered` with matching 15M/1H or explicit invalidation-cross evidence outrank a merely `late` candidate on the opposite side.
- `late` outranks only weaker `armed`, `watch`, or unsupported opposite candidates.
- preserve the accepted 14:05 result where Short is late and Long is only zone-armed.
- mirrored behavior is required.

Do not add score thresholds or signal-ID special cases.

## 8. Acceptance

### 13:05 pinned case

Using `logs/signals/20260712_040500.json`:

- Long: `STOP_OR_EXIT`
- Short: `B_CHECK_15M`
- Short state: `armed`
- primary side: `short`
- chase: `not_late`

### 14:05 moved case

Using `logs/signals/20260712_050500.json` with 13:05 as previous:

- Short: `B_CHECK_15M`
- Short state: `late`
- primary side: `short`
- chase: `late_no_chase` or `tp1_reached_no_chase`
- primary headline visibly prohibits chasing
- detail-page hero visibly contains `追いかけ禁止`

### False substring case

With all genuine Long evidence removed and only `support_to_resistance_confirmed` present:

- Long must not receive timeframe/transition activation.
- Short may receive explicit semantic Short evidence.

### Primary selection case

When one side is late and the opposite side has genuine matching 15M trigger or follow-through evidence:

- the genuinely triggered/follow-through side must become primary.

Mirror the case for the opposite direction.

## 9. Validation

Run only:

```bash
./.venv312/bin/python -m unittest tests.test_side_aware_mtf_action tests.test_side_aware_mtf_action_integration tests.test_notification_detail_page
```

Run bounded previews for 13:05 and 14:05 only under `local/side_aware_mtf_preview/`.

Do not run the monitor, send mail, fetch new market data, modify existing logs, or restart runtime.

Finally:

```bash
git diff --check
```

## 10. Completion

- tests pass,
- previews satisfy acceptance,
- active spec is archived,
- one local commit is created,
- no push,
- no runtime restart.
