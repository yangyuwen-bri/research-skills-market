# 科研Skills市场文档索引

## 文档
- `multi-agent-research-skills-market.md`：总体体系框架与指标。
- `multi-agent-operating-guide.md`：执行手册（输入输出契约、评分规则、周流程）。

## 数据样例
- `../data/sample_raw_candidates.json`
- `../data/sample_classified_pool.json`
- `../data/sample_evaluation_cards.json`

## 配置
- `../config/grade.yaml`：分数阈值、权重与测试合规阈值。

## 市场展示
- `index.html`：网站默认首页（展示页，内容同 `market-showcase-v2.html`）。
- `market-showcase-v2.html`：历史兼容入口（同上，仍可直接访问）。
- `market-showcase-v2.md`：结构化文档版市场清单。

## 一键跑通命令
- 默认内置样本（约50条）：
  - `python3 scripts/collect_market_multi_agents.py`
- 以外部文件跑更大规模（支持 JSON/JSONL/CSV）：
  - `python3 scripts/collect_market_multi_agents.py --source-file /path/to/skills.json --max-items 180000`
  - `--source-format` 可显式指定 `json|jsonl|csv`（默认按后缀自动识别）。
- 并发参数：
  - `--scout-workers 6 --classifier-workers 6 --evaluator-workers 6 --tester-workers 6`
  - 当前执行环境若不支持多进程信号量，会自动降级到线程并行。
- 上架策略（推荐）：
  - `--publish-before-test`：先生成可上架目录，所有条目标记为“待测试”，用于先行发布；
  - `--skip-tester`：完全跳过测试阶段；
  - 未使用上述参数时默认会在本轮执行 `top N` 场景测试并回写 `test_status`。
- LLM 参与分类（可选）：
  - `--enable-llm-classifier`：规则预筛后再用大模型判断科研相关性，适合提升召回与精度。
- `--llm-api-key` 或设置 `OPENAI_API_KEY`（兼容脚本新增的 `LLM_API_KEY`）：
  调用兼容 OpenAI 的聊天接口（默认 `https://api.openai.com/v1/chat/completions`）。
- `--llm-model`：如 `gpt-4o-mini`。
- `--llm-api-url`：直接传完整接口地址（如 `https://api.openai.com/v1/chat/completions`），或设置 `LLM_API_URL` 让脚本自动读取。
- 若使用中转服务且地址是域名（如 `https://apidekey.xyz`），本脚本会自动补齐到 `/v1/chat/completions`。
- `--llm-skip-tls-verify`：当前遇到 `certificate verify failed` 时可临时绕过证书校验（仅用于自有环境测试）。
- `--llm-ca-bundle`：可传自定义 CA 证书路径。未配置时优先使用系统证书链，找不到时回退到 certifi 证书包（若已安装）。
  - `--llm-confidence-threshold 0.82`：规则置信度低于该阈值触发 LLM（默认 0.82）。
- `--llm-max-calls`：限制模型调用次数（0 表示不限）。
- `--llm-classify-all`：对全部技能都调用 LLM（通常不建议，除非条目较少时做人工质检前的复核）。
  - `--llm-only-classifier`：完全不走关键词规则，全部由模型判断（推荐与 `--enable-llm-classifier` 同时使用；若无密钥将直接报错）。
- 纯智能示例：
  - `LLM_API_URL=https://apidekey.xyz OPENAI_API_KEY=你的Key python3 scripts/collect_market_multi_agents.py --enable-llm-classifier --llm-only-classifier --llm-model gpt-4o-mini --max-items 0 --classifier-workers 1`
  - `--max-items 0` 表示不截断，按源文件全量跑（例如 `--source-file data/raw/clawhub/clawhub_official_downloads.jsonl --source-format jsonl`）。

- 抓官方 ClawHub 列表（超出 `clawhub explore` 的 1-200 上限）：
  - 推荐：`bash scripts/fetch_clawhub_official.sh --sort downloads --mode auto --limit 200 --pause 0.4 --max-items 0 --out-jsonl data/raw/clawhub/clawhub_official_downloads.jsonl`
  - 如果结果仍偏少且页面返回中未包含分页游标，可直接改 `--mode page` 强制翻页：`bash scripts/fetch_clawhub_official.sh --sort downloads --mode page --limit 200 --pause 0.4 --max-items 0 --out-jsonl data/raw/clawhub/clawhub_official_downloads.jsonl`
  - 该脚本自动做分页（先尝试 `cursor`，回退到 `page/offset`），并生成 JSONL。
  - 如果觉得结果偏少，可加 `--max-pages 0 --max-items 0` 进行完整抓取；脚本会输出 `Estimated total from API`，用于判断这是官方接口返回的总量还是抓取策略问题。
  - 抓到文件后运行：
    - `python3 scripts/collect_market_multi_agents.py --source-file data/raw/clawhub/clawhub_official_downloads.jsonl --source-format jsonl --resolve-repo-links --repo-resolve-limit 0`
    - 若你计划“先上架后慢测”，改成：
      `python3 scripts/collect_market_multi_agents.py --source-file data/raw/clawhub/clawhub_official_downloads.jsonl --source-format jsonl --publish-before-test --test-top 0`
  - 若要更严格区分官方技能页与源码页，可在抓取脚本中保留 `repository_url` 字段后重跑（已支持），默认会优先使用抓取到的源码地址渲染“查看源码”按钮。

## 数据来源说明
- `source_feed` 为空时，脚本会根据 GitHub 组织名自动标注官方性。
- `origin_type` 字段会被计算为 `官方 / 非官方 / 未知`。
- 输出里还带有 `security_level`（低/中/高）与 `security_checks` 风险提示。

## 建议下步落地
1. 在 `data/` 下按阶段新增输出文件：`raw/`、`classified/`、`evaluated/`、`curated/`、`tested/`。
2. 把 `config/grade.yaml` 接入自动化评分脚本（首版可用规则引擎/脚本逐条处理）。
3. 将`market_catalog`渲染为一个Markdown目录页（可放在 `docs/market-catalog.md`）。
4. 如果未来要线上发布，建议将 `market-showcase-v2.html` 接入静态托管并增加 HTTPS 访问入口。

## GitHub Pages 一键上线

你现在就可以直接用 GitHub Pages 上线静态展示页，流程如下：

1. 登录 GitHub 新建一个仓库（比如 `skill-market-site`）。
2. 将当前目录推到该仓库的 `main` 分支（建议 `main` 为默认分支）。
3. 打开仓库设置：`Settings -> Pages`，Source 选 `GitHub Actions`。
4. 推送任意提交后，Actions 会自动运行 `.github/workflows/pages-deploy.yml`：
   - 重新生成 `docs/index.html`（同时保持 `docs/market-showcase-v2.html` 兼容副本）
   - 发布 `docs/` 目录到 Pages

部署成功后，访问地址使用仓库根路径：

```text
https://<你的用户名>.github.io/<仓库名>/
```

（不再需要手动打开 `market-showcase-v2.html`）

本地快速命令（非必须）：

```bash
cd /Users/yuwen/work/research-skills-market
python3 scripts/publish_market_showcase.py --curated data/curated_market_v2.json --output docs/index.html
```

仓库里也提供了一个发布脚本（用于你已接入 git 的环境）：

```bash
bash scripts/deploy_github_pages.sh
```

第一次提交可直接测试用手动触发：

```bash
gh workflow run "GitHub Pages Deploy"
```
