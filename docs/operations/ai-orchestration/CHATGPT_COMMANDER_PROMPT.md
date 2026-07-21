# CHATGPT_COMMANDER_PROMPT

互換入口です。プロジェクト初期プロンプトの正本は次です。

`docs/operations/ai-orchestration/INITIAL_PROMPT.md`

別のcommander規則をこのファイルへ追加しません。

起動時は `INITIAL_PROMPT.md` を適用し、repo内では次を辿ります。

1. `AGENTS.md`
2. `START_HERE.md`
3. 必要時だけ `CURRENT_STATE.md` / `NEXT_ACTION.md`
4. 実装・FIX・acceptance時だけactive spec
5. 作業指示・review時は `AI_WORKFLOW.md`

同じthread・同じtaskではstable docsを再読せず、deltaだけを確認します。
