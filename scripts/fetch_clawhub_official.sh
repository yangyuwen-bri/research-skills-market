#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: bash scripts/fetch_clawhub_official.sh [options]

Options:
  --sort <downloads|stars|rating|installs|installsAllTime|trending|newest>  Sort field for /api/v1/skills
  --limit <1-200>                                                            Page size (API hard cap is 200)
  --max-items <n>                                                            Stop after n records (0 means no limit)
  --max-pages <n>                                                            Stop after n pages (0 means no limit)
  --registry <url>                                                            API base URL (default: https://clawhub.ai)
  --mode <auto|cursor|offset|page>                                           Force pagination mode
  --out-jsonl <path>                                                         Output JSONL path
  --out-json <path>                                                           Output JSON array path
  --pause <seconds>                                                           Delay between requests to avoid throttling
  --timeout <seconds>                                                         Per-request timeout in seconds (default: 25)
  --retries <n>                                                              Retry attempts per request (default: 4)
  --source-feed <name>                                                        value written to source_feed
  --enrich [0|1]                                                             Enable per-skill enrichment from skill detail + SKILL.md (default: 0)
  --enrich-workers <n>                                                       Number of concurrent enrich workers (default: 6)
  --enrich-timeout <seconds>                                                  Per-request timeout for enrichment (default: 22)
  --enrich-retries <n>                                                       Retry attempts for enrichment requests (default: 3)
  --enrich-pause <seconds>                                                   Delay between enrichment requests (default: 0.1)
  --enrich-skip-download [0|1]                                               Skip download+ZIP extraction to speed up (default: 0)
  --enrich-max <n>                                                           Enrich only first N records after list collection (0 means all)
  --download-endpoint <url>                                                  Skill download API endpoint (default: https://wry-manatee-359.convex.site/api/v1/download?slug=)
  -h, --help                                                                 Show this help
USAGE
}

SORT="downloads"
LIMIT=200
MAX_ITEMS=0
MAX_PAGES=0
REGISTRY="https://clawhub.ai"
MODE="auto"
PAUSE=0.2
TIMEOUT=25
RETRIES=4
SOURCE_FEED="official-clawhub"
OUT_JSONL="data/raw/clawhub/clawhub_official_${SORT}_$(date +%Y%m%d_%H%M%S).jsonl"
OUT_JSON="${OUT_JSONL%.jsonl}.json"
ENRICH=0
ENRICH_WORKERS=6
ENRICH_TIMEOUT=22
ENRICH_RETRIES=3
ENRICH_PAUSE=0.1
ENRICH_MAX=0
ENRICH_SKIP_DOWNLOAD=0
DOWNLOAD_ENDPOINT="https://wry-manatee-359.convex.site/api/v1/download?slug="
ENRICH_SCRIPT="scripts/enrich_clawhub_official.py"
CONSECUTIVE_ERROR_LIMIT=3
FETCH_MODE_FALLBACKS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sort)
      SORT="$2"; shift 2 ;;
    --limit)
      LIMIT="$2"; shift 2 ;;
    --max-items)
      MAX_ITEMS="$2"; shift 2 ;;
    --max-pages)
      MAX_PAGES="$2"; shift 2 ;;
    --registry)
      REGISTRY="$2"; shift 2 ;;
    --mode)
      MODE="$2"; shift 2 ;;
    --out-jsonl)
      OUT_JSONL="$2"; OUT_JSON="${OUT_JSONL%.jsonl}.json"; shift 2 ;;
    --out-json)
      OUT_JSON="$2"; shift 2 ;;
    --pause)
      PAUSE="$2"; shift 2 ;;
    --timeout)
      TIMEOUT="$2"; shift 2 ;;
    --retries)
      RETRIES="$2"; shift 2 ;;
    --source-feed)
      SOURCE_FEED="$2"; shift 2 ;;
    --enrich)
      ENRICH="$2"; shift 2 ;;
    --enrich-workers)
      ENRICH_WORKERS="$2"; shift 2 ;;
    --enrich-timeout)
      ENRICH_TIMEOUT="$2"; shift 2 ;;
    --enrich-retries)
      ENRICH_RETRIES="$2"; shift 2 ;;
    --enrich-pause)
      ENRICH_PAUSE="$2"; shift 2 ;;
    --enrich-skip-download)
      ENRICH_SKIP_DOWNLOAD="$2"; shift 2 ;;
    --enrich-max)
      ENRICH_MAX="$2"; shift 2 ;;
    --download-endpoint)
      DOWNLOAD_ENDPOINT="$2"; shift 2 ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required." >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl is required." >&2
  exit 1
fi

if [[ "$ENRICH" == "1" ]] && ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is required when --enrich=1." >&2
  exit 1
fi

if [[ "$ENRICH" == "1" ]] && [[ ! -x "$ENRICH_SCRIPT" ]]; then
  echo "Error: enrichment script not executable: $ENRICH_SCRIPT" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT_JSONL")"

if (( LIMIT > 200 )); then
  echo "WARN: clawhub API/CLI pagination usually caps page size at 200; clamp limit to 200." >&2
  LIMIT=200
elif (( LIMIT < 1 )); then
  LIMIT=200
fi

normalize_response_items='(.items // .results // .data // .skills // [])'
extract_next_cursor='(.nextCursor // .next_cursor // .pagination.nextCursor // .pagination.next_cursor // .next // .nextPageCursor // empty)'
extract_has_more='(.hasMore // .has_more // .pagination.hasMore // .pagination.has_more // false)'
extract_page='(.pagination.page // .pagination.currentPage // .page // 1)'
extract_total_pages='(.pagination.totalPages // .pagination.total_pages // .totalPages // .total_pages // 0)'
extract_total_count='(.total // .count // .pagination.total // .pagination.totalCount // .pagination.totalItems // .pagination.total_items // 0)'
extract_next_page='(.pagination.nextPage // .nextPage // .next_page // empty)'
extract_page_signature='((.items // .results // .data // .skills // []) as $items | if ($items | type == "array") then (($items | map(.slug // .name // .url // .id // "" ) | .[0:12] | map(select(. != "")) | join("::")) ) else "" end)'

to_positive_int() {
  local value="$1"
  if [[ "$value" =~ ^[0-9]+$ ]]; then
    echo "$value"
  else
    echo 0
  fi
}

trim_number() {
  local value="$1"
  value="$(echo "$value" | tr -dc '0-9')"
  to_positive_int "$value"
}

fetch_page() {
  local mode="$1"
  local page="$2"
  local cursor="$3"
  local offset="$4"
  local url="$REGISTRY/api/v1/skills"
  local code=0
  local response
  local attempt=1
  local max_attempts
  local retry_wait=1
  local request_opts
  local started_at
  local elapsed

  max_attempts=$((RETRIES > 0 ? RETRIES : 1))
  request_opts=(--silent --show-error --location --request GET --get --compressed \
    --max-time "$TIMEOUT" --connect-timeout 8 --retry "$((RETRIES < 2 ? 1 : 2))" \
    --retry-delay 1 --retry-all-errors --retry-max-time "$((TIMEOUT * 3))")

  while (( attempt <= max_attempts )); do
    started_at=$(date +%s)
    case "$mode" in
      cursor)
        response="$(curl "${request_opts[@]}" \
          --data-urlencode "limit=$LIMIT" \
          --data-urlencode "sort=$SORT" \
          --data-urlencode "cursor=$cursor" "$url")" || code=$?
        ;;
      page)
        if (( page < 1 )); then
          page=1
        fi
        response="$(curl "${request_opts[@]}" \
          --data-urlencode "limit=$LIMIT" \
          --data-urlencode "sort=$SORT" \
          --data-urlencode "page=$page" "$url")" || code=$?
        ;;
      offset)
        response="$(curl "${request_opts[@]}" \
          --data-urlencode "limit=$LIMIT" \
          --data-urlencode "sort=$SORT" \
          --data-urlencode "offset=$offset" "$url")" || code=$?
        ;;
      *)
        response="$(curl "${request_opts[@]}" \
          --data-urlencode "limit=$LIMIT" \
          --data-urlencode "sort=$SORT" "$url")" || code=$?
        ;;
    esac

    elapsed=$(( $(date +%s) - started_at ))
    if (( code == 0 )); then
      if (( elapsed >= TIMEOUT - 2 )); then
        echo "WARN: slow API response (mode=$mode page=$page cursor=${cursor:0:12}... elapsed=${elapsed}s)." >&2
      fi
      break
    fi

    if (( attempt < max_attempts )); then
      echo "WARN: request failed (mode=$mode page=$page cursor=${cursor:0:12}... code=$code), retrying in ${retry_wait}s (attempt ${attempt}/${max_attempts})" >&2
      sleep "$retry_wait"
      retry_wait=$(( retry_wait * 2 ))
      attempt=$((attempt + 1))
      continue
    fi
    break
  done

  if (( code != 0 )); then
    echo "Failed request for mode=$mode page=$page cursor=$cursor offset=$offset (code=$code)" >&2
    return "$code"
  fi

  if ! jq -e . <<< "$response" >/dev/null 2>&1; then
    echo "Invalid JSON response for mode=$mode page=$page cursor=$cursor offset=$offset" >&2
    return 1
  fi

  echo "$response"
}

TOTAL=0
PAGE=1
offset=0
cursor=""
REQUESTS=0
ESTIMATED_TOTAL=""
current_mode="$MODE"
SEEN_SIGNATURE_FILE="$(mktemp)"
trap 'rm -f "$SEEN_SIGNATURE_FILE"' EXIT

: > "$OUT_JSONL"

  seen_same_signature=0
  last_cursor=""
  while true; do
    if ! response="$(fetch_page "$current_mode" "$PAGE" "$cursor" "$offset")"; then
      if (( FETCH_MODE_FALLBACKS >= CONSECUTIVE_ERROR_LIMIT )); then
        echo "WARN: repeated request failures ($FETCH_MODE_FALLBACKS). Stop collection to avoid endless loop. Saved partial result." >&2
        break
      fi

      if [[ "$current_mode" == "cursor" || "$current_mode" == "auto" || "$current_mode" == "offset" ]]; then
        echo "WARN: request failed, retrying in page mode (fallback #$((FETCH_MODE_FALLBACKS + 1)))." >&2
        current_mode="page"
        PAGE=1
        cursor=""
        offset=0
        FETCH_MODE_FALLBACKS=$((FETCH_MODE_FALLBACKS + 1))
        continue
      fi

      if [[ "$current_mode" == "page" ]]; then
        echo "WARN: request failed in page mode. Trying auto mode with increased timeout." >&2
        current_mode="auto"
        TIMEOUT=$((TIMEOUT + 15))
        FETCH_MODE_FALLBACKS=$((FETCH_MODE_FALLBACKS + 1))
        continue
      fi

      break
    fi

  count="$(trim_number "$(echo "$response" | jq -r "${normalize_response_items} | if type==\"array\" then length else 0 end")")"
  total_count_hint="$(trim_number "$(echo "$response" | jq -r "$extract_total_count")")"
  total_pages_hint="$(trim_number "$(echo "$response" | jq -r "$extract_total_pages")")"
  page_no_hint="$(to_positive_int "$(echo "$response" | jq -r "$extract_page")")"
  next_page_hint="$(echo "$response" | jq -r "$extract_next_page")"
  has_more="$(echo "$response" | jq -r "$extract_has_more")"
  next_cursor="$(echo "$response" | jq -r "$extract_next_cursor")"
  page_signature="$(echo "$response" | jq -r "$extract_page_signature")"

    if [[ -n "$page_signature" ]] && grep -Fxq "$page_signature" "$SEEN_SIGNATURE_FILE" 2>/dev/null; then
      echo "Duplicate page detected. API may not support requested pagination mode; stop to avoid loops." >&2
      if [[ "$count" -eq "$LIMIT" ]]; then
        echo "WARN: duplicate signature but full page size; attempting fallback mode page=${PAGE}." >&2
        if [[ "$current_mode" != "page" ]]; then
          current_mode="page"
          PAGE=$((PAGE + 1))
          cursor=""
          offset=0
          seen_same_signature=0
          continue
        fi
      fi
      break
    fi
    if [[ -n "$page_signature" ]]; then
      printf '%s\n' "$page_signature" >> "$SEEN_SIGNATURE_FILE"
    fi

    if [[ "$current_mode" == "cursor" && -n "$next_cursor" && "$next_cursor" == "$cursor" ]]; then
      seen_same_signature=1
    else
      seen_same_signature=0
    fi
    if (( seen_same_signature == 1 )); then
      if (( PAGE >= 2 )); then
        echo "WARN: cursor not advanced; fallback to page mode from page=$PAGE." >&2
        current_mode="page"
        PAGE=$((PAGE + 1))
        cursor=""
        continue
      fi
    fi

    if [[ "$count" == "0" ]]; then
      break
    fi

    if [[ "$current_mode" == "page" && "$last_cursor" == "$next_cursor" && -n "$last_cursor" ]]; then
      echo "WARN: next cursor equals last cursor in page mode; stopping to avoid loop." >&2
      break
    fi
    last_cursor="$cursor"

DOWNLOAD_ENDPOINT_DEFAULT="${DOWNLOAD_ENDPOINT:-$REGISTRY/api/v1/download?slug=}"
echo "$response" \
    | jq -c --arg sf "$SOURCE_FEED" --arg reg "$REGISTRY" --arg dz "$DOWNLOAD_ENDPOINT_DEFAULT" '
      (.items // .results // .data // .skills // []) as $items
      | if ($items | type == "array") then $items else [] end
      | .[]
      | {
          name: (.displayName // .name // .slug // .title // ""),
          url: (.url // (if .slug then ($reg + "/skills/" + .slug) else "" end)),
          desc: (.summary // .description // .about // ""),
          repository_url: (.repositoryUrl // .repository_url // .repository // .sourceCodeUrl // .source_code_url // .github // .github_url // ""),
          source_code_url: (.sourceCodeUrl // .source_code_url // ""),
          git_repo: (.gitRepo // .repo // ""),
          files_count: (.filesCount // .files_count // 0),
          install_hint: (.installHint // .install_command // .installCommand // .install // ""),
          stars: (.stats.stars // .stars // 0),
          forks: (.stats.forks // .forks // 0),
          source_feed: $sf,
          source_file: "clawhub-official",
          source_slug: (.slug // ""),
          source: "clawhub-official-list",
          source_url: (.url // (if .slug then ($reg + "/skills/" + .slug) else "" end)),
          download_zip: ($dz + (.slug // "")),
          version: (.latestVersion // .version // .stats.version // ""),
          updated_at: (.updatedAt // .updated_at // .updated // ""),
          downloads: (.stats.downloads // .downloads // 0)
        }' >> "$OUT_JSONL"

  page_count=$count
  TOTAL=$((TOTAL + page_count))
  REQUESTS=$((REQUESTS + 1))
  if [[ "$REQUESTS" -eq 1 && "$total_count_hint" != "null" && "$total_count_hint" != "0" ]]; then
    ESTIMATED_TOTAL="$total_count_hint"
  fi

  if (( MAX_ITEMS > 0 && TOTAL >= MAX_ITEMS )); then
    break
  fi
  if (( MAX_PAGES > 0 && REQUESTS >= MAX_PAGES )); then
    break
  fi

  FETCH_MODE_FALLBACKS=0

  case "$current_mode" in
    auto)
      if [[ "$next_cursor" != "null" && -n "$next_cursor" ]]; then
        current_mode="cursor"
        cursor="$next_cursor"
        PAGE=1
        offset=0
      elif [[ "$total_pages_hint" != "0" && "$total_pages_hint" != "null" ]]; then
        current_mode="page"
        PAGE=$((page_no_hint + 1))
        cursor=""
        offset=0
      elif [[ "$next_page_hint" != "null" && -n "$next_page_hint" ]]; then
        current_mode="page"
        PAGE="$next_page_hint"
        cursor=""
        offset=0
      elif [[ "$count" == "$LIMIT" ]]; then
        current_mode="page"
        PAGE=$((PAGE + 1))
        cursor=""
        offset=0
      elif [[ "$has_more" == "true" || "$has_more" == "1" ]]; then
        current_mode="offset"
      elif [[ "$total_count_hint" != "null" && "$total_count_hint" != "0" && "$total_count_hint" != "" ]]; then
        if (( PAGE * LIMIT < total_count_hint )); then
          current_mode="page"
          PAGE=$((PAGE + 1))
        else
          current_mode="no-pagination"
        fi
      else
        current_mode="no-pagination"
      fi
      ;;

    cursor)
      cursor="$(echo "$response" | jq -r "$extract_next_cursor")"
      if [[ "$cursor" == "null" || -z "$cursor" ]]; then
        break
      fi
      ;;

    page)
      pageno="$(echo "$response" | jq -r "$extract_page")"
      PAGE=$((pageno + 1))
      total_pages="$(echo "$response" | jq -r "$extract_total_pages")"

      if [[ "$total_pages" != "0" && "$total_pages" != "null" ]]; then
        if (( PAGE > total_pages )); then
          break
        fi
      elif (( page_count < LIMIT )); then
        break
      fi
      ;;

    offset)
      offset=$((offset + LIMIT))
      if (( page_count < LIMIT )); then
        break
      fi
      ;;

    no-pagination)
      break
      ;;
  esac

  if (( TOTAL >= MAX_ITEMS )) && (( MAX_ITEMS > 0 )); then
    break
  fi
  if (( MAX_PAGES > 0 && REQUESTS >= MAX_PAGES )); then
    break
  fi

  sleep "$PAUSE"
  done

jq -s 'map(.)' "$OUT_JSONL" > "$OUT_JSON"

if [[ "$ENRICH" == "1" ]]; then
  ENRICH_OUT_JSONL="${OUT_JSONL%.jsonl}_enriched.jsonl"
  ENRICH_OUT_JSON="${ENRICH_OUT_JSONL%.jsonl}.json"

  ENRICH_OUTPUT_DIR="$(dirname "$ENRICH_OUT_JSONL")"
  mkdir -p "$ENRICH_OUTPUT_DIR"

  echo "Starting enrichment..." >&2
  python3 "$ENRICH_SCRIPT" \
    --input "$OUT_JSONL" \
    --output "$ENRICH_OUT_JSONL" \
    --registry "$REGISTRY" \
    --download-endpoint "$DOWNLOAD_ENDPOINT" \
    --workers "$ENRICH_WORKERS" \
    --timeout "$ENRICH_TIMEOUT" \
    --retries "$ENRICH_RETRIES" \
    --pause "$ENRICH_PAUSE" \
    --skip-download "$ENRICH_SKIP_DOWNLOAD" \
    --max "$ENRICH_MAX" \
    || {
      echo "Error: enrichment failed." >&2
      exit 1
    }

  jq -s 'map(.)' "$ENRICH_OUT_JSONL" > "$ENRICH_OUT_JSON"
  OUT_JSONL="$ENRICH_OUT_JSONL"
  OUT_JSON="$ENRICH_OUT_JSON"
fi

COUNT=$(jq 'length' "$OUT_JSON")
{
  echo "Saved JSONL: $OUT_JSONL"
  echo "Saved JSON : $OUT_JSON"
  echo "Total    : $COUNT"
  if [[ -n "$ESTIMATED_TOTAL" && "$ESTIMATED_TOTAL" != "null" && "$ESTIMATED_TOTAL" != "0" ]]; then
    echo "Estimated total from API: $ESTIMATED_TOTAL"
  fi
  echo "Pages    : $REQUESTS"
  echo "Mode     : $current_mode"
} >&2

exit 0
