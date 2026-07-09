# 20260709 operator HTML mock v2

## v1から変えたこと

- `Current Price` を `現在値` に変更した
- `BTCFX Manual Trading Report / Operator Mock` を `BTCFX 手動判断レポート / デザイン案` に変更した
- 最上段に `結論` を追加した
- `方向メーター` を追加し、ロング / ショート / 待機を横バーで見せた
- `Big Chance / Failed Thesis` を `大転換候補 / 失敗シナリオ` に変更した
- `これはエントリー指示ではありません` を主表示にし、英語文は小さな安全メモへ下げた
- `shallow zone` / `defense zone` を `浅い反応帯` / `本命防衛帯` に置き換えた
- `pattern A/B` を `例A/B` に変更した
- 内部語は `内部補足` に畳んだ

## 本番適用時に残すべき構成

- answer-first の結論
- ロング / ショート / 待機の方向メーター
- chart-first の大きな表示領域
- 短い `今やること`
- 少数の理由
- Big Chance は小さな補助箱
- Phase4 cue は `読み方メモ` として簡略化

## 本番適用時に出さない方がよい表現

- `active_limit_retest`
- `chart_review_only`
- `not_directly_evaluated`
- `preserve cue`
- `entry prohibition`
- raw cue ID の大きな見出し表示

## 未決定事項

- 方向メーターの値をどの既存データから表示するか
- 4時間足 / 1時間足 / 15分足の実チャートをどの密度で載せるか
- Big Chance と Value Defense の配置順
- 内部補足を本番では完全非表示にするか、折りたたみにするか

## mock-only safety note

この v2 は mock-only / artifact-only です。  
runtime-applied ではありません。  
source / runtime / notification behavior は変更していません。

