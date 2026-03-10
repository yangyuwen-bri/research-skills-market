#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_DIR="$BASE_DIR/reports"

python3 "$BASE_DIR/scripts/run_daily_skill_experience.py" \
  --config "$BASE_DIR/config/skill_cases.json" \
  --limit 10 \
  --out "$REPORT_DIR" \
  --include-json

