---
title: HTMLオペレーター報告書GUI v5・受け入れギャップ完了計画
date: 2026-07-25
tags:
  - btc_monitor
  - html-report
  - gui
  - tests
  - acceptance
  - report-only
status: active-review-gap-plan
work_id: P-HTML-OPERATOR-GUI-V5-ACCEPTANCE-GAPS
branch_target: Ver04-v5
safety: report-only / not FORMAL_GO / no automatic order / human decides manually
---

# HTMLオペレーター報告書GUI v5・受け入れギャップ完了計画

## 0. この文書の役割

この文書は、次のGUI改善計画を置き換えるものではない。

- `docs/operations/strategy/HTML_OPERATOR_REPORT_GUI_IMPROVEMENT_PLAN_20260725.md`

元の計画書は、5エリア構成、用語、情報優先度、時間軸、Long・Short表示、価格マップ、補助監視の正本である。

本書は、実装後レビューで残った**受け入れ証拠の不足、テスト移行の不透明さ、premature acceptance記録**だけを補完する。

優先順位は次のとおり。

1. repo正本の安全・Git・validationルール
2. 元のGUI改善計画
3. 本書の未完了ギャップとacceptance手順
4. 実装済みsource、tests、previewのrepo実体

元のGUI改善計画末尾にある未commitの受け入れ記録と本書が矛盾する場合、**本書を優先する**。

---

## 1. 現在地

2026-07-25のAFROG_MCPレビューで次を確認した。

- branch: `Ver04-v5`
- HEAD: `22dee8fbbb6830518af6824d8d42d9c148a69a03`
- latest commit: `fix: close operator report GUI review gaps`
- upstream: none
- GUI source/test対象には未commit差分なし
- repo全体には本件と無関係な大量のdirty / untracked差分が存在する

関連commit:

- `a7ecc36aca1671adb134eaf1736e8e7262d88e87`
  - `feat: reorganize operator report GUI`
- `0a490dfe540c7302063ad572e36fd4faf90de3df`
  - `fix: complete operator report GUI contract`
- `22dee8fbbb6830518af6824d8d42d9c148a69a03`
  - `fix: close operator report GUI review gaps`

現時点で成立している内容:

- 5エリア構成
- 表示専用view model
- Area 2の方向付き具体文
- lifecycle値を方向へ変換しないfail-closed
- 15M方向を`primary_side`から補完しない
- exact-signal preview
- branch名`Ver04-v5`

現時点のacceptance状態:

```text
implemented / acceptance pending
```

**まだ`implemented-and-accepted`ではない。**

---

## 2. 今回の最終目的

GUI sourceを再設計することではない。

次の2点を、1回の最終bounded passで完了させる。

1. 旧renderer契約テストの削除が、安全・互換性・fail-closed契約の喪失になっていないことを、active testsで明示する
2. 元の計画書に書かれた未commitのpremature acceptance記録を、事実に合う状態へ訂正する

作業後、ChatGPTがAFROG_MCPでcommit、tests、preview、scopeを直接確認し、初めてacceptanceを判断する。

Codexや作業AIは、自分で`accepted`と確定してはならない。

---

## 3. 今回変更しないもの

次は成立済みであり、テストが実際の欠陥を示さない限り変更しない。

- 5エリアの順序
- Area 1「今の結論」
- Area 2「時間軸別の方向」
- Area 3「15分足の実行判断」
- Area 4「価格マップ」
- Area 5「判断が変わる条件・補助監視」
- `build_operator_report_view()`の基本構造
- Long・Shortの日本語ラベル
- A/B/C/STOPの表示用変換
- chart time-frame switch
- layer switch
- exact-signal previewの出力先

テスト追加の都合だけでDOMや用語を再変更しない。

---

## 4. 重要なレビュー所見

### 4.1 旧テストの大量削除

`0a490df`では、`tests/test_notification_detail_page.py`から旧GUI関連テストが大きく削除された。

削除された行数を元へ戻すこと自体は目的ではない。

問題は、各契約が次のどれに該当するかが明示されていないことである。

- obsolete: 旧DOM・旧文言だけを固定していたため廃止可能
- replaced: 新しいactive testで同じ契約を検証済み
- restore/update: 現在のactive testでは未検証なので、新GUI向けに復元・更新が必要

この分類がないまま「新テストへ移行済み」と扱わない。

### 4.2 現在のactive GUIテスト

`tests/test_operator_report_view.py`には、少なくとも次のactive testsが存在する。

- `test_dynamic_content_escaped`
- `test_malformed_fails_closed`
- `test_raw_terms_only_in_diagnostic_details`
- `test_five_area_order`
- `test_prices_and_chart_controls_preserved`
- `test_safety_boundary_top_and_footer`
- `test_structural_allocation_and_independent_scores_show_actual_values`
- `test_two_real_action_cards_for_missing_invalid_and_malformed_priority`
- `test_lifecycle_is_not_a_timeframe_direction`
- `test_missing_invalidation_is_fail_closed`
- `test_preserves_stable_surface_safety_and_hidden_version_labels`
- `test_chart_geometry_big_chance_and_responsive_contract`
- `test_notification_kinds_keep_same_report_only_surface_and_diagnostics_below`

これらは有効な移行先である。

ただし、テスト名が存在するだけで旧契約全体をカバーしたとは扱わない。assert内容まで確認する。

### 4.3 元計画書のpremature acceptance記録

元計画書末尾の未commit差分には次がある。

```text
acceptance_status: implemented-and-accepted
```

さらに、renderer regression tests、ChatGPT MCP review、acceptance完了を断定している。

この記録は現在のreview状態と矛盾する。

本書の作業が完了し、ChatGPTが最終reviewするまで、元計画書は次のいずれかにする。

- 受け入れ記録節を削除する
- `implemented / acceptance pending`へ訂正する

作業AIは`implemented-and-accepted`を書いてはならない。

---

## 5. 作業範囲

### 5.1 原則変更するファイル

- `tests/test_notification_detail_page.py`
- `tests/test_operator_report_view.py`
- `docs/operations/strategy/HTML_OPERATOR_REPORT_GUI_IMPROVEMENT_PLAN_20260725.md`
- `docs/operations/strategy/HTML_OPERATOR_REPORT_GUI_ACCEPTANCE_GAP_COMPLETION_PLAN_20260725.md`

### 5.2 条件付きで変更可能なファイル

active testを正しく追加した結果、実際のrenderer / view-model欠陥が見つかった場合だけ変更可能。

- `src/notification/detail_page.py`
- `src/notification/operator_report_view.py`

source変更が不要なら変更しない。

### 5.3 変更禁止

- `src/analysis/`配下
- `src/feedback/`配下のclassifier / producer
- gates
- scores
- thresholds
- entry / SL / TP計算
- notification条件
- mail
- runtime
- LaunchAgent
- schedule
- public publication
- automatic order
- private/account/order endpoint

安全境界:

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```

---

## 6. テスト移行マトリクス

作業AIは、削除前の`tests/test_notification_detail_page.py`をcommit historyから確認し、旧GUI関連テストごとに次の表を作業メモとして埋める。

この表自体を別artifactにする必要はない。commit前に判断を完了することが必要である。

| 旧契約 | 分類 | 現在のactive test | 必要対応 |
|---|---|---|---|
| 動的テキストのHTML escape | replaced / restore | test名 | assert不足なら追加 |
| unknown sideのfail-closed | replaced / restore | test名 | 推測禁止と2カードを確認 |
| no-chase表示 | replaced / restore | test名 | 人間向け表示と重複数を確認 |
| setup欠損時のページ維持 | replaced / restore | test名 | chartと5エリアが残ることを確認 |
| stable product title | replaced / restore | test名 | titleとversion leakを確認 |
| private/order情報非表示 | replaced / restore | test名 | visible surfaceで確認 |
| Big Chance補助性 | replaced / restore | test名 | 順序・非上書き・補助見出しを確認 |
| chart controls | replaced / restore | test名 | 15m/1h/4hとbasic/fullを確認 |
| chart geometry | replaced / restore | test名 | 主要価格帯が15m view内で描画されることを確認 |
| notification kind互換 | replaced / restore | test名 | main/attention/followupを確認 |
| malformed data | replaced / restore | test名 | exceptionではなくfail-closed HTML |
| diagnostics separation | replaced / restore | test名 | detailsより上に内部コードが出ない |
| safety boundary | replaced / restore | test名 | 上部とfooter、注文許可なし |

分類ルール:

- 旧class名や旧DOM selectorだけに依存するテストは`obsolete`でよい
- safety、escaping、fail-closed、価格、notification kindを`obsolete`にしてはならない
- 新テストに同等assertがなければ`replaced`にしてはならない
- 1つの新テストが複数契約をカバーしてもよい
- テスト名だけでなくassertの実体を確認する

---

## 7. 必須active test契約

以下はすべてactiveでなければならない。

### 7.1 HTML escape

最低限、次を別々に確認する。

- `next_condition`へHTML / script様文字列を入れてもraw tagが出ない
- setup由来の動的価格・ラベル値へ文字列が混入してもraw HTMLにならない
- diagnostic JSONもHTML文脈でescapeされる

単に`<script>`が1件escapeされるだけで、すべての動的renderer契約を証明したと扱わない。

### 7.2 primary sideのfail-closed

次の各ケースを確認する。

- missing
- blank
- unknown string
- malformed object

期待結果:

- Longカードが1枚
- Shortカードが1枚
- unknown値からLong / Shortを推測しない
- priorityなしでもrendererが壊れない
- 15M方向をprimary sideから補完しない

### 7.3 no-chase

- lifecycleまたはchase statusがlate / no-chaseなら「追いかけ禁止」を表示
- 同じカード内で不必要に重複しない
- 優先側headlineだけに依存しない
- no-chaseを実行許可として誤読させない

### 7.4 setup欠損

Long / Shortの片側または両側setupが欠損しても、次を維持する。

- HTML生成成功
- 5エリア順序
- chart panel
- Long / Shortカード
- fail-closedな`データ未取得`または`判定材料不足`
- fabricated priceを生成しない

### 7.5 stable surfaceと秘匿境界

通常画面で次を確認する。

含む:

- `BTCFX Manual Trading Report`
- `REPORT ONLY / HUMAN DECISION`
- report-only footer

含まない:

- version label
- `send_email`
- private endpoint
- account endpoint
- order endpoint
- automatic order enabledを示す文言

### 7.6 Big Chance

- `補助監視`と明記
- 通常Long / Short判断を上書きしない文言
- Area 5の主たる判断変更条件より視覚・DOM順で後
- 市場補足と同等以下の優先度
- opposite-side候補でもprimary judgmentに昇格しない
- raw `stale`を通常画面へ出さない

### 7.7 chart contract

最低限:

- `data-chart-view="15m"`
- `data-chart-view="1h"`
- `data-chart-view="4h"`
- `data-layer-mode="basic"`
- `data-layer-mode="full"`
- initial 15m `viewBox="0 726 860 429"`
- heading switch map
- horizontal scrollはchartに限定するresponsive contract

さらに、旧geometryテストが検証していた主要価格帯のmarker / zoneが15m表示範囲外へ飛んでいないことを、deterministic fixtureで確認する。

CSS文字列の存在だけでgeometry全体を証明したと扱わない。

### 7.8 notification kind

`main`、`attention`、`followup`で次を確認する。

- 同じoperator-dashboard surface
- 5エリアが維持される
- safety boundaryが維持される
- diagnosticsはmain contentより後
- private/account/order情報を表示しない

### 7.9 malformed / partial evidence

- malformed `side_aware_mtf_action`
- malformed `operator_decision`
- lifecycle値をsignalsへ入れたケース
- 4Hだけ既知、1H・15M不明
- price / invalidation欠損

期待結果:

- unknownを推測しない
- `判定材料不足`または`データ未取得`
- renderer例外なし

---

## 8. テスト配置方針

### `tests/test_operator_report_view.py`

次を中心に置く。

- pure view-model conversion
- direction summary
- lifecycleと方向の分離
- visible HTMLの5エリア契約
- internal code非表示
- rendererのGUI-specific regression

### `tests/test_notification_detail_page.py`

次を中心に残す。

- detail page全体の既存renderer契約
- breakout / warning / runtime statusなどGUI v5外の既存機能
- publish path / notification flow
- renderer全体のcompatibility boundary

同じ契約を両ファイルへ重複させない。

ただし、「GUIテストは新ファイルへ移した」という理由だけで、既存detail-page全体の安全契約を消さない。

---

## 9. preview契約

既存preview:

`local/operator_report_gui_v5_preview/20260724_220500/index.html`

入力:

`logs/signals/20260724_220500.json`

現在確認済み:

- signal: `20260724_220500`
- timestamp: `2026-07-25 07:05:00.871936+09:00`

今回の作業では、source変更がない場合はpreviewを再生成しなくてよい。

sourceを変更した場合だけ、既存のdeterministic routeで再生成して次を確認する。

- signal ID一致
- timestamp一致
- current price一致
- Long / Short setupの代表価格一致
- chart controls存在
- Area 1〜5順序
- internal codesが通常画面へ出ない

previewはstage / commitしない。

ディレクトリ名だけを合わせたsample fixtureは禁止する。

---

## 10. 元計画書の訂正契約

作業開始時に、元計画書末尾の未commit受け入れ記録を確認する。

最終ChatGPT acceptance前は次に訂正する。

```text
acceptance_status: implemented / acceptance pending
```

または、prematureな受け入れ記録節を削除する。

次の断定は最終acceptance前に書かない。

- accepted
- complete
- ChatGPT review passed
- renderer regression coverage complete
- no remaining gaps

作業AIが記載可能な内容:

- implementation commit
- test commandと結果
- diff-check結果
- previewの確認事実
- push none
- ChatGPT acceptance pending

ChatGPT最終review後だけ、別途`implemented-and-accepted`へ更新できる。

---

## 11. Validation

正規repo環境を使う。

優先command:

```text
./.venv312/bin/python -m unittest tests.test_notification_detail_page tests.test_operator_report_view
```

必要なら、変更したclass / testだけのfocused実行を先に1回行ってよい。

最終証拠として、上記2 moduleを同じcommandで1回実行する。

必須:

- pass
- skipped=0
- expected failureなし
- import errorなし

AFROG_MCP標準Pythonに`pandas`がないことは既知である。新しい依存をinstallしない。

task-scoped diff check:

```text
git diff --check -- \
  src/notification/detail_page.py \
  src/notification/operator_report_view.py \
  tests/test_notification_detail_page.py \
  tests/test_operator_report_view.py \
  docs/operations/strategy/HTML_OPERATOR_REPORT_GUI_IMPROVEMENT_PLAN_20260725.md \
  docs/operations/strategy/HTML_OPERATOR_REPORT_GUI_ACCEPTANCE_GAP_COMPLETION_PLAN_20260725.md
```

行わないもの:

- full suite
- replay
- runtime restart
- notification送信
- mail送信
- public publication
- browser automation
- screenshot生成
- heavy validation
- 同じtestの理由なき再実行

---

## 12. Git・dirty treeルール

repo全体のcleanlinessを完了条件にしない。

本件対象と重なる差分だけを確認する。

禁止:

- reset
- restore
- clean
- stash apply
- stash pop
- stash drop
- `git add .`
- `git add -A`
- unrelated fileのstage

元計画書は現在、本件に関連する未commit差分を含むため、内容を確認せず上書きしない。

本書と元計画書、tests、必要な場合のみsourceを個別stageする。

---

## 13. Commit境界

推奨commit message:

```text
test: complete operator report GUI acceptance coverage
```

または、source修正が必要だった場合:

```text
fix: complete operator report GUI acceptance coverage
```

commit対象候補:

- `tests/test_notification_detail_page.py`
- `tests/test_operator_report_view.py`
- `docs/operations/strategy/HTML_OPERATOR_REPORT_GUI_IMPROVEMENT_PLAN_20260725.md`
- `docs/operations/strategy/HTML_OPERATOR_REPORT_GUI_ACCEPTANCE_GAP_COMPLETION_PLAN_20260725.md`
- 実際の欠陥修正がある場合だけsource 2 files

commitしない:

- preview
- logs
- unrelated dirty files
- raw exchange files
- runtime artifacts

push: none

---

## 14. 完了条件

次をすべて満たしたとき、作業AIは`done / ChatGPT acceptance pending`として報告する。

1. branchが`Ver04-v5`
2. 5エリアGUIを変更していない、または実欠陥だけを最小修正
3. 旧GUIテストをobsolete / replaced / restore-updateへ分類済み
4. safety・escaping・fail-closed契約をobsolete扱いしていない
5. 必須active test契約がすべて存在
6. no-chaseの表示と重複防止をactive testで確認
7. setup欠損時の5エリア・chart維持をactive testで確認
8. chart geometryをdeterministic fixtureで確認
9. Big Chanceの順序・補助性・非上書きをactive testで確認
10. main / attention / followup互換をactive testで確認
11. unknown / malformed primary sideで2カードを維持
12. lifecycleを方向へ変換しない
13. internal codesが通常画面に出ない
14. stable titleとsafety boundaryを維持
15. private/account/order情報を通常画面に出さない
16. focused 2-module testがpass、skipped=0
17. task-scoped diff checkがpass
18. previewが正しいsignalのまま、またはsource変更後に再確認済み
19. previewをcommitしていない
20. 元計画書のpremature acceptance記録を訂正
21. 本書をcommit
22. unrelated dirty treeを変更していない
23. local commit済み
24. pushしていない
25. reportは`ChatGPT acceptance pending`であり、自動acceptしていない

---

## 15. ChatGPT最終review

作業報告は証明ではなくlocatorである。

ChatGPTは最初にAFROG_MCPで次を確認する。

1. `get_workspace_repo_status`
2. `get_workspace_repo_diff(scope="commit", commit="<reported commit>")`

必要な場合だけ追加確認する。

- active test source
- source変更
- preview
- 元計画書と本書のstatus

ChatGPTのacceptanceチェック:

- testsの行数ではなく契約が保全されたか
- obsolete判定が旧DOMだけに限定されているか
- safety testを消していないか
- source scopeが表示層だけか
- premature acceptance記録がないか
- previewがcommitされていないか
- unrelated変更がcommitへ混入していないか

十分な証拠が揃った時点でreviewを終了する。

---

## 16. 作業AIの報告形式

```text
WORK_ID: P-HTML-OPERATOR-GUI-V5-ACCEPTANCE-GAPS
STATUS: done | partial | blocked | failed
BRANCH: <branch>
CHANGED:
- <file or none>
TESTS:
- <command> => pass | fail | not run
MIGRATION:
- obsolete: <count>
- replaced: <count>
- restored_or_updated: <count>
PREVIEW:
- signal: <id>
- committed: no
COMMIT: <hash or none>
PUSH: none
ACCEPTANCE: ChatGPT acceptance pending
NOTES: <必要な場合のみ>
```

local filesystemへアクセスできる作業では、同じcompact reportを次へexactly one writeする。

`/Users/marupro/CODEX/chatGPTweb-to-Terminal/outbox/response.txt`

write後はread、存在確認、retry、watch、poll、再作成を行わない。

---

## 17. 停止条件

次の場合は推測で続行せず、`blocked`として報告する。

- 対象tests / docsに別作業の未commit差分が重なる
- safety契約を維持するために表示層以外のproducer変更が必要
- test fixtureが実データやprivate情報を必要とする
- chart geometry契約を確認するためにheavy replayが必要
- `Ver04-v5`が想定外の履歴へ移動している
- 元計画書の未commit差分の所有関係が判断できない

---

## 18. 結論

今回の残作業は、GUIをさらに装飾することではない。

重要なのは次の3点である。

1. 削除された旧テストの意味を分類し、重要契約の移行先を明示する
2. safety・escaping・fail-closed・chart・notification-kindのactive coverageを完成させる
3. ChatGPT review前にacceptance完了を記録しない

本書の完了後、ChatGPTがcommit差分とactive testsを直接確認し、最終acceptanceを判断する。
