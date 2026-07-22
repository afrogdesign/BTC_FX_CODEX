---
title: M計画・実装済み機能と運用仕様
date: 2026-07-22
tags:
  - btc_monitor
  - macro-structure
  - implemented-features
  - manual-trading
  - report-only
---

# M計画・実装済み機能と運用仕様

## 1. 文書の目的

この文書は、`btc_monitor`のM計画で現在実装・受入・運用されている機能を、ユーザー価値、入力、処理、出力、失敗時の挙動、安全境界まで含めて整理した実装概要である。

対象は次の流れである。

```text
公開15m / 1H / 4H OHLCV
→ macro snapshot
→ chronological history
→ 4H-first operator
→ horizontal zones
→ trendline / channel
→ structural events
→ scenario hypotheses
→ fixed latest entry
→ public URL / notification mail integration
→ scenario outcome stats shadow
→ health status
→ 人間が15分足を確認してmanual trading判断
```

自動注文は行わない。

> [!important]
> 初期計画書や個別module specには、作成時点の`next`、`not started`、`implementation pending`が残っている場合がある。現在の実装・運用状態は、`CURRENT_STATE.md`、runtime status、生成artifact、archive済みacceptance specを優先する。

---

## 2. 現在の完成状態

| 項目 | 状態 |
|---|---|
| 公開15m / 1H / 4Hデータ取得 | 稼働中 |
| macro snapshot生成 | 稼働中 |
| chronological history生成 | 稼働中 |
| 4H-first operator HTML | 実装・稼働中 |
| 水平support / resistance | 実装済み |
| trendline / channel | 実装済み |
| structural event | 実装済み |
| condition / confirmation / invalidation scenario | 実装済み |
| 固定`latest.html`入口 | 実装・稼働中 |
| 公開固定URL | 実装・稼働中 |
| 既存notification mailとの接続 | 実装・稼働中 |
| runtime health | 実装・稼働中 |
| M-STATS1 outcome counts shadow | 実装・稼働中 |
| 十分な統計サンプル | 未蓄積、`insufficient` |
| 自動売買 | 対象外・無効 |

---

## 3. ユーザー利用フロー

通常の利用手順は次のとおりである。

1. macro runtimeが公開市場データから最新構造を生成する。
2. operator HTMLへ4H大局構造を描画する。
3. 固定`latest.html`と固定公開URLを更新する。
4. 既存notification logicが送信を承認した場合だけメールを送る。
5. 受信者がメール内の4H大局チャートURLを開く。
6. cutoff、freshness、healthを確認する。
7. 水平zone、trendline、channelを確認する。
8. touch、break、acceptance、retestなどの構造eventを確認する。
9. condition、next confirmation、invalidationを持つscenarioを確認する。
10. supplemental 15m chartを確認する。
11. 人間が取引するかどうかを判断する。

この流れにおいて、システムが注文を作成、送信、変更、取消することはない。

---

# Part A. M-OPS分析・運用基盤

## 4. 公開OHLCV取得

### 4.1 対象時間足

- 15分足
- 1時間足
- 4時間足

### 4.2 入力境界

- 公開市場データのみを使用する。
- private、account、position、order endpointを使用しない。
- 各runtime cycleで各時間足を1回だけ取得する。
- 同一cycle内で取得した15mと4Hを、snapshotとoperatorで再利用する。

### 4.3 staging

取得データは一時directoryへ書き、3時間足がすべて揃った場合だけ次へatomic promotionする。

```text
local/runtime/macro_structure_inputs/latest/
  ohlcv_15m.csv
  ohlcv_1h.csv
  ohlcv_4h.csv
```

途中失敗した不完全な入力setを`latest`として公開しない。

---

## 5. M-OPS1：macro snapshot

macro snapshotは、最新の大局構造を1つのstructural checkpointとして生成する。

### 5.1 主な出力

- current price
- structure state
- price location
- 1H / 4H由来の水平level
- support / resistance role
- reliability score / band
- lifecycle
- nearest reliable support / resistance
- next upside / downside target
- obstruction
- volatility state
- expansion risk
- directional activation
- stale status
- continuity status
- data quality status
- reason codes

### 5.2 水平levelの特徴

各levelは安定した`level_id`を持ち、次を保持する。

- low / high / center
- source timeframe
- first seen
- last confirmed
- touch count
- rejection count
- break count
- reclaim count
- current role
- lifecycle
- reliability score
- reliability band
- current priceからの距離

### 5.3 安全な解釈

- directional activationは注文許可ではない。
- reliabilityは既存計算をそのまま使用し、visual moduleの都合で変更しない。
- `insufficient`、`stale`、`discontinuous`を強いpositive表現へ変換しない。

---

## 6. M-OPS2：chronological history

snapshotの時系列変化を保存し、現在の構造がどのように変化したかを追跡する。

### 6.1 追跡内容

- structure state変化
- price location変化
- reliability upgrade / downgrade
- support / resistance role change
- lifecycle change
- geometry change
- level absence
- level reappearance
- stale / discontinuous reevaluation

### 6.2 特徴

- snapshot run IDとhistory IDを保持する。
- 現在のsnapshotがhistoryに含まれることを検証する。
- current snapshotとhistoryが一致しない場合はoperator生成をfail closedする。
- 過去の変化を後から都合よく書き換えない。

---

## 7. M-OPS3：operator artifact

分析結果を人間が確認できるself-contained HTMLへ変換する。

### 7.1 immutable出力

各operator artifact directoryには次を保存する。

```text
macro_structure_operator.html
macro_structure_operator.json
macro_structure_operator.md
run_manifest.json
```

### 7.2 artifactの特徴

- immutable directory
- deterministic artifact ID
- stable JSON serialization
- inline SVG
- external JavaScriptなし
- external imageなし
- external fontなし
- external stylesheetなし
- machine固有absolute pathなし
- 同一inputは同一outputを再利用可能
- 同一IDでbytesが異なる場合はconflictとしてfail closed

### 7.3 primary hierarchy

現在のoperator画面は概ね次の順序で表示する。

```text
1. status / safety / health
2. 4H Macro Structure Chart
3. horizontal zone evidence
4. diagonal trendline / channel evidence
5. Structural events
6. Scenario hypotheses
7. supplemental 15m manual-confirmation view
8. chronological changes / evidence / limitations
```

---

# Part B. Visual Product v1

## 8. M-VIS1：4H-first macro chart

### 8.1 目的

15分足から直接判断を始めるのではなく、最初に4時間足の大局構造を確認できる画面を提供する。

### 8.2 表示内容

- 4H candles
- current price line
- high / medium support zones
- high / medium resistance zones
- zone source timeframe
- reliability band
- lifecycle
- zone ID
- target / obstruction geometry
- cutoff UTC / JST
- evaluation UTC / JST
- stale status
- continuity status
- data quality
- report-only safety banner

### 8.3 1H・4H zone表示

水平zoneには生成元時間足を表示する。

例：

- `4H`
- `1H+4H`

これにより、15分足由来の短期線を大局levelと誤認しない。

### 8.4 低品質証拠の扱い

- low reliability levelをhigh / medium zoneとして昇格表示しない。
- level不足時は推測zoneを作らない。
- `insufficient`を正常な情報不足状態として表示する。

### 8.5 15分足補助表示

4H chartの後に15m viewを残す。

目的は、4Hで大局を確認したあとに、manual entry timingを人間が確認することである。

Entry / SL / TPを自動生成する機能ではない。

---

## 9. M-LINE1：trendline / channel

### 9.1 trendline種類

生成する基準lineは次の2種類である。

| kind | anchor |
|---|---|
| `ascending_support` | 2つのconfirmed 4H swing low |
| `descending_resistance` | 2つのconfirmed 4H swing high |

### 9.2 event-time correctness

- confirmed 4H pivotだけを使用する。
- pivotは`confirmation_timestamp`以後にのみ利用可能とする。
- pivot timestampへ確認結果を遡及表示しない。
- future-confirmed pivotを使用しない。

### 9.3 line情報

各lineは次を保持する。

- line ID
- kind
- state
- anchor 1 / anchor 2 pivot ID
- anchor timestamp
- anchor confirmation timestamp
- slope per 4H bar
- anchor span bars
- touch count
- touch timestamps
- break timestamp
- current line value
- priceからの距離
- ATR換算距離

### 9.4 line state

| state | 意味 |
|---|---|
| `active` | 有効でdistinct touch clusterが2 |
| `tested` | distinct touch clusterが3以上 |
| `broken` | wrong-sideへ4H終値で明確にbreak |
| `invalidated` | anchor間のprice pathとgeometryが矛盾 |
| `insufficient` | 確定証拠不足 |

broken lineは後からactiveへ戻さない。reclaimやretestはevent moduleで別に追跡する。

### 9.5 chart表示上限

- line modelはkindごとに上位3候補まで保持する。
- chartはkindごとに最大2本を表示する。
- 全体の表示lineは最大4本。
- active / testedをsolidで表示する。
- recent brokenをdashedで表示する。
- 候補不足時に推測lineを引かない。

### 9.6 channel

- ascending channel
- descending channel
- base line
- opposite confirmed pivot
- upper / lower boundary
- channel width
- width ATR
- current position percent
- stable channel ID

channel幅が小さすぎる、または大きすぎる場合は生成しない。

---

## 10. M-EVENT1：structural events

horizontal zoneとdisplayed trendlineに対して、現在までに起きた構造変化をeventとして生成する。

### 10.1 event一覧

| event type | 意味 |
|---|---|
| `approach` | objectへ接近中 |
| `touch` | zone / lineへ接触 |
| `clean_rejection` | 明確な反発 |
| `break` | wrong-sideへ終値break |
| `closed_candle_acceptance` | 2本連続終値でbreak側へ定着 |
| `false_break_reclaim` | acceptance前に元側へ回帰 |
| `retest` | acceptance後にobjectへ再接触 |
| `retest_hold` | retest後にbreak方向を維持 |
| `retest_failure` | retest後に元側へ戻る |
| `higher_high` | confirmed highが切り上がる |
| `higher_low` | confirmed lowが切り上がる |
| `lower_high` | confirmed highが切り下がる |
| `lower_low` | confirmed lowが切り下がる |

### 10.2 event model

各eventは次を持つ。

- event ID
- event type
- event status
- sequence status
- event timestamp
- object kind
- object ID
- related object ID
- parent event ID
- direction
- price
- object geometry
- distance ATR
- interaction count
- reason codes

### 10.3 sequence追跡

objectごとに1つのactive break sequenceだけを持つ。

```text
neutral
→ break pending
→ acceptance または false-break reclaim
→ retest
→ retest hold または retest failure
```

これにより、同じclose、touch、breakを重複計上しない。

### 10.4 ongoingとconfirmed

- `approach`はcutoff時点のongoing state。
- touch以降の確定eventはconfirmed state。
- chart markerとevent listは同じevent IDを参照する。

### 10.5 retentionと表示

- modelは最新48 eventsまで保持する。
- pivot structure eventsは最新8件まで。
- event listは最大12件。
- chart markerは最大8件。

---

## 11. M-HYP1：scenario hypotheses

### 11.1 目的

現在の構造から「何が起きるとscenarioが継続し、何が起きると否定されるか」を短く表示する。

scenarioは予測断定やentry signalではなく、観測手順である。

### 11.2 scenario families

| scenario type | 内容 |
|---|---|
| `break_resolution_watch` | breakがacceptanceになるかreclaimになるかを監視 |
| `accepted_break_continuation` | acceptance後の継続を監視 |
| `failed_break_reversal` | false break / retest failure後の反対方向候補 |
| `boundary_reaction_watch` | zone / trendlineでの反応を監視 |
| `pivot_structure_continuation` | HH+HLまたはLH+LLの構造継続 |

### 11.3 必須情報

各scenarioは必ず次を持つ。

- scenario ID
- scenario type
- `watch` / `active`
- `UP` / `DOWN`
- trigger timestamp
- primary object kind / ID
- supporting event IDs
- condition
- next confirmation
- invalidation
- reason codes

### 11.4 表示上限とconflict suppression

- 最大3 scenarios。
- 最上位candidateのdirectionをdominant directionとする。
- 追加scenarioはdominant directionと同方向だけを表示する。
- 反対方向candidateはsuppressed countへ回す。
- 同じscenario typeを重複表示しない。
- 同じsupporting eventを共有する候補は上位だけを表示する。

同じ画面で、UP継続とDOWN継続を同時に断定しない。

### 11.5 禁止表現

scenario modelとHTMLでは次を使用しない。

- probability / 確率
- win rate / 勝率
- confidence percentage
- buy / sell
- long / short
- entry
- stop loss / SL
- take profit / TP
- order permission

---

## 12. M-ENTRY1：fixed latest entry

### 12.1 固定ローカルpath

```text
local/reports/macro_structure/operator/latest.html
```

ユーザーはartifact IDごとのdirectoryを探さず、常にこのpathから最新画面を開ける。

### 12.2 available entry

complete operator HTMLが正常生成された場合だけ、available entryをatomic publicationする。

completeの最低条件：

- status / safety banner
- 4H chart
- horizontal zones
- diagonal structure
- structural events
- scenario hypotheses
- supplemental 15m view
- report-only safety wording

### 12.3 unavailable entry

新しいcomplete画面を生成できなかった場合、古い成功画面を無条件に現在の正常画面として残さない。

代わりに次を表示する。

```text
Macro Structure Latest Entry Unavailable
```

表示内容：

- stable error code
- current attemptではcomplete entryが公開されなかったこと
- report-only safety
- previous成功artifactが安全に解決できる場合だけhistorical reference

### 12.4 publication方式

- regular UTF-8 HTML
- self-contained
- JavaScript fetchなし
- iframeなし
- meta refreshなし
- external assetなし
- symlinkなし
- temporary fileへcomplete write
- flush / fsync
- `os.replace`相当でatomic replacement

### 12.5 freshness注意

fixed entryの存在は市場データの鮮度を保証しない。

画面上のcutoff、evaluation、stale、continuity、data qualityを確認する必要がある。

---

# Part C. Delivery

## 13. M-DELIVERY1：public URL publication

### 13.1 固定公開URL

```text
https://server.afrog.jp/btc-monitor/notifications/macro-structure/latest.html
```

URLはnotificationごとに増やさず、固定URLを更新する。

### 13.2 publication source

```text
/Users/marupro/CODEX/100_MCP_Server/btc_monitor/local/reports/macro_structure/operator/latest.html
```

### 13.3 source validation

remote publication前に次を検証する。

- regular file
- non-symlink
- UTF-8
- non-empty
- size上限内
- availableまたはunavailableのどちらか一方
- fixed entry marker
- entry ID
- cutoff / stale / continuity / data quality
- required 4H / event / scenario / 15m sections
- report-only safety wording
- secret markerを含まない

### 13.4 atomic remote publication

```text
validate local latest.html
→ compute SHA-256
→ create remote macro-structure directory
→ rsync to deterministic temporary basename
→ remote atomic rename to latest.html
```

失敗時：

- previous remote `latest.html`を削除しない。
- raw SSH / rsync stderrを公開metadataへ入れない。
- stable error codeだけを返す。

---

## 14. notification mail integration

### 14.1 送信判断

M-DELIVERY1は通知送信を決めない。

既存の`should_notify`だけが送信を決定する。

変更しないもの：

- notification cadence
- notification kind
- suppression reason
- pending resend rule
- subject
- main / attention / followup threshold
- duplicate suppression
- recipient

### 14.2 email block

public publicationが成功した場合、既存メール本文へ固定URL blockを1つ追加する。

例：

```text
【4H大局チャート（公開URL）】
https://server.afrog.jp/btc-monitor/notifications/macro-structure/latest.html
状態: available / cutoff JST=... / stale=... / continuity=... / data_quality=...
固定URLの存在は鮮度を保証しません。時刻と状態を確認してください。
```

### 14.3 unavailable時

unavailable entryが正常公開された場合：

- URLは表示できる。
- 状態は`unavailable`と明示する。
- 過去成功画面を現在成功として表現しない。

### 14.4 publication failure時

- URLを追加しない。
- stable error codeだけを表示する。
- 既存logicが承認済みのメール送信は妨げない。

### 14.5 duplicate抑止

- public URL成功がメールを強制送信しない。
- public URL失敗が承認済みメールを抑止しない。
- URLは固定なのでnotificationごとのURL増殖がない。

---

# Part D. Runtime and Health

## 15. macro runtime service

### 15.1 LaunchAgent

```text
com.afrog.btc-macro-structure
```

### 15.2 WorkingDirectory

```text
/Users/marupro/CODEX/100_MCP_Server/btc_monitor
```

### 15.3 schedule

JSTで1日6回。

- 01:10
- 05:10
- 09:10
- 13:10
- 17:10
- 21:10

UTC整列4H candle closeの10分後に実行する。

### 15.4 runtime core order

```text
public OHLCV fetch
→ snapshot
→ history
→ operator
→ scenario stats shadow
→ health
```

core success gateは次の3工程である。

```text
snapshot
history
operator
```

### 15.5 lock

non-blocking target-only lockを使用する。

前回cycleが実行中の場合は新しい処理を開始せず、`already_running`を返す。

### 15.6 runtime status

```text
logs/runtime/macro_structure_service_last_result.json
```

主なfield：

- started / finished UTC・JST
- evaluation UTC・JST
- symbol
- step status
- return code
- snapshot run / snapshot ID
- history ID
- operator artifact ID
- latest entry status / ID
- stale / continuity / data quality
- public input fingerprints
- scenario stats generation
- safety flags

runtime statusへ次を入れない。

- secrets
- raw market rows
- stdout / stderr
- exception text
- account data
- order data

---

## 16. health status

healthはruntimeと成果物の整合性を確認する。

### 16.1 確認対象

- runtime status
- snapshot artifact
- history artifact
- operator artifact
- operator HTML
- fixed latest entry
- public input fingerprints
- stale status
- continuity status
- data quality
- displayed zone counts
- LaunchAgent plist contract
- report-only safety flags

### 16.2 health states

- `healthy`
- `healthy_insufficient`
- `degraded`
- `overdue`
- `failed`
- `inconsistent`
- `unavailable`

### 16.3 特徴

- health failureはcore runtime statusを後からsuccessへ書き換えない。
- health generationはruntime status保存後に実行する。
- stats shadow failureでもhealth generationを継続する。
- health状態は注文許可ではない。

---

# Part E. M-STATS1

## 17. scenario outcome counts shadow

### 17.1 目的

生成済みscenarioが、その後どのような構造結果になったかを6H / 12H / 24Hで集計する。

これはhistorical win-rate engineではなく、現在蓄積されるimmutable operator artifactsに対するbounded outcome countである。

### 17.2 input

```text
local/reports/macro_structure/operator/operator_*/macro_structure_operator.json
```

### 17.3 output

```text
local/reports/macro_structure/scenario_stats/
  <artifact_id>/
    macro_structure_scenario_outcome_stats.json
    macro_structure_scenario_outcome_rows.csv
    macro_structure_scenario_outcome_stats.md
    run_manifest.json
  latest.json
```

### 17.4 horizon

- 6H
- 12H
- 24H

各horizonはtarget時刻以降、1つの4H cadence以内にある最初の有効artifactを使用する。

該当artifactがない場合は`immature`とする。

### 17.5 outcome

| outcome | 意味 |
|---|---|
| `continuation` | confirmationがinvalidationより先 |
| `rejection` | invalidationが先、または同時刻 |
| `indeterminate` | horizonまでに決定eventなし |
| `immature` | horizon評価に必要な後続artifact不足 |

同timestampではrejectionを優先する。

### 17.6 group

次の組合せごとに独立集計する。

```text
scenario_type × direction
```

各groupは次を持つ。

- outcome counts
- mature row count
- evidence strength

### 17.7 evidence strength

| mature rows | evidence strength |
|---:|---|
| 20未満 | `insufficient` |
| 20以上 | `descriptive_only` |

overall mature countが20以上でも、個別groupが20未満ならそのgroupは`insufficient`である。

### 17.8 identity conflict

全artifactは1つのimmutable identity namespaceとして扱う。

- 同じ`event_id`でpayloadが異なる場合はfail closed。
- 同じ`scenario_id`でpayloadが異なる場合はfail closed。
- 同一payloadのrepeatはdeterministicに処理する。

### 17.9 禁止出力

- probability
- win rate
- confidence percentage
- buy / sell
- long / short
- entry
- SL / TP
- order permission

### 17.10 non-blocking runtime

statsはoperator成功後に1回だけ実行する。

statsが失敗しても次を変更しない。

- core runtime success
- core process exit code
- snapshot
- history
- operator
- fixed latest entry
- health generation

runtime statusにはprivacy-safeな次だけを保存する。

- attempted
- published / failed / not_run
- artifact ID
- evidence strength
- mature row count
- source artifact count
- excluded artifact count
- stable error code

### 17.11 現在のevidence

2026-07-22に直接確認された状態：

- artifact ID: `ef3dc500f1368a83912e`
- source artifact count: `4`
- excluded incompatible / legacy artifacts: `8`
- mature rows: `0`
- evidence strength: `insufficient`

現段階では統計的判断材料ではなく、今後の自動蓄積を開始した状態である。

---

# Part F. Fail-closed and Safety

## 18. fail-closed方針

次のような不整合では、既存の正常成果物やlatest pointerを安易に更新しない。

- non-monotonic timestamp
- invalid OHLC
- snapshot / history identity mismatch
- missing current snapshot in history
- zone geometry reversal
- line ID collision
- event ID collision
- scenario ID collision
- future event timestamp
- missing event / parent / object reference
- invalid fixed entry source
- publication staging failure
- atomic replacement failure
- stats identity conflict

候補不足やsample不足はfailureではなく`insufficient`として扱う。

---

## 19. safety boundary

常に維持する。

- report-only
- human decides manually
- no automatic order
- not `FORMAL_GO`
- no API keys or secrets in artifacts
- no private / account / order endpoints
- no raw exchange export commit
- no unapproved `paper_positions.csv` integration
- no automatic Entry / SL / TP
- no probability-based execution permission
- no unapproved gate / score / threshold / classifier change
- no future-confirmed pivot backdating

---

## 20. 実装していない機能

- automatic order placement
- automatic position management
- automatic Entry selection
- automatic SL / TP selection
- account balance retrieval
- open position retrieval
- order history retrieval
- private exchange API
- probability-based direction prediction
- historical win-rate execution gate
- Elliott Wave numbering
- human freehand trendlineの完全再現
- fully autonomous trading decision

---

# Part G. Current Paths and References

## 21. 主要path

### Primary repo

```text
/Users/marupro/CODEX/100_MCP_Server/btc_monitor
```

### Fixed local entry

```text
/Users/marupro/CODEX/100_MCP_Server/btc_monitor/local/reports/macro_structure/operator/latest.html
```

### Fixed public URL

```text
https://server.afrog.jp/btc-monitor/notifications/macro-structure/latest.html
```

### Runtime status

```text
logs/runtime/macro_structure_service_last_result.json
```

### Stats output

```text
local/reports/macro_structure/scenario_stats
```

### Health output

```text
local/reports/macro_structure/health
```

---

## 22. 主要method versions

| 機能 | method version |
|---|---|
| operator artifact | `macro_structure_operator_artifact.v2` |
| trendline | `macro_structure_trendline.v1` |
| structural events | `macro_structure_structural_events.v1` |
| scenario hypotheses | `macro_structure_scenarios.v1` |
| fixed latest entry | `macro_structure_latest_entry.v1` |
| public delivery | `macro_structure_public_delivery.v1` |
| runtime service | `macro_structure_runtime_service.v1` |
| health | `macro_structure_health_status.v1` |
| scenario outcome stats | `macro_structure_scenario_outcome_stats.v1` |

---

## 23. 受入済みcheckpoint / report locator

| 項目 | locator |
|---|---|
| M-VIS1 | `c1ceda3` |
| M-LINE1 | `77b9ca3` |
| M-EVENT1 | `a79e488` |
| M-HYP1 | `e06fb99` |
| M-ENTRY1 | `475ae4d` |
| M-DELIVERY1 initial | `311bf00` |
| M-DELIVERY1 hardening | `9409551` |
| runtime delivery correction | `bc61478` |
| runtime completion state | `601dfc4` |
| notification runtime reload state | `7fe196a` |
| M-STATS1 evaluator FIX1 | `68ed430` |
| M-STATS1 runtime shadow | `c4d9a4a` |
| M-STATS1 state acceptance | `bfedf9b` |

> [!note]
> safe public workspaceから`.git` objectを直接読めない場合、上記hashはreport locatorとして扱う。実装・artifact・stateのacceptanceは、source、tests、runtime status、生成artifactの直接reviewに基づく。

---

## 24. 現在の運用上の結論

M計画のvisual product、固定入口、公開URL、notification mail連携、runtime、health、M-STATS1 shadowは実装・受入済みである。

現在のシステムは次の役割を持つ。

```text
4時間足で大局構造を整理する
→ 重要な水平・斜め構造を表示する
→ 何が起きたかをeventとして表示する
→ 次に確認する条件と否定条件をscenarioとして表示する
→ 15分足を人間が確認する
→ 人間がmanual trading判断を行う
```

M-STATS1は自動蓄積を開始しているが、現在は`insufficient`である。sample不足は画面、通知、manual judgment workflowの利用をblockしない。


---

## 2026-07-23追補：公開URL更新とnotificationの責任分離

この追補は、本文中のruntime順序またはpublication経路に関する古い記述と矛盾する場合に優先する。

### 確定したruntime順序

```text
public OHLCV fetch
→ snapshot
→ history
→ operator
→ fixed public publication
→ scenario stats shadow
→ atomic runtime status
→ health
```

- fixed public publicationはoperator成功後、scenario stats前に1回だけ実行する。
- 公開更新はnotification送信の有無に依存しない。
- core success gateは引き続き`snapshot + history + operator`である。
- publication failureまたはdisabledは、成功済みcore status、process exit code、scenario stats、healthを妨げない。
- publication結果は`logs/runtime/macro_structure_service_last_result.json`の`public_delivery_generation`へprivacy-safeに保存する。
- 保存対象はstatus、public URL、entry status/ID、source SHA-256、cutoff、stale、continuity、data quality、stable error codeに限定する。
- SSH host、key path、remote path、stdout、stderr、exception全文、raw HTML、secretは保存しない。

### notification側の責任

```text
existing should_notify
→ recorded public_delivery_generationをread-only取得
→ fixed URL blockを追加
→ existing email send
```

notification runtimeはmacro pageについて次を実行しない。

- SSH
- rsync
- remote rename
- local fixed-entry validation
- publication retry

missingまたはinvalidなruntime publication statusは、compactな利用不可表示へ変換する。既に承認されたメール送信は抑止しない。

### 受入証拠

- implementation locator: `ae6969e`
- focused FIX1 locator: `c4d7caf`
- accepted entry ID: `113cbd20a4345818f644`
- local/public entry ID: 一致確認済み
- public URL: `https://server.afrog.jp/btc-monitor/notifications/macro-structure/latest.html`
- report-only: `true`
- automatic order allowed: `false`
- 新規LaunchAgent、plist変更、schedule変更、notification reload、SMTP test、notification cycleは実施していない。
- FIX1ではruntime、health、publication、public GETを再実行していない。
