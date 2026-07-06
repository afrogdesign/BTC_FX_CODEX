# BTC_BIG_CHANCE_FAILED_THESIS_DESIGN_20260706

## 背景

20260706 の失敗ケースでは、attention レポートの中に「long で見る理由」と同時に「その long が崩れたら短期で大きく伸びる」という兆候が含まれていた。

現状のシステムは、注意喚起や Value Defense、トレンド転換レビューの材料は出せている。しかし、その情報を「失敗した仮説の次の機会」という戦略層に昇格できていない。

この文書の目的は、失敗を単なるリスクではなく、次の大きな機会として扱うための設計原則を明文化すること。

## 20260706の失敗から得た本質

- long で追う前提が弱くなった瞬間、short の大きなチャンスになることがある。
- short で追う前提が弱くなった瞬間、long の大きなチャンスになることがある。
- BTC は「失敗した thesis の裏側」で鋭く動くことがある。
- HTF は trap / fuel を決める。15m は activation / invalidation を確認する。

この失敗は「守りが足りなかった」だけではない。
本質は、「失敗した thesis を次の機会に変換するレイヤーが無い」ことにある。

## 最重要原則: Failed Thesis is Opportunity

```text
Failed Thesis is Opportunity
```

意味は次の通り。

- 失敗した long thesis は、short の big chance を示す。
- 失敗した short thesis は、long の big chance を示す。
- 失敗は終点ではなく、反対側の加速候補になる。
- ただし、これは entry 指示ではない。report-only の review concept である。

## BTCでこの考え方が重要な理由

BTC は、レンジからトレンド、トレンドから reclaim、reclaim から extension へ移りやすい。
そのため、単純な「買い / 売り」ではなく、失敗仮説の反転を早く見つけた方が強い。

特に重要なのは以下。

- 4H / 1H が trap の文脈を作る
- 15m が activation と invalidation を決める
- shallow retest は単独では不十分
- support-to-resistance / resistance-to-support の反転は fuel になる
- 微益で終えると、BTC の大きな伸びを取り逃がしやすい

## 現システムの問題

- Value Defense はあるが、「失敗した thesis の次の機会」を別レイヤーとして表現していない。
- attention / followup / self-review はあるが、Big Chance の候補として統合されていない。
- normal long / short のスコアに足し込むだけでは、拡張局面と通常局面が混ざる。
- 15m の短期判断だけで late chase すると、trap を増やす。

## 既存資産として活用できるもの

- `market_map`
- `value_defense_entry_layer`
- `attack_review_flags`
- `self_review_readiness`
- `judgment_self_review`
- `followup` 通知レイヤー
- `detail_page` の report-only UI

既存資産は十分ある。必要なのは「Failed Thesis / Big Chance」という上位概念の追加であり、既存スコアの再配点ではない。

## 作るべき Big Chance / Failed Thesis Layer

この層は、正常な long/short の候補とは別に置く。

### 役割

- 失敗した thesis を検知する
- その失敗が反対側の fuel かを評価する
- 15m の activation を待つ
- human が追う価値があるかを report-only で示す

### 非役割

- 自動注文
- 既存スコアへの単純加点
- ルールの暴走
- Phase4 tuning の即時許可

## Macro Context Layer

HTF で trap / fuel を判定する上位層。

見るべき信号の例:

- 4H の reclaim / exhaustion
- 1H の range ceiling reclaim
- support-to-resistance / resistance-to-support の反転
- early trend flip
- breakout extension の余地

Macro Context Layer は「どちら側の thesis が崩れやすいか」を先に決める。

## Failed Thesis Detector

失敗仮説検出器は、既存の market_map / Value Defense / self-review の情報から次を見つける。

- 先に置いていた方向性が崩れている
- 1H が弱い / reclaim している
- 15m が shallow retest で再加速し得る
- 反対側の stop / cover fuel がある
- 既存の TP では拡張余地を取り逃がす

重要なのは「entry 可能性」ではなく、「failed thesis から big chance へ移る条件」を見つけること。

## Big Chance Candidate schema draft

```json
{
  "schema_version": "big_chance_failed_thesis.v1",
  "side": "long | short",
  "type": "failed_thesis | reclaim_extension | continuation_after_failure",
  "status": "watch | armed | triggered | follow_through | invalidated",
  "score": 0,
  "grade": "A | B | C | D",
  "macro_context": {
    "htf_trap": true,
    "htf_reclaim": false,
    "trend_regime": "range | transition | reclaim | extension"
  },
  "failed_thesis": {
    "prior_side": "long | short",
    "failure_reason": ["support_to_resistance", "1h_reclaim", "trend_flip"]
  },
  "activation": {
    "activation_tf": "15m",
    "activation_condition": "shallow_retest_break | reclaim_confirm | continuation_close"
  },
  "invalidation": {
    "invalidation_tf": "15m",
    "invalidation_reason": ["rejection", "reclaim_failure", "range_reentry"]
  },
  "evidence": {
    "market_map": {},
    "value_defense": {},
    "self_review": {}
  },
  "safety_boundary": "report-only / not FORMAL_GO / no automatic order / human decides manually"
}
```

## 状態遷移: watch / armed / triggered / follow_through / invalidated

- `watch`: まだ thesis 失敗が見え始めた段階
- `armed`: HTF trap が揃い、15m で activation 待ち
- `triggered`: 15m で activation 条件を満たした
- `follow_through`: 方向が継続し、runner 候補を含む段階
- `invalidated`: 反対側の thesis が否定された

この状態遷移は normal long/short と別系統で扱う。

## スコア設計案

Big Chance score は normal long/short score と分離する。

```text
normal_score != big_chance_score
```

やってはいけないこと:

- normal score に点を足して Big Chance を混ぜる
- late chase を高得点で誤魔化す
- 15m だけで強引に判定する

代わりに:

- HTF context を first class にする
- 15m は activation / invalidation の確認に使う
- failed thesis の反対側にのみ高い Big Chance score を付ける

## UI / notification 表示方針

- public UI には normal long/short と分けて表示する
- failed thesis の反対側は「Big Chance Candidate」と明示する
- followup と混ざらないようにする
- report-only で、human が理由を読める表現にする
- 既存の `BTCFX Manual Trading Report` と `manual-trading` の枠組みを崩さない

## やってはいけないこと

- normal スコアの単純加点
- 自動注文
- ルールの過剰一般化
- Phase4 tuning の前倒し
- 失敗 thesis を単なるノイズとして捨てること
- 失敗 thesis を entry 指示に誤変換すること

## 段階的実装ロードマップ

### Phase 0: design doc only

- 本文書の整備
- review terms の固定

### Phase 1: local artifact only

- local のみで Big Chance 候補 JSON / Markdown を出す
- runtime / mail には影響させない

### Phase 2: detail HTML surface only

- Big Chance 候補を detail HTML に report-only 表示する
- subject / sending / scoring は変えない

### Phase 3: observation / replay

- 過去の notified snapshot で再生し、失敗 thesis と反対側の候補を確認する

### Phase 4: notification candidate

- followup や attention と並ぶ候補として通知するかを review する

### Phase 5: display priority adjustment

- human review を経て、必要なら表示優先度を調整する

No Phase4 scoring / gate tuning without explicit human approval.

## Safety boundary

- report-only
- not `FORMAL_GO`
- no automatic order
- human decides manually
- no scoring / gate / threshold tuning from this doc alone
- no runtime restart
- no launchd change
- no private/account/order endpoint access
- no raw exchange export commit
