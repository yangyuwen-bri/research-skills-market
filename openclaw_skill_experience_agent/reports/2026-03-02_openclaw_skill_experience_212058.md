# OpenClaw 对话式 Skill 体验日报
生成时间：2026-03-02 21:20:58
目标：独立 agent 每日自动测试 10 个 skill 的对话可用性

## 说明
- 每个案例先用“用户口播问题”模拟真实对话入口。
- 评估结果优先看“是否能直接落地”，再看降级可解释性。

## 执行汇总
- 测试项：10
- 通过：7
- 降级：3
- 失败：0
- 情景得分：38 / 44

### S01 | find-skills | PASS
**场景**：能力发现
**能力**：按意图检索可安装技能并给出安装路径与可选方案
**用户发言**：我想给 OpenClaw 增加测试相关能力，帮我先找 3 个可直接装的技能并给安装方式。
**参考回复方向**：我先按“测试能力”关键词做一次检索，先给你 3 个可用候选和安装命令。你要我直接装哪个我就继续执行。
**评分**：5 / 5
- 结论：核心链路可直接交付。
- Probe `skills_cli_find`
  - 命令：`npx --yes skills ls -g | head -n 20`
  - 退出码：0（耗时 2.2s）
  - 可选项：否
  - 输出片段：
    ```
Global Skills

apify-twitter ~/.openclaw/skills/apify-twitter
  Agents: OpenClaw
gsdata ~/.openclaw/skills/gsdata
  Agents: OpenClaw
moltbook ~/.openclaw/skills/moltbook
  Agents: OpenClaw
patent-disclosure-writer ~/.openclaw/skills/patent-disclosure-writer-community
  Agents: OpenClaw
patent-pro ~/.openclaw/skills/patent-pro
  Agents: OpenClaw
Patent Scanner ~/.openclaw/skills/patent-scanner-community
  Agents: OpenClaw
Patent Validator ~/.openclaw/skills/patent-validator-community
  Agents: OpenClaw
figma ~/.codex/skills/figma
  Agents: Codex
figma-implement-design ~/.codex/skills/figma-implement-design
  Agents: Codex
    ```

### S02 | weather | PASS
**场景**：信息查询
**能力**：在对话中基于公开天气源给出即时天气结论并支持降级回退
**用户发言**：我刚到伦敦，今天要不要带伞？直接给我一句天气结论。
**参考回复方向**：我先查伦敦实时天气，再给你一句结论：是否有降雨、体感温度和风速，方便你快速决策。
**评分**：5 / 5
- 结论：核心链路可直接交付。
- Probe `weather_probe`
  - 命令：`python3 runtime_scripts/weather/weather_probe.py`
  - 退出码：0（耗时 15.0s）
  - 可选项：否
  - 输出片段：
    ```
wttr_primary_fail fallback_to_open_meteo
open_meteo_fallback_ok temperature=14.4 wind=14.8
    ```

### S03 | github | DEGRADED
**场景**：代码协作
**能力**：查 CI/Action 失败路径并给出最短故障排查链路
**用户发言**：我想快速看下项目最近 CI 失败的上下文，先给我最短链路。
**参考回复方向**：我先确认 `gh` 是否就绪；可以直接用 `gh run list` 与 `gh run view --log-failed` 定位失败摘要，之后给你建议复测步骤。
**评分**：3 / 5
- 结论：技能可用，但存在外部依赖/环境约束，建议先补环境后再用。
- Probe `github_binary`
  - 命令：`command -v gh >/dev/null`
  - 退出码：1（耗时 0.0s）
  - 可选项：是
  - 备注：退出码不符: expect=0, actual=1
  - 输出片段：
    （无）
- Probe `github_doc`
  - 命令：`grep -n "Interact with GitHub" references/skill_pages/github.md | head -n 1`
  - 退出码：0（耗时 0.0s）
  - 可选项：否
  - 输出片段：
    ```
3:description: "Interact with GitHub using the \`gh\` CLI. Use \`gh issue\`, \`gh pr\`, \`gh run\`, and \`gh api\` for issues, PRs, CI runs, and advanced queries."
    ```

### S04 | ontology | PASS
**场景**：知识结构化
**能力**：用本地知识图谱维护实体与关系，支持创建和检索
**用户发言**：我想建立一个名为『Q1技能体验』的项目节点，并关联负责人『我』，然后列出该类型实体。
**参考回复方向**：我先建立项目和负责人节点，再把“负责人”关系写入图谱，最后给你回传创建结果。
**评分**：5 / 5
- 结论：核心链路可直接交付。
- Probe `ontology_create_node`
  - 命令：`cd runtime_scripts/ontology && python3 ontology.py create --type Project --props '{"name":"Q1技能体验","status":"active"}' | head -n 40`
  - 退出码：0（耗时 0.1s）
  - 可选项：否
  - 输出片段：
    ```
{
  "id": "proj_c2e203da",
  "type": "Project",
  "properties": {
    "name": "Q1\u6280\u80fd\u4f53\u9a8c",
    "status": "active"
  },
  "created": "2026-03-02T13:20:31.048479+00:00",
  "updated": "2026-03-02T13:20:31.048479+00:00"
}
    ```
- Probe `ontology_query`
  - 命令：`cd runtime_scripts/ontology && python3 ontology.py query --type Project --where '{"status":"active"}' | head -n 80`
  - 退出码：0（耗时 0.1s）
  - 可选项：否
  - 输出片段：
    ```
[
  {
    "id": "proj_44f334fe",
    "type": "Project",
    "properties": {
      "name": "Q1\u6280\u80fd\u4f53\u9a8c",
      "status": "active"
    },
    "created": "2026-03-02T12:44:33.159728+00:00",
    "updated": "2026-03-02T12:44:33.159728+00:00"
  },
  {
    "id": "proj_3c200304",
    "type": "Project",
    "properties": {
      "name": "Q1\u6280\u80fd\u4f53\u9a8c",
      "status": "active"
    },
    "created": "2026-03-02T12:44:57.713387+00:00",
    "updated": "2026-03-02T12:44:57.713387+00:00"
  },
  {
    "id": "proj_b099ccb0",
    "type": "Project",
    "properties": {
      "name": "Q1\u6280\u80fd\u4f53\u9a8c",
      "status": "active"
    },
    "created": "2026-03-02T12:45:57.306709+00:00",
    "updated": "2026-03-02T12:45:57.306709+00:00"
  },
  {
    "id": "proj_f3dd5cc6",
    "type": "Project",
    "properties": {
      "name": "Q1\u6280\u80fd\u4f53\u9a8c",
      "status": "active"
    },
    "created": "2026-03-02T12:48:10.331791+00:00",
    "updated": "2026-03-02T12:48:10.331791+00:00"
  },
  {
    "id": "proj_c2e203da",
    "type": "Project",
    "properties": {
      "name": "Q1\u6280\u80fd\u4f53\u9a8c",
      "status": "active"
    },
    "created": "2026-03-02T13:20:31.048479+00:00",
    "updated": "2026-03-02T13:20:31.048479+00:00"
  }
]
    ```

### S05 | agent-browser | DEGRADED
**场景**：网页动作
**能力**：对网页执行器（按钮、内容抓取、流程动作）提供可落地指导
**用户发言**：我想给页面按钮做一次自动化操作演练，先给我能力边界和安装前置。
**参考回复方向**：这类网页自动化能力可落地，先确认本地 `agent-browser` 与 `node/npm`，我会给你安装与回退步骤。
**评分**：2 / 4
- 结论：技能可用，但存在外部依赖/环境约束，建议先补环境后再用。
- Probe `agent_browser_cmd`
  - 命令：`command -v agent-browser >/dev/null`
  - 退出码：1（耗时 0.0s）
  - 可选项：是
  - 备注：退出码不符: expect=0, actual=1
  - 输出片段：
    （无）
- Probe `agent_browser_docs`
  - 命令：`grep -q "agent-browser" references/skill_pages/agent-browser.md && echo 'docs-ok'`
  - 退出码：0（耗时 0.0s）
  - 可选项：否
  - 输出片段：
    ```
docs-ok
    ```

### S06 | vercel-react-best-practices | PASS
**场景**：开发辅助
**能力**：高安装量 React 实践建议能力，适合前端代码评审与规范落地
**用户发言**：我想对一个 React 页面做结构和实现评审，先给我一版最推荐的 skill 方案。
**参考回复方向**：我会优先推荐高流量的 React 实践类 skill，给你可直接执行的安装入口和使用场景示例。
**评分**：4 / 4
- 结论：核心链路可直接交付。
- Probe `popular_react_practices`
  - 命令：`npx --yes skills find "vercel-react-best-practices" | head -n 30`
  - 退出码：0（耗时 5.4s）
  - 可选项：否
  - 输出片段：
    ```
███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

Install with npx skills add <owner/repo@skill>

vercel-labs/agent-skills@vercel-react-best-practices 182.3K installs
└ https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices

am-will/codex-skills@vercel-react-best-practices 3.6K installs
└ https://skills.sh/am-will/codex-skills/vercel-react-best-practices

supercent-io/skills-template@vercel-react-best-practices 3K installs
└ https://skills.sh/supercent-io/skills-template/vercel-react-best-practices

langgenius/dify@vercel-react-best-practices 612 installs
└ https://skills.sh/langgenius/dify/vercel-react-best-practices

lobehub/lobehub@vercel-react-best-practices 418 installs
└ https://skills.sh/lobehub/lobehub/vercel-react-best-practices

sickn33/antigravity-awesome-skills@vercel-react-best-practices 288 installs
└ https://skills.sh/sickn33/antigravity-awesome-skills/vercel-react-best-practices
    ```
- Probe `related_design_guidelines`
  - 命令：`npx --yes skills find "web-design-guidelines" | head -n 30`
  - 退出码：0（耗时 5.1s）
  - 可选项：是
  - 输出片段：
    ```
███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

Install with npx skills add <owner/repo@skill>

vercel-labs/agent-skills@web-design-guidelines 140.5K installs
└ https://skills.sh/vercel-labs/agent-skills/web-design-guidelines

antfu/skills@web-design-guidelines 4.6K installs
└ https://skills.sh/antfu/skills/web-design-guidelines

supercent-io/skills-template@web-design-guidelines 2.9K installs
└ https://skills.sh/supercent-io/skills-template/web-design-guidelines

langgenius/dify@web-design-guidelines 688 installs
└ https://skills.sh/langgenius/dify/web-design-guidelines

davila7/claude-code-templates@web-design-guidelines 315 installs
└ https://skills.sh/davila7/claude-code-templates/web-design-guidelines

sickn33/antigravity-awesome-skills@web-design-guidelines 309 installs
└ https://skills.sh/sickn33/antigravity-awesome-skills/web-design-guidelines
    ```

### S07 | web-design-guidelines | PASS
**场景**：开发辅助
**能力**：把页面问题转成可执行设计指导，支持一次性落地建议
**用户发言**：我需要给 UI 改版出一版可执行建议，先帮我找到最接近主流流程的设计准则 skill。
**参考回复方向**：我会先确认高热度的 design-guideline 类 skill，直接返回安装方式和输出产物边界。
**评分**：4 / 4
- 结论：核心链路可直接交付。
- Probe `design_guideline_skill`
  - 命令：`npx --yes skills find "web design guidelines" | head -n 30`
  - 退出码：0（耗时 5.5s）
  - 可选项：否
  - 输出片段：
    ```
███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

Install with npx skills add <owner/repo@skill>

vercel-labs/agent-skills@web-design-guidelines 140.5K installs
└ https://skills.sh/vercel-labs/agent-skills/web-design-guidelines

antfu/skills@web-design-guidelines 4.6K installs
└ https://skills.sh/antfu/skills/web-design-guidelines

supercent-io/skills-template@web-design-guidelines 2.9K installs
└ https://skills.sh/supercent-io/skills-template/web-design-guidelines

langgenius/dify@web-design-guidelines 688 installs
└ https://skills.sh/langgenius/dify/web-design-guidelines

davila7/claude-code-templates@web-design-guidelines 315 installs
└ https://skills.sh/davila7/claude-code-templates/web-design-guidelines

sickn33/antigravity-awesome-skills@web-design-guidelines 309 installs
└ https://skills.sh/sickn33/antigravity-awesome-skills/web-design-guidelines
    ```

### S08 | openai-whisper | DEGRADED
**场景**：音频转写
**能力**：离线转写短音频，减少人工记录与重复听写负担
**用户发言**：我后面有 60 秒音频，临时处理下转写，能直接本地跑吗？
**参考回复方向**：有 `whisper` CLI 最稳；我先确认本地可执行性，再给你参数和输出目录建议，避免把转写文件散落。
**评分**：2 / 4
- 结论：技能可用，但存在外部依赖/环境约束，建议先补环境后再用。
- Probe `whisper_binary`
  - 命令：`command -v whisper >/dev/null`
  - 退出码：1（耗时 0.0s）
  - 可选项：是
  - 备注：退出码不符: expect=0, actual=1
  - 输出片段：
    （无）
- Probe `whisper_no_key_doc`
  - 命令：`grep -n "no API key" references/skill_pages/openai-whisper.md | head -n 1`
  - 退出码：0（耗时 0.0s）
  - 可选项：否
  - 输出片段：
    ```
3:description: Local speech-to-text with the Whisper CLI (no API key).
    ```

### S09 | summarize | PASS
**场景**：文本处理
**能力**：长文本快速总结与信息压缩，适合会议纪要和日报降噪
**用户发言**：我有一大段日志和会议记录，先帮我找最热门的 summarize 能力，直接告诉我可装路径。
**参考回复方向**：我先给你筛选高关注度 summarize 候选，再给安装命令和适配场景（会议纪要/PR/报告）。
**评分**：4 / 4
- 结论：核心链路可直接交付。
- Probe `summarize_candidates`
  - 命令：`npx --yes skills find "summarize" | head -n 40`
  - 退出码：0（耗时 5.4s）
  - 可选项：否
  - 输出片段：
    ```
███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

Install with npx skills add <owner/repo@skill>

steipete/clawdis@summarize 446 installs
└ https://skills.sh/steipete/clawdis/summarize

coffeefuelbump/csv-data-summarizer-claude-skill@csv-data-summarizer 283 installs
└ https://skills.sh/coffeefuelbump/csv-data-summarizer-claude-skill/csv-data-summarizer

sickn33/antigravity-awesome-skills@youtube-summarizer 212 installs
└ https://skills.sh/sickn33/antigravity-awesome-skills/youtube-summarizer

patricio0312rev/skills@codebase-summarizer 62 installs
└ https://skills.sh/patricio0312rev/skills/codebase-summarizer

dkyazzentwatwa/chatgpt-skills@text-summarizer 48 installs
└ https://skills.sh/dkyazzentwatwa/chatgpt-skills/text-summarizer

yulong-me/skills@daily-news-summarizer 43 installs
└ https://skills.sh/yulong-me/skills/daily-news-summarizer
    ```

### S10 | self-improving-agent | PASS
**场景**：自我迭代
**能力**：让 agent 具备自评估与持续改进机制，适合流程自动化场景
**用户发言**：我想用一套机制让 agent 自动总结不足并优化下次响应，先给我可落地思路。
**参考回复方向**：我会给你先落地一个可迭代的闭环设计：采集场景、反思规则、定时复盘与迭代动作。
**评分**：4 / 4
- 结论：核心链路可直接交付。
- Probe `self_improving_intro`
  - 命令：`grep -n "self-improving" references/skill_pages/self-improving-agent.md | head -n 1`
  - 退出码：0（耗时 0.1s）
  - 可选项：否
  - 输出片段：
    ```
36:clawdhub install self-improving-agent
    ```
- Probe `self_improving_agent_count`
  - 命令：`npx --yes skills find "self improving agent" | head -n 20`
  - 退出码：0（耗时 5.8s）
  - 可选项：是
  - 输出片段：
    ```
███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

Install with npx skills add <owner/repo@skill>

halthelobster/proactive-agent@proactive-agent 3K installs
└ https://skills.sh/halthelobster/proactive-agent/proactive-agent

charon-fan/agent-playbook@self-improving-agent 1.2K installs
└ https://skills.sh/charon-fan/agent-playbook/self-improving-agent

pskoett/self-improving-agent@self-improvement 348 installs
└ https://skills.sh/pskoett/self-improving-agent/self-improvement

sundial-org/awesome-openclaw-skills@proactive-agent 44 installs
    ```

## 复用建议（未使用过 skill 的同学）
1) 先看“参考回复方向”，按场景直接复制到 OpenClaw 对话里。
2) 遇到 `DEGRADED`，优先按输出中的可安装/可配置项完成环境再复测。
3) 失败项可直接丢给经验官，重点复测外部依赖和命令路径。
