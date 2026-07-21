---
title: M-ENTRY1・固定latest HTML入口実装仕様
date: 2026-07-22
tags:
  - btc_monitor
  - macro-structure
  - fixed-entry
  - atomic-publication
  - report-only
---

> [!abstract]
> M-VIS1からM-HYP1までを含むcomplete operator HTMLを、毎回同じローカルpathから開ける固定入口として公開する。成功時はcomplete self-contained HTMLをatomic replacementし、生成失敗時は古い正常画面を無条件に「現在の最新正常」と見せず、明示的なunavailable状態へ切り替える。immutable operator artifact、既存`latest.json`、report-only安全境界は維持する。

## 目的

ユーザーが毎回artifact directoryを探さず、次の固定pathを開いて4H大局から15m確認まで進めるようにする。

```text
local/reports/macro_structure/operator/latest.html
```

既定output root以外では、同じ規則で次を使う。

```text
<output_root>/latest.html
```

この入口はローカルのuser-facing entryであり、mail、notification、runtime、LaunchAgentの変更ではない。

## 前提

M-ENTRY1は次のaccepted moduleを再実装しない。

- M-VIS1 4H-first chart
- M-LINE1 trendline / channel
- M-EVENT1 structural events
- M-HYP1 condition / confirmation / invalidation scenarios

固定入口はaccepted operator HTMLを公開するだけで、zone reliability、line geometry、event state、scenario selectionを変更しない。

## method identity

```text
schema_version = macro_structure_latest_entry.v1
method_version = macro_structure_latest_entry.v1
```

固定入口のidentityはoperator artifact identityとは分離する。

### available entry ID

```text
entry_id = sha256(
  "macro_structure_latest_entry.v1|available|"
  "<operator_artifact_id>|<source_digest>"
)[:20]
```

### unavailable entry ID

```text
entry_id = sha256(
  "macro_structure_latest_entry.v1|unavailable|"
  "<error_code>|<last_success_artifact_id>|<last_success_source_digest>"
)[:20]
```

同じ入力と状態から同じentry IDとHTML bytesを生成する。wall-clock現在時刻をidentityまたは本文へ追加しない。

## 固定入口の形式

- regular UTF-8 HTML file
- self-contained
- JavaScript fetchなし
- iframeなし
- meta refreshなし
- external asset依存なし
- symlinkなし
- fixed fileからimmutable artifactへの自動redirectなし
- `open <output_root>/latest.html`で直接読める

## success publication

4H inputを含むoperator renderがcompleteに成功した場合だけ、`latest.html`をavailable entryへ更新する。

### completeの定義

source immutable HTMLに次が存在すること。

- status / safety banner
- `4H Macro Structure Chart`
- horizontal zone evidence
- diagonal structure evidence
- `Structural events`
- `Scenario hypotheses`
- supplemental 15m manual-confirmation view
- report-only / no automatic order / human decides manually

不足する場合はsuccess entryを公開せずfail closedする。

### available entry content

available entryはsource immutable `macro_structure_operator.html`の全内容を保持し、`<body>`直後へ小さな固定entry bannerを追加する。

bannerに最低限表示する。

- entry method version
- entry ID
- `entry_status=available`
- source operator artifact ID
- source digest
- source cutoff UTC / JST
- source evaluation UTC / JST
- source stale status
- source continuity status
- source data-quality status
- safety boundary
- 次の注意文

```text
fixed entry availability does not imply current market freshness; verify cutoff and status
```

banner追加以外でoperator本文、chart、event、scenario、15m viewを書き換えない。

### deterministic source

available entryは、同じrender内で生成してimmutable artifactへ保存したHTML bytesだけをsourceにする。

- 後から別artifactを探索しない
- `latest.json`のpointerだけからHTMLを推測しない
- source artifact ID、source digest、cutoffは同じrender resultと一致させる

## unavailable publication

4H inputを明示したoperator renderが、validation、model construction、immutable publication、またはfixed-entry publicationの前段で失敗した場合、可能な限り`latest.html`をatomicにunavailable pageへ置換する。

### unavailable pageの役割

- complete operator画面を装わない
- current/latest正常と表現しない
- failureを明示する
- previous immutable artifactを削除しない
- existing operator `latest.json`を更新しない
- automatic orderへつながる表現をしない

### unavailable page content

最低限表示する。

- `Macro Structure Latest Entry Unavailable`
- entry method version
- entry ID
- `entry_status=unavailable`
- deterministic error code
- report-only / no automatic order / human decides manually
- 次の注意文

```text
no complete current entry was published for this attempt
```

validなprevious `latest.json`が存在し、そのartifact directoryとHTMLが安全に解決できる場合だけ次を表示する。

- last successful operator artifact ID
- last successful source digest
- last successful cutoff UTC / JST
- `historical only; not the current successful result`
- previous immutable HTMLへのrelative link

previous referenceは次を満たす場合だけ使用する。

- artifact IDはbasenameと一致するdirect child
- `operator_` prefix
- matching immutable `macro_structure_operator.html`が存在
- latest pointerのartifact IDとdirectoryが一致

invalid pointerやmissing artifactからlinkを作らない。

## no-4H compatibility

`ohlcv_4h_csv`を省略した既存callerはM-ENTRY1対象外とする。

- existing digestを維持
- existing artifact IDを維持
- existing output behaviorを維持
- `latest.html`を作成、更新、unavailable化しない
- M-HYP1以前のlegacy callerがcomplete fixed entryを15m-only画面で置換しない

## atomic replacement

固定入口のauthorityは単一file `<output_root>/latest.html`とする。

更新手順。

1. output root内のtemporary regular fileへcomplete bytesを書く
2. flushし、可能ならfile fsyncする
3. `os.replace`相当で`latest.html`へatomic replacementする
4. temporary fileを残さない

partial writeされた`latest.html`を公開しない。

同じsourceで再実行した場合、同じbytesで置換またはno-opとしてよい。

### publication order

- immutable artifact directoryをcompleteに作る
- available fixed entryをatomic replacementする
- existing operator `latest.json`をatomic publicationする

途中失敗時、successを装うfixed entryを残さないようunavailable replacementを試みる。

immutable artifact directoryが作成済みでもpointer publication前に失敗した場合、そのdirectoryは未参照immutable evidenceとして残してよい。削除やresetは行わない。

### fixed-entry write自体が失敗した場合

- render resultはfailure
- error codeは`latest_entry_publication_failed`または同等の固定code
- operator `latest.json`を新しいsuccessへ進めない
- previous `latest.html`を破損させない
- previous available entryには常にcutoffと「freshnessを保証しない」注意文があるため、それをcurrent保証として扱わない

## renderer result

4H success resultへ次を追加する。

- `latest_entry_path`
- `latest_entry_status=available`
- `latest_entry_id`
- `latest_entry_method_version=macro_structure_latest_entry.v1`
- `latest_entry_source_artifact_id`

4H failureでunavailable pageを公開できた場合。

- existing failure resultを維持
- `latest_entry_path`
- `latest_entry_status=unavailable`
- `latest_entry_id`
- `latest_entry_method_version`

no-4H resultへこれらを追加しない。

## immutable artifactとidentity

- immutable artifact directoryのfilesを変更しない
- operator schema/methodは`macro_structure_operator_artifact.v2`のまま
- operator digestへM-ENTRY1 tokenを追加しない
- same analytical inputのoperator artifact IDを変更しない
- fixed entryをimmutable manifest outputsへ追加しない
- `latest.html`はmutable user-facing entryであり、immutable evidenceではない

## fail-closed

次の場合、available fixed entryを公開しない。

- source HTML missing / non-UTF-8
- required complete section missing
- source artifact ID mismatch
- source digest mismatch
- source cutoff/evaluation mismatch
- invalid previous latest pointer
- unsafe previous artifact path
- temporary write failure
- atomic replace failure
- immutable publication failure
- operator latest pointer publication failure

invalid previous pointerはunavailable pageのlast-success linkを省略する理由であり、raw pathを表示しない。

## operator CLI route

既存operator render routeを維持する。

- 新しいnetwork fetchを追加しない
- 新しいbackground processを追加しない
- rendererが4H input付きで正常終了したとき固定入口も更新される
- 別のmanual copy commandを必須にしない

M-ENTRY1ではruntime service、schedule、LaunchAgentを変更しない。

## matching validation

最低限証明する。

1. 4H successで`<output_root>/latest.html`がregular fileとして存在する
2. available entryにentry ID、source artifact ID、source digest、cutoff、statusがある
3. complete operator sectionsが全て残る
4. scenario condition / next confirmation / invalidationが残る
5. report-only / no automatic order / human decides manuallyが残る
6. freshnessを保証しない注意文がある
7. JavaScript fetch、iframe、meta refresh、external redirectがない
8. same inputでentry IDとHTML bytesが同じ
9. fixed entry bytesはpartial publicationされない
10. immutable source artifactは変更されない
11. operator artifact IDとdigestはM-ENTRY1導入前の同input identityを維持する
12. invalid 4H render後、operator `latest.json`はprevious successを維持する
13. invalid 4H render後、fixed entryはunavailableを明示する
14. unavailable pageはprevious successをhistorical onlyと表示する
15. valid previous artifactだけにrelative linkを作る
16. invalid previous pointerからunsafe linkを作らない
17. previous successがないfailureでもunavailable pageを作れる
18. fixed-entry atomic replace failureはrender failureとなりprevious fileを破損しない
19. no-4H callerはfixed entryを作成・更新しない
20. generated fixed pathを`open`対象として案内できる

## bounded smoke

既存local inputを使い、fetchやpipeline再実行なしで1回だけ生成する。

```text
snapshot root: local/reports/macro_structure
history root: local/reports/macro_structure/history
15m input: local/runtime/macro_structure_inputs/latest/ohlcv_15m.csv
4h input: local/runtime/macro_structure_inputs/latest/ohlcv_4h.csv
output root: local/reports/macro_structure/mentry1_review/operator
fixed entry: local/reports/macro_structure/mentry1_review/operator/latest.html
```

確認する。

- immutable complete artifact
- existing `latest.json`
- fixed `latest.html`
- entry status available
- source artifact identity一致
- 4H chart、zones、diagonal、events、scenarios、15m view
- no fetch / iframe / redirect
- report-only safety

失敗状態はunit fixtureで検証し、smokeのためにaccepted local inputを破壊しない。

## 対象外

- runtime / LaunchAgent / schedule変更
- mail / notification
- local web server
- cloud hosting
- network fetch
- automatic browser launch during normal render
- M-STATS1
- probability / win rate
- Entry / SL / TP
- automatic order
- zone / line / event / scenario logic変更
- private/account/order data

## Acceptance

- `open local/reports/macro_structure/operator/latest.html`相当の固定pathでcomplete画面を開ける
- success entryは完全でself-contained
- failureはunavailableとして明示される
- previous normal artifactをcurrent成功と無条件に誤認させない
- immutable evidenceとoperator identityを維持する
- no-4H compatibilityを維持する
- matching tests、1回のbounded smoke、task-scoped diff checkが通る

M-ENTRY1 acceptanceで、M-DELIVERY1を除くvisual Product v1を完成とする。M-DELIVERY1は別の明示承認なしに開始しない。
