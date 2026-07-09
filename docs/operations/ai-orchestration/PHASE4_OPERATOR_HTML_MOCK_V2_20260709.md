# Phase4 operator HTML mock v2

## purpose

v1 の方向性を保ったまま、visible UI の英語・内部語をさらに減らした operator-facing static mock を作成した。

## difference from v1

- `現在値` / `結論` / `方向メーター` を追加
- Big Chance を `大転換候補 / 失敗シナリオ` として日本語中心に変更
- `これはエントリー指示ではありません` を主表示に変更
- `shallow zone` / `defense zone` を `浅い反応帯` / `本命防衛帯` に変更
- 技術語は `内部補足` へ退避

## files created

- `local/design_mock/20260709_operator_html_mock_v2.html`
- `local/design_mock/20260709_operator_html_mock_v2.md`
- `docs/operations/ai-orchestration/PHASE4_OPERATOR_HTML_MOCK_V2_20260709.md`

## status

mock-only / not runtime-applied.  
source / tests / runtime / notification behavior は変更していない。

## next decision

human review of the mock を行い、その後に production implementation scope を決める。

