#!/usr/bin/env python3
"""Generate a minimal market showcase markdown from prepared sample JSON files."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "sample_raw_candidates.json"
CLASSIFIED = ROOT / "data" / "sample_classified_pool.json"
EVAL = ROOT / "data" / "sample_evaluation_cards.json"
OUT = ROOT / "docs" / "market-showcase-runtime.md"


def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def grade_to_level(grade):
    return {
        "可直接用": "高",
        "需小改": "中",
        "仅参考": "较低",
        "不推荐": "低",
    }.get(grade, "待定")


def summarize_stages(item):
    stages = item.get("research_stage") or []
    return ", ".join(stages) if stages else "未标注"


def summarize_domains(item):
    domains = item.get("domain") or []
    return ", ".join(domains) if domains else "未标注"


def main():
    raw = {i["id"]: i for i in load(RAW)["items"]}
    classified = {i["candidate_id"]: i for i in load(CLASSIFIED)["items"]}
    evals = {i["classified_id"]: i for i in load(EVAL)["items"]}

    lines = [
        "# 科研Skills市场展示（Runtime）",
        "",
        "基于当前样例数据自动生成。",
        "",
        "## 可发布项目",
        "",
    ]

    for cid, item in classified.items():
        if not item.get("is_research_related"):
            continue
        e = evals.get(cid, {})
        grade = e.get("grade", "未评估")
        src = raw.get(cid, {})
        lines.extend(
            [
                f"### {src.get('name', cid)}",
                f"- 链接：{src.get('url', 'N/A')}",
                f"- 评估：{grade}（{grade_to_level(grade)}）",
                f"- 研究阶段：{summarize_stages(item)}",
                f"- 适用学科：{summarize_domains(item)}",
                f"- 简介：{src.get('desc_raw', '')}",
                "",
            ]
        )

    lines.extend(["## 过滤项", "",])
    for cid, item in classified.items():
        if item.get("is_research_related"):
            continue
        src = raw.get(cid, {})
        lines.append(f"- {src.get('name', cid)}：{item.get('reject_reason', '未通过研究相关性判定')}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {OUT}")


if __name__ == "__main__":
    main()
