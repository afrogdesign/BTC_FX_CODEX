---
title: "P WP2 Semantic Identity and Versioning"
date: 2026-07-25
status: implementation-authorized
work_id: P-GENERATION-ALIGNMENT-WP2
program: P
package: WP2
branch: Ver04-v5
reviewed_base: c764b289192700b4840a9c2f86461a227490d38c
safety_boundary: "report-only / spec-first / output parity / not FORMAL_GO / no automatic order / human decides manually"
---

# P WP2 — Semantic Identity and Versioning

## 1. Decision

WP0とWP1はacceptedである。WP2は、P系の証拠を将来安全に累積・比較するため、次の2契約をコード上の単一ownerとして追加する。

1. `no_trade_flags`のhard / advisory / unknown意味契約
2. program・generation・schema・methodを分離するgeneration identity / comparison契約

このWP2はcontract foundationであり、production判断や既存出力を変更しない。実装後も次は不変である。

- `trade_execution_gate`はnon-empty `no_trade_flags`を従来どおりblockする。
- `manual_operator_classifier.v4`のA/B/C/STOP判定、threshold、reason code、schema、method version、出力byteは変えない。
- unknown tokenはP5 offline classifierで従来どおりfail-closedし、`STOP_OR_EXIT`になる。
- advisory tokenは必要条件を満たす場合だけ従来どおり`C_WATCH_ZONE`になり、A/Bへ昇格しない。
- `operator_decision.v1`、notification、mail、runtime、Product P9、注文挙動は変更しない。

## 2. Verified current facts

### 2.1 Authority

- formal executionの唯一の現行authorityは`src/trade/execution_gate.py`の`determine_trade_execution_gate`である。
- P5 classifierは`offline_evaluation`であり、production gateを再計算・置換しない。
- operator decisionは`display`であり、注文許可ではない。
- notification authorityは`should_notify`系であり、今回の対象外である。

### 2.2 Existing no-trade behavior

`manual_operator_classifier.py`には現在、次のlocal constantsがある。

```text
HARD_NO_TRADE_TOKENS = {volatile_regime}
ADVISORY_NO_TRADE_TOKENS = {
  short_at_major_support_wait_only,
  long_at_major_resistance_wait_only,
  breakout_follow_candidate,
  upside_breakout_follow_watch,
  downside_breakdown_follow_watch,
  short_invalidated_by_up_break,
  long_invalidated_by_down_break,
  short_invalidation_watch,
  long_invalidation_watch
}
```

P5の現在の判定契約は次である。

```text
empty tokens                         -> no no-trade stop
all tokens are known advisory        -> advisory-only
hard token present                   -> fail-closed STOP
unknown token present                -> fail-closed STOP
advisory + hard or advisory + unknown -> fail-closed STOP
```

`execution_gate.py`はtokenの種類を解釈せず、non-emptyなら`no_trade_flags_present`でblockする。この保守的挙動を変更しない。

### 2.3 Existing version facts

- P5 schema: `manual_operator_classification.v1`
- P5 report schema: `manual_operator_classifier_report.v1`
- P5 method: `manual_operator_classifier.v4`
- operator decision schema: `operator_decision.v1`
- active plan: `active_trade_plan_v1`
- side-aware: `side_aware_mtf_action.v1`
- structural priority: `structural_priority.v1`
- versionがない現行資産は推測せず`legacy_unversioned`として扱う。
- Product P9は`program=P`, `phase=P9`である。
- Macro proposal engineは`program=M`であり、Product P9ではない。

## 3. Scope

### 3.1 Required source changes

新規packageを作成する。

```text
src/contracts/__init__.py
src/contracts/operator_semantics.py
src/contracts/generation_identity.py
```

既存source変更は次だけに限定する。

```text
src/feedback/manual_operator_classifier.py
```

### 3.2 Required tests

```text
tests/test_operator_semantics_contract.py
tests/test_generation_identity_contract.py
tests/test_manual_operator_classifier.py
```

既存testは、import compatibilityまたはparity assertionの最小変更だけ許可する。

### 3.3 Documentation included in the implementation commit

ChatGPTが先行作成した次の2ファイルをexact current contentのままstageする。

```text
chatgpt/specs/active/20260725_p_wp2_semantic_identity_and_versioning.md
docs/operations/ai-orchestration/P_GENERATION_RECONCILIATION_REPORT.md
```

後者はWP1 acceptance後も残っていた旧「未受理」文をaccepted truthへ直す1行修正だけである。Codexは再編集しない。

## 4. Out of scope

- `execution_gate.py`のpass/blocked条件変更
- opportunity gate、operator decision、notification triggerへの新しいsemantic判断の接続
- classifier threshold、class priority、reason code、output columns、schema/method version変更
- P8 manifest/evidence outputへのgeneration field追加
- cumulative evidence bank
- P9 readiness v2
- production behavior、runtime、launchd、mail、notification変更
- Product P9 activation、phase promotion、`FORMAL_GO`
- private/account/order endpointまたは注文
- Macro M-routeの変更
- frozen runtimeの読取・編集・実行

上記はWP2 acceptance後の別packageでのみ検討する。

## 5. Operator semantic contract

### 5.1 Public constants

`src/contracts/operator_semantics.py`は最低限次をexportする。

```python
SEMANTICS_SCHEMA_VERSION = "operator_no_trade_semantics.v1"
HARD_NO_TRADE_TOKENS: frozenset[str]
ADVISORY_NO_TRADE_TOKENS: frozenset[str]
```

token集合は現行P5の値と完全一致させる。追加・削除・改名・case変更を行わない。

### 5.2 Normalization

次の入力を受け取るpure functionを提供する。

```python
normalize_no_trade_tokens(value: object) -> tuple[str, ...]
```

契約:

- `None`、空文字、空collectionは`()``。
- list / tuple / setは各要素を文字列化し、trim・lowercaseする。
- 文字列は現行P5と同等にJSON list、`;`、`,`、`|`を扱う。
- 重複を除去し、sort済みtupleを返す。
- 入力を変更しない。
- malformed JSON-like stringは例外を外へ出さず、通常のdelimiter parsingへfail closedする。

### 5.3 Classification result

immutableな結果型を提供する。dataclassまたはNamedTupleを使用してよい。

必須field:

```text
schema_version
normalized_tokens
hard_tokens
advisory_tokens
unknown_tokens
has_tokens
all_advisory
fail_closed
```

pure function:

```python
classify_no_trade_tokens(value: object) -> NoTradeSemanticResult
```

契約:

```text
has_tokens = normalized_tokens is non-empty
all_advisory = has_tokens and every token is advisory
fail_closed = hard_tokens or unknown_tokens are non-empty
```

hard、advisory、unknownはmutually exclusiveに分類する。

### 5.4 Lane helpers

意味をlane authorityと混同しないため、次のhelperを別名で提供する。

```python
formal_execution_blocks_no_trade(value: object) -> bool
offline_classifier_stops_for_no_trade(value: object) -> bool
```

契約:

- `formal_execution_blocks_no_trade`はnon-emptyなら常にtrue。これは現行formal gateのparityを表すだけで、今回`execution_gate.py`へ接続しない。
- `offline_classifier_stops_for_no_trade`はhardまたはunknownがあるとtrue。known advisory-onlyはfalse。

### 5.5 P5 integration

`manual_operator_classifier.py`はlocal token集合を削除し、shared moduleからimportする。

既存外部import compatibilityを守るため、次の名前は引き続き`manual_operator_classifier`moduleから参照できなければならない。

```text
HARD_NO_TRADE_TOKENS
ADVISORY_NO_TRADE_TOKENS
```

`_tokens`の広い用途を無理に置換しない。`no_trade_flags`のsemantic判定部分だけshared contractを利用する。

既存判定の論理同値:

```text
advisory_only = semantic_result.all_advisory
if no_trade exists and not advisory_only -> STOP
```

unknown tokenをsilent advisoryへ変換してはならない。

## 6. Generation identity contract

### 6.1 Public constants

`src/contracts/generation_identity.py`は次をexportする。

```python
GENERATION_IDENTITY_SCHEMA_VERSION = "p_generation_identity.v1"
LEGACY_UNVERSIONED = "legacy_unversioned"
```

### 6.2 Identity model

immutableなidentity modelを提供する。

必須field:

```text
identity_schema_version
program
runtime_generation
source_head
schema_version
method_version
cutoff_utc
```

任意component versions:

```text
score_version
market_map_version
active_plan_version
side_aware_version
structural_priority_version
operator_decision_version
notification_trigger_version
classifier_version
replay_version
linker_version
p8_evidence_version
readiness_version
```

制約:

- `program`は`P`または`M`だけ。
- `runtime_generation`、`source_head`、`cutoff_utc`は空を許可しない。
- component versionの空・Noneは`legacy_unversioned`へ明示変換する。
- `source_head`をcurrent HEADから暗黙取得しない。callerが渡す。
- timestampはtimezone-aware ISO-8601としてvalidateする。naive timestampは拒否する。
- model生成はfilesystem、git、network、clockへアクセスしないpure operationとする。

constructor/helper名は近接styleに合わせてよいが、dict serializationをdeterministicに提供する。

### 6.3 Comparison contract

comparison resultは少なくとも次を持つ。

```text
status
comparable
baseline_reset_required
reason_codes
```

状態値:

```text
comparable
not_comparable_program
not_comparable_runtime_generation
not_comparable_schema_version
baseline_reset_required_method_version
not_comparable_legacy_unversioned
```

優先順位:

1. program mismatch
2. runtime generation mismatch
3. primary schema mismatch
4. claim-relevant fieldが`legacy_unversioned`
5. method version mismatch
6. comparable

契約:

- program mismatchは絶対に比較不可。PとMを同じP9 evidenceとして比較しない。
- runtime generation mismatchはdefault比較不可。
- schema mismatchは比較不可。
- claim-relevant versionが`legacy_unversioned`なら比較資格を自動付与しない。
- methodだけが異なる場合は`baseline_reset_required_method_version`、`comparable=false`、`baseline_reset_required=true`。
- `source_head`差だけでは自動的に性能比較不可としない。generation/schema/methodの契約で判断し、source_headはlineageとして残す。
- callerが比較対象component fieldを指定できるようにする。未指定時はprimary `schema_version`と`method_version`を使う。
- unknown component field名は例外で拒否する。

### 6.4 No current pipeline wiring

このWP2ではgeneration identityをP8、classifier report、notification、runtime payloadへ追加しない。pure contractとunit testsを先にacceptedにし、出力schema migrationは後続packageへ分離する。

## 7. Observable parity contract

実装前後で次を完全一致させる。

### 7.1 P5 classification parity

固定fixtureについて次が不変である。

- `manual_operator_classifier.v4`
- schema/report schema strings
- A/B/C/STOP class
- classification status
- reason codes
- warning codes
- threshold snapshot
- classification ID
- CSV/JSON/Markdown bytes

最低限fixture:

```text
no no-trade token
all 9 advisory tokens individually
volatile_regime
unknown_token
advisory + unknown
advisory + volatile_regime
```

### 7.2 Formal gate parity

既存`determine_trade_execution_gate`のtestで次を再確認するだけとし、sourceは変更しない。

```text
no_trade_flags=[]        -> no_trade_flags_presentなし
no_trade_flags=[known advisory] -> no_trade_flags_presentあり
no_trade_flags=[unknown] -> no_trade_flags_presentあり
```

### 7.3 Operator decision parity

既存sourceは変更しない。既存testがある場合だけmatching testを実行し、non-empty `no_trade_flags`でblockedになる現行挙動を維持する。

## 8. Required tests

### 8.1 Semantic contract tests

- constant set exact equality
- normalization of None/list/tuple/set/delimited string/JSON list
- lowercase、trim、dedup、sort
- hard/advisory/unknown partition
- empty behavior
- all advisory behavior
- hard behavior
- unknown behavior
- mixed behavior
- formal lane helper blocks every non-empty set
- offline helper stops hard/unknown only
- deterministic result serialization if serialization is provided

### 8.2 Generation tests

- valid P and M identities
- invalid program
- empty required field
- naive cutoff rejection
- absent versions become`legacy_unversioned`
- deterministic dict output
- P vs M not comparable
- generation mismatch not comparable
- schema mismatch not comparable
- legacy claim field not comparable
- method mismatch requests baseline reset
- identical compatible identity comparable
- source_head-only difference remains comparable
- unknown comparison component rejected

### 8.3 Existing matching tests

Required minimum:

```text
python -m unittest tests.test_operator_semantics_contract
python -m unittest tests.test_generation_identity_contract
python -m unittest tests.test_manual_operator_classifier
python -m unittest tests.test_phase1_trade_plans
python -m unittest tests.test_signal_reversal_safety
```

full suiteは不要。

## 9. Allowed files for implementation

```text
src/contracts/__init__.py
src/contracts/operator_semantics.py
src/contracts/generation_identity.py
src/feedback/manual_operator_classifier.py
tests/test_operator_semantics_contract.py
tests/test_generation_identity_contract.py
tests/test_manual_operator_classifier.py
chatgpt/specs/active/20260725_p_wp2_semantic_identity_and_versioning.md
docs/operations/ai-orchestration/P_GENERATION_RECONCILIATION_REPORT.md
```

既存`tests/test_phase1_trade_plans.py`と`tests/test_signal_reversal_safety.py`は読取・実行のみ。変更が必要なら停止して報告する。

## 10. Prohibited files and actions

- `main.py`
- `src/trade/execution_gate.py`
- `src/trade/opportunity_gate.py`
- `src/analysis/operator_decision.py`
- notification、mail、runtime、launchd files
- P8/P9 implementation files
- generated artifacts、CSV、XLSX、raw exchange exports
- canonical state docs beyond the one pre-existing reconciliation line
- archive/history
- frozen runtime
- threshold、gate、classifier version、schema、reason code、notification、order behavior changes
- broad cleanup
- reset、restore、checkout、clean、stash
- push

## 11. Validation and stop conditions

### 11.1 Validation

- matching tests above
- deterministic P5 output parity through existing tests
- exact changed-path check
- task-scoped `git diff --check`
- no generated artifact
- no output schema/version change

### 11.2 Stop conditions

停止して`blocked`を報告する条件:

- branchまたはstarting HEADが指定値と異なる。
- ChatGPT-authored spec/reportのstarting SHAが指定値と異なる。
- allowed fileに既存dirty collisionがある。ただし上記2つのpinned ChatGPT-authored filesを除く。
- parity維持にgate、threshold、reason code、schema、method version変更が必要。
- source integrationが`main.py`、notification、runtime、P8/P9まで必要になる。
- matching test failureの原因が既存unrelated dirty changeにある。

既存のunrelated dirty/untracked filesは調査・整理・stageしない。

## 12. Acceptance

WP2は次をすべて満たした時だけaccepted候補となる。

1. shared semantic registryがsingle ownerになる。
2. P5 local hard/advisory token definitionが除去される。
3. P5 importsの互換性が維持される。
4. unknownはfail-closed、advisory-onlyは既存C behaviorを維持する。
5. formal gateのnon-empty blockingが不変である。
6. generation identityがP/M、generation、schema、method、legacyを分離する。
7. method mismatchがbaseline resetを要求する。
8. source_head-only differenceをperformance generation mismatchと誤認しない。
9. P5 fixed fixture output parityが通る。
10. source、test、spec、1行reconciliation fix以外を変更しない。
11. runtime、notification、mail、P9、order behaviorを変更しない。
12. local commitが作成され、pushしない。

## 13. Post-WP2 boundary

WP2 acceptanceはpure contract foundationの受理だけを意味する。次を自動認可しない。

- P8 evidence payloadへのmanifest接続
- cumulative evidence bank
- modern actual attribution
- P9 readiness v2
- gate semantic変更
- production adoption

次packageはWP2の実装・test・commitをChatGPTがreviewしてから選択する。
