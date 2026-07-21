# MANUAL_SURFACE_QUALITY_BACKLOG

## Purpose

report-only evidence improvements を manual trading surface に載せる優先順をまとめる。

## Evidence basis

- MCP-primary repo is the current source of truth
- no_ohlcv coverage は reviewed reports の全てで 91%超
- valid sample denominator は `rows excluding outcome == no_ohlcv`
- report-only win-like / loss-like / unresolved counts を分けて扱える
- entry-reached resolved / unresolved breakdown を分けて扱える
- candidate_type / side / active_primary_action breakdown を分けて扱える
- major-turn review counts は `potential_fakeout` / `potential_missed_turn` / `bad_entry_timing`
- no profitability claim is made

## Manual surface backlog

| Priority | Surface item | Why it matters | Safe display / action | Stop condition |
|---:|---|---|---|---|
| 1 | no_ohlcv coverage / valid sample denominator | 分母が見えないと解釈が崩れる | valid sample と no_ohlcv を同じ画面で表示する | 分母表示が安定したら止める |
| 2 | report-only win-like / loss-like / unresolved counts | win-rate の前提を明示する | win-like / loss-like / unresolved を並べる | 3 区分が固定表示されたら止める |
| 3 | entry-reached resolved / unresolved breakdown | entry 後の状態が見える必要がある | resolved / unresolved を分けて表示する | 内訳が固定表示されたら止める |
| 4 | candidate_type / side / active_primary_action breakdown | どの軸で偏りがあるか見たい | 3 軸 breakdown を report-only で表示する | 3 軸の見え方が揃ったら止める |
| 5 | major-turn review counts | human review の入口を明確にする | `potential_fakeout` / `potential_missed_turn` / `bad_entry_timing` を表示する | 3 件数が見えるようになったら止める |

## Priority order

1. `no_ohlcv` coverage / valid sample denominator
2. report-only win-like / loss-like / unresolved counts
3. entry-reached resolved / unresolved breakdown
4. candidate_type / side / active_primary_action breakdown
5. major-turn review counts

## Next implementation recommendation

- `BTCFX-20260630-MANUAL-SURFACE-EVIDENCE-SUMMARY`
- Goal: expose the evidence-quality summaries on the manual trading surface without changing trading logic.

## Safety boundary

- report-only / not FORMAL_GO / no automatic order / human decides manually
- trading logic unchanged
- no private/account/order endpoint

## Out of scope

- no trading logic change
- no auto order
- no private/account/order endpoint
- no notification sending
- no runtime action
- no generated file commit
- no source edit
- no test edit
- no profitability claim
- no old runtime repo access
