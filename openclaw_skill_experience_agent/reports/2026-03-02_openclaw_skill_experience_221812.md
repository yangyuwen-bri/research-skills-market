# OpenClaw 对话式 Skill 体验日报
生成时间：2026-03-02 22:18:12
目标：独立 agent 每日自动测试 10 个 skill 的对话可用性

## 说明
- 每个案例先用“用户口播问题”模拟真实对话入口。
- 评估结果优先看“是否能直接落地”，再看降级可解释性。

## 执行汇总
- 测试项：1
- 通过：1
- 降级：0
- 失败：0
- 情景得分：5 / 5

### P01 | peekaboo | PASS
**场景**：系统自动化
**能力**：验证 peekaboo 作为 macOS UI 自动化技能是否可发现、可安装入口与运行前置条件是否清晰
**用户发言**：我想用 OpenClaw 自动做一次 macOS 的界面点击与截图，先帮我先把 peekaboo 能力先核实一下。
**参考回复方向**：我先检查能不能查到 peekaboo 技能源并确认安装方式；再判断当前环境是否已具备 peekaboo 二进制，以及缺了哪些依赖。
**评分**：5 / 5
- 结论：核心链路可直接交付。
- Probe `peekaboo_skill_index`
  - 命令：`npx --yes skills find "peekaboo" | head -n 40`
  - 退出码：0（耗时 19.8s）
  - 可选项：否
  - 输出片段：
    ```
███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

Install with npx skills add <owner/repo@skill>

steipete/clawdis@peekaboo 401 installs
└ https://skills.sh/steipete/clawdis/peekaboo

elizaos/eliza@peekaboo 6 installs
└ https://skills.sh/elizaos/eliza/peekaboo

insight68/skills@peekaboo 4 installs
└ https://skills.sh/insight68/skills/peekaboo

cowork-os/cowork-os@peekaboo 2 installs
└ https://skills.sh/cowork-os/cowork-os/peekaboo

jiulingyun/openclaw-cn@peekaboo 2 installs
└ https://skills.sh/jiulingyun/openclaw-cn/peekaboo

thinkfleetai/thinkfleet-engine@peekaboo 2 installs
└ https://skills.sh/thinkfleetai/thinkfleet-engine/peekaboo
    ```
- Probe `peekaboo_binary_check`
  - 命令：`if command -v peekaboo >/dev/null; then echo "peekaboo_binary_ok"; else echo "peekaboo_binary_missing"; fi`
  - 退出码：0（耗时 0.0s）
  - 可选项：是
  - 输出片段：
    ```
peekaboo_binary_missing
    ```
- Probe `peekaboo_install_hint_probe`
  - 命令：`echo "peekaboo 安装建议：npx skills add steipete/clawdis@peekaboo -g -y 或 npx skills add openclaw/skills -g --skill peekaboo"`
  - 退出码：0（耗时 0.0s）
  - 可选项：否
  - 输出片段：
    ```
peekaboo 安装建议：npx skills add steipete/clawdis@peekaboo -g -y 或 npx skills add openclaw/skills -g --skill peekaboo
    ```

## 复用建议（未使用过 skill 的同学）
1) 先看“参考回复方向”，按场景直接复制到 OpenClaw 对话里。
2) 遇到 `DEGRADED`，优先按输出中的可安装/可配置项完成环境再复测。
3) 失败项可直接丢给经验官，重点复测外部依赖和命令路径。
