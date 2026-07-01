# Ver04-v1 Self-Improvement Loop Final Design

## Metadata

- repo: `afrogdesign/BTC_FX_CODEX`
- working_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- created_at: `2026-07-02`
- status: final design draft for user-reviewed product direction
- prior_baseline: `Ver03-v4`
- retained companion definition: `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

## 1. Purpose

この設計図は、実際の取引履歴インポートが2週間に1回程度しかできない前提で、BTCFX Ver04-v1 の自己改善ループを最終設計する。

目的は、自動売買ではない。

目的は、notification mail を受け取った人間が15分足を確認し、攻めの姿勢で勝てる実用的な manual trading support system を作ること。

ここでいう「15分足で人間が勝てる」の詳細定義は、 companion definition `VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md` を正本とする。

## 2. Core product direction

Ver04-v1 の次の方向性は次の通り。

```text
守りすぎる通知から、攻めるためのレーダーへ変更する。

ただし、long / short の両方を常に検出する。
現在の regime に合わせて優先方向だけ変える。

entry は人間が15分足で判断する。
turning point risk が高いときだけ強制ブレーキをかける。

この設計は report-only / human-decided の範囲に留める。
```

## 3. System layers

実取引履歴は最重要の ground truth だが、頻繁には取得できない。そのため、自己改善ループは3層に分ける。

```text
Layer 1: Daily Proxy Loop
  毎日自動で回る。実取引CSVなしで改善候補を出す。

Layer 2: Weekly Review Loop
  週次で傾向をまとめる。攻め/守り/転換のズレを確認する。

Layer 3: Biweekly Ground Truth Loop
  2週間に1回の実取引Excelインポートで、実損益ベースに補正する。
```

## 4. Daily Proxy Loop

毎日自動で回る主系。

Inputs:

- notification logs
- `user_reviews.csv`
- `signal_outcomes.csv`
- `active_plan_candidate_outcomes.csv`
- `active_plan_candidate_intraperiod_outcomes.csv`
- `shadow_log.csv`
- optional `manual_15m_judgments.csv`
- daily reports

Outputs:

- daily mail usefulness estimate
- direction correctness estimate
- aggressive short / long candidate proxy score
- over-suppression candidate count
- turning point risk candidate count
- top improvement candidates
- AI post-review health

Daily loop は実損益を確定しない。あくまで proxy である。

Daily loop で許可する改善提案:

- subject wording candidate
- label split candidate
- `NO_TRADE` to `WATCH` candidate
- `ENTRY_OK` to `CHECK_15M_ENTRY` candidate
- turning risk warning candidate
- long / short opportunity display candidate

Daily loop で許可しないこと:

- automatic trading
- threshold auto-mutation
- notification send behavior change
- runtime restart
- private/order endpoint
- profitability claim

## 5. Weekly Review Loop

週次で、daily proxy の揺れをならす。

Outputs:

- short / long の機会品質傾向
- regime shift possibility
- subject too defensive trend
- over-suppression trend
- turning point missed candidates
- top 3 product-quality issues
- next small implementation candidates

Weekly loop は、実取引CSVなしでも product direction を保つための中間レビュー。

## 6. Biweekly Ground Truth Loop

2週間に1回、取引所 export を取り込む。

Inputs:

- futures position history
- futures order history
- futures trade history

Optional later:

- futures fund flow
- futures details

Outputs:

- actual human trade PnL
- net PnL after fee if available
- actual manual short / long win rate
- actual PF
- actual R if SL/TP linkage exists
- notification-to-trade linkage
- proxy-vs-actual calibration
- confirmed improvement candidates

この loop が最終的な ground truth である。

## 7. User burden design

2週間に1回の export 以外で、ユーザーに大きな負担をかけない。

Daily use should remain:

```text
mailを見る
15分足を見る
取引する/見送る
```

Optional low-burden manual note:

```text
entered short
entered long
skipped
watched_no_entry
took profit
missed
```

But even this should be optional.

The system should still work with:

- no manual notes
- no daily trade import
- only biweekly exchange export

## 8. Import file design

### 8.1 Import directory

```text
local/manual_trade_imports/YYYYMMDD/
```

Example:

```text
local/manual_trade_imports/20260715/
  futures_position_history.xlsx
  futures_order_history.xlsx
  futures_trade_history.xlsx
```

Initial policy:

- local generated input
- do not commit raw exports
- do not store secrets
- do not include API keys
- files may contain account/trade info, so keep local only

### 8.2 Canonical converted CSV

```text
logs/csv/manual_actual_trades.csv
logs/csv/manual_actual_orders.csv
logs/csv/manual_actual_positions.csv
```

Initial policy:

- generated local outputs
- do not commit by default
- can be summarized into reports
- no `paper_positions.csv` mixing

### 8.3 Linkage output

```text
logs/csv/manual_trade_signal_links.csv
```

Purpose:

- link actual trades to notification / signal / mail events
- store link confidence

Columns:

| column | meaning |
|---|---|
| `actual_trade_id` | actual trade identifier |
| `signal_id` | linked signal id |
| `mail_timestamp_jst` | notification time |
| `trade_opened_at_jst` | actual open time |
| `trade_closed_at_jst` | actual close time |
| `side_match` | true/false |
| `time_delta_minutes` | trade open after mail |
| `price_context_match` | true/false/unknown |
| `link_confidence` | high/medium/low/manual_confirmed/ambiguous |
| `link_note` | short explanation |

## 9. Import workflow

### 9.1 User export selection

最初に必要な export:

```text
✅ Futures position history
✅ Futures order history
✅ Futures trade history
Format: EXCEL
Frequency: every 2 weeks
```

Optional later:

```text
Futures fund flow
Futures details
```

### 9.2 Import command concept

Future CLI concept:

```text
./.venv312/bin/python tools/log_feedback.py import-manual-actual-trades \
  --input-dir local/manual_trade_imports/20260715 \
  --output-dir logs/csv \
  --stdout-json
```

Safety:

- no exchange API
- no account endpoint
- no order endpoint
- no secrets
- local file only

### 9.3 Link command concept

```text
./.venv312/bin/python tools/log_feedback.py link-manual-trades-to-signals \
  --manual-trades logs/csv/manual_actual_trades.csv \
  --signals logs/csv/user_reviews.csv \
  --signal-outcomes logs/csv/signal_outcomes.csv \
  --output-csv logs/csv/manual_trade_signal_links.csv \
  --stdout-json
```

### 9.4 Report command concept

```text
./.venv312/bin/python tools/log_feedback.py build-manual-trade-ground-truth-report \
  --manual-trades logs/csv/manual_actual_trades.csv \
  --links logs/csv/manual_trade_signal_links.csv \
  --output-md 運用資料/reports/post_eval/manual_trade_ground_truth_20260715.md \
  --stdout-json
```

## 10. Linkage logic

Actual trade と mail/signal の紐づけは、最初は heuristic でよい。

Scoring:

| factor | score |
|---|---:|
| trade opened 0-90 min after mail | +3 |
| trade opened 90-240 min after mail | +1 |
| side matches priority direction | +3 |
| side matches secondary opportunity | +2 |
| symbol matches BTCUSDT | +2 |
| entry price near signal reference price | +1 |
| no competing signal nearby | +1 |
| manual note confirms | +5 |

Link confidence:

| score | confidence |
|---:|---|
| 8+ | high |
| 5-7 | medium |
| 2-4 | low |
| conflict | ambiguous |
| manual selected | manual_confirmed |

Actual performance claims should use high + manual_confirmed first.

## 11. Proxy-vs-actual calibration

Biweekly import の最大価値は、daily proxy が実際の損益とどれだけ合っていたかを測ること。

Calibration questions:

- `AGGRESSIVE_SHORT_A` は実取引で本当に勝っているか。
- `AGGRESSIVE_LONG_A` はロング相場で機能するか。
- `TURN_RISK_HIGH` は実際に大損回避に役立ったか。
- `NO_TRADE_CANDIDATE` は守りすぎだったか。
- `ENTRY_OK` は実際には `CHECK_15M_ENTRY` として扱うべきか。
- Daily PF / direction win-rate と actual net PnL は一致しているか。

Calibration outputs:

| output | meaning |
|---|---|
| `proxy_aligned` | proxy評価と実損益が一致 |
| `proxy_too_pessimistic` | systemは警戒したが実取引は勝ち |
| `proxy_too_aggressive` | systemは攻めたが実取引は負け |
| `turning_risk_underestimated` | 転換リスクを過小評価 |
| `turning_risk_overestimated` | 転換警戒が強すぎた |
| `manual_edge_confirmed` | 人間の15分足フィルターでedgeが確認された |

## 12. Long / short and aggressive-balanced logic

Long / Short の機会は常に両方検出する。ただし、優先表示は market regime に応じて変える。

```text
if regime is downtrend:
    short opportunity is prioritized
    long opportunity is still shown as scout / reversal watch

if regime is uptrend:
    long opportunity is prioritized
    short opportunity is still shown as exhaustion / pullback risk watch

if regime is transition:
    both sides are shown strongly, but aggression rank is capped

if turning risk is HIGH or EXTREME:
    new aggressive entries are suppressed or downgraded
```

Subject / display は「禁止」ではなく「行動」を示す。

Example subject format:

```text
[BTCFX Ver04-v1] {priority_direction}｜{15m_action}｜攻め{A/B/C or 停止}｜転換警戒:{LOW/MED/HIGH/EXTREME}
```

Examples:

```text
[BTCFX Ver04-v1] SHORT強｜15m戻り売り確認｜攻めA｜転換警戒:LOW
[BTCFX Ver04-v1] LONG初動候補｜15m押し目確認｜攻めB｜転換警戒:MED
[BTCFX Ver04-v1] 大転換警戒｜新規停止・利確優先｜攻め停止｜転換警戒:EXTREME
```

## 13. AI post review position

AI事後評価は捨てない。ただし、自己改善ループの主役にはしない。

New role:

```text
AI post review = qualitative explanation layer
Deterministic post-eval = main evaluation layer
Biweekly actual trade import = ground truth layer
```

If AI fails:

- daily proxy loop still runs
- weekly loop still runs
- biweekly ground truth still runs
- report says AI enrichment unavailable

AI post review recovery should happen after deterministic loop is reliable.

## 14. Reports

### 14.1 Daily proxy report

File concept:

```text
運用資料/reports/post_eval/post_eval_daily_proxy_YYYYMMDD.md
```

Sections:

- Purpose fit summary
- Mail usefulness estimate
- Aggressive short / long proxy results
- Turning risk candidates
- Over-suppression candidates
- Top 3 improvement candidates
- AI post review health
- Safety boundary

### 14.2 Weekly review report

File concept:

```text
運用資料/reports/post_eval/post_eval_weekly_review_YYYYMMDD.md
```

Sections:

- Weekly trend
- Short / long opportunity balance
- Regime drift
- Aggression rank stability
- Turning brake review
- Recommended next implementation scope

### 14.3 Biweekly ground truth report

File concept:

```text
運用資料/reports/post_eval/manual_trade_ground_truth_YYYYMMDD.md
```

Sections:

- Import summary
- Actual trade summary
- Actual manual short performance
- Actual manual long performance
- Signal linkage quality
- Proxy-vs-actual calibration
- Over-suppression confirmed cases
- Turning point actual cases
- Confirmed improvement list
- Next 2-week action plan

## 15. Self-improvement decision rules

### 15.1 Daily recommendations

Daily proxy は次の軽い改善候補まで出せる。

- subject wording improvement
- label naming improvement
- display priority improvement
- watch/scout classification suggestion
- manual log missing warning
- stale OHLCV warning

### 15.2 Weekly recommendations

Weekly review は次を提案できる。

- short / long priority bias adjustment candidate
- regime display improvement
- turning risk wording improvement
- no-trade split candidate
- manual logging burden reduction

### 15.3 Biweekly recommendations

Biweekly actual import は次を提案できる。

- confirmed subject redesign
- confirmed aggressive rank adjustment
- confirmed turning brake adjustment
- confirmed no-trade split
- confirmed long/short regime weighting
- confirmed manual 15m win-rate metrics

### 15.4 Human approval required

次は必ず人間承認が必要。

- production wording change
- threshold change
- gate change
- config change
- runtime schedule change
- any API behavior
- semi-automatic approval design

## 16. Safety boundary

This design does not start automatic trading.

Hard no:

- no automatic order
- no private/account/order endpoint
- no API key reading or printing
- no runtime restart
- no SMTP/Gmail behavior change
- no `paper_positions.csv` mixing unless explicitly approved
- no automatic threshold mutation

Allowed:

- local file import
- deterministic report generation
- post-evaluation recommendation
- human-approved product improvement

## 17. Implementation phases

### Phase SIL-0: Final design baseline

Add this design doc and remove superseded intermediate drafts.

### Phase SIL-1: Asset health audit

Audit current post-evaluation assets and runtime logs safely.

No API, no secrets, no runtime restart.

### Phase SIL-2: Daily proxy evaluator

Build deterministic daily proxy report that works without manual trade import.

### Phase SIL-3: Manual trade import schema

Define and validate local import files.

### Phase SIL-4: Link actual trades to signals

Build safe local heuristic linking.

### Phase SIL-5: Biweekly ground truth report

Generate actual trade performance and proxy calibration report.

### Phase SIL-6: Recommendation engine

Rank confirmed improvements from daily/weekly/biweekly evidence.

### Phase SIL-7: Surface integration

Show post-eval status on public HTML / mail / dashboard as report-only support.

## 18. Final operating model

```text
Every day:
  system predicts
  system evaluates proxy outcomes
  system reports likely improvements

Every week:
  system summarizes trend and regime drift
  system reviews attack/defense balance

Every 2 weeks:
  user exports futures history Excel
  system imports actual trades
  system links trades to mail/signals
  system calibrates proxy vs actual
  system confirms what to improve next

Always:
  no automatic order
  human decides manually
```

## 19. Final definition of success

The self-improvement loop is successful when:

```text
1. The user only needs to export actual trade data about once every two weeks.
2. Daily and weekly reports still produce useful improvement candidates without that export.
3. Biweekly actual trade import corrects the proxy evaluation.
4. The system learns whether aggressive short/long opportunities are actually helping.
5. Over-suppression and turning-point misses become visible.
6. Future changes are chosen from evidence, not from vague impressions.
7. The user becomes better at winning manual trades from mail + 15m chart checks.
```

This is the practical final design for a human-operated, aggressive-but-controlled BTC trading support system.
