# OpenClaw / ClawHub Skill 深度调研（2026-03-04）

## 结论先看

如果目标是“真的有人用、口碑也不错”，当前最稳的入门结论是：

1. **第一梯队（高使用 + 高互动）**：
   - `self-improving-agent`
   - `gog`
   - `tavily-search`
   - `summarize`
   - `github`

2. **第二梯队（高使用，偏场景化）**：
   - `weather`
   - `agent-browser`
   - `sonoscli`
   - `notion`
   - `nano-pdf`

3. **怎么做出来的（共性）**：
   - 大多数是“**把成熟 CLI/API 封成稳定工作流**”，不是从零造复杂系统。
   - 高采用 Skill 通常都有：
     - 清晰触发描述（description）
     - 安装/依赖说明
     - 快速可跑的最小命令
     - 明确失败处理或注意事项

---

## 1) 数据口径与方法

- 数据源：`https://clawhub.ai/api/v1/skills`
- 抓取时间：2026-03-04（Asia/Shanghai）
- 样本：按 `downloads` 分页抓取到的 **2812 个公开技能**（去重后）
- 指标：
  - `downloads`（下载）
  - `installsCurrent`（当前安装）
  - `stars`
  - `comments`

说明：
- “好用”没有官方统一满意度评分，本文用 `stars/comments` 作为“用户认可度代理指标”（**推断**）。
- “经常用”以 `downloads + installsCurrent` 为主（**事实指标**）。

---

## 2) Top Skills（按 downloads）

| 排名 | Skill | owner | downloads | current installs | stars | comments |
|---|---|---|---:|---:|---:|---:|
| 1 | self-improving-agent | pskoett | 92,855 | 1,006 | 1,129 | 45 |
| 2 | Tavily Web Search | arun-8687 | 79,740 | 767 | 367 | 25 |
| 3 | Gog | steipete | 79,169 | 1,382 | 611 | 35 |
| 4 | Find Skills | JimLiuxinghai | 76,438 | 631 | 341 | 3 |
| 5 | Summarize | steipete | 68,983 | 1,387 | 318 | 11 |
| 6 | Github | steipete | 63,563 | 1,225 | 213 | 7 |
| 7 | Agent Browser | TheSethRose | 63,017 | 736 | 333 | 1 |
| 8 | Weather | steipete | 53,894 | 1,013 | 187 | 6 |
| 9 | Proactive Agent | halthelobster | 51,066 | 407 | 342 | 17 |
| 10 | Sonoscli | steipete | 45,196 | 1,104 | 30 | 1 |

---

## 3) “高使用 + 高口碑”候选（推断）

口径：综合 `downloads / installsCurrent / stars / comments` 做加权排序（0.4/0.3/0.2/0.1）。

Top 10：
1. self-improving-agent
2. gog
3. summarize
4. tavily-search
5. github
6. find-skills
7. weather
8. agent-browser
9. sonoscli
10. proactive-agent

解释（推断）：
- `self-improving-agent` 同时在下载、星标、评论都高，说明“被广泛尝试且有讨论”。
- `gog/summarize/github/weather` 这类“高频日常任务”技能安装量很高，说明实用性强。
- `tavily-search/agent-browser` 代表“联网检索 + 自动化交互”刚需场景。

---

## 4) 这些热门 Skill 都是怎么做的？（实包解剖）

我对 Top 技能包（本地 zip）做了结构分析，样本 10 个：

- 中位行数：`49` 行（平均 150 行，主要被超长 skill 拉高）
- 有 `setup/install` 的：`7/10`
- 有 `quick start` 的：`3/10`
- 有明确 `workflow/phase` 的：`4/10`
- 带 `scripts/` 的：`2/10`（`self-improving-agent`, `tavily-search`）

### 制作模式 A：轻量包装型（20-60 行）
- 代表：`nano-pdf`, `gog`, `summarize`, `github`, `weather`
- 核心：
  - 前言说明“这个 Skill 管什么”
  - 直接给可运行命令
  - 补几条风险提示
- 适合：新手快速做“能用版”

### 制作模式 B：流程编排型（100-300 行）
- 代表：`find-skills`, `agent-browser`, `notion`
- 核心：
  - 任务分阶段
  - 给出参数选项和输出约定
  - 给典型场景路径
- 适合：复杂任务但还不需要重脚本

### 制作模式 C：系统增强型（500+ 行 + scripts）
- 代表：`self-improving-agent`
- 核心：
  - 除主文档外有脚本和资产
  - 有日志格式、跨会话策略、升级路径
- 适合：你要做“长期演进”能力时

---

## 5) 社区趋势（最近 PR/Issue）

从 `anthropics/skills` 与 `ComposioHQ/awesome-claude-skills` 最近 50 条 issue/PR 看：

- 高频方向：
  - `testing/playwright`
  - `security/audit`
  - `automation/agent workflow`
  - `docs/extract`

推断：
- 市场正在从“单点工具”走向“可执行流程与质量保障”（测试、安全、自动化）。

---

## 6) 给你的产品建议（面向小白教学科普）

你要做“Skill 教学应用”，建议把热门技能拆成 3 层教学：

1. **第一层：一分钟上手（轻量包装型）**
   - 用 `summarize/github/weather` 做演示
2. **第二层：流程思维（流程编排型）**
   - 用 `find-skills/agent-browser/notion` 教“阶段化设计”
3. **第三层：工程化升级（系统增强型）**
   - 用 `self-improving-agent` 教“日志-反馈-迭代闭环”

---

## 7) 风险提醒（必须加在教学产品里）

第三方 skill 生态存在供应链与权限风险。上线教学时应默认展示：
- 来源（作者/仓库）
- 依赖（bins/env）
- 权限范围
- 风险等级

并给默认策略：
- 新手先用“低权限、可审阅、可本地复现”的技能。

---

## 8) 参考链接

- ClawHub Skills 列表 API（排序与分页）
  - https://clawhub.ai/api/v1/skills?sort=downloads&limit=20
- ClawHub 单技能详情 API（owner 与 stats）
  - https://clawhub.ai/api/v1/skills/self-improving-agent
- ClawHub 技能下载 API（包结构分析）
  - https://clawhub.ai/api/v1/download?slug=self-improving-agent

- Anthropic 官方 skills 仓库
  - https://github.com/anthropics/skills
- Agent Skills 规范
  - https://agentskills.io/specification

- 社区趋势来源
  - https://github.com/anthropics/skills/issues
  - https://github.com/ComposioHQ/awesome-claude-skills/pulls

- 供应链风险研究
  - https://labs.snyk.io/resources/openclaw-security/
