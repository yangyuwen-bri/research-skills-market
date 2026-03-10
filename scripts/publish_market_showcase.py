#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


def _safe(value):
    return value if isinstance(value, str) else ""


def _is_clawhub_url(raw: str) -> bool:
    if not isinstance(raw, str) or not raw:
        return False
    host = (urlparse(raw).netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host.endswith("clawhub.ai")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build simplified market showcase page")
    parser.add_argument("--curated", default="data/curated_market_v2.json")
    parser.add_argument("--output", default="docs/index.html")
    args = parser.parse_args()

    curated_path = Path(args.curated)
    output_path = Path(args.output)
    curated = json.loads(curated_path.read_text(encoding="utf-8"))

    items = []
    for ent in curated.get("entries", []):
        source = _safe(ent.get("canonical_source_url")) or _safe(ent.get("repo_url"))
        source_url = _safe(ent.get("source_url"))
        clawhub_page = _safe(ent.get("clawhub_page_url"))
        platform_url = clawhub_page or (source_url if _is_clawhub_url(source_url) else "")
        items.append(
            {
                "title": _safe(ent.get("title_zh")) or _safe(ent.get("title")),
                "summary": _safe(ent.get("one_line_zh")) or _safe(ent.get("one_line")),
                "stage": _safe(ent.get("use_case_zh")) or _safe(ent.get("use_case")),
                "grade": _safe(ent.get("grade")) or "需小改",
                "test_status": _safe(ent.get("test_status")) or "待测试",
                "difficulty": _safe(ent.get("difficulty_zh")) or _safe(ent.get("difficulty")) or "进阶",
                "source_url": source,
                "platform_url": platform_url,
                "git_clone": _safe(ent.get("git_clone")),
                "source_status": _safe(ent.get("source_status")) or ("verified" if source else "missing"),
                "source_confidence": ent.get("source_confidence", 0),
            }
        )

    payload = json.dumps({"items": items}, ensure_ascii=False).replace("</script>", "<\\/script>")

    html = """<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Research Skills Market</title>
  <style>
    :root {
      --bg0: #061326;
      --bg1: #0b2241;
      --panel: #102748;
      --panel2: #0d2140;
      --line: #2d5d93;
      --txt: #ebf4ff;
      --muted: #9fbbdb;
      --ok: #7ff0b5;
      --warn: #ffd27d;
      --bad: #ff9a96;
      --btn: #7fd0ff;
      --btn2: #163f73;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--txt);
      font-family: \"IBM Plex Sans\", \"Noto Sans SC\", \"PingFang SC\", sans-serif;
      background: radial-gradient(1200px 520px at 10% -10%, #1b4f7e 0%, transparent 55%),
                  radial-gradient(950px 480px at 100% 0%, #0d3f6d 0%, transparent 52%),
                  linear-gradient(180deg, var(--bg1), var(--bg0));
      min-height: 100vh;
      padding: 22px;
    }
    .wrap { max-width: 1160px; margin: 0 auto; }
    .hero {
      background: linear-gradient(140deg, rgba(127,208,255,0.18), rgba(255,255,255,0.03));
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
    }
    h1 { margin: 0; font-size: 34px; letter-spacing: .3px; }
    .sub { margin-top: 6px; color: var(--muted); }
    .filters {
      margin-top: 14px;
      display: grid;
      grid-template-columns: 1.6fr 1fr 1fr 1fr;
      gap: 10px;
    }
    label { display: block; font-size: 12px; color: var(--muted); margin-bottom: 5px; }
    input, select {
      width: 100%;
      border-radius: 10px;
      border: 1px solid var(--line);
      background: #0a1b36;
      color: var(--txt);
      padding: 10px;
    }
    .stats {
      margin-top: 12px;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .chip {
      border: 1px solid var(--line);
      background: #0a1f3b;
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 13px;
    }
    .grid {
      margin-top: 14px;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 12px;
    }
    .card {
      border: 1px solid var(--line);
      border-radius: 14px;
      background: linear-gradient(180deg, var(--panel), var(--panel2));
      padding: 12px;
    }
    .title { margin: 0; font-size: 19px; line-height: 1.35; }
    .meta {
      margin-top: 8px;
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      color: var(--muted);
      font-size: 12px;
    }
    .tag {
      border-radius: 999px;
      padding: 2px 8px;
      font-size: 12px;
    }
    .ok { background: rgba(127,240,181,.18); color: var(--ok); }
    .warn { background: rgba(255,210,125,.18); color: var(--warn); }
    .bad { background: rgba(255,154,150,.18); color: var(--bad); }
    .summary { margin-top: 8px; color: #d9e8fb; font-size: 14px; }
    .actions { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 8px; }
    .btn {
      border: 0;
      border-radius: 9px;
      padding: 8px 10px;
      font-size: 13px;
      cursor: pointer;
      text-decoration: none;
      color: var(--txt);
      background: var(--btn2);
    }
    .btn-main { background: var(--btn); color: #06213d; font-weight: 600; }
    .empty { border: 1px dashed var(--line); border-radius: 12px; padding: 20px; color: var(--muted); }
    .toast {
      position: fixed;
      right: 20px;
      bottom: 20px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #112a4e;
      padding: 9px 12px;
      opacity: 0;
      transform: translateY(6px);
      transition: .2s;
    }
    .toast.show { opacity: 1; transform: translateY(0); }
    @media (max-width: 880px) { .filters { grid-template-columns: 1fr 1fr; } }
    @media (max-width: 640px) {
      body { padding: 12px; }
      h1 { font-size: 25px; }
      .filters { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class=\"wrap\">
    <section class=\"hero\">
      <h1>Research Skills Market / 科研技能市场</h1>
      <p class=\"sub\">只展示对用户有用的信息：能做什么、适用场景、可用性、是否有可用源码。</p>
      <div class=\"filters\">
        <div>
          <label>关键词</label>
          <input id=\"keyword\" type=\"text\" placeholder=\"技能名 / 描述 / 场景\" />
        </div>
        <div>
          <label>场景</label>
          <select id=\"stage\"><option value=\"all\">全部</option></select>
        </div>
        <div>
          <label>可用性</label>
          <select id=\"grade\">
            <option value=\"all\">全部</option>
            <option value=\"可直接用\">可直接用</option>
            <option value=\"需小改\">需小改</option>
            <option value=\"仅参考\">仅参考</option>
          </select>
        </div>
        <div>
          <label>源码状态</label>
          <select id=\"source\">
            <option value=\"all\">全部</option>
            <option value=\"verified\">仅可用源码</option>
            <option value=\"missing\">无可用源码</option>
          </select>
        </div>
      </div>
      <div class=\"stats\">
        <span class=\"chip\">上架总数: <strong id=\"published\">0</strong></span>
        <span class=\"chip\">可用源码: <strong id=\"withSource\">0</strong></span>
        <span class=\"chip\">筛选结果: <strong id=\"matched\">0</strong></span>
      </div>
    </section>
    <main id=\"grid\" class=\"grid\"></main>
  </div>
  <div id=\"toast\" class=\"toast\">已复制安装命令</div>
  <script>
    const market = __PAYLOAD__;
    const els = {
      keyword: document.getElementById('keyword'),
      stage: document.getElementById('stage'),
      grade: document.getElementById('grade'),
      source: document.getElementById('source'),
      published: document.getElementById('published'),
      withSource: document.getElementById('withSource'),
      matched: document.getElementById('matched'),
      grid: document.getElementById('grid'),
      toast: document.getElementById('toast'),
    };

    const esc = (v) => String(v ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');

    const firstStage = (v) => String(v || '').split(',').map(s => s.trim()).filter(Boolean)[0] || '待补充';
    const allStages = Array.from(new Set(market.items.map((x) => firstStage(x.stage)))).sort();
    allStages.forEach((s) => {
      const opt = document.createElement('option');
      opt.value = s;
      opt.textContent = s;
      els.stage.appendChild(opt);
    });

    const gradeClass = (g) => g === '可直接用' ? 'ok' : g === '需小改' ? 'warn' : 'bad';

    const toast = (text) => {
      els.toast.textContent = text;
      els.toast.classList.add('show');
      setTimeout(() => els.toast.classList.remove('show'), 1100);
    };

    const copyCmd = async (cmd) => {
      if (!cmd) {
        toast('当前条目没有安装命令');
        return;
      }
      try {
        await navigator.clipboard.writeText(cmd);
        toast('已复制安装命令');
      } catch {
        toast('复制失败');
      }
    };

    const renderCard = (item) => {
      const title = esc(item.title);
      const summary = esc(item.summary || '');
      const stage = esc(firstStage(item.stage));
      const grade = esc(item.grade || '需小改');
      const testStatus = esc(item.test_status || '待测试');
      const difficulty = esc(item.difficulty || '进阶');
      const sourceStatus = item.source_status === 'verified' ? '可用源码' : '无可用源码';
      const sourceTag = item.source_status === 'verified' ? 'ok' : 'bad';
      const sourceBtn = item.source_url ? `<a class=\"btn btn-main\" href=\"${esc(item.source_url)}\" target=\"_blank\" rel=\"noopener\">查看源码</a>` : '';
      const platformBtn = item.platform_url ? `<a class=\"btn\" href=\"${esc(item.platform_url)}\" target=\"_blank\" rel=\"noopener\">去Clawhub使用</a>` : '';
      const cloneBtn = `<button class=\"btn\" data-copy=\"${esc(item.git_clone || '')}\">复制安装命令</button>`;
      return `<article class=\"card\">
        <h3 class=\"title\">${title}</h3>
        <div class=\"meta\">
          <span class=\"tag ${gradeClass(item.grade)}\">${grade}</span>
          <span class=\"tag ${sourceTag}\">${sourceStatus}</span>
          <span>场景: ${stage}</span>
          <span>门槛: ${difficulty}</span>
          <span>测试: ${testStatus}</span>
        </div>
        <div class=\"summary\">${summary}</div>
        <div class=\"actions\">${sourceBtn}${platformBtn}${cloneBtn}</div>
      </article>`;
    };

    const applyFilter = () => {
      const keyword = els.keyword.value.trim().toLowerCase();
      const stage = els.stage.value;
      const grade = els.grade.value;
      const sourceState = els.source.value;

      const all = market.items;
      const visible = all.filter((item) => {
        const text = `${item.title} ${item.summary} ${item.stage}`.toLowerCase();
        const byKeyword = !keyword || text.includes(keyword);
        const byStage = stage === 'all' || firstStage(item.stage) === stage;
        const byGrade = grade === 'all' || item.grade === grade;
        const bySource = sourceState === 'all' || (item.source_status || 'missing') === sourceState;
        return byKeyword && byStage && byGrade && bySource;
      });

      els.published.textContent = String(all.length);
      els.withSource.textContent = String(all.filter((x) => x.source_status === 'verified').length);
      els.matched.textContent = String(visible.length);

      if (!visible.length) {
        els.grid.innerHTML = '<div class=\"empty\">当前条件没有匹配结果，换个关键词或筛选条件试试。</div>';
        return;
      }

      els.grid.innerHTML = visible.map(renderCard).join('');
      els.grid.querySelectorAll('button[data-copy]').forEach((btn) => {
        btn.addEventListener('click', () => copyCmd(btn.getAttribute('data-copy') || ''));
      });
    };

    els.keyword.addEventListener('input', applyFilter);
    els.stage.addEventListener('change', applyFilter);
    els.grade.addEventListener('change', applyFilter);
    els.source.addEventListener('change', applyFilter);

    applyFilter();
  </script>
</body>
</html>
""".replace("__PAYLOAD__", payload)

    output_path.write_text(html, encoding="utf-8")

    # Keep historical filename for compatibility, root path `index.html` as GitHub Pages default.
    if output_path.name == "index.html":
        legacy_path = output_path.with_name("market-showcase-v2.html")
        if legacy_path != output_path:
            legacy_path.write_text(html, encoding="utf-8")
    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
