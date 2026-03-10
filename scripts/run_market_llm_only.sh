#!/usr/bin/env bash
set -euo pipefail

: "${OPENAI_API_KEY:?请先设置 OPENAI_API_KEY}"
: "${LLM_API_URL:=https://api.openai.com/v1/chat/completions}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

python3 "${PROJECT_ROOT}/scripts/collect_market_multi_agents.py" \
  --enable-llm-classifier \
  --llm-only-classifier \
  --llm-api-url "${LLM_API_URL}" \
  --max-items "${RUN_MAX_ITEMS:-0}" \
  --classifier-workers "${RUN_CLASSIFIER_WORKERS:-1}" \
  --evaluator-workers "${RUN_EVALUATOR_WORKERS:-1}" \
  --tester-workers "${RUN_TESTER_WORKERS:-1}" \
  "$@"
