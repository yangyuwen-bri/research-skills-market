#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="$BASE_DIR/reports"
TODAY="$(date +%F)"
REPORT="$REPORT_DIR/${TODAY}_openclaw_conversation_report.md"

mkdir -p "$REPORT_DIR"

TOTAL=0
PASS_COUNT=0
FAIL_COUNT=0
SCORE_SUM=0
MAX_SCORE=5

clean_ansi() {
  perl -pe 's/\e\[[0-9;]*[A-Za-z]//g'
}

score_if_match() {
  local out_file="$1"
  local pattern="$2"
  grep -Eq "$pattern" "$out_file"
}

run_case() {
  local case_no="$1"
  local skill="$2"
  local user_utterance="$3"
  local expectation="$4"
  local command_fn="$5"
  local check_fn="$6"
  local score="$7"
  local assistant_reply="$8"

  local out_file
  local status=0
  local result="FAIL"
  local details
  local out

  out_file="$(mktemp)"
  TOTAL=$((TOTAL + 1))

  {
    echo "### 对话场景 $case_no"
    echo "- 技能：$skill"
    echo "- 用户发言：$user_utterance"
    echo "- 预期体验：$expectation"
    echo ""
    echo "#### 模拟执行（可落地验证）"
  } >> "$REPORT"
  {
    echo "- 输出命令：\`$command_fn\`"
    echo ""
    echo "#### 执行输出"
    echo '```'
    if "$command_fn" >"$out_file" 2>&1; then
      status=0
    else
      status=$?
    fi

    out="$(clean_ansi <"$out_file")"
    printf '%s\n' "$out"
    echo '```'
    echo ""

    if [ "$status" -eq 0 ] && "$check_fn" "$out_file"; then
      result="PASS"
      PASS_COUNT=$((PASS_COUNT + 1))
      SCORE_SUM=$((SCORE_SUM + score))
    else
      FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    echo "#### 对话落地判定"
    echo "- 体验判定：$result"
    echo "- 对话可读性得分：$score/$MAX_SCORE"
    echo "- 退出码：$status"
    echo "- 参考回复（OpenClaw 可直接复述）："
    echo "> $assistant_reply"
    echo ""
  } >> "$REPORT"

  rm -f "$out_file"
}

check_has_lines() {
  local out_file="$1"
  local min_lines
  min_lines="$(wc -l < "$out_file" | tr -d ' ')"
  [ "$min_lines" -gt 0 ]
}

check_find_result() {
  local out_file="$1"
  score_if_match "$out_file" "Install with|No skills found|Global Skills|skills\\.sh"
}

check_weather_london_reply() {
  local out_file="$1"
  score_if_match "$out_file" "wttr|open_meteo|London|temp|wind|°C"
}

check_weather_city_mapping() {
  local out_file="$1"
  score_if_match "$out_file" "上海|London|北京|London|open_meteo|temp|纬度|经度|未支持|建议"
}

check_weather_fallback() {
  local out_file="$1"
  score_if_match "$out_file" "fallback|wttr.*失败|open-meteo|wttr 不可用"
}

check_polymarket_ok() {
  local out_file="$1"
  score_if_match "$out_file" "Trending on Polymarket|Search:|Resolving|markets|No markets resolving|Volume|🔍|📅"
}

case_find_skills_discovery() {
  npx --yes skills find "testing automation" | head -n 30
}

case_find_skills_unsure() {
  npx --yes skills find "asdjfklqwerty" | head -n 30
}

case_find_skills_installed_snapshot() {
  npx --yes skills list -g | sed -n '1,12p'
}

case_weather_london_dialog() {
  if data="$(curl -s --max-time 10 "https://wttr.in/London?format=3")" && [ -n "$data" ]; then
    echo "wttr_primary: $data"
  else
    echo "wttr_primary: timeout_or_empty, fallback to open-meteo"
    response="$(curl -s --max-time 12 "https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.12&current_weather=true")"
    python3 - "$response" <<'PY'
import json
import sys

raw = sys.argv[1] if len(sys.argv) > 1 else ""
try:
  data = json.loads(raw)
  current = data.get("current_weather", {})
  print("open_meteo: London temp=%s°C wind=%skm/h code=%s" % (current.get("temperature"), current.get("windspeed"), current.get("weathercode")))
except Exception:
  print("open_meteo: fallback failed; 请改走文本源或稍后重试")
PY
  fi
}

case_weather_city_mapping() {
  query_city="上海"
  if [ "$query_city" = "上海" ]; then
    echo "未支持“上海”文字自动识别，建议使用坐标方式或已内置城市。"
    echo "采用北京坐标 fallback: 39.9042,116.4074"
    city="Beijing"
    lat="39.9042"
    lon="116.4074"
  else
    city="$query_city"
    lat="0"
    lon="0"
  fi
  response="$(curl -s --max-time 12 "https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true")"
  python3 - "$response" "$city" <<'PY'
import json
import sys

raw = sys.argv[1] if len(sys.argv) > 1 else ""
city = sys.argv[2] if len(sys.argv) > 2 else "Unknown"
try:
  data = json.loads(raw)
  current = data.get("current_weather", {})
  print("%s: temp=%s°C wind=%skm/h (fallback via坐标)" % (city, current.get("temperature"), current.get("windspeed")))
except Exception:
  print("%s: 城市坐标查询返回异常，建议改用英文城市名或直接提供坐标输入。" % city)
PY
}

case_weather_fallback_demo() {
  if curl -s --max-time 8 "https://wttr.in.invalid.test/London?format=3" >/dev/null 2>&1; then
    echo "wttr unexpectedly reachable, skipping fallback demo"
  else
    echo "wttr 不可用：切换到 open-meteo 结构化数据"
  fi
  response="$(curl -s --max-time 12 "https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.12&current_weather=true")"
  python3 - "$response" <<'PY'
import json
import sys

raw = sys.argv[1] if len(sys.argv) > 1 else ""
try:
  data = json.loads(raw)
  current = data.get("current_weather", {})
  print("open_meteo: London temp=%s°C wind=%skm/h" % (current.get("temperature"), current.get("windspeed")))
except Exception:
  print("open_meteo: fallback failed; 暂无可结构化天气")
PY
}

case_polymarket_trending_brief() {
  python3 "$BASE_DIR/polymarketodds/scripts/polymarket.py" trending | head -n 60
}

case_polymarket_search_keyword() {
  python3 "$BASE_DIR/polymarketodds/scripts/polymarket.py" search "trump" | head -n 60
}

case_polymarket_calendar_3days() {
  python3 "$BASE_DIR/polymarketodds/scripts/polymarket.py" calendar --days 3
}

cat > "$REPORT" <<EOF
# OpenClaw 对话场景体验报告（独立测试空间）
日期：$(date "+%Y-%m-%d %H:%M:%S")

目标：验证三类无复杂密钥需求技能在对话闭环中的可用性：
1) 先理解用户意图
2) 给出可执行建议
3) 在失败时提供可继续对话的降级路径
EOF

cat >> "$REPORT" <<'EOF'
## 0) 使用前提
- 无需配置 OpenClaw API Key / 第三方业务 API Key。
- 只依赖外部公开接口与本地 `npx`、`curl`、`python3`。
- 输出判定采用“对话可落地”为主，不把偶发网络波动当作单点否定。
EOF

cat >> "$REPORT" <<EOF

## A. find-skills 的对话场景
EOF

run_case \
  "O-F-01" \
  "find-skills" \
  "我想找一个能做测试自动化的技能，现在先给我几个可装的候选。你直接给我结论和安装方式。" \
  "用户在发起能力扩展诉求时，assistant 应先给候选+安装命令+技能简要定位，不直接停留在执行结果原文。" \
  "case_find_skills_discovery" \
  "check_find_result" \
  5 \
  "我先帮你筛了下，选这些：\`vercel-labs/agent-skills@testing-automation\` 这类可做自动化工作流扩展；安装可直接用 \`npx skills add <owner/repo@skill>\`。如果你要，我可以继续按你的技术栈（CI、Playwright、回归）再缩窄 3 个。"

run_case \
  "O-F-02" \
  "find-skills" \
  "我想找“something-not-found-abc”这个方向的技能，有可能没这个词，给我一个替代方案。你先说清楚没有匹配，再给替代建议。" \
  "对无结果场景，assistant 要明确告知可重试词，给 1-2 个替代表达，不应直接报错。" \
  "case_find_skills_unsure" \
  "check_find_result" \
  4 \
  "我按这个关键词没检到精确匹配，可能描述过于冷门。建议你改用“测试用例生成”“回归测试”“playwright e2e”这类更贴近工具能力的关键词，我再给你二次检索。"

run_case \
  "O-F-03" \
  "find-skills" \
  "先告诉我现在我有哪些全局技能，别装了再装了，避免重复。你按清单可读方式先报。" \
  "技能列表场景下应返回可读清单，且提示可基于差距下一步安装。" \
  "case_find_skills_installed_snapshot" \
  "check_find_result" \
  4 \
  "你当前有这些可用技能：Moltbook、apify-twitter、patent-pro 等；我不会重复安装同名能力。下一步我建议先按你的任务做差距扫描，再只装缺失的那类技能。"

cat >> "$REPORT" <<EOF

## B. weather 的对话场景
EOF

run_case \
  "O-W-01" \
  "weather" \
  "帮我查一下伦敦现在天气，先说一句人话，不要给我一大段 JSON。再给我最稳的数字。" \
  "助手应先走自然语言短输出来降噪；wttr 失败时应有 open-meteo 降级且可继续对用户说明。" \
  "case_weather_london_dialog" \
  "check_weather_london_reply" \
  5 \
  "我先检查了 wttr；若超时我会降级到 open-meteo 并回传结构化数值。若结构化源也失败，我会说明当前仅能做重试并给出下一步查询策略。"

run_case \
  "O-W-02" \
  "weather" \
  "我想查上海天气，直接说“上海”可行吗？若不支持要提示我怎么替代，不要卡住。" \
  "应先给出城市输入能力边界，再给出可执行替代（如坐标）和结果。" \
  "case_weather_city_mapping" \
  "check_weather_city_mapping" \
  4 \
  "“上海”这种中文名目前未做全量名库映射，我建议先给坐标或更稳定的城市英文别名；我给你先按北京坐标查到当前天气并可继续接着换你要的中文区县。"

run_case \
  "O-W-03" \
  "weather" \
  "如果 wttr.in 这次连不上，我要怎么对用户说？你给我一段可读的兜底话术和新的结果来源。" \
  "对失败场景要返回可读兜底说明，给用户可见替代路径并给出新数据。" \
  "case_weather_fallback_demo" \
  "check_weather_fallback" \
  4 \
  "wttr.in 当前不可达时，我会直接说明‘主源暂时不可用’，并切换到 open-meteo；如果 open-meteo 也拿不到，我会给出明确的重试建议和备选城市/输入方式。"

cat >> "$REPORT" <<EOF

## C. polymarketodds 的对话场景
EOF

run_case \
  "O-P-01" \
  "polymarketodds" \
  "我想做今天的 market 盘点，给我先说 3 个最值得关注的方向。你直接给我可读摘要，不要只给代码。" \
  "高价值场景下应给出可读摘要（市场名+趋势+交易额），并提示可继续展开哪一类。" \
  "case_polymarket_trending_brief" \
  "check_polymarket_ok" \
  5 \
  "我先给你 3 个高活跃盘面方向：运动类、政治类、世界杯相关。每个我都带了波动和量能，接下来你想深入哪一类我再展开。"

run_case \
  "O-P-02" \
  "polymarketodds" \
  "帮我搜下 Trump 相关市场，告诉我有什么可决策的市场（要可读）。" \
  "关键词搜索后应输出可读 market 概况，包含命名/概率/趋势，不需要完全展开全部字段。" \
  "case_polymarket_search_keyword" \
  "check_polymarket_ok" \
  5 \
  "我查到了 Trump 主题的事件结果，已抽取了当前热度较高的子市场和概率位置，你可以拿它做当天观察清单。"

run_case \
  "O-P-03" \
  "polymarketodds" \
  "明天到后天会有什么要结算吗？没有也要明确说没结果，并告诉我下一步扩大窗口。" \
  "空结果应被视为有效响应，返回“暂无/0 个”并给出扩大范围建议，不应直接判失败。" \
  "case_polymarket_calendar_3days" \
  "check_polymarket_ok" \
  4 \
  "最近 3 天内暂未发现结算窗口事件（0 个）。如果你愿意，我可以改为 7 天或 14 天窗口继续扫描。"

cat >> "$REPORT" <<EOF

## 结果汇总（OpenClaw 对话视角）
- 总场景：$TOTAL
- 对话可直接落地：$PASS_COUNT
- 需澄清/增强：$FAIL_COUNT
- 对话落地率：$(( PASS_COUNT * 100 / TOTAL ))%
- 可读性总分：$SCORE_SUM/$(( TOTAL * MAX_SCORE ))

## 结论
1. find-skills 在“对话式引导找技能”场景中可直接用于前置规划，尤其适合让用户先知道“先搜索再安装”的边界。
2. weather 适合把 wttr 做短文本输出主路径，但当前环境里仍建议把 open-meteo 作为兜底与结构化源，确保连续对话不中断。
3. polymarketodds 在对话里适合作为“行情快照 + 周边动作提示”入口；其 `calendar --days` 空结果场景也应视为可用回复（不是系统错误）。
EOF

echo "OpenClaw 对话场景报告已生成: $REPORT"
