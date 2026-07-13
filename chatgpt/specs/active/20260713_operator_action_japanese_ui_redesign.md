# Operator Action Japanese UI Redesign

status: active
work_id: BTCFX-20260713-OPERATOR-ACTION-JAPANESE-UI-REDESIGN
created: 2026-07-13

## Objective

Public detail HTMLの次の2ブロックを、承認済みデザイン方針に沿って見やすく再設計する。

1. side-aware operator action block
2. manual operator shadow / current trading decision block

内部tokenを主要表示へ露出せず、人間が次の行動を日本語で即座に理解できる表示へ変更する。

## Current evidence

対象実装は主に次に存在する。

- `src/notification/detail_page.py::_side_aware_operator_action_html`
- `src/notification/detail_page.py::_operator_dashboard_shadow_panel_html`
- `src/notification/detail_page.py::_operator_dashboard_v2_css`
- matching tests in `tests/test_notification_detail_page.py`

現在の主要表示には次のようなraw tokenが露出している。

- `SHORT B_CHECK_15M`
- `C_WATCH_ZONE`
- `15M: late`
- `1H: wait`
- `4H: wait`

内部payload、CSV、JSON、classification tokenは変更しない。

## Exact behavior

### 1. Current action policy block

主要見出しを日本語で表示する。

例:

```text
ショート優先：15分足で戻りを確認
```

上部構成:

- badge: `現在の行動方針 / レポート専用`
- dynamic Japanese headline
- short explanatory subtitle
- timeframe status chips:
  - `15分足：追いかけ禁止`
  - `1時間足：様子見`
  - `4時間足：様子見`

Long / Shortの2カードを明確に比較できる構成にする。

- primary side cardを強調し、`今の優先`を表示
- non-primary sideは弱い視覚優先度
- headings use Japanese action wording, for example:
  - `ロング：監視のみ`
  - `ショート：15分足確認`
- primary card: `優先度：高`
- non-primary card: `優先度：低`
- next condition / zone / no-chase explanationを短い自然な日本語で表示

主要表示ではraw action/state tokenを表示しない。

### 2. Current trading decision block

Header:

```text
現在の売買判断
```

Intro:

```text
相場判断を支援するための情報です。最終判断と注文は人間が行います。
```

Safety text must remain visible:

```text
report-only / not FORMAL_GO / no automatic order / human decides manually
```

A/B/C/STOP guide uses clear Japanese labels:

| Internal token | Visible primary label | Visible explanation |
|---|---|---|
| `A_FORMAL` | `A：正式条件に近い` | `成立に最も近い状態` |
| `B_CHECK_15M` | `B：15分足を確認` | `戻り・タイミングを確認` |
| `C_WATCH_ZONE` | `C：価格帯を監視` | `価格帯の推移を観察` |
| `STOP_OR_EXIT` | `STOP：新規見送り・保護確認` | `新規は見送り、保護を優先` |

Current summary band must use a natural Japanese sentence, for example:

```text
現在の判断：ロングは監視、ショートは新規見送り・保護確認
```

Detail card labels:

- `想定動き`
- `候補状態`
- `エントリー帯`
- `無効化ライン`
- `利確目安1`
- `利確目安2`
- `内部判定`

The visible decision value must be Japanese. Do not display raw class tokens as the primary value.

### 3. Japanese mapping contract

Add or reuse deterministic display-only helpers in `detail_page.py`.

Action class mapping:

| Token | Japanese display |
|---|---|
| `A_FORMAL` | `正式条件に近い` |
| `B_CHECK_15M` | `15分足を確認` |
| `C_WATCH_ZONE` | `価格帯を監視` |
| `STOP_OR_EXIT` | `新規見送り・保護確認` |

State mapping:

| Token | Japanese display |
|---|---|
| `follow_through` | `継続確認` |
| `triggered` | `条件成立` |
| `late` | `追いかけ禁止` |
| `armed` | `条件待ち` |
| `watch` | `監視中` |
| `invalidated` | `無効化` |
| `wait` | `様子見` |

Unknown or empty values must fail closed to a neutral Japanese fallback such as `判定待ち`; do not expose the raw unknown token in the primary UI.

### 4. Visual contract

Preserve the current dark navy premium dashboard theme.

Required visual hierarchy:

- larger clear Japanese headline
- concise subtitle
- colored timeframe chips
- Long card uses green accent
- Short card uses red accent
- current primary side receives stronger border/background emphasis and `今の優先`
- clear spacing and row separation
- summary band uses gold/yellow accent
- detail table remains readable on desktop and mobile

Do not add external assets, external CSS, external JavaScript, or network dependencies.

## Input / output contract

Input remains the existing result payload.

Do not modify:

- `side_aware_mtf_action` schema
- operator classifier tokens
- scores
- structural priority values
- gates
- thresholds
- notification trigger data
- entry / SL / TP calculations

Output changes only the generated public detail HTML presentation and matching tests.

## Allowed implementation files

- `src/notification/detail_page.py`
- `tests/test_notification_detail_page.py`

A new test file is not expected. Add one only if existing matching tests cannot express the contract.

## Tests

Required targeted validation:

```bash
./.venv312/bin/python -m unittest tests.test_notification_detail_page
git diff --check
```

Add/update tests for:

- Japanese primary headline for the Short B / late example
- Japanese Long and Short card labels
- Japanese timeframe chips
- Japanese A/B/C/STOP guide labels
- Japanese summary and detail labels
- visible `追いかけ禁止` for late/no-chase
- preserved safety wording
- absence of the current raw variable-like strings from the two rendered blocks
- HTML escaping for dynamic next-condition/zone text remains intact

A single local render smoke may be run using an existing fixture. Do not send mail and do not regenerate historical artifacts.

## Success criteria

- the two approved blocks are understandable without knowing internal tokens
- primary action, waiting posture and no-chase state are visible at a glance
- Long / Short priority is visually distinct
- numeric entry, invalidation, TP1 and TP2 values remain unchanged
- existing report-only safety wording remains visible
- targeted tests pass
- no unrelated files change

## Safety boundary

- report-only
- not FORMAL_GO
- no automatic order
- human decides manually
- no scoring change
- no gate or threshold change
- no notification trigger or mail behavior change
- no runtime restart
- no launchd change
- no API, account, position or order operation
- no historical HTML/CSV regeneration

## Responsibility boundary

ChatGPT fixed the product wording, visual hierarchy and safety scope.

Codex may implement only the deterministic display/CSS/test changes defined here. Codex must not reinterpret trading meaning or change classification logic.

## Archive condition

Archive this spec only after:

- implementation diff is reviewed by ChatGPT
- targeted tests pass
- no safety or scope regression is found


---

## ChatGPT review findings — 2026-07-13

Implementation commit reported by Codex: `93c301a`.

The implementation is not yet accepted. The following display-only corrections are required before archive/runtime apply:

1. `STOP_OR_EXIT` side card semantics
   - Current source routes `STOP_OR_EXIT` to a card heading equivalent to `監視のみ`.
   - This weakens the approved meaning and conflicts with the mapping contract.
   - Required visible wording: `新規見送り・保護確認`.

2. Japanese side labels in the shadow/detail block
   - Current source uppercases the row side and visibly renders `LONG` / `SHORT`.
   - Required primary visible wording: `ロング` / `ショート`.
   - Internal values may remain unchanged in payloads and hidden diagnostic data.

3. Fail-closed unknown side handling
   - The side-label helper currently treats every non-`long` value as `ショート`.
   - Unknown, empty, or malformed values must display a neutral fallback such as `判定待ち`; they must not imply a Short direction.

4. Duplicate no-chase wording
   - For `primary_state=late` plus a no-chase chase status, the current hero status can render `追いかけ禁止 / 追いかけ禁止`.
   - Render the no-chase wording once while keeping it clearly visible.

5. Tests
   - Replace assertions that lock `STOP_OR_EXIT` to `監視のみ`.
   - Replace primary visible `LONG` / `SHORT` assertions with Japanese labels within the redesigned block.
   - Add coverage for unknown-side fail-closed behavior.
   - Add an assertion that the late/no-chase hero does not duplicate `追いかけ禁止`.

All corrections remain display-only. Do not change classifier tokens, action/state payloads, scores, gates, thresholds, notification behavior, runtime, mail, APIs, accounts, positions, or orders.


---

## ChatGPT Review Finding — unknown-side headline fail-closed correction

Codex report for commit `a6e7dea` states the first review fix completed. MCP source inspection confirms the following corrections are present:

- `STOP_OR_EXIT` card heading now preserves `新規見送り・保護確認`
- shadow/detail visible side labels use Japanese
- `_operator_side_label` returns `判定待ち` for unknown or empty side
- late/no-chase hero status avoids duplicate `追いかけ禁止`

One remaining defect blocks acceptance:

- when `primary_action_class=B_CHECK_15M` and `primary_side` is unknown or empty, headline construction uses the non-short branch and renders `判定待ち優先：15分足で押し目を確認`
- this incorrectly implies Long-side pullback semantics for an unknown side and uses `優先` despite no side being selected
- the current matching test explicitly accepts this incorrect string

Required correction:

- known `short`: `ショート優先：15分足で戻りを確認`
- known `long`: `ロング優先：15分足で押し目を確認`
- unknown/empty/malformed side: `方向判定待ち：15分足を確認`
- unknown side must not contain `優先`, `押し目`, or `戻り`
- apply the same fail-closed principle to non-B headline construction: unknown side must not produce `判定待ち優先：...`
- preserve internal payload and all trading semantics

Acceptance remains blocked until this correction and targeted tests pass. Runtime apply is not authorized.
