# 多Agent协作体系执行手册（续）

## A. 目标
将多Agent体系从“思路文档”变成“可分发执行动作”：
- 每个Agent有明确输入契约
- 每个输出可被下一个Agent直接消费
- 每周形成可追踪的处理记录和可复用模板

## B. 全局工作流状态机

```text
RAW_CANDIDATE -> CLASSIFIED -> EVALUATED -> CURATED -> ADAPTED(optional) -> TESTED -> PUBLISHED
                  -> FILTERED_OUT(任一阶段可淘汰)
```

### 推荐状态字段
- `status`: 当前状态
- `owner`: 当前处理Agent
- `next_owner`: 下游接收人
- `risk`: 风险级别（高/中/低）
- `priority`: P0/P1/P2/P3

## C. 每日周期开启（建议）
1. 周一：Scout导入候选池
2. 周二：Classifier完成分类与标签
3. 周三：Evaluator打分
4. 周四：Curator完成目录化（同时给Adapter发起改造单）
5. 周五：Tester完成验收和回流

## D. 各Agent输入/输出契约（强制）

### D1. Scout
- 输入：
  - `research_scope`（科研方向）
  - `time_window_days`（抓取时间窗）
- 输出：`raw_candidates.json`

```json
{
  "agent": "scout",
  "created_at": "YYYY-MM-DD",
  "window_days": 7,
  "items": [
    {
      "id": "uuid",
      "name": "",
      "source": "github|huggingface|x|reddit|discord|blog",
      "url": "https://...",
      "desc_raw": "",
      "stars": 0,
      "forks": 0,
      "watchers_7d": 0,
      "last_commit": "YYYY-MM-DD",
      "activity_hint": "issues/commits/discussions",
      "collected_by": "scout-bot-v1"
    }
  ]
}
```

规则：
1) 禁止主观判定，只输出“被发现”项。
2) 去重依据 `url`。
3) 每项需至少三项可追溯证据（URL正文、stars、更新动态）。

### D2. Classifier
- 输入：`raw_candidates.json`
- 输出：`classified_pool.json`

```json
{
  "agent": "classifier",
  "reviewed_at": "YYYY-MM-DD",
  "items": [
    {
      "candidate_id": "uuid",
      "is_research_related": true,
      "research_stage": ["文献检索", "实验设计", "数据分析", "论文写作", "复现", "知识管理", "可视化"],
      "domain": ["生物医学", "材料", "教育", "人工智能", "社会科学"],
      "dependencies": ["python", "mcp", "docker"],
      "fit_reason": "",
      "reject_reason": ""
    }
  ]
}
```

规则：
1) `is_research_related=false` 的项直接标记 `FILTERED_OUT`。
2) 每项必填 `fit_reason` 或 `reject_reason`（二选一）。

### D3. Evaluator
- 输入：`classified_pool.json`
- 输出：`evaluation_cards.json`

```json
{
  "agent": "evaluator",
  "assessed_at": "YYYY-MM-DD",
  "items": [
    {
      "classified_id": "uuid",
      "scores": {
        "code_quality": 1,
        "docs": 1,
        "maintainability": 1,
        "maturity": 1,
        "usability": 1,
        "security": 1
      },
      "grade": "可直接用|需小改|仅参考|不推荐",
      "security_checks": ["依赖审阅", "权限边界", "数据外泄风险"],
      "notes": "风险与局限"
    }
  ]
}
```

规则：
1) 代码质量与安全字段必须给出 1-5 分。
2) `grade` 与 `max`/`min` 分数一致（可见下文阈值）。
3) 安全分数 <=2 自动标记阻断，不允许上架。

### D4. Curator
- 输入：`evaluation_cards.json`
- 输出：`market_catalog.json`

```json
{
  "agent": "curator",
  "published_at": "YYYY-MM-DD",
  "entries": [
    {
      "evaluation_id": "uuid",
      "title": "",
      "one_line": "",
      "use_case": "",
      "quick_start": ["步骤1", "步骤2", "步骤3"],
      "difficulty": "入门|进阶",
      "category_path": ["流程", "文献", "数据分析", "写作"],
      "bundle_ids": ["文献综述套装", "数据分析五件套"],
      "status": "draft|published|retest"
    }
  ]
}
```

规则：
1) 进入 `published` 的条目必须含 `quick_start` 且不少于 3 步。
2) 一条技能至少挂在 1 个`category_path`和 1 个`research_stage`。

### D5. Adapter
- 输入：`evaluation_cards.json` + `feedback`
- 输出：`adapt_requests.json` + 改造产物路径

```json
{
  "agent": "adapter",
  "ticket_id": "uuid",
  "source_id": "uuid",
  "plan": {
    "goal": "",
    "minimal_change": true,
    "changes": ["", ""],
    "rollback": "git revert / patch revert"
  },
  "result": {
    "diff_summary": "",
    "compatibility": "保留原始接口参数",
    "validation": "通过最小化回归测试"
  }
}
```

规则：
1) 仅改造 grade=`需小改` 的条目。
2) 明确“与原版差异边界”。

### D6. Tester
- 输入：`market_catalog.json` + `adapted_skill`
- 输出：`test_report.json`

```json
{
  "agent": "tester",
  "run_at": "YYYY-MM-DD",
  "items": [
    {
      "skill_id": "uuid",
      "task_set": [
        {
          "case_id": "T1",
          "scenario": "文献综述",
          "pass": true,
          "latency_sec": 120,
          "notes": ""
        }
      ],
      "summary": {
        "pass_rate": 0.86,
        "avg_latency_sec": 150,
        "top_failures": ["..."]
      },
      "verdict": "通过|需改造|不通过"
    }
  ]
}
```

规则：
1) 每项至少3个场景。
2) `pass_rate < 0.8` 的任务触发回流。

## E. 评分规则（建议阈值）
- `总分=(code_quality*0.20 + docs*0.10 + maintainability*0.20 + maturity*0.20 + usability*0.20 + security*0.10)`
- `可直接用`：总分 >= 4.3，且 security >= 4
- `需小改`：3.0 <= 总分 < 4.3，且 non-blocking 风险
- `仅参考`：2.0 <= 总分 < 3.0 或存在中等风险
- `不推荐`：总分 < 2.0 或 security <=2

## F. 自动化最小脚本清单（可直接加到仓库）
- `pipeline/dedup.py`：按 URL 去重 + 标准化字段
- `pipeline/validate_schema.py`：校验 6 种输出是否满足字段约束
- `pipeline/kpi.py`：输出周报指标
- `pipeline/render_catalog.py`：把 `market_catalog.json` 渲染为网页/markdown

你可以在首期只做轻量版脚本：
1) Python脚本 + CSV 输入
2) 手工复核每个JSON字段

## G. 示例：每周处理演示（小样本）

### 原始发现（Scout）
- `A`：开源文献检索增强工具
- `B`：实验数据清洗流水线模板
- `C`：娱乐型闲聊bot skill

### 分类（Classifier）
- `A` => research_related=true，阶段=文献检索，领域=生物医学
- `B` => research_related=true，阶段=数据分析，领域=通用科研
- `C` => research_related=false，直接过滤

### 评估（Evaluator）
- `A` => 4.5，可直接用
- `B` => 3.2，需小改（安装脚本依赖缺失）

### 策展（Curator）
- 形成两条上架候选
- `B` 备注“已进入改编队列”

### 改编（Adapter）
- `B` 增加requirements说明和本地环境模板

### 测试（Tester）
- `A` pass_rate 0.9（通过）
- `B` 改造后 pass_rate 0.83（通过）

---

### 你可以直接执行的下一步
1. 用本文件定义“每日输入文件名”和目录（例如 `data/raw/`、`data/classified/`）。
2. 把 E 部分的分数阈值固化成配置文件（`config/grade.yaml`）。
3. 先跑 20 条样本，产出第一版周报。
