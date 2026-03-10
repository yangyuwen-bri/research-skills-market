# OpenClaw Skill 体验官（独立测试空间）

这个目录是**可迁移到 OpenClaw 的独立体验空间**，目标是：

- 每天跑 10 个 skill 的“对话场景”  
- 场景由“真实用户一句话输入”驱动  
- 输出可直接发给同事/群组的体验报告（Markdown）

## 目录结构

- `config/skill_cases.json`  
  10 个场景定义：技能名、用户发言、预期助理回复方向、验证命令。
- `references/skill_pages/*.md`  
  10 个 skill 的能力说明摘录，确保不依赖远端仓库。
- `runtime_scripts/`  
  需要本地可复现实验的脚本（如 polymarket / ontology / weather）。
- `runtime_scripts/weather/weather_probe.py`  
  天气场景主备源探测脚本，wttr.in 失败会自动切到 open-meteo 并仍能继续判定。
- `scripts/run_daily_skill_experience.py`  
  对话场景执行器：逐条运行场景、采集命令输出、打分并生成报告。
- `scripts/run_daily10_skill_tests.sh`  
  统一入口，建议放入 cron / openclaw 定时任务。
- `reports/`  
  每日产出目录（日期+时间戳的 md 报告）。

## 快速跑一遍

```bash
cd /path/to/openclaw_skill_experience_agent
bash scripts/run_daily10_skill_tests.sh
```

报告示例：

- `reports/2026-03-02_openclaw_skill_experience_124500.md`
- `reports/2026-03-02_openclaw_skill_experience_124500.json`（`--include-json`）

## OpenClaw 迁移建议

你可以把整个文件夹拷贝到 OpenClaw 的工作区，然后手动执行：

```bash
openclaw agents add skill-experience \
  --workspace /path/to/openclaw_skill_experience_agent \
  --non-interactive
```

迁移后在该 agent 的消息处理里，绑定一条定时规则或手动触发：

```bash
cd /path/to/openclaw_skill_experience_agent
bash scripts/run_daily10_skill_tests.sh
```

> 说明：`agents add` 行为在不同 OpenClaw 版本有差异，若命令参数不兼容可先用 `openclaw agents add --help` 校验参数。

## 你会得到什么

当前套件默认测试 10 个“热门+实操”场景（可按需替换）：
- `find-skills`, `weather`, `github`, `ontology`, `agent-browser`
- `vercel-react-best-practices`, `web-design-guidelines`, `openai-whisper`, `summarize`, `self-improving-agent`

每个 case 都有：

- 真实用户口播问题（可直接贴到对话里）
- 预计回复方向（让助理对齐风格）
- 执行检查（命令、退出码、输出片段）
- 结论：`PASS / DEGRADED / FAIL`
- 能力定位：每个场景对应什么业务动作、给什么对话建议

`DEGRADED` 的场景通常是“技能可用，但缺少外部依赖”，不是完全不可用。
