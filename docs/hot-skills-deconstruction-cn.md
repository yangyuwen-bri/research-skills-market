# 热门 Skill 逐个拆解学习手册（2026-03-04）

## 使用说明

这份手册按“可学习性”来拆 10 个热门 Skill。每个 Skill 都包含：
- 这是做什么的
- 为什么大家常用（基于下载/安装/互动数据）
- 结构怎么写出来的
- 你要模仿的写法
- 练习作业（从小白到可复用）

数据口径：ClawHub API（downloads / installsCurrent / stars / comments），时间为 2026-03-04。

---

## 0. 学习顺序（建议）

先从低门槛开始，再到复杂系统：
1. `weather`
2. `github`
3. `summarize`
4. `gog`
5. `tavily-search`
6. `find-skills`
7. `sonoscli`
8. `agent-browser`
9. `self-improving-agent`
10. `proactive-agent`

---

## 1) self-improving-agent

- 人气数据：`downloads 92,855 / current installs 1,006 / stars 1,129 / comments 45`
- 定位：把“犯错-纠正-沉淀”流程产品化，让 agent 越用越稳。
- 源文件：[SKILL.md](/tmp/skill-study/toplocal/tmp_self-improving-agent/SKILL.md)

### 它为什么好用
- 不是只给指令，而是给了完整运维闭环：日志、模板、hook、推广到工作区规则。
- 明确“什么时候记录、记录到哪、怎么升级为长期规则”。

### 结构拆解
- 文档规模：647 行（系统型 Skill）
- 有脚本：`scripts/activator.sh`, `scripts/extract-skill.sh`, `scripts/error-detector.sh`
- 核心模块：Quick Reference -> Setup -> Logging Format -> Promotion targets

### 你要学的写法
- 把“行为原则”变成“可执行流程”。
- 给出标准日志格式（字段固定、可追踪）。
- 明确“从临时经验到长期记忆”的升级路径。

### 练习作业
- 作业 A：给你的科研 Skill 增加 `ERRORS.md / LEARNINGS.md` 两个日志模板。
- 作业 B：定义 3 条“何时必须写入学习日志”的触发规则。

---

## 2) tavily-search

- 人气数据：`79,740 / 767 / 367 / 25`
- 定位：联网搜索，返回对 AI 友好的结果。
- 源文件：[SKILL.md](/tmp/skill-study/toplocal/tmp_tavily-search/SKILL.md)

### 它为什么好用
- 非常短小（38 行），但可直接用。
- 用 `scripts/*.mjs` 包装搜索和抽取，降低模型临场发挥。

### 结构拆解
- 依赖：`node`
- 环境变量：`TAVILY_API_KEY`
- 模块：Search / Options / Extract

### 你要学的写法
- 少废话，先给能跑的命令。
- 参数说明只写高价值选项（结果数、深度、主题、时间）。

### 练习作业
- 作业 A：做一个 `paper-search` skill，支持 `--n`、`--from-year`、`--domain`。
- 作业 B：把“网页抽取”拆成独立脚本命令。

---

## 3) gog

- 人气数据：`79,169 / 1,382 / 611 / 35`
- 定位：Google Workspace 一体化 CLI 操作。
- 源文件：[SKILL.md](/tmp/skill-study/toplocal/tmp_gog/SKILL.md)

### 它为什么好用
- 命令密度高，覆盖 Gmail/Calendar/Drive/Sheets/Docs 高频任务。
- “一次认证，多场景复用”，用户粘性高。

### 结构拆解
- 36 行，几乎全是“场景命令表”。
- 先 Setup，再 Common commands，再 Notes。

### 你要学的写法
- 一行一个任务，任务名 + 命令，不绕弯。
- 每条命令都是用户真实动作，不是抽象描述。

### 练习作业
- 作业 A：做你的“科研工作台命令清单”（检索/整理/导出/引用）。
- 作业 B：至少写 12 条高频命令，覆盖 4 个子场景。

---

## 4) find-skills

- 人气数据：`76,438 / 631 / 341 / 3`
- 定位：帮用户“先找到技能，再安装技能”。
- 源文件：[SKILL.md](/tmp/skill-study/toplocal/tmp_find-skills/SKILL.md)

### 它为什么好用
- 把“用户说不清需求”的问题流程化了。
- 有分步骤、分类和兜底策略（找不到技能时怎么办）。

### 结构拆解
- 133 行，典型流程编排型。
- 主体是 Step 1-4：理解需求 -> 搜索 -> 展示选项 -> 安装。

### 你要学的写法
- 让 Skill 本身像“咨询顾问流程”。
- 输出模板可复用，减少 agent 自由发挥。

### 练习作业
- 作业 A：做一个 `find-research-skills`，按学科和任务类型推荐。
- 作业 B：写“无匹配时兜底话术 + 替代方案”。

---

## 5) summarize

- 人气数据：`68,983 / 1,387 / 318 / 11`
- 定位：网页/文件/YouTube 摘要统一入口。
- 源文件：[SKILL.md](/tmp/skill-study/toplocal/tmp_summarize/SKILL.md)

### 它为什么好用
- 典型高频刚需（“先看懂内容”）且跨格式。
- 参数设计直接对齐用户目标（长度、模型、JSON 输出）。

### 结构拆解
- 49 行，分为 Quick start / keys / flags / config。
- 没有复杂流程，但“配置与参数”解释完整。

### 你要学的写法
- 新手最需要的不是原理，而是“3 条命令马上跑起来”。
- 参数只保留会明显影响结果的项。

### 练习作业
- 作业 A：做一个 `literature-summarize`，固定输出字段。
- 作业 B：加入 `--json` 输出，保证可被后续流程消费。

---

## 6) github

- 人气数据：`63,563 / 1,225 / 213 / 7`
- 定位：面向工程协作的 GitHub CLI 标准操作。
- 源文件：[SKILL.md](/tmp/skill-study/toplocal/tmp_github/SKILL.md)

### 它为什么好用
- 解决真实工程团队常见动作：PR 检查、CI 定位、API 查询。
- 结构非常克制，几乎没有噪音。

### 结构拆解
- 47 行。
- 模块：PR -> run/log -> gh api -> JSON 输出。

### 你要学的写法
- 以任务分组，不按命令分组。
- 默认鼓励结构化输出（`--json` + `--jq`），便于自动化。

### 练习作业
- 作业 A：做一个 `paper-repo-check` skill（检查复现实验仓库健康度）。
- 作业 B：输出统一 JSON 结果，供后续评估器读取。

---

## 7) agent-browser

- 人气数据：`63,017 / 736 / 333 / 1`
- 定位：网页自动化交互（导航、点击、填充、快照、录屏）。
- 源文件：[SKILL.md](/tmp/skill-study/toplocal/tmp_agent-browser/SKILL.md)

### 它为什么好用
- 提供了完整操作原语和建议工作流（open -> snapshot -> interact -> re-snapshot）。
- 指令体系稳定，适合 agent 批量执行 UI 任务。

### 结构拆解
- 328 行，命令字典型文档。
- 模块非常清晰：安装、核心流程、导航、交互、信息获取、状态检查、截图、等待等。

### 你要学的写法
- 大型 Skill 要“分层命令目录”，避免用户迷路。
- 把关键流程做成固定顺序，降低误操作。

### 练习作业
- 作业 A：做一个 `journal-site-crawler`（先快照后抽取）。
- 作业 B：为每个交互动作补一个失败重试策略。

---

## 8) weather

- 人气数据：`53,894 / 1,013 / 187 / 6`
- 定位：无 Key 的天气查询与回退策略。
- 源文件：[SKILL.md](/tmp/skill-study/toplocal/tmp_weather/SKILL.md)

### 它为什么好用
- 0 认证门槛，开箱即用。
- 主服务 + 备用服务（wttr.in + open-meteo）简洁可靠。

### 结构拆解
- 49 行。
- 先主路径，再 fallback，再 tips。

### 你要学的写法
- 小工具型 Skill 的核心是“可达性”和“回退机制”。
- 给最常用输出格式，别让用户自己拼参数。

### 练习作业
- 作业 A：做一个 `paper-status` 查询 Skill（主源 + 备源）。
- 作业 B：定义 2 条“主源失败时自动降级”的规则。

---

## 9) proactive-agent

- 人气数据：`51,066 / 407 / 342 / 17`
- 定位：把 agent 变成主动协作伙伴（记忆、检查、恢复、持续改进）。
- 源文件：[SKILL.md](/tmp/skill-study/toplocal/tmp_proactive-agent/SKILL.md)

### 它为什么好用
- 高概念 + 强流程：不仅告诉“做什么”，还告诉“什么时候必须做”。
- 对上下文丢失、记忆恢复、周期任务有明确协议。

### 结构拆解
- 632 行，系统架构型。
- 关键模式：WAL 协议、Working Buffer、Compaction Recovery、Security Hardening。
- 带脚本：`scripts/security-audit.sh`

### 你要学的写法
- 高阶 Skill 要有“协议层”，而不是散乱技巧。
- 给触发器（trigger）和执行顺序（protocol），减少遗漏。

### 练习作业
- 作业 A：给你的科研系统加 `SESSION-STATE` 与 `working-buffer`。
- 作业 B：定义一次“上下文丢失恢复流程”。

---

## 10) sonoscli

- 人气数据：`45,196 / 1,104 / 30 / 1`
- 定位：局域网 Sonos 音箱控制。
- 源文件：[SKILL.md](/tmp/skill-study/toplocal/tmp_sonoscli/SKILL.md)

### 它为什么好用
- 极简命令集，覆盖 discover/status/play/volume/group 等常见操作。
- 本地网络场景明确，用户预期稳定。

### 结构拆解
- 26 行。
- Quick start + Common tasks + Notes。

### 你要学的写法
- 垂直场景 Skill 不需要长文档，关键是“任务覆盖完整 + 注意事项准确”。

### 练习作业
- 作业 A：做一个你领域内的“局部垂直 Skill”（只做一件事，但做透）。
- 作业 B：写 8 条常见任务命令 + 3 条排错提示。

---

## 通用抄作业模板（你写任何 Skill 都可套）

```markdown
---
name: your-skill
description: 什么时候该用它，什么时候不该用。
---

# Your Skill

## Quick start
- 一条最小可运行命令

## When to use
- 3-5 条触发条件

## Core workflow
1. Step A
2. Step B
3. Step C

## Common commands
- 任务1: 命令
- 任务2: 命令

## Failure handling
- 主路径失败时回退策略

## Notes
- 依赖、权限、风险提示
```

---

## 你接下来该怎么学（两周节奏）

第 1 周：轻量型
- `weather -> github -> summarize -> gog`
- 目标：能写出 50 行内、可直接跑的 Skill

第 2 周：流程与系统型
- `find-skills -> agent-browser -> self-improving-agent -> proactive-agent`
- 目标：能写出 150-300 行的流程型 Skill，并有日志/恢复机制

