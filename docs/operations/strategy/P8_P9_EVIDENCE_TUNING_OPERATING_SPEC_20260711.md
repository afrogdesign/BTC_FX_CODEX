# P8 / P9 Evidence and Tuning Operating Specification

## Metadata

- created_at: `2026-07-11`
- status: approved operating specification
- scope: P8 human manual trial / P9 evidence-backed tuning review
- primary repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- product objective: notificationを起点に人間が15分足を確認し、攻めの姿勢で勝つmanual trading support
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

## 1. Executive decision

P8は、人間が各通知を文章で記録する期間ではない。

P8の主系は、既存の予測、scenario、A/B/C/STOP、OHLCV outcome、実取引CSV、trade episode、signal/scenario linkを自動結合し、予測と実結果を継続評価する仕組みである。

人間の入力は例外だけに限定する。

```text
自動で確定できる事実
→ deterministic evaluatorが評価

実取引CSVで照合できる事実
→ importer / episode / linkerが評価

人間の意図がなければ確定できない事実
→ review queueで必要なものだけ確認
```

P9は自動再調整ではない。

```text
systemが証拠を収集
→ deterministic reportが問題を検出
→ AIが原因と改善案を整理
→ offline replay / holdoutで検証
→ 人間が承認
→ bounded implementation
→ shadow observation
→ 必要な場合だけproduction反映
```

threshold、gate、notification、runtime、order behaviorをAIが自動変更してはならない。

## 2. Current implementation baseline

P8開始時点で、次の基盤は実装済みである。

- actual trade importer
- fillからposition lifecycleを作るmanual trade episode builder
- actual tradeとsignal/scenarioを結ぶlinker
- actual-backed ground-truth report
- scenario normalization / lifecycle / duplicate compression
- append-only manual decision events
- event-time A/B/C/STOP offline classifier
- historical replay
- public detail HTMLのshadow surface

したがってP8はgreenfieldではない。

不足しているのは、これらを日次・週次・実取引取込時の一つの評価運用へ接続し、例外だけを人間へ返す層である。

## 3. Responsibility split

### 3.1 Deterministic system

主評価を担当する。

- event-time予測snapshotの固定
- scenario単位の重複排除
- outcome maturity判定
- OHLCVによるTP1-first / SL-first / MFE / MAE
- direction correctness
- missed-opportunity proxy
- over-suppression proxy
- STOP false-alarm proxy
- actual trade import
- trade episode再構成
- signal/scenario link confidence
- actual PnL / fee / R / PF
- A/B/C/STOP、long/short、regime、setup別集計
- unresolved / no_ohlcvの分離

### 3.2 AI review

定性的説明と改善候補の整理を担当する。

- recurring issueの要約
- 原因仮説の分類
- UI問題と判定問題の分離
- side / regime / setup別の偏り説明
- 改善候補の優先順位付け
- offline replayで比較するcandidate spec作成
- human approval用の短い提案作成

AIは次を行わない。

- event outcomeの最終数値計算
- thresholdの自動変更
- gateの自動変更
- notification behaviorの自動変更
- runtime restart
- order/API操作
- 単一例からのproduction tuning

### 3.3 Human

人間が担当するのは次だけである。

- 取引所履歴の定期export
- ambiguous linkの確認
- 取引しなかった理由が重要な例外の確認
- UIが誤解を生んだかの確認
- tuning proposalの承認または却下
- manual tradeの最終判断

## 4. P8 objective

P8の目的は、shadow表示の実用性を自動評価し、P9で調整すべき問題を十分な証拠付きで確定することである。

P8は次を答えられる状態を作る。

1. 予測方向と実際の値動きは一致したか。
2. entry/watch zoneは実際に機能したか。
3. A/B/C/STOPのclassは適切だったか。
4. LongとShortのどちらを過剰に抑制したか。
5. STOPは損失回避に寄与したか、それとも機会を消したか。
6. Big Chanceや補助仮説が主判断と矛盾して見えたか。
7. 実取引はどのsignal/scenarioに基づく可能性が高いか。
8. actual PnLとproxy outcomeは整合したか。
9. どの問題が繰り返され、どの変更をP9候補にすべきか。

## 5. P8 automatic evidence pipeline

### 5.1 Event-time snapshot

各評価行は、通知・候補が生成された時点の情報だけを固定する。

後から取得した結果を予測入力へ混ぜない。

最低限のidentity:

- `signal_id`
- `scenario_id`
- `scenario_event_id`
- `candidate_id`
- event timestamp
- side
- operator class
- classifier method/version
- gate snapshot
- no-trade / warning / risk snapshot
- entry/watch zone
- invalidation
- TP1 / TP2
- confidence shadows
- regime / setup family

### 5.2 Market-path outcome

既存OHLCV評価を使い、評価windowが成熟した行だけをresolvedにする。

判定対象:

- TP1-first / SL-first
- TP2 reach
- MFE / MAE
- zone touched / not reached
- invalidation
- direction move
- continuation / reversal
- outcome unavailable

`no_ohlcv`、unresolved、ambiguousは勝敗へ混ぜない。

### 5.3 Actual trade evidence

取引所exportをlocal importerへ読み込み、fillをposition episodeへ再構成する。

actual-backed評価はepisode単位を主とし、fill件数を取引回数として扱わない。

signal/scenario linkは既存confidenceを保持する。

- high / medium: actual-backed aggregateへ使用可能
- low / ambiguous: review queueへ送る
- manual confirmed:人間確認後に使用可能

### 5.4 Prediction-to-result comparison

各scenario-sideについて、最低限次の評価を出す。

- `aligned`: class/sideと結果が整合
- `too_defensive`: 有効な機会をSTOP/C/WAITで抑制した可能性
- `too_aggressive`: A/B候補が不利な結果
- `wrong_side`: 優先方向と結果が逆
- `zone_useful`: zoneが反応点として機能
- `zone_failed`: zoneが明確に機能しない
- `stop_useful_proxy`: STOP後に不利方向へ進行
- `stop_false_alarm_proxy`: STOP後に候補方向へ十分進行
- `big_chance_failed`: 補助仮説が成立せず失効
- `unresolved`: data不足

これらは市場pathのproxyであり、人間の利益・損失回避を自動断定しない。

### 5.5 Human exception queue

全イベントを人間へ入力させない。

次だけをqueueへ送る。

- actual tradeが複数signalへ同程度にlinkする
- sideまたはposition actionが曖昧
- high-value missed-opportunity proxyだが取引がない
- STOPと反対side opportunityが強く競合
- UI表示が主判断と補助仮説を混同させた可能性
- 人間の意図が評価結論を左右する
- unresolvedのうち再取得で解消できない重要例

回答は選択式を基本にする。

```text
この取引はこの通知を根拠にしたか
- はい
- いいえ
- 不明

取引しなかった主因
- 通知を見ていない
- 15分足triggerなし
- STOPに従った
- 間に合わなかった
- リスクが高い
- 表示が分かりにくい
- 別理由
```

## 6. P8 outputs

実装時は既存schemaを正本として再利用し、重複事実を増やさない。

追加する場合の役割は次に限定する。

### 6.1 Trial fact view

既存データを結合したgenerated view。

候補名:

```text
logs/csv/manual_operator_trial_facts.csv
```

1行はscenario-side-eventの評価単位とする。

### 6.2 Review queue

候補名:

```text
logs/csv/manual_operator_trial_review_queue.csv
```

人間確認が本当に必要な行だけを出す。

### 6.3 Daily deterministic report

- resolved / unresolved coverage
- class distribution
- direction / zone / STOP proxy result
- long/short split
- new issue candidates
- actual trade import待ちの明示

### 6.4 Weekly review report

- recurring issue top 3
- A/B/C/STOP別
- long/short別
- regime/setup別
- over-suppression trend
- wrong-side trend
- STOP false-alarm trend
- UI confusion evidence
- P9 readiness

### 6.5 Ground-truth refresh report

実取引CSV取込時に次を更新する。

- actual episode count
- link confidence coverage
- actual PF / R / PnL
- proxy-vs-actual calibration
- confirmed / rejected issue candidates

### 6.6 Issue register

問題は会話だけに残さず、継続管理する。

最低限のfield:

- issue ID
- first seen / last seen
- category
- description
- evidence source
- affected side / regime / setup
- occurrence count
- resolved sample count
- actual-backed count
- severity
- confidence
- proposed action
- tuning eligibility
- status
- linked implementation/replay version

## 7. Current issue register seed

### P8-ISSUE-001: global STOP masks side-specific opportunity

- category: classifier logic / over-suppression
- status: open hypothesis
- observed: `no_trade_flags`が存在するとside別評価前に`STOP_OR_EXIT`を返す
- effect: LongとShortの両方が同時STOPになり、Short zoneが機能しても`B_CHECK_15M`または`C_WATCH_ZONE`へ進まない
- current evidence: source inspection + one human-observed screenshot case
- action: P8で同種ケースを自動集計し、side-specific STOP hypothesisをoffline replayする
- prohibition: single caseだけでproduction classifierを変更しない

### P8-ISSUE-002: main decision and Big Chance hierarchy is unclear

- category: UI / operator comprehension
- status: confirmed usability issue
- observed: main `WAIT` / shadow `STOP_OR_EXIT`と、Big ChanceのLong候補が同一画面で競合する
- effect: 補助仮説がentry推奨に見える
- action: UI改善候補としてP8 reviewへ登録する。Big Chanceをentry permissionとして扱わない

### P8-ISSUE-003: raw classifier payload is exposed to the operator

- category: UI / explainability
- status: confirmed usability issue
- observed: slash区切りのinternal fieldsが人間向けcardへ露出
- effect: side、理由、次行動が理解しにくい
- action: human summaryとtechnical detailsを分離する候補

### P8-ISSUE-004: side identity is not sufficiently visible on STOP cards

- category: UI / actionability
- status: confirmed usability issue
- effect: 2枚のSTOPがLong/Shortのどちらか直感的に分かりにくい
- action: card headerでsideとactionを明示する候補

### P8-ISSUE-005: manual-trial doctrine was misunderstood as full manual logging

- category: operations / documentation
- status: corrected by this specification
- correct doctrine: market resultとactual tradeは自動評価し、人間は曖昧な意図だけを補う

## 8. Operating cadence

### Every notification

- event-time prediction snapshotを保持
- scenario identityへ接続
- production behaviorは変更しない

### Daily automatic run

- maturity済みoutcomeを評価
- trial fact viewを更新
- unresolved coverageを更新
- issue candidateを増分集計
- threshold/gateを変更しない

### Weekly deterministic + AI review

- deterministic weekly reportを先に作る
- AIがtop issues、原因仮説、必要な追加証拠を整理
- AIは変更を実行しない
- 重要な新規issueだけ人間へ提示

### Every two weeks or on-demand actual import

- userがlocal exportを配置
- importer / episode / linker / ground-truthを実行
- actual-backed metricsでproxyを補正
- ambiguous linkだけreview queueへ出す

### Immediate stop/review

次はサンプル数を待たずに試験を停止または修正する。

- data leakage
- privacy leak
- wrong identity join
- duplicate counting defect
- future evidence contamination
- UIがLong/Shortを逆に表示
- safety boundaryが消える
- runtime/mail behaviorが意図せず変化

## 9. P8 completion and P9 entry gates

### Initial P9 review eligibility

次を満たすと、shadow/manual layerの最初のtuning proposalを作成できる。

- manual decision eventsまたは同等のresolved scenario events: 100以上
- actual entry episodes: 30以上
- A/B/C/STOP、long/short別集計が可能
- scenario deduplicationが安定
- no_ohlcv / unresolvedが別管理
- actual trade linksはhigh / medium / manual-confirmedだけをactual-backed集計へ使用
- current classifier/versionとevaluation cutoffが再現可能

この段階ではproduction gate変更を承認しない。

### Practical tuning eligibility

次を満たすと、より強いproduction-adjacent proposalを検討できる。

- manual decision eventsまたは同等のresolved scenario events: 200以上
- actual entry episodes: 50以上
- PF 1.50以上を目標として評価
- average R +0.30R以上を目標として評価
- long/short、regime、setup別に極端な悪化がない
- newest validation windowで改善が再現
- explicit human approval

### Insufficient segment rule

aggregateで十分でも、特定side/regime/setupの標本が不足する場合、そのsegmentの変更は保留する。

## 10. P9 tuning process

### Step 1: Freeze evidence cutoff

proposalごとに次を固定する。

- data cutoff
- input fingerprints
- classifier version
- evaluation version
- included / excluded rows
- unresolved reason counts

### Step 2: Build evidence matrix

各issueについて次を比較する。

- occurrence count
- actual-backed count
- proxy-only count
- long/short
- regime
- setup family
- current behavior
- expected alternative behavior
- win rateだけでなくPF / R / MFE / MAE
- missed opportunity / avoided loss proxy
- notification burden

### Step 3: Separate change class

変更候補を混ぜない。

1. data quality / identity bug
2. UI / wording / hierarchy
3. shadow classifier logic
4. comparison threshold
5. production gate
6. notification trigger
7. runtime behavior

UI修正とtrading logic変更を同一taskにしない。

### Step 4: Offline candidate replay

変更候補はcurrent baselineと比較する。

- CURRENT_STRICT
- current A/B/C/STOP
- proposed candidate
- side-specific breakdown
- regime/setup breakdown
- duplicate notification impact
- missed opportunity
- false positive
- STOP effectiveness

### Step 5: Validation window

同じデータだけで改善を証明しない。

- proposal作成に使った期間と、最新の未使用validation期間を分ける
- validation期間が不足する場合はshadow継続
- aggregate改善だけで特定sideが悪化する変更は採用しない

### Step 6: Human approval

proposalには最低限次を含める。

- change summary
- evidence
- expected benefit
- known risk
- affected files/functions
- rollback
- validation
- shadow duration
- production impact

人間承認前はcode/configを変更しない。

### Step 7: Bounded implementation

承認後も一つの整合したchange classだけを実装する。

- targeted tests
- historical replay
- diff check
- local commit
- checkpoint when required

### Step 8: Shadow observation

production behaviorを変える前に、可能な限りshadowで再評価する。

### Step 9: Production decision

production threshold、gate、notification、runtime変更は別のexplicit approval taskとする。

## 11. Automatic vs AI vs human decision table

| Action | Automatic | AI | Human approval |
|---|---|---|---|
| prediction snapshot | yes | no | no |
| OHLCV outcome evaluation | yes | explanation only | no |
| actual trade import after files are placed | yes | no | export placement |
| trade-to-signal linking | yes | ambiguous explanation | ambiguous only |
| issue count / metrics | yes | summary | no |
| improvement candidate generation | deterministic flags | yes | no |
| threshold/gate mutation | no | proposal only | required |
| UI wording change | no | proposal only | required |
| notification change | no | proposal only | required |
| runtime restart | no | no | required |
| automatic order | prohibited | prohibited | outside current scope |

## 12. Non-negotiable safety and quality rules

- report-only
- not `FORMAL_GO`
- no automatic order
- no private/account/order endpoints
- no API key or secret handling
- raw exchange exports remain local and uncommitted
- no `paper_positions.csv` integration
- no automatic threshold mutation
- no tuning from one example
- no unresolved/no_ohlcv rows in win-loss claims
- no fill count as trade count
- no future outcome leakage
- no candidate row count as independent opportunity count
- no actual performance claim from low/ambiguous links
- human decides manually

## 13. Definition of completion

P8/P9 operating loop is properly organized when:

1. Human does not manually write every prediction result.
2. Market-path outcomes are evaluated automatically.
3. Actual trades are imported and linked automatically from local exports.
4. Human input is limited to ambiguous intent and exceptional cases.
5. Current and recurring issues live in a persistent issue register.
6. Daily, weekly, and ground-truth refresh reports are reproducible.
7. AI explains and proposes but does not self-modify production behavior.
8. Tuning starts only at explicit evidence gates.
9. Every approved change has offline replay, validation evidence, and rollback.
10. Automatic trading remains a separate future program, not a continuation assumed by P8/P9.
