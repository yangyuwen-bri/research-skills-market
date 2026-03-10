# Skill 写作成长教程（导师版）

更新时间：2026-03-04

## 1) 你要先建立的正确心智模型

Skill 不是“提示词堆砌”，而是一个可维护的微型产品：
- 输入：用户任务与上下文
- 处理：可重复的工作流、决策规则、工具调用
- 输出：稳定的交付格式与质量下限
- 运维：版本迭代、错误修复、性能优化（尤其是 token 成本）

官方定义里，Skill 通常由三部分组成：
- `SKILL.md`（说明+触发条件+流程）
- `scripts/`（确定性步骤，降低模型自由发挥）
- `references/`（按需加载的知识，不污染主上下文）

---

## 2) 学习路径（建议 4 周）

### 第 1 周：吃透官方规范（只学框架，不追求花哨）
目标：你要能写出结构正确、触发明确、边界清晰的 Skill。

1. Anthropic 官方技能仓库 README
2. Claude API Skills Guide（创建/上传/调用）
3. Agent Skills 标准（agentskills.io）

验收标准：
- 你能解释“何时用 SKILL.md 指令、何时下沉到 scripts”。
- 你能写出高质量 `description`，避免误触发。

### 第 2 周：拆优秀 Skill（学组织能力）
目标：学会把复杂能力拆成稳定流程。

重点拆 3 个：
1. `webapp-testing`：决策树 + 黑盒脚本优先
2. `mcp-builder`：阶段化流程 + 引用文档分层
3. `docx`：高约束规范 + 快速参考表 + 明确反模式

验收标准：
- 你能说清每个 Skill 的“约束强度”为何不同。
- 你能复刻一套“同风格骨架”。

### 第 3 周：做你自己的科研 Skill
目标：从 0 到 1 做可用版本。

建议先做一个“科研文献工作流 Skill”（检索→筛选→摘要→引用导出）。

验收标准：
- 至少 5 条真实任务通过。
- 输出格式稳定（结构一致，字段齐全）。

### 第 4 周：评估与迭代（从可用到可靠）
目标：建立工程化反馈回路。

- 增加失败案例集（bad cases）
- 增加测试场景（边界、异常、超长输入）
- 做 token 成本优化（信息分层、按需读取）

验收标准：
- 失败率下降
- token 消耗下降
- 输出一致性提升

---

## 3) 优秀案例拆解（可直接套模板）

### 案例 A：`webapp-testing`（官方）
你该学什么：
- 先“决策树”再执行，避免盲目行动。
- 强调“先跑脚本 --help，再决定是否读源码”，控制上下文成本。
- 明确常见坑（例如动态页面必须 `networkidle` 后再取 DOM）。

可复用模板句式：
- “Always run scripts with `--help` first.”
- “Reconnaissance-then-action pattern.”
- “Common pitfalls: ...”

### 案例 B：`mcp-builder`（官方）
你该学什么：
- 大任务按 Phase 分层（Research → Implementation → Review → Evaluation）。
- 每阶段有明确输入/输出。
- 引导加载外部 reference，而不是把所有知识硬塞进主文档。

可复用模板句式：
- “Phase N: [目标]”
- “Load [reference] when [condition].”
- “Quality checklist: ...”

### 案例 C：`docx`（官方）
你该学什么：
- 高风险领域要高约束（强规则、禁用反模式、详细参数规范）。
- 用“Quick Reference 表格”降低调用成本。
- 复杂规则给出明确“CRITICAL”警示，减少歧义。

可复用模板句式：
- “CRITICAL: ...”
- “✅ CORRECT / ❌ WRONG”
- “Task → Approach”

### 案例 D：`lead-research-assistant`（社区）
你该学什么：
- 任务驱动输出结构很强（评分、优先级、联系策略）。
- 输出模版具体，便于直接交付。

注意点：
- 结构很完整，但约束力度偏中等，遇到高风险任务应再增加边界规则。

---

## 4) 社区实战经验（你要吸收的“坑”）

### 经验 1：大型项目要“总索引 + 领域技能”
来自 `anthropics/claude-code` issue #9959：
- 把单一大文档拆成多个领域 Skill 后，可维护性和一致性明显提升。
- 主文档只做目录与路由（何时用哪个技能）。

可落地做法：
- `CLAUDE.md` 保持轻量索引
- 领域细节放 `skills/<domain>/SKILL.md`

### 经验 2：token 成本是硬指标
来自 `anthropics/skills` issue #497：
- 不要为“定位问题”读完整重内容；先返回轻量索引/元数据，再按需深入。

可落地做法：
- Orientation 阶段只返回导航信息
- 详细读取做成二段式调用

### 经验 3：可从日志自动发现“可技能化流程”
来自 `awesome-claude-skills` PR #296：
- 可观察重复操作模式，自动生成 Skill 初稿。

可落地做法：
- 收集重复任务日志
- 每周归纳“重复 3 次以上”的流程做成 Skill

---

## 5) 你的 Skill 骨架模板（科研向）

```markdown
---
name: literature-workflow
description: Use this skill when the user asks to search papers, screen relevance, summarize evidence, build citations, or draft literature review sections. Do not use for unrelated coding/debug tasks.
---

# Literature Workflow

## When to Use
- 任务触发条件（明确）

## When NOT to Use
- 非目标场景（明确）

## Inputs Required
- 主题、时间范围、领域、输出语言、引用格式

## Workflow
### Phase 1: Retrieval
- 数据源、检索策略、结果上限

### Phase 2: Screening
- 纳入/排除标准

### Phase 3: Synthesis
- 证据分组、冲突点、研究空白

### Phase 4: Output
- 固定输出格式（表格/JSON/Markdown）

## Output Contract
- 必须包含字段：`question`, `method`, `key_findings`, `limitations`, `citations`

## Failure Handling
- 数据不足时怎么降级
- 来源冲突时怎么标注

## Scripts
- 先 `scripts/xxx --help`

## References
- 当需要引用格式时读取 `references/citation_style.md`
- 当需要筛选标准时读取 `references/screening_rules.md`
```

---

## 6) 评估标准（你写完必须自测）

每个 Skill 用下面 10 项打分（每项 0/1）：
1. 触发条件是否清晰
2. 非触发边界是否清晰
3. 输出格式是否固定
4. 是否有失败降级策略
5. 是否有常见坑提示
6. 是否把高确定性步骤下沉到 `scripts/`
7. 是否采用 progressive disclosure（主文档精简，细节按需读）
8. 是否标注性能/成本约束
9. 是否有至少 3 条真实任务样例
10. 是否可维护（结构清晰、无重复矛盾）

建议上线阈值：`>= 8/10`。

---

## 7) 你从今天开始的训练计划（导师作业）

第 1 轮（今天）：
- 选一个科研场景（如文献综述）
- 按上面模板写 `v0.1`
- 我来帮你做逐段 review

第 2 轮（明天）：
- 增加 `scripts/` 一条（哪怕只做检索参数标准化）
- 增加 5 条测试任务

第 3 轮（后天）：
- 做一次“失败样例复盘”
- 输出 `v0.2`（修复触发误判和输出不稳定）

---

## 8) 参考资料（本教程来源）

官方：
- Anthropic skills repo: https://github.com/anthropics/skills
- Claude API Skills Guide: https://docs.claude.com/en/api/skills-guide
- Agent Skills specification: https://agentskills.io/specification
- Agent Skills blog: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

社区与讨论：
- Claude Code issue #9959 (文档拆分模式): https://github.com/anthropics/claude-code/issues/9959
- anthropics/skills issue #497 (token 成本优化思路): https://github.com/anthropics/skills/issues/497
- awesome-claude-skills PR #296 (从使用模式生成 skill): https://github.com/ComposioHQ/awesome-claude-skills/pull/296

案例仓库：
- 官方示例（docx / mcp-builder / webapp-testing）: https://github.com/anthropics/skills/tree/main/skills
- 社区示例（lead-research-assistant 等）: https://github.com/ComposioHQ/awesome-claude-skills
