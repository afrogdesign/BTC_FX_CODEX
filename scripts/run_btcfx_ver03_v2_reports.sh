#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ ! -d "${REPO_ROOT}/.git" ]]; then
  echo "error: repository root not found at ${REPO_ROOT}" >&2
  exit 1
fi

cd "${REPO_ROOT}"

PRELIGHT_ONLY=0
for arg in "$@"; do
  case "${arg}" in
    --preflight-only)
      PRELIGHT_ONLY=1
      ;;
    *)
      echo "error: unknown argument: ${arg}" >&2
      exit 1
      ;;
  esac
done

PYTHON_BIN="${PYTHON_BIN:-./.venv312/bin/python}"
REPORT_DATE="$(date +%Y%m%d)"
LABEL="BTCFX Ver03-v2"
REPORT_DIR="運用資料/reports/analysis"
OUTCOME_CSV="logs/csv/active_plan_candidate_intraperiod_outcomes.csv"
PAPER_CANDIDATES_CSV="logs/csv/active_plan_paper_candidates.csv"
OHLCV_CSV="logs/csv/active_plan_intraperiod_ohlcv.csv"
OUTCOME_REPORT_PATH="${REPORT_DIR}/active_plan_candidate_intraperiod_outcomes_${REPORT_DATE}.md"
REPORT_HUB_REL_PATH="運用資料/reports/report_hub_latest.md"
REPORT_HUB_ABS_PATH="${REPO_ROOT}/${REPORT_HUB_REL_PATH}"

preflight_status="pass"
candidate_csv_state="missing"
ohlcv_csv_state="missing"

preflight_warn() {
  local message="$1"
  echo "warning: ${message}"
  if [[ "${preflight_status}" == "pass" ]]; then
    preflight_status="warn"
  fi
}

preflight_fail() {
  local message="$1"
  echo "error: ${message}" >&2
  preflight_status="fail"
}

ensure_writable_parent() {
  local parent_dir="$1"
  if ! mkdir -p "${parent_dir}"; then
    preflight_fail "cannot create parent directory: ${parent_dir}"
    return 1
  fi
  if [[ ! -d "${parent_dir}" ]]; then
    preflight_fail "parent directory is missing after creation attempt: ${parent_dir}"
    return 1
  fi
  if [[ ! -w "${parent_dir}" ]]; then
    preflight_fail "parent directory is not writable: ${parent_dir}"
    return 1
  fi
}

run_preflight() {
  echo "${LABEL} preflight"
  echo "repo: ${REPO_ROOT}"
  echo "python: ${PYTHON_BIN}"

  if [[ "$(pwd -P)" != "${REPO_ROOT}" ]]; then
    preflight_fail "script is not running from the repository root"
    return 1
  fi
  if [[ ! -d ".git" ]]; then
    preflight_fail ".git not found at repository root"
    return 1
  fi
  if [[ -z "${PYTHON_BIN}" ]]; then
    preflight_fail "PYTHON_BIN is empty"
    return 1
  fi
  if [[ ! -x "${PYTHON_BIN}" ]]; then
    preflight_fail "PYTHON_BIN is not executable: ${PYTHON_BIN}"
    return 1
  fi
  if [[ ! -f "tools/log_feedback.py" ]]; then
    preflight_fail "tools/log_feedback.py is missing"
    return 1
  fi

  ensure_writable_parent "logs/csv" || return 1
  ensure_writable_parent "運用資料/reports/analysis" || return 1
  ensure_writable_parent "運用資料/reports" || return 1

  if [[ -f "${PAPER_CANDIDATES_CSV}" ]]; then
    candidate_csv_state="present"
    echo "candidate_csv: present (${PAPER_CANDIDATES_CSV})"
  else
    preflight_warn "candidate_csv missing: ${PAPER_CANDIDATES_CSV}; report can still emit a missing/empty notice"
  fi

  if [[ -f "${OHLCV_CSV}" ]]; then
    ohlcv_csv_state="present"
    echo "ohlcv_csv: present (${OHLCV_CSV})"
  else
    preflight_warn "ohlcv_csv missing: ${OHLCV_CSV}; no_ohlcv behavior will be used"
  fi

  echo "label: ${LABEL}"
  echo "preflight_status: ${preflight_status}"
  echo "candidate_csv: ${candidate_csv_state}"
  echo "ohlcv_csv: ${ohlcv_csv_state}"
  echo "report_hub_path: ${REPORT_HUB_REL_PATH}"
  echo "report_hub_cli_path: ${REPORT_HUB_ABS_PATH}"
  echo "intended_output: ${OUTCOME_CSV}"
  echo "intended_output: ${OUTCOME_REPORT_PATH}"
  echo "intended_output: ${REPORT_HUB_REL_PATH}"
}

echo "${LABEL} temporary execution entrypoint"
echo "repo: ${REPO_ROOT}"
echo "python: ${PYTHON_BIN}"

run_preflight
if [[ "${preflight_status}" == "fail" ]]; then
  exit 1
fi

if [[ "${PRELIGHT_ONLY}" -eq 1 ]]; then
  echo "preflight-only: no report or CSV generation"
  exit 0
fi

if [[ -f "${PAPER_CANDIDATES_CSV}" ]]; then
  echo "building intraperiod outcomes from ${PAPER_CANDIDATES_CSV}"
  if [[ -f "${OHLCV_CSV}" ]]; then
    echo "using OHLCV path: ${OHLCV_CSV}"
    "${PYTHON_BIN}" tools/log_feedback.py build-active-plan-candidate-intraperiod-outcomes \
      --candidates-path "${PAPER_CANDIDATES_CSV}" \
      --ohlcv-path "${OHLCV_CSV}"
  else
    echo "OHLCV file missing, continuing with no_ohlcv behavior"
    "${PYTHON_BIN}" tools/log_feedback.py build-active-plan-candidate-intraperiod-outcomes \
      --candidates-path "${PAPER_CANDIDATES_CSV}"
  fi
else
  echo "skip: missing candidate CSV ${PAPER_CANDIDATES_CSV}"
fi

echo "building outcome report: ${OUTCOME_REPORT_PATH}"
"${PYTHON_BIN}" tools/log_feedback.py build-active-plan-candidate-intraperiod-outcomes-report \
  --intraperiod-outcomes-path "${OUTCOME_CSV}" \
  --output-md "${OUTCOME_REPORT_PATH}"

echo "building report hub: ${REPORT_HUB_REL_PATH}"
echo "report hub absolute path: ${REPORT_HUB_ABS_PATH}"
"${PYTHON_BIN}" tools/log_feedback.py build-report-hub \
  --output-md "${REPORT_HUB_ABS_PATH}"

echo "done: ${LABEL}"
