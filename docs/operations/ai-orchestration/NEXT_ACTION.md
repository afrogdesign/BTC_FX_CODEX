# NEXT_ACTION

- current_work_id: `M-ENTRY1`
- mode: `BOUNDED_CODEX`
- branch: `Ver04-v4`
- accepted_checkpoint: `e06fb99`
- active_spec: `chatgpt/specs/active/20260722_macro_structure_fixed_latest_entry.md`
- canonical_plan: `docs/operations/strategy/MACRO_VISUAL_STRUCTURE_PRODUCT_PLAN_20260722.md`
- status: implementation complete; ChatGPT review next
- push: none

## Current action

Review the M-ENTRY1 fixed latest HTML entry implementation.

```text
complete immutable operator artifact
→ validate all M-VIS1 / M-LINE1 / M-EVENT1 / M-HYP1 sections
→ add deterministic fixed-entry banner
→ atomic replacement of <output_root>/latest.html
→ explicit unavailable page on failed 4H attempts
```

## Fixed contract

The complete observable contract is in:

- `chatgpt/specs/active/20260722_macro_structure_fixed_latest_entry.md`

Key decisions:

- default fixed path: `local/reports/macro_structure/operator/latest.html`
- fixed entry is a regular self-contained UTF-8 HTML file
- no JavaScript fetch, iframe, redirect, external asset, or symlink
- success is published only from the complete HTML created by the same render
- available banner exposes entry ID, source artifact ID, source digest, cutoff, evaluation, freshness, continuity, and safety
- fixed entry availability does not imply current market freshness
- invalid 4H attempts preserve immutable evidence and existing operator `latest.json`
- invalid 4H attempts publish an explicit unavailable page when possible
- previous success is labeled historical only
- fixed-file replacement is atomic
- operator artifact schema, digest, and artifact ID remain unchanged
- no-4H callers do not create or update the fixed entry

## User-visible acceptance

- `open <output_root>/latest.html` opens one complete screen
- 4H chart, horizontal zones, diagonal evidence, structural events, scenarios, and supplemental 15m view remain
- scenario condition, next confirmation, and invalidation remain readable
- failure is visibly unavailable rather than an old page presented as current success
- previous valid artifact may be linked only as historical evidence
- report-only, no automatic order, and human-decides-manually remain visible

## Validation budget

- matching unittest
- one bounded direct-renderer smoke using existing local inputs
- one fixed-entry inspection
- task-scoped `git diff --check`

Do not run full suite, full replay, network fetches, repeated health cycles, runtime service, background processes, or parameter searches.

## Explicitly excluded

- runtime or schedule changes
- mail or notification changes
- local web server or hosting
- automatic browser launch during normal render
- analytical model changes
- probability, Entry / SL / TP, or automatic order
- private/account/order data

## Transition

After implementation, ChatGPT reviews changed source, focused tests, fixed `latest.html`, immutable identity preservation, scope, and safety. Acceptance completes visual Product v1 except separately authorized M-DELIVERY1.
