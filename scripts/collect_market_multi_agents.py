#!/usr/bin/env python3
"""Run a multi-process pipeline for Scout / Classifier / Evaluator / Curator / Tester."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import ssl
import uuid
from functools import partial
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from datetime import date
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Tuple
import urllib.error
import urllib.request
from urllib.parse import quote, urlparse, urlsplit, urlunsplit
try:
    import certifi
except ImportError:  # pragma: no cover
    certifi = None
try:
    import requests
except Exception:  # pragma: no cover
    requests = None

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
OUT_RUN = ROOT / "run"

RAW_SEED = [
    {
        "name": "anthropics/docx",
        "url": "https://github.com/anthropics/skills/tree/main/skills/docx",
        "desc": "Create, edit, and analyze Word documents for reports and论文初稿组织。",
        "source_feed": "official-awesome-agent-skills",
        "stars": 0,
        "forks": 0,
    },
    {
        "name": "anthropics/doc-coauthoring",
        "url": "https://github.com/anthropics/skills/tree/main/skills/doc-coauthoring",
        "desc": "Collaborative document editing and co-authoring workflow support.",
        "source_feed": "official-awesome-agent-skills",
        "stars": 0,
        "forks": 0,
    },
    {
        "name": "anthropics/pptx",
        "url": "https://github.com/anthropics/skills/tree/main/skills/pptx",
        "desc": "Create and edit presentation slides for论文汇报/答辩展示。",
        "source_feed": "official-awesome-agent-skills",
        "stars": 0,
        "forks": 0,
    },
    {
        "name": "anthropics/xlsx",
        "url": "https://github.com/anthropics/skills/tree/main/skills/xlsx",
        "desc": "Data analysis in spreadsheet format with公式和图表。",
        "source_feed": "official-awesome-agent-skills",
        "stars": 0,
        "forks": 0,
    },
    {
        "name": "anthropics/pdf",
        "url": "https://github.com/anthropics/skills/tree/main/skills/pdf",
        "desc": "Extract text, split and merge PDFs, and perform structured reading.",
        "source_feed": "official-awesome-agent-skills",
        "stars": 0,
        "forks": 0,
    },
    {
        "name": "anthropics/webapp-testing",
        "url": "https://github.com/anthropics/skills/tree/main/skills/webapp-testing",
        "desc": "Automated web app testing using Playwright to support reproducible实验结果。",
        "source_feed": "official-awesome-agent-skills",
        "stars": 0,
        "forks": 0,
    },
    {
        "name": "anthropics/mcp-builder",
        "url": "https://github.com/anthropics/skills/tree/main/skills/mcp-builder",
        "desc": "Build MCP servers and integrate external APIs for科研流程自动化。",
        "source_feed": "official-awesome-agent-skills",
        "stars": 0,
        "forks": 0,
    },
    {
        "name": "huggingface/hugging-face-datasets",
        "url": "https://github.com/huggingface/skills/tree/main/skills/hugging-face-datasets",
        "desc": "Create and manage datasets with SQL querying for实验复现。",
        "source_feed": "official-awesome-agent-skills",
    },
    {
        "name": "huggingface/hugging-face-evaluation",
        "url": "https://github.com/huggingface/skills/tree/main/skills/hugging-face-evaluation",
        "desc": "Model evaluation for实验对比和指标分析，适用于论文方法评估。",
        "source_feed": "official-awesome-agent-skills",
    },
    {
        "name": "huggingface/hugging-face-model-trainer",
        "url": "https://github.com/huggingface/skills/tree/main/skills/hugging-face-model-trainer",
        "desc": "Model training and fine-tuning workflows useful for可复现实验。",
        "source_feed": "official-awesome-agent-skills",
    },
    {
        "name": "huggingface/hugging-face-paper-publisher",
        "url": "https://github.com/huggingface/skills/tree/main/skills/hugging-face-paper-publisher",
        "desc": "Publish papers with model and dataset links for实验可追溯。",
        "source_feed": "official-awesome-agent-skills",
        "stars": 0,
    },
    {
        "name": "huggingface/hugging-face-trackio",
        "url": "https://github.com/huggingface/skills/tree/main/skills/hugging-face-trackio",
        "desc": "Track ML experiments and experiment artifacts dashboards。",
        "source_feed": "official-awesome-agent-skills",
    },
    {
        "name": "huggingface/hugging-face-cli",
        "url": "https://github.com/huggingface/skills/tree/main/skills/hugging-face-cli",
        "desc": "CLI operations for model/dataset lifecycle and reproducible workflows。",
        "source_feed": "official-awesome-agent-skills",
    },
    {
        "name": "huggingface/hugging-face-tool-builder",
        "url": "https://github.com/huggingface/skills/tree/main/skills/hugging-face-tool-builder",
        "desc": "Build reusable HF API scripts for实验和工具链。",
        "source_feed": "official-awesome-agent-skills",
    },
    {
        "name": "microsoft/azure-ai-document-intelligence-dotnet",
        "url": "https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/ai/Azure.AI.DocumentIntelligence",
        "desc": "Document extraction and OCR for文献和实验记录结构化读取。",
        "source_feed": "official-awesome-agent-skills",
    },
    {
        "name": "microsoft/azure-search-documents-dotnet",
        "url": "https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/search/Azure.Search.Documents",
        "desc": "Vector/hybrid search APIs, useful for literature/数据检索。",
        "source_feed": "official-awesome-agent-skills",
    },
    {
        "name": "microsoft/azure-ai-anomalydetector-java",
        "url": "https://github.com/Azure/azure-sdk-for-java/blob/main/sdk/anomalydetector/README.md",
        "desc": "Anomaly detection and time-series analysis for实验监控。",
        "source_feed": "official-awesome-agent-skills",
    },
    {
        "name": "microsoft/m365-agents-dotnet",
        "url": "https://github.com/Azure-Samples/m365-agent-samples",
        "desc": "M365、Teams和Copilot相关智能体能力，用于文献协同与知识汇报。",
        "source_feed": "official-awesome-agent-skills",
    },
    {
        "name": "PSPDFKit-labs/nutrient-agent-skill",
        "url": "https://github.com/PSPDFKit-labs/nutrient-agent-skill",
        "desc": "Document processing + OCR + form filling, supports论文与资料提取。",
        "source_feed": "community-list",
    },
    {
        "name": "kreuzberg-dev/kreuzberg",
        "url": "https://github.com/kreuzberg-dev/kreuzberg",
        "desc": "Extract text/tables/metadata from many document formats for文献梳理。",
        "source_feed": "community-list",
    },
    {
        "name": "notiondevs/notion-skills",
        "url": "https://github.com/notiondevs/notion",
        "desc": "Notion技能与知识库管理，适合研究知识组织。",
        "source_feed": "community-list",
    },
    {
        "name": "hanfang/claude-memory-skill",
        "url": "https://github.com/hanfang/claude-memory-skill",
        "desc": "Hierarchical memory system for persistent notes and retrieval in研究写作中。",
        "source_feed": "community-list",
    },

    # Literature / database oriented
    {
        "name": "anuj0456/arxiv-mcp-server",
        "url": "https://github.com/anuj0456/arxiv-mcp-server",
        "desc": "Search, analyze and export academic papers from arXiv with citation/trend capabilities。",
        "source_feed": "research-search",
        "stars": 17,
    },
    {
        "name": "prashalruchiranga/arxiv-mcp-server",
        "url": "https://github.com/prashalruchiranga/arxiv-mcp-server",
        "desc": "Search and load arXiv papers with article metadata and PDF export。",
        "source_feed": "research-search",
    },
    {
        "name": "mnehmos/arxiv-mcp-server",
        "url": "https://github.com/Mnehmos/arxiv-mcp-server",
        "desc": "arXiv search, category filtering, paper details and PDF content extraction。",
        "source_feed": "research-search",
    },
    {
        "name": "takashiishida/arxiv-latex-mcp",
        "url": "https://github.com/takashiishida/arxiv-latex-mcp",
        "desc": "Fetch arXiv LaTeX source for equation-heavy paper interpretation。",
        "source_feed": "research-search",
    },
    {
        "name": "1Dark134/arxiv-mcp-server",
        "url": "https://github.com/1Dark134/arxiv-mcp-server",
        "desc": "Citation insights and paper trend exports for literature reviews。",
        "source_feed": "research-search",
        "stars": 8,
    },
    {
        "name": "chrismannina/pubmed-mcp",
        "url": "https://github.com/chrismannina/pubmed-mcp",
        "desc": "PubMed literature search, citations and detailed article comparison。",
        "source_feed": "research-search",
        "stars": 8,
    },
    {
        "name": "grll/pubmedmcp",
        "url": "https://github.com/grll/pubmedmcp",
        "desc": "Search and fetch biomedical citations from PubMed.",
        "source_feed": "research-search",
        "stars": 96,
    },
    {
        "name": "cyanheads/pubmed-mcp-server",
        "url": "https://github.com/cyanheads/pubmed-mcp-server",
        "desc": "A production-grade PubMed server with citation and analysis tools.",
        "source_feed": "research-search",
    },
    {
        "name": "zongmin-yu/semantic-scholar-fastmcp-mcp-server",
        "url": "https://github.com/zongmin-yu/semantic-scholar-fastmcp-mcp-server",
        "desc": "Semantic Scholar API wrapper for citation networks and author data。",
        "source_feed": "research-search",
        "stars": 95,
    },
    {
        "name": "benhaotang/mcp-semantic-scholar-server",
        "url": "https://github.com/benhaotang/mcp-semantic-scholar-server",
        "desc": "MCP server for Semantic Scholar paper search and metadata retrieval。",
        "source_feed": "research-search",
    },
    {
        "name": "hbiaou/openalex-mcp",
        "url": "https://github.com/hbiaou/openalex-mcp",
        "desc": "Academic literature search via OpenAlex API for literature mapping。",
        "source_feed": "research-search",
        "stars": 15,
    },
    {
        "name": "oksure/openalex-research-mcp",
        "url": "https://github.com/oksure/openalex-research-mcp",
        "desc": "OpenAlex API MCP server for研究综述和研究生态分析。",
        "source_feed": "research-search",
    },
    {
        "name": "afrise/academic-search-mcp-server",
        "url": "https://github.com/afrise/academic-search-mcp-server",
        "desc": "Academic paper search across multiple databases for review workflows。",
        "source_feed": "research-search",
    },
    {
        "name": "kujenga/zotero-mcp",
        "url": "https://github.com/kujenga/zotero-mcp",
        "desc": "Operate Zotero libraries for literature检索、全文和元数据。",
        "source_feed": "research-search",
        "stars": 132,
    },
    {
        "name": "cr625/zotero-mcp-server",
        "url": "https://github.com/cr625/zotero-mcp-server",
        "desc": "MCP server with access/search/citation operations for Zotero collections。",
        "source_feed": "research-search",
    },
    {
        "name": "swairshah/zotero-mcp-server",
        "url": "https://github.com/swairshah/zotero-mcp-server",
        "desc": "Expose local Zotero repository to MCP clients for文献管理。",
        "source_feed": "research-search",
    },
    {
        "name": "cookjohn/zotero-mcp",
        "url": "https://github.com/cookjohn/zotero-mcp",
        "desc": "Plugin/connector for Zotero MCP integration and全文检索。",
        "source_feed": "research-search",
    },
    {
        "name": "cyanheads/clinicaltrialsgov-mcp-server",
        "url": "https://github.com/cyanheads/clinicaltrialsgov-mcp-server",
        "desc": "ClinicalTrials.gov search, comparison, eligibility and trend analysis。",
        "source_feed": "research-search",
        "stars": 51,
    },
    {
        "name": "Kartha-AI/agentcare-mcp",
        "url": "https://github.com/Kartha-AI/agentcare-mcp",
        "desc": "FHIR + EMR integration with links to clinical trials and medical research resources。",
        "source_feed": "research-search",
        "stars": 104,
    },
    {
        "name": "Augmented-Nature/ClinicalTrials-MCP-Server",
        "url": "https://github.com/Augmented-Nature/ClinicalTrials-MCP-Server",
        "desc": "Unofficial ClinicalTrials.gov API MCP server for study comparison and analysis。",
        "source_feed": "research-search",
    },
    {
        "name": "JackKuo666/ClinicalTrials-MCP-Server",
        "url": "https://github.com/JackKuo666/ClinicalTrials-MCP-Server",
        "desc": "Search and analyze clinical studies with statistics and trial metadata。",
        "source_feed": "research-search",
        "stars": 13,
    },
    {
        "name": "bio-mcp",
        "url": "https://github.com/bio-mcp",
        "desc": "Bioinformatics MCP collection (BLAST/序列检索等).",
        "source_feed": "research-search",
    },
    {
        "name": "Augmented-Nature/PubChem-MCP-Server",
        "url": "https://github.com/Augmented-Nature/PubChem-MCP-Server",
        "desc": "Access compound and bioassay data from PubChem for chemistry-in-科学 pipelines。",
        "source_feed": "research-search",
        "stars": 32,
    },
    {
        "name": "cyanheads/pubchem-mcp-server",
        "url": "https://github.com/cyanheads/pubchem-mcp-server",
        "desc": "LLM tools for PUG REST API and molecular property lookup。",
        "source_feed": "research-search",
    },

    # non-research or low relevance
    {
        "name": "google-labs-code/design-md",
        "url": "https://github.com/google-labs-code/stitch-skills/tree/main/skills/design-md",
        "desc": "Generate/maintain DESIGN.md for design documentation.",
        "source_feed": "official-awesome-agent-skills",
        "is_non_research": True,
    },
    {
        "name": "vercel-labs/react-native-skills",
        "url": "https://github.com/vercel-labs/agent-skills/tree/main/skills/react-native-skills",
        "desc": "React Native development best practices and upgrade workflows。",
        "source_feed": "official-awesome-agent-skills",
        "is_non_research": True,
    },
    {
        "name": "cloudflare/building-ai-agent-on-cloudflare",
        "url": "https://github.com/cloudflare/skills/tree/main/skills/building-ai-agent-on-cloudflare",
        "desc": "Cloudflare AI agent开发流程 and WebSocket runtime。",
        "source_feed": "official-awesome-agent-skills",
        "is_non_research": True,
    },
    {
        "name": "cloudflare/wrangler",
        "url": "https://github.com/cloudflare/skills/tree/main/skills/wrangler",
        "desc": "CLI reference for deploying Cloudflare Workers。",
        "source_feed": "official-awesome-agent-skills",
        "is_non_research": True,
    },
    {
        "name": "composioHQ/image-enhancer",
        "url": "https://github.com/ComposioHQ/image-enhancer",
        "desc": "Image enhancement and processing utilities。",
        "source_feed": "community-list",
        "is_non_research": True,
    },
]

GRADE_THRESHOLDS = {
    "direct": {"total": 4.3, "security": 4},
    "small": {"total": 3.0, "security": 2},
    "reference": {"total": 2.0, "security": 1},
}

OFFICIAL_FEEDS = {
    "official-awesome-agent-skills",
    "official",
    "official-source",
}

OFFICIAL_ORGS = {
    "anthropics",
    "huggingface",
    "microsoft",
    "azure",
    "azure-samples",
}

KNOWN_ORIGINS = [
    "官方",
    "非官方",
    "未知",
]

RESEARCH_STAGES = ["文献检索", "数据分析", "实验设计", "论文写作", "可视化", "知识管理"]
RESEARCH_DOMAINS = ["文献计量", "统计", "计算机", "知识管理"]
DEFAULT_REJECT_REASON = "当前为产品开发或工程效率类技能，科研关联度较低"
LLM_CLASSIFIER_CACHE: Dict[str, Dict[str, Any]] = {}
_LLM_CALL_COUNT = 0


def _safe(v, d=0):
    return d if v is None else v


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="run research skills market pipeline")
    parser.add_argument(
        "--source-file",
        action="append",
        default=[],
        help="one or more source files (json/jsonl/csv) with skill candidates",
    )
    parser.add_argument(
        "--source-format",
        choices=["auto", "json", "jsonl", "csv"],
        default="auto",
        help="explicit source format; default auto detect by extension",
    )
    parser.add_argument("--max-items", type=int, default=None, help="limit raw candidates for quick test")
    parser.add_argument("--scout-workers", type=int, default=max(1, (os.cpu_count() or 4) - 1))
    parser.add_argument("--scout-chunk", type=int, default=12000)
    parser.add_argument("--classifier-workers", type=int, default=max(1, (os.cpu_count() or 4) - 1))
    parser.add_argument("--enable-llm-classifier", action="store_true", help="use LLM-assisted classification for research relevance")
    parser.add_argument("--llm-only-classifier", action="store_true", help="use LLM-only classification (skip keyword rule stage)")
    parser.add_argument("--llm-provider", default="openai-compatible", choices=["openai-compatible"], help="LLM provider compatibility mode")
    parser.add_argument("--llm-api-url", default="", help="LLM endpoint for chat completions (empty means env var/默认值)")
    parser.add_argument("--llm-api-url-env", default="LLM_API_URL", help="environment variable for API endpoint")
    parser.add_argument("--llm-api-key", default="", help="LLM API key (if empty, read from env)")
    parser.add_argument("--llm-api-key-env", default="OPENAI_API_KEY", help="environment variable for API key")
    parser.add_argument("--llm-model", default="gpt-4o-mini", help="model name sent to chat endpoint")
    parser.add_argument("--llm-timeout", type=float, default=20.0, help="LLM request timeout seconds")
    parser.add_argument(
        "--llm-skip-tls-verify",
        action="store_true",
        help="skip TLS certificate verification for LLM API requests (use only if cert trust fails)",
    )
    parser.add_argument(
        "--llm-ca-bundle",
        default="",
        help="custom CA bundle path for LLM HTTPS requests (defaults to certifi bundle if available)",
    )
    parser.add_argument("--llm-confidence-threshold", type=float, default=0.82, help="if rule confidence >= threshold, skip llm unless --llm-classify-all")
    parser.add_argument("--llm-classify-all", action="store_true", help="use LLM for all items (not just low-confidence ones)")
    parser.add_argument("--llm-max-calls", type=int, default=0, help="max LLM calls for classifier; 0 means no limit")
    parser.add_argument("--llm-temperature", type=float, default=0.0, help="LLM sampling temperature")
    parser.add_argument("--evaluator-workers", type=int, default=max(1, (os.cpu_count() or 4) - 1))
    parser.add_argument("--tester-workers", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    parser.add_argument("--test-top", type=int, default=20)
    parser.add_argument("--publish-before-test", action="store_true", help="publish entries first, then update test tags later")
    parser.add_argument("--skip-tester", action="store_true", help="skip tester stage this run")
    parser.add_argument("--update-test-status-only", action="store_true", help="only apply an existing test report to a published market json")
    parser.add_argument("--curated-market", default=str(DATA_DIR / "curated_market_v2.json"), help="curated market file for status update mode")
    parser.add_argument("--test-report", default=str(DATA_DIR / "test_report_v2.json"), help="test report file for status update mode")
    parser.add_argument("--non-official-priority", action="store_true", help="do not prefer official over community in dedupe")
    parser.add_argument("--resolve-repo-links", action="store_true", help="try to resolve official skill source repo_url from official detail page")
    parser.add_argument("--repo-resolve-timeout", type=float, default=6.0, help="timeout for one repo-lookup request (seconds)")
    parser.add_argument("--repo-resolve-limit", type=int, default=0, help="max number of auto-resolve operations (0 means no limit)")

    return parser.parse_args()


def _normalize_llm_api_url(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        return "https://api.openai.com/v1/chat/completions"

    trimmed = raw.rstrip("/")
    parsed = urlsplit(trimmed)
    if not (parsed.scheme and parsed.netloc):
        # keep legacy behaviour for non-url strings (e.g., hostname without scheme)
        if trimmed.startswith("api.openai.com"):
            return "https://api.openai.com/v1/chat/completions"
        if trimmed.startswith("https://") or trimmed.startswith("http://"):
            return trimmed
        return trimmed

    path = (parsed.path or "").rstrip("/")
    if not path:
        path = "/v1/chat/completions"
    elif path.endswith("/chat/completions"):
        pass
    elif path == "/v1":
        path = "/v1/chat/completions"
    elif path.endswith("/v1"):
        path = path + "/chat/completions"
    elif "/chat/completions" in path:
        pass
    else:
        path = path + "/v1/chat/completions"

    if not path.startswith("/"):
        path = "/" + path
    return urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            path,
            parsed.query,
            "",
        )
    )


def _collect_llm_api_urls(raw_api_url: str) -> List[str]:
    raw_api_url = (raw_api_url or "").strip()
    if not raw_api_url:
        return ["https://api.openai.com/v1/chat/completions"]

    normalized = _normalize_llm_api_url(raw_api_url)
    parsed = urlsplit(raw_api_url)
    raw_candidates: List[str] = []
    normalized_candidates: List[str] = []
    if parsed.scheme and parsed.netloc:
        raw_candidates.append(urlunsplit((parsed.scheme, parsed.netloc, (parsed.path or "/"), parsed.query, "")))
        if normalized not in raw_candidates:
            normalized_candidates.append(normalized)
    else:
        normalized_candidates.append(normalized)

    urls = []
    for item in raw_candidates + normalized_candidates:
        if not item:
            continue
        urls.append(item.rstrip("/"))
    deduped = []
    seen = set()
    for item in urls:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def _build_llm_classifier_config(args: argparse.Namespace) -> Dict[str, Any]:
    if not args.enable_llm_classifier and not args.llm_only_classifier:
        return {"enabled": False}

    api_key = (args.llm_api_key or "").strip()
    if not api_key:
        api_key = (os.environ.get(args.llm_api_key_env, "") or "").strip()
    if not api_key:
        api_key = (os.environ.get("LLM_API_KEY", "") or "").strip()
    if not api_key:
        api_key = (os.environ.get("OPENAI_API_KEY", "") or "").strip()

    raw_api_url = (args.llm_api_url or "").strip()
    if not raw_api_url:
        raw_api_url = (os.environ.get(args.llm_api_url_env, "") or "").strip()
    if not raw_api_url:
        raw_api_url = "https://api.openai.com/v1/chat/completions"
    api_urls = _collect_llm_api_urls(raw_api_url)
    api_url = api_urls[0] if api_urls else _normalize_llm_api_url(raw_api_url)

    return {
        "enabled": True,
        "only": bool(args.llm_only_classifier),
        "provider": args.llm_provider,
        "api_url": api_url,
        "api_urls": api_urls,
        "api_key": api_key,
        "model": args.llm_model.strip() or "gpt-4o-mini",
        "timeout": float(args.llm_timeout or 20.0),
        "temperature": float(args.llm_temperature if args.llm_temperature is not None else 0.0),
        "confidence_threshold": max(0.0, min(1.0, float(args.llm_confidence_threshold or 0.82))),
        "classify_all": bool(args.llm_classify_all),
        "max_calls": int(args.llm_max_calls or 0),
        "skip_tls_verify": bool(args.llm_skip_tls_verify),
        "ca_bundle": (args.llm_ca_bundle or "").strip() or os.environ.get("LLM_CA_BUNDLE", "").strip(),
    }


def _post_json(
    urls: str | List[str],
    payload: Dict[str, Any],
    api_key: str = "",
    timeout: float = 20.0,
    skip_tls_verify: bool = False,
    ca_bundle: str = "",
) -> Any:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; research-skills-market-bot/1.0; +https://github.com)",
        "Accept": "application/json, text/plain, */*",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    debug = os.environ.get("LLM_DEBUG", "").lower() in {"1", "true", "yes", "on"}
    if debug:
        urls_preview = urls if isinstance(urls, str) else ",".join(urls[:3])
        print(f"[LLM] request url={urls_preview}")

    if timeout is None or timeout <= 0:
        timeout = 20.0

    payload_variants = [payload]
    if "max_tokens" in payload and "max_completion_tokens" not in payload:
        alt_payload = dict(payload)
        alt_payload["max_completion_tokens"] = alt_payload.pop("max_tokens")
        payload_variants.append(alt_payload)

    def _parse_json_or_raw(text: str, status_code: int = 0) -> Dict[str, Any]:
        text = (text or "").strip()
        if not text:
            return {"_status_code": status_code, "_raw": "", "_raw_error": "empty"}
        try:
            return json.loads(text)
        except Exception as err:
            return {
                "_status_code": status_code,
                "_raw_error": f"json_decode_failed: {err}",
                "_raw": text[:4000],
            }

    def _ensure_verify():
        if skip_tls_verify:
            return False
        if ca_bundle:
            return ca_bundle
        if certifi and certifi.where():
            return certifi.where()
        return True

    api_urls = _collect_llm_api_urls(urls) if isinstance(urls, str) else list(urls)

    def _requests_post() -> Dict[str, Any]:
        last_response: Dict[str, Any] = {"_status_code": 0, "_raw": "", "_raw_error": "requests_failed"}
        for url_idx, url in enumerate(api_urls, start=1):
            for body_idx, body in enumerate(payload_variants, start=1):
                data = json.dumps(body, ensure_ascii=False)
                if api_key:
                    auth_headers = [
                        {**dict(headers), "Authorization": f"Bearer {api_key}"},
                        {**dict(headers), "api-key": api_key},
                        {**dict(headers), "X-API-Key": api_key},
                        {**dict(headers), "X-API-KEY": api_key},
                        dict(headers),
                    ]
                else:
                    auth_headers = [dict(headers)]
                # dedupe
                auth_headers = list({json.dumps(item, sort_keys=True): item for item in auth_headers}.values())
                for header_idx, hdr in enumerate(auth_headers):
                    try:
                        resp = requests.post(url, headers=hdr, data=data, timeout=timeout, verify=_ensure_verify()) if requests is not None else None
                        if resp is None:
                            continue
                        text = resp.text or ""
                        if debug:
                            print(f"[LLM] request attempt url={url_idx} variant={body_idx} header={header_idx} status={resp.status_code} len={len(text)}")
                        if resp.status_code >= 200 and resp.status_code < 300:
                            parsed = _parse_json_or_raw(text, resp.status_code)
                            if "_raw_error" in parsed:
                                last_response = parsed
                                last_response["_url"] = url
                                # if provider返回非JSON内容，继续尝试下一个地址/参数组合
                                continue
                            return parsed
                        parsed = _parse_json_or_raw(text, resp.status_code)
                        last_response = parsed
                        last_response["_url"] = url
                        if resp.status_code in {400, 422} and "max_tokens" in payload and body_idx == 1:
                            # some providers reject max_tokens, try alt payload
                            break
                        # try other auth headers/payload variants first, do not return early
                        continue
                    except Exception as err:
                        if debug:
                            print(f"[LLM] requests exception: {err}")
                        last_response = {"_status_code": 0, "_raw": "", "_raw_error": str(err), "_url": url}
                        continue
        return last_response

    # Prefer requests as primary transport; keep urllib as fallback
    if requests is not None:
        return _requests_post()

    contexts = []
    if skip_tls_verify:
        contexts.append((ssl._create_unverified_context(), "skip-tls"))
    else:
        contexts.append((ssl.create_default_context(), "system-trust"))
        if ca_bundle:
            try:
                contexts.append((ssl.create_default_context(cafile=ca_bundle), "custom-ca"))
            except OSError:
                contexts.append((ssl.create_default_context(), "system-trust"))
        if certifi and certifi.where():
            try:
                contexts.append((ssl.create_default_context(cafile=certifi.where()), "certifi-ca"))
            except OSError:
                pass

    last_error = None
    for url_idx, url in enumerate(api_urls, start=1):
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        if debug:
            print(f"[LLM] urllib request url={url_idx} endpoint={url}")
        for idx, (context, label) in enumerate(contexts):
            if idx > 0 and last_error is not None and debug:
                print(f"[LLM] retry with {label}")
            try:
                with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
                    data = response.read()
                    content = data.decode("utf-8", errors="ignore") if data else ""
                    if response.status < 200 or response.status >= 300:
                        last_error = {
                            "_status_code": response.status,
                            "_raw": content[:4000],
                            "_raw_error": "status_error",
                            "_url": url,
                        }
                        continue
                    return _parse_json_or_raw(content, response.status)
            except ssl.SSLCertVerificationError as err:
                last_error = err
                continue
            except urllib.error.URLError as err:
                last_error = err
                continue
            except Exception as err:
                if debug:
                    print(f"[LLM] urllib exception: {err}")
                return {"_status_code": 0, "_raw": "", "_raw_error": str(err)}

    if last_error is not None:
        if debug:
            print(f"[LLM] request failed: {last_error}")
        if isinstance(last_error, dict):
            return {
                "_status_code": last_error.get("_status_code", 0),
                "_raw": last_error.get("_raw", ""),
                "_raw_error": last_error.get("_raw_error", str(last_error)),
                "_url": last_error.get("_url"),
            }
        return {"_status_code": 0, "_raw": "", "_raw_error": str(last_error)}
    return {"_status_code": 0, "_raw": "", "_raw_error": "unknown"}


def chunks(items: List[Dict[str, Any]], size: int) -> Iterable[List[Dict[str, Any]]]:
    for i in range(0, len(items), size):
        yield items[i:i + size]


def normalize_source_feed(raw: Dict[str, Any]) -> str:
    for k in ["source_feed", "source", "origin", "sourceType", "channel"]:
        v = raw.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return "unknown"


def normalize_seed_item(raw: Dict[str, Any], default_source: str = "seed") -> Dict[str, Any]:
    name = raw.get("name") or raw.get("repo") or raw.get("full_name") or raw.get("title") or raw.get("id")
    url = raw.get("url") or raw.get("repo_url") or raw.get("source_url") or raw.get("html_url")
    repo_hint = (
        raw.get("repo_url")
        or raw.get("repository_url")
        or raw.get("repositoryUrl")
        or raw.get("source_code_url")
        or raw.get("sourceCodeUrl")
        or raw.get("git_repo")
        or raw.get("gitRepo")
        or raw.get("html_url")
        or raw.get("source_url")
        or raw.get("github")
        or raw.get("github_url")
        or raw.get("repo")
    )
    desc = raw.get("desc") or raw.get("description") or raw.get("summary") or raw.get("raw_description") or ""
    if not isinstance(name, str) or not isinstance(url, str):
        return {}

    return {
        "name": name.strip(),
        "url": url.strip(),
        "desc": desc.strip() if isinstance(desc, str) else "",
        "source_feed": normalize_source_feed(raw) or default_source,
        "stars": _safe(raw.get("stars", raw.get("stargazers_count", 0)), 0),
        "forks": _safe(raw.get("forks", raw.get("forks_count", 0)), 0),
        "is_non_research": bool(raw.get("is_non_research", raw.get("not_research", False))),
        "source_slug": raw.get("source_slug", ""),
        "repo_hint": str(repo_hint).strip() if isinstance(repo_hint, str) else "",
        "source_file": default_source,
    }


def load_json_seed(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        obj = json.load(f)

    if isinstance(obj, dict):
        for key in ["items", "data", "results", "skills", "rows"]:
            if key in obj and isinstance(obj[key], list):
                obj = obj[key]
                break
        else:
            # sometimes dict is actually one sample record
            if isinstance(obj.get("name") or obj.get("url") or obj.get("repo"), str):
                obj = [obj]
            else:
                obj = []

    if not isinstance(obj, list):
        return []

    return [normalize_seed_item(item, default_source=str(path)) for item in obj if isinstance(item, dict)]


def load_jsonl_seed(path: Path) -> List[Dict[str, Any]]:
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                out.append(normalize_seed_item(item, default_source=str(path)))
    return out


def load_csv_seed(path: Path) -> List[Dict[str, Any]]:
    out = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if isinstance(row, dict):
                out.append(normalize_seed_item(row, default_source=str(path)))
    return out


def load_seed_sources(source_files: List[str], source_format: str) -> List[Dict[str, Any]]:
    out = []
    for sf in source_files:
        path = Path(sf)
        if not path.exists():
            print(f"WARN: source file not found: {path}")
            continue
        fmt = (source_format if source_format != "auto" else path.suffix.lower().lstrip(".")) or "json"
        fmt = fmt.lower()

        if fmt == "jsonl":
            out.extend(load_jsonl_seed(path))
        elif fmt == "csv":
            out.extend(load_csv_seed(path))
        else:
            out.extend(load_json_seed(path))

    # remove empty
    out = [r for r in out if r.get("name") and r.get("url")]
    return out


def detect_origin_type(seed: Dict[str, Any]) -> str:
    feed = (seed.get("source_feed") or "").lower()
    if feed in OFFICIAL_FEEDS or "official" in feed:
        return "官方"
    if feed in {"community-list", "community"} or "community" in feed:
        return "非官方"

    url = seed.get("url", "") or ""
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+)", url)
    if m:
        org = m.group(1).lower()
        if org in OFFICIAL_ORGS:
            return "官方"

    return "未知"


def dedup_key(item: Dict[str, Any]) -> str:
    return str(item.get("url", "")).strip().lower()


def dedup_candidates(items: List[Dict[str, Any]], prefer_non_official: bool = False) -> List[Dict[str, Any]]:
    if not items:
        return []

    rank = {"官方": 0, "未知": 1, "非官方": 2}
    if prefer_non_official:
        rank = {"非官方": 0, "官方": 1, "未知": 2}

    picked: Dict[str, Dict[str, Any]] = {}
    for item in items:
        key = dedup_key(item)
        if key not in picked:
            picked[key] = item
            continue

        if rank[item.get("origin_type", "未知")] < rank[picked[key].get("origin_type", "未知")]:
            picked[key] = item

    return list(picked.values())


def run_scout(agent: str, candidates: List[Dict[str, str]], run_id: str):
    out = []
    for item in candidates:
        rec = {
            "id": str(uuid.uuid4()),
            "name": item["name"],
            "url": item["url"],
            "source": item.get("source_feed", "unknown"),
            "raw_description": item.get("desc", ""),
            "stars": _safe(item.get("stars"), 0),
            "forks": _safe(item.get("forks"), 0),
            "origin_type": detect_origin_type(item),
            "source_file": item.get("source_file", "seed"),
            "source_slug": item.get("source_slug", ""),
            "repo_hint": item.get("repo_hint", ""),
            "collected_at": str(date.today()),
            "agent": "Scout",
            "run_id": run_id,
            "extra": {
                "forced_non_research": bool(item.get("is_non_research", False)),
                "agent_hint": agent,
            },
        }
        out.append(rec)

    return out


def _stage_and_domains(text: str, forced_non_research: bool):
    t = (text or "").lower()
    if forced_non_research:
        return [], []

    stages = []
    domains = []

    if any(k in t for k in ["arxiv", "pubmed", "semantic", "openalex", "scholar", "paper", "literature", "zotero", "citation", "trial", "clinical", "pubchem"]):
        stages.append("文献检索")
        domains.append("文献计量")

    if any(k in t for k in ["dataset", "sql", "数据", "analysis", "anomaly", "track", "实验", "model-trainer", "evaluation", "benchmark", "metrics"]):
        stages.append("数据分析")
        domains.extend(["计算机", "统计"])

    if any(k in t for k in ["实验", "训练", "reproduc", "pipeline", "workflow", "mcp", "api", "automation", "agent"]):
        stages.append("实验设计")
        if "计算机" not in domains:
            domains.append("计算机")

    if any(k in t for k in ["pdf", "doc", "xlsx", "pptx", "coauthor", "协作", "paper", "写作", "文稿", "report"]):
        stages.append("论文写作")
        if "知识管理" not in domains:
            domains.append("知识管理")

    if any(k in t for k in ["visual", "chart", "dashboard", "图", "可视化", "visualize"]):
        stages.append("可视化")

    if any(k in t for k in ["memory", "notion", "knowledge", "知识库", "知识管理", "记忆", "tag", "citation", "wiki"]):
        stages.append("知识管理")

    # 去重
    stages = list(dict.fromkeys(stages))
    domains = list(dict.fromkeys(domains))
    keyword_hits = sum(
        1 for keyword in [
            "arxiv",
            "pubmed",
            "semantic",
            "openalex",
            "scholar",
            "paper",
            "literature",
            "zotero",
            "citation",
            "analysis",
            "dataset",
            "实验",
            "workflow",
            "pipeline",
            "mcp",
            "api",
            "reproduc",
            "paper",
            "coauthor",
            "visual",
            "memory",
            "pdf",
            "xlsx",
            "doc",
            "sql",
        ]
        if keyword in t
    )
    confidence = 0.05 if not stages else min(0.95, 0.6 + 0.05 * keyword_hits + 0.05 * len(stages))
    return stages, domains, min(1.0, confidence)


def _safe_list_of_strings(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    out = []
    for item in value:
        if isinstance(item, str):
            text = item.strip()
            if text:
                out.append(text)
    return out


def _extract_first_json_block(text: str) -> str:
    if not isinstance(text, str):
        return ""
    match = re.search(r"\{[\s\S]*\}", text)
    return match.group(0) if match else text.strip()


def _classify_with_llm(text: str, name: str, url: str, llm_config: Dict[str, Any], fallback_reason: str) -> Dict[str, Any] | None:
    global _LLM_CALL_COUNT

    if not llm_config.get("enabled", False):
        return None
    if llm_config.get("max_calls", 0) > 0 and _LLM_CALL_COUNT >= llm_config["max_calls"]:
        return {
            "status": "skipped",
            "reason": f"LLM call limit reached ({llm_config['max_calls']})",
        }

    cache_key = f"{llm_config.get('model')}::{name}::{text[:200]}"
    cached = LLM_CLASSIFIER_CACHE.get(cache_key)
    if cached:
        return {"status": "cache", **cached}

    system_prompt = (
        "你是科研技能分类器，输出必须是严格 JSON：\n"
        "{\n"
        "  \"is_research_related\": bool,\n"
        "  \"research_stages\": [string...],\n"
        "  \"research_domains\": [string...],\n"
        "  \"fit_reason\": \"简短中文原因\",\n"
        "  \"reject_reason\": \"简短中文原因（无研究相关时）\",\n"
        "  \"confidence\": 0.0-1.0,\n"
        "  \"rationale\": \"判定依据\",\n"
        "}\n"
        "research_stages 仅允许: 文献检索, 数据分析, 实验设计, 论文写作, 可视化, 知识管理.\n"
        "research_domains 仅允许: 文献计量, 统计, 计算机, 知识管理.\n"
    )
    user_prompt = (
        f"候选：\n名称：{name}\n描述：{text}\n"
        f"来源：{url}\n"
        f"规则分类备选：{fallback_reason}\n"
        "请判断是否适合科研场景（文献检索、实验设计、数据分析、论文写作、可视化、知识管理），并返回上面 JSON 格式。"
    )
    payload = {
        "model": llm_config.get("model", "gpt-4o-mini"),
        "temperature": llm_config.get("temperature", 0.0),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 400,
    }

    try:
        resp = _post_json(
            llm_config["api_urls"],
            payload,
            api_key=llm_config.get("api_key", ""),
            timeout=llm_config.get("timeout", 20.0),
            skip_tls_verify=llm_config.get("skip_tls_verify", False),
            ca_bundle=llm_config.get("ca_bundle", ""),
        )
        if not isinstance(resp, dict):
            return {"status": "invalid", "reason": "响应不是 JSON 对象"}
        if resp.get("_raw_error"):
            status = resp.get("_status_code", "")
            url_used = resp.get("_url")
            if url_used:
                url_msg = f"（url={url_used}）"
            else:
                url_msg = ""
            if status:
                return {"status": "invalid", "reason": f"LLM API 调用失败(status={status}){url_msg}: {resp.get('_raw_error')}"}
            return {"status": "invalid", "reason": f"LLM API 调用失败{url_msg}: {resp.get('_raw_error')}"}
        if "error" in resp:
            return {"status": "error", "reason": f"API返回错误: {json.dumps(resp.get('error'), ensure_ascii=False)}"}
        raw = ""
        message = resp.get("choices", [{}])[0].get("message", {})
        if isinstance(message, dict):
            raw = str(message.get("content", "")).strip()
        if not raw and isinstance(resp.get("output_text"), str):
            raw = resp["output_text"].strip()
        if not raw and isinstance(resp.get("content"), str):
            raw = resp["content"].strip()
        if not raw and isinstance(resp.get("_raw"), str):
            raw = resp.get("_raw", "").strip()
        if not raw:
            if resp.get("_status_code"):
                return {"status": "invalid", "reason": f"模型返回空/不可解析响应(status={resp.get('_status_code')}): {str(resp.get('_raw', ''))[:240]}"}
            return {"status": "invalid", "reason": "模型未返回内容"}

        parsed = json.loads(_extract_first_json_block(raw))
        is_research = bool(parsed.get("is_research_related"))
        stages = _safe_list_of_strings(parsed.get("research_stages"))
        domains = _safe_list_of_strings(parsed.get("research_domains"))
        stages = [s for s in stages if s in RESEARCH_STAGES]
        domains = [d for d in domains if d in RESEARCH_DOMAINS]

        parsed_confidence = float(parsed.get("confidence", 0.0))
        if not (0 <= parsed_confidence <= 1):
            parsed_confidence = 0.5

        result = {
            "status": "ok",
            "is_research_related": is_research,
            "research_stages": stages,
            "research_domains": domains,
            "fit_reason": str(parsed.get("fit_reason", "")).strip() if parsed.get("fit_reason") else "",
            "reject_reason": str(parsed.get("reject_reason", "")).strip() if parsed.get("reject_reason") else "",
            "confidence": parsed_confidence,
            "rationale": str(parsed.get("rationale", "")).strip(),
            "raw_model_output": raw[:1500],
        }
        if not result["fit_reason"] and result["is_research_related"]:
            result["fit_reason"] = "LLM 判定为科研相关技能"
        if not result["reject_reason"] and not result["is_research_related"]:
            result["reject_reason"] = fallback_reason

        LLM_CLASSIFIER_CACHE[cache_key] = result
        _LLM_CALL_COUNT += 1
        return result
    except Exception as err:
        return {"status": "error", "reason": f"LLM call failed: {err}"}


def run_classifier(item: Dict[str, str], llm_config: Dict[str, Any] | None = None):
    if llm_config is None:
        llm_config = {"enabled": False}
    text = (item.get("name", "") + " " + item.get("raw_description", "")).lower()
    forced_non_research = bool(item.get("extra", {}).get("forced_non_research", False))
    if forced_non_research:
        return {
            "candidate_id": item["id"],
            "origin_type": item.get("origin_type", "未知"),
            "is_research_related": False,
            "research_stages": [],
            "research_domains": [],
            "tech_stack": ["python" if "python" in text else "typescript" if "ts" in text else "mixed"],
            "tags": ["待评估"],
            "fit_reason": "",
            "reject_reason": DEFAULT_REJECT_REASON,
            "agent": "Classifier",
            "classifier_mode": "keyword" if not llm_config.get("enabled") else "llm-only-fallback",
            "rule_confidence": 0.0,
            "llm_status": "forced_non_research",
            "confidence": 0.0,
            "classifier_rationale": "来源已标记为非科研用途",
        }

    if llm_config.get("enabled") and llm_config.get("only"):
        llm_result = _classify_with_llm(
            (item.get("name", "") + " " + item.get("raw_description", "")),
            item.get("name", ""),
            item.get("url", ""),
            llm_config,
            DEFAULT_REJECT_REASON,
        )
        if not llm_result:
            return {
                "candidate_id": item["id"],
                "origin_type": item.get("origin_type", "未知"),
                "is_research_related": False,
                "research_stages": [],
                "research_domains": [],
                "tech_stack": ["python" if "python" in text else "typescript" if "ts" in text else "mixed"],
                "tags": ["待评估"],
                "fit_reason": "",
                "reject_reason": "LLM分类失败，待补充评估",
                "agent": "Classifier",
                "classifier_mode": "llm-only",
                "rule_confidence": 0.0,
                "llm_status": "failed",
                "confidence": 0.0,
            "classifier_rationale": "LLM调用未返回有效结果",
        }
    if llm_config.get("enabled") and not forced_non_research:
        llm_result = _classify_with_llm(
            (item.get("name", "") + " " + item.get("raw_description", "")),
            item.get("name", ""),
            item.get("url", ""),
            llm_config,
            DEFAULT_REJECT_REASON,
        )
        if llm_result and llm_result.get("status") == "ok":
            return {
                "candidate_id": item["id"],
                "origin_type": item.get("origin_type", "未知"),
                "is_research_related": llm_result.get("is_research_related", False),
                "research_stages": llm_result.get("research_stages", []),
                "research_domains": llm_result.get("research_domains", []),
                "tech_stack": ["python" if "python" in text else "typescript" if "ts" in text else "mixed"],
                "tags": [s for s in llm_result.get("research_stages", []) if s] or ["待评估"],
                "fit_reason": llm_result.get("fit_reason", ""),
                "reject_reason": llm_result.get("reject_reason", ""),
                "agent": "Classifier",
                "classifier_mode": "llm-only",
                "rule_confidence": 0.0,
                "llm_status": llm_result.get("status", "ok"),
                "confidence": llm_result.get("confidence", 0.0),
                "classifier_rationale": llm_result.get("rationale", ""),
            }

        reason = llm_result.get("reason") if isinstance(llm_result, dict) else "LLM分类失败，待补充评估"
        return {
            "candidate_id": item["id"],
            "origin_type": item.get("origin_type", "未知"),
            "is_research_related": False,
            "research_stages": [],
            "research_domains": [],
            "tech_stack": ["python" if "python" in text else "typescript" if "ts" in text else "mixed"],
            "tags": ["待评估"],
            "fit_reason": "",
            "reject_reason": reason or "LLM分类失败，待补充评估",
            "agent": "Classifier",
            "classifier_mode": "llm-only",
            "rule_confidence": 0.0,
            "llm_status": llm_result.get("status", "failed") if isinstance(llm_result, dict) else "failed",
            "confidence": 0.0,
            "classifier_rationale": reason or "",
        }

    rule_stages, rule_domains, rule_confidence = _stage_and_domains(text, forced_non_research)
    is_research = bool(rule_stages)
    reason = "" if is_research else DEFAULT_REJECT_REASON
    if is_research:
        reason = "匹配文献/实验/数据/写作/可视化场景关键词"

    return {
        "candidate_id": item["id"],
        "origin_type": item.get("origin_type", "未知"),
        "is_research_related": is_research,
        "research_stages": rule_stages,
        "research_domains": rule_domains,
        "tech_stack": ["python" if "python" in text else "typescript" if "ts" in text else "mixed"],
        "tags": [s for s in ("文献检索", "实验", "数据", "写作") if any(k in s for k in rule_stages)] or ["待评估"],
        "fit_reason": reason if is_research else "",
        "reject_reason": "" if is_research else reason,
        "agent": "Classifier",
        "classifier_mode": "keyword",
        "rule_confidence": round(rule_confidence, 4),
        "llm_status": "",
        "confidence": rule_confidence,
    }


_REPO_URL_CACHE: Dict[str, str] = {}


def _extract_skill_slug(url: str) -> str:
    try:
        parsed = urlparse(url)
    except Exception:
        return ""

    if parsed.netloc.replace("www.", "") != "clawhub.ai":
        return ""

    segments = [segment for segment in parsed.path.split("/") if segment]
    if len(segments) < 2 or segments[0] != "skills":
        return ""

    return segments[1]


def _is_github_repo_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    host = (parsed.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if host != "github.com":
        return False
    parts = [segment for segment in (parsed.path or "").split("/") if segment]
    return len(parts) >= 2


def _normalize_github_repo(url: str) -> str:
    if not isinstance(url, str):
        return ""
    url = url.strip()

    if re.match(r"^git@github\\.com:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\\.git)?$", url, re.IGNORECASE):
        owner, repo = re.sub(r"^git@github\\.com:", "", url, flags=re.IGNORECASE).split("/", 1)
        repo = re.sub(r"\\.git$", "", repo)
        return f"https://github.com/{owner}/{repo}"

    try:
        parsed = urlparse(url)
    except Exception:
        return ""
    host = (parsed.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if host != "github.com":
        return ""
    parts = [segment for segment in (parsed.path or "").split("/") if segment]
    if len(parts) < 2:
        return ""
    owner = parts[0].strip()
    repo = re.sub(r"\.git$", "", parts[1].strip())
    if not owner or not repo:
        return ""
    return f"https://github.com/{owner}/{repo}"


def _extract_repo_from_text(value: str) -> str:
    if not value:
        return ""
    m = re.search(r"https?://(?:www\\.)?github\\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+[^\\s\"'`<>]*", value, re.IGNORECASE)
    if not m:
        return ""
    return _normalize_github_repo(m.group(0))


def _extract_repo_from_payload(payload: Any) -> str:
    if isinstance(payload, str):
        return _extract_repo_from_text(payload)

    if isinstance(payload, list):
        for item in payload:
            found = _extract_repo_from_payload(item)
            if found:
                return found
        return ""

    if isinstance(payload, dict):
        for key in (
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
        ):
            if key in payload:
                found = _extract_repo_from_payload(payload.get(key))
                if found:
                    return found

        for value in payload.values():
            found = _extract_repo_from_payload(value)
            if found:
                return found

    return ""


def _http_get_text(url: str, timeout: float = 6.0) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; research-skills-market-bot/1.0; +https://github.com)",
            "Accept": "application/json, text/plain, */*",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as response:
            if response.status < 200 or response.status >= 300:
                return ""
            data = response.read()
            if not data:
                return ""
            return data.decode("utf-8", errors="ignore")
    except Exception as err:
        if not isinstance(err, urllib.error.HTTPError):
            # Keep only visible errors in explicit debug mode if needed
            pass
        return ""


def _resolve_repo_from_official_page(url: str, timeout: float = 6.0, slug: str = "") -> str:
    if not isinstance(url, str):
        return ""

    key = f"{url}::{slug}"
    if key in _REPO_URL_CACHE:
        return _REPO_URL_CACHE[key]

    for candidate in (url,):
        body = _http_get_text(candidate, timeout=timeout)
        if not body:
            continue
        found = _extract_repo_from_payload(body)
        if found:
            _REPO_URL_CACHE[key] = found
            return found

    # fallback: try skill detail API endpoint
    if not slug:
        slug = _extract_skill_slug(url)
    if not slug:
        return ""

    for endpoint in (
        f"https://clawhub.ai/api/v1/skills/{quote(slug)}",
        f"https://clawhub.ai/api/v1/skills?slug={quote(slug)}",
    ):
        payload = _http_get_text(endpoint, timeout=timeout)
        if not payload or payload.lstrip().startswith("<"):
            continue
        try:
            parsed = json.loads(payload)
        except Exception:
            continue
        found = _extract_repo_from_payload(parsed)
        if found:
            _REPO_URL_CACHE[key] = found
            return found

    return ""


def _clean_link_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    value = value.strip()
    if not value or value == "#":
        return ""
    return value


def _normalize_links(source: Dict[str, str]) -> Dict[str, str]:
    source_url = _clean_link_text(source.get("source_url"))
    repo_url = _clean_link_text(source.get("repo_url"))

    if not source_url or (not source_url.startswith("http://") and not source_url.startswith("https://")):
        source_url = ""

    if repo_url and repo_url == source_url:
        repo_url = ""

    if repo_url and not (repo_url.startswith("http://") or repo_url.startswith("https://")):
        norm = _normalize_github_repo(repo_url)
        repo_url = norm

    if repo_url == source_url:
        repo_url = ""

    source["source_url"] = source_url
    source["repo_url"] = repo_url

    if repo_url and _is_github_repo_url(repo_url):
        source["git_clone"] = f"git clone {repo_url}.git"
        source["download_zip_main"] = f"{repo_url}/archive/refs/heads/main.zip"
        source["download_zip_master"] = f"{repo_url}/archive/refs/heads/master.zip"
    else:
        source["git_clone"] = ""
        source["download_zip_main"] = ""
        source["download_zip_master"] = ""

    return source


def build_source_links(
    candidate: Dict[str, Any],
    *,
    resolve_repo: bool = False,
    resolve_budget: Dict[str, int] | None = None,
    resolve_limit: int = 0,
    resolve_timeout: float = 6.0,
) -> Dict[str, str]:
    url = candidate.get("url", "")
    source = {
        "source_url": url,
        "repo_url": "",
        "git_clone": "",
        "download_zip_main": "",
        "download_zip_master": "",
    }

    if not isinstance(url, str):
        return source

    repo_url = _normalize_github_repo(candidate.get("repo_hint", ""))
    if not repo_url and _is_github_repo_url(url):
        repo_url = _normalize_github_repo(url)

    if not repo_url and resolve_repo:
        can_resolve = resolve_limit <= 0
        if resolve_budget is not None and resolve_limit > 0:
            if resolve_budget.get("count", 0) >= resolve_limit:
                can_resolve = False
        if can_resolve:
            if resolve_budget is not None:
                resolve_budget["count"] = resolve_budget.get("count", 0) + 1
            repo_url = _resolve_repo_from_official_page(url, timeout=resolve_timeout, slug=str(candidate.get("source_slug", "")))

    source["repo_url"] = repo_url or ""

    return _normalize_links(source)


def _security_risk(item: Dict[str, Any], classified: Dict[str, Any], scores: Dict[str, float]):
    flags = []
    text = (item.get("name", "") + " " + item.get("raw_description", "")).lower()

    if item.get("origin_type") == "非官方":
        flags.append("非官方来源，建议人工复核权限与发布者可信度")

    if _safe(item.get("stars", 0), 0) < 5:
        flags.append("社区活跃度较低（stars < 5）")

    if _safe(item.get("forks", 0), 0) == 0 and item.get("origin_type") == "非官方":
        flags.append("社区分支/协作证据不足（forks=0）")

    if "api" in text and "key" in text and _safe(item.get("stars", 0), 0) < 20:
        flags.append("依赖外部 API 且缺乏社区验证，需重点检查 secret/鉴权边界")

    if not classified["is_research_related"]:
        flags.append("用途偏工程/产品开发，不属于科研主线")

    if item.get("origin_type") == "非官方" and scores["security"] >= 4:
        flags.append("虽有权限声明，但来源依旧建议先在沙箱环境验证")

    risk_level = "高"
    if scores["security"] >= 4.0:
        risk_level = "低"
    elif scores["security"] >= 3.0:
        risk_level = "中"

    return flags, risk_level


def _scores_from_profile(item: Dict[str, str], classified: Dict[str, str]):
    text = (item.get("name", "") + " " + item.get("raw_description", "")).lower()
    stars = item.get("stars") or 0

    if stars >= 80:
        maturity = 4.6
    elif stars >= 30:
        maturity = 4.0
    elif stars >= 10:
        maturity = 3.5
    else:
        maturity = 3.0

    code_quality = 3.5
    if "server" in text:
        code_quality += 0.4
    if "api" in text:
        code_quality += 0.2
    if item.get("origin_type") == "官方":
        code_quality += 0.2
    code_quality = min(code_quality, 5)

    docs = 4.0 if "README" in item.get("raw_description", "") or "README" in text else 3.4

    if not classified["is_research_related"]:
        code_quality = 2.0
        docs = 1.8
        maturity = 2.0
        usability = 2.0
        security = 1.5
    else:
        usability = 3.9 if ("search" in text or "analysis" in text or "paper" in text) else 3.3
        security = 4.0 if "auth" in text or "oauth" in text or stars >= 50 else 3.4
        if item.get("origin_type") == "官方":
            security += 0.4

    return {
        "code_quality": round(code_quality, 2),
        "docs": round(docs, 2),
        "maintainability": 3.8 if stars >= 50 else 3.4 if stars >= 20 else 3.0,
        "maturity": round(maturity, 2),
        "usability": round(usability, 2),
        "security": round(min(security, 5), 2),
    }


def run_evaluator(candidate: Dict[str, str], classified: Dict[str, str]):
    scores = _scores_from_profile(candidate, classified)
    total = (
        scores["code_quality"] * 0.20
        + scores["docs"] * 0.10
        + scores["maintainability"] * 0.20
        + scores["maturity"] * 0.20
        + scores["usability"] * 0.20
        + scores["security"] * 0.10
    )

    if classified["is_research_related"] and scores["security"] >= GRADE_THRESHOLDS["direct"]["security"] and total >= GRADE_THRESHOLDS["direct"]["total"]:
        grade = "可直接用"
    elif classified["is_research_related"] and scores["security"] >= GRADE_THRESHOLDS["small"]["security"] and total >= GRADE_THRESHOLDS["small"]["total"]:
        grade = "需小改"
    elif classified["is_research_related"] and total >= GRADE_THRESHOLDS["reference"]["total"]:
        grade = "仅参考"
    elif classified["is_research_related"]:
        grade = "仅参考"
    else:
        grade = "不推荐"

    security_checks, risk_level = _security_risk(candidate, classified, scores)

    return {
        "classified_id": candidate["id"],
        "quality_score": scores,
        "grade": grade,
        "security_level": risk_level,
        "security_checks": security_checks,
        "notes": f"自动评估总分={total:.2f}，依据: 代码清晰度、可维护性、成熟度、可用性、权限边界",
        "agent": "Evaluator",
        "run_id": candidate.get("run_id"),
    }


def _evaluate_pair(payload: Tuple[Dict[str, str], Dict[str, str]]):
    return run_evaluator(payload[0], payload[1])


_TERM_DICT = [
    (r"\bautomates?\b", "自动化"),
    (r"\bautomating\b", "自动化"),
    (r"\bauto\b", "自动"),
    (r"\bresearch\b", "科研"),
    (r"\bliterature\b", "文献"),
    (r"\bpapers?\b", "论文"),
    (r"\bpaper\b", "论文"),
    (r"\bdataset\b", "数据集"),
    (r"\bdatasets\b", "数据集"),
    (r"\bdata\b", "数据"),
    (r"\banalyze\b", "分析"),
    (r"\banalyzing\b", "分析"),
    (r"\banalysis\b", "分析"),
    (r"\banalysis\b", "分析"),
    (r"\bworkflow\b", "流程"),
    (r"\bworkflows\b", "流程"),
    (r"\bmanage\b", "管理"),
    (r"\bmanagement\b", "管理"),
    (r"\bsearch\b", "搜索"),
    (r"\bretriev\w*\b", "检索"),
    (r"\bquery\b", "查询"),
    (r"\bfilter\b", "过滤"),
    (r"\bvisual|visualization|visualize|visualising|visualizing\b", "可视化"),
    (r"\bplot\b", "绘图"),
    (r"\bdashboard\b", "仪表盘"),
    (r"\bdocumentation\b", "文档"),
    (r"\bdocument\b", "文档"),
    (r"\bdocuments\b", "文档"),
    (r"\bcreate\b", "创建"),
    (r"\bcreation\b", "创建"),
    (r"\bbuild\b", "构建"),
    (r"\bbuilding\b", "构建"),
    (r"\bgenerate\b", "生成"),
    (r"\bdownload\b", "下载"),
    (r"\bexports?\b", "导出"),
    (r"\bimport\b", "导入"),
    (r"\bpipeline\b", "流程"),
    (r"\bagent\b", "智能体"),
    (r"\bassist|assistant\b", "助手"),
    (r"\btool\b", "工具"),
    (r"\bserver\b", "服务端"),
    (r"\bapi\b", "API"),
    (r"\bgithub\b", "GitHub"),
    (r"\bcli\b", "CLI"),
    (r"\bplugin\b", "插件"),
    (r"\bplugin\b", "插件"),
    (r"\bintegration\b", "集成"),
    (r"\bsync\b", "同步"),
    (r"\breproducible\b", "可复现"),
    (r"\breproduce\b", "复现"),
    (r"\breproducibility\b", "可复现性"),
    (r"\bmodel\b", "模型"),
    (r"\btraining\b", "训练"),
    (r"\blearn\w*\b", "学习"),
]


def _has_chinese(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text or ""))


def _rough_zh_translate(text: str, subject: str = "该技能") -> str:
    if not text:
        return f"{subject}可用于科研场景。"
    if _has_chinese(text):
        return text.strip()

    translated = text
    for pattern, rep in _TERM_DICT:
        translated = re.sub(pattern, rep, translated, flags=re.IGNORECASE)

    translated = re.sub(r"\s{2,}", " ", translated).strip().strip("。.!?")
    translated = f"{subject}，用于科研场景{('，用于' if translated else '')}{translated}。"
    return translated


def _zh_stage_list(stages: List[str]) -> str:
    if not stages:
        return "待补充"
    return ",".join(stages)


def _en_stage_list(stages: List[str]) -> str:
    mapping = {
        "文献检索": "Literature Search",
        "实验设计": "Experiment Design",
        "数据分析": "Data Analysis",
        "论文写作": "Paper Writing",
        "可视化": "Visualization",
        "知识管理": "Knowledge Management",
        "待补充": "To be categorized",
    }
    return ",".join(mapping.get(x, x) for x in stages) if stages else "To be categorized"


def _to_english_step_list(steps: List[str]) -> List[str]:
    if not steps:
        return ["Please check the repository README before setup."]
    return [
        "Setup by following the repository README.",
        "Configure API keys or local dependencies if required.",
        "Run one small sample task to verify (e.g., search one keyword or process a single document).",
    ]


def _default_test_meta() -> Dict[str, Any]:
    return {
        "test_status": "待测试",
        "test_verdict": "待测试",
        "test_pass_rate": None,
        "test_cases": [],
        "tested_at": "",
    }


def _status_from_pass_rate(pass_rate: float, verdict: str) -> str:
    if pass_rate >= 0.67:
        return "已测试-通过"
    if pass_rate > 0:
        return "已测试-需改进"
    if pass_rate <= 0:
        return "已测试-未通过"
    return "已测试-待确认"


def _apply_test_report(entries: List[Dict[str, Any]], test_report: Dict[str, Any], now: str = "") -> Dict[str, int]:
    if not test_report:
        return {"updated": 0, "total": len(entries)}

    report_items = test_report.get("items", [])
    if not isinstance(report_items, list):
        return {"updated": 0, "total": len(entries)}

    index = {item.get("id"): item for item in report_items if isinstance(item, dict)}
    updated = 0
    for ent in entries:
        report_item = index.get(ent.get("evaluation_id"))
        if not report_item:
            continue
        pass_rate = report_item.get("pass_rate")
        if pass_rate is None:
            continue
        verdict = report_item.get("verdict", ent.get("test_verdict", "待测试"))
        ent.update(
            {
                "test_status": _status_from_pass_rate(float(pass_rate), str(verdict)),
                "test_verdict": str(verdict),
                "test_pass_rate": pass_rate,
                "test_cases": report_item.get("cases", []),
                "tested_at": now or str(date.today()),
                "test_summary": {
                    "passed_case_count": report_item.get("passed_case_count", 0),
                    "total_case_count": report_item.get("total_case_count", 0),
                },
            }
        )
        updated += 1
    return {"updated": updated, "total": len(entries)}


def run_curation(
    evaluations: List[Dict],
    classified_map: Dict[str, Dict],
    *,
    resolve_repo_links: bool = False,
    repo_resolve_timeout: float = 6.0,
    repo_resolve_limit: int = 0,
):
    entries = []
    filtered = []
    resolve_state = {"count": 0}
    bundles = {
        "文献检索五件套": ["文献检索", "论文写作", "知识管理"],
        "实验复现实验套件": ["实验设计", "数据分析", "可视化"],
    }

    for ev in evaluations:
        c = classified_map[ev["classified_id"]]
        status = "draft"
        raw_desc = c.get("raw_description", c.get("desc", ""))
        stage_list = c["research_stages"]
        use_case_zh = _zh_stage_list(stage_list)
        use_case_en = _en_stage_list(stage_list)
        desc_zh = _rough_zh_translate(raw_desc, c["name"])
        difficulty_zh = "入门" if ev["grade"] == "可直接用" else "进阶"
        difficulty_en = "Beginner" if difficulty_zh == "入门" else "Advanced"
        if ev["grade"] in ["可直接用", "需小改"]:
            status = "published"
            bundle = []
            for b, tags in bundles.items():
                if any(tag in c["research_stages"] for tag in tags):
                    bundle.append(b)
            if not bundle:
                bundle = ["综合科研工具"]
            links = build_source_links(
                c,
                resolve_repo=resolve_repo_links,
                resolve_budget=resolve_state,
                resolve_limit=repo_resolve_limit,
                resolve_timeout=repo_resolve_timeout,
            )

            entries.append({
                "evaluation_id": ev["classified_id"],
                "title": c["name"],
                "title_zh": c["name"],
                "title_en": c["name"],
                "one_line": raw_desc,
                "one_line_zh": desc_zh,
                "one_line_en": raw_desc,
                "use_case": use_case_zh,
                "use_case_zh": use_case_zh,
                "use_case_en": use_case_en,
                "source_url": links["source_url"],
                "repo_url": links["repo_url"],
                "git_clone": links["git_clone"],
                "download_zip_main": links["download_zip_main"],
                "download_zip_master": links["download_zip_master"],
                "difficulty": difficulty_zh,
                "difficulty_zh": difficulty_zh,
                "difficulty_en": difficulty_en,
                "category_path": c["research_stages"][:2] or ["待分类"],
                "bundle_ids": bundle,
                "status": status,
                "grade": ev["grade"],
                "origin_type": c.get("origin_type", "未知"),
                "security_level": ev.get("security_level", "中"),
                "security_checks": ev.get("security_checks", []),
                **_default_test_meta(),
            })
        else:
            filtered.append({
                "evaluation_id": ev["classified_id"],
                "title": c["name"],
                "reason": ",".join(ev["security_checks"]) or "非科研或目标不匹配",
                "reason_zh": ",".join(ev["security_checks"]) or "非科研或目标不匹配",
                "reason_en": ",".join(ev["security_checks"]) or "Not matching research scenarios.",
                "status": status,
                "origin_type": c.get("origin_type", "未知"),
                "security_level": ev.get("security_level", "中"),
            })

    return entries, filtered


def _test_entry(entry: Dict[str, Any], top_n: int = 20) -> Dict[str, Any]:
    cases = [
        {"case_id": "T1", "scenario": "文献检索", "required_stage": "文献检索", "pass_if_present": True},
        {"case_id": "T2", "scenario": "数据分析", "required_stage": "数据分析", "pass_if_present": True},
        {"case_id": "T3", "scenario": "论文写作", "required_stage": "论文写作", "pass_if_present": True},
    ]

    stages = entry.get("use_case", "")
    passes = []
    for case in cases:
        hit = case["required_stage"] in stages
        passes.append(
            {
                "case_id": case["case_id"],
                "scenario": case["scenario"],
                "pass": bool(hit),
                "notes": "通过" if hit else f"缺少{case['required_stage']}能力映射",
            }
        )

    pass_rate = mean([1 if p["pass"] else 0 for p in passes])
    passed = sum(1 for p in passes if p["pass"])
    return {
        "id": entry["evaluation_id"],
        "title": entry.get("title", ""),
        "cases": passes,
        "pass_rate": round(pass_rate, 2),
        "passed_case_count": passed,
        "total_case_count": len(passes),
        "verdict": "通过" if pass_rate >= 0.67 else "需改进",
        "grade": entry.get("grade"),
    }


def run_tester(entries: List[Dict], top_n=20, workers=1):
    target = entries[:top_n]
    now = str(date.today())
    if workers <= 1:
        test_items = [_test_entry(ent) for ent in target]
    else:
        try:
            with ProcessPoolExecutor(max_workers=workers) as executor:
                test_items = list(executor.map(_test_entry, target))
        except Exception as err:
            print(f"[Tester] process pool fallback: {err}")
            with ThreadPoolExecutor(max_workers=workers) as executor:
                test_items = list(executor.map(_test_entry, target))

    entry_map = {entry["evaluation_id"]: entry for entry in entries}
    tested_ids = set()
    for item in test_items:
        ent = entry_map.get(item["id"])
        if not ent:
            continue
        ent.update(
            {
                "test_status": _status_from_pass_rate(item["pass_rate"], item["verdict"]),
                "test_verdict": item["verdict"],
                "test_pass_rate": item["pass_rate"],
                "test_cases": item["cases"],
                "tested_at": now,
                "test_summary": {
                    "passed_case_count": item["passed_case_count"],
                    "total_case_count": item["total_case_count"],
                },
            }
        )
        tested_ids.add(item["id"])

    for ent in entries:
        if ent["evaluation_id"] not in tested_ids:
            ent.setdefault("test_status", "待测试")

    return {
        "verifier": "Tester",
        "run_at": str(date.today()),
        "test_scope": f"Top {top_n} published skills + 3场景",
        "items": test_items,
        "summary": {
            "items_total": len(entries),
            "tested": len(test_items),
            "overall_pass_rate": round(mean([i["pass_rate"] for i in test_items]) if test_items else 0, 2),
            "comment": "该轮为场景映射测试，不含外网真实连通与端到端运行。",
        },
    }


def to_market_md(classified: Dict, entries: List[Dict], filtered: List[Dict], out_dir: Path):
    origin_counter = Counter([c.get("origin_type", "未知") for c in classified])
    security_counter = Counter([e.get("security_level", "中") for e in entries])

    lines = [
        "# 科研 Skills 市场",
        "",
        "## 一、抓取与评估概览",
        f"- 总raw候选：{len(classified)}",
    f"- 研究相关：{len([c for c in classified if c.get('is_research_related', False)])}",
        f"- 可上架（可直接用/需小改）：{len(entries)}",
        f"- 过滤/不推荐：{len(filtered)}",
        f"- 来源结构：官方 {origin_counter.get('官方', 0)}，非官方 {origin_counter.get('非官方', 0)}，未知 {origin_counter.get('未知', 0)}",
        f"- 安全级别分布：低 {security_counter.get('低', 0)}，中 {security_counter.get('中', 0)}，高 {security_counter.get('高', 0)}",
        "",
        "## 二、上架结果（按流程：文献→数据→工具链）",
        "",
    ]

    # 文献
    lines.append("### 文献检索")
    for e in [x for x in entries if "文献检索" in x["use_case"]]:
        lines.extend(
            [
                f"- {e['title']} ({e['grade']}, {e.get('origin_type', '未知')}, 风险:{e.get('security_level', '中')})",
                f"  - 一句话：{e['one_line']}",
                f"  - 场景：{e['use_case']}",
                "",
            ]
        )

    # 数据复现
    lines.append("### 数据分析与实验")
    for e in [x for x in entries if ("数据分析" in x["use_case"] or "实验设计" in x["use_case"] or "可视化" in x["use_case"])]:
        lines.extend(
            [
                f"- {e['title']} ({e['grade']}, {e.get('origin_type', '未知')}, 风险:{e.get('security_level', '中')})",
                f"  - 一句话：{e['one_line']}",
                f"  - 场景：{e['use_case']}",
                "",
            ]
        )

    # 被过滤
    lines.append("### 被过滤")
    for f in filtered:
        lines.append(f"- {f['title']}（{f['origin_type']}）：{f['reason']}")

    lines.extend(
        [
            "",
            "## 下载与上手",
            "",
            "- 进入上架列表后可直接点击：`查看源码`、`下载 ZIP`、`复制安装命令`。",
            "- 已按来源与安全级别标注官方/非官方与风险提示。",
            "- 建议先看仓库 README 的依赖与鉴权说明，再执行最小样例验证。",
            "- 所有入口均基于仓库公开链接，支持离线二次分发。",
        ]
    )

    path = out_dir / "market-showcase-v2.md"
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return path


def _market_html_items(entries: List[Dict]) -> List[Dict]:
    cleaned = []
    for item in entries:
        cleaned.append({k: v for k, v in item.items() if not k.startswith("quick_start")})
    return cleaned


def _legacy_to_market_html(entries: List[Dict], filtered: List[Dict], out_dir: Path):
    market_payload = {
        "items": _market_html_items(entries),
        "filtered": filtered,
    }
    payload = json.dumps(market_payload, ensure_ascii=False).replace("</script>", "<\\/script>")

    lines = [
        "<!doctype html>",
        '<html lang="zh-CN">',
        "<head>",
        "  <meta charset=\"utf-8\" />",
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />",
        "  <title>科研 Skills 市场</title>",
        "  <style>",
        "    :root {",
        "      --bg: #050b17;",
        "      --panel: #111a31;",
        "      --border: #273f70;",
        "      --text: #eaf0ff;",
        "      --muted: #9eb0d5;",
        "      --accent: #72abff;",
        "      --good: #22c55e;",
        "      --warn: #f59e0b;",
        "    }",
        "    * { box-sizing: border-box; }",
        "    body {",
        "      margin: 0;",
        "      min-height: 100vh;",
        "      padding: 24px;",
        "      font-family: 'Noto Sans SC', Inter, 'Segoe UI', Roboto, sans-serif;",
        "      background: radial-gradient(circle at 12% 2%, #1c2f58, var(--bg) 38%),",
        "        linear-gradient(180deg, #050b17 0%, #091127 100%);",
        "      color: var(--text);",
        "    }",
        "    .container { max-width: 1120px; margin: 0 auto; }",
        "    .top {",
        "      border: 1px solid var(--border);",
        "      border-radius: 18px;",
        "      padding: 18px 20px;",
        "      margin-bottom: 16px;",
        "      background: linear-gradient(120deg, rgba(114, 171, 255, .16), rgba(255,255,255,0.05));",
        "    }",
        "    h1 { margin: 0 0 8px; font-size: 34px; letter-spacing: 0.4px; }",
        "    p { margin: 0; color: var(--muted); }",
        "    .toolbar { display: grid; grid-template-columns: 1.3fr 1fr 1fr 1fr 1fr 1fr; gap: 12px; margin-top: 14px; }",
        "    .toolbar > div label { display:block; margin-bottom: 5px; font-size: 12px; color: var(--muted); }",
        "    .toolbar input, .toolbar select {",
        "      width: 100%;",
        "      padding: 10px 11px;",
        "      border: 1px solid var(--border);",
        "      border-radius: 10px;",
        "      background: #0a1430;",
        "      color: var(--text);",
        "    }",
        "    .stats {",
        "      margin-top: 10px;",
        "      display: flex;",
        "      gap: 12px;",
        "      flex-wrap: wrap;",
        "    }",
        "    .stats .item {",
        "      border: 1px solid var(--border);",
        "      border-radius: 10px;",
        "      padding: 10px 14px;",
        "      background: #0a1430;",
        "    }",
        "    .grid {",
        "      margin-top: 14px;",
        "      display: grid;",
        "      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));",
        "      gap: 14px;",
        "    }",
        "    .card {",
        "      border: 1px solid var(--border);",
        "      border-radius: 14px;",
        "      background: var(--panel);",
        "      padding: 14px;",
        "    }",
        "    .card h3 { margin: 0 0 8px; font-size: 18px; line-height: 1.35; }",
        "    .meta { color: var(--muted); font-size: 13px; margin-bottom: 8px; display: flex; gap: 8px; flex-wrap: wrap; }",
        "    .meta span { white-space: nowrap; }",
        "    .tag { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; }",
        "    .good { background: rgba(34,197,94,.2); color: #aefcb8; }",
        "    .warn { background: rgba(245,158,11,.2); color: #fde68a; }",
        "    .actions { margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap; }",
        "    .btn {",
        "      text-decoration: none;",
        "      color: var(--text);",
        "      border: 0;",
        "      border-radius: 10px;",
        "      background: #17316f;",
        "      padding: 8px 10px;",
        "      font-size: 13px;",
        "      cursor: pointer;",
        "      display: inline-block;",
        "    }",
        "    .btn-primary { background: var(--accent); color: #05102f; font-weight: 600; }",
        "    .mini { margin-top: 9px; font-size: 12px; color: var(--muted); }",
        "    ul.steps { margin: 10px 0 0 16px; padding: 0; color: #c6d4f5; font-size: 13px; }",
        "    ul.steps li { margin: 4px 0; }",
        "    code { background: rgba(255,255,255,.08); padding: 2px 5px; border-radius: 6px; }",
        "    .filtered { margin-top: 22px; border: 1px dashed var(--border); border-radius: 12px; padding: 12px 16px; background: rgba(11,23,52,.45); }",
        "    .filtered.hidden { display: none; }",
        "    .filtered ul { margin: 8px 0 0 20px; }",
        "    .filtered li { margin: 5px 0; color: #d6e0ff; }",
        "    .origin-official { background: rgba(34,197,94,.2); color: #aefcb8; }",
        "    .origin-non-official { background: rgba(168,85,247,.2); color: #ddd5ff; }",
        "    .origin-unknown { background: rgba(148,163,184,.2); color: #d1d5db; }",
        "    .risk-high { background: rgba(239,68,68,.2); color: #fecaca; }",
        "    .risk-mid { background: rgba(245,158,11,.2); color: #fde68a; }",
        "    .risk-low { background: rgba(34,197,94,.2); color: #aefcb8; }",
        "    .status-ok { background: rgba(34,197,94,.2); color: #aefcb8; }",
        "    .status-warn { background: rgba(245,158,11,.2); color: #fde68a; }",
        "    .status-pending { background: rgba(56,189,248,.2); color: #bfdbfe; }",
        "    .status-fail { background: rgba(239,68,68,.2); color: #fecaca; }",
        "    .toast {",
        "      position: fixed;",
        "      right: 22px;",
        "      bottom: 22px;",
        "      border: 1px solid var(--border);",
        "      border-radius: 10px;",
        "      background: #111e45;",
        "      padding: 10px 12px;",
        "      opacity: 0;",
        "      transform: translateY(12px);",
        "      transition: .25s;",
        "    }",
        "    .toast.show { opacity: 1; transform: translateY(0); }",
        "    @media (max-width: 860px) {",
        "      .toolbar { grid-template-columns: 1fr 1fr 1fr; }",
        "    }",
        "    @media (max-width: 640px) {",
        "      body { padding: 12px; }",
        "      .toolbar { grid-template-columns: 1fr 1fr; }",
        "      h1 { font-size: 24px; }",
        "      .toolbar input, .toolbar select { font-size: 13px; }",
        "    }",
        "  </style>",
        "</head>",
        "<body>",
        "  <div class=\"container\">",
        "    <header class=\"top\">",
        "      <h1>科研 Skills 市场</h1>",
        "      <p>可搜索、筛选、复制安装命令并直接下载 Skill 源码。支持官方/非官方与安全风险筛选。</p>",
        "      <div class=\"toolbar\">",
        "        <div>",
        "          <label>关键词</label>",
        "          <input id=\"keyword\" type=\"text\" placeholder=\"输入技能名 / 场景 / 简介关键词\" />",
        "        </div>",
        "        <div>",
        "          <label>流程场景</label>",
        "          <select id=\"stage\">",
        "            <option value=\"全部\">全部</option>",
        "          </select>",
        "        </div>",
        "        <div>",
        "          <label>评分等级</label>",
        "          <select id=\"grade\">",
        "            <option value=\"全部\">全部</option>",
        "            <option>可直接用</option>",
        "            <option>需小改</option>",
        "            <option>仅参考</option>",
        "          </select>",
        "        </div>",
        "        <div>",
        "          <label>使用门槛</label>",
        "          <select id=\"difficulty\">",
        "            <option value=\"全部\">全部</option>",
        "            <option>入门</option>",
        "            <option>进阶</option>",
        "          </select>",
        "        </div>",
        "        <div>",
        "          <label>来源</label>",
        "          <select id=\"origin\">",
        "            <option value=\"全部\">全部</option>",
        "            <option>官方</option>",
        "            <option>非官方</option>",
        "            <option>未知</option>",
        "          </select>",
        "        </div>",
        "        <div>",
        "          <label>安全风险</label>",
        "          <select id=\"risk\">",
        "            <option value=\"全部\">全部</option>",
        "            <option>低</option>",
        "            <option>中</option>",
        "            <option>高</option>",
        "          </select>",
        "        </div>",
        "      </div>",
        "      <div class=\"stats\">",
        f"        <div class=\"item\">上架可用：<strong>{len(entries)}</strong> 个</div>",
        "        <div class=\"item\">当前结果：<strong id=\"resultCount\">0</strong> 个</div>",
        "      </div>",
        "    </header>",
        "    <main class=\"grid\" id=\"marketGrid\"></main>",
        "  </div>",
        "  <div id=\"toast\" class=\"toast\">已复制安装命令</div>",
        "  <script>",
        f"    const market = {payload};",
        "    const keywordInput = document.getElementById('keyword');",
        "    const stageSelect = document.getElementById('stage');",
        "    const gradeSelect = document.getElementById('grade');",
        "    const difficultySelect = document.getElementById('difficulty');",
        "    const originSelect = document.getElementById('origin');",
        "    const riskSelect = document.getElementById('risk');",
        "    const marketGrid = document.getElementById('marketGrid');",
        "    const resultCount = document.getElementById('resultCount');",
        "    const toast = document.getElementById('toast');",
        "",
        "    const allStages = Array.from(new Set(",
        "      market.items.flatMap((item) => String(item.use_case || '').split(',').map((s) => s.trim()).filter(Boolean))",
        "    )).filter((x) => x !== '待补充');",
        "    allStages.forEach((stage) => {",
        "      const opt = document.createElement('option');",
        "      opt.value = stage;",
        "      opt.textContent = stage;",
        "      stageSelect.appendChild(opt);",
        "    });",
        "",
        "    const escapeHtml = (value) => String(value ?? '')",
        "      .replaceAll('&', '&amp;')",
        "      .replaceAll('<', '&lt;')",
        "      .replaceAll('>', '&gt;')",
        "      .replaceAll('\\\"', '&quot;')",
        "      .replaceAll(\"'\", '&#39;');",
        "",
        "    const originClass = (v) => v === '官方' ? 'origin-official' : v === '非官方' ? 'origin-non-official' : 'origin-unknown';",
        "    const riskClass = (v) => v === '低' ? 'risk-low' : v === '中' ? 'risk-mid' : 'risk-high';",
        "",
        "    const copy = async (text, btn) => {",
        "      try {",
        "        await navigator.clipboard.writeText(text);",
        "        btn.textContent = '已复制';",
        "        toast.classList.add('show');",
        "        setTimeout(() => {",
        "          toast.classList.remove('show');",
        "          btn.textContent = '复制安装命令';",
        "        }, 1300);",
        "      } catch (err) {",
        "        btn.textContent = '复制失败';",
        "      }",
        "    };",
        "",
        "    const cardTemplate = (item) => {",
        "      const tagClass = item.grade === '可直接用' ? 'good' : 'warn';",
        "      const zipMain = item.download_zip_main ? `<a class=\\\"btn\\\" href=\\\"${escapeHtml(item.download_zip_main)}\\\" target=\\\"_blank\\\">下载 ZIP(main)</a>` : '';",
        "      const zipMaster = item.download_zip_master ? `<a class=\\\"btn\\\" href=\\\"${escapeHtml(item.download_zip_master)}\\\" target=\\\"_blank\\\">下载 ZIP(master)</a>` : '';",
        "      const copyCmdRaw = item.git_clone || item.source_url || '';",
        "      const cloneCmd = escapeHtml(copyCmdRaw);",
        "      const source = escapeHtml(item.source_url || '');",
        "      const repo = escapeHtml(item.repo_url || '');",
        "      const hasSource = source && source !== '#';",
        "      const hasRepo = repo && repo !== source;",
        "      const sourceButton = hasSource ? `<a class=\\\"btn\\\" href=\\\"${source}\\\" target=\\\"_blank\\\">打开技能页</a>` : '';",
        "      const repoButton = hasRepo ? `<a class=\\\"btn btn-primary\\\" href=\\\"${repo}\\\" target=\\\"_blank\\\">查看源码</a>` : '';",
        "      const codeHint = item.git_clone ? `<span class=\\\"mini\\\">安装提示：优先执行 <code>${escapeHtml(item.git_clone)}</code></span>` : '<span class=\\\"mini\\\">安装提示：请按仓库说明配置依赖。</span>';",
        "      const origin = item.origin_type || '未知';",
        "      const risk = item.security_level || '中';",
        "      return `<article class=\\\"card\\\">",
        "        <h3>${escapeHtml(item.title)}</h3>",
        "        <div class=\\\"meta\\\"><span class=\\\"tag ${tagClass}\\\">${escapeHtml(item.grade)}</span><span class=\\\"tag ${originClass(origin)}\\\">${escapeHtml(origin)}</span><span class=\\\"tag ${riskClass(risk)}\\\">风险:${escapeHtml(risk)}</span><span>场景：${escapeHtml(item.use_case || '待补充')}</span><span>门槛：${escapeHtml(item.difficulty || '进阶')}</span></div>",
        "        <p>${escapeHtml(item.one_line)}</p>",
        "        <div class=\\\"actions\\\">",
        "          ${repoButton}",
        "          ${sourceButton}",
        "          <button class=\\\"btn copy\\\" data-cmd=\\\"${cloneCmd}\\\">复制安装命令</button>",
        "          ${zipMain}${zipMaster}",
        "        </div>",
        "        ${codeHint}",
        "      </article>`;",
        "    };",
        "",
        "    const render = () => {",
        "      const keyword = keywordInput.value.trim().toLowerCase();",
        "      const stage = stageSelect.value;",
        "      const grade = gradeSelect.value;",
        "      const difficulty = difficultySelect.value;",
        "      const origin = originSelect.value;",
        "      const risk = riskSelect.value;",
        "",
        "      const visible = market.items.filter((item) => {",
        "        const text = `${item.title} ${item.one_line} ${item.use_case} ${(item.category_path || []).join(' ')}`.toLowerCase();",
        "        const hitText = !keyword || text.includes(keyword);",
        "        const hitStage = stage === '全部' || String(item.use_case || '').includes(stage);",
        "        const hitGrade = grade === '全部' || item.grade === grade;",
        "        const hitDifficulty = difficulty === '全部' || (item.difficulty || '进阶') === difficulty;",
        "        const hitOrigin = origin === '全部' || (item.origin_type || '未知') === origin;",
        "        const hitRisk = risk === '全部' || (item.security_level || '中') === risk;",
        "        return hitText && hitStage && hitGrade && hitDifficulty && hitOrigin && hitRisk;",
        "      });",
        "      resultCount.textContent = String(visible.length);",
        "      marketGrid.innerHTML = '';",
        "      if (!visible.length) {",
        "        marketGrid.innerHTML = '<div class=\\\"card\\\"><p>当前筛选结果为空，调整条件后重试。</p></div>';",
        "        return;",
        "      }",
        "      visible.forEach((item) => {",
        "        const wrapper = document.createElement('div');",
        "        wrapper.innerHTML = cardTemplate(item);",
        "        const card = wrapper.firstElementChild;",
        "        const btn = card.querySelector('.copy');",
        "        if (btn) {",
        "          btn.addEventListener('click', () => copy(btn.dataset.cmd, btn));",
        "        }",
        "        marketGrid.appendChild(card);",
        "      });",
        "    };",
        "",
        "    keywordInput.addEventListener('input', render);",
        "    stageSelect.addEventListener('change', render);",
        "    gradeSelect.addEventListener('change', render);",
        "    difficultySelect.addEventListener('change', render);",
        "    originSelect.addEventListener('change', render);",
        "    riskSelect.addEventListener('change', render);",
        "    render();",
        "  </script>",
        "</body>",
        "</html>",
    ]

    path = out_dir / "market-showcase-v2.html"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def to_market_html(entries: List[Dict], filtered: List[Dict], out_dir: Path):
    market_payload = {
        "items": _market_html_items(entries),
        "filtered": filtered,
    }
    payload = json.dumps(market_payload, ensure_ascii=False).replace("</script>", "<\\/script>")

    lines = [
        "<!doctype html>",
        '<html lang="zh-CN">',
        "<head>",
        "  <meta charset=\"utf-8\" />",
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />",
        "  <title>Research Skills Market / 科研 Skills 市场</title>",
        "  <style>",
        "    :root {",
        "      --bg: #050b17;",
        "      --panel: #111a31;",
        "      --border: #273f70;",
        "      --text: #eaf0ff;",
        "      --muted: #9eb0d5;",
        "      --accent: #72abff;",
        "    }",
        "    * { box-sizing: border-box; }",
        "    body {",
        "      margin: 0;",
        "      min-height: 100vh;",
        "      padding: 24px;",
        "      font-family: 'Noto Sans SC', Inter, 'Segoe UI', Roboto, sans-serif;",
        "      background: radial-gradient(circle at 12% 2%, #1c2f58, var(--bg) 38%),",
        "        linear-gradient(180deg, #050b17 0%, #091127 100%);",
        "      color: var(--text);",
        "    }",
        "    .container { max-width: 1120px; margin: 0 auto; }",
        "    .top {",
        "      border: 1px solid var(--border);",
        "      border-radius: 18px;",
        "      padding: 18px 20px;",
        "      margin-bottom: 16px;",
        "      background: linear-gradient(120deg, rgba(114, 171, 255, .16), rgba(255,255,255,0.05));",
        "    }",
        "    h1 { margin: 0 0 8px; font-size: 34px; letter-spacing: 0.4px; }",
        "    p { margin: 0; color: var(--muted); }",
        "    .toolbar { display: grid; grid-template-columns: 1.2fr 1fr 1fr 1fr 1fr 1fr 1fr; gap: 12px; margin-top: 14px; }",
        "    .toolbar > div label { display:block; margin-bottom: 5px; font-size: 12px; color: var(--muted); }",
        "    .toolbar input, .toolbar select {",
        "      width: 100%;",
        "      padding: 10px 11px;",
        "      border: 1px solid var(--border);",
        "      border-radius: 10px;",
        "      background: #0a1430;",
        "      color: var(--text);",
        "      line-height: 1.2;",
        "    }",
        "    .stats {",
        "      margin-top: 10px;",
        "      display: flex;",
        "      gap: 12px;",
        "      flex-wrap: wrap;",
        "    }",
        "    .stats .item {",
        "      border: 1px solid var(--border);",
        "      border-radius: 10px;",
        "      padding: 10px 14px;",
        "      background: #0a1430;",
        "    }",
        "    .grid {",
        "      margin-top: 14px;",
        "      display: grid;",
        "      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));",
        "      gap: 14px;",
        "    }",
        "    .card {",
        "      border: 1px solid var(--border);",
        "      border-radius: 14px;",
        "      background: var(--panel);",
        "      padding: 14px;",
        "    }",
        "    .card h3 { margin: 0 0 8px; font-size: 18px; line-height: 1.35; }",
        "    .meta { color: var(--muted); font-size: 13px; margin-bottom: 8px; display: flex; gap: 8px; flex-wrap: wrap; }",
        "    .meta span { white-space: nowrap; }",
        "    .tag { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; }",
        "    .good { background: rgba(34,197,94,.2); color: #aefcb8; }",
        "    .warn { background: rgba(245,158,11,.2); color: #fde68a; }",
        "    .actions { margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap; }",
        "    .btn {",
        "      text-decoration: none;",
        "      color: var(--text);",
        "      border: 0;",
        "      border-radius: 10px;",
        "      background: #17316f;",
        "      padding: 8px 10px;",
        "      font-size: 13px;",
        "      cursor: pointer;",
        "      display: inline-block;",
        "    }",
        "    .btn-primary { background: var(--accent); color: #05102f; font-weight: 600; }",
        "    .mini { margin-top: 9px; font-size: 12px; color: var(--muted); }",
        "    ul.steps { margin: 10px 0 0 16px; padding: 0; color: #c6d4f5; font-size: 13px; }",
        "    ul.steps li { margin: 4px 0; }",
        "    code { background: rgba(255,255,255,.08); padding: 2px 5px; border-radius: 6px; }",
        "    .filtered { margin-top: 22px; border: 1px dashed var(--border); border-radius: 12px; padding: 12px 16px; background: rgba(11,23,52,.45); }",
        "    .filtered ul { margin: 8px 0 0 20px; }",
        "    .filtered li { margin: 5px 0; color: #d6e0ff; }",
        "    .origin-official { background: rgba(34,197,94,.2); color: #aefcb8; }",
        "    .origin-non-official { background: rgba(168,85,247,.2); color: #ddd5ff; }",
        "    .origin-unknown { background: rgba(148,163,184,.2); color: #d1d5db; }",
        "    .risk-high { background: rgba(239,68,68,.2); color: #fecaca; }",
        "    .risk-mid { background: rgba(245,158,11,.2); color: #fde68a; }",
        "    .risk-low { background: rgba(34,197,94,.2); color: #aefcb8; }",
        "    .toast {",
        "      position: fixed;",
        "      right: 22px;",
        "      bottom: 22px;",
        "      border: 1px solid var(--border);",
        "      border-radius: 10px;",
        "      background: #111e45;",
        "      padding: 10px 12px;",
        "      opacity: 0;",
        "      transform: translateY(12px);",
        "      transition: .25s;",
        "    }",
        "    .toast.show { opacity: 1; transform: translateY(0); }",
        "    @media (max-width: 860px) {",
        "      .toolbar { grid-template-columns: 1fr 1fr 1fr; }",
        "    }",
        "    @media (max-width: 640px) {",
        "      body { padding: 12px; }",
        "      .toolbar { grid-template-columns: 1fr 1fr; }",
        "      h1 { font-size: 24px; }",
        "      .toolbar input, .toolbar select { font-size: 13px; }",
        "    }",
        "  </style>",
        "</head>",
        "<body>",
        "  <div class=\"container\">",
        "    <header class=\"top\">",
        "      <h1 id=\"title\">Research Skills Market / 科研 Skills 市场</h1>",
        "      <p id=\"subtitle\">Search, filter, copy install commands, and download skill source.</p>",
        "      <div class=\"toolbar\">",
        "        <div>",
        "          <label id=\"langLabel\" for=\"uiLang\">Language / 语言</label>",
        "          <select id=\"uiLang\">",
        "            <option value=\"zh\">中文</option>",
        "            <option value=\"en\">English</option>",
        "          </select>",
        "        </div>",
        "        <div>",
        "          <label id=\"keywordLabel\" for=\"keyword\">Keyword</label>",
        "          <input id=\"keyword\" type=\"text\" placeholder=\"Search by skill name / use case / description\" />",
        "        </div>",
        "        <div>",
        "          <label id=\"stageLabel\" for=\"stage\">Research Stage</label>",
        "          <select id=\"stage\">",
        "            <option value=\"all\">All</option>",
        "          </select>",
        "        </div>",
        "        <div>",
        "          <label id=\"gradeLabel\" for=\"grade\">Readiness</label>",
        "          <select id=\"grade\">",
        "            <option value=\"all\">All</option>",
        "            <option value=\"可直接用\">Ready</option>",
        "            <option value=\"需小改\">Small Tuning</option>",
        "            <option value=\"仅参考\">Reference</option>",
        "          </select>",
        "        </div>",
        "        <div>",
        "          <label id=\"difficultyLabel\" for=\"difficulty\">Difficulty</label>",
        "          <select id=\"difficulty\">",
        "            <option value=\"all\">All</option>",
        "            <option value=\"入门\">Beginner</option>",
        "            <option value=\"进阶\">Advanced</option>",
        "          </select>",
        "        </div>",
        "        <div>",
        "          <label id=\"originLabel\" for=\"origin\">Source</label>",
        "          <select id=\"origin\">",
        "            <option value=\"all\">All</option>",
        "            <option value=\"官方\">Official</option>",
        "            <option value=\"非官方\">Community</option>",
        "            <option value=\"未知\">Unknown</option>",
        "          </select>",
        "        </div>",
        "        <div>",
        "          <label id=\"riskLabel\" for=\"risk\">Risk</label>",
        "          <select id=\"risk\">",
        "            <option value=\"all\">All</option>",
        "            <option value=\"低\">Low</option>",
        "            <option value=\"中\">Medium</option>",
        "            <option value=\"高\">High</option>",
        "          </select>",
        "        </div>",
        "        <div>",
        "          <label id=\"testStatusLabel\" for=\"testStatus\">Test Status</label>",
        "          <select id=\"testStatus\">",
        "            <option value=\"all\">All</option>",
        "            <option value=\"待测试\">待测试</option>",
        "            <option value=\"已测试-通过\">已测试-通过</option>",
        "            <option value=\"已测试-需改进\">已测试-需改进</option>",
        "            <option value=\"已测试-未通过\">已测试-未通过</option>",
        "            <option value=\"已测试-待确认\">已测试-待确认</option>",
        "          </select>",
        "        </div>",
        "      </div>",
        "      <div class=\"stats\">",
        "        <div class=\"item\" id=\"statPublished\">Published: <strong>{0}</strong></div>".format(len(entries)),
        "        <div class=\"item\">Matched: <strong id=\"resultCount\">0</strong></div>",
        "      </div>",
        "    </header>",
        "    <main class=\"grid\" id=\"marketGrid\"></main>",
        "  </div>",
        "  <div id=\"toast\" class=\"toast\">Copied</div>",
        "  <script>",
        f"    const market = {payload};",
        "    const els = {",
        "      lang: document.getElementById('uiLang'),",
        "      title: document.getElementById('title'),",
        "      subtitle: document.getElementById('subtitle'),",
        "      keyword: document.getElementById('keyword'),",
        "      keywordLabel: document.getElementById('keywordLabel'),",
        "      stageLabel: document.getElementById('stageLabel'),",
        "      gradeLabel: document.getElementById('gradeLabel'),",
        "      difficultyLabel: document.getElementById('difficultyLabel'),",
        "      originLabel: document.getElementById('originLabel'),",
        "      riskLabel: document.getElementById('riskLabel'),",
        "      testStatusLabel: document.getElementById('testStatusLabel'),",
        "      langLabel: document.getElementById('langLabel'),",
        "      stage: document.getElementById('stage'),",
        "      grade: document.getElementById('grade'),",
        "      difficulty: document.getElementById('difficulty'),",
        "      origin: document.getElementById('origin'),",
        "      risk: document.getElementById('risk'),",
        "      testStatus: document.getElementById('testStatus'),",
        "      statPublished: document.getElementById('statPublished'),",
        "      resultCount: document.getElementById('resultCount'),",
        "      marketGrid: document.getElementById('marketGrid'),",
        "      toast: document.getElementById('toast'),",
        "    };",
        "    const i18n = {",
        "      zh: {",
        "        title: '科研 Skills 市场',",
        "        subtitle: '可搜索、筛选、复制安装命令并直接下载 Skill 源码。支持官方/非官方与安全风险筛选。',",
        "        langLabel: '语言',",
        "        keywordLabel: '关键词',",
        "        keywordPlaceholder: '输入技能名 / 场景 / 简介关键词',",
        "        stageLabel: '流程场景',",
        "        gradeLabel: '评分等级',",
        "        difficultyLabel: '使用门槛',",
        "        originLabel: '来源',",
        "        riskLabel: '安全风险',",
        "        testStatusLabel: '测试状态',",
        "        all: '全部',",
        "        stageMap: {",
        "          文献检索: '文献检索',",
        "          数据分析: '数据分析',",
        "          实验设计: '实验设计',",
        "          论文写作: '论文写作',",
        "          可视化: '可视化',",
        "          知识管理: '知识管理',",
        "          待补充: '待补充',",
        "        },",
        "        gradeMap: { '可直接用': '可直接用', '需小改': '需小改', '仅参考': '仅参考' },",
        "        difficultyMap: { 入门: '入门', 进阶: '进阶' },",
        "        originMap: { 官方: '官方', 非官方: '非官方', 未知: '未知' },",
        "        riskMap: { 低: '低', 中: '中', 高: '高' },",
        "        statPublished: '可上架',",
        "        statMatched: '当前结果',",
        "        buttons: {",
        "          viewSource: '查看源码',",
        "          openPage: '打开技能页',",
        "          copy: '复制安装命令',",
        "          copied: '已复制',",
        "          copyFailed: '复制失败',",
        "          noCmd: '请按仓库说明配置依赖。',",
        "        },",
        "        labels: {",
        "          scene: '场景',",
        "          difficulty: '门槛',",
        "          risk: '风险',",
        "        },",
        "        empty: '当前筛选结果为空，调整条件后重试。',",
        "        toast: '已复制安装命令',",
        "        filteredReasonFallback: '不推荐',",
        "        testStatusMap: {",
        "          '待测试': '待测试',",
        "          '已测试-通过': '已测试-通过',",
        "          '已测试-需改进': '已测试-需改进',",
        "          '已测试-未通过': '已测试-未通过',",
        "          '已测试-待确认': '已测试-待确认',",
        "        },",
        "      },",
        "      en: {",
        "        title: 'Research Skills Market',",
        "        subtitle: 'Search, filter, copy install commands, and download skill source.',",
        "        langLabel: 'Language',",
        "        keywordLabel: 'Keyword',",
        "        keywordPlaceholder: 'Search by skill name / use case / description',",
        "        stageLabel: 'Research Stage',",
        "        gradeLabel: 'Readiness',",
        "        difficultyLabel: 'Difficulty',",
        "        originLabel: 'Source',",
        "        riskLabel: 'Risk',",
        "        testStatusLabel: 'Test Status',",
        "        all: 'All',",
        "        stageMap: {",
        "          文献检索: 'Literature Search',",
        "          数据分析: 'Data Analysis',",
        "          实验设计: 'Experiment Design',",
        "          论文写作: 'Paper Writing',",
        "          可视化: 'Visualization',",
        "          知识管理: 'Knowledge Management',",
        "          待补充: 'To be categorized',",
        "        },",
        "        gradeMap: { '可直接用': 'Ready', '需小改': 'Small Tuning', '仅参考': 'Reference' },",
        "        difficultyMap: { 入门: 'Beginner', 进阶: 'Advanced' },",
        "        originMap: { 官方: 'Official', 非官方: 'Community', 未知: 'Unknown' },",
        "        riskMap: { 低: 'Low', 中: 'Medium', 高: 'High' },",
        "        statPublished: 'Published',",
        "        statMatched: 'Matched',",
        "        buttons: {",
        "          viewSource: 'View Source',",
        "          openPage: 'Open Skill Page',",
        "          copy: 'Copy install command',",
        "          copied: 'Copied',",
        "          copyFailed: 'Copy failed',",
        "          noCmd: 'Please follow repository setup instructions.',",
        "        },",
        "        labels: {",
        "          scene: 'Stage',",
        "          difficulty: 'Difficulty',",
        "          risk: 'Risk',",
        "        },",
        "        empty: 'No result for current filters.',",
        "        toast: 'Copied',",
        "        filteredReasonFallback: 'Not recommended',",
        "        testStatusMap: {",
        "          '待测试': 'Pending',",
        "          '已测试-通过': 'Passed',",
        "          '已测试-需改进': 'Needs Improvement',",
        "          '已测试-未通过': 'Failed',",
        "          '已测试-待确认': 'Review Needed',",
        "        },",
        "      },",
        "    };",
        "    const allStages = Array.from(new Set(",
        "      market.items.flatMap((item) => String(item.use_case_zh || item.use_case || '').split(',').map((s) => s.trim()).filter(Boolean))",
        "    ));",
        "    const escapeHtml = (value) => String(value ?? '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('\"', '&quot;').replaceAll(\"'\", '&#39;');",
        "    const getText = (item, key, lang) => {",
        "      if (lang === 'en') {",
        "        return item[`${key}_en`] || item[`${key}_zh`] || item[key] || '';",
        "      }",
        "      return item[`${key}_zh`] || item[`${key}_en`] || item[key] || '';",
        "    };",
        "    const originClass = (v) => v === '官方' ? 'origin-official' : v === '非官方' ? 'origin-non-official' : 'origin-unknown';",
        "    const riskClass = (v) => v === '低' ? 'risk-low' : v === '中' ? 'risk-mid' : 'risk-high';",
        "    const testStatusClass = (v) => {",
        "      if (!v || v.includes('待测试')) return 'status-pending';",
        "      if (v.includes('通过')) return 'status-ok';",
        "      if (v.includes('未通过')) return 'status-fail';",
        "      return 'status-warn';",
        "    };",
        "    const setText = (el, val) => { if (el) el.textContent = val; };",
        "    const fillStageOptions = (lang) => {",
        "      const t = i18n[lang];",
        "      const selected = els.stage.value || 'all';",
        "      const options = allStages.map((s) => `<option value=\"${escapeHtml(s)}\">${escapeHtml(t.stageMap[s] || s)}</option>`).join('');",
        "      els.stage.innerHTML = `<option value=\"all\">${escapeHtml(t.all)}</option>` + options;",
        "      if (Array.from(els.stage.options).some((o) => o.value === selected)) {",
        "        els.stage.value = selected;",
        "      }",
        "    };",
        "    const setLang = (lang) => {",
        "      const t = i18n[lang] || i18n.zh;",
        "      els.lang.value = lang === 'en' ? 'en' : 'zh';",
        "      els.title.textContent = t.title;",
        "      els.subtitle.textContent = t.subtitle;",
        "      document.documentElement.lang = lang === 'en' ? 'en-US' : 'zh-CN';",
        "      setText(els.langLabel, t.langLabel);",
        "      setText(els.keywordLabel, t.keywordLabel);",
        "      setText(els.stageLabel, t.stageLabel);",
        "      setText(els.gradeLabel, t.gradeLabel);",
        "      setText(els.difficultyLabel, t.difficultyLabel);",
        "      setText(els.originLabel, t.originLabel);",
        "      setText(els.riskLabel, t.riskLabel);",
        "      setText(els.testStatusLabel, t.testStatusLabel);",
        "      els.keyword.placeholder = t.keywordPlaceholder;",
        "      els.statPublished.innerHTML = `${t.statPublished}: <strong>${market.items.length}</strong>`;",
        "      Array.from(els.grade.options).forEach((o) => {",
        "        o.textContent = (o.value === 'all') ? t.all : (t.gradeMap[o.value] || o.textContent);",
        "      });",
        "      Array.from(els.difficulty.options).forEach((o) => {",
        "        o.textContent = (o.value === 'all') ? t.all : (t.difficultyMap[o.value] || o.textContent);",
        "      });",
        "      Array.from(els.origin.options).forEach((o) => {",
        "        o.textContent = (o.value === 'all') ? t.all : (t.originMap[o.value] || o.textContent);",
        "      });",
        "      Array.from(els.risk.options).forEach((o) => {",
        "        o.textContent = (o.value === 'all') ? t.all : (t.riskMap[o.value] || o.textContent);",
        "      });",
        "      Array.from(els.testStatus.options).forEach((o) => {",
        "        o.textContent = (o.value === 'all') ? t.all : (t.testStatusMap[o.value] || t.testStatusMap[o.textContent] || o.textContent);",
        "      });",
        "      fillStageOptions(lang);",
        "    };",
        "    const cardTemplate = (item, lang) => {",
        "      const t = i18n[lang] || i18n.zh;",
        "      const grade = item.grade || '需小改';",
        "      const difficulty = (item.difficulty || item.difficulty_zh || item.difficulty_en || '进阶');",
        "      const origin = item.origin_type || '未知';",
        "      const risk = item.security_level || '中';",
        "      const testStatus = item.test_status || '待测试';",
        "      const copyCmdRaw = item.git_clone || item.source_url || '';",
        "      const cloneCmd = escapeHtml(copyCmdRaw);",
        "      const source = escapeHtml(item.source_url || '');",
        "      const repo = escapeHtml(item.repo_url || '');",
        "      const hasSource = source && source !== '#';",
        "      const hasRepo = repo && repo !== source;",
        "      const sourceButton = hasSource ? `<a class=\\\"btn\\\" href=\\\"${source}\\\" target=\\\"_blank\\\">${t.buttons.openPage}</a>` : '';",
        "      const repoButton = hasRepo ? `<a class=\\\"btn btn-primary\\\" href=\\\"${repo}\\\" target=\\\"_blank\\\">${t.buttons.viewSource}</a>` : '';",
        "      return `<article class=\\\"card\\\">",
        "        <h3>${escapeHtml(getText(item, 'title', lang))}</h3>",
        "        <div class=\\\"meta\\\"><span class=\\\"tag ${grade === '可直接用' ? 'good' : 'warn'}\\\">${escapeHtml(t.gradeMap[grade] || grade)}</span><span class=\\\"tag ${originClass(origin)}\\\">${escapeHtml(t.originMap[origin] || origin)}</span><span class=\\\"tag ${riskClass(risk)}\\\">${escapeHtml(t.labels.risk)}:${escapeHtml(risk)}</span><span class=\\\"tag ${testStatusClass(testStatus)}\\\">${escapeHtml((t.testStatusMap && t.testStatusMap[testStatus]) || testStatus)}</span><span>${escapeHtml(t.labels.scene)}:${escapeHtml(t.stageMap[item.use_case_zh?.split(',')[0]] || item.use_case_zh || item.use_case || '')}</span><span>${escapeHtml(t.labels.difficulty)}:${escapeHtml(t.difficultyMap[difficulty] || difficulty)}</span></div>",
        "        <p>${escapeHtml(getText(item, 'one_line', lang))}</p>",
        "        <div class=\\\"actions\\\">",
        "          ${repoButton}",
        "          ${sourceButton}",
        "          <button class=\\\"btn copy\\\" data-cmd=\\\"${cloneCmd}\\\">${t.buttons.copy}</button>",
        "        </div>",
        "      </article>`;",
        "    };",
        "    const applyFilter = () => {",
        "      const lang = els.lang.value || 'zh';",
        "      const keyword = els.keyword.value.trim().toLowerCase();",
        "      const state = {",
        "        stage: els.stage.value,",
        "        grade: els.grade.value,",
        "        difficulty: els.difficulty.value,",
        "        origin: els.origin.value,",
        "        risk: els.risk.value,",
        "        testStatus: els.testStatus.value,",
        "      };",
        "      const visible = market.items.filter((item) => {",
        "        const text = `${getText(item, 'title', lang)} ${getText(item, 'one_line', lang)} ${getText(item, 'use_case', lang)} ${(item.category_path || []).join(' ')}`.toLowerCase();",
        "        const byKeyword = !keyword || text.includes(keyword);",
        "        const byStage = state.stage === 'all' || String(item.use_case_zh || '').split(',').map((s) => s.trim()).includes(state.stage);",
        "        const byGrade = state.grade === 'all' || item.grade === state.grade;",
        "        const byDifficulty = state.difficulty === 'all' || (item.difficulty || item.difficulty_zh || item.difficulty_en || '') === state.difficulty;",
        "        const byOrigin = state.origin === 'all' || (item.origin_type || '未知') === state.origin;",
        "        const byRisk = state.risk === 'all' || (item.security_level || '中') === state.risk;",
        "        const byTestStatus = state.testStatus === 'all' || (item.test_status || '待测试') === state.testStatus;",
        "        return byKeyword && byStage && byGrade && byDifficulty && byOrigin && byRisk && byTestStatus;",
        "      });",
        "      els.resultCount.textContent = String(visible.length);",
        "      els.marketGrid.innerHTML = '';",
        "      if (!visible.length) {",
        "        els.marketGrid.innerHTML = `<div class=\\\"card\\\"><p>${escapeHtml(i18n[lang].empty)}</p></div>`;",
        "      } else {",
        "        visible.forEach((item) => {",
        "          const node = document.createElement('div');",
        "          node.innerHTML = cardTemplate(item, lang);",
        "          const card = node.firstElementChild;",
        "          const btn = card.querySelector('.copy');",
        "          if (btn) {",
        "            btn.addEventListener('click', () => {",
        "              if (!btn.dataset.cmd) {",
        "                btn.textContent = i18n[lang].buttons.noCmd;",
        "                return;",
        "              }",
        "              navigator.clipboard.writeText(btn.dataset.cmd).then(() => {",
        "                btn.textContent = i18n[lang].buttons.copied;",
        "                els.toast.textContent = i18n[lang].toast;",
        "                els.toast.classList.add('show');",
        "                setTimeout(() => {",
        "                  btn.textContent = i18n[lang].buttons.copy;",
        "                  els.toast.classList.remove('show');",
        "                }, 1200);",
        "              }).catch(() => {",
        "                btn.textContent = i18n[lang].buttons.copyFailed;",
        "              });",
        "            });",
        "          }",
        "          els.marketGrid.appendChild(card);",
        "        });",
        "      }",
        "    };",
        "    const render = () => {",
        "      const lang = els.lang.value || 'zh';",
        "      setLang(lang);",
        "      applyFilter();",
        "    };",
        "    const storedLang = localStorage.getItem('market_lang');",
        "    const browser = (navigator.language || navigator.userLanguage || '').toLowerCase();",
        "    const initialLang = storedLang === 'en' ? 'en' : storedLang === 'zh' ? 'zh' : (browser.startsWith('en') ? 'en' : 'zh');",
        "    fillStageOptions(initialLang);",
        "    setLang(initialLang);",
        "    render();",
        "    els.lang.addEventListener('change', () => {",
        "      const lang = els.lang.value;",
        "      localStorage.setItem('market_lang', lang);",
        "      fillStageOptions(lang);",
        "      render();",
        "    });",
        "    els.keyword.addEventListener('input', render);",
        "    els.stage.addEventListener('change', render);",
        "    els.grade.addEventListener('change', render);",
        "    els.difficulty.addEventListener('change', render);",
        "    els.origin.addEventListener('change', render);",
        "    els.risk.addEventListener('change', render);",
        "    els.testStatus.addEventListener('change', render);",
      "  </script>",
        "</body>",
        "</html>",
    ]

    path = out_dir / "market-showcase-v2.html"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main():
    args = parse_args()
    llm_classifier_config = _build_llm_classifier_config(args)
    if llm_classifier_config["enabled"] and not llm_classifier_config.get("api_key"):
        if llm_classifier_config.get("only"):
            raise RuntimeError("[Classifier] --llm-only-classifier enabled but no LLM API key found.")
        print("[Classifier] No LLM API key provided; fallback to keyword-only classification.")

    if args.update_test_status_only:
        curated_path = Path(args.curated_market)
        report_path = Path(args.test_report)
        curated = json.loads(curated_path.read_text(encoding="utf-8")) if curated_path.exists() else None
        report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else None
        if not curated:
            raise FileNotFoundError(f"curated market file not found: {curated_path}")
        if not report:
            raise FileNotFoundError(f"test report file not found: {report_path}")
        entries = curated.get("entries", [])
        filtered = curated.get("filtered", [])
        if not isinstance(entries, list):
            raise ValueError("curated file format invalid: expected entries list.")
        result = _apply_test_report(entries, report)
        curated_path.write_text(json.dumps({"entries": entries, "filtered": filtered}, ensure_ascii=False, indent=2), encoding="utf-8")
        md_path = to_market_md([], entries, filtered, DOCS_DIR)
        html_path = to_market_html(entries, filtered, DOCS_DIR)
        print(
            json.dumps(
                {
                    "run_mode": "update_test_status_only",
                    "curated_market": str(curated_path),
                    "test_report": str(report_path),
                    "updated": result["updated"],
                    "total": result["total"],
                    "md_path": str(md_path),
                    "html_path": str(html_path),
                },
                ensure_ascii=False,
            )
        )
        return

    run_id = str(uuid.uuid4())
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_RUN.mkdir(parents=True, exist_ok=True)

    if args.source_file:
        seed_items = load_seed_sources(args.source_file, args.source_format)
        if not seed_items:
            print("WARN: source file(s) loaded but no valid entries; fallback to built-in seed.")
    else:
        seed_items = [normalize_seed_item(item, default_source="raw_seed") for item in RAW_SEED]

    if args.max_items:
        seed_items = seed_items[: args.max_items]

    if not seed_items:
        raise RuntimeError("no seed inputs available")

    # Step 1) Scout (in parallel subprocesses)
    scout_chunks = list(chunks(seed_items, max(args.scout_chunk, 1)))
    raw_candidates = []
    scout_workers = max(1, args.scout_workers)
    if scout_workers == 1:
        for idx, chunk in enumerate(scout_chunks):
            raw_candidates.extend(run_scout(f"Scout-{idx:03d}", chunk, run_id))
    else:
        try:
            with ProcessPoolExecutor(max_workers=scout_workers) as executor:
                futures = [executor.submit(run_scout, f"Scout-{idx:03d}", chunk, run_id) for idx, chunk in enumerate(scout_chunks)]
                for fut in futures:
                    raw_candidates.extend(fut.result())
        except Exception as err:
            print(f"[Scout] process pool unavailable, fallback to threads: {err}")
            with ThreadPoolExecutor(max_workers=scout_workers) as executor:
                futures = [executor.submit(run_scout, f"Scout-{idx:03d}", chunk, run_id) for idx, chunk in enumerate(scout_chunks)]
                for fut in futures:
                    raw_candidates.extend(fut.result())

    # 去重
    raw_candidates = dedup_candidates(raw_candidates, prefer_non_official=args.non_official_priority)

    # Step 2) Classifier (parallel subprocesses)
    classifier_workers = max(1, args.classifier_workers)
    if llm_classifier_config.get("enabled", False):
        print("[Classifier] LLM enabled: running classifier in parallel if workers > 1.")
    classifier_fn = partial(run_classifier, llm_config=llm_classifier_config)
    if classifier_workers == 1:
        classified_list = [classifier_fn(item) for item in raw_candidates]
    else:
        with ThreadPoolExecutor(max_workers=classifier_workers) as executor:
            classified_list = list(executor.map(classifier_fn, raw_candidates))

    # 关联候选 -> 分类
    candidate_map = {c["id"]: c for c in raw_candidates}
    classified_map = {
        c["candidate_id"]: {**candidate_map[c["candidate_id"]], **c} for c in classified_list
    }

    eval_payload = [(candidate_map[ev["candidate_id"]], ev) for ev in classified_list]

    # Step 3) Evaluator (parallel subprocesses)
    evaluator_workers = max(1, args.evaluator_workers)
    if evaluator_workers == 1:
        evaluations = [_evaluate_pair(pair) for pair in eval_payload]
    else:
        try:
            with ProcessPoolExecutor(max_workers=evaluator_workers) as executor:
                evaluations = list(executor.map(_evaluate_pair, eval_payload))
        except Exception as err:
            print(f"[Evaluator] process pool unavailable, fallback to threads: {err}")
            with ThreadPoolExecutor(max_workers=evaluator_workers) as executor:
                evaluations = list(executor.map(_evaluate_pair, eval_payload))

    # Step 4) Curator
    entries, filtered = run_curation(
        evaluations,
        classified_map,
        resolve_repo_links=args.resolve_repo_links,
        repo_resolve_timeout=args.repo_resolve_timeout,
        repo_resolve_limit=args.repo_resolve_limit,
    )

    # Step 5) Tester
    tester_report: Dict[str, Any] = {
        "verifier": "Tester",
        "run_at": str(date.today()),
        "test_scope": "Tester skipped (publish-before-test/skip-tester)",
        "items": [],
        "summary": {
            "items_total": len(entries),
            "tested": 0,
            "overall_pass_rate": 0,
            "comment": "本轮未执行真实测试，请使用待测标签，后续可补测。",
        },
    }
    if not args.publish_before_test and not args.skip_tester:
        tester_report = run_tester(entries, top_n=args.test_top, workers=args.tester_workers)
    else:
        publish_state = "publish-before-test" if args.publish_before_test else "skip-tester"
        print(f"[Tester] skipped: {publish_state}")

    # Step 6) 输出
    raw_out = {
        "agent": "Scout",
        "run_id": run_id,
        "raw_count": len(raw_candidates),
        "items": raw_candidates,
    }
    classified_out = {
        "agent": "Classifier",
        "run_id": run_id,
        "items": [
            {
                **classified_map[c["candidate_id"]],
                "is_research_related": c["is_research_related"],
                "research_stage": c["research_stages"],
                "domain": c["research_domains"],
                "fit_reason": c["fit_reason"],
                "reject_reason": c["reject_reason"],
            }
            for c in classified_list
        ],
    }
    evaluation_out = {
        "agent": "Evaluator",
        "run_id": run_id,
        "items": evaluations,
    }

    (DATA_DIR / "raw_candidates_v2.json").write_text(json.dumps(raw_out, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "classified_pool_v2.json").write_text(json.dumps(classified_out, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "evaluation_cards_v2.json").write_text(json.dumps(evaluation_out, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "curated_market_v2.json").write_text(json.dumps({"entries": entries, "filtered": filtered}, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "test_report_v2.json").write_text(json.dumps(tester_report, ensure_ascii=False, indent=2), encoding="utf-8")

    md_path = to_market_md(classified_list, entries, filtered, DOCS_DIR)
    html_path = to_market_html(entries, filtered, DOCS_DIR)

    origin_counter = Counter([c.get("origin_type", "未知") for c in classified_list])
    summary = {
        "run_id": run_id,
        "raw_count": len(raw_candidates),
        "research_count": len([i for i in classified_list if i["is_research_related"]]),
        "published_count": len(entries),
        "filtered_count": len(filtered),
        "tester_status": "skipped" if (args.publish_before_test or args.skip_tester) else "done",
        "origin_counter": dict(origin_counter),
        "md_path": str(md_path),
        "html_path": str(html_path),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
