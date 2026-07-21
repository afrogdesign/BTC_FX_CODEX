# NEXT_ACTION

- current_work_id: `BTCFX-20260721-P8-ACTUAL-EXPORT-INPUT`
- mode: `HUMAN_CHECK`
- branch: `Ver04-v3` documentation line; confirm from local git before the next Codex task
- active_spec: none
- status: blocked pending local private input
- push: none

## Current action

Place one complete MEXC futures export batch under the ignored canonical directory:

```text
local/manual_trade_imports/YYYYMMDD/
```

The batch must contain `.xlsx` files matching all three categories:

- Trade History
- Order History
- Position History

Raw exchange exports must remain local and uncommitted.

## Why this is required

The accepted importer, episode builder, signal linker, and P8 actual-evidence route already exist and have matching test coverage. Current inspection found no canonical raw input directory and no generated actual-trade, episode, or signal-link CSVs. Consequently eligible actual-backed evidence is 0.

Codex must not fabricate, download, infer, or synthesize private exchange history.

## Next Codex task after input exists

Run one bounded operations task in the primary repo:

1. confirm the complete three-category batch without printing raw rows or private paths
2. run `import-manual-actual-trades` with `--dry-run --conflict-policy reject --stdout-json`
3. stop on any missing category, schema error, row rejection requiring judgment, or corrected-export conflict
4. only after a clean dry-run, run the canonical importer and generate:
   - `logs/csv/manual_actual_trades.csv`
   - `logs/csv/manual_actual_orders.csv`
   - `logs/csv/manual_actual_positions.csv`
5. build `logs/csv/manual_trade_episodes.csv`
6. build `logs/csv/manual_trade_signal_links.csv`
7. report compact aggregate counts only; do not commit generated CSVs or raw exports
8. return to ChatGPT before any P8 replay or production conclusion

## Safety

- report-only
- no private/account/order endpoints
- no API keys or secrets
- no raw exchange export commit
- no generated actual CSV commit
- no automatic order
- no classifier, score, gate, threshold, notification, mail, runtime, schedule, or phase-promotion change
- no `paper_positions.csv` integration
- frozen runtime repo remains out of scope
