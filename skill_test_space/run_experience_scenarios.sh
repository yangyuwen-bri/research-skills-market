#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="$BASE_DIR/reports"
TODAY="$(date +%F)"
REPORT="$REPORT_DIR/${TODAY}_experience_report.md"
TIMEOUT_SECONDS=60
TIMEOUT_BIN=""
if command -v timeout >/dev/null 2>&1; then
  TIMEOUT_BIN="timeout $TIMEOUT_SECONDS"
fi

TOTAL=0
PASSED=0
FAILED=0
SCORE_SUM=0
MAX_SCORE=5
mkdir -p "$REPORT_DIR"

clean_ansi() {
  perl -pe 's/\e\[[0-9;]*[A-Za-z]//g'
}

run_case() {
  local case_no="$1"
  local skill="$2"
  local title="$3"
  local scenario="$4"
  local command="$5"
  local checker="$6"
  local score="$7"
  local status=0
  local result="FAIL"
  local out_file
  out_file="$(mktemp)"
  TOTAL=$((TOTAL + 1))

  {
    echo "### 用例 $case_no"
    echo "- 用例名：$title"
    echo "- 技能：$skill"
    echo "- 场景：$scenario"
    echo "- 命令：\`$command\`"
    echo ""
    echo "#### 执行输出"
    echo '```'
    if [ -n "$TIMEOUT_BIN" ]; then
      if $TIMEOUT_BIN bash -lc "$command" >"$out_file" 2>&1; then
        status=0
      else
        status=$?
      fi
    elif bash -lc "$command" >"$out_file" 2>&1; then
      status=0
    else
      status=$?
    fi
    clean_ansi <"$out_file"
    echo ""

    if [ "$status" -eq 0 ]; then
      if [ -n "$checker" ]; then
        if OUT_FILE="$out_file" bash -lc "$checker"; then
          result="PASS"
        fi
      else
        result="PASS"
      fi
    fi

    rm -f "$out_file"

    echo '```'
    echo ""
    if [ "$result" = "PASS" ]; then
      PASSED=$((PASSED + 1))
      SCORE_SUM=$((SCORE_SUM + score))
    else
      FAILED=$((FAILED + 1))
    fi

    echo "#### 体验判定"
    echo "- 体验结论：${result}"
    echo "- 场景打分：$score/$MAX_SCORE"
    echo "- 退出码：$status"
    echo ""
  } >> "$REPORT"
}

cat > "$REPORT" <<EOF
# 每日 Skill 体验场景测试报告（独立测试空间）
日期：$(date "+%Y-%m-%d %H:%M:%S")
场景总数：9

## 评测目标
1. 按真实用户任务场景验证技能是否能落地。
2. 记录每个场景的实际输出、可读性、是否适合新手直接使用。
3. 标记异常场景的降级方案。

EOF

cat >> "$REPORT" <<'EOF'
## 0) 使用前提
- 未预置任何 Skills API Key 或服务认证信息。
- 允许访问外网并可执行 `npx`、`curl`、`python3`。
- 报告以“场景是否可落地”为主，不以单次网络抖动作为必然失败处理。
EOF

echo "## 1) find-skills 场景测试" >> "$REPORT"

run_case \
  "F-01" \
  "find-skills" \
  "按关键词快速发现技能" \
  "用户要找与 web search 相关的能力，先查询候选技能" \
  "npx --yes skills find \"web search\" | head -n 40" \
  "grep -Eq \"@|skills\\.sh|Install with\" \"\$OUT_FILE\"" \
  5

run_case \
  "F-02" \
  "find-skills" \
  "处理无精确匹配的搜索输入" \
  "用户给了一个不常见词，检查是否能快速判断“无结果/改写建议”" \
  "npx --yes skills find \"asdfghjklqwertyui\" | head -n 40" \
  "[ -z \"\$(grep -E \"@|skills\\.sh|Install with\" \"\$OUT_FILE\" | tr -d '[:space:]')\" ]" \
  4

run_case \
  "F-03" \
  "find-skills" \
  "确认当前可直接用技能列表" \
  "用户想确认当前已安装技能，决定下一步是否重复安装" \
  "npx --yes skills list -g | sed -n '1,12p'" \
  "grep -Eq \"Global Skills|Agents:\" \"\$OUT_FILE\"" \
  5

echo "## 2) weather 场景测试" >> "$REPORT"

run_case \
  "W-01" \
  "weather" \
  "快速文本天气输出（优先路径）" \
  "用户想快速查看当前天气，尝试最短路径" \
  "curl --max-time 8 -s 'https://wttr.in/London?format=3'" \
  "grep -Eq \"[A-Za-z].*\\+?-?[0-9]+\" \"\$OUT_FILE\"" \
  4

run_case \
  "W-02" \
  "weather" \
  "结构化天气 JSON 直接可用（程序化）" \
  "用户要稳定拿天气数据用于脚本，要求含经纬度" \
  "curl -s --max-time 12 'https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.12&current_weather=true' | python3 -c 'import sys,json; import itertools; d=json.load(sys.stdin); c=d.get(\"current_weather\",{}); print(\"London: temp=%s℃ wind=%skm/h\" % (c.get(\"temperature\"), c.get(\"windspeed\")) )'" \
  "grep -Eq \"London: temp=.*℃ wind=.*km/h\" \"\$OUT_FILE\"" \
  5

run_case \
  "W-03" \
  "weather" \
  "跨地区查询（北京）+ 降级流程说明" \
  "用户想比对两地天气，验证接口可扩展" \
  "curl -s --max-time 12 'https://api.open-meteo.com/v1/forecast?latitude=39.9&longitude=116.4&current_weather=true' | python3 -c 'import sys,json; d=json.load(sys.stdin); c=d.get(\"current_weather\",{}); print(\"Beijing: temp=%s℃ wind=%skm/h\" % (c.get(\"temperature\"), c.get(\"windspeed\")) )'" \
  "grep -Eq \"Beijing: temp=.*℃ wind=.*km/h\" \"\$OUT_FILE\"" \
  5

echo "## 3) polymarketodds 场景测试" >> "$REPORT"

run_case \
  "P-01" \
  "polymarketodds" \
  "快速掌握当前热度市场" \
  "用户想先看最值得关注的市场（决策类）" \
  "python3 $BASE_DIR/polymarketodds/scripts/polymarket.py trending | head -n 60" \
  "grep -Eq \"Trending on Polymarket|Volume:\" \"\$OUT_FILE\"" \
  5

run_case \
  "P-02" \
  "polymarketodds" \
  "按关键词查找事件（Trump）" \
  "用户拿到一个具体事件关键词，先快速查找对应市场" \
  "python3 $BASE_DIR/polymarketodds/scripts/polymarket.py search \"trump\" | head -n 60" \
  "grep -Eq \"Search: 'trump'|Trending|🔍|Volume:\" \"\$OUT_FILE\"" \
  5

run_case \
  "P-03" \
  "polymarketodds" \
  "查看未来 3 天结算窗口（空结果处理）" \
  "用户要做每日提醒，关心近期是否有事件结算" \
  "python3 $BASE_DIR/polymarketodds/scripts/polymarket.py calendar --days 3" \
  "grep -Eq \"Resolving in 3 days|No markets resolving\" \"\$OUT_FILE\"" \
  4

cat >> "$REPORT" <<EOF

## 结果汇总
- 总场景数：$TOTAL
- 可直接落地：$PASSED
- 需人工降级/网络重试：$FAILED
- 通过率：$(( PASSED * 100 / TOTAL ))%
- 总分（按5分制）：$SCORE_SUM/$(( TOTAL * MAX_SCORE ))

## 关键解读（给未使用过技能的人）
1. find-skills 适合作为“任务前置动作”：先搜可复用技能，再决定是否安装。
2. weather 适合日常脚本和提醒类场景；在本环境中 wttr.in 有偶发超时，建议默认回退 open-meteo。
3. polymarketodds 适合市场监控；适合把“trending/search/calendar”作为固定三件套。

## 执行建议（复制可用）
- 查询/筛选：\`npx --yes skills find \"web search\" | head -n 20\`
- 天气（稳定版）：\`curl -s 'https://api.open-meteo.com/v1/forecast?latitude=<lat>&longitude=<lon>&current_weather=true'\`
- 热门市场：\`python3 skill_test_space/polymarketodds/scripts/polymarket.py trending | head -n 40\`
EOF

echo "体验报告已生成: $REPORT"
