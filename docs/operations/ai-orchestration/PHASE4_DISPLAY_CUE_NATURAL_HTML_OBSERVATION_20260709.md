# Phase4 display cue natural HTML observation

## 結論

自然生成された detail HTML に Phase4 display cue panel が載っていることを確認した。
これは `d2beafe` の display/report-label-only 実装が runtime 経路まで反映された技術確認である。
ただし、human readability や誤読リスクの評価はまだ観察段階であり、Phase4 tuning remains blocked のまま。

## 確認したHTML

- `logs/notifications_html/manual-trading/attention/20260709_040500.html`
- `logs/notifications_html/manual-trading/followup/20260709_060500.html`
- `logs/notifications_html/manual-trading/main/20260708_210500.html`

## marker確認

以下の marker は3件すべてで確認できた。

- `chart_review_only`
- `not entry prohibition`
- `preserve cue`
- `not_directly_evaluated`
- `Big Chance is not an entry instruction`
- `shallow zone`
- `defense zone`
- `report-only / not FORMAL_GO / no automatic order / human decides manually`

## cue別メモ

- CUE02 は long 側 review の chart_review_only 補助表示として出ている
- CUE03 は active cue ではなく hold / do_not_show_yet の扱いが維持されている
- CUE04 は short 側の preserve cue として出ている
- CUE05 / CUE06 は not_directly_evaluated として表示され、0 扱いされていない
- CUE08 は Big Chance is not an entry instruction を visible に含む
- CUE09 は shallow zone と defense zone を別々に確認する構成になっている

## まだ判断してはいけないこと

- 勝率改善
- human usability の合格
- cue のノイズ感の解消
- Phase4 tuning の前進

## 次の観察ポイント

- cue panel が 1 画面で読み切れるか
- CUE02 が long 禁止に誤読されないか
- Big Chance が entry instruction に誤読されないか
- Value Defense の shallow / defense split が役に立つか

## Safety Boundary

report-only / not FORMAL_GO / no automatic order / human decides manually

