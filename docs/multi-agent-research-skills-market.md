# 科研Skills市场多Agent协作体系设计（v1.0）

## 1. 目标
把“全网技能源头发现 → 研究相关筛选 → 质量评估 → 上市整理 → 改编优化 → 测试迭代”固定为可执行的流水线，围绕科研场景（文献、实验、数据、代码复现、写作、知识管理）产出可直接上手的 Skills 市场。

## 2. 总体闭环
`发现(Scout) -> 筛选(Classifier) -> 评估(Evaluator) -> 策展(Curator) -> 改编(Adapter) -> 测试(Tester) -> 回流(问题数据库/新任务)`

## 3. 组织边界与角色

### Agent 1：Scout（侦察兵）
- 定位：高覆盖抓取，不做质量判断。
- 采集渠道：GitHub、HuggingFace、Reddit、X、Discord、博客、社区索引。
- 输出：`raw_candidates`（原始候选池）。

### Agent 2：Classifier（分类员）
- 定位：科研适配性判定与结构化分类。
- 输出：`classified_pool`（结构化清单）。

### Agent 3：Evaluator（评估员）
- 定位：可直接使用视角下的质量评估与风险审核。
- 输出：`evaluation_cards`（可用性卡片）。

### Agent 4：Curator（策展人）
- 定位：用户可发现性与发布形态设计。
- 输出：`market_catalog`（市场目录）。

### Agent 5：Adapter（改编师）
- 定位：最小改动落地化改造。
- 输出：`adapted_skills`（改编PR/文件）。

### Agent 6：Tester（测试员）
- 定位：真实场景验证与回归。
- 输出：`test_report`（通过率与问题库）。

## 4. 数据模型（建议落地为JSON/DB）

### 4.1 `raw_candidate`
```json
{
  "id": "uuid",
  "name": "string",
  "source": "github|huggingface|reddit|x|discord|blog",
  "url": "https://...",
  "description": "string",
  "raw_snapshot_date": "YYYY-MM-DD",
  "metadata": {
    "stars": 0,
    "forks": 0,
    "last_commit": "YYYY-MM-DD",
    "active_issues": 0,
    "last_issue_update": "YYYY-MM-DD"
  }
}
```

### 4.2 `classified_skill`
```json
{
  "candidate_id": "uuid",
  "is_research_related": true,
  "research_stages": ["文献检索", "实验设计", "数据分析", "论文写作", "可视化", "复现", "知识管理"],
  "research_domains": ["生物", "计算机", "心理", "物理"],
  "tech_stack": ["python", "rust", "web", "mcp"],
  "tags": ["可复现", "生物信息"],
  "filter_reason": "可选，不通过时说明原因"
}
```

### 4.3 `evaluation_card`
```json
{
  "classified_id": "uuid",
  "quality_score": {
    "code": 4,
    "maintainability": 4,
    "maturity": 3,
    "usability": 3,
    "security": 2
  },
  "grade": "可直接用|需小改|仅参考|不推荐",
  "pros": ["..."],
  "risks": ["..."],
  "usage_requirements": ["需API key", "需本地依赖"],
  "evidence": ["链接/截图/测试记录"],
  "next_owner": "Adapter|Curator|Archive"
}
```

### 4.4 `market_entry`
```json
{
  "evaluation_id": "uuid",
  "one_line": "一句话说明",
  "scene": "适用场景",
  "quick_start": "30分钟内可用步骤",
  "discipline_view": "按学科映射",
  "bundle_ids": ["文献综述套装", "数据分析五件套"],
  "status": "发布|试用|下线",
  "test_status": "待测试|已测试-通过|已测试-需改进|已测试-未通过",
  "test_verdict": "待测试|通过|需改进|..."
}
```

### 4.5 `adapt_plan`（Adapter 输出）
```json
{
  "target_id": "uuid",
  "issues_found": ["..."],
  "changes": ["最小改动说明"],
  "compatibility_map": "与原始版本差异边界",
  "pr": "patch链接或文件路径",
  "rollback_plan": "回滚策略"
}
```

### 4.6 `test_report`
```json
{
  "skill_id": "uuid",
  "task_suite": ["task_name", "result"],
  "pass_rate": 0.83,
  "failure_cases": ["..."],
  "baseline_compare": {
    "before": {"pass_rate": 0.5},
    "after": {"pass_rate": 0.83}
  },
  "recommendation": "通过|需进一步改造|淘汰"
}
```

## 5. 交付标准

### Scout 输出标准
- 缺失率：关键字段完整率 >= 95%
- 去重：URL与仓库名组合去重
- 覆盖：每周新增样本增长 >= 20%（若源稳定时至少持平上周）

### Classifier 输出标准
- `is_research_related` 判定准确率：与人工抽检一致率 >= 90%
- 标签体系一致性：同类技能标签重叠度一致率 >= 80%

### Evaluator 输出标准
- 关键指标覆盖率：5 项得分全部具备
- 风险提示覆盖率：每条推荐至少 1 条风险或边界说明
- 决策一致性：不同评估者互评差异 <= 1 个等级

### Curator 输出标准
- 所有上架项须含：一句话描述、场景、快速上手
- 页面检索命中率：通过关键词找到目标条目 >= 95%
- 目录完整性：每周新上架项必须归类到至少 1 个主类 + 1 个流程节点

### Adapter 输出标准
- 改动说明可追溯至 `evaluation_card` 风险
- 兼容性：不改变原始技能核心语义与主入口参数
- 回滚时长：可在 10 分钟内回滚到原版

### Tester 输出标准
- 覆盖场景：每个上架项至少 3 个科研任务场景
- 通过率阈值：面向新手上手任务 >= 80%
- 报告闭环：重大问题在 72 小时内生成改造任务

## 6. 阶段化执行建议

### P0（1-2 周）
- 上线 Scout + Classifier + Evaluator，跑通最小流水线。
- 首批标准化字段与评分表。

### P1（第3-4周）
- 引入 Curator 目录模板，发布“首发市场页”。
- 建立每周评估会与问题库。

### P2（第5-8周）
- 启动 Adapter 与 Tester 并行，形成原版/改编版对照。
- 建立实验化指标：上架留存、重复报修率、文档完善度。

### P3（第9周起）
- 增加自动化脚本化抓取、测试编排、告警。
- 引入订阅与版本控制（catalog v1/v2）。

## 7. 关键运行机制（避免碎片化）
- 使用统一 ID：`skill_id` 贯通所有 agent，避免同名冲突。
- 统一优先级：评分卡->策展->测试，测试失败不会“自动下线”，而是触发改编或标记“待修”。
- 争议机制：评分边界不一致触发复核人（双人复评）。
- 问题闭环：Tester 记录的问题进入 `backlog`，由 Classifier/Adapter 周度复评。

## 8. 可落地流程图（文字版）
1) Scout 每周五前提交 `raw_candidates`
2) Classifier 次日完成分类与标签并标红不相关项
3) Evaluator 对 `is_research_related=true` 项做评分
4) Curator 构建可发布目录并形成 `market_entry`
5) Adapter 按“需小改”触发最小改造
6) Tester 执行场景回归并输出 pass/reject
7) 管理员审核是否发布（或退回）
8) 周报同步：新增、淘汰、待改、问题 Top3

## 9. 推荐补充模板（可直接套用）

### 9.1 科研任务场景模板（Tester）
- 文献综述：给定5篇核心论文，要求输出研究趋势+缺口
- 数据分析：给定公开数据集，完成清洗+统计+可视化
- 复现实验：给定原始代码/方法，生成可重复执行步骤
- 论文写作：给定实验结果，产出 methods/results/discussion 草稿

### 9.2 上架文案模板（Curator）
- 一句话：`面向X场景，解决Y问题，擅长Z。`
- 适用场景：`课程作业/课题研究/实验室日常/跨学科协作`
- 快速上手：`安装 -> 配置 -> 一条样例命令 -> 一条结果验证指令`

## 10. 迭代监控指标
- 周新采集候选数、有效科研候选数、可用项新增数
- 平均评估时延（提交到可测试时间）
- 上架后 14 天复用率与问题率
- Adapter 改造收益（原始 pass_rate -> 改造 pass_rate）
- 用户反馈：收藏率、跳出率、五星评论率

## 11. 人工干预边界
- 严禁盲目批量上架：任何 `不推荐` 项不得进入市场。
- 严禁未评估发布：`evaluation_card` 缺失即不发布。
- 未完成 `security` 检查的项默认标记“高风险，不推荐”。

---
该框架用于把“发现-上架-测试”变成可复制流程。下一步建议先补齐每个 Agent 的输入输出 API（字段+状态机），再开始首轮样本运行。
