#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import ssl
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ALLOWED_REPO_HOSTS = {"github.com", "gitlab.com", "gitee.com"}
REPO_KEYS = (
    "repo_url",
    "repository_url",
    "repositoryUrl",
    "source_code_url",
    "sourceCodeUrl",
    "git_repo",
    "gitRepo",
    "github",
    "github_url",
    "source_url",
)


def _safe_str(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _host(raw: str) -> str:
    host = (urlparse(raw).netloc or "").lower()
    return host[4:] if host.startswith("www.") else host


def _is_clawhub_url(raw: str) -> bool:
    host = _host(raw)
    return host.endswith("clawhub.ai")


def _extract_urls(text: str) -> Iterable[str]:
    if not isinstance(text, str) or not text:
        return []
    found = re.findall(r"(?:https?://[^\s\]>)'\"]+|git@github\.com:[\w./-]+)", text, flags=re.IGNORECASE)
    return found


def _normalize_repo_url(raw: str) -> str:
    raw = _safe_str(raw)
    if not raw:
        return ""

    if raw.startswith("git+https://"):
        raw = "https://" + raw[len("git+https://") :]
    if raw.startswith("git@github.com:"):
        raw = "https://github.com/" + raw[len("git@github.com:") :]

    if not raw.startswith(("http://", "https://")):
        if raw.startswith("github.com/"):
            raw = "https://" + raw
        else:
            return ""

    parsed = urlparse(raw)
    host = (parsed.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if host not in ALLOWED_REPO_HOSTS:
        return ""

    parts = [p for p in (parsed.path or "").split("/") if p]
    if len(parts) < 2:
        return ""
    owner = parts[0].strip()
    repo = re.sub(r"\.git$", "", parts[1].strip())
    if not owner or not repo:
        return ""
    return f"https://{host}/{owner}/{repo}"


def _validate_repo_url(repo_url: str, timeout: float = 8.0) -> bool:
    normalized = _normalize_repo_url(repo_url)
    if not normalized:
        return False

    req = Request(
        normalized,
        headers={
            "User-Agent": "research-skills-market-bot/3.0 (+https://github.com)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        method="GET",
    )
    contexts = (ssl.create_default_context(), ssl._create_unverified_context())
    for context in contexts:
        try:
            with urlopen(req, timeout=timeout, context=context) as resp:
                if resp.status < 200 or resp.status >= 400:
                    continue
                final_url = getattr(resp, "url", normalized)
                if _normalize_repo_url(final_url) or _normalize_repo_url(normalized):
                    return True
        except Exception:
            continue
    return False


def _repo_candidates_from_enriched(record: Dict[str, Any]) -> List[Tuple[str, str, float]]:
    out: List[Tuple[str, str, float]] = []
    if not isinstance(record, dict):
        return out

    repo_source = _safe_str(record.get("repo_url_source"))
    conf_map = {
        "api_or_skillmd": 0.95,
        "owner_slug_guess": 0.35,
        "none": 0.0,
        "unknown": 0.2,
    }

    for key in REPO_KEYS:
        value = _safe_str(record.get(key))
        if not value:
            continue
        normalized = _normalize_repo_url(value)
        if normalized:
            base_method = "enriched_repo"
            if key == "source_url" and not _is_clawhub_url(value):
                base_method = "enriched_source_url"
            method = f"{base_method}:{repo_source or 'unknown'}"
            confidence = conf_map.get(repo_source, 0.65)
            if base_method == "enriched_source_url":
                confidence = max(confidence, 0.8)
            out.append((normalized, method, confidence))
        for maybe in _extract_urls(value):
            normalized2 = _normalize_repo_url(maybe)
            if normalized2:
                out.append((normalized2, f"enriched_text_scan:{key}", 0.7))

    return out


def _repo_candidates_from_entry(entry: Dict[str, Any]) -> List[Tuple[str, str, float]]:
    out: List[Tuple[str, str, float]] = []
    existing_repo = _normalize_repo_url(_safe_str(entry.get("repo_url")))
    if existing_repo:
        out.append((existing_repo, "existing_repo_url", 0.7))

    source_url = _safe_str(entry.get("source_url"))
    if source_url and not _is_clawhub_url(source_url):
        normalized = _normalize_repo_url(source_url)
        if normalized:
            out.append((normalized, "existing_source_url", 0.75))

    git_clone = _safe_str(entry.get("git_clone"))
    for maybe in _extract_urls(git_clone):
        normalized = _normalize_repo_url(maybe)
        if normalized:
            out.append((normalized, "existing_git_clone", 0.75))

    return out


def _dedupe_candidates(items: List[Tuple[str, str, float]]) -> List[Tuple[str, str, float]]:
    best: Dict[str, Tuple[str, float]] = {}
    for url, method, confidence in items:
        prev = best.get(url)
        if prev is None or confidence > prev[1]:
            best[url] = (method, confidence)
    ranked = [(url, method, conf) for url, (method, conf) in best.items()]
    ranked.sort(key=lambda x: x[2], reverse=True)
    return ranked


def _load_jsonl_index(path: Path) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if not isinstance(obj, dict):
                continue
            key = _safe_str(obj.get("url"))
            if key:
                out[key] = obj
    return out


def _resolve_one(
    entry: Dict[str, Any],
    enriched: Dict[str, Any],
    timeout: float,
) -> Dict[str, Any]:
    source_page = _safe_str(entry.get("source_url"))
    if source_page and _is_clawhub_url(source_page):
        entry.setdefault("clawhub_page_url", source_page)

    candidates = _repo_candidates_from_entry(entry)
    candidates.extend(_repo_candidates_from_enriched(enriched))
    ranked = _dedupe_candidates(candidates)

    chosen_url = ""
    chosen_method = ""
    chosen_conf = 0.0
    for candidate_url, method, confidence in ranked:
        if _validate_repo_url(candidate_url, timeout=timeout):
            chosen_url = candidate_url
            chosen_method = method
            chosen_conf = confidence
            break

    today = date.today().isoformat()
    if chosen_url:
        entry["canonical_source_url"] = chosen_url
        entry["source_url"] = chosen_url
        entry["repo_url"] = chosen_url
        entry["source_method"] = chosen_method
        entry["source_confidence"] = round(chosen_conf, 2)
        entry["source_status"] = "verified"
        entry["source_checked_at"] = today
        entry["git_clone"] = f"git clone {chosen_url}.git"
        host = _host(chosen_url)
        if host == "github.com":
            entry["download_zip_main"] = f"{chosen_url}/archive/refs/heads/main.zip"
            entry["download_zip_master"] = f"{chosen_url}/archive/refs/heads/master.zip"
        else:
            entry["download_zip_main"] = ""
            entry["download_zip_master"] = ""
        return {"status": "verified", "method": chosen_method, "source": chosen_url}

    entry["canonical_source_url"] = ""
    entry["repo_url"] = ""
    entry["git_clone"] = ""
    entry["download_zip_main"] = ""
    entry["download_zip_master"] = ""
    entry["source_method"] = ""
    entry["source_confidence"] = 0.0
    entry["source_status"] = "missing"
    entry["source_checked_at"] = today
    if source_page and _is_clawhub_url(source_page):
        entry["source_url"] = source_page
    return {"status": "missing", "method": "", "source": ""}


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh and validate source links for curated market entries")
    parser.add_argument("--curated", default="data/curated_market_v2.json")
    parser.add_argument("--enriched-jsonl", default="data/raw/clawhub/clawhub_official_downloads_full_with_links_api_only_enriched_v5.jsonl")
    parser.add_argument("--report", default="data/source_link_refresh_report.json")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--timeout", type=float, default=8.0)
    parser.add_argument("--max", type=int, default=0)
    args = parser.parse_args()

    curated_path = Path(args.curated)
    curated = json.loads(curated_path.read_text(encoding="utf-8"))
    entries = curated.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("invalid curated format: entries must be list")

    enriched_index = _load_jsonl_index(Path(args.enriched_jsonl))

    target_entries = entries[: args.max] if args.max > 0 else entries

    stats = {
        "entries_total": len(entries),
        "entries_targeted": len(target_entries),
        "verified": 0,
        "missing": 0,
        "methods": {},
    }

    workers = max(1, int(args.workers))
    timeout = max(1.0, float(args.timeout))

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        future_map = {}
        for idx, entry in enumerate(target_entries):
            source_key = _safe_str(entry.get("clawhub_page_url") or entry.get("source_url"))
            enriched = enriched_index.get(source_key, {}) if source_key else {}
            future = ex.submit(_resolve_one, entry, enriched, timeout)
            future_map[future] = idx

        for future in concurrent.futures.as_completed(future_map):
            result = future.result()
            status = result.get("status", "missing")
            stats[status] = stats.get(status, 0) + 1
            method = _safe_str(result.get("method"))
            if method:
                stats["methods"][method] = stats["methods"].get(method, 0) + 1

    curated_path.write_text(json.dumps(curated, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.report).write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
