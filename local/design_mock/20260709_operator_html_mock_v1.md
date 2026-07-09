# 20260709 operator HTML mock v1

## 目的

自然生成 HTML は情報量が多く、operator が一目で判断しづらい。  
この mock は、実運用の detail page をどう単純化すると読みやすいかを確認するための design-only artifact です。

## いまの HTML が dense に見える理由

- cue card と technical label が多い
- 英語の変数風 wording が視線を止める
- 1 画面で「いま何を見るか」が先に入ってこない
- chart よりも説明テキストが前に出やすい

## mock で簡略化した点

- 最上段に「いまの見方」を大きく置いた
- ロング / ショート / 見送り を先に見せた
- chart を中央に大きく確保した
- 「今やること」を短くした
- 理由は 3〜6 個に絞った
- Big Chance は小さな補助箱にした
- Phase4 cue は「読み方メモ」に統合して密度を下げた

## mock で前面に出した情報

- current directional posture
- どの方向を watch するか
- どこを chart で確認するか
- 何に注意するか
- Big Chance は entry instruction ではないこと

## mock で脇に退けた情報

- raw cue ID
- variable-like English label
- technical jargon の連打
- 大量の detail card 群

## まだ残っている open question

- どの程度までチャートを実画像に寄せるか
- Safety boundary を hero へどの強さで残すか
- Big Chance / Value Defense をどこまで見出しとして残すか
- 15分足の実行帯を何個まで見せるか
- Phase4 cue の補足を完全に隠すか、極小 footnote にするか

## 次の判断

この mock を human review してから、実 HTML への反映可否を決める。  
これは mock-only / artifact-only であり、runtime-applied ではない。

