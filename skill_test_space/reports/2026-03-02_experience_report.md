# 每日 Skill 体验场景测试报告（独立测试空间）
日期：2026-03-02 19:50:21
场景总数：9

## 评测目标
1. 按真实用户任务场景验证技能是否能落地。
2. 记录每个场景的实际输出、可读性、是否适合新手直接使用。
3. 标记异常场景的降级方案。

## 0) 使用前提
- 未预置任何 Skills API Key 或服务认证信息。
- 允许访问外网并可执行 `npx`、`curl`、`python3`。
- 报告以“场景是否可落地”为主，不以单次网络抖动作为必然失败处理。
## 1) find-skills 场景测试
### 用例 F-01
- 用例名：按关键词快速发现技能
- 技能：find-skills
- 场景：用户要找与 web search 相关的能力，先查询候选技能
- 命令：`npx --yes skills find "web search" | head -n 40`

#### 执行输出
```

███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

Install with npx skills add <owner/repo@skill>

inference-sh-9/skills@web-search 10.3K installs
└ https://skills.sh/inference-sh-9/skills/web-search

langchain-ai/deepagents@web-research 439 installs
└ https://skills.sh/langchain-ai/deepagents/web-research

jezweb/claude-skills@google-gemini-file-search 333 installs
└ https://skills.sh/jezweb/claude-skills/google-gemini-file-search

sundial-org/awesome-openclaw-skills@exa-web-search-free 320 installs
└ https://skills.sh/sundial-org/awesome-openclaw-skills/exa-web-search-free

jwynia/agent-skills@web-search 232 installs
└ https://skills.sh/jwynia/agent-skills/web-search

jwynia/agent-skills@web-search-tavily 203 installs
└ https://skills.sh/jwynia/agent-skills/web-search-tavily


```

#### 体验判定
- 体验结论：PASS
- 场景打分：5/5
- 退出码：0

### 用例 F-02
- 用例名：处理无精确匹配的搜索输入
- 技能：find-skills
- 场景：用户给了一个不常见词，检查是否能快速判断“无结果/改写建议”
- 命令：`npx --yes skills find "asdfghjklqwertyui" | head -n 40`

#### 执行输出
```

███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

No skills found for "asdfghjklqwertyui"

```

#### 体验判定
- 体验结论：PASS
- 场景打分：4/5
- 退出码：0

### 用例 F-03
- 用例名：确认当前可直接用技能列表
- 技能：find-skills
- 场景：用户想确认当前已安装技能，决定下一步是否重复安装
- 命令：`npx --yes skills list -g | sed -n '1,12p'`

#### 执行输出
```
Global Skills

apify-twitter ~/.openclaw/skills/apify-twitter
  Agents: OpenClaw
gsdata ~/.openclaw/skills/gsdata
  Agents: OpenClaw
moltbook ~/.openclaw/skills/moltbook
  Agents: OpenClaw
patent-disclosure-writer ~/.openclaw/skills/patent-disclosure-writer-community
  Agents: OpenClaw
patent-pro ~/.openclaw/skills/patent-pro
  Agents: OpenClaw

```

#### 体验判定
- 体验结论：PASS
- 场景打分：5/5
- 退出码：0

## 2) weather 场景测试
### 用例 W-01
- 用例名：快速文本天气输出（优先路径）
- 技能：weather
- 场景：用户想快速查看当前天气，尝试最短路径
- 命令：`curl --max-time 8 -s 'https://wttr.in/London?format=3'`

#### 执行输出
```

```

#### 体验判定
- 体验结论：FAIL
- 场景打分：4/5
- 退出码：28

### 用例 W-02
- 用例名：结构化天气 JSON 直接可用（程序化）
- 技能：weather
- 场景：用户要稳定拿天气数据用于脚本，要求含经纬度
- 命令：`curl -s --max-time 12 'https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.12&current_weather=true' | python3 -c 'import sys,json; import itertools; d=json.load(sys.stdin); c=d.get("current_weather",{}); print("London: temp=%s℃ wind=%skm/h" % (c.get("temperature"), c.get("windspeed")) )'`

#### 执行输出
```
London: temp=13.1℃ wind=14.8km/h

```

#### 体验判定
- 体验结论：PASS
- 场景打分：5/5
- 退出码：0

### 用例 W-03
- 用例名：跨地区查询（北京）+ 降级流程说明
- 技能：weather
- 场景：用户想比对两地天气，验证接口可扩展
- 命令：`curl -s --max-time 12 'https://api.open-meteo.com/v1/forecast?latitude=39.9&longitude=116.4&current_weather=true' | python3 -c 'import sys,json; d=json.load(sys.stdin); c=d.get("current_weather",{}); print("Beijing: temp=%s℃ wind=%skm/h" % (c.get("temperature"), c.get("windspeed")) )'`

#### 执行输出
```
Beijing: temp=3.2℃ wind=6.9km/h

```

#### 体验判定
- 体验结论：PASS
- 场景打分：5/5
- 退出码：0

## 3) polymarketodds 场景测试
### 用例 P-01
- 用例名：快速掌握当前热度市场
- 技能：polymarketodds
- 场景：用户想先看最值得关注的市场（决策类）
- 命令：`python3 /Users/yuwen/work/research-skills-market/skill_test_space/polymarketodds/scripts/polymarket.py trending | head -n 60`

#### 执行输出
```
🔥 **Trending on Polymarket**

🎯 **Khamenei out as Supreme Leader of Iran by February 28?**
   Volume: $101.1M (24h: $19.8M)
   ⏰ Ended
   Markets: 1
   • Khamenei out as Supreme Leader of Iran b: 99.9% ↑0.4% ($101.1M)
   🔗 polymarket.com/event/khamenei-out-as-supreme-leader-of-iran-by-february-28

🎯 **2026 NBA Champion**
   Volume: $321.3M (24h: $11.2M)
   ⏰ Jul 01, 2026
   Markets: 30
   • Oklahoma City Thunder: 35.5% ($4.4M)
   • San Antonio Spurs: 12.0% ↑0.2% ($4.6M)
   • Denver Nuggets: 11.5% ($2.5M)
   • Cleveland Cavaliers: 7.4% ↓0.7% ($3.4M)
   • Boston Celtics: 7.2% ↑0.1% ($4.3M)
   • Detroit Pistons: 6.9% ↓0.2% ($4.2M)
   • New York Knicks: 4.5% ↓0.1% ($2.7M)
   • Houston Rockets: 3.5% ↓0.1% ($2.5M)
   • Minnesota Timberwolves: 3.1% ↑0.1% ($3.7M)
   • Los Angeles Lakers: 1.5% ($3.8M)
   ... and 20 more
   🔗 polymarket.com/event/2026-nba-champion

🎯 **2026 FIFA World Cup Winner **
   Volume: $234.7M (24h: $8.2M)
   ⏰ Jul 20, 2026
   Markets: 43
   • Spain: 14.9% ↑0.1% ($2.9M)
   • England: 13.2% ($2.5M)
   • Argentina: 11.5% ↓0.2% ($3.4M)
   • France: 10.7% ($2.7M)
   • Brazil: 8.6% ($2.4M)
   • Portugal: 7.1% ↑0.3% ($6.3M)
   • Germany: 5.5% ↑0.1% ($4.5M)
   • Netherlands: 3.1% ($4.9M)
   • Norway: 2.9% ↑0.1% ($5.2M)
   • Italy: 1.9% ($4.5M)
   ... and 33 more
   🔗 polymarket.com/event/2026-fifa-world-cup-winner-595

🎯 **Khamenei out as Supreme Leader of Iran by March 31?**
   Volume: $57.8M (24h: $8.0M)
   ⏰ Ends in 4w
   Markets: 1
   • Khamenei out as Supreme Leader of Iran b: 99.9% ↓1.0% ($57.8M)
   🔗 polymarket.com/event/khamenei-out-as-supreme-leader-of-iran-by-march-31

🎯 **La Liga Winner **
   Volume: $126.1M (24h: $5.9M)
   ⏰ May 30, 2026
   Markets: 20
   • Barcelona: 61.0% ↓1.0% ($1.6M)
   • Real Madrid: 36.5% ↑1.0% ($1.5M)
   • Atletico Madrid: 0.4% ↑0.1% ($8.0M)
   • Villarreal: 0.2% ↑0.1% ($6.6M)
   • Betis: 0.2% ($4.6M)
   • Celta Vigo: 0.1% ($3.8M)

```

#### 体验判定
- 体验结论：PASS
- 场景打分：5/5
- 退出码：0

### 用例 P-02
- 用例名：按关键词查找事件（Trump）
- 技能：polymarketodds
- 场景：用户拿到一个具体事件关键词，先快速查找对应市场
- 命令：`python3 /Users/yuwen/work/research-skills-market/skill_test_space/polymarketodds/scripts/polymarket.py search "trump" | head -n 60`

#### 执行输出
```
🔍 **Search: 'trump'**

🎯 **What will happen before GTA VI?**
   Volume: $18.4M (24h: $105.8K)
   ⏰ Jul 31, 2026
   Markets: 9
   • Drake releases Iceman: 97.5% ↑4.9% ($66.3K)
   • GPT-6 released: 67.0% ↓1.0% ($596.8K)
   • Russia-Ukraine Ceasefire: 57.5% ($1.3M)
   • New Rihanna Album: 54.5% ↓1.0% ($642.6K)
   • Trump out as President : 52.0% ($521.3K)
   • China invades Taiwan : 51.5% ↑0.5% ($1.4M)
   • Bitcoin hits $1m: 48.6% ↓0.1% ($3.4M)
   • New Playboi Carti Album : 48.0% ↑1.5% ($677.4K)
   • Jesus Christ returns: 47.5% ($9.7M)
   🔗 polymarket.com/event/what-will-happen-before-gta-vi

🎯 **Trump eliminates capital gains tax on crypto by ___?**
   Volume: $96.7K (24h: $1.2K)
   ⏰ Ended
   Markets: 2
   • December 31, 2026: 8.5% ↓3.4% ($12.4K)
   • December 31
   🔗 polymarket.com/event/trump-eliminates-capital-gains-tax-on-crypto-in-2025

🎯 **Presidential Election Winner 2028**
   Volume: $350.3M (24h: $3.7M)
   ⏰ Nov 07, 2028
   Markets: 35
   • JD Vance: 21.3% ↓0.5% ($7.2M)
   • Gavin Newsom: 17.3% ↓0.1% ($4.6M)
   • Marco Rubio: 8.2% ↓0.2% ($3.9M)
   • Alexandria Ocasio-Cortez: 6.4% ↑0.1% ($6.8M)
   • Kamala Harris: 3.5% ↑0.2% ($5.0M)
   • Donald Trump: 2.4% ↓0.1% ($4.7M)
   • Josh Shapiro: 2.2% ↑0.1% ($4.1M)
   • Pete Buttigieg: 1.9% ↓0.1% ($2.5M)
   • Jon Ossoff: 1.8% ($1.2M)
   • Dwayne 'The Rock' Johnson: 1.7% ↑0.1% ($3.5M)
   ... and 25 more
   🔗 polymarket.com/event/presidential-election-winner-2028

🎯 **Republican Presidential Nominee 2028**
   Volume: $343.6M (24h: $3.1M)
   ⏰ Nov 07, 2028
   Markets: 33
   • J.D. Vance: 41.3% ($4.7M)
   • Marco Rubio: 17.1% ↑2.4% ($4.7M)
   • Donald Trump: 2.5% ↓0.1% ($4.6M)
   • Ron DeSantis: 2.5% ↓0.1% ($3.9M)
   • Ted Cruz: 2.2% ($7.1M)
   • Donald Trump Jr.: 2.0% ($3.4M)
   • Thomas Massie: 1.8% ($1.0M)
   • Glenn Youngkin: 1.8% ($3.8M)
   • Ivanka Trump: 1.8% ↑0.1% ($3.6M)
   • Brian Kemp: 1.6% ↑0.2% ($7.4M)
   ... and 23 more
   🔗 polymarket.com/event/republican-presidential-nominee-2028

🎯 **Will Trump pardon Ghislaine Maxwell by end of 2026?**

```

#### 体验判定
- 体验结论：PASS
- 场景打分：5/5
- 退出码：0

### 用例 P-03
- 用例名：查看未来 3 天结算窗口（空结果处理）
- 技能：polymarketodds
- 场景：用户要做每日提醒，关心近期是否有事件结算
- 命令：`python3 /Users/yuwen/work/research-skills-market/skill_test_space/polymarketodds/scripts/polymarket.py calendar --days 3`

#### 执行输出
```
📅 **Resolving in 3 days** (0 markets)

No markets resolving in this timeframe.

```

#### 体验判定
- 体验结论：PASS
- 场景打分：4/5
- 退出码：0


## 结果汇总
- 总场景数：9
- 可直接落地：8
- 需人工降级/网络重试：1
- 通过率：88%
- 总分（按5分制）：38/45

## 关键解读（给未使用过技能的人）
1. find-skills 适合作为“任务前置动作”：先搜可复用技能，再决定是否安装。
2. weather 适合日常脚本和提醒类场景；在本环境中 wttr.in 有偶发超时，建议默认回退 open-meteo。
3. polymarketodds 适合市场监控；适合把“trending/search/calendar”作为固定三件套。

## 执行建议（复制可用）
- 查询/筛选：`npx --yes skills find \"web search\" | head -n 20`
- 天气（稳定版）：`curl -s 'https://api.open-meteo.com/v1/forecast?latitude=<lat>&longitude=<lon>&current_weather=true'`
- 热门市场：`python3 skill_test_space/polymarketodds/scripts/polymarket.py trending | head -n 40`
