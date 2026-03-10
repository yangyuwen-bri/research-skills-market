#!/usr/bin/env python3
"""Weather probe for regression tests.

This helper avoids brittle assertions by accepting wttr.in primary response or
open-meteo fallback response and emits concise normalized markers for checks.
"""

import json
import subprocess
import sys


def run_cmd(cmd: str) -> str:
    proc = subprocess.run(
        ["bash", "-lc", cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return proc.stdout.strip(), proc.returncode


def format_open_meteo(raw: str) -> bool:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return False
    current = data.get("current_weather", {})
    if not isinstance(current, dict):
        return False
    temp = current.get("temperature")
    wind = current.get("windspeed")
    if temp is None or wind is None:
        return False
    print(f"open_meteo_fallback_ok temperature={temp} wind={wind}")
    return True


def main() -> int:
    # Primary path (wttr.in).
    primary, code = run_cmd("curl -s --max-time 12 'https://wttr.in/London?format=3'")
    if code == 0 and primary:
        print(f"wttr_primary_ok {primary}")
        return 0

    print("wttr_primary_fail fallback_to_open_meteo")

    # Fallback path (open-meteo).
    fallback, code = run_cmd(
        "curl -s --max-time 12 'https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.12&current_weather=true'"
    )
    if code != 0 or not fallback:
        print("open_meteo_fallback_fail")
        return 1

    if format_open_meteo(fallback):
        return 0

    print("open_meteo_payload_invalid")
    return 1


if __name__ == "__main__":
    sys.exit(main())
