#!/usr/bin/env python3
import argparse
import concurrent.futures
import io
import json
import re
import ssl
import sys
import time
import zipfile
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import URLError


USER_AGENT = "research-skills-market-bot/2.0 (+https://github.com)"
DEFAULT_GITHUB = ("https://github.com/",)
JSON_FIELDS_FROM_LIST = ("repository_url", "source_code_url", "git_repo", "source")
JSON_FIELDS_TO_REPO = (
    "codeRepository",
    "repository",
    "repositoryUrl",
    "repository_url",
    "repositoryUrlFull",
    "sourceCodeUrl",
    "source_code_url",
    "sourceUrl",
    "source_url",
    "github",
    "github_url",
    "repo",
    "repoUrl",
    "git_repo",
    "gitRepo",
    "git_url",
)
JSON_FIELDS_TO_HOMEPAGE = (
    "homepage",
    "website",
    "site",
    "projectUrl",
    "project_url",
    "documentation",
    "documentationUrl",
    "documentation_url",
    "docUrl",
    "doc_url",
)


def _sleep_pause(pause: float) -> None:
    if pause > 0:
        time.sleep(pause)


def _safe_str(value):
    if isinstance(value, str):
        return value.strip()
    return ""


def _normalize_github_url(value):
    value = _safe_str(value)
    if not value:
        return ""
    if value.startswith("git+https://"):
        value = value[len("git+https://") :]
        value = "https://" + value
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value[len("git@github.com:") :]
    if value.startswith("http://") or value.startswith("https://"):
        raw = value
    elif value.startswith("github.com/"):
        raw = "https://" + value
    else:
        return ""
    if not raw.startswith("https://github.com/"):
        return ""
    # strip markdown wrappers and trailing punctuation
    cleaned = re.sub(r"[,.)>\]]+$", "", re.sub(r"^[`'\"<({\\[]+", "", raw))
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]
    stripped = cleaned.split("?")[0].split("#")[0].rstrip("/")
    parts = stripped.replace("https://github.com/", "").split("/")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        return ""
    return f"{DEFAULT_GITHUB[0]}{parts[0]}/{parts[1]}"


def _extract_slug(url: str, fallback: str = ""):
    if fallback:
        fallback = _safe_str(fallback)
        if fallback:
            return fallback
    if not url or not isinstance(url, str):
        return ""
    url = url.strip()
    if not url:
        return ""
    if "/skills/" in url:
        return url.rsplit("/skills/", 1)[-1].strip("/")
    return ""


def _http_get_bytes(url: str, timeout: int, retries: int, pause: float = 0.0):
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/octet-stream, application/json, text/plain, */*",
    }
    default_ctx = ssl.create_default_context()
    insecure_ctx = ssl._create_unverified_context()
    last_err = None
    for attempt in range(max(1, retries + 1)):
        if attempt > 0:
            _sleep_pause(pause)
        try:
            for context in (default_ctx, insecure_ctx):
                try:
                    req = Request(url, headers=headers, method="GET")
                    with urlopen(req, timeout=timeout, context=context) as resp:
                        if resp.status < 200 or resp.status >= 300:
                            return None, f"http {resp.status}"
                        data = resp.read()
                        if not data:
                            return None, "empty response"
                        return data, ""
                except Exception as err:  # pragma: no cover - network dependent
                    last_err = str(err)
                    if context is not insecure_ctx and isinstance(err, URLError) and isinstance(
                        getattr(err, "reason", None), ssl.SSLError
                    ):
                        continue
                    last_err = str(err)
                    break
        except Exception as err:
            last_err = str(err)
            _sleep_pause(min(1.5 * (attempt + 1), 6.0))
    return None, last_err or "request error"


def _http_get_json(url: str, timeout: int, retries: int, pause: float = 0.0):
    data, err = _http_get_bytes(url, timeout=timeout, retries=retries, pause=pause)
    if data is None:
        return None, err
    try:
        return json.loads(data.decode("utf-8", errors="ignore")), ""
    except Exception as err:
        return None, str(err)


def _walk_text_nodes(payload):
    if isinstance(payload, dict):
        for value in payload.values():
            yield from _walk_text_nodes(value)
    elif isinstance(payload, list):
        for value in payload:
            yield from _walk_text_nodes(value)
    elif isinstance(payload, str):
        yield payload


def _contains_github_repo(url):
    if not url or not isinstance(url, str):
        return False
    return "github.com/" in url.lower()


def _choose_first_http_url(values, *, exclude_domains=()):
    for value in values:
        value = _safe_str(value)
        if not value:
            continue
        candidates = _extract_urls(value)
        if not candidates:
            continue
        for url in candidates:
            if not url.lower().startswith(("http://", "https://")):
                continue
            low = url.lower()
            if any(domain in low for domain in exclude_domains):
                continue
            return url
    return ""


def _first_matching(payload, keys):
    if not isinstance(payload, dict):
        return ""
    for key in keys:
        value = payload.get(key)
        if value is None:
            continue
        if isinstance(value, (dict, list)):
            continue
        value = _safe_str(value)
        if value:
            if key in JSON_FIELDS_TO_REPO:
                normalized = _normalize_github_url(value)
                if normalized:
                    return normalized
            else:
                for url in _extract_urls(value):
                    if url:
                        return url
    return ""


def _extract_repo_from_payload(payload):
    if isinstance(payload, str):
        candidates = []
        candidates.extend(_extract_urls(payload))
        candidates.extend(_walk_text_nodes(payload))
        direct = _choose_first_http_url(candidates)
        return _normalize_github_url(direct)
    if isinstance(payload, list):
        for item in payload:
            found = _extract_repo_from_payload(item)
            if found:
                return found
        return ""

    if not isinstance(payload, dict):
        return ""

    candidate = _first_matching(payload, JSON_FIELDS_TO_REPO)
    if candidate:
        return _normalize_github_url(candidate)

    for value in payload.values():
        found = _extract_repo_from_payload(value)
        if found:
            return found
    return ""


def _is_excluded_homepage_url(url: str):
    low = _safe_str(url).lower()
    if not low:
        return True
    if low.startswith("http://") or low.startswith("https://"):
        for bad in (
            "clawhub.ai",
            "wry-manatee-359.convex.site",
            "avatars.githubusercontent.com",
            "user-images.githubusercontent.com",
        ):
            if bad in low:
                return True
        return False
    return True


def _first_matching(payload, keys, *, exclude_domains=()):
    if not isinstance(payload, dict):
        return ""
    for key in keys:
        value = payload.get(key)
        if value is None:
            continue
        if isinstance(value, (dict, list)):
            continue
        value = _safe_str(value)
        if not value:
            continue
        if key in JSON_FIELDS_TO_REPO:
            normalized = _normalize_github_url(value)
            if normalized:
                return normalized
        else:
            for url in _extract_urls(value):
                if url and not any(domain in url.lower() for domain in exclude_domains):
                    return url
    return ""


def _extract_homepage_from_payload(payload):
    if isinstance(payload, str):
        homepage = _first_matching({"homepage": payload}, ("homepage",))
        if homepage:
            return homepage
        return _choose_first_http_url(
            [payload],
            exclude_domains=(
                "clawhub.ai",
                "wry-manatee-359.convex.site",
                "avatars.githubusercontent.com",
                "user-images.githubusercontent.com",
            ),
        )

    if not isinstance(payload, dict):
        return ""
    direct = _first_matching(
        payload,
        JSON_FIELDS_TO_HOMEPAGE,
        exclude_domains=(
            "avatars.githubusercontent.com",
            "user-images.githubusercontent.com",
        ),
    )
    if direct:
        normalized = direct.strip()
        if normalized and not _is_excluded_homepage_url(normalized):
            return normalized

    for value in payload.values():
        if isinstance(value, (dict, list)):
            found = _extract_homepage_from_payload(value)
            if found:
                return found
        elif isinstance(value, str):
            found = _choose_first_http_url(
                [value],
                exclude_domains=(
                    "clawhub.ai",
                    "wry-manatee-359.convex.site",
                    "avatars.githubusercontent.com",
                    "user-images.githubusercontent.com",
                ),
            )
            if found:
                return found
    return ""


def _extract_urls(text: str):
    if not text:
        return []
    found = []
    # capture common markdown and raw URL patterns
    for m in re.finditer(r"(?:https?://[^\s\]>)]+|git@github\.com:[\w.\-_/]+|git\+https://github\.com/[^\s\]>)]+)", text, re.I):
        found.append(m.group(0))
    return found


def _choose_first_repo(values):
    for value in values:
        normalized = _normalize_github_url(value)
        if normalized:
            return normalized
    return ""


def _extract_front_matter(text: str):
    if not text:
        return ""
    m = re.match(r"(?s)^---\s*\n(.*?)\n---\s*(\n|$)", text)
    if not m:
        return ""
    return m.group(1)


def _extract_metadata_kv(block: str):
    data = {}
    if not block:
        return data
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue
        data[key] = value
    return data


def _extract_install_hint(text: str):
    # prefer explicit install lines, then common command-like lines
    patterns = [
        r"(?im)^\s*install\s*[:=]\s*(.+?)$",
        r"(?im)^\s*clawdbot\.install\s*[:=]\s*(.+?)$",
        r"(?im)^\s*`?(brew|pip\s+install|npm\s+install|go\s+get|python\s+-m\s+pip\s+install)\s+[^`\n]+`?",
    ]
    for pat in patterns:
        m = re.search(pat, text or "")
        if m:
            if len(m.groups()) >= 1 and m.group(0).strip():
                return m.group(0).strip().strip("`").strip()
    return ""


def _extract_from_skill_md(skill_md: str):
    result = {}
    if not skill_md:
        return result
    front = _extract_front_matter(skill_md)
    kv = _extract_metadata_kv(front)

    if "homepage" in kv and kv["homepage"]:
        result["homepage"] = kv["homepage"]
    if "website" in kv and kv["website"]:
        result.setdefault("homepage", kv["website"])

    for field in ("repository", "repository_url", "source_code_url", "sourceurl", "github", "github_url"):
        if field in kv and kv[field]:
            result.setdefault("repo_url", kv[field])

    install = _extract_install_hint(front)
    if install:
        result["install_hint_from_skill_md"] = install

    urls = _extract_urls(skill_md)
    result.setdefault("repo_url_from_body", _choose_first_repo(urls))
    return result


def _enrich_one(
    record: dict,
    registry: str,
    download_endpoint: str,
    timeout: int,
    retries: int,
    pause: float,
    skip_download: bool = False,
):
    slug = _safe_str(record.get("source_slug"))
    if not slug:
        slug = _extract_slug(_safe_str(record.get("url")), _safe_str(record.get("source_slug")))
    source_url = _safe_str(record.get("url"))
    if not source_url and slug:
        source_url = f"{registry.rstrip('/')}/skills/{slug}"

    enriched = dict(record)
    enriched["clawhub_page_url"] = source_url
    enriched["source_url"] = source_url
    enriched["download_zip"] = f"{download_endpoint}{quote(slug)}" if slug else ""

    repo_url = _normalize_github_url(_safe_str(record.get("repository_url")))
    homepage = _safe_str(record.get("homepage", ""))
    install_candidates = [_safe_str(record.get("install_hint", ""))]
    enrich_status = []
    source_api = ""
    source_owner = ""
    guessed_repo_url = ""

    # 1) Try official skill detail payload (both object and slug query fallback)
    if slug:
        detail_url = f"{registry.rstrip('/')}/api/v1/skills/{quote(slug)}"
        payload, err = _http_get_json(detail_url, timeout=timeout, retries=retries, pause=pause)
        if payload and isinstance(payload, dict):
            if isinstance(payload, dict):
                owner_obj = payload.get("owner")
                if isinstance(owner_obj, dict):
                    source_owner = _safe_str(owner_obj.get("handle"))

            candidate_repo = _extract_repo_from_payload(payload)
            if candidate_repo and not repo_url:
                repo_url = candidate_repo

            candidate_home = _extract_homepage_from_payload(payload)
            if candidate_home and not homepage and "clawhub.ai" not in candidate_home.lower():
                homepage = candidate_home

            if not homepage:
                metadata = payload.get("metadata")
                if not isinstance(metadata, dict):
                    metadata = {}
                possible_home = (
                    _safe_str(payload.get("homepage"))
                    or _safe_str(metadata.get("homepage"))
                    or _safe_str(payload.get("website"))
                )
                if possible_home:
                    homepage = possible_home

            if not guessed_repo_url and source_owner and slug:
                guessed_repo_url = _normalize_github_url(f"{DEFAULT_GITHUB[0]}{source_owner}/{quote(slug, safe='')}")

            candidate_hint = _safe_str(payload.get("installHint", "")) or _safe_str(
                payload.get("install_hint", "")
            )
            if candidate_hint:
                install_candidates.append(candidate_hint)

            source_api = payload.get("source", "")
            enrich_status.append("api")
        elif payload and isinstance(payload, list):
            enrich_status.append(f"api_unexpected_list")
        else:
            enrich_status.append(f"api_error:{err if err else 'empty'}")

    # 2) Try SKILL.md from package zip for repo/homepage/install info
    if slug and not skip_download:
        zip_url = enriched["download_zip"]
        zip_data, zip_err = _http_get_bytes(zip_url, timeout=timeout, retries=retries, pause=pause)
        if zip_data is not None:
            try:
                with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
                    candidates = [
                        n
                        for n in zf.namelist()
                        if n.strip("/") and n.lower().split("/")[-1] == "skill.md"
                    ]
                    if candidates:
                        target = min(candidates, key=lambda n: (n.count("/"), len(n)))
                        skill_md_bytes = zf.read(target)
                        skill_md = skill_md_bytes.decode("utf-8", errors="ignore")
                        extracted = _extract_from_skill_md(skill_md)
                        if not repo_url:
                            repo_url = _normalize_github_url(extracted.get("repo_url")) or _normalize_github_url(
                                extracted.get("repo_url_from_body", "")
                            )
                        if not homepage:
                            homepage = _safe_str(extracted.get("homepage", ""))
                        if extracted.get("install_hint_from_skill_md"):
                            install_candidates.append(_safe_str(extracted["install_hint_from_skill_md"]))
                        enrich_status.append("zip")
            except Exception as err:
                enrich_status.append(f"zip_error:{err}")
        else:
            enrich_status.append(f"zip_error:{zip_err}")
    elif slug and skip_download:
        enrich_status.append("zip_skipped")

    if not repo_url and guessed_repo_url:
        repo_url = guessed_repo_url
        enrich_status.append("owner_guess_repo")

    installed = _choose_first_repo(_safe_str(x) for x in install_candidates if x)
    homepage = _safe_str(homepage)
    repo_url = _normalize_github_url(repo_url)

    if repo_url:
        enriched["source_url"] = repo_url
    elif homepage:
        enriched["source_url"] = homepage
    else:
        enriched["source_url"] = source_url

    enriched["homepage"] = homepage
    enriched["repo_url"] = repo_url
    if not enriched.get("install_hint"):
        for candidate in install_candidates:
            if candidate:
                enriched["install_hint"] = candidate
                break
    enriched["install_hint_candidates"] = [x for x in install_candidates if x]
    if installed:
        enriched["install_hint_enhanced"] = installed
    enriched["source_type"] = "official-clawhub"
    enriched["enrich_status"] = ",".join(enrich_status) if enrich_status else "none"
    enriched["enrich_source"] = source_api
    enriched["source_owner"] = source_owner
    if repo_url and repo_url == guessed_repo_url:
        enriched["repo_url_source"] = "owner_slug_guess"
    elif guessed_repo_url and repo_url:
        enriched["repo_url_source"] = "api_or_skillmd"
    elif guessed_repo_url:
        enriched["repo_url_source"] = "none"
    else:
        enriched["repo_url_source"] = "unknown"

    if repo_url and _normalize_github_url(repo_url):
        # canonical git links for market UI usage
        enriched["git_clone"] = f"git clone {repo_url}.git"
        enriched["download_zip_main"] = f"{repo_url}/archive/refs/heads/main.zip"
        enriched["download_zip_master"] = f"{repo_url}/archive/refs/heads/master.zip"
    else:
        enriched["git_clone"] = ""
        enriched["download_zip_main"] = ""
        enriched["download_zip_master"] = ""

    return enriched


def _iter_records(path: str, max_records: int):
    count = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            yield rec
            count += 1
            if max_records > 0 and count >= max_records:
                return


def main():
    parser = argparse.ArgumentParser(description="Enrich clawhub official skill list with repo/homepage/install info.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--download-endpoint", required=True)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--timeout", type=int, default=22)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--pause", type=float, default=0.1)
    parser.add_argument("--skip-download", type=int, default=0)
    parser.add_argument("--max", type=int, default=0)
    args = parser.parse_args()

    workers = max(1, args.workers)
    timeout = max(1, args.timeout)
    retries = max(0, args.retries)
    pause = max(0.0, args.pause)

    records = list(_iter_records(args.input, args.max))
    if not records:
        return 0

    with open(args.output, "w", encoding="utf-8") as out_f:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_index = {
                executor.submit(
                    _enrich_one,
                    rec,
                    args.registry,
                    args.download_endpoint,
                    timeout,
                    retries,
                    pause,
                    args.skip_download == 1,
                ): idx
                for idx, rec in enumerate(records)
            }

            # Preserve source order.
            results = {}
            for fut in concurrent.futures.as_completed(future_to_index):
                idx = future_to_index[fut]
                try:
                    results[idx] = fut.result()
                except Exception as err:  # pragma: no cover - defensive
                    fallback = dict(records[idx])
                    fallback["enrich_status"] = f"error:{err}"
                    fallback["repo_url"] = _normalize_github_url(fallback.get("repository_url", ""))
                    fallback["clawhub_page_url"] = _safe_str(fallback.get("url"))
                    fallback["source_url"] = fallback["repo_url"] or _safe_str(fallback.get("homepage", "")) or _safe_str(fallback.get("url"))
                    fallback["download_zip"] = f"{args.download_endpoint}{quote(_safe_str(fallback.get('source_slug')))}" if fallback.get(
                        "source_slug"
                    ) else ""
                    results[idx] = fallback

            for idx in range(len(records)):
                out_f.write(json.dumps(results[idx], ensure_ascii=False))
                out_f.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
