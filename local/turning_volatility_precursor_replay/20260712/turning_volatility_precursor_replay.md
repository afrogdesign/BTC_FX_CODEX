# Turning / Volatility Precursor Replay

## Executive result
continue_shadow_collection

## Current baseline versus policies
{"POLICY_COMBINED_PRECURSOR": {"clean_directional_precision": 0.475962, "false_precursor_rate": 0.052885, "matching_large_moves": 198, "median_lead_minutes": 27969.993000000002, "opposite_move_rate": 0.454327, "precursor_episodes": 417, "resolved_episodes": 416, "unresolved_rate": 0.002398, "whipsaw_rate": 0.016827}, "POLICY_CURRENT_NOTIFICATION": {"clean_directional_precision": 0.561508, "false_precursor_rate": 0.027778, "matching_large_moves": 283, "median_lead_minutes": 79449.993, "opposite_move_rate": 0.396825, "precursor_episodes": 505, "resolved_episodes": 504, "unresolved_rate": 0.00198, "whipsaw_rate": 0.013889}, "POLICY_FAILED_FLIP_GUARD": {"clean_directional_precision": 0.435028, "false_precursor_rate": 0.067797, "matching_large_moves": 77, "median_lead_minutes": 24009.986, "opposite_move_rate": 0.474576, "precursor_episodes": 178, "resolved_episodes": 177, "unresolved_rate": 0.005618, "whipsaw_rate": 0.022599}, "POLICY_LEVEL_REJECTION": {"clean_directional_precision": 0.4689, "false_precursor_rate": 0.057416, "matching_large_moves": 98, "median_lead_minutes": 26619.991, "opposite_move_rate": 0.454545, "precursor_episodes": 210, "resolved_episodes": 209, "unresolved_rate": 0.004762, "whipsaw_rate": 0.019139}, "POLICY_THESIS_STRESS": {"clean_directional_precision": 0.475962, "false_precursor_rate": 0.052885, "matching_large_moves": 198, "median_lead_minutes": 27969.993000000002, "opposite_move_rate": 0.454327, "precursor_episodes": 417, "resolved_episodes": 416, "unresolved_rate": 0.002398, "whipsaw_rate": 0.016827}}

## Long / Short split
{"BOTH": {"episodes": 0, "resolved": 0}, "DOWN": {"episodes": 613, "resolved": 613}, "UP": {"episodes": 1114, "resolved": 1109}}

## Regime / phase split
{"phase": {"breakout": 87, "pullback": 249, "range": 1114, "reversal_risk": 275, "trend_following": 2}, "regime": {"downtrend": 260, "range": 774, "transition": 638, "uptrend": 52, "volatile": 3}}

## Pinned 07:05 case
{"signal_id": "20260711_220501", "status": "caught_before_move"}

## Data limitations
Proxy OHLCV only; unresolved and whipsaw rows are excluded from clean directional precision.

## Recommendation status
continue_shadow_collection

## Safety boundary
report-only / not FORMAL_GO / no automatic order / human decides manually
No production scoring, market-map, gate, notification, mail, runtime, API, account, or order behavior changed.
