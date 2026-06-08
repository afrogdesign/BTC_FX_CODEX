# Active Trade Plan 実用化計画

更新日: 2026-06-07 JST  
対象ブランチ: `ver02.6-v2`  
位置づけ: ChatGPT 司令塔用の確定前計画書。Codex はこの計画を実装仕様へ落とす作業員として扱う。

---

## 0. 結論

現行の BTC Monitor は、方向認識と危険検出は改善しているが、実トレードへ使うには `trade_execution_gate` が厳しすぎる。

`trade_execution_gate` は正式・高信頼ゲートとして残す。ただし、実務ではそれだけを GO と扱わない。

次に作るべきものは、正式 gate を緩める機能ではなく、毎回の通知で「今すぐ成行」「指値待ち」「ブレイク追随」「逆方向短期」「保有中の処理」を分けて出す `active_trade_plan` である。

この計画の目的は、危ないから入るな、ではない。BTC の実際の動きに合わせて、常に利用可能な行動計画を出すことである。

---

## 1. 現状認識

### 1.1 既存計画との整合

既存の `運用資料/計画/マイルストーン定義.md` は、旧設計の「正式 Phase 1B が出るまで待つ」方針をやめ、自動取引直前までの準備を先に進めると定義している。

既存ロードマップも、`trade_execution_gate` は安全基準として維持しつつ、前進は厳格 gate 待ちだけにせず `opportunity_gate` と `paper_positions.csv` の型別成績で進める、としている。

この計画は、その方針をさらに実務化する。

### 1.2 現行 gate の問題

現行コードでは、`phase1_active` は `primary_setup_status == ready` のときだけ true になる。`watch` は `watch_reference_only` で false である。

さらに `trade_execution_gate` は以下で blocked になる。

- `phase1_active == false`
- `primary_setup_status != ready`
- `confidence_execution_shadow <= 20`
- `confidence_wait_shadow >= 60`
- no trade flags あり

この設計だと、BTC で多い `watch / retest / sweep / support reaction / resistance reaction` の局面が、ほぼ正式 GO にならない。

正式 GO がゼロに近いのは、ユーザーの運用ミスではなく、設計上かなり自然に起きる。

### 1.3 ただし正式 gate を雑に緩めてはいけない

6/7 基準の report では、正式な `trade_execution_gate=pass` と `paper_orders planned` は 0 件のまま。

一方で、方向・通知観測の成績は良い。daily-sync では完了 37 件、近似 PF 10.18、全体勝率 97.3%。Phase 1 観測候補も直近では良い。

しかし、紙ポジション診断では closed 376 件、`sl_hit=145件`、`missed_opportunity=166件`、`market_map_opportunity=117件` の品質課題が残る。

つまり、方向は読めているが、入る価格・入る形式・SL/TP・待ち方への変換が未完成である。

---

## 2. BTC の実務的な特徴として扱う前提

この計画では、BTC を次のように扱う。

1. 完璧な ready 条件を待つと、実務上の機会が少なすぎる。
2. 方向が強い局面ほど、現在値で成行すると遅いことが多い。
3. サポート直近のショート、レジスタンス直近のロングは負けやすいが、逆方向短期の候補にはなり得る。
4. `下方向バイアス` と `今ショートできる` は別である。
5. `上方向転換` は強いロング根拠としてはまだ弱いが、ショート継続やショート新規を止める材料にはなる。
6. 実務通知では、方向より先に「どう構えるか」を出す必要がある。
7. 1時間ごとの通知は、売買禁止の宣告ではなく、次の行動計画であるべき。

---

## 3. 新フェーズ定義

既存の Phase A-E は維持する。ただし、Phase D の中に実務レイヤーを追加する。

### Phase D-Active: 実務行動計画レイヤー

目的:

- 正式 GO が出なくても、毎回の通知で使える行動案を出す。
- 自動発注はしない。
- 人間が成行、指値、ブレイク、逆方向短期、保有中の撤退/利確を判断できる状態にする。
- 将来の自動化へ向け、active plan ごとの紙成績を残す。

Phase D-Active は正式 Phase 1B ではない。

`trade_execution_gate=pass` を不要にするものでもない。

正式 gate は高信頼レーンとして残し、別レーンとして `active_trade_plan` を出す。

---

## 4. 新しい出力分類

今後の通知は、最低でも以下の分類を出す。

| 分類 | 意味 | 実務扱い |
|---|---|---|
| `FORMAL_GO` | 既存 `trade_execution_gate=pass` かつ `paper_order_status=planned` | 将来の自動化候補。現時点でも最上位。 |
| `ACTIVE_MARKET_SMALL` | 現在値で小さく入れる候補 | SL 必須。サイズ小さめ。 |
| `ACTIVE_LIMIT_RETEST` | 指値で待つ候補 | BTC の主戦場。現在値で追わない。 |
| `ACTIVE_BREAKOUT_FOLLOW` | ブレイク後の追随候補 | 確定足・出来高・再テスト条件つき。 |
| `ACTIVE_COUNTER_SCALP` | 主要サポート/レジスタンス反応の逆方向短期 | 小サイズ、短命、TP 近め。 |
| `POSITION_MANAGEMENT` | すでに持っているポジションの処理 | 利確、建値撤退、損切り、保持条件。 |
| `NO_ACTION` | データ不良または価格帯も RR も悪い | 完全見送り。 |

重要: `NO_ACTION` は最後の手段にする。多くの通知では、少なくとも `ACTIVE_LIMIT_RETEST` または `POSITION_MANAGEMENT` を出す。

---

## 5. active_trade_plan の仕様

### 5.1 payload 形式

`core_result` に以下を追加する。

```python
active_trade_plan = {
    "plan_version": "active_trade_plan_v1",
    "primary_action": "ACTIVE_LIMIT_RETEST",
    "headline": "戻り売り待ち。成行ショート不可。現値は反発帯。",
    "market_entry_now": {...},
    "limit_retest_entry": {...},
    "breakout_follow_entry": {...},
    "countertrend_scalp_entry": {...},
    "position_management": {...},
    "side_plans": {
        "long": {...},
        "short": {...},
    },
    "warnings": [...],
}
```

### 5.2 side_plan 形式

```python
{
    "side": "short",
    "bias_alignment": "primary" | "counter" | "neutral",
    "entry_zone_low": 60680.82,
    "entry_zone_high": 60882.88,
    "entry_mid": 60781.85,
    "current_price": 60513.0,
    "zone_position": "below_zone" | "inside_zone" | "above_zone",
    "market_entry_status": "allowed" | "blocked" | "conditional",
    "limit_entry_status": "allowed" | "blocked" | "conditional",
    "breakout_status": "watch" | "armed" | "blocked",
    "counter_scalp_status": "allowed" | "blocked" | "conditional",
    "stop_loss": 61179.73,
    "tp1": 60264.61,
    "tp2": 59826.94,
    "rr_current_tp1": 0.37,
    "rr_current_tp2": 1.03,
    "rr_zone_mid_tp1": 1.02,
    "rr_zone_mid_tp2": 2.10,
    "blockers": [...],
    "triggers": [...],
    "next_condition": "60,681-60,883 へ戻るまで待つ",
}
```

---

## 6. 判定ルール v1

### 6.1 現在値の zone 位置

side ごとに、現在値と entry zone の位置を出す。

long:

- `below_zone`: 現在値が long entry zone より下
- `inside_zone`: 現在値が long entry zone 内
- `above_zone`: 現在値が long entry zone より上

short:

- `below_zone`: 現在値が short entry zone より下。追いかけショートになりやすい。
- `inside_zone`: 現在値が short entry zone 内
- `above_zone`: 現在値が short entry zone より上

### 6.2 成行エントリー

`market_entry_now` は厳しくする。

許可条件:

- data quality が ok
- fatal no_trade flag なし
- 現在値が対象 side の entry zone 内、または breakout follow 条件が armed
- `rr_current_tp1 >= 0.8` または `rr_current_tp2 >= 1.5`
- SL が有効
- 実行しやすさが最低基準以上
  - primary side: `execution >= 20`
  - counter scalp: `execution >= 15` かつ support/resistance reaction がある
- side 固有の追いかけ禁止に該当しない

blocked 理由例:

- `current_price_below_short_zone_chase_risk`
- `current_price_above_long_zone_chase_risk`
- `current_rr_too_low`
- `short_into_major_support_market_block`
- `long_into_major_resistance_market_block`
- `execution_too_low_for_market`

### 6.3 指値・戻り待ち

`limit_retest_entry` は、BTC 実務の主レーンにする。

許可条件:

- 対象 side の entry zone が存在
- SL/TP が存在
- zone mid 基準の RR が成立
- fatal no_trade なし

現在値が zone 外でも、これは出してよい。

例:

- 大局 short、現在値が short zone より下なら、成行 short は blocked、戻り売り指値は allowed。
- 大局 long、現在値が long zone より上なら、成行 long は blocked、押し目指値は allowed。

### 6.4 ブレイク追随

`breakout_follow_entry` は、現行の `breakout_up` / `breakout_down` と `execution_precision_action=allow_breakout_follow` を使う。

許可条件:

- 15分足または1時間足で明確な breakout
- 出来高比 `volume_ratio >= TRIGGER_VOLUME_RATIO`
- 直近サポレジの役割転換が確認または再テスト待ち
- 成行ではなく、確定足後の再評価を原則にする

### 6.5 逆方向短期スキャル

`countertrend_scalp_entry` は、正式トレンド転換ではない。小サイズの短期反発/反落候補である。

long counter scalp 条件例:

- bias は short または downtrend
- 現在値が long entry zone 内、または主要サポート直近
- `major_support_rejection` または `failed_breakout_up_reversal` または `short_into_major_support`
- short の成行が blocked
- TP1 が近く、SL が明確

short counter scalp 条件例:

- bias は long または uptrend
- 現在値が short entry zone 内、または主要レジスタンス直近
- `major_resistance_rejection` または `failed_breakout_down_reversal` または `long_into_major_resistance`
- long の成行が blocked
- TP1 が近く、SL が明確

注意:

- `trend_flip_confirmed_up` は強い long 根拠へ戻さない。
- ただし short 継続や short 成行を止める注意材料として使う。
- counter scalp は通常サイズの 1/4 から開始する想定で表示する。

### 6.6 保有中ポジション管理

システムは現時点でユーザーの実ポジションを知らない。したがって v1 では「もし保有中なら」を必ず出す。

例:

- short 保有中で、主要サポート反発 / long counter scalp 条件あり:
  - 利確検討
  - 建値撤退検討
  - 直近高値上抜けで撤退
- long 保有中で、主要レジスタンス拒否 / short counter scalp 条件あり:
  - 利確検討
  - 建値撤退検討
  - 直近安値割れで撤退

v2 では `logs/manual_positions.csv` を追加し、ユーザーの手入力ポジションを active plan に反映する。

---

## 7. 20260606_230500 の期待出力

実レポート:

- signal_id: `20260606_230500`
- 現在値: `60,513`
- final rank: `通常監視・実行不可`
- direction: `下方向バイアス`
- execution: `18.0`
- wait: `59.2`
- long zone: `60,322.42 - 60,524.08`
- long SL: `60,025.57`
- long TP1: `60,940.23`
- long TP2: `61,377.68`
- short zone: `60,680.82 - 60,882.88`
- short SL: `61,179.73`
- short TP1: `60,264.61`
- short TP2: `59,826.94`
- short 執行チェック: 主要サポートが近く、追いかけず待機

期待される active plan:

```text
primary_action: ACTIVE_LIMIT_RETEST + ACTIVE_COUNTER_SCALP
headline: 下方向優勢。ただし成行ショート不可。戻り売り待ち。現値は短期反発帯。

market_entry_now:
  short: blocked
  reason:
    - current_price_below_short_zone_chase_risk
    - short_into_major_support_market_block
    - execution_too_low_for_market
  long: conditional_counter_scalp
  reason:
    - current_price_inside_long_zone
    - short_chase_blocked_near_support
    - use_small_size_only

limit_retest_entry:
  short: allowed
  zone: 60,680.82 - 60,882.88
  stop: 61,179.73
  tp1: 60,264.61
  tp2: 59,826.94
  condition: この帯まで戻り、15分足で再失速するなら候補

countertrend_scalp_entry:
  long: conditional
  zone: 60,322.42 - 60,524.08
  stop: 60,025.57
  tp1: 60,940.23
  tp2: 61,377.68
  condition: 60,322 を維持し、15分足で反発継続なら小サイズのみ

position_management:
  if_short_holding: 反発帯なので利確/建値撤退を優先。60,883 上抜けで下落警戒を弱める。
  if_long_holding: 60,940 付近で部分利確、60,322 割れで撤退検討。
```

この出力なら、ユーザーは「下方向だから今ショート」ではなく、「下方向だが今は戻り売り待ち、同時に短期反発も取れる」と理解できる。

---

## 8. 通知 UI / 件名の改善

### 8.1 件名ルール

現状の件名:

```text
[通常監視・実行不可] 下方向バイアス | サポート割れ後の戻り売り確認
```

これは方向が強く見えすぎる。

改善後:

```text
[戻り売り待ち・成行ショート不可] 下方向優勢 / 指値 60,681-60,883 / 現値は反発帯
```

または:

```text
[現値ショート不可・短期反発注意] 下目線 / short待ち 60,681-60,883 / long反発 60,322-60,524
```

### 8.2 hero 表示

最上段は以下の順にする。

1. 今すぐ成行できるか
2. どこで指値待ちか
3. 逆方向短期があるか
4. 保有中ならどう処理するか
5. 大局方向

方向スコアは最上段に出さない。方向スコアは「大局」セクションへ下げる。

---

## 9. コード修正案

### 9.1 追加ファイル

`src/trade/active_plan.py`

責務:

- current price と long/short setup から side plan を作る
- zone position を判定する
- current RR / zone mid RR を計算する
- market / limit / breakout / counter / position management を分類する
- final primary_action と headline を作る

関数案:

```python
def build_active_trade_plan(
    *,
    current_price: float,
    bias: str,
    market_regime: str,
    long_setup: dict[str, Any],
    short_setup: dict[str, Any],
    confidence_direction_shadow: Any,
    confidence_execution_shadow: Any,
    confidence_wait_shadow: Any,
    risk_flags: list[str],
    market_map_flags: list[str],
    no_trade_flags: list[str],
    data_quality_flag: str,
    breakout_up: bool,
    breakout_down: bool,
    volume_ratio: float,
    trigger_volume_ratio_threshold: float,
) -> dict[str, Any]:
    ...
```

補助関数案:

```python
def classify_zone_position(side: str, price: float, entry_low: float, entry_high: float) -> str:
    ...

def rr_for_current(side: str, current_price: float, stop: float, target: float) -> float | None:
    ...

def rr_for_entry(side: str, entry_price: float, stop: float, target: float) -> float | None:
    ...

def build_side_plan(...):
    ...
```

### 9.2 `main.py`

追加 import:

```python
from src.trade.active_plan import build_active_trade_plan
```

追加位置:

- `long_setup` / `short_setup`
- `confidence_details`
- `result_flags`
- `market_map`
- `execution_gate` / `opportunity_gate`

がそろった後、`build_notification_context()` より前に呼ぶ。

実装位置候補:

```python
core_result.update(opportunity_gate)
core_result["active_trade_plan"] = build_active_trade_plan(...)
core_result["active_primary_action"] = core_result["active_trade_plan"].get("primary_action", "NO_ACTION")
core_result["active_headline"] = core_result["active_trade_plan"].get("headline", "")
```

注意:

- `trade_execution_gate` は変更しない。
- `paper_order_status` は正式 gate のみで維持。
- `active_trade_plan` は通知・紙検証用の新レイヤー。

### 9.3 `src/presentation/sanitize.py`

`build_notification_context()` に active plan を追加する。

追加フィールド案:

```python
"active_primary_action": active_plan.get("primary_action", "NO_ACTION"),
"active_headline": active_plan.get("headline", ""),
"active_market_entry_label": ...,
"active_limit_entry_label": ...,
"active_counter_label": ...,
"active_position_management_label": ...,
```

`_final_rank()` は正式 gate の表示を壊さない。ただし件名・hero 用に active headline を優先できるようにする。

### 9.4 `src/ai/summary.py`

`build_summary_subject()` を修正。

優先順位:

1. `FORMAL_GO`
2. `ACTIVE_MARKET_SMALL`
3. `ACTIVE_LIMIT_RETEST`
4. `ACTIVE_COUNTER_SCALP`
5. `POSITION_MANAGEMENT`
6. 既存 final_rank

件名例:

```text
[戻り売り待ち・成行ショート不可] 下方向優勢 / 指値 60,681-60,883 / 現値は反発帯
```

### 9.5 `src/notification/detail_page.py`

hero を active plan 優先へ変更。

追加セクション:

- `今すぐ成行`
- `指値/戻り待ち`
- `ブレイク追随`
- `逆方向短期`
- `保有中なら`

方向スコアと long/short score は、hero ではなく下段へ移す。

### 9.6 `src/storage/csv_logger.py`

shadow_log / trade_log に最低限の列を追加する。

```text
active_primary_action
active_headline
active_market_side
active_limit_side
active_counter_side
active_market_entry_status_long
active_market_entry_status_short
active_limit_entry_status_long
active_limit_entry_status_short
active_rr_current_long_tp1
active_rr_current_short_tp1
active_zone_position_long
active_zone_position_short
```

既存 CSV 互換を壊さないため、append 時に missing column は空で処理する。

### 9.7 `tools/log_feedback.py`

新 report builder を追加。

```bash
./.venv312/bin/python tools/log_feedback.py build-active-trade-plan-diagnostics \
  --date-from 2026-04-18 \
  --date-to 2026-06-07 \
  --output-md 運用資料/reports/analysis/active_trade_plan_diagnostics_20260607.md
```

集計項目:

- primary_action 別件数
- market entry allowed / blocked の件数
- limit retest allowed の件数
- counter scalp conditional の件数
- それぞれの MFE/MAE、TP1先行率、sl_hit、missed_opportunity
- `NO_ACTION` が多すぎないか
- 成行 allowed が多すぎないか

### 9.8 テスト

追加:

`tests/test_active_trade_plan.py`

最低限のテスト:

1. `20260606_230500` 型で、成行 short は blocked、limit short は allowed、counter long は conditional。
2. 現在値が short zone 内で RR が成立する場合、short market が allowed。
3. 現在値が long zone より上で RR が悪い場合、long market は blocked、long limit は allowed。
4. fatal no_trade flag ありなら market / limit / counter は blocked。
5. data_quality != ok なら `NO_ACTION`。
6. `trend_flip_confirmed_up` 単独では formal long にしないが、short market の警戒材料にはする。

---

## 10. ロールアウト順

### Step 1: 表示だけ追加

- `active_trade_plan` を payload に追加
- 通知 HTML / 件名に表示
- paper order や gate は変更しない

### Step 2: active plan diagnostics

- 過去ログに後付けで active plan を評価
- 成行 allowed が過剰でないか確認
- limit / counter の missed / sl_hit を見る

### Step 3: active paper positions

`paper_positions.csv` とは別に、または `opportunity_type` を分けて active plan を追跡する。

候補:

- `active_market_small`
- `active_limit_retest`
- `active_counter_scalp`
- `active_breakout_follow`

### Step 4: 実務通知へ昇格

以下を満たしたら、通知上で `ACTIVE_*` を強く出す。

- active plan の `NO_ACTION` が少なく、1日あたり十分な候補が出る
- 成行 allowed の sl_hit 偏重が許容範囲
- limit retest が missed だけでなく actual entry へ移行できる
- counter scalp が小 TP で機能している

### Step 5: 自動化直前

実弾 API はまだ接続しない。

ただし、以下は整える。

- kill switch
- blackout window
- daily loss limit
- max consecutive loss
- active plan type 別 size multiplier
- manual position tracking
- notification acknowledge

---

## 11. 実務運用ルール

ユーザーが通知を使うときのルール:

1. `FORMAL_GO`: 最上位。ただし現時点ではまだ稀。
2. `ACTIVE_MARKET_SMALL`: 小サイズのみ。SL 同時設定必須。
3. `ACTIVE_LIMIT_RETEST`: 主戦場。通知された帯まで待つ。
4. `ACTIVE_COUNTER_SCALP`: 小サイズ・短時間。欲張らない。
5. `POSITION_MANAGEMENT`: すでに持っている時は新規より優先。
6. `NO_ACTION`: データ不良または価格が悪い。ここだけ完全見送り。

---

## 12. Codex への実装指示案

```text
対象ブランチ: ver02.6-v2

目的:
正式 trade_execution_gate は維持しつつ、実務で使える active_trade_plan を追加する。
BTC の実際の動きに合わせ、毎回の通知で「成行 / 指値 / ブレイク / 逆方向短期 / 保有中処理」を出す。

変更範囲:
- src/trade/active_plan.py を追加
- main.py に active_trade_plan の生成を追加
- src/presentation/sanitize.py に active plan 表示用 context を追加
- src/ai/summary.py の件名を active plan 優先に変更
- src/notification/detail_page.py の hero を active plan 優先に変更
- src/storage/csv_logger.py に active plan 列を追加
- tools/log_feedback.py に active_trade_plan_diagnostics builder を追加
- tests/test_active_trade_plan.py を追加

禁止:
- trade_execution_gate の pass 条件を緩めない
- paper_order_status=planned の条件を変えない
- 実弾発注 API を追加しない
- 取引所 API キーや秘密鍵を扱わない
- ACTIVE_* を FORMAL_GO と表示しない

fixture:
20260606_230500 相当のデータで、以下を確認する。
- 成行 short: blocked
- limit short: allowed
- counter long: conditional
- headline は「下方向優勢。ただし成行ショート不可。戻り売り待ち。現値は短期反発帯。」相当
```

---

## 13. 自己精査

この計画は、単に gate を緩める案ではない。

現行 repo の重要判断である「正式 trade_execution_gate は安全基準として維持する」と矛盾しない。

同時に、ユーザーの実務要求である「ほぼ取引機会がない」「BTC では常に構えが必要」「3か月 GO ゼロはおかしい」に対応する。

弱点は、active plan の成績がまだ未計測であること。そのため Step 1 では表示と記録だけ追加し、Step 2 で diagnostics を必ず出す。

この計画で目指す状態は、毎回の通知が以下の形になることである。

```text
大局方向: short
成行: 不可
指値: short 60,681-60,883
逆方向短期: long 60,322-60,524 条件付き
保有中: short は利確/建値撤退警戒
正式GO: なし
```

この形になれば、正式 GO が出なくても、実務として使える通知になる。
