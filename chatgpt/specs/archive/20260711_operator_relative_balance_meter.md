# Operator Relative Balance Meter — Active Specification

- work_id: `BTCFX-20260711-OPERATOR-RELATIVE-BALANCE-METER`
- status: completed / accepted by bounded validation
- surface: existing public detail HTML only

## Contract

Add a display-only full-width relative balance meter after the SHADOW panel and before the workspace. It uses the existing `long_display_score` and `short_display_score`, normalized through `_operator_dashboard_score`; it never recomputes or changes scores, decisions, gates, thresholds, classifier behavior, notifications, runtime, orders, or P9 tuning.

For total score greater than zero, render deterministic one-decimal-at-most shares: `long / (long + short) * 100` and `short = 100 - long`, with green LONG from the left, red SHORT from the right, and a 50% center reference. For zero/zero, render a neutral insufficient-evidence state with `判定材料不足`, never a fake 50/50 split. Preserve existing side-card absolute scores.

The section exposes stable semantic hooks, relative state/share attributes, role and accessible score/share labels, responsive full-width CSS, and the note `機械評価上の相対バランス。最終判断ではありません。` No animation or JavaScript is added.

Safety: report-only / not FORMAL_GO / no automatic order / human decides manually. P9 remains evidence-gated and does not start in this task.

## Acceptance record

- implementation: `src/notification/detail_page.py`
- tests: `tests.test_notification_detail_page` — 37 passed
- no-send smoke: pass; real_mail_sent=false; report-only/not FORMAL_GO/no automatic order/human-decided=true
- runtime restart, launchd operation, mail send, and public publish: not performed
- existing scores, decisions, gates, classifier, notification behavior, and runtime behavior: unchanged
