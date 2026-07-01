# Ver04-v1 Manual 15m Win Definition

## Metadata

- repo: `afrogdesign/BTC_FX_CODEX`
- working_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- created_at: `2026-07-02`
- status: definition draft for user-reviewed product direction
- prior_baseline: `Ver03-v4`
- related design: `docs/operations/strategy/VER04_V1_SELF_IMPROVEMENT_LOOP_FINAL_DESIGN_20260702.md`
- related product plan: `docs/operations/strategy/VER04_V1_INTEGRATED_PRODUCT_PLAN.md`
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

## 1. Purpose

この文書は、「15分足で人間が勝てる」という言葉を、BTCFX Ver04-v1 の設計・評価・事後レビューで使えるように具体的に定義する。

この定義は、感覚的な「なんとなく勝てそう」ではなく、notification mail を受け取った人間が 15分足を見て判断する manual trading support の成績を測るための定義である。

## 2. Short definition

```text
15分足で人間が勝てる
=
通知メールをきっかけに人間が15分足を確認し、
entry / watch / skip / exit / take-profit を判断した結果、
十分な回数の実運用サンプルで、
損失を限定しながら、正の期待値を継続的に出せる状態。
```

ここでいう「勝てる」は、毎回勝つことではない。

次を満たす状態を指す。

- 入るべき場面を一定以上拾える。
- 入らないべき場面を一定以上避けられる。
- 損失を小さく抑えられる。
- 転換期の大損を避けられる。
- 一定サンプルで PF / 平均R / 最大損失が許容範囲にある。
- 判断ルールが再現可能で、たまたまではない。

## 3. What this does NOT mean

「15分足で人間が勝てる」は、次を意味しない。

| not meaning | explanation |
|---|---|
| 通知が来たら即entryする | mail は order ではなく、15分足確認のトリガー |
| 全通知で勝つ | 見送り・待機も成功に含む |
| 勝率だけが高い | PF / R / 最大逆行 / 大損回避も必要 |
| 人間の勘だけで勝つ | system の方向・risk・15m action が役立つ必要がある |
| 自動売買できる | automatic order readiness とは別 |
| ノーリスクで勝てる | 小さな損失は許容し、大きな損失を避ける設計 |

## 4. Evaluation unit

### 4.1 Primary unit: mail-triggered manual decision event

評価単位は、原則として1通の notification mail を起点にした人間の判断である。

```text
mail-triggered manual decision event
=
notification mail が届いたあと、
人間が15分足を確認し、
何らかの判断をした1イベント。
```

1イベントには、entry だけでなく、watch / skip / exit / take-profit も含める。

### 4.2 Required event fields

最低限、次を記録する。

| field | meaning |
|---|---|
| `mail_signal_id` | 通知ID |
| `mail_timestamp_jst` | 通知時刻 |
| `human_checked_at_jst` | 人間が15分足を確認した時刻 |
| `priority_direction` | system が優先した方向: SHORT / LONG / NEUTRAL |
| `human_side` | 人間が実際に検討/entryした方向: short / long / none |
| `human_action` | entered / watched_no_entry / skipped / exited / took_profit |
| `entry_price` | entry した場合の価格 |
| `sl_price` | 想定または実際のSL |
| `tp1_price` | 想定または実際のTP1 |
| `tp2_price` | 想定または実際のTP2 |
| `result` | tp1 / tp2 / sl / avoided_loss / missed_opportunity / unclear |
| `manual_note` | 人間の短い理由 |

## 5. Decision categories

### 5.1 Entry decision

人間が実際に入った場合。

```text
human_action = entered
```

成功判定は、原則として R multiple で行う。

| result | definition |
|---|---|
| `tp1` | entry 後、SLより先に TP1 へ到達 |
| `tp2` | entry 後、SLより先に TP2 へ到達 |
| `sl` | TP1より先に SL 到達 |
| `manual_exit_win` | TP1未到達でも裁量撤退でプラス |
| `manual_exit_loss` | SL未到達でも裁量撤退でマイナス |
| `breakeven` | ほぼ±0 |
| `unclear` | 判定材料不足 |

### 5.2 Watch decision

人間が見たが入らなかった場合。

```text
human_action = watched_no_entry
```

これは失敗ではない。

成功例:

- entry形にならず、その後も伸びなかった。
- 転換警戒が出ていて、入らずに大損を避けた。
- 方向は合っていたが、15分足の位置が悪く、待ちが妥当だった。

失敗例:

- 良い entry形が出ていたのに、件名や警戒表現が強すぎて見送った。
- その後 TP1/TP2 相当まで伸びた。

### 5.3 Skip decision

人間が見送り判断をした場合。

```text
human_action = skipped_bad_setup / skipped_late / skipped_defensive_subject
```

skip の成功/失敗は、機会損失と損失回避の両方で評価する。

| result | meaning |
|---|---|
| `avoided_loss` | 見送って正解。入っていたら損失リスクが高かった |
| `missed_opportunity` | 見送りにより利益機会を逃した |
| `skip_neutral` | 見送り後も大きな機会なし |
| `unclear` | 判定不能 |

### 5.4 Exit / take-profit decision

通知が新規entryではなく、既存ポジションの利確・撤退判断に役立った場合。

```text
human_action = exited / took_profit
```

これは重要な成功に含める。

特に転換期では、新規entryよりも利確・撤退が価値になる。

## 6. Success definition

### 6.1 Trade-level success

実際に entry したイベントでは、次のいずれかを success とする。

| success type | condition |
|---|---|
| `tp1_success` | SLより先に TP1 到達 |
| `tp2_success` | SLより先に TP2 到達 |
| `positive_manual_exit` | 裁量撤退でプラス |
| `good_risk_trade` | 小損または建値で撤退し、大損回避できた |

単純な勝敗だけではなく、Rで評価する。

### 6.2 Decision-level success

entry しなかったイベントも success になりうる。

| success type | condition |
|---|---|
| `avoided_loss` | 入らずに損失を避けた |
| `correct_wait` | まだ entry形でなく、待ちが正しかった |
| `take_profit_saved` | 転換前に利確できた |
| `exit_saved_loss` | 逆行前に撤退できた |

### 6.3 System-level success

システムとしての成功は、個別トレードではなく一定期間で見る。

```text
system-level success
=
mail-triggered manual decision events の集合で、
正の期待値を出し、
大損を避け、
人間の判断負担を下げている状態。
```

## 7. Failure definition

### 7.1 Trade-level failure

| failure type | condition |
|---|---|
| `sl_first` | TP1より先にSL到達 |
| `large_adverse_move` | 想定SLを超える大きな逆行 |
| `late_entry` | 方向は合っていたが遅く入って損失 |
| `bad_chase` | 伸びた後に追いかけて損失 |
| `fakeout_loss` | だましで損失 |

### 7.2 Decision-level failure

| failure type | condition |
|---|---|
| `missed_opportunity` | 良い機会を見逃した |
| `over_suppression` | 件名・ラベルが守りすぎて entry を妨げた |
| `turning_point_missed` | 転換を見逃して大きな逆行リスクを受けた |
| `wrong_side_bias` | short/long の優先方向が相場転換に追随できなかった |
| `no_action_when_actionable` | 15分足では入れる形なのに NO_ACTION になっていた |

## 8. Quantitative thresholds

### 8.1 Initial evaluation threshold

初期段階では、次の条件を満たしたら「実用的に勝てる可能性がある」とみなす。

| metric | initial target |
|---|---:|
| manual entry sample | 30 trades minimum |
| manual decision events | 100 events minimum |
| manual entry win rate | 45% or higher |
| manual entry PF | 1.30 or higher |
| average R | +0.20R or higher |
| max single loss | -1.20R以内を原則 |
| large-loss events | 0 or clearly explainable |
| missed opportunity rate | tracked, reducing trend |
| turning point missed | tracked, reducing trend |

この段階は「仮説として有効」。まだ自動化判断には使わない。

### 8.2 Practical useful threshold

次を満たすと、「人間が使う実用支援としてかなり有効」とみなす。

| metric | practical target |
|---|---:|
| manual entry sample | 50 trades minimum |
| manual decision events | 200 events minimum |
| manual entry win rate | 48% or higher |
| manual entry PF | 1.50 or higher |
| average R | +0.30R or higher |
| max drawdown by manual sequence | acceptable and known |
| avoided_loss count | clearly positive contribution |
| over_suppression count | decreasing |
| turning point missed | rare and reviewed |

### 8.3 Strong threshold

次を満たすと、「かなり使える」とみなす。

| metric | strong target |
|---|---:|
| manual entry sample | 100 trades minimum |
| manual decision events | 300+ events |
| manual entry PF | 1.80 or higher |
| average R | +0.40R or higher |
| max single loss | controlled within rule |
| long/short regime split | both measured |
| turning brake effectiveness | proven |

この段階でも、automatic trading readiness とは別扱いにする。

## 9. R-based evaluation

勝率だけでは不十分なので、R multiple を主指標に入れる。

```text
R = entry price と SL price の距離を 1R とする。
```

Short の例:

```text
entry = 60000
SL = 60300
risk = 300 = 1R
TP1 = 59700 -> +1R
TP2 = 59400 -> +2R
```

Long の例:

```text
entry = 60000
SL = 59700
risk = 300 = 1R
TP1 = 60300 -> +1R
TP2 = 60600 -> +2R
```

評価は次を記録する。

- actual R
- max favorable excursion in R
- max adverse excursion in R
- TP1 first / SL first
- manual exit R

## 10. Mail usefulness definition

メールが役に立ったかは、entry の有無だけで評価しない。

### 10.1 Useful mail

次のいずれかを満たす場合、useful とする。

- 15分足を見る価値があった。
- 実際に entry して利益につながった。
- entryしなかったが、損失回避に役立った。
- 利確・撤退判断に役立った。
- long/short 転換の初動把握に役立った。
- 見送りでも今後の判断材料として有用だった。

### 10.2 Not useful mail

次の場合は not useful とする。

- 方向も行動も曖昧で、見る価値がなかった。
- 件名が守りすぎて、実際には良い機会を逃した。
- 15分足上で明らかに遅すぎた。
- long/short の方向表示が実態と逆だった。
- 転換警戒が遅すぎた。

## 11. Long / short balance definition

「short も long も同じくらい機会を知りたい」は、同じ回数 entry することではない。

正しい定義:

```text
long / short の機会を常に両方検出し、
現在の regime に応じて優先方向を変え、
反対方向も scout / exhaustion / turning watch として提示する。
```

評価は分ける。

| metric | purpose |
|---|---|
| `manual_short_win_rate` | short 手動entryの成績 |
| `manual_long_win_rate` | long 手動entryの成績 |
| `short_opportunity_usefulness` | short通知の有用性 |
| `long_opportunity_usefulness` | long通知の有用性 |
| `short_to_long_transition_success` | short相場からlong初動を拾えたか |
| `long_to_short_transition_success` | long相場からshort初動を拾えたか |

## 12. Turning point success definition

BTCでは転換期の大きな動きを見逃すと、大きな損失リスクがある。

したがって、turning point は独立して評価する。

### 12.1 Turning point saved

次の場合、success とする。

- short中に踏み上げ警戒を出し、利確・撤退・新規停止に役立った。
- long中に急落警戒を出し、利確・撤退・新規停止に役立った。
- 反対方向 scout を早めに出し、相場転換の準備ができた。

### 12.2 Turning point missed

次の場合、failure とする。

- short優勢表示のまま、15分足で上昇転換が始まった。
- long優勢表示のまま、15分足で下落転換が始まった。
- 主要サポート/レジスタンスの役割転換を見逃した。
- 転換警戒が出た時には既に大きく動いた後だった。

### 12.3 Turning brake false alarm

次の場合、false alarm とする。

- 転換警戒HIGHで攻めを止めたが、実際には継続方向へ大きく伸びた。
- 利確優先を出したが、継続保有の方が明らかに良かった。

False alarm は悪ではないが、多すぎると機会損失になる。

## 13. Over-suppression definition

攻め型運用では、守りすぎも失敗として扱う。

```text
over_suppression
=
方向予測は有効で、15分足でもentry可能性があったのに、
件名・ラベル・gate が安全側に倒れすぎて、
人間のentry判断を妨げた状態。
```

典型例:

- 件名が `売買非推奨` だが、15分足では戻り売り/押し目買いの良形だった。
- `NO_TRADE_CANDIDATE` だが、その後TP1相当まで動いた。
- `ENTRY_OK` ではなく `WATCH_ONLY` だったが、実際には攻めB相当だった。
- 転換警戒がLOWなのに、実行不可表現が強すぎた。

## 14. Practical interpretation

「15分足で人間が勝てる」を最も実務的に言うと、次である。

```text
メールが来たことで、
人間が15分足を見るべきタイミングを知り、
入る / 待つ / 見送る / 利確する / 撤退する判断の質が上がり、
一定期間でトータルのRがプラスになること。
```

ここには、勝ちトレードだけでなく、損失回避と機会損失削減も含む。

## 15. Implementation implication

この定義により、今後の事後評価は次を必須とする。

1. `manual_15m_judgments.csv` または同等の人間判断ログが必要。
2. entry だけでなく watch / skip / exit / take-profit を評価する。
3. 勝率だけでなく PF / R / avoided_loss / missed_opportunity を見る。
4. short / long を別々に見る。
5. turning point を独立評価する。
6. over_suppression を失敗候補として扱う。
7. AI事後評価は補助であり、 deterministic な評価定義が主役。

## 16. Final definition

最終定義:

```text
Ver04-v1 における「15分足で人間が勝てる」とは、
notification mail を起点に人間が15分足を確認し、
entry / watch / skip / exit / take-profit を判断した結果、
十分なサンプル数で、
manual entry の期待値がプラスであり、
見送りによる損失回避も機能し、
守りすぎによる機会損失が管理され、
転換期の大損リスクが抑えられている状態を指す。

これは自動売買可能性の定義ではなく、
人間が攻めの姿勢で実用的に勝つための trading support quality の定義である。
```
