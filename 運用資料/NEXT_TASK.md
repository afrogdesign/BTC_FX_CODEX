# NEXT TASK TRACKER

更新日: 2026-06-08 JST

このファイルは人間向けの入口です。
AI / Codex / future agents の現在地は `docs/operations/ai-orchestration/CONTROL.md` を正本にします。

## 現在のブランチ

- current branch: `Ver03-v2`
- Ver03-v2 は、Ver03-v1 の計画フォルダ再構成完了点 `e3506e4` から分岐したブランチ。
- Ver03-v2 の最初の目的は、トレードロジック実装ではなく、AI / Codex 運用基盤を安定させること。

## AI運用正本

- Codex固定ルール: `AGENTS.md`
- 現在地: `docs/operations/ai-orchestration/CONTROL.md`
- AI向けrepo地図: `docs/operations/ai-orchestration/REPO_MAP.md`
- 作業台帳: `docs/operations/ai-orchestration/TASK_LEDGER.md`
- 判断ログ: `docs/operations/ai-orchestration/DECISIONS.md`
- プロンプト雛形: `docs/operations/ai-orchestration/PROMPTS.md`
- 引き継ぎ: `docs/operations/ai-orchestration/handoffs/CURRENT_HANDOFF.md`

## プロダクト計画正本

- 計画入口: `運用資料/計画/README.md`
- 統合再計画: `運用資料/計画/00_Ver03-v1_統合再計画_20260608.md`
- 実装ロードマップ: `運用資料/計画/02_Ver03-v1_実装ロードマップ_20260608.md`
- AI参照ファイル設計: `運用資料/計画/03_AI参照ファイル設計_20260608.md`
- 次にCodexへ渡す作業方針: `運用資料/計画/04_次にCodexへ渡す作業方針_20260608.md`

## 現在の方針

このrepoの目的は、実際のBTC市場に合わせた、実践的で実用性の高いトレード支援システムを作ること。

段階:

1. メール通知で人間が取引する。
2. Active Planで、成行、指値待ち、ブレイク追随、逆方向短期、保有中処理を提示する。
3. ログと診断で実用性を検証する。
4. intraperiod検証で、entry到達、TP/SL先行、timeout、MFE/MAEを評価する。
5. 安全装置を整備する。
6. 将来的に自動トレードへ進む。

## 次にやること

1. `docs/operations/ai-orchestration/CONTROL.md` を開く。
2. `Next recommended task` を確認する。
3. ChatGPTがrepoを確認してから、Codexへ短い `NEXT <WORK_ID>` を出す。

## 禁止事項

- 実弾発注APIを追加しない。
- 取引所APIキーや秘密鍵を扱わない。
- 自動注文送信をしない。
- `ACTIVE_*` を正式GOとして扱わない。
- `trade_execution_gate=pass` と `ACTIVE_*` を混同しない。
- runtime再起動は明示指示がある場合だけ行う。
