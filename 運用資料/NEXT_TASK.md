# NEXT TASK TRACKER

更新日: 2026-04-10 10:05 JST
運用メモ: このファイルを AI の日常入口にする。実行履歴は `履歴/progress.md` に記録し、ここには「次の判断に必要な情報」だけを残す。
補足: フェーズや大型節目の確認が必要になったときだけ [開発ロードマップ.md](開発ロードマップ.md) を開く。
評価シート更新の定型手順: [運用資料/運用/実務/評価シート更新_AI手順.md](運用/実務/評価シート更新_AI手順.md)

## 現在の状況
- 主対象は `iMac 2019` で動かしている `Ver02.4-v1`。日常の通知観測と品質判断はこの 1 本で進める。
- `MBP2020` の `Ver02.1` は `2026-03-31 03:39 JST` に停止し、`/Users/marupro/CODEX/archive/BTC_FX_CODEX_ver02_20260331_0339.tgz` へ凍結退避済み。`mbp2020-btc` は archive 参照用。
- `iMac 2019` の旧 `Ver02.1` 状態同期ジョブ `com.afrog.btc-monitor-status-sync` は停止後に定義ごと整理し、現行運用から外した。旧版参照が必要なときだけ `tools/sync_ver021_prod_status.sh` を手動実行する。
- フェーズはまだ `Ver02.4 / Phase 0 本番観測中`。ただし次段階の主対象はレビュー蓄積ではなく `Phase 1` の本有効確認へ移した。
- ブランチ整理として、`Ver02.3v4` は v5 着手直前の安定点 `7b8c02b` に戻し、`Ver02.4-v1` は価格精度の AI 事後評価を含む現行開発版として扱う。
- 通知表示は `notification_context` を共通層にして、件名・本文・詳細 HTML・`evaluation_trace` で `ステータス` `執行判断` `方向判断` を同じ順番で出す形へ更新済み。説明メモは [通知共通層_notification_contextメモ.md](運用/実務/通知共通層_notification_contextメモ.md)。
- 通知の人間向け出口は `最終ランク` に一本化した。現在の主表示は `⚪ 送信なし / 👀 注意報 / 📊 通常の本通知 / 🟠 高め本通知 / 🔥 強い本通知` の 5 段で、`執行可 / 監視 / 無効 / 注意報 / 中立` は補足状態として下段表示に回した。
- 詳細 HTML は取引所ロウソク足を使った `4時間足 / 1時間足 / 15分足` の3段チャートへ更新した。上段は大局方向、中段は再検討帯の妥当性、下段は入る価格・SL・TP の確認に使う。
- 再検討ラインチャートは 15 分足を主役にして、価格帯・SL・TP1・TP2 を同じ図で見られるようにした。人の確認にも AI の事後評価にもこの図を使う。
- `NOTIFICATION_HTML_ENABLED=true` の実運用確認を実施し、MacServer 公開は `maruPro@192.168.50.5` + `~/.ssh/id_ed25519_afrog_lan` 明示で成功する形へ修正済み。確認用の実送信ではメール本文末尾の `【詳細ページ】` URL と公開 HTML の `200 OK` まで確認した。
- AI の役割は「全サイクル補足」から「通知時監査」へ再設計する方針で整理した。検証と新方針の履歴メモは [AI役割再設計_通知監査移行設計.md](計画/履歴/AI役割再設計_通知監査移行設計.md)。
- 通知評価は `HTML + JSON` 正本で維持しつつ、主軸を `AI事後評価` に切り替えた。`user_reviews.csv` は AI 正本、人の修正は `human_override` として保護する。
- 評価フォームでは、各通知カードの上部で `24時間後機械評価` `AIレビュー` `人が確認` の3段階進捗が見えるようにし、`未完了だけ表示` も `ON / OFF` が視覚的に分かる形へ更新した。
- AI事後評価の現行運用を [AI事後評価運用_Ver02.4-v1.md](計画/AI事後評価運用_Ver02.4-v1.md) に整理した。`daily-sync` は既定で新規AI評価を走らせず、`sync-ai-post-reviews` だけで少量追加する。
- クレジット制御として、既定は `1日最大2件`、`main通知優先` にした。保存済み `ai_post_reviews` は再利用し、既存AI評価の再実行はしない。
- `primary_setup_status=ready` と `phase1_active=true` の意味と実測発生率は [Phase1条件の見方.md](計画/Phase1条件の見方.md) に整理した。
- 実運用は `launchd` に切り出した。`03:20 JST` に `daily-sync`、`03:35 JST` に `sync-ai-post-reviews` を回す構成にした。
- レビュー対象は `2026-03-30 05:05 JST` 以降の通知だけ。古い通知はレビュー画面と集計から外す。
- `2026-03-31 03:24 JST` の `daily-sync` 結果では、完了データ 32 件、全体勝率 71.9%、近似PF 0.75、レビュー要約は `useful_entry=3`、`too_late=1`、平均役立ち度 2.25 / 5。
- `Ver02.3v4` までは、`ENTRY_OK + invalid` の整合補正、`long` 側の反発示唆過大評価の抑制、feedback report の `bias別 direction 正誤` / `risk flag 群別 wrong rate` / `直近12時間速報` を追加済み。
- `Ver02.4-v1` では、AI の役割を「通知時監査 + 通知後24時間の価格精度評価」へ拡張し、通知で示した価格帯・SL・TP が妥当だったかを後追いで記録できる。
- `daily-sync` は `Phase 1 判定サマリー` に加えて、`SL評価 / TP評価 / 15分足評価` など価格精度ベースの改善候補まで出せる状態になった。
- `Ver02.3v4` と `Ver02.3-v5` の差分要約メモを [Ver02.3v4とVer02.3-v5の差分要約.md](計画/履歴/Ver02.3v4とVer02.3-v5の差分要約.md) として保存済み。
- 直近確認では `direction_execution_conflict=3件`、`countertrend_long_cluster=4件` を速報で拾える状態になった。
- `Phase 1` 前倒し判断の整理を `phase1-forwarding-gate` でコミット `574eefe` として確定した。`daily-sync` は `Phase 1 判定サマリー` と判定文、直近観測対象表示まで出る。
- Global_BOX の `開発環境/iMac 2019` は `2026-04-02 15:28 JST` 時点の実測へ更新済み。現在ロード中は `com.afrog.btc-monitor` のみ。

## 次のタスク
1. `daily-sync` で `Phase 1 判定サマリー` を見て、`phase1_active=true` と `primary_setup_status=ready` の本番母数を先に確認する。
2. `launchd` の `com.afrog.btc-feedback-daily-sync` と `com.afrog.btc-ai-post-reviews` が動いていることを確認する。
3. `15分足評価=poor` や `tp_eval=too_far / too_close` がどの通知で出るかを見て、価格帯・SL・TP の改善対象を切り出す。
4. `ENTRY_OK` で `too_late` が再発するかを観測し、`confidence_jump` / `prelabel_improved` / `status_upgraded` の 1 本前で通知できる余地があるかを見る。
5. `NO_TRADE_CANDIDATE` で `skip_too_strict` が再発するかを観測し、再現したら `src/analysis/position_risk.py` の閾値見直し候補として切り出す。
6. レビューは最低 5 件を維持しつつ、以後の主評価は AI に任せる。人は `human_override` が必要なケースだけ直す。
7. 実送信メールで 3 段チャートの見え方を確認し、下段 15 分足で「入る価格 / SL / TP」が直感的に読めるかを確認する。
8. `📊 / 🟠 / 🔥 / 👀` の最終ランクが届いた実メールを見て、直感とズレる通知がないかを確認する。ズレがあれば `signal_tier` と `high_main` 条件のどちらが原因かを切り分ける。
9. `Ver03` 昇格条件は維持するが、`Phase 1` の本有効確認そのものは `Phase 0` 完了前でも前倒しで進める。

## ブロッカー
- フォームのワンクリック保存は `serve-review-form` を前提に運用する。未起動時は localStorage 下書きにしか残らないため、レビュー考察へ反映されない。
- `tests/test_codex_cli_wrapper.py` の不一致は別件として残っているが、通知評価運用より優先度は下げる。
- `tests/test_log_feedback.py` の `test_improvement_candidates_have_expected_limits` は既存レビュー母数依存で現時点 1 件不一致。今回の通知表示改修とは切り分けて扱う。

## 完了条件
- レビュー運用: フォーム保存から `review_form_state.json` / `user_reviews.csv` / Obsidian 要約がそろう状態を維持する。
- Phase 0: 通知発生から 24 時間後評価までを本番で 1 周完了し、レビューは最低 5 件を確認すれば次段階の停止条件から外す。
- Phase 1: `primary_setup_status=ready` と `phase1_active=true` を本有効として、正式指標を実データで確認できる状態にする。現時点では未到達。
