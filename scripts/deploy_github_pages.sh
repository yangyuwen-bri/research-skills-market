#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

if ! command -v git >/dev/null 2>&1; then
  echo "git 未安装，请先安装 Git。"
  exit 1
fi

if [ ! -d .git ]; then
  echo "当前目录不是 git 仓库：$PROJECT_ROOT"
  echo "请先在目标目录执行 git init 或 clone 已有仓库，再继续。"
  exit 1
fi

if [ "${1:-}" = "--help" ]; then
  echo "用法: bash scripts/deploy_github_pages.sh [branch]"
  echo "说明: 默认将当前更改提交到 main，并触发 GitHub Pages 自动部署。"
  echo "示例: bash scripts/deploy_github_pages.sh"
  exit 0
fi

branch="${1:-main}"

echo "同步并重建展示页..."
python3 scripts/publish_market_showcase.py --curated data/curated_market_v2.json --output docs/market-showcase-v2.html

git add docs/market-showcase-v2.html .github/workflows/pages-deploy.yml
git add docs/index.html docs/README.md 2>/dev/null || true

if git diff --cached --quiet; then
  echo "没有可提交的变更。"
  exit 0
fi

if ! git commit -m "chore: update showcase page for GitHub Pages"; then
  echo "提交失败：请先配置 Git 用户信息（user.name / user.email）后重试。"
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "未检测到 origin 远端，先执行：git remote add origin <你的仓库URL>"
  exit 1
fi

git push origin "$branch"
echo "已推送到 origin/$branch，等待 GitHub Actions 完成部署。"
