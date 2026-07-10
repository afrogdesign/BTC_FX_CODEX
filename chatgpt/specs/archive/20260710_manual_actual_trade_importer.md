# Manual Actual Trade Importer Hardening Active Spec

## Metadata

- work_id: `BTCFX-20260710-MTP-ACTUAL-TRADE-IMPORT-SPEC`
- created_at: `2026-07-10`
- status: archived / reviewed implementation baseline
- task_type: completed P2 importer hardening
- next implementation phase: P3 linkage and ground-truth pipeline, not greenfield implementation
- repo: `afrogdesign/BTC_FX_CODEX`
- working_repo: `/Users/marupro/CODEX/100_MCP_Server/btc_monitor`
- safety: report-only / not `FORMAL_GO` / no automatic order / human decides manually

---

## 1. Objective

既存のMEXC actual trade importerを、manual trading practicality routeで安全に使えるlocal normalization componentへhardeningする。

このspecは新規importerの設計ではない。repoにはすでに次が存在する。

```text
tools/log_feedback.py
  import_mexc_actual_trades()
  normalize_mexc_trade_history()
  normalize_mexc_order_history()
  normalize_mexc_position_history()

tests/test_mexc_actual_trade_importer.py
```

さらに、signal linkerとground-truth reportも既に存在する。

```text
link_manual_trades_to_signals()
build_manual_trade_ground_truth_report()
tests/test_manual_trade_signal_linker.py
tests/test_manual_trade_ground_truth_report.py
```

ただし、現在のimporterは次の契約を満たしていない。

- deterministic idempotency
- overlapping export merge
- corrected export conflict handling
- atomic output update
- required-column validation
- malformed row rejection report
- strict timezone normalization
- numeric normalization
- stable side / position semantics
- canonical private input path protection

P2では既存実装を捨てず、上記をhardeningする。

---

## 2. Current evidence and design correction

### 2.1 Existing implementation reality

現行CLIは次である。

```text
import-mexc-actual-trades
```

計画文書にある概念名は次である。

```text
import-manual-actual-trades
```

P2で`import-manual-actual-trades`をcanonical commandとして追加し、既存`import-mexc-actual-trades`は後方互換aliasとして維持する。

### 2.2 Existing behavior that must change

現行importerは、入力ごとに3つのCSVを全体上書きする。

現行IDはrow indexを含むため、同一データの並び替えやcorrected exportで不安定になり得る。

現行処理は、必須column欠落、重複、期間重複、corrected export、malformed valueを明確に区別しない。

P2ではmerge-first / conflict-safe / atomic-writeへ変更する。

### 2.3 Existing downstream compatibility

既存linker/reportが参照する次のfield名はP2で維持する。

```text
actual_trade_id
actual_order_id
actual_position_id
timestamp_jst
opened_at_jst
closed_at_jst
symbol
side
fee
fee_asset
realized_pnl
source_file
```

fieldの意味を変える場合は、このspecで定義した正規化へ統一し、matching testsを同じP2 taskで更新する。

---

## 3. Canonical input contract

### 3.1 Canonical local-only path

canonical raw input path:

```text
local/manual_trade_imports/YYYYMMDD/
```

Example:

```text
local/manual_trade_imports/20260715/
  MEXC Trade History 20260701-20260715.xlsx
  MEXC Order History 20260701-20260715.xlsx
  MEXC Position History 20260701-20260715.xlsx
```

Rules:

- `YYYYMMDD` is the user export/import batch date in JST.
- raw files remain local only.
- raw files are never committed.
- `.gitignore` must include `local/manual_trade_imports/` before any real export is placed there.
- `docs/mexc_csv/` is a historical path reference only and is not canonical.
- P1/P2 must not move, delete, inspect, or migrate real files from `docs/mexc_csv/`.
- the CLI may accept any explicit local `--input-dir`, but documentation and default examples use the canonical path only.
- there is no automatic fallback scan of `docs/mexc_csv/`.

### 3.2 Accepted file categories

A complete batch requires exactly one or more workbook files for each category.

| category | accepted filename match |
|---|---|
| trade history | case-insensitive basename containing `Trade History` and ending `.xlsx` |
| order history | case-insensitive basename containing `Order History` and ending `.xlsx` |
| position history | case-insensitive basename containing `Position History` and ending `.xlsx` |

Canonical aliases may also be accepted:

```text
futures_trade_history*.xlsx
futures_order_history*.xlsx
futures_position_history*.xlsx
```

A workbook matching multiple categories is rejected.

Unknown `.xlsx` files are not read. When all three required categories have valid `.xlsx` inputs, unrelated `.xls`, `.xlsm`, CSV, PDF, and unknown `.xlsx` files are warning-only entries in `unsupported_files`; their summary names are hashed safe names. If a required category has no valid `.xlsx`, the category remains missing and the import exits `2`.

### 3.3 Required workbooks

Default strict import requires all three categories.

```text
trade history
order history
position history
```

Missing category behavior:

- exit code `2`
- `ok=false`
- no output file mutation
- missing categories listed in stdout JSON

P2 does not add partial-import mode. A future explicit task may add it if operational evidence requires it.

### 3.4 Sheet selection

- preferred sheet name: `Sheet1`
- if `Sheet1` is absent and the workbook has exactly one visible worksheet, use that worksheet
- if multiple visible worksheets exist and `Sheet1` is absent, reject the workbook
- hidden worksheets are not imported
- macro-enabled `.xlsm`, legacy `.xls`, CSV, PDF, and unknown `.xlsx` files are never read and are warning-only when the complete valid batch exists
- a password-protected or malformed matched `.xlsx` is an input-contract error

### 3.5 Required source columns

#### Trade History

Required headers:

```text
UID
時間(UTC+09:00)
先物取引ペア
方向
注文の種類
約定価格
取引手数料
手数料支払い暗号資産
役割
決済損益
```

At least one quantity header is required:

```text
約定数量 (枚)
約定数量 (トークン)
約定数量 (金額)
```

#### Order History

Required headers:

```text
UID
時間(UTC+09:00)
先物取引ペア
方向
レバレッジ
注文の種類
約定数量
平均約定価格
決済損益
手数料
ステータス
```

#### Position History

Required headers:

```text
UID
取引ペア
オープン時間(UTC+09:00)
決済時刻
方向
実現損益
ステータス
```

Header presence is required even when individual values may be blank.

### 3.6 Unsupported format handling

Unsupported workbook, ambiguous sheet, missing header, empty sheet, unreadable zip/XML, or password protection is an input-contract error.

Default behavior is batch-atomic failure:

- collect all validation errors
- write no canonical CSV
- return exit code `2`
- return compact error codes only
- do not print raw row contents

---

## 4. Privacy and safety contract

Hard requirements:

- raw exchange exports are local only
- no raw export commit
- no exchange API
- no account/private/order endpoint
- no API key or secret read
- no `.env` access
- no raw UID in canonical outputs, stdout, logs, reports, tests, or exceptions
- no full local path in stdout JSON
- no `paper_positions.csv` integration
- tests use synthetic sanitized xlsx fixtures only
- no runtime restart
- no notification behavior change
- no gate, threshold, scoring, or trading logic change

UID policy:

```text
source_uid_hash = sha256("mexc:" + raw_uid)
```

- raw UID is required as a source identity input
- only the hash is retained
- an empty UID rejects the row

Source filename policy:

- store sanitized basename only
- never store parent directories
- if basename contains an email-like token or a digit sequence of 6 or more digits, replace it with:

```text
mexc_<category>_<source_file_sha256_prefix>.xlsx
```

---

## 5. Canonical outputs

Canonical generated outputs:

```text
logs/csv/manual_actual_trades.csv
logs/csv/manual_actual_orders.csv
logs/csv/manual_actual_positions.csv
```

Generated diagnostic output:

```text
logs/csv/manual_actual_trade_import_issues.csv
```

All files under `logs/` remain generated/local and are not committed by default.

### 5.1 Common metadata fields

Each canonical CSV includes:

| field | contract |
|---|---|
| `schema_version` | fixed value `manual_actual_trade.v2` |
| category ID | `actual_trade_id`, `actual_order_id`, or `actual_position_id` |
| `source_row_id` | exact-source identity from file hash + sheet + worksheet row number |
| `logical_key` | stable business identity used to detect corrected exports |
| `row_fingerprint` | hash of all normalized business values |
| `source_uid_hash` | one-way hash of source UID |
| `source_file` | sanitized basename |
| `source_file_sha256` | full file SHA-256 |
| `import_batch_id` | deterministic fingerprint of the complete input batch |
| `imported_at_utc` | importer execution time, ISO-8601 UTC |
| `import_status` | `inserted`, `duplicate_skipped`, or `corrected_replaced` in the current operation summary; stored rows normally use `active` |

`normalized_id` is not added as a duplicate generic column. The category-specific `actual_*_id` is the normalized identifier.

### 5.2 `manual_actual_trades.csv`

Responsibility: fill-level execution facts. One accepted row represents one normalized trade-history fill row.

Columns:

```text
schema_version
actual_trade_id
source_row_id
logical_key
row_fingerprint
source_uid_hash
source_file
source_file_sha256
import_batch_id
imported_at_utc
timestamp_utc
timestamp_jst
symbol
side
transaction_side
position_action
order_type
fill_qty_contract
fill_qty_token
fill_qty_value
fill_price
fee
fee_asset
role
realized_pnl
status
import_status
```

### 5.3 `manual_actual_orders.csv`

Responsibility: order-level state and aggregate fill facts. It must not duplicate fill rows as trade records.

Columns:

```text
schema_version
actual_order_id
source_row_id
logical_key
row_fingerprint
source_uid_hash
source_file
source_file_sha256
import_batch_id
imported_at_utc
timestamp_utc
timestamp_jst
symbol
side
transaction_side
position_action
leverage
order_type
filled_qty
avg_fill_price
realized_pnl
fee
fee_asset
status
source_status
import_status
```

### 5.4 `manual_actual_positions.csv`

Responsibility: position lifecycle facts. It does not aggregate or infer individual fills.

Columns:

```text
schema_version
actual_position_id
source_row_id
logical_key
row_fingerprint
source_uid_hash
source_file
source_file_sha256
import_batch_id
imported_at_utc
opened_at_utc
opened_at_jst
closed_at_utc
closed_at_jst
symbol
side
realized_pnl
status
source_status
import_status
```

### 5.5 Import issues CSV

Columns:

```text
import_batch_id
category
source_file
sheet_name
source_row_number
issue_type
reason_code
field_name
logical_key
existing_normalized_id
incoming_row_fingerprint
```

Rules:

- `issue_type`: `rejected` or `conflict`
- do not include raw UID
- do not include raw cell value
- do not include full local path
- issues file is written only when the canonical batch operation succeeds with non-fatal row rejections, or when explicitly requested by dry-run output planning
- batch-level fatal errors are returned in stdout JSON and do not mutate outputs

---

## 6. Normalization rules

### 6.1 Timezone

Source timezone is fixed to UTC+09:00 / `Asia/Tokyo`.

Accepted source examples:

```text
2026-07-01 09:15:00
2026/07/01 09:15:00
2026-07-01T09:15:00+09:00
```

Output:

```text
JST: 2026-07-01T09:15:00+09:00
UTC: 2026-07-01T00:15:00Z
```

Rules:

- timezone-naive source timestamps are interpreted as JST only
- source timestamps with a conflicting explicit offset are rejected
- malformed or impossible dates reject the row
- open positions may have blank close time
- closed positions require a valid close time

### 6.2 Numeric parsing

- use decimal semantics, not binary float, for normalization and fingerprints
- trim surrounding whitespace
- remove comma thousands separators
- normalize full-width signs and digits when deterministic
- output plain decimal strings without exponent notation
- do not silently convert malformed values to zero

Required numeric values reject the row when malformed.

Optional numeric values become blank only when the source cell is blank.

### 6.3 Symbol mapping

Accepted BTC aliases:

```text
BTC_USDT
BTC-USDT
BTC/USDT
BTCUSDT
```

Canonical output:

```text
BTCUSDT
```

Other symbols are rejected with `unsupported_symbol`.

No cross-symbol import is added in P2.

### 6.4 Direction mapping

Canonical `side` is position orientation:

```text
long
short
unknown
```

Canonical `transaction_side`:

```text
buy
sell
unknown
```

Canonical `position_action`:

```text
open
close
reduce
unknown
```

Mapping examples:

| source direction | side | transaction_side | position_action |
|---|---|---|---|
| `LONG`, `ロング` | long | unknown | unknown |
| `SHORT`, `ショート` | short | unknown | unknown |
| `BUY`, `買い` | unknown | buy | unknown |
| `SELL`, `売り` | unknown | sell | unknown |
| `Open Long`, `ロングを開く` | long | buy | open |
| `Close Long`, `ロングを決済` | long | sell | close |
| `Open Short`, `ショートを開く` | short | sell | open |
| `Close Short`, `ショートを決済` | short | buy | close |

Unknown non-empty direction values reject the row instead of guessing.

### 6.5 Fee

- canonical fee is a non-negative cost
- source `-1.25` and `1.25` both normalize to `1.25`
- blank fee remains blank when the workbook contract allows blank values
- malformed non-blank fee rejects the row
- fee currency is normalized to uppercase
- missing fee currency is allowed only when fee is blank

### 6.6 Realized PnL

- preserve the source economic sign
- positive remains positive
- negative remains negative
- blank is allowed for open/unrealized rows
- malformed non-blank PnL rejects the row
- importer does not infer net PnL or subtract fee from realized PnL

### 6.7 Status

Canonical order status:

```text
filled
partially_filled
canceled
open
unknown
```

Canonical position status:

```text
open
closed
unknown
```

The original normalized text is retained in `source_status` for orders and positions.

### 6.8 Partial fill and partial close

- trade history remains fill-level; do not aggregate fills
- order history may contain `partially_filled`
- `filled_qty` is the executed quantity, not requested quantity
- partial close is represented by trade/order rows with `position_action=reduce` or `close` when source direction makes this explicit
- importer does not reconstruct remaining position size
- position aggregation belongs to later analysis, not P2

### 6.9 Open and closed position consistency

- blank close time + open status is valid
- valid close time + closed status is valid
- close time earlier than open time rejects the row
- closed status with blank close time rejects the row
- open status with non-blank close time is a row conflict and rejects the row

---

## 7. Identity, idempotency, and conflict policy

### 7.1 Source file fingerprint

```text
source_file_sha256 = sha256(raw workbook bytes)
```

### 7.2 Import batch fingerprint

```text
import_batch_id = "batch_" + sha256(
  sorted(category + ":" + source_file_sha256 for every accepted workbook)
)[:24]
```

The batch fingerprint is independent of file path and file ordering.

### 7.3 Source row identity

```text
source_row_id = sha256(
  source_file_sha256 + sheet_name + one_based_worksheet_row_number
)
```

This identifies the exact physical source row.

### 7.4 Logical key

The logical key detects the same business event across overlapping or corrected exports.

Trade logical key inputs:

```text
category
source_uid_hash
timestamp_utc
symbol
side
transaction_side
position_action
order_type
fill_qty_contract
fill_qty_token
fill_qty_value
fill_price
```

Order logical key inputs:

```text
category
source_uid_hash
timestamp_utc
symbol
side
transaction_side
position_action
order_type
filled_qty
avg_fill_price
```

Position logical key inputs:

```text
category
source_uid_hash
opened_at_utc
symbol
side
```

### 7.5 Row fingerprint

`row_fingerprint` hashes all normalized business values, including fee, realized PnL, close time, and status, but excluding source filename, source file hash, batch ID, and import time.

Category ID:

```text
actual_trade_id    = "tra_" + row_fingerprint[:24]
actual_order_id    = "ord_" + row_fingerprint[:24]
actual_position_id = "pos_" + row_fingerprint[:24]
```

### 7.6 Same-file reimport

If the same file fingerprint and same rows are already present:

- no duplicate rows are added
- no canonical output is rewritten unless another new row exists in the batch
- summary increments `duplicate_rows_skipped`
- exit code is `0`

### 7.7 Overlapping export ranges

If a new batch overlaps an earlier export:

- identical logical key + identical row fingerprint: duplicate skipped
- new logical key: inserted
- same logical key + different row fingerprint: conflict

### 7.8 Corrected export

Default conflict policy:

```text
--conflict-policy reject
```

Behavior:

- collect conflicts
- exit code `3`
- do not mutate any canonical output
- return conflict count and safe reason codes

Explicit replacement policy:

```text
--conflict-policy replace
```

Behavior:

- replace the prior row sharing the logical key
- preserve deterministic category ID from the incoming row fingerprint
- report replaced row count
- write conflict audit rows to the issues CSV
- perform the three canonical output updates atomically

No silent last-write-wins behavior is allowed.

---

## 8. Merge and atomic write policy

Default policy is merge with existing canonical CSVs.

- existing rows are loaded and schema-validated
- new accepted rows are merged by logical key / row fingerprint
- prior unrelated rows remain intact
- canonical outputs are sorted deterministically by primary timestamp, category ID
- all changed files are written to temporary files first
- all validation and serialization must succeed before replacement
- replacement uses process-level transactional replacement with rollback: existing targets receive same-filesystem backups, targets are replaced in order, and a failure restores replaced targets or removes newly-created targets before re-raising
- when an issues CSV is written for the batch, it is included in the same replacement transaction
- this process-level rollback does not claim absolute crash or power-loss atomicity
- no header-only file is created after a failed or incomplete batch
- P2 does not add a destructive rebuild option

If an existing canonical CSV has an unsupported schema/header:

- exit code `4`
- no mutation
- report `existing_output_schema_mismatch`

---

## 9. CLI contract

Canonical command:

```bash
./.venv312/bin/python tools/log_feedback.py import-manual-actual-trades \
  --input-dir local/manual_trade_imports/20260715 \
  --output-dir logs/csv \
  --conflict-policy reject \
  --stdout-json
```

Backward-compatible alias:

```text
import-mexc-actual-trades
```

The alias invokes the same implementation and returns `cli_alias_used=true`.

### 9.1 Arguments

Required:

```text
--input-dir <path>
```

Optional:

```text
--output-dir <path>              default: logs/csv
--dry-run
--stdout-json
--conflict-policy reject|replace default: reject
```

No API-related arguments are permitted.

### 9.2 Dry run

`--dry-run`:

- reads and validates local sanitized/private input
- computes fingerprints, merge, duplicate, rejection, and conflict results
- writes no canonical CSV
- writes no issues CSV
- creates no output directory
- returns `would_write_outputs` and `would_write_issues_file` planning fields without creating files or directories
- `would_write_outputs` contains the three canonical filenames when inserts or replacements are planned; duplicate-only batches leave it empty
- rejected/conflict issues without canonical changes set `would_write_issues_file=true`; a complete no-op leaves both planning fields empty/false

### 9.3 Exit codes

| code | meaning |
|---:|---|
| `0` | success, including duplicate-only no-op |
| `1` | unexpected internal failure |
| `2` | input contract or row validation failure / no input / missing required category |
| `3` | corrected-export conflict under reject policy |
| `4` | existing output schema or output I/O failure |

### 9.4 No-input behavior

No matching required workbook:

- exit `2`
- `ok=false`
- `error=no_input_files`
- no output directory or file creation

### 9.5 stdout JSON

When `--stdout-json` is supplied, stdout contains exactly one compact JSON object plus a trailing newline.

Required keys:

```text
ok
schema_version
dry_run
cli_command
cli_alias_used
input_dir
output_dir
import_batch_id
source_file_count
category_file_counts
sheets_read
rows_read
rows_accepted
rows_rejected
duplicate_rows_skipped
conflicts_found
rows_inserted
rows_replaced
outputs_written
outputs_unchanged
issues_file
would_write_outputs
would_write_issues_file
symbols
date_range_utc
date_range_jst
missing_categories
unsupported_files
errors
safety_boundary
```

Privacy:

- input/output paths are repo-relative when inside the repo
- external paths are represented as basename only
- no UID
- no raw row
- no workbook content
- no full diff
- no traceback on stdout

---

## 10. Validation and tests

P2 must use synthetic minimal xlsx fixtures only.

Required tests:

1. normal complete import
2. canonical CLI command
3. legacy CLI alias
4. dry-run creates no output
5. no-input returns exit `2`
6. missing required workbook category returns exit `2` and no mutation
7. same file imported twice is a no-op
8. overlapping export range merges only new rows
9. corrected export under reject policy returns exit `3` and no mutation
10. corrected export under replace policy replaces deterministically
11. malformed date rejects batch/row according to contract
12. malformed numeric value is never converted to zero
13. comma-separated decimal parses correctly
14. missing required column rejects workbook
15. empty sheet rejects workbook
16. ambiguous multiple sheets reject workbook
17. complete valid batch with unrelated `.xls`, `.xlsm`, CSV, PDF, or unknown `.xlsx` records safe warning names; missing required `.xlsx` remains exit `2`; matched malformed/password-protected workbook is rejected
18. unsupported symbol is rejected
19. BTC symbol aliases normalize to `BTCUSDT`
20. side / transaction_side / position_action mapping
21. unknown non-empty direction is rejected
22. partial fill remains order/trade evidence without aggregation
23. partial close remains explicit without position-size inference
24. fee present normalizes to non-negative cost
25. fee blank remains blank
26. realized PnL sign is preserved
27. open position with blank close time
28. closed position with valid close time
29. inconsistent open/close status is rejected
30. source UID never appears in CSV/stdout/error
31. full local path never appears in stdout
32. source filename redaction
33. existing output schema mismatch returns exit `4`
34. atomic no-partial-write when one output serialization fails
35. downstream linker/report compatibility test remains passing

Targeted validation command for P2:

```bash
./.venv312/bin/python -m unittest \
  tests.test_mexc_actual_trade_importer \
  tests.test_manual_trade_signal_linker \
  tests.test_manual_trade_ground_truth_report
git diff --check
```

Do not run the full suite unless a shared helper change creates a broader regression risk.

---

## 11. Reporting contract

Import summary reports:

- workbook counts by category
- `sheets_read`: count of validated worksheets selected per category; failed workbook validation is not counted
- rows read
- accepted rows
- rejected rows
- duplicates skipped
- conflicts found
- inserted rows
- replaced rows
- outputs changed / unchanged
- imported UTC/JST date range
- symbols
- safety boundary

It does not report:

- raw UID
- account identifier
- raw rows
- private full paths
- workbook contents
- profitability claims

---

## 12. Responsibility boundary

P1/P2 importer is responsible only for:

- local workbook validation
- privacy-safe normalization
- deterministic identity
- merge/idempotency/conflict control
- generated local CSVs
- compact import reporting

P1/P2 importer does not perform:

- signal linking
- scenario linking
- notification matching
- performance claims
- A/B/C/STOP classification
- over-suppression classification
- avoided-loss or missed-opportunity inference
- production tuning
- runtime changes
- mail changes

Exchange export provides ground truth only for actual orders, fills, positions, fees, and realized PnL.

It cannot prove why the human entered, watched, skipped, exited, or took profit.

Those decisions require a separate scenario-linked human decision event record in a later phase.

---

## 13. Later-phase correction

Current repo already contains early linker and ground-truth report implementations. They are not treated as completed product phases merely because source exists.

After P2 importer hardening:

```text
P3 linker / ground-truth pipeline contract audit and hardening
→ P4 scenario identity, coverage, and human decision-event schema
→ P5 offline A/B/C/STOP classifier
→ P6 historical replay
→ P7 shadow surface
→ P8 human manual trial
→ P9 evidence-backed tuning review
```

P3 must verify that existing linker semantics are compatible with the hardened importer before any performance claim.

P4 must separate:

```text
exchange ground truth
human decision ground truth
market counterfactual evidence
```

---

## 14. Allowed implementation files for P2

Expected minimum scope:

```text
.gitignore
tools/log_feedback.py
tests/test_mexc_actual_trade_importer.py
```

A dedicated module is preferred because `tools/log_feedback.py` is already very large:

```text
src/feedback/__init__.py
src/feedback/manual_actual_trade_importer.py
```

Matching downstream tests may be updated only when required for importer schema compatibility:

```text
tests/test_manual_trade_signal_linker.py
tests/test_manual_trade_ground_truth_report.py
```

P2 must not modify:

```text
src/trade/execution_gate.py
src/trade/phase1b_lite.py
src/trade/opportunity_gate.py
notification trigger/sending code
runtime/launchd files
paper_positions.csv integration
```

---

## 15. Completion criteria

P1 is complete when:

- this active spec exists
- existing implementation reality is documented
- canonical input path is unique
- `.gitignore` protects the canonical raw path
- input/output schemas are unambiguous
- idempotency and conflict behavior are deterministic
- CLI and exit codes are fixed
- privacy boundaries are explicit
- test matrix is fixed
- importer / linker / scenario responsibilities are separated
- no raw export was read or committed
- no source importer change was made in P1

P2 is complete when:

- targeted tests pass
- same-file and overlap imports do not duplicate
- corrected exports never silently overwrite
- output mutation is atomic
- malformed input cannot silently become zero/blank accepted data
- no raw UID/private path leaks
- existing linker/report compatibility is preserved or deliberately migrated in the same bounded task
- no trading, notification, runtime, gate, or threshold behavior changes

---

## 16. Archive condition

Archive this spec only after:

1. P2 hardening implementation is committed.
2. targeted importer/linker/report tests pass.
3. ChatGPT reviews the diff and compact report.
4. no raw export/private data is present in the diff.
5. the next active spec is selected explicitly.

Archive destination:

```text
chatgpt/specs/archive/20260710_manual_actual_trade_importer.md
```
