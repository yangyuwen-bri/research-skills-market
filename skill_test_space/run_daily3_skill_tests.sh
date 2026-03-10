#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="$BASE_DIR/reports"
TODAY="$(date +%F)"
REPORT="$REPORT_DIR/$TODAY.md"
TIMEOUT_SECONDS=60
PASSED=0
FAILED=0
TIMEOUT_BIN=""
if command -v timeout >/dev/null 2>&1; then
  TIMEOUT_BIN="timeout $TIMEOUT_SECONDS"
fi

mkdir -p "$REPORT_DIR"

clean_ansi() {
  perl -pe 's/\e\[[0-9;]*[A-Za-z]//g'
}

run_block() {
  local title="$1"
  local cmd="$2"
  local status=0
  local pass="FAIL"
  local out_file
  out_file="$(mktemp)"

  {
    echo "## $title"
    echo "Command: $cmd"
    echo '```'
    if [ -n "$TIMEOUT_BIN" ]; then
      if $TIMEOUT_BIN bash -lc "$cmd" >"$out_file" 2>&1; then
        status=0
      else
        status=$?
      fi
    elif bash -lc "$cmd" >"$out_file" 2>&1; then
      status=0
    else
      status=$?
    fi
    if [ "$status" -eq 0 ]; then
      pass="PASS"
    fi
    clean_ansi <"$out_file"
    rm -f "$out_file"
    echo "exit_code:$status"
    echo "result:$pass"
    echo '```'
    echo
  } >> "$REPORT"

  if [ "$pass" = "PASS" ]; then
    PASSED=$((PASSED + 1))
  else
    FAILED=$((FAILED + 1))
  fi
}

cat > "$REPORT" <<EOF
# Daily Skill Test Report
Date: $(date "+%Y-%m-%d %H:%M:%S")
---

EOF

run_block "1) find-skills (Skills CLI query)" "npx --yes skills find \"testing\" | head -n 12"
run_block "1) find-skills (installed list)" "npx --yes skills list -g | sed -n '1,12p'"
run_block "2) weather (wttr.in)" "curl -m 8 -s 'https://wttr.in/London?format=3'"
run_block "2) weather (open-meteo json)" "curl -m 8 -s 'https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.12&current_weather=true' | head -c 240"
run_block "3) polymarket (trending)" "python3 $BASE_DIR/polymarketodds/scripts/polymarket.py trending | head -n 40"
run_block "3) polymarket (calendar)" "python3 $BASE_DIR/polymarketodds/scripts/polymarket.py calendar --days 3"

cat >> "$REPORT" <<EOF
## Summary
- Passed: $PASSED
- Failed: $FAILED

EOF

echo "Report saved: $REPORT"
