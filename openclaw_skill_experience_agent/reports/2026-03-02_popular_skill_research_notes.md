# OpenClaw 技能“热门性/可用性”复核（截至 2026-03-02）

## 目的
在你要做“10个skill体验报告”之前，先做一版“选什么skill”的证据化筛选，来源覆盖：
- 官方/半官方目录与入口
- 第三方技能目录/聚合页
- Reddit 社区真实讨论
- `npx skills find` 本地命令行可得安装统计/命令入口

## 结论（先验）
若以“**对话场景里能真实解决问题、且尽量不依赖复杂 key**”为优先，当前更值得先测的不是“单纯流行”，而是：
1. `agent-browser`（可替代/增强网页自动化场景）
2. `github`（CI/PR/issue 这类日常开发对话非常高频）
3. `coding-agent`（AI coding workflow 的对话触发率高）
4. `obsidian`（本地知识库类任务）
5. `self-improving-agent`（错误修复复盘、持续体验提升场景）
6. `openai-whisper`（短时转写）
7. `summarize`（对话中压缩信息）
8. `peekaboo`（社媒/动态整理类，作为轻量对话案例）
9. `video-frames`（媒体素材抽帧、质量抽查）
10. `browser-control`（Reddit 用户高频提及的浏览器执行能力名，需按具体实现名校准）

## 证据来源与可信度

### 1) 目录/官方生态信号
- OpenClaw 官方生态入口显示了“技能 + 关键能力+场景”的推荐逻辑（如基础类/搜索类/记忆类），并明确了 `web-search` 与 `browser-control` 在官方讨论中的常见组合路径。  
  来源: [OpenClaw 官方FAQ/文档聚合页面（按抓取）](https://openclaws.io/)
- OpClawSkills 目录明确标注“按下载量与稳定性精选”，`agent-browser`、`github`、`clawbrowser`、`tavily`、`perplexity` 一类在其 Feature 列表中位于高展示位。  
  来源: [OpClawSkills Featured Skills](https://opclawskills.com/)
- 同目录的 `agent-browser` 页面明确了**无需 API key**、运行时仅需 Node/npm 依赖，且适配表单交互、截图、会话持久化等对话场景。  
  来源: [Agent Browser Skill Guide](https://opclawskills.com/skills/agent-browser)
- 同目录的 `github` 说明强调通过 `gh` 做仓库、PR、CI 全量链路能力，适合“我最近 CI 挂了怎么办”这类对话。  
  来源: [GitHub Skill Guide](https://opclawskills.com/skills/github)
- OpenClaw Directory（社区目录）首页显示了类别与“Most Viewed”，虽无绝对大规模下载，但至少反映了当前社区页面交互热度：例如 `coder-workspaces`（434 views）。  
  来源: [OpenClaw Skills Directory](https://openclawdir.com/skills)

### 2) 社媒讨论信号
- Reddit 用户“2周体验分享”明确提到 `browser-control`、`self-improving-agent`、`voice/whisper` 的实战价值，并提到“security non-negotiable”。  
  来源: [r/openclaw 体验反馈帖](https://www.reddit.com/r/openclaw/comments/1rf0vz6/two_weeks_later_with_openclaw_and_this_is_what/)
- 同样社区里也有大量关于“browser control unstable”等问题帖，说明该能力虽然常用但也要把稳定性和桥接层重试策略写进体验报告。  
  来源: [r/openclaw “browser control unstable”](https://www.reddit.com/r/openclaw/comments/1qx7nhj/browser_control_unstable/)
- 外部安全讨论（如 PCWorld、Microsoft 的官方警示文章）给出“技能市场可用也高风险，安装前风险隔离优先”的一致口径。  
  来源: [PCWorld](https://www.pcworld.com/article/3064874/openclaw-ai-is-going-viral-dont-install-it.html)、[Cybernews/微软消息](https://cybernews.com/security/microsoft-openclaw-unsuited-run-standard-personal-enterprise-workstation/)

### 3) CLI 侧可验证信号（本地快速查询）
我执行了 `npx --yes skills find` 的快照，得到部分命中值（不同来源统计口径不同，数值仅用于“热度参考”）：
- `coding-agent`: 2.9K installs（`supercent-io/skills-template@copilot-coding-agent`）
- `obsidian`: 3.8K installs（`kepano/obsidian-skills@obsidian-bases`）
- `openai-whisper`: 177 installs（`steipete/clawdis@openai-whisper`）
- `summarize`: 449 installs（`steipete/clawdis@summarize`）
- `peekaboo`: 400 installs（`steipete/clawdis@peekaboo`）
- `video-frames`: 122 installs（`steipete/clawdis@video-frames`）
- `discord`: 424 installs（`steipete/clawdis@discord`，部分来源以 `discord-bot-architect` 为主）

> 说明：`skills find "github"` 当前查询更容易返回 `microsoft/github-copilot-for-azure` 这一类高流量仓库条目，且与 OpenClaw 核心 `github` 关键词命名不完全一致；建议在最终测试时使用明确仓库路径（或 `skills find "gh"` 先探底）来避免命名噪音。

## 测试优先级建议（给你后续“10个案例”直接用）

按“对话体验价值 × 热度 × 依赖复杂度”排序：
1. `agent-browser`（高）  
   对话场景：表单提交、页面导航、截图核查、DOM 数据抽取
2. `github`（高）  
   对话场景：CI 挂了、PR 阶段失败、issue/PR 查询
3. `coding-agent`（高）  
   对话场景：代码自动修复、任务拆解、跨工具执行
4. `self-improving-agent`（中高）  
   对话场景：失败复盘、错误规则沉淀、用户修正反馈
5. `obsidian`（中）  
   对话场景：从聊天到知识库结构化写入/查询
6. `summarize`（中）  
   对话场景：日志/会议记录/长文压缩
7. `openai-whisper`（中）  
   对话场景：音频转写到可检索文本
8. `peekaboo`（中低）  
   对话场景：社媒信息抓取后摘要
9. `video-frames`（中低）  
   对话场景：短视频或会议回放素材抽帧核验
10. `browser-control`（需映射）  
   对话场景：与未提供 API 时的网页操作 fallback（与 agent-browser 可形成互补）

## 建议下一步（可直接执行）
1. 将上述 10 个中的命名统一规范为“可直接安装名”并更新到 `openclaw_skill_experience_agent/config/skill_cases.json`  
2. 把每个用例改写为“用户第一句发言 + 期待系统动作 + 降级提示”，继续跑你现有的每日报告流水线  
3. 把安全类说明写入每个报告模板（尤其是 `browser-*` 与第三方依赖较多的技能）
