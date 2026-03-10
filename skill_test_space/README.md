# Skill Test Space

Goal: keep an isolated area to evaluate high-quality skills that can be used without complex API keys.

This space is independent from the main repo code and stores:
- Candidate selection data from local crawling cache
- Skill package snapshots extracted from official/crawled archives
- Reproducible test scripts and report output

Current target (daily 3-skill format):
1. Find Skills (`find-skills`) — discovery utility for other skills
2. Weather (`weather`) — no-key weather data query
3. Polymarket (`polymarketodds`) — prediction-market odds and calendars

Why this set:
- No explicit API-key requirement in official metadata/SKILL docs
- Strong signals from official/crawled quality fields (`stars`, install/download count, metadata)
- Each can be exercised with short commands and plain network access

## Data used for selection

`skill_test_space/tmp_candidates.json`

Contains crawled candidates with stars/downloads from
`data/raw/clawhub/clawhub_official_downloads_full_with_links_api_only_enriched_v5.jsonl`

## How to run the full daily test

```bash
cd /Users/yuwen/work/research-skills-market/skill_test_space
bash run_daily3_skill_tests.sh
bash run_experience_scenarios.sh
bash run_openclaw_conversation_scenarios.sh
```

`run_daily3_skill_tests.sh` prints 基础冒烟结果，`run_experience_scenarios.sh` 输出完整体验场景报告，`run_openclaw_conversation_scenarios.sh` 输出 OpenClaw 对话场景报告。三者都会写入 markdown 到
`skill_test_space/reports/`.

体验场景报告默认文件名:
- `skill_test_space/reports/$(date +%F)_experience_report.md`

## How quality was validated

1. Confirm the local/official page text explicitly says no API key or keyless operation.
2. Execute at least one representative command (or request) with empty env (no API tokens configured).
3. Record command output + exit code + pass/fail into a daily report file.
4. Keep one report per date under `skill_test_space/reports/`.

Use the latest report files for proof:
- 基础冒烟：`skill_test_space/reports/$(date +%F).md`
- 体验场景：`skill_test_space/reports/$(date +%F)_experience_report.md`
- OpenClaw 对话场景：`skill_test_space/reports/$(date +%F)_openclaw_conversation_report.md`

Current latest sample reports:
- `skill_test_space/reports/2026-03-02.md`
- `skill_test_space/reports/2026-03-02_experience_report.md`
- `skill_test_space/reports/2026-03-02_openclaw_conversation_report.md`
