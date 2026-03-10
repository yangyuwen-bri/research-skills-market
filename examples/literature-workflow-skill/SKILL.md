---
name: literature-workflow
description: Use this skill when the user asks to search papers, screen relevance, synthesize findings, or draft literature review sections with citations. Do not use for unrelated coding/debug tasks.
---

# Literature Workflow

## When To Use
- The task requires literature retrieval, relevance screening, evidence synthesis, or citation-aware writing.

## When Not To Use
- The task is pure coding/debugging with no research-literature objective.
- The user only asks for generic brainstorming without source grounding.

## Required Inputs
- Research question
- Scope (domain/time range/language)
- Output format (summary table, bullet review, or draft section)
- Citation style (APA/MLA/GB/T or project-specific)

## Workflow

### Phase 1: Retrieval
- Build 2-3 query variants from the research question.
- Retrieve candidate sources from requested databases.
- Keep a bounded candidate pool to control noise.

### Phase 2: Screening
- Apply inclusion criteria: relevance, recency, methodological quality.
- Apply exclusion criteria: duplicates, off-topic, weak provenance.
- Record screening reasons for traceability.

### Phase 3: Synthesis
- Cluster findings by theme/method/result.
- Identify consensus, disagreements, and evidence gaps.
- Distinguish evidence from inference explicitly.

### Phase 4: Output
- Produce structured result with required fields.
- Attach citations near claims, not only at the end.
- Mark uncertainty where evidence is insufficient.

## Output Contract
Always include:
- `question`
- `scope`
- `search_strategy`
- `included_sources`
- `key_findings`
- `limitations`
- `research_gaps`
- `citations`

## Failure Handling
- If source quality is low: state this clearly and reduce claim strength.
- If sources conflict: present both sides and note confidence.
- If evidence is sparse: provide next-step retrieval plan instead of over-claiming.

## Quality Guardrails
- No fabricated citations.
- No claim without source support.
- No silent scope drift.

## Optional Scripts
- Run `scripts/* --help` first before reading script internals.
- Prefer deterministic scripts for repetitive formatting and validation.

## Optional References
- `references/screening_rules.md` for inclusion/exclusion criteria.
- `references/citation_style.md` for citation formatting rules.
