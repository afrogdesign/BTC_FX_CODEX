# Side-Aware Multi-Timeframe Operator Action — Active Specification

## Metadata

- work_id: `BTCFX-20260712-P8-SIDE-AWARE-MTF-OPERATOR-ACTION`
- status: human-approved for bounded source implementation
- phase: P8 manual-trading support improvement
- change_class: side-aware operator action routing + display hierarchy + evidence logging
- created_at: `2026-07-12`
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- branch: resolve from `git status --short --branch`; expected `Ver04-v2`
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## 1. Goal

Implement a deterministic operator-action layer that evaluates Long and Short independently and separates:

1. 4H structural context,
2. 1H tactical setup,
3. 15M execution state,
4. side-specific entry prohibition,
5. opposite-side manual opportunity.

The operator surface must be able to state, at the same time:

```text
LONG = STOP_OR_EXIT
SHORT = B_CHECK_15M / armed
```

without changing the existing formal bias, score, gate, notification trigger, mail-send behavior, or order behavior.

The purpose is to expose usable 15-minute opportunities that already exist in Active Plan data but are hidden by a dominant-side score or global STOP posture.

## 2. Observed regression case

Pinned source signal:

```text
20260712_040500
2026-07-12 13:05 JST
```

Observed source facts:

- displayed Long / Short score: `76 / 12`
- current price: approximately `64,200`
- `primary_setup_side = long`
- Long primary setup: `invalid`
- `active_limit_retest_long = allowed`
- `active_limit_retest_short = allowed`
- `active_countertrend_scalp_short = conditional`
- Short watch zone: approximately `64,114–64,272`
- Short TP1: approximately `63,880`
- 4H / 1H / 15M discrete signals were all `wait`
- the next hourly signal changed to Short only after price had already moved near `63,974`

Expected new interpretation for this pinned signal:

```text
4H context: WAIT / structural score still Long-heavy
1H tactical: WAIT with Short opportunity evidence
15M execution: Short armed, not yet confirmed
LONG action: STOP_OR_EXIT
SHORT action: B_CHECK_15M
primary operator action: SHORT B_CHECK_15M
entry permission: unchanged / human decides manually
```

The implementation must not special-case this signal ID.

## 3. Product doctrine

Use this ordering:

```text
Detect opportunity aggressively.
Execute selectively.
Invalidate quickly.
Do not chase.
```

Timeframe ownership:

| Timeframe | Role |
|---|---|
| 4H | structural context, major zones, holding horizon |
| 1H | tactical continuation / pullback / transition setup |
| 15M | armed / triggered / invalidated / late execution state |

Important rule:

```text
4H Long does not prohibit a tactical 15M Short.
4H Short does not prohibit a tactical 15M Long.
```

A counter-structural action must remain bounded by shorter holding expectations, earlier TP management, and explicit invalidation. It is never automatic entry permission.

## 4. Non-goals and hard boundaries

Do not modify:

- `compute_scores`
- `decide_bias`
- Long / Short display-score weights
- market-map classification
- `trade_execution_gate`
- `phase1b_lite_gate`
- `opportunity_gate`
- confidence thresholds
- notification trigger conditions
- mail sending
- runtime schedule
- launchd
- API endpoints
- account, order, or position endpoints
- `paper_positions.csv`
- automatic order behavior

Do not restart `com.afrog.btc-monitor`.
Do not run a manual production monitor cycle.
Do not edit or inspect the frozen old runtime repo.

## 5. New deterministic module

Create:

```text
src/analysis/side_aware_mtf_action.py
```

Primary API:

```python
evaluate_side_aware_mtf_action(current: dict, previous: dict | None = None) -> dict
```

Schema version:

```text
side_aware_mtf_action.v1
```

The function must be pure, deterministic, symmetric, and fail closed on malformed input.

## 6. Output contract

Minimum output:

```text
schema_version
present
signal_id
structural_context
  signals_4h
  long_display_score
  short_display_score
  bias
  market_regime
  phase

tactical_context
  signals_1h
  market_map_primary_state
  transition_direction
  trend_flip_state
  level_flip_state
  failed_breakout_state

execution_context
  signals_15m
  current_price
  primary_side
  primary_action_class
  primary_state
  headline
  next_condition
  chase_status
  reason_codes

long
  action_class
  state
  plan_support
  zone
  invalidation
  tp1
  tp2
  reason_codes

short
  action_class
  state
  plan_support
  zone
  invalidation
  tp1
  tp2
  reason_codes

safety_boundary
```

Allowed action classes:

- `A_FORMAL`
- `B_CHECK_15M`
- `C_WATCH_ZONE`
- `STOP_OR_EXIT`
- `NONE`

Allowed lifecycle states:

- `dormant`
- `watch`
- `armed`
- `triggered`
- `follow_through`
- `late`
- `invalidated`
- `expired`

Allowed chase status:

- `not_late`
- `late_no_chase`
- `tp1_reached_no_chase`
- `unknown`

## 7. Input ownership

Use existing result fields only. Do not add another market-data fetch.

Required sources, when present:

- `signal_id`
- `current_price`
- `bias`
- `signals_4h`
- `signals_1h`
- `signals_15m`
- `market_regime`
- `phase`
- `market_map_primary_state`
- `market_map_flags`
- `transition_direction`
- `trend_flip_state`
- `level_flip_state`
- `failed_breakout_state`
- `long_display_score`
- `short_display_score`
- `primary_setup_side`
- `primary_setup_status`
- `primary_setup_reason`
- `trade_execution_gate`
- `no_trade_flags`
- `risk_flags`
- `active_trade_plan`

The evaluator must accept `active_trade_plan` as a dict and also tolerate the existing serialized JSON representation when necessary.

## 8. Global-fatal versus side-specific blocking

Only global-fatal conditions may stop both sides.

Initial global-fatal set:

- invalid or missing data-quality state when the source explicitly reports failure
- `ATR_extreme`
- `Funding_prohibited`
- `Funding_prohibited_long` and `Funding_prohibited_short` only when both sides are prohibited

Side-specific examples:

```text
long_at_major_resistance_wait_only -> blocks or degrades Long only
short_at_major_support_wait_only -> blocks or degrades Short only
long thesis invalid -> does not automatically block Short
short thesis invalid -> does not automatically block Long
```

Informational flags such as breakout-watch or sweep-incomplete must remain visible but must not silently become global-fatal blockers.

## 9. Action-class rules

### 9.1 A_FORMAL

A side may be `A_FORMAL` only when the existing formal contract already permits it.

Minimum:

- `trade_execution_gate == pass`
- side matches the existing executable primary direction/setup
- no global-fatal condition

This module must never manufacture a new formal candidate.

### 9.2 B_CHECK_15M

A side may become `B_CHECK_15M` when:

1. no global-fatal condition exists,
2. an existing Active Plan side candidate is `allowed` or `conditional`, and
3. at least one independent activation group exists.

Activation groups:

- opposite thesis/setup is invalid or side-specifically stopped,
- mirrored market-map transition evidence supports this side,
- `signals_1h` or `signals_15m` supports this side,
- current price is in the existing side zone and the plan has a concrete next condition,
- previous snapshot shows the opposite thesis weakening while this side remains actionable.

`B_CHECK_15M` means “check the 15-minute chart now”. It does not mean entry permission.

### 9.3 C_WATCH_ZONE

Use `C_WATCH_ZONE` when an existing side plan and zone exist but activation evidence is insufficient for B.

### 9.4 STOP_OR_EXIT

Use side-specific `STOP_OR_EXIT` when:

- that side’s primary setup is invalid,
- that side’s own invalidation/stop has been crossed,
- that side has a side-specific wait-only blocker at the wrong location,
- the opposite side has a stronger actionable state and this side’s thesis is stressed or invalid.

A side-specific STOP must not erase a valid opposite-side B/C/A candidate.

## 10. Trigger-state rules

### armed

A side is `armed` when B conditions exist but neither 15M nor 1H confirms the side yet.

The pinned `20260712_040500` Short candidate must be `armed`, not `triggered`.

### triggered

A side is `triggered` when at least one deterministic trigger is present:

- `signals_15m` matches the side,
- current/previous price crosses the opposite thesis invalidation and does not immediately reclaim it,
- a plan-defined side zone is active together with matching 15M continuation evidence.

Do not infer candle patterns that are not already present in the source payload.

### follow_through

Use only when 1H and 15M both match the side and the action is not late.

### invalidated

Use when own stop/invalidation is crossed or 1H and 15M both align with the opposite side.

### late / no chase

Calculate progress from the side entry midpoint to TP1 when all values are available.

- progress below `0.70`: `not_late`
- progress from `0.70` to below `1.00`: `late_no_chase`
- progress at or above `1.00`: `tp1_reached_no_chase`

For Short:

```text
progress = (entry_mid - current_price) / (entry_mid - tp1)
```

For Long:

```text
progress = (current_price - entry_mid) / (tp1 - entry_mid)
```

Invalid or zero denominators produce `unknown`.

A late candidate may remain directionally valid but its headline must prohibit chasing.

## 11. Primary-action selection

Select one primary operator action without deleting the other side.

Priority:

1. `A_FORMAL`
2. `B_CHECK_15M` with `triggered` or `follow_through`
3. `B_CHECK_15M` with `armed`
4. `C_WATCH_ZONE`
5. side-specific `STOP_OR_EXIT`
6. `NONE`

When one side is STOP and the opposite side is B/A, the opposite side is primary.

Tie-breakers must be deterministic and symmetric. Use stronger lifecycle state, existing plan status, matching timeframe evidence, and then stable side ordering only as a final deterministic fallback.

## 12. Integration contract

Integrate the evaluator after the existing Active Plan is available in the normal result-building path.

Store the complete object at:

```text
result["side_aware_mtf_action"]
```

Do not overwrite:

- `bias`
- existing scores
- existing setup states
- existing gates
- existing Active Plan
- existing Big Chance artifact

If the current architecture has one canonical result-assembly function, integrate there. Codex may inspect `main.py` narrowly to locate this exact assembly point.

## 13. Evidence logging

Append the following columns to future `logs/csv/trades.csv` rows through the existing logger:

- `side_aware_primary_side`
- `side_aware_primary_class`
- `side_aware_primary_state`
- `side_aware_long_class`
- `side_aware_long_state`
- `side_aware_short_class`
- `side_aware_short_state`
- `side_aware_chase_status`
- `side_aware_reason_codes`

Existing rows remain untouched. Missing module output writes blank values, not fabricated defaults.

## 14. Operator HTML contract

Update the operator detail page so the top decision hierarchy becomes:

1. current operator action,
2. 15M execution state,
3. 1H tactical state,
4. 4H structural context,
5. side-specific Long and Short action cards,
6. existing relative score as secondary structural context.

Required visible examples:

```text
現在の行動: SHORT B｜15分足で戻り売り確認
15M: armed
1H: wait
4H: wait
LONG: STOP_OR_EXIT
SHORT: B_CHECK_15M
```

The existing Long/Short score panel must be relabeled as secondary structural context and must not be described as the final action.

Big Chance remains auxiliary. When it conflicts with the side-aware primary action or its side is invalidated, the page must visibly mark it as auxiliary/stale and must not let it become the hero decision.

Do not alter whether mail is sent or which signal triggers a mail.

## 15. Symmetry requirements

Every Short rule must have a mirrored Long rule.

Tests must include:

- pinned Long-stressed / Short-armed case,
- mirrored Short-stressed / Long-armed case,
- both sides C watch,
- formal A preserved,
- global-fatal both-side STOP,
- side-specific blocker does not suppress the opposite side,
- triggered and follow-through states,
- late-no-chase and TP1-reached-no-chase,
- malformed or missing Active Plan fail-closed behavior.

## 16. Allowed implementation files

Primary allowed files:

- new `src/analysis/side_aware_mtf_action.py`
- exact canonical result-assembly file, expected `main.py`
- `src/storage/csv_logger.py`
- `src/notification/detail_page.py`
- new `tests/test_side_aware_mtf_action.py`
- matching focused integration tests for result assembly, CSV logging, and detail-page rendering
- this spec, moved to archive after successful validation
- `docs/operations/ai-orchestration/P8_P9_ISSUE_REGISTER.md` only for concise completion evidence
- `docs/operations/ai-orchestration/NEXT_ACTION.md` only if posture changes after implementation

Nearby helpers may be read. Do not edit scoring, market-map, gates, trigger, email sender, runtime, deploy, or config files.

More than five changed files is explicitly authorized because this is one coherent source + evidence + UI theme.

## 17. Pinned acceptance assertions

Using explicit local source artifacts for signal `20260712_040500`, the evaluator must produce:

```text
long.action_class = STOP_OR_EXIT
short.action_class = B_CHECK_15M
short.state = armed
execution_context.primary_side = short
execution_context.primary_action_class = B_CHECK_15M
execution_context.chase_status = not_late
```

It must preserve:

```text
bias = long
long_display_score = 76
short_display_score = 12
trade_execution_gate = blocked
```

Using the subsequent signal around `20260712_050500`, the evaluator must identify Short direction as already late/no-chase when entry-mid-to-TP1 progress is at least 70 percent.

Generated preview files must remain under `local/` or `logs/` and must not be committed.

## 18. Validation

Minimum targeted validation:

```bash
./.venv312/bin/python -m unittest tests.test_side_aware_mtf_action
./.venv312/bin/python -m unittest <focused result-assembly integration test>
./.venv312/bin/python -m unittest <focused csv logger test>
./.venv312/bin/python -m unittest <focused detail page test>
```

Then run one bounded explicit-artifact preview for:

```text
logs/signals/20260712_040500.json
logs/signals/20260712_050500.json
```

The preview must not send mail, call an exchange API, restart runtime, or mutate source logs.

Finally:

```bash
git diff --check
```

Do not run the full unittest suite.

## 19. Completion criteria

Implementation is complete when:

- Long and Short are independently classified,
- the pinned case produces Long STOP + Short B armed,
- the subsequent moved case produces Short late/no-chase,
- mirrored Long behavior is tested,
- formal A semantics remain unchanged,
- existing scores, gates, notification triggers, mail behavior, runtime, and order behavior remain unchanged,
- future operator HTML makes the side-aware current action primary,
- future CSV rows contain compact evidence fields,
- targeted validation passes,
- active spec is archived,
- changes are committed locally,
- no push and no runtime restart occur.

## 20. Next phase after completion

Do not implement a 15-minute scheduler or additional mail notification in this task.

After this source implementation is reviewed, the next separate spec may evaluate a lightweight 15-minute state watcher that reuses cached 4H/1H context. That future work requires separate runtime and notification-boundary approval.
