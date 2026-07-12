# Structural Priority Meter Rebalance — Active Specification

## Metadata

- work_id: `BTCFX-20260712-P8-STRUCTURAL-PRIORITY-METER-REBALANCE`
- status: human-approved for bounded audit and source implementation
- phase: P8 manual-trading observation improvement
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- branch: resolve from `git status --short --branch`; expected `Ver04-v2`
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## 1. Goal

Separate medium-term market priority from immediate 15-minute execution.

The top balance meter must answer:

```text
4H / 1Hを基準に、いまLongとShortのどちらを中期的に優先して見るか。
```

The existing side-aware action, entry zones, SL, TP1, TP2, lifecycle, and no-chase state must continue to answer:

```text
15分足で、いま確認・待機・実行検討・追いかけ禁止のどれか。
```

A fast tactical reversal must not turn a medium-term meter into false `0 / 100` certainty.

## 2. Confirmed audit finding

The current meter is mathematically correct for its old contract but unsuitable for human structural interpretation.

Current behavior:

```text
long_share = long_display_score / (long_display_score + short_display_score)
```

Therefore `0 / 68` becomes `0% / 100%`, even though `68` is not 100-percent certainty.

The underlying display scores also mix several ownership layers:

- 4H regime, EMA alignment, EMA slope, EMA50 position and structure,
- 1H structure,
- market-map role flips and failed breakouts,
- current support / resistance location,
- 15M signal, RSI, volume and breakout activity,
- RR, ATR, funding and range-center penalties.

The display transform clamps raw values at both ends:

```text
raw <= -30 -> display 0
raw >= 50  -> display 100
```

Recent rows repeatedly reach `0 / 100` or `100 / 0`. Correlated market-map facts can also stack in one cycle. This is acceptable as a responsive tactical score input, but not as the sole source of a broad human priority meter.

## 3. Parameter audit decision

Do not change production scoring, thresholds, gates or risk parameters in this task.

Reviewed execution/risk values are internally coherent enough to retain pending evidence-backed tuning:

- Long/Short bias gap thresholds: `8 / 9`
- confidence minimums: Long `45`, Short `55`
- attention score/gap: `55 / 15`
- minimum RR: `1.10`
- SL: `1.5 ATR`
- TP1 / TP2: `1R / 2R`
- acceptable ATR ratio: `0.25–2.4`
- volume trigger: `1.15`
- position-risk thresholds: `55 / 80`

The Long/Short confidence asymmetry is existing evidence-aware policy and is not changed here.

The immediate defect is display ownership and normalization, not a proven production scoring defect.

## 4. New ownership model

### 4.1 Top meter — structural priority

Use only stable 4H and 1H structural evidence.

Exclude from the top meter:

- 15M signal,
- RSI,
- MACD,
- volume,
- breakout execution activity,
- current entry-location penalties,
- RR, ATR and funding execution penalties,
- market-map turning/role-flip signals.

Turning signals remain visible as a separate alert overlay.

### 4.2 Side cards and action layer — tactical execution

Preserve existing tactical values and behavior:

- `long_display_score`
- `short_display_score`
- side-aware A/B/C/STOP action
- `armed / triggered / follow_through / late`
- entry zone / invalidation / SL / TP1 / TP2
- `追いかけ禁止`

Relabel the existing side-card score as `短期実行スコア` or equivalent so it is not confused with the structural meter.

## 5. Structural priority formula

Create a pure deterministic report-only module:

```text
src/analysis/structural_priority.py
```

Primary API:

```python
build_structural_priority(current: dict) -> dict
```

Schema:

```text
structural_priority.v1
```

### 5.1 4H evidence

Read exact factor codes from existing Long/Short score-factor breakdowns.

Long 4H codes and configured weights:

- `regime_uptrend`: 15
- `ema_alignment_bullish`: 12
- `ema20_slope_up`: 6
- `price_above_ema50_4h`: 6
- `structure_4h_hh_hl`: 14

Short mirror:

- `regime_downtrend`: 15
- `ema_alignment_bearish`: 12
- `ema20_slope_down`: 6
- `price_below_ema50_4h`: 6
- `structure_4h_lh_ll`: 14

Maximum directional 4H evidence per side: `53`.

### 5.2 1H evidence

- Long: `structure_1h_hh_hl`: 12
- Short: `structure_1h_lh_ll`: 12

Maximum directional 1H evidence per side: `12`.

### 5.3 Normalization

```text
net_4h = clamp((long_4h - short_4h) / 53, -1, 1)
net_1h = clamp((long_1h - short_1h) / 12, -1, 1)
weighted_net = 0.75 * net_4h + 0.25 * net_1h
long_points = round(clamp(50 + 40 * weighted_net, 10, 90))
short_points = 100 - long_points
```

This deliberately gives 4H primary ownership and 1H tactical context.

Expected fixtures:

- full 4H + 1H Long alignment: `90 / 10`
- full 4H + 1H Short alignment: `10 / 90`
- full 4H Long with 1H Short: approximately `70 / 30`
- neutral 4H with 1H Short: approximately `40 / 60`
- current partial 4H Long evidence with 1H Short: approximately `47 / 53`

Never emit `0 / 100` or `100 / 0` from the structural meter.

If no valid structural evidence exists, return `50 / 50` with `present=false` and an explicit insufficient/neutral label. Do not fall back to tactical display scores.

## 6. Turning / reversal overlay

Keep turning evidence separate from structural points.

Derive a deterministic display-only `turning_watch` from existing exact fields and flags.

Long examples:

- confirmed: `trend_flip_confirmed_up`, `resistance_to_support_confirmed`, `resistance_to_support_retest_confirmed`
- early: `trend_flip_early_up`, `failed_breakout_up_reversal`, `major_support_rejection`

Short examples:

- confirmed: `trend_flip_confirmed_down`, `support_to_resistance_confirmed`, `support_to_resistance_retest_confirmed`
- early: `trend_flip_early_down`, `failed_breakout_down_reversal`, `major_resistance_rejection`

Output:

- direction: `long | short | mixed | none`
- strength: `confirmed | early | none`
- reason_codes
- against_structural_priority: boolean

No arbitrary substring matching.

## 7. Structural / 15M alignment label

Derive a display-only alignment state using the new structural primary side and existing side-aware primary action:

- `aligned`: structural side and 15M action side agree
- `turning_candidate`: 15M action opposes structural side and confirmed turning evidence supports the 15M side
- `countertrend`: 15M action opposes structural side without confirmed turning support
- `neutral`: structural evidence or action side is unavailable

This is context, not entry permission.

## 8. Result integration

Attach the complete object after score-factor breakdown and side-aware action are available:

```text
result["structural_priority"]
```

Do not overwrite:

- bias,
- Long/Short display score,
- raw score,
- confidence,
- market-map output,
- side-aware action,
- setup state,
- gates,
- Active Plan,
- notification decision.

No additional market-data fetch.

## 9. Evidence logging

Append compact fields to future `logs/csv/trades.csv` rows:

- `structural_priority_long`
- `structural_priority_short`
- `structural_priority_side`
- `structural_priority_strength`
- `structural_turning_direction`
- `structural_turning_strength`
- `structural_alignment_state`

Existing rows remain unchanged. Missing output writes blank values.

## 10. Operator HTML

Replace the current top relative meter contract.

Required heading:

```text
4H / 1H STRUCTURAL PRIORITY
中期の優先方向
```

Required note:

```text
4時間足75%・1時間足25%。15分足の実行判断は下のアクション欄で確認します。
```

Display:

- structural Long/Short points and shares,
- qualitative priority label,
- turning-watch badge,
- structural/15M alignment label,
- center reference.

The top meter must use only `structural_priority`.

The side cards retain tactical scores, relabeled clearly as `短期実行スコア / 100`.

Entry zone, SL, TP and action hierarchy remain unchanged.

## 11. Quantitative balance audit before acceptance

Before source completion, run a bounded local audit over the most recent 336 valid signal rows, or all available recent rows when fewer exist.

Use only event-time fields. Do not use future outcomes.

Compare old and proposed meter behavior:

- count/rate of `0/100` or `100/0`,
- count/rate of shares outside `5/95`,
- median, p90 and maximum one-step Long-point change,
- direction-flip count,
- latest three signals,
- 13:05 / 14:05 / 15:05 regression sequence.

Write local, uncommitted outputs under:

```text
local/structural_priority_audit/
```

Acceptance:

- proposed saturation rate is zero,
- proposed maximum one-step movement is lower than the old relative meter,
- proposed direction-flip count is not greater than the old meter,
- 13:05–15:05 structural movement is bounded and does not jump to false 100-percent certainty,
- existing tactical scores and side-aware actions are unchanged.

If the fixed 75/25 formula fails these criteria, stop and report the exact evidence. Do not invent another weight without ChatGPT review.

## 12. Parameter audit report requirements

The compact report must classify reviewed numeric settings as:

- retained,
- display defect corrected,
- future evidence review only.

Do not mutate config values in this task.

## 13. Allowed files

Allowed edit:

- new `src/analysis/structural_priority.py`
- exact canonical result-integration point, expected `main.py`
- `src/storage/csv_logger.py`
- `src/notification/detail_page.py`
- new focused unit/integration tests
- narrowly matching existing CSV/detail-page tests
- this spec, moved to archive after successful completion
- `docs/operations/ai-orchestration/NEXT_ACTION.md`
- `docs/operations/ai-orchestration/P8_P9_ISSUE_REGISTER.md` for concise evidence

Do not edit:

- `src/analysis/scoring.py`
- `config.py`
- market-map generation
- execution/opportunity/phase gates
- notification trigger
- email sender
- deploy or launchd files
- API/account/order code
- frozen old runtime repo

## 14. Validation

Required targeted validation:

```text
./.venv312/bin/python -m unittest tests.test_structural_priority tests.test_structural_priority_integration tests.test_csv_logger_active_plan tests.test_notification_detail_page
```

Run one bounded render-only preview for:

- `logs/signals/20260712_040500.json`
- `logs/signals/20260712_050500.json`
- `logs/signals/20260712_060500.json` or `logs/last_result.json`

Preview output may be written only under:

```text
local/structural_priority_preview/
```

Do not publish, send mail, fetch market data, run the monitor, or modify historical logs.

Finally:

```text
git diff --check
```

## 15. Completion

Complete when:

- quantitative audit passes,
- structural meter is 4H/1H-owned,
- tactical score and 15M action remain separate,
- top meter cannot display false 0/100 certainty,
- turning warning and alignment are visible,
- future CSV rows contain evidence fields,
- targeted tests and bounded previews pass,
- active spec is archived,
- one local commit is created,
- no push and no runtime restart occur.

Runtime application is a separate controlled task after ChatGPT review.


## 16. Neutral band and qualitative labels

Points remain continuous, but the structural primary side must not flip on a narrow difference.

Use:

```text
45–55 inclusive: neutral structural band
Long >= 56: structural primary Long
Short >= 56: structural primary Short
```

Qualitative strength by winning-side points:

- `50–55`: neutral
- `56–64`: slight
- `65–74`: clear
- `75–84`: strong
- `85–90`: very_strong

The expected `47 / 53` regression sequence is therefore displayed as `中立圏（Short寄り）`, not as a confirmed structural Short flip.

The alignment state must be `neutral` while structural points remain inside the neutral band. Turning-watch and 15M action remain visible separately.

## 17. Bounded completion record

- numeric audit: pass over the latest 336 valid rows
- old tactical meter: 41/336 (12.20%) 0/100 saturation, p90 step 47.6, maximum step 88, direction flips 73
- structural meter: 0/336 saturation, p90 step 10, maximum step 18, direction flips 10
- 13:05, 14:05 and 15:05: structural Long 47 / Short 53, neutral / Short-leaning
- targeted tests: 55 passed
- bounded local previews: 040500, 050500 and 060500 passed; tactical scores remained unchanged
- no scoring, config, gate, market-map, notification, mail, runtime, launchd or order behavior changed
- status: completed by bounded validation; runtime application remains a separate task
