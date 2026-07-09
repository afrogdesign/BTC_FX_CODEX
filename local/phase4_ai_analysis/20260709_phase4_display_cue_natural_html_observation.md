# Phase4 display cue natural HTML observation

- work_id: `BTCFX-20260709-PHASE4-DISPLAY-CUE-NATURAL-HTML-OBSERVATION`
- observation_date: `2026-07-09`
- implementation_commit: `d2beafe`
- docs_sync_commit: `dfe8955`
- runtime_status: `runtime_applied`

> [!abstract]
> 自然生成された detail HTML に Phase4 display/report-label cue panel が載っていることを確認した観察レポートです。
> これは runtime 反映の技術確認であり、勝率改善や human usability の合格を意味しません。

## 結論

Phase4 display cue panel は自然生成 HTML に出ています。
これは `d2beafe` の display/report-label-only 実装が runtime 経路まで反映されたことを示します。

ただし、この観察だけでは human readability の良し悪し、cue の見誤りやノイズ感、実運用での読みやすさは判断できません。
Phase4 tuning remains blocked のままです。

## 観察対象HTML

| 種別 | ファイル |
|---|---|
| attention | `logs/notifications_html/manual-trading/attention/20260709_040500.html` |
| followup | `logs/notifications_html/manual-trading/followup/20260709_060500.html` |
| main | `logs/notifications_html/manual-trading/main/20260708_210500.html` |

## marker確認結果

| marker | attention | followup | main |
|---|---:|---:|---:|
| `chart_review_only` | yes | yes | yes |
| `not entry prohibition` | yes | yes | yes |
| `preserve cue` | yes | yes | yes |
| `not_directly_evaluated` | yes | yes | yes |
| `Big Chance is not an entry instruction` | yes | yes | yes |
| `shallow zone` | yes | yes | yes |
| `defense zone` | yes | yes | yes |
| `report-only / not FORMAL_GO / no automatic order / human decides manually` | yes | yes | yes |

## cue別確認

- CUE02: long active_limit_retest の review で `chart_review_only` として表示されている
- CUE03: active cue ではなく hold / do_not_show_yet の扱いが保たれている
- CUE04: short active_limit_retest の `preserve cue` が表示されている
- CUE05 / CUE06: `not_directly_evaluated` として表示され、0 扱いされていない
- CUE08: `Big Chance is not an entry instruction` が visible で明示されている
- CUE09: `shallow zone` と `defense zone` が別々に確認する形で表示されている

## 技術反映として確認できたこと

- natural generated detail HTML に Phase4 cue panel が載った
- report-only safety boundary が自然生成 HTML でも維持された
- Big Chance と Value Defense の補助文言が detail HTML surface に反映された
- これは runtime reflection の確認であり、生成済み HTML のレベルでは実装が有効になっている

## まだ判断してはいけないこと

- この表示が勝率を改善したとは言えない
- human usability が十分だとはまだ言えない
- cue が本当に見やすいか、誤読されないかは次の観察が必要
- Phase4 tuning を進めてよいとは言えない

## 次の観察ポイント

- cue panel が長すぎず、1画面で把握できるか
- CUE02 が long 禁止に誤読されないか
- Big Chance が entry instruction に誤読されないか
- Value Defense の shallow / defense split が実際に役立つか
- report-only safety boundary が常に見えているか

## Safety Boundary

report-only / not FORMAL_GO / no automatic order / human decides manually

