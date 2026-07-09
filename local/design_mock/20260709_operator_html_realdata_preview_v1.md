# 20260709 operator HTML real-data preview v1

## 目的

mock v2 の方向性を、自然生成された実データ HTML の値に当てた static preview です。  
本番実装ではなく、人間が real values / real operator text を見たときに読みやすいかを判断するための artifact です。

## 使用した実データHTML

- primary source: `logs/notifications_html/manual-trading/attention/20260709_040500.html`
- optional references were not needed for this v1

## v2 mockから引き継いだ構成

- answer-first の `結論`
- `現在値`
- ロング / ショート / 待機の `方向メーター`
- chart-first area
- 3 bullets の `今やること`
- compact Big Chance
- simplified `読み方メモ`

## 実データを入れて確認したい点

- `61,944.00` などの実値が入っても top section が読みやすいか
- attention でも「今は入らない」が明確に見えるか
- ロング / ショートの見送りと監視可が混乱しないか
- Big Chance が entry instruction に見えないか
- 浅い反応帯と本命防衛帯の読み分けが自然か

## 本番適用前の未決定事項

- 実 chart SVG をどの程度そのまま流用するか
- 方向メーターの数値を既存スコアからどう安全に表示するか
- attention / followup / main で top wording をどこまで変えるか
- Big Chance の score / grade を hero に出すか、下段だけにするか

## mock-only safety note

これは real-data preview only / mock-only です。  
runtime-applied ではありません。  
source / runtime / notification behavior は変更していません。

