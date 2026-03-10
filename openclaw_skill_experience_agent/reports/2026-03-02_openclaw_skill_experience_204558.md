# OpenClaw 对话式 Skill 体验日报
生成时间：2026-03-02 20:45:58
目标：独立 agent 每日自动测试 10 个 skill 的对话可用性

## 说明
- 每个案例先用“用户口播问题”模拟真实对话入口。
- 评估结果优先看“是否能直接落地”，再看降级可解释性。

## 执行汇总
- 测试项：10
- 通过：3
- 降级：4
- 失败：3
- 情景得分：21 / 44

### S01 | find-skills | PASS
**场景**：能力发现
**用户发言**：我想给 OpenClaw 增加测试相关能力，帮我先找 3 个可直接装的技能并给安装方式。
**参考回复方向**：我先按“测试能力”关键词做一次检索，先给你 3 个可用候选和安装命令。你要我直接装哪个我就继续执行。
**评分**：5 / 5
- 结论：核心链路可直接交付。
- Probe `skills_cli_find`
  - 命令：`npx --yes skills ls -g | head -n 20`
  - 退出码：0（耗时 9.0s）
  - 可选项：否
  - 输出片段：
    ```
[1mGlobal Skills[0m

[36mapify-twitter[0m [38;5;102m~/.openclaw/skills/apify-twitter[0m
  [38;5;102mAgents:[0m OpenClaw
[36mgsdata[0m [38;5;102m~/.openclaw/skills/gsdata[0m
  [38;5;102mAgents:[0m OpenClaw
[36mmoltbook[0m [38;5;102m~/.openclaw/skills/moltbook[0m
  [38;5;102mAgents:[0m OpenClaw
[36mpatent-disclosure-writer[0m [38;5;102m~/.openclaw/skills/patent-disclosure-writer-community[0m
  [38;5;102mAgents:[0m OpenClaw
[36mpatent-pro[0m [38;5;102m~/.openclaw/skills/patent-pro[0m
  [38;5;102mAgents:[0m OpenClaw
[36mPatent Scanner[0m [38;5;102m~/.openclaw/skills/patent-scanner-community[0m
  [38;5;102mAgents:[0m OpenClaw
[36mPatent Validator[0m [38;5;102m~/.openclaw/skills/patent-validator-community[0m
  [38;5;102mAgents:[0m OpenClaw
[36mfigma[0m [38;5;102m~/.codex/skills/figma[0m
  [38;5;102mAgents:[0m Codex
[36mfigma-implement-design[0m [38;5;102m~/.codex/skills/figma-implement-design[0m
  [38;5;102mAgents:[0m Codex
    ```

### S02 | weather | FAIL
**场景**：信息查询
**用户发言**：我刚到伦敦，今天要不要带伞？直接给我一句天气结论。
**参考回复方向**：我先查伦敦实时天气，再给你一句结论：是否有降雨、体感温度和风速，方便你快速决策。
**评分**：0 / 5
- 结论：核心链路异常，当前对话路径无法直接交付。
- Probe `wttr_primary`
  - 命令：`curl -s --max-time 12 'https://wttr.in/London?format=3'`
  - 退出码：28（耗时 12.1s）
  - 可选项：否
  - 备注：退出码不符: expect=0, actual=28
  - 输出片段：
    （无）
- Probe `open_meteo_fallback`
  - 命令：`curl -s --max-time 12 'https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.12&current_weather=true'`
  - 退出码：0（耗时 3.3s）
  - 可选项：否
  - 输出片段：
    ```
{"latitude":51.49349,"longitude":-0.13172913,"generationtime_ms":0.10633468627929688,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":1.0,"current_weather_units":{"time":"iso8601","interval":"seconds","temperature":"°C","windspeed":"km/h","winddirection":"%","is_day":"","weathercode":"wmo code"},"current_weather":{"time":"2026-03-02T12:45","interval":900,"temperature":14.1,"windspeed":14.4,"winddirection":188,"is_day":1,"weathercode":0}}
    ```

### S03 | polymarket | FAIL
**场景**：市场追踪
**用户发言**：我想关注近期跟政治相关的热门市场，先给我一个当日趋势清单。
**参考回复方向**：我先抓取 Polymarket 的 trending 清单，按热度和关键价格变动给你先做一版观察日报。
**评分**：0 / 5
- 结论：核心链路异常，当前对话路径无法直接交付。
- Probe `polymarket_trending`
  - 命令：`python3 runtime_scripts/polymarket/polymarket.py trending | head -n 80`
  - 退出码：0（耗时 2.0s）
  - 可选项：否
  - 备注：缺少关键内容: Yes
  - 输出片段：
    ```
🔥 **Trending on Polymarket**

🎯 **Khamenei out as Supreme Leader of Iran by February 28?**
   Volume: $101.2M (24h: $19.8M)
   ⏰ Ended
   Markets: 1
   • Khamenei out as Supreme Leader of Iran b: 99.9% ↑0.4% ($101.2M)
   🔗 polymarket.com/event/khamenei-out-as-supreme-leader-of-iran-by-february-28

🎯 **2026 NBA Champion**
   Volume: $323.6M (24h: $11.2M)
   ⏰ Jul 01, 2026
   Markets: 30
   • Oklahoma City Thunder: 35.5% ($4.4M)
   • San Antonio Spurs: 12.0% ↑0.2% ($4.6M)
   • Denver Nuggets: 11.5% ($2.5M)
   • Cleveland Cavaliers: 7.5% ↓0.7% ($3.4M)
   • Boston Celtics: 7.3% ↑0.1% ($4.3M)
   • Detroit Pistons: 6.8% ↓0.2% ($4.2M)
   • New York Knicks: 4.6% ↓0.1% ($2.7M)
   • Houston Rockets: 3.5% ↓0.1% ($2.5M)
   • Minnesota Timberwolves: 3.1% ↑0.1% ($3.7M)
   • Los Angeles Lakers: 1.5% ($3.8M)
   ... and 20 more
   🔗 polymarket.com/event/2026-nba-champion

🎯 **2026 FIFA World Cup Winner **
   Volume: $234.9M (24h: $8.2M)
   ⏰ Jul 20, 2026
   Markets: 43
   • Spain: 14.9% ↑0.1% ($2.9M)
   • England: 13.2% ($2.5M)
   • Argentina: 11.5% ↓0.2% ($3.4M)
   • France: 10.7% ($2.7M)
   • Brazil: 8.6% ($2.4M)
   • Portugal: 7.3% ↑0.3% ($6.3M)
   • Germany: 5.5% ↑0.1% ($4.5M)
   • Netherlands: 3.1% ($4.9M)
   • Norway: 2.9% ↑0.1% ($5.2M)
   • Italy: 1.9% ($4.5M)
   ... and 33 more
   🔗 polymarket.com/event/2026-fifa-world-cup-winner-595

🎯 **Khamenei out as Supreme Leader of Iran by March 31?**
   Volume: $57.8M (24h: $8.0M)
   ⏰ Ends in 4w
   Markets: 1
   • Khamenei out as Supreme Leader of Iran b: 99.9% ↓1.0% ($57.8M)
   🔗 polymarket.com/event/khamenei-out-as-supreme-leader-of-iran-by-march-31

🎯 **La Liga Winner **
   Volume: $126.2M (24h: $5.9M)
   ⏰ May 30, 2026
   Markets: 20
   • Barcelona: 61.0% ↓1.0% ($1.6M)
   • Real Madrid: 36.0% ↑1.0% ($1.5M)
   • Atletico Madrid: 0.4% ↑0.1% ($8.0M)
   • Villarreal: 0.2% ↑0.1% ($6.6M)
   • Betis: 0.2% ($4.6M)
   • Celta Vigo: 0.1% ($3.8M)
   • Osasuna: 0.1% ($4.3M)
   • Athletic Bilbao: 0.1% ↓0.1% ($16.3M)
   • Real Sociedad: 0.1% ($3.9M)
   • Sevilla: 0.1% ($5.7M)
   ... and 10 more
   🔗 polymarket.com/event/la-liga-winner-114
    ```
- Probe `polymarket_calendar`
  - 命令：`python3 runtime_scripts/polymarket/polymarket.py calendar --days 2 | head -n 60`
  - 退出码：0（耗时 2.5s）
  - 可选项：是
  - 输出片段：
    ```
📅 **Resolving in 2 days** (0 markets)

No markets resolving in this timeframe.
    ```

### S04 | ontology | FAIL
**场景**：知识结构化
**用户发言**：帮我建立一个名为『Q1技能体验』的项目节点，并关联负责人『我』，然后列出该类型实体。
**参考回复方向**：我先建立项目和负责人节点，再把“负责人”关系写入图谱，最后给你回传创建结果。
**评分**：0 / 5
- 结论：核心链路异常，当前对话路径无法直接交付。
- Probe `ontology_create_node`
  - 命令：`cd runtime_scripts/ontology && python3 ontology.py create --type Project --props '{"name":"Q1技能体验","status":"active"}' | head -n 40`
  - 退出码：0（耗时 0.1s）
  - 可选项：否
  - 输出片段：
    ```
{
  "id": "proj_b099ccb0",
  "type": "Project",
  "properties": {
    "name": "Q1\u6280\u80fd\u4f53\u9a8c",
    "status": "active"
  },
  "created": "2026-03-02T12:45:57.306709+00:00",
  "updated": "2026-03-02T12:45:57.306709+00:00"
}
    ```
- Probe `ontology_query`
  - 命令：`cd runtime_scripts/ontology && python3 ontology.py query --type Project --where '{"status":"active"}' | head -n 80`
  - 退出码：0（耗时 0.1s）
  - 可选项：否
  - 备注：缺少关键内容: "Q1技能体验"
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
  }
]
    ```

### S05 | agent-browser | DEGRADED
**场景**：网页动作
**用户发言**：我想在一个页面上点开“获取验证码”按钮，能不能先告诉我这类能力要不要安装依赖？
**参考回复方向**：这类网页自动化能力需要本地 `agent-browser` 与 `node/npm` 环境；我先给你可执行安装步骤和常见回退方案。
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

### S06 | github | DEGRADED
**场景**：代码协作
**用户发言**：我想快速看下某仓库的最近 CI 失败记录，先给我最短路径。
**参考回复方向**：我会先检查 `gh` 是否就绪；可直接用 `gh run list` 和 `gh run view --log-failed` 输出失败摘要，必要时给你可复制命令。
**评分**：2 / 4
- 结论：技能可用，但存在外部依赖/环境约束，建议先补环境后再用。
- Probe `gh_binary`
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

### S07 | obsidian | DEGRADED
**场景**：个人知识库
**用户发言**：我想从命令行批量找出最近提过“AI”相关的便签，有没更快方法？
**参考回复方向**：可先确认 `obsidian-cli` 是否已就绪；有的话可用 `obsidian-cli search-content` 做文本检索，否则我先给你先决条件和配置路径。
**评分**：2 / 4
- 结论：技能可用，但存在外部依赖/环境约束，建议先补环境后再用。
- Probe `obsidian_cli`
  - 命令：`command -v obsidian-cli >/dev/null`
  - 退出码：1（耗时 0.0s）
  - 可选项：是
  - 备注：退出码不符: expect=0, actual=1
  - 输出片段：
    （无）
- Probe `obsidian_doc`
  - 命令：`grep -n "Obsidian" references/skill_pages/obsidian.md | head -n 1`
  - 退出码：0（耗时 0.1s）
  - 可选项：否
  - 输出片段：
    ```
3:description: Work with Obsidian vaults (plain Markdown notes) and automate via obsidian-cli.
    ```

### S08 | humanizer | PASS
**场景**：内容优化
**用户发言**：下面这段话太像 AI 了，帮我润色到更自然："在现代社会背景下，我们应当进一步强化系统性的协同机制，以确保可持续增长。"
**参考回复方向**：我会先识别这段文本中的 AI 味道，再给你给出更自然的版本；如果你要我可直接改写成更有语气的人类版本。
**评分**：4 / 4
- 结论：核心链路可直接交付。
- Probe `humanizer_desc`
  - 命令：`grep -n "humanizer" references/skill_pages/humanizer.md | head -n 1`
  - 退出码：0（耗时 0.1s）
  - 可选项：否
  - 输出片段：
    ```
2:name: humanizer
    ```
- Probe `humanizer_features`
  - 命令：`grep -n "Signs of AI" references/skill_pages/humanizer.md | head -n 1`
  - 退出码：0（耗时 0.1s）
  - 可选项：是
  - 输出片段：
    ```
7:  comprehensive "Signs of AI writing" guide. Detects and fixes patterns including:
    ```

### S09 | openai-whisper | DEGRADED
**场景**：音频转写
**用户发言**：我后面有 60 秒音频，临时处理下转写，能直接本地跑吗？
**参考回复方向**：有 `whisper` CLI 最稳；我先确认本地可执行性，再给你参数和输出目录建议，避免把转写文件散落。
**评分**：2 / 4
- 结论：技能可用，但存在外部依赖/环境约束，建议先补环境后再用。
- Probe `whisper_binary`
  - 命令：`command -v whisper >/dev/null`
  - 退出码：1（耗时 0.1s）
  - 可选项：是
  - 备注：退出码不符: expect=0, actual=1
  - 输出片段：
    （无）
- Probe `whisper_no_key_doc`
  - 命令：`grep -n "no API key" references/skill_pages/openai-whisper.md | head -n 1`
  - 退出码：0（耗时 0.1s）
  - 可选项：否
  - 输出片段：
    ```
3:description: Local speech-to-text with the Whisper CLI (no API key).
    ```

### S10 | proactive-agent | PASS
**场景**：自我迭代
**用户发言**：我不想每次都等我说，需要主动提醒我做汇总，这个能力怎么落地？
**参考回复方向**：我先确认该技能的自省能力边界：偏流程治理与任务提醒，给你建议如何在路由里做定时检查并触发日报。
**评分**：4 / 4
- 结论：核心链路可直接交付。
- Probe `proactive_intro`
  - 命令：`grep -n "Proactive" references/skill_pages/proactive-agent.md | head -n 1`
  - 退出码：0（耗时 0.1s）
  - 可选项：否
  - 输出片段：
    ```
8:# Proactive Agent 🦞
    ```
- Probe `proactive_crons`
  - 命令：`grep -n "cron" references/skill_pages/proactive-agent.md | head -n 2`
  - 退出码：0（耗时 0.1s）
  - 可选项：是
  - 输出片段：
    ```
74:11. [Autonomous vs Prompted Crons](#autonomous-vs-prompted-crons) ⭐ NEW
353:**Key insight:** There's a critical difference between cron jobs that *prompt* you vs ones that *do the work*.
    ```

## 复用建议（未使用过 skill 的同学）
1) 先看“参考回复方向”，按场景直接复制到 OpenClaw 对话里。
2) 遇到 `DEGRADED`，优先按输出中的可安装/可配置项完成环境再复测。
3) 失败项可直接丢给经验官，重点复测外部依赖和命令路径。
