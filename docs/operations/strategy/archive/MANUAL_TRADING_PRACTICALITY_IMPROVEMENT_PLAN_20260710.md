# Manual Trading Practicality Improvement Plan

## Metadata

- repo: `afrogdesign/BTC_FX_CODEX`
- primary working repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- created_at: `2026-07-10`
- status: approved product-improvement planning route
- active source branch: read from `git status --short --branch` and `docs/operations/ai-orchestration/CURRENT_STATE.md`
- scope: manual trading practicality / operator actionability / scenario lifecycle / ground-truth evaluation
- related documents:
  - `docs/operations/ai-orchestration/PRODUCT_IMPLEMENTATION_ROUTE.md`
  - `docs/operations/ai-orchestration/MANUAL_TRADING_PRACTICALITY_EXECUTION_ROUTE_20260710.md`
  - `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
  - `docs/operations/strategy/VER04_V1_MANUAL_15M_WIN_DEFINITION_20260702.md`
  - `docs/operations/ai-orchestration/PHASE4_SELF_IMPROVEMENT_CONTROL_PLAN_20260707.md`
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

---

## 1. Executive decision

現在のシステムは、分析・候補生成・安全装置の完成度は高い。

主な問題は、相場機会を検出できていないことではない。内部では多数の `Active Plan` 候補を生成できている一方、それらを人間が実践で使える判断へ変換する段階で、厳格な条件が直列に重なり、最終的な本採用候補が極端に少なくなっている。

したがって、改善の中心は単純なgate緩和ではない。

```text
既存の厳格なformal execution判定は維持する。
その下に、15分足で人間が確認する候補、監視候補、停止・利確候補を追加する。
```

目標構造は次である。

```text
A_FORMAL
  現在の厳格な最高品質候補。

B_CHECK_15M
  15分足のtriggerを人間が確認して判断する主力候補。

C_WATCH_ZONE
  方向と価格帯は有望だが、まだentry条件が未成立の監視候補。

STOP_OR_EXIT
  新規entryを止め、利確・撤退・建値保護を優先する局面。
```

この分類は既存の `trade_execution_gate`、`phase1b_lite_gate`、`opportunity_gate` を置き換えない。既存gateは内部の安全・品質判定として維持し、その上に人間向けのoperator action layerを追加する。

また、候補行数をそのまま通知数へ変換してはいけない。同一相場シナリオの時間更新、long/short両side、複数entry typeを1つのscenario lifecycleへ統合し、人間が処理できる判断イベント数へ圧縮する。

---

## 2. この計画が解決する問題

### 2.1 本採用候補が少なすぎる

直近の約2週間では、main通知のうち厳格な `ENTRY_OK` は6件だった。一方で、内部のActive Planはより多くの候補を生成している。

これは、相場機会が6回しかなかったことを意味しない。

以下の段階で候補が圧縮される。

```text
market data
→ setup生成
→ position risk / prelabel
→ confidence / quality guard
→ execution gate
→ opportunity gate
→ signal tier
→ notification trigger
→ operator表示
```

各段階の判定は個別には合理的である。しかし、複数のAND条件が直列に連なることで、次のような人間向け候補まで消えやすい。

- setupは`watch`だが、価格帯が良い
- executionは中程度だが、方向とRRは良い
- wait pressureは高いが、戻り・押しの完了を待てば使える
- 軽微なwarningがあるが、15分足で回避可能
- entry zoneへ接近中だが、まだ正式readyではない
- trend継続候補だが、通知条件となる状態変化が小さい

### 2.2 「本採用か見送りか」の二択になっている

現行出力では、内部に多様な候補があっても、最終的には次のように見えやすい。

- ENTRY_OK
- 売買非推奨
- 監視
- 待ち
- 紙候補

人間が必要としているのは、許可・禁止の二択ではなく、具体的な次行動である。

```text
いま入れるのか
何を待つのか
どの価格帯を見るのか
何が起きたら昇格するのか
どこでシナリオが無効になるのか
保有中なら利確すべきか
```

### 2.3 同じシナリオが候補行として重複する

Active Plan candidateは、時間更新ごと、sideごと、entry typeごとに行が増える。

そのため、候補行が374件あっても、374回の独立した売買機会を意味しない。

重複を除かず通知を増やすと、次の問題が起きる。

- 同じ価格帯の通知が繰り返される
- 相場の重要度より更新頻度が通知数を支配する
- 人間が新規機会と状態更新を区別できない
- 事後評価で母数が膨らむ
- 勝率・機会損失率の解釈が歪む

### 2.4 実取引ground truthが未接続

現在のproxy評価は有用だが、以下を直接表していない。

- 実際に人間がentryしたか
- 約定価格
- 手数料
- slippage
- 部分利確
- 裁量撤退
- 同時保有制約
- 通知を見たが見送ったケース
- 人間が15分足を確認した時刻

このため、production thresholdを変更する前にactual trade importとsignal/scenario linkingが必要である。

---

## 3. Review scope and evidence

## 3.1 Daily Proxy 2026-07-02

参照:

```text
運用資料/reports/post_eval/daily_proxy_evaluator_20260702.md
```

7日間のsignal outcome:

| prelabel | 件数 |
|---|---:|
| `ENTRY_OK` | 4 |
| `RISKY_ENTRY` | 7 |
| `SWEEP_WAIT` | 6 |
| `NO_TRADE_CANDIDATE` | 15 |
| 合計 | 32 |

同期間のActive Plan candidateは374行。

| candidate type | 件数 |
|---|---:|
| `active_limit_retest` | 270 |
| `active_counter_scalp` | 101 |
| `active_market_small` | 3 |

この差から、候補生成能力自体は存在することが分かる。

ただし、374行には次が含まれる。

- 同一scenarioの時間更新
- long/short両side
- 同時に生成された複数entry type
- entry zone未到達
- OHLCV未解決
- operatorが実際には見ていない候補

したがって、候補行数を独立した取引機会数として扱わない。

## 3.2 約2週間のmain通知proxy

対象期間:

```text
2026-06-26 から 2026-07-10 JST
```

通知HTMLは約102ファイル存在したが、attentionとfollowupは新規entry推奨ではないため、新規候補の母数から除外した。

main通知28件のprelabel:

| prelabel | 件数 |
|---|---:|
| `ENTRY_OK` | 6 |
| `RISKY_ENTRY` | 7 |
| `SWEEP_WAIT` | 8 |
| `NO_TRADE_CANDIDATE` | 7 |

TP1先行を暫定winとしたproxy:

| 対象 | win / total | 暫定率 |
|---|---:|---:|
| `ENTRY_OK`のみ | 5 / 6 | 83.3% |
| `ENTRY_OK` + `RISKY_ENTRY` | 9 / 13 | 69.2% |
| 上記 + `SWEEP_WAIT` | 15 / 21 | 71.4% |
| 全main通知・resolvedのみ | 17 / 27 | 63.0% |

読み方:

- `ENTRY_OK` は少数だが高品質である可能性がある。
- 一部の `RISKY_ENTRY` と `SWEEP_WAIT` にも、人間の15分足確認を条件とすれば使える候補が含まれる。
- 厳格判定を壊すより、下位のmanual review layerを追加する方が安全である。

限界:

- 実際のentryではない。
- 実約定・手数料・slippageを含まない。
- 人間の15分足フィルターを再現していない。
- 小標本であり、production threshold変更の根拠には不足する。
- 通知が来た時点で同時保有中だった可能性を考慮していない。

## 3.3 Judgment self-review

参照:

```text
local/self_review_current_check/self_review_current.json
docs/operations/ai-orchestration/PHASE4_SELF_IMPROVEMENT_CONTROL_PLAN_20260707.md
```

| 項目 | 件数 |
|---|---:|
| candidate review rows | 1700 |
| good | 35 |
| wrong | 39 |
| false alarm | 12 |
| no data | 1612 |
| unresolved | 2 |
| TP1 first | 35 |
| SL first | 39 |

Phase4資料では次も確認されている。

```text
resolved_intraperiod = 88
no_ohlcv = 1742
```

最大の問題は、勝率が悪いことではなく、解決済みデータが少なすぎることである。

`no_ohlcv` と unresolved を勝ち・負けのどちらにも混ぜない。

## 3.4 Long / short非対称性

現行evidenceでは、sideごとに傾向が異なる。

- short `active_limit_retest` はTP1先行が比較的強い。
- long `active_limit_retest` はSL先行に偏る。
- long側では、浅いentry、方向確認不足、value defense zone未確認が問題になりやすい。
- `trend_flip_confirmed_up` 単独を強評価へ戻す根拠はない。

したがって、同じ閾値緩和をlong/shortへ一律適用してはいけない。

---

## 4. Current architecture review

## 4.1 End-to-end structure

```text
Market data / OHLCV / orderbook / liquidation / OI / CVD
  ↓
Setup generation / market map / regime analysis
  ↓
Position risk and prelabel
  ↓
Confidence shadows / quality guards
  ↓
Execution gate / opportunity gate / signal tier
  ↓
Active Plan
  ↓
Notification trigger
  ↓
Mail / HTML / dashboard
  ↓
Signal outcome / intraperiod outcome / self-review
```

## 4.2 `src/analysis/position_risk.py`

現在の役割:

- liquidity距離
- liquidation cluster
- orderbook wall
- sweep完了/未完了
- OI/CVD divergence
- location risk
- prelabel分類

長所:

- 危険な位置を明示的に分離できる。
- `ENTRY_OK`、`RISKY_ENTRY`、`SWEEP_WAIT`、`NO_TRADE_CANDIDATE` の段階がある。
- risk breakdownが残るため、説明可能性が高い。

問題:

- prelabelが後段で実質的な許可/禁止として強く使われる。
- `SWEEP_WAIT` や `RISKY_ENTRY` の中に、人間なら条件付きで扱える候補が混ざる。

改善:

- prelabelは内部risk分類として維持する。
- operator action layerで「どの条件を確認すれば使えるか」へ変換する。

## 4.3 `src/analysis/signal_tier.py`

strong判定は次のAND条件で構成される。

- `prelabel == ENTRY_OK`
- `primary_status == ready`
- confidenceがside別基準より10以上高い
- RR 1.8以上
- no-trade flagなし
- major warningなし
- minor warningは1件以下
- machine agreementが`agree`

長所:

- 最高品質候補の純度を高く維持できる。
- Aランクの基準として有効。

問題:

- 人間確認用候補の入口としては狭すぎる。
- 一つの軽微な不一致で通常扱いへ落ちる。

改善:

- strong tierはAとして保持する。
- B/Cは別のoperator classifierで扱う。

## 4.4 `src/trade/execution_gate.py`

現在の条件:

- phase1 active
- setup ready
- `rr_below_min`ではない
- data quality正常
- no-trade flagなし
- execution shadow > 20
- wait shadow < 60

長所:

- formal candidateに必要な最低条件を明確にできる。
- 将来の自動化に近い安全境界として有効。

問題:

- manual review candidateとformal candidateが混同されると、使える候補が消える。

改善:

- `trade_execution_gate`は緩和しない。
- gate不通過でもfatalでない候補をB/Cへ回す並行ルートを作る。

## 4.5 `src/trade/opportunity_gate.py`

現在の役割:

- formal execution candidate
- phase1b-lite
- phase1 observation
- market-map opportunity
- high-wait / low-execution / long weakness / trend flip upのquality guard

長所:

- 多様な機会を一つの判定へ統合している。
- fatal flagとsoft riskを分けている。
- longの弱さやtrend flip upの過信を抑制している。

問題:

- gateの出力が最終的な行動表示へ直接近いため、条件付き候補の意味が失われる。

改善:

- opportunity typeをscenario evidenceとして保持する。
- operator actionは別layerで決定する。

## 4.6 `src/trade/active_plan.py`

生成できるもの:

- `ACTIVE_MARKET_SMALL`
- `ACTIVE_LIMIT_RETEST`
- `ACTIVE_BREAKOUT_FOLLOW`
- `ACTIVE_COUNTER_SCALP`
- position management
- long/short両side plan

長所:

- 実践に必要な候補生成能力は既に高い。
- entry zone、SL、TP、RR、zone position、next conditionを持つ。

問題:

- candidateの数が多く、scenario identityがない。
- `ACTIVE_*` が実行許可と誤解されやすい。
- operatorが次に見る15分足条件が統一されていない。

改善:

- `ACTIVE_*` は内部plan typeとして保持する。
- scenarioへ統合し、A/B/C/STOPへ翻訳する。

## 4.7 `src/notification/trigger.py`

現在の主な通知契機:

- status upgrade
- bias change
- prelabel improvement
- confidence jump
- agreement change
- signal tier upgrade

長所:

- 同じ状態の繰り返し通知を抑えられる。
- attentionとfollowupを分離している。

問題:

- 実践上重要な価格・scenarioイベントが中心ではない。

必要な将来イベント:

- approaching zone
- zone touched
- trigger wait
- trigger confirmed
- invalidated
- TP1 reached
- runner decision
- expired

---

## 5. Target operator workflow

目標利用フロー:

```text
通知を受け取る
→ scenarioの方向・種類を理解する
→ entry zoneとinvalidationを確認する
→ 15分足triggerを確認する
→ entry / watch / skip / exit / take-profitを判断する
→ 同じscenarioへ結果を紐づける
→ daily / weekly / biweekly評価へ反映する
```

通知には最低限、次を含める。

- action class
- side
- scenario type
- current lifecycle state
- entry/watch zone
- 15分足で確認する条件
- invalidation
- TP1 / TP2または保有管理
- risk warning
- 「entry指示ではない」という安全境界

---

## 6. A / B / C / STOP operator action layer

## 6.1 A_FORMAL

意味:

- 現在の厳格なformal execution candidate相当。
- 最高品質候補。
- それでも15分足確認は必要。
- 自動注文許可ではない。

原則:

- `trade_execution_gate=pass` の価値を維持する。
- `ENTRY_OK` やstrong tierを安易に増やさない。
- Aの勝率・PF・平均Rを独立評価する。

## 6.2 B_CHECK_15M

意味:

- システム上はformal未満だが、人間が15分足を確認すれば実践候補になり得る。
- manual trading supportの主力拡張層。

初期offline hypothesis:

- data quality正常
- long/shortの方向あり
- fatal no-trade flagなし
- setupは`ready`または`watch`
- direction shadow 55以上
- execution shadow 18以上
- wait shadow 75以下
- entry zone内、または定義された近接範囲
- TP1 RR 0.8以上、またはTP2 RR 1.5以上
- 15分足trigger確認必須
- warningは明示する

重要:

```text
上記はoffline replay用の比較条件であり、production thresholdではない。
```

Bは次のような候補を救う。

- 良い戻り売りだがexecutionが少し不足
- setup watchだがzone touched
- sweep未完了だが15分足再失速で使える
- 軽微warning付きの継続候補

## 6.3 C_WATCH_ZONE

意味:

- 方向と価格帯は有望。
- まだentry条件は成立していない。
- scenarioを捨てず、次の昇格条件を明示する。

表示内容:

- 監視zone
- 現在価格との距離
- Bへ昇格する条件
- invalidation
- expected wait reason

CはdashboardまたはHTML中心とし、すべてをメール送信しない。

## 6.4 STOP_OR_EXIT

意味:

- 新規entry停止
- 保有中の利確・撤退・建値保護を優先
- scenario invalidation
- turning riskへの対応

STOP条件候補:

- data quality不良
- fatal no-trade flag
- scenario invalidation
- turning risk HIGH / EXTREME
- major support/resistanceで逆行risk増大
- long/short thesisが崩れた

STOPを単なる「何もしない」にしない。

---

## 7. Scenario identity and lifecycle

## 7.1 Scenario identity

`signal_id` と `scenario_id` を分ける。

scenario identity候補:

- side
- setup type
- entry zone bucket
- source signal lineage
- market regime
- initial detection time
- invalidation level
- primary thesis

例:

```text
scenario_id = short_limit_retest_61900_62100_20260710_01
```

## 7.2 Lifecycle

```text
detected
→ approaching_zone
→ zone_touched
→ trigger_wait
→ confirmed
→ entered / skipped / watched
→ tp1 / tp2 / manual_exit / invalidated / expired
```

## 7.3 Deduplication rules

- 同じside、setup、zone、thesisの小幅更新は同一scenario。
- 価格帯の微修正だけで新scenarioにしない。
- side反転、主要thesis変更、invalidation後の再構築は新scenario候補。
- 同じscenarioの状態更新は新規機会数へ加算しない。
- notificationはstate transition単位で制御する。

## 7.4 Notification policy

メール候補:

- CからBへ昇格
- BからAへ昇格
- zone touched
- trigger confirmed
- invalidated
- TP1 / exit優先

dashboard/HTMLのみ候補:

- approaching zoneの小幅更新
- RRの微修正
- confidenceの小幅変化
- 同一scenario内の非重要更新

---

## 8. Side-aware and regime-aware design

## 8.1 Short

最初のB拡張対象として優先的にoffline検証する。

対象候補:

- short active limit retest
- support to resistance flip
- failed breakout down reversal
- trend flip confirmed down
- major resistance rejection

shortでは、方向と位置が良ければ、executionがformal基準より少し低くてもB候補になり得る。

ただしmajor support直前やshort cover riskではSTOPまたはCへ落とす。

## 8.2 Long

shortと同条件で広げない。

追加確認:

- shallow pullbackだけで入らない
- value defense zone
- support reclaim
- resistance to support flip
- retest confirmed
- major resistanceへの距離
- trend transition
- short invalidation by reclaim

`trend_flip_confirmed_up` 単独で強評価へ戻さない。

## 8.3 Transition regime

- long/short両sideを表示する。
- aggression rankは上限を設ける。
- counter-bias opportunityをscoutとして残す。
- turning riskを強く表示する。
- entryよりexit/take-profit価値が高い場合を認識する。

---

## 9. Notification and UI direction

B例:

```text
SHORT B｜戻り売り候補
監視帯: 61,900–62,100
現在: zone_touched / trigger_wait
15分足条件: 上ヒゲ形成後の安値更新
無効化: 62,280超え
TP1: 61,500
注意: formal execution candidateではない
```

C例:

```text
LONG C｜押し目候補準備
監視帯: 60,800–61,000
現在: approaching_zone
15分足反発確認まではentryしない
無効化: 60,620割れ
```

STOP例:

```text
STOP｜転換警戒
新規short停止
保有shortは利確または建値撤退を優先
理由: reclaim + short cover risk
```

原則:

- labelはpermissionではなくoperator actionを示す。
- `ACTIVE_*` とA/B/C/STOPを混同しない。
- Big Chanceはentry指示にしない。
- mail / HTML / dashboardはsingle-source。
- 同一scenarioの全更新をメール送信しない。

---

## 10. Evidence and ground-truth foundation

実装順序:

1. actual trade importer
2. actual tradeとsignalのlinking
3. signalからscenarioへのlinking
4. OHLCV / intraperiod coverage診断
5. scenario normalization
6. offline A/B/C/STOP classifier
7. historical replay
8. shadow表示
9. manual trial
10. evidence-backed tuning review

評価項目:

- actual net PnL
- fee
- win rate
- PF
- average R
- MFE / MAE
- TP1 first / SL first
- avoided loss
- missed opportunity
- over-suppression
- turning-point miss
- duplicate notification rate
- mail usefulness
- A/B別成績
- long/short別成績
- regime別成績
- setup type別成績

---

## 11. Phased implementation plan

## Phase P0: Plan and routing

この文書とAI導線を作成する。

成果物:

- detailed improvement plan
- execution route
- startup routing
- next active-spec task

## Phase P1: Manual actual trade import active spec

作業ID:

```text
BTCFX-20260710-MTP-ACTUAL-TRADE-IMPORT-SPEC
```

目的:

- 既存の `BTCFX-20260702-MEXC-ACTUAL-TRADE-IMPORTER` を新計画へ接続する。
- 実装前にschema、安全境界、test、重複取込方針を確定する。

このphaseではsource実装しない。

## Phase P2: Actual trade importer implementation

- local xlsx only
- raw export非commit
- no exchange API
- timezone normalization
- realized PnL / fee / side / open-close time
- duplicate import handling
- privacy-safe validation

## Phase P3: Actual trade to signal/scenario linking

- time proximity
- side match
- price context
- competing signals
- manual confirmation
- link confidence

## Phase P4: Coverage and scenario normalization

- no_ohlcv原因診断
- intraperiod coverage
- scenario identity
- duplicate candidate compression
- lifecycle outcome

## Phase P5: Offline A/B/C/STOP classifier

- report-only
- existing gates変更なし
- thresholdはCLI/report比較値
- long/short別
- regime別

## Phase P6: Historical replay

比較:

- current strict baseline
- A+B
- A+B+C observation
- notification frequency
- duplicate reduction
- false positive
- missed opportunity

## Phase P7: Shadow surface

- mail送信behavior変更なし
- HTMLまたはlocal reportのみ
- existing operator surfaceとsingle-source確認

## Phase P8: Human manual trial

- A: 通常の高品質候補
- B: 15分足確認後に人間判断
- C: 監視のみ
- STOP: 新規停止・利確・撤退

実取引とdecision eventを記録する。

## Phase P9: Evidence-backed tuning review

最低サンプルと人間承認を満たした場合だけ実施する。

---

## 12. Success criteria

初期評価:

| metric | target |
|---|---:|
| manual entry sample | 30以上 |
| manual decision events | 100以上 |
| entry win rate | 45%以上 |
| PF | 1.30以上 |
| average R | +0.20R以上 |
| max single loss | 原則-1.20R以内 |

実用評価:

| metric | target |
|---|---:|
| manual entry sample | 50以上 |
| manual decision events | 200以上 |
| PF | 1.50以上 |
| average R | +0.30R以上 |

必須分解:

- A vs B
- long vs short
- trend vs range vs transition
- setup type
- market / limit retest / breakout / counter scalp

勝率だけで変更判断しない。

---

## 13. Human approval gates

以下は必ず人間承認を必要とする。

- production threshold変更
- `trade_execution_gate`変更
- `phase1b_lite_gate`変更
- `opportunity_gate`変更
- notification trigger変更
- production wording変更
- runtime schedule変更
- live追加通知
- automatic / semi-automatic order design
- API behavior変更

---

## 14. Explicit prohibitions

- `trade_execution_gate`を緩和しない。
- `phase1b_lite_gate`を勝手に変更しない。
- `opportunity_gate`を勝手に緩和しない。
- `paper_orders planned`を増やす目的の変更をしない。
- `trend_flip_confirmed_up`を根拠なく強評価へ戻さない。
- Phase 1B正式昇格を勝手にしない。
- unresolved / no_ohlcvを勝ち負けへ混ぜない。
- candidate row数を独立機会数として扱わない。
- review cueをentry ruleへ変換しない。
- 単一例からtuningしない。
- 実弾発注をしない。
- 取引所API送信をしない。
- 秘密鍵連携をしない。
- `.env`、認証情報を変更しない。

---

## 15. Expected product outcome

```text
厳格なA候補の品質を維持しながら、
B候補によって人間が15分足で選別できる実践機会を増やす。

C候補によって、まだ早い機会を消さずに監視する。

STOPによって、転換時の大損を避け、
新規entryだけでなく利確・撤退判断も支援する。

候補行をscenarioへ圧縮し、
人間が処理できる数の有用な判断イベントへ変換する。
```

最終目的は通知数を増やすことではない。

```text
メールを起点に15分足を確認した人間の判断品質を上げ、
一定期間のactual R、PF、損失回避、機会損失削減を改善すること。
```


---

## 16. Existing import-design reconciliation

既存のactual trade import資料には、raw input pathの差異がある。

### Earlier readiness package

参照:

```text
docs/operations/ai-orchestration/VER04_V1_IMPLEMENTATION_READINESS_PACKAGE_20260702.md
```

記載:

```text
docs/mexc_csv/
```

### Later self-improvement final design

参照:

```text
docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md
```

記載:

```text
local/manual_trade_imports/YYYYMMDD/
```

raw exportはprivate/local/generated inputであり、source documentation treeの`docs/`配下より、明示的なlocal-only領域の方が安全な可能性が高い。

ただし、この計画だけでpathを推測確定しない。

Phase P1 active specで次を確認して正本を1つに固定する。

- 現在の実ファイル配置
- `.gitignore`の保護範囲
- 既存tool / testの参照
- migrationが必要か
- `docs/mexc_csv/`が履歴上の一時配置か
- `local/manual_trade_imports/YYYYMMDD/`をcanonicalにする場合の互換方針

P1完了条件に、raw input pathの一意な確定を追加する。

曖昧な2経路を並行運用しない。
