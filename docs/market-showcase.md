# 科研Skills市场展示（版本：2026-02-27）

## 1. 市场总览
以下为当前可发布候选的科研 Skills 目录。每条都经过 `Scout -> Classifier -> Evaluator` 处理，并给出状态、适配场景、快速上手与风险提示。

- 总筛选规模：3
- 研究相关：2
- 上架中：2
- 待改造：1（需小改）

---

## 2. 按科研流程分类

### A. 文献检索与综述

#### 1) Paper Trend Summarizer（直接可用）
- 来源：GitHub `paper-trend-summarizer`
- 标签：`文献检索` `论文写作` `研究空白识别`
- 学科：`生物医学` `计算机`
- 评估：`可直接用`，综合评分较高（安全性良好）
- 适用场景：
  - 写综述/研究计划时快速扫描近年文献趋势
  - 生成研究问题清单与可检验假设
  - 辅助方法章节中的背景梳理
- 快速上手：
  1. 安装依赖：`pip install paper-trend-summarizer`
  2. 准备 5-20 条核心论文 DOI 或关键词
  3. 执行：`paper-summary run --input papers.txt --outdir ./out`
  4. 检查输出中的“研究空白”与“可复用方法链路”
- 风险提示：
  - 依赖外部学术数据库，网络抖动时摘要质量可能波动
  - 建议复核关键信息链路，避免“幻觉式归纳”

### B. 数据处理与复现

#### 2) Dataset Cleaning Pipeline（需小改）
- 来源：GitHub `dataset-cleaning-pipeline`
- 标签：`数据分析` `复现` `可视化`
- 学科：`通用科研`
- 评估：`需小改`，主要问题是依赖与环境约束未锁定
- 适用场景：
  - 导入实验数据（CSV/TSV）进行缺失值处理与一致性检查
  - 自动生成清洗报告（缺失率、异常值、分布漂移）
  - 为后续统计分析/绘图提供预处理脚本
- 快速上手：
  1. 克隆仓库并创建虚拟环境
  2. 安装：`pip install -r requirements.txt`
  3. 建议先升级：固定依赖版本（如 `pandas==2.x`）
  4. 运行 `clean --input data.csv --report ./report` 生成预处理报告
- 风险提示：
  - 依赖版本未锁定，可能出现兼容性问题
  - 对少量非常规格式数据需要手工补充清洗规则
- 推荐：进入改编池，由 Adapter 完成最小兼容修复后再大规模使用

### C. 非科研相关（已过滤）
- `Fun Chatbot Skill`
- 结论：`不推荐`（当前未通过科研适配性）

---

## 3. 按学科标签分类

### 生物医学
- Paper Trend Summarizer

### 计算机/AI
- Paper Trend Summarizer

### 通用科研（跨学科）
- Dataset Cleaning Pipeline

---

## 4. 按成熟度分类

### 可直接上手（高）
- Paper Trend Summarizer

### 需小改（中）
- Dataset Cleaning Pipeline

### 仅参考/不推荐（低）
- 无

---

## 5. 推荐使用合集（Bundle）

### 1. 文献综述套装
- Paper Trend Summarizer
- 使用步骤：先跑文献摘要 → 抽取研究空白 → 输出 3-5 个可行研究问题 → 转交写作模块

### 2. 数据分析五件套（预备版）
- Dataset Cleaning Pipeline（改造后版本）
- 目标组件：清洗、缺失处理、异常识别、可视化检查、输出复现实验参数
- 说明：当前为“需小改”版本，适合愿意做轻量工程改造的小组

---

## 6. 每周更新示例（可直接展示）
- 本周新增：0
- 本周通过：1（Paper Trend Summarizer）
- 本周待改：1（Dataset Cleaning Pipeline）
- 本周淘汰：1（Fun Chatbot Skill）

---

## 7. 当前可尝试路径（给最终用户）
1. 新手/综述方向：优先使用 `Paper Trend Summarizer`，先拿“可复核的研究问题清单”。
2. 数据实验方向：先试用 `Dataset Cleaning Pipeline` 的原始版进行小数据集验证，再看适配后稳定版。 
3. 导师/团队协作：在 `文献综述套装` 中统一定义输出模板，保持研究问题与方法章节的风格一致。

## 8. 下一步（系统已就绪）
- 将本页面挂到市场首页（`docs/market-showcase.md` -> 对外展示）
- 把 `Dataset Cleaning Pipeline` 交给 Adapter 完成小改版后更新“推荐级别”
- 按周发布 `docs/market-changelog.md`，展示新增、淘汰、复验结果
