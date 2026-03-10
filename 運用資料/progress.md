# Progress Log

- 日時: 2026-03-10 16:19 JST
- 実施内容: ユーザー許可のうえで `run_cycle` を手動1回実行し、Ver02の新項目が実出力に入ることを確認した。結果は `prelabel=SWEEP_WAIT`、`location_risk=60.0`、`oi_value=81815.097`、`orderbook_bias=bid_heavy`、`market_structure_missing_fields=[]`、AI判定 `WAIT_FOR_SWEEP` で、位置フィルターと市場構造データが実運用ラインで動作していることを確認した。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: WS清算イベントは時間帯によって0件が続くため、イベント蓄積（ローカル保存）による安定化が次タスク。
- メモ: OpenAI API を使う手動実行は本件で実施済み（許可取得済み）。

- 日時: 2026-03-10 15:42 JST
- 実施内容: `NEXT_TASK` の実行を進め、`.venv312` に `websocket-client` を導入した。Binance REST 側（OI/板/CVD材料）の取得は実データで成功を確認した。WS清算イベントは0件継続だったため、`!forceOrder@arr` フォールバックと SSL 検証失敗時の接続フォールバックを追加して取りこぼし耐性を上げた。あわせて通知本文フォールバックの先頭が「方向」ではなく「位置評価」になることをローカル生成で確認した。
- 変更ファイル: `requirements.txt`, `src/data/provider_client/binance_market.py`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 清算イベントはテスト時点で0件のため、次の本番サイクルで実測確認が必要。`last_result.json` の新項目確認は1サイクル実行後に実施予定。OpenAI API を使う実通信確認はユーザー許可待ち。
- メモ: `fetch_market_structure` 単体テストで `missing_fields=[]`、`oi_value`・`oi_change_pct`・orderbook件数は取得できた。

- 日時: 2026-03-10 15:15 JST
- 実施内容: 打ち合わせシートに、今回のブランチ評価として「実用性はかなり上がったが、精度の大幅向上はまだ運用確認待ち」という整理を追記した。期待しすぎず、それでも前進ははっきりしているという温度感でまとめた。
- 変更ファイル: `打ち合わせシート.md`, `運用資料/progress.md`
- 未解決事項: 実ログ確認後に、この見立てを「仮評価」から「実績評価」へ更新する必要がある。
- メモ: 打ち合わせシートの `updated` は `2026-03-10 15:13 JST` に更新済み。

- 日時: 2026-03-10 15:05 JST
- 実施内容: Obsidian の打ち合わせシートに、今回の「流動性・清算・OI・CVD・板情報対応版」実装の報告を追記した。内容は技術ログではなく、今の状況・現在の動向・今後のやるべきことに分けて、位置フィルター化の意味が追いやすい形へ整理した。
- 変更ファイル: `打ち合わせシート.md`, `運用資料/progress.md`
- 未解決事項: 打ち合わせシート上の今後のやるべきことは、次回の本番サイクル確認後に進捗反映が必要。
- メモ: Obsidian ノートの `updated` は `2026-03-10 14:57 JST` に更新済み。

- 日時: 2026-03-10 14:57 JST
- 実施内容: 無料API前提の「流動性・清算・板情報対応版」を実装した。MEXCベースの既存判定は維持しつつ、Binance公開APIを使う市場構造取得層、流動性・清算クラスター・OI/CVD・板の分析モジュール、位置フィルターによる `prelabel` / `location_risk` / `risk_flags`、通知・要約・CSV・バックテスト追従を追加した。清算は有料ヒートマップではなく、直近の清算イベント集計による近似実装にした。
- 変更ファイル: `main.py`, `config.py`, `requirements.txt`, `.env.example`, `README.md`, `backtest/runner.py`, `prompts/advice_prompt.md`, `prompts/summary_prompt.md`, `src/data/exchange_fetcher.py`, `src/data/provider_client/binance_market.py`, `src/analysis/liquidity.py`, `src/analysis/liquidation.py`, `src/analysis/oi_cvd.py`, `src/analysis/orderbook.py`, `src/analysis/position_risk.py`, `src/ai/advice.py`, `src/ai/summary.py`, `src/notification/trigger.py`, `src/storage/csv_logger.py`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: Binanceの清算イベント取得は `websocket-client` 導入後に本番環境で実データ確認が必要。OpenAI API を使う実通信確認は、許可をもらってから行う。
- メモ: 構文チェックは `.venv312/bin/python -m compileall .` で通過。位置判定モジュールの単体サンプル実行でも `prelabel` と `risk_flags` の出力を確認した。

- 日時: 2026-03-10 13:48 JST
- 実施内容: 他プロジェクトでも使い回せるよう、`Global_BOX` に打ち合わせノート共通テンプレートを新規作成し、`AGENTS_TEMPLATE.md` に打ち合わせノートの運用ルールを追加した。今後は各案件で保存先だけ決めれば、同じ型をそのまま導入できる状態にした。
- 変更ファイル: `Global_BOX/AGENTS_TEMPLATE.md`, `Global_BOX/打ち合わせノートテンプレート.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 既存プロジェクトへ反映する場合は、それぞれの `AGENTS.md` に保存先と参照ルールを追記する必要がある。
- メモ: テンプレート本体と運用ルールを分けて用意したので、ノートの見た目と運用基準の両方を使い回せる。

- 日時: 2026-03-10 13:46 JST
- 実施内容: ユーザーが打ち合わせノートの見出しとレイアウトを調整した内容を確認した。今後は `見立て` ではなく `現在の動向` を使い、`今の状況` → `現在の動向` → `今後のやるべきこと` の順で、読みやすさ優先の追記形式に合わせる方針を反映した。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: なし
- メモ: 打ち合わせノートは技術ログ化せず、短く状況判断しやすい形を優先する。

- 日時: 2026-03-10 13:36 JST
- 実施内容: Obsidian の打ち合わせシートに、現在の監視システムの状況と今後やるべきことを、専門ログではなく判断しやすい要約として追記した。あわせて `NEXT_TASK.md` も、直近の確認ポイントがより追いやすい表現へ整理した。
- 変更ファイル: `打ち合わせシート.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: AI 判定復帰とメール本文の読みやすさは、次回以降の定時実行結果を見て確認が必要。
- メモ: 打ち合わせシートには中長期の見立てを、`運用資料/` には実務ログを置く使い分けを維持した。

- 日時: 2026-03-10 13:05 JST
- 実施内容: `progress.md` の日時記録を、推測ではなく実時刻ベースで残す運用に修正した。今後は更新直前に `date` コマンドで取得した JST をそのまま記録する。あわせて、根拠が取れた直近エントリの時刻をファイル更新時刻ベースで補正した。
- 変更ファイル: `運用資料/progress.md`
- 未解決事項: すでに残っている古いエントリには概算時刻が混ざる可能性があるため、厳密性が必要な場合は都度ログ照合が必要。
- メモ: 以後は「手入力のだいたい時刻」を避け、必ず実時刻を入れる。

- 日時: 2026-03-10 12:13 JST
- 実施内容: メール本文が `bias=short` や `long=59 short=74` のような生データ中心で読みにくい問題に対応した。`src/ai/summary.py` のフォールバック本文を、数値の意味を日本語で説明する文章へ変更し、AI要約成功時も同じ方向性になるよう `prompts/summary_prompt.md` を調整した。
- 変更ファイル: `src/ai/summary.py`, `prompts/summary_prompt.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 次回メールで、AI要約成功時とフォールバック時の両方が十分読みやすいか確認が必要。
- メモ: 「数字を見せる」より「意味を伝える」を優先する方向へ調整。

- 日時: 2026-03-10 08:11 JST
- 実施内容: 08:05 実行で `ai_summary_error` が発生し、要約生成のみ `APITimeoutError` で失敗していることを確認したため、要約側だけ別タイムアウト設定を持てるよう修正した。`AI_SUMMARY_TIMEOUT_SEC=10` を追加し、判定AIは `AI_TIMEOUT_SEC=5` のまま、要約生成のみ 10 秒待つ構成へ変更した。
- 変更ファイル: `config.py`, `main.py`, `.env`, `.env.example`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 設定反映後の次回実行で `ai_summary_error` が再発するかは確認が必要。
- メモ: 判定AIと要約AIを同じ待ち時間にせず、要約だけ長めにしたので、全体の応答性を大きく落としにくい。

- 記録ルール: 以後、`日付` ではなく `日時` を `YYYY-MM-DD HH:MM JST` 形式で記録し、更新直前に `date` コマンドで取得した実時刻を使う。

- 日時: 2026-03-10 07:53 JST
- 実施内容: 定時実行を 4時間ごとから 1時間ごとへ変更した。`.env` の `REPORT_TIMES` を毎時 `:05` 実行に更新し、常駐再起動で反映する前提にした。ユーザー観察として、2026-03-09 朝9時ごろのロングが理想タイミングだったという情報も踏まえ、短めの機会を逃しにくい運用へ寄せた。
- 変更ファイル: `.env`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 1時間運用で通知量が増えすぎないか、数サイクルの観察が必要。
- メモ: 15分足を使う判定ロジックに対して、1時間実行は 4時間実行より実戦に寄せた設定。

- 日時: 2026-03-10 07:48 JST
- 実施内容: `tools/start_monitor.sh` に実PID保存処理を追加し、`launchctl print` で取得した PID を `logs/runtime/monitor.pid` に書き込むよう修正した。修正反映のため常駐プロセスを再起動し、`monitor.pid=49076` と `launchd` 上の実PIDが一致することを確認した。
- 変更ファイル: `tools/start_monitor.sh`, `運用資料/README.md`, `運用資料/運用コマンドメモ.md`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 次回定時サイクル後に AI判定が復帰するかは引き続き確認が必要。
- メモ: PID ファイルは再起動時に同期される方式。手動で `launchctl` 操作だけ行った場合は、`tools/start_monitor.sh` を使う運用に寄せるとずれにくい。

- 日時: 2026-03-10 07:42 JST
- 実施内容: `tools/start_monitor.sh` で `launchd` 常駐プロセスを再起動し、最新の `.env` とコード変更を反映した。`launchctl print` で `com.afrog.btc-monitor` が `running`、PID `48843`、実行バイナリが `.venv312/bin/python` であることを確認した。あわせて `monitor.err` に新しいAIエラーは出ていないことも確認した。
- 変更ファイル: `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: `logs/runtime/monitor.pid` は古い PID `37423` のままで、実プロセスPIDと一致していない。必要なら PID ファイル更新処理を別途追加する。
- メモ: `logs/heartbeat.txt` と `logs/last_result.json` の更新時刻はまだ前回サイクル時刻のままなので、次回定時実行後に AI判定復帰可否を確認する。

- 日時: 2026-03-10 07:38 JST
- 実施内容: ChatGPT API の実接続テストを実施し、`.venv312` から `gpt-4o-mini` へ正常応答 `OK` を確認した。これにより API キー不正や接続不能ではないことを確認できたため、AI判定エラーの主因を `.env` の `AI_TIMEOUT_SEC=1` / `AI_RETRY_COUNT=1` と判断し、`AI_TIMEOUT_SEC=5`、`AI_RETRY_COUNT=3` に戻した。
- 変更ファイル: `.env`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 設定変更後の常駐サイクルで `ai_error` が解消するかは次回実行結果の確認が必要。
- メモ: ChatGPT API 実接続テストはユーザー許可のうえで実施。最小限の疎通確認のみで、本番ロジック全体の実行までは行っていない。

- 日時: 2026-03-10 07:20 JST
- 実施内容: AI判定エラーを調査した。`logs/last_result.json` では 2026-03-10 05:05 JST 時点の `ai_advice=null` と `reason_for_notification=["confidence_jump","ai_error"]` を確認。設定も点検し、`.env` の `AI_TIMEOUT_SEC=1`・`AI_RETRY_COUNT=1` が原因候補として強いと判断した。あわせて、AI例外が握りつぶされて詳細不明になる問題を改善し、`src/ai/advice.py` と `src/ai/summary.py` に失敗理由を `logs/errors/` へ保存するログ出力を追加した。
- 変更ファイル: `src/ai/advice.py`, `src/ai/summary.py`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`
- 未解決事項: 実際の OpenAI 応答失敗理由は、次回サイクル実行後に新設ログを確認するまで確定しない。設定上はタイムアウト1秒が最有力。
- メモ: APIキー自体は設定済み。常駐実行は `.venv312/bin/python` を使っており、そこで `openai 2.26.0` は導入済み。今回こちらから ChatGPT API 実行テストはしていない。

- 日時: 2026-03-10 00:20 JST
- 実施内容: 通知設定を「気づき重視」に調整した。`CONFIDENCE_LONG_MIN=60`、`CONFIDENCE_SHORT_MIN=65`、`CONFIDENCE_ALERT_CHANGE=7`、`ALERT_COOLDOWN_MINUTES=30` に変更し、通知が少し早めに来るようにした。あわせて記録ファイルを整理し、この案件で今必要な情報だけ残す形へ簡素化した。`launchd` 再起動後、常駐プロセスが新しい PID で動作していることも確認した。さらに、状態確認・ログ確認・再起動・停止・自動起動確認をまとめた運用メモを新規作成し、資料類を `運用資料/` に集約した。
- 変更ファイル: `.env`, `運用資料/progress.md`, `運用資料/NEXT_TASK.md`, `運用資料/運用コマンドメモ.md`, `運用資料/README.md`, `運用資料/ログ検証と改善運用ガイド.md`
- 未解決事項: 変更後の実際の通知頻度はまだ未確認。次回以降の `last_notified.json` と通知メールの増え方を見て微調整が必要な可能性がある。
- メモ: この通知は「売買サイン」ではなく「考えるきっかけ」を目的にした軽め設定。通知が増えすぎる場合は、まず `CONFIDENCE_ALERT_CHANGE` を 7 から 8 か 9 へ戻すと調整しやすい。
