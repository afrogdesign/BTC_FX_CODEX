# Anonymized output sample

This sample shows the intended shape and tone of BTC FX CODEX output without exposing private logs, credentials, account identifiers, or live operational data.

The values below are synthetic and for documentation only.

## Example notification summary

```text
[BTC FX CODEX / Ver03-v4]
Status: observation
Symbol: BTCUSDT
Timeframe focus: 4H / 1H / 15M
Market bias: neutral-to-watch
Confidence: 58 / 100
Signal tier: watch

Summary:
BTC is consolidating near a previously observed range boundary. Momentum is not strong enough for a ready signal. Liquidity is visible above and below the current range, so the system classifies the current state as observation rather than action.

Key observations:
- 4H trend: mixed
- 1H structure: range
- 15M trigger: not confirmed
- Funding: neutral
- Position risk: medium
- RR quality: not sufficient for ready classification

Operational note:
No trading instruction is generated. This output is for review and learning only.
```

## Example JSON-like payload

```json
{
  "system_label": "Ver03-v4",
  "symbol": "BTCUSDT",
  "status": "observation",
  "market_bias": "neutral-to-watch",
  "confidence": 58,
  "signal_tier": "watch",
  "position_risk": "medium",
  "risk_note": "Synthetic example. Not financial advice.",
  "checks": {
    "trend_structure": "mixed",
    "trigger_confirmed": false,
    "rr_sufficient": false,
    "funding_extreme": false
  },
  "actionability": {
    "ready": false,
    "reason": "Trigger and RR quality are not sufficient."
  }
}
```

## Intended wording standard

Use wording such as:

- analysis
- reference information
- observation
- review candidate
- paper / simulated when applicable

Avoid wording such as:

- guaranteed entry
- must buy / must sell
- profit confirmed
- automatic trade recommendation
- safe trade

## Privacy standard

Public samples should never include:

- API keys
- SMTP settings
- email addresses
- private account identifiers
- raw operational logs
- server paths or hostnames
- live position details
