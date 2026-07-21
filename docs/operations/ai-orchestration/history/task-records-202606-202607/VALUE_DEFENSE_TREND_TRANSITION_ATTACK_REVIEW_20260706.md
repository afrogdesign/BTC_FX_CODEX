# VALUE_DEFENSE_TREND_TRANSITION_ATTACK_REVIEW_20260706

## Purpose

トレンド転換期の Value Defense observation で、保守的な watch / TP 設計だけでは取り逃がす伸びを、次回以降の review / Phase4 候補に確実に残す。

This is a human-observed review note. It is not a trading signal, not a profitability claim, and not approval for Phase4 tuning.

## Human operator conclusion

- ユーザーの最重要目的は「勝てるトレード」である。
- 保守は重要だが、BTCでは取れる時に伸びを取り切る姿勢が必要。
- 微益で終わり、急変で損だけ大きくなる構造は、目的に反する。
- 必要なのは無根拠な攻めではなく、根拠と仕組みに基づいた攻め。
- “攻めの姿勢” は project objective の中核として扱う。

## Review sample

- Review timing: 2026-07-06 JST discussion
- Relevant observation context:
  - latest known notified observation before discussion: `20260705_220500`
  - later chart review showed strong upward continuation after the long-side read
- Human-visible market behavior:
  - BTC moved from a difficult trend-transition / range-compression area into strong upward extension.
  - The system directionally respected long better than older sensitive notification behavior.
  - However, the system still looked fragmented / local and did not fully express how far a higher-timeframe break could extend.

## What was good

- The newer system is less blindly sensitive than the old behavior.
- It is starting to recognize subtle zones and transition structure.
- In a difficult trend-turn area, the long-side read around the early phase was materially better than random or purely defensive behavior.
- Value Defense zones / shallow retest concepts are useful as entry-review anchors.

## What was insufficient

- Directional read was good, but upside extension was under-expressed.
- TP design appears too conservative for higher-timeframe reclaim / breakout-transition conditions.
- The system still reasons too much from local segments instead of integrating the 4H / 1H / 15m story.
- Short invalidation / no-short warning should be stronger when 1H reclaim and momentum expansion are present.
- A normal TP2 is not enough when the situation is no longer a normal local 15m trade.

## Core lesson

When BTC enters a transition from compression into higher-timeframe reclaim, the product must not only say:

```text
long is possible / watch shallow retest
```

It must also classify whether the setup is:

```text
ordinary local trade
or
trend-transition breakout with extension potential
```

If extension conditions are present, the manual surface should show an extension plan rather than treating TP2 as the final meaningful target.

## Required future review tags

Add these as human-review concepts before any Phase4 tuning:

- `trend_transition_candidate`
- `higher_timeframe_reclaim`
- `breakout_extension_candidate`
- `tp_too_conservative`
- `short_invalidated_by_reclaim`
- `runner_should_have_been_considered`
- `micro_profit_trap_risk`

## Extension-mode evidence checklist

For future observations, review whether these were present:

- 4H structure suggests downtrend exhaustion or reclaim.
- 1H closes reclaim EMA cluster / prior range ceiling.
- 15m forms shallow retest instead of deep rejection.
- RSI / MACD show acceleration rather than only mean reversion.
- Volume expands on the breakout or reclaim candle.
- Short-side setup becomes invalid before long-side target is exhausted.
- Price enters a thin / stop-run zone where short covering can accelerate movement.

## Desired future surface behavior

When extension-mode evidence is present, manual report should distinguish:

| Layer | Meaning |
|---|---|
| TP1 | near profit / risk reduction |
| TP2 | ordinary target, not necessarily final |
| Extension target | higher-timeframe continuation zone |
| Runner logic | keep partial exposure only while invalidation remains intact |
| Hard invalidation | point where the attack thesis is wrong |

This is not approval for automated trade execution. It is a review requirement for better human decision support.

## Attack principle

The product must preserve report-only safety, but safety must not become passivity.

```text
勝てる manual trading support system =
守るところは守る
ただし、BTCが取れる局面では、根拠ある攻めを明確に表示する
```

The target behavior is not reckless entry. The target behavior is evidence-backed aggression:

- avoid bad entries
- avoid overtrading
- avoid automatic orders
- but do not hide valid extension opportunities behind overly conservative TP framing

## Phase4 implication

Do not tune yet from a single example.

However, this sample should be preserved as a high-priority Phase4 review candidate once enough observations exist.

Potential later improvements:

- extension-mode classification
- higher-timeframe context summary
- stronger short invalidation wording after reclaim
- TP ladder that separates ordinary TP from extension target
- runner / partial-profit review wording for human manual judgment

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- no real trade instruction
- no scoring / gate tuning from this note alone
- no mail behavior change
- no runtime restart
- human decides manually
