#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ ! -d "${REPO_ROOT}/.git" ]]; then
  echo "error: repository root not found at ${REPO_ROOT}" >&2
  exit 1
fi

cd "${REPO_ROOT}"

PYTHON_BIN="${PYTHON_BIN:-./.venv312/bin/python}"
REPORT_DATE="$(date +%Y%m%d)"
LABEL="BTCFX Ver03-v2"
REPORT_DIR="運用資料/reports/analysis"
OUTCOME_CSV="logs/csv/active_plan_candidate_intraperiod_outcomes.csv"
PAPER_CANDIDATES_CSV="logs/csv/active_plan_paper_candidates.csv"
OHLCV_CSV="logs/csv/active_plan_intraperiod_ohlcv.csv"
OUTCOME_REPORT_PATH="${REPORT_DIR}/active_plan_candidate_intraperiod_outcomes_${REPORT_DATE}.md"
REPORT_HUB_PATH="運用資料/reports/report_hub_latest.md"

echo "${LABEL} temporary execution entrypoint"
echo "repo: ${REPO_ROOT}"
echo "python: ${PYTHON_BIN}"

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

echo "building report hub: ${REPORT_HUB_PATH}"
"${PYTHON_BIN}" tools/log_feedback.py build-report-hub

echo "done: ${LABEL}"
