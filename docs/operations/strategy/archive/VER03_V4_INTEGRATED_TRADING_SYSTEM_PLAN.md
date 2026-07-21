# Ver03-v4 BTC取引システム統合計画

## メタデータ

- repo: `afrogdesign/BTC_FX_CODEX`
- branch: `Ver03-v4`
- reviewed_baseline: `7aceb7a449d30289746ffac1db85a26513d5f702`
- status: authoritative strategy until superseded by a newer reviewed roadmap
- safety: report-only / not FORMAL_GO / no automatic order / human decides manually

## 目的

1. 勝てる実用レベルの BTC 取引支援システムを作る。
2. 現在の主運用は通知メールから公開HTMLレポートを開いて手動取引判断する流れなので、この HTML 通知レポートを継続的に改善する。
3. 将来的に自動取引へ進むため、ローカル dashboard / app surface / ready gate も同時に育てる。
4. メール、公開 HTML、ローカル dashboard は別判断を出さず、同じ判断ソースから違う表示を出す。

## 3 つの面

### A. Public HTML notification report

- 現在の実務上の main manual-trading UI。
- `src/notification/detail_page.py` が生成する。
- いまのデザインとプレゼンテーションは好評なので、明示的な要望がない限り視覚言語を維持する。
- manual-trading support の最優先 surface として扱う。
- entry / TP / SL / invalidation / wait / timeout / ready / safety の理解を速くする表示を最優先する。

### B. Notification mail

- triage / entry point。
- `src/ai/summary.py` と `src/presentation/sanitize.py` が生成する。
- subject version は active product branch に従い、現在は `[BTCFX Ver03-v4]`。
- mail は public HTML report と local app surface への導線を載せてよい。
- send / SMTP / Gmail の挙動は明示許可があるまで触らない。

### C. Local dashboard / app surface

- local confirmation, ready gate, manifest, snapshot, 将来の approval / automation 基盤。
- 現在の成果物は `local/manual_delivery_app_surface/` 配下。
- 現在の起動補助は `scripts/refresh_current_manual_delivery_app_surface.command`。
- local dashboard は public HTML report の有用な情報設計に収束させる。別物の UI にしない。

## Single-source doctrine

- 共有する source concepts:
  - `result_payload`
  - `build_display_context`
  - `build_notification_context`
  - `active_trade_plan`
  - `app-ready`
  - `app-snapshot`
  - `app-surface-manifest`
  - ready gate
- mail / public HTML / local dashboard で別々の trading logic を作らない。
- manual-trading signal や safety field が変わるなら、3 つの surface すべてへの影響を同時に評価する。
- 3 つの surface は同じ意思決定の別表示であり、別判断系ではない。

## Phased roadmap

### Phase 0: 現在の手動運用を安定化する

- email -> public HTML report を current main workflow として維持する。
- subject prefix は `[BTCFX Ver03-v4]` を維持する。
- mail と public HTML に ready-gate / local surface 参照を持たせる。
- report-only / not FORMAL_GO / no automatic order / human decides manually を崩さない。

### Phase 1: Public HTML report を manual trade quality 向けに改善する

- 現在のデザインを維持する。
- actionability, entry mode, TP / SL, invalidation, wait / timeout, ready / safety summaries をより明確にする。
- 注文発行や追加通知は増やさない。

### Phase 2: Local dashboard を public HTML report に揃える

- コアの判断セクションを合わせる。
- static / local / report-only に留める。
- 同じ ready gate と manifest を使う。
- public HTML の useful information architecture を local dashboard に反映する。

### Phase 3: Evidence と win-rate の改善

- intraperiod verification を使う。
- entry reached / TP / SL sequence / timeout / MFE / MAE を観測する。
- false positives, missed opportunities, bad entry timing を診断する。
- findings を Active Plan と report wording 改善に反映する。

### Phase 4: Semi-automatic approval path

- 最初は human review only。
- private / order endpoints は作らない。
- explicit approval / copy support は safety design の後に限定する。

### Phase 5: Automatic trading readiness

- proven metrics, stable gates, explicit human approval が揃ってから考える。
- `FORMAL_GO` と `ACTIVE_*` は分ける。
- separate safety design without approval の auto order はしない。

## Development rules

- 取引品質の改善は public HTML / notification mail / local dashboard を一緒に考える。
- email subject / report version を変えるなら branch / version prefix も更新する。
- public HTML report の見た目と情報設計を優先基準にする。
- local dashboard は public HTML report の代替ではない。
- mail は全分析面ではなく、public HTML と local surface への入口にする。
- Active Plan candidates を `paper_positions.csv` に混ぜない。明示許可があるときだけ。
- auto-order, private/account/order endpoint, runtime restart, send/notify behavior は明示許可があるまで追加しない。
- report-only / not FORMAL_GO / no automatic order / human decides manually を全 surface で共有する。

## Immediate next-task sequence

1. もしまだ未完了なら launcher operator summary を終える。
2. Ver03-v4 の public HTML notification report を改善し、ready-gate / local surface / manual-safety context を追加する。
3. public HTML report content のテストを追加する。
4. notification mail の subject/body を Ver03-v4 と public HTML に揃える。
5. dashboard parity を public HTML section に合わせて進める。
6. その後に intraperiod / win-rate diagnostics に戻る。

## Acceptance criteria

- 次の task が aligned と言えるのは、少なくとも次のいずれかを改善または維持する場合だけ:
  - public HTML manual-trading clarity
  - notification mail triage usefulness
  - local dashboard readiness
  - evidence-based trading accuracy
  - safety-gated automation readiness
- 次の task が misaligned なのは、次のいずれかを起こす場合:
  - 別の decision path を作る
  - safety boundary を隠す
  - send / SMTP / Gmail behavior を無断で変える
  - formal safety design なしに automatic trading を始める

## 参照する surface / command

- Public HTML report: `src/notification/detail_page.py`
- Notification mail: `src/ai/summary.py`, `src/presentation/sanitize.py`
- Local dashboard / app surface: `local/manual_delivery_app_surface/`
- Launcher: `scripts/refresh_current_manual_delivery_app_surface.command`
- Ready gate: `refresh-and-check-current-manual-delivery-app-surface --stdout-json`
- Read-side check: `check-current-manual-delivery-app-ready --stdout-json`
- Contract introspection: `describe-current-manual-delivery-app-contract --stdout-json`
- Surface validator: `check-current-manual-delivery-app-surface --stdout-json`
- Surface ready gate: `refresh-and-check-current-manual-delivery-app-surface --stdout-json`

## 運用メモ

- public HTML report が今の manual-trading main UI。
- notification mail は入口。
- local dashboard / app surface は confirmation と future automation の土台。
- 3 surface は report-only / human-decided を守りながら、同じ判断ソースから出力する。
