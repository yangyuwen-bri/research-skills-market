#!/usr/bin/env python3
"""Run daily conversation-style skill experiments and generate user-friendly reports."""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def run_command(command: str, workdir: Path, timeout_sec: int = 30):
    proc = subprocess.run(
        ["bash", "-lc", command],
        cwd=str(workdir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout_sec,
        env=os.environ.copy(),
    )
    return proc.returncode, proc.stdout or ""


def sanitize_output(output: str) -> str:
    """Remove ANSI control sequences and trim noise."""
    return ANSI_RE.sub("", output).strip()


def probe_ok(result: int, output: str, probe: dict, fail_notes: list) -> bool:
    required_exit = probe.get("required_exit")
    if required_exit is not None and result != int(required_exit):
        fail_notes.append(f"退出码不符: expect={required_exit}, actual={result}")
        return False

    for pattern in probe.get("assert_contains", []):
        if not re.search(pattern, output, re.IGNORECASE | re.MULTILINE):
            fail_notes.append(f"缺少关键内容: {pattern}")
            return False

    assert_any = probe.get("assert_any", [])
    if assert_any:
        any_match = any(
            re.search(pattern, output, re.IGNORECASE | re.MULTILINE) for pattern in assert_any
        )
        if not any_match:
            fail_notes.append(
                "关键内容缺失（任一匹配即可）: " + ", ".join(assert_any)
            )
            return False

    return True


def format_duration(sec: float):
    if sec < 60:
        return f"{sec:.1f}s"
    return f"{sec/60:.1f}m"


def evaluate_case(case: dict, base_dir: Path):
    case_result = {
        "id": case["id"],
        "skill": case["skill"],
        "status": "PASS",
        "checks": [],
        "score": case.get("weight", 5),
    }
    probes = case.get("probes", [])
    soft_fail = False
    case_result.setdefault("notes", [])

    for probe in probes:
        start = time.time()
        output = ""
        exit_code = 0
        timed_out = False
        timeout_sec = int(probe.get("timeout", 30))
        try:
            exit_code, output = run_command(probe["command"], base_dir, timeout_sec)
        except subprocess.TimeoutExpired:
            timed_out = True
            exit_code = 124
            output = f"command timeout after {timeout_sec}s"
        except Exception as exc:  # pragma: no cover - defensive
            exit_code = 1
            output = str(exc)

        notes = []
        if timed_out:
            notes.append(f"超时: 超过 {timeout_sec}s 未返回")
        ok = (not timed_out) and probe_ok(exit_code, output, probe, notes)

        check_item = {
            "label": probe.get("label", "probe"),
            "command": probe["command"],
            "exit_code": exit_code,
            "duration": format_duration(time.time() - start),
            "optional": bool(probe.get("optional", False)),
            "notes": notes,
            "output": sanitize_output(output)[:4500],
        }
        case_result["checks"].append(check_item)
        if check_item["notes"]:
            case_result["notes"].extend(check_item["notes"])

        if not ok:
            if check_item["optional"]:
                soft_fail = True
            else:
                case_result["status"] = "FAIL"
                case_result["score"] = 0

    if case_result["status"] == "PASS" and soft_fail:
        case_result["status"] = "DEGRADED"
        case_result["score"] = max(2, int(case.get("weight", 5) * 0.6))

    return case_result


def build_report(data: dict, results: list, out_path: Path):
    total_score = sum(item["score"] for item in results if item["status"] != "FAIL")
    max_score = sum(item.get("weight", 5) for item in data["cases"][: len(results)])
    fail_count = len([r for r in results if r["status"] == "FAIL"])
    degrade_count = len([r for r in results if r["status"] == "DEGRADED"])
    pass_count = len([r for r in results if r["status"] == "PASS"])

    with out_path.open("w", encoding="utf-8") as fp:
        fp.write("# OpenClaw 对话式 Skill 体验日报\n")
        fp.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        fp.write("目标：独立 agent 每日自动测试 10 个 skill 的对话可用性\n\n")
        fp.write("## 说明\n")
        fp.write("- 每个案例先用“用户口播问题”模拟真实对话入口。\n")
        fp.write("- 评估结果优先看“是否能直接落地”，再看降级可解释性。\n\n")

        fp.write("## 执行汇总\n")
        fp.write(f"- 测试项：{len(results)}\n")
        fp.write(f"- 通过：{pass_count}\n")
        fp.write(f"- 降级：{degrade_count}\n")
        fp.write(f"- 失败：{fail_count}\n")
        fp.write(f"- 情景得分：{total_score} / {max_score}\n\n")

        for case, result in zip(data["cases"][: len(results)], results):
            fp.write(f"### {case['id']} | {case['skill']} | {result['status']}\n")
            fp.write(f"**场景**：{case['skill_group']}\n")
            if case.get("capability"):
                fp.write(f"**能力**：{case['capability']}\n")
            fp.write(f"**用户发言**：{case['user_prompt']}\n")
            fp.write(f"**参考回复方向**：{case['agent_reply_example']}\n")
            fp.write(f"**评分**：{result['score']} / {case.get('weight', 5)}\n")

            if result["status"] != "PASS":
                if result["status"] == "DEGRADED":
                    fp.write("- 结论：技能可用，但存在外部依赖/环境约束，建议先补环境后再用。\n")
                else:
                    fp.write("- 结论：核心链路异常，当前对话路径无法直接交付。\n")
            else:
                fp.write("- 结论：核心链路可直接交付。\n")

            for check in result["checks"]:
                fp.write(f"- Probe `{check['label']}`\n")
                fp.write(f"  - 命令：`{check['command']}`\n")
                fp.write(f"  - 退出码：{check['exit_code']}（耗时 {check['duration']}）\n")
                fp.write(f"  - 可选项：{'是' if check['optional'] else '否'}\n")
                if check["notes"]:
                    fp.write(f"  - 备注：{'; '.join(check['notes'])}\n")
                fp.write("  - 输出片段：\n")
                if check["output"]:
                    snippet = check["output"].replace("`", "\\`")
                    fp.write(f"    ```\n{snippet}\n    ```\n")
                else:
                    fp.write("    （无）\n")
            fp.write("\n")

        fp.write("## 复用建议（未使用过 skill 的同学）\n")
        fp.write("1) 先看“参考回复方向”，按场景直接复制到 OpenClaw 对话里。\n")
        fp.write("2) 遇到 `DEGRADED`，优先按输出中的可安装/可配置项完成环境再复测。\n")
        fp.write("3) 失败项可直接丢给经验官，重点复测外部依赖和命令路径。\n")


def build_turn_plan(results, out_path: Path):
    records = []
    for item in results:
        records.append({
            "case_id": item["id"],
            "skill": item["skill"],
            "status": item["status"],
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "notes": item["checks"],
        })
    out_path.write_text(json.dumps(records, ensure_ascii=False, indent=2))


def parse_args():
    p = argparse.ArgumentParser(description="Run skill conversation cases and generate report.")
    p.add_argument("--config", default=str(ROOT / "config" / "skill_cases.json"))
    p.add_argument("--limit", type=int, default=10, help="run at most N cases")
    p.add_argument("--out", default=str(ROOT / "reports"), help="report output directory")
    p.add_argument("--include-json", action="store_true", help="also write structured json summary")
    return p.parse_args()


def main():
    args = parse_args()
    config_path = Path(args.config)
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)

    with config_path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)

    cases = sorted(data["cases"], key=lambda x: x.get("priority", 999))
    selected = cases[: args.limit]

    results = []
    for case in selected:
        results.append(evaluate_case(case, ROOT))

    today = datetime.now().strftime("%Y-%m-%d")
    ts = datetime.now().strftime("%H%M%S")
    report_file = output_dir / f"{today}_openclaw_skill_experience_{ts}.md"
    build_report({"agent_name": data.get("agent_name", ""), "cases": selected}, results, report_file)

    print(f"报告已生成: {report_file}")
    for r in results:
        print(f"{r['id']} {r['skill']}: {r['status']}（{r['score']}）")
    if args.include_json:
        json_file = output_dir / f"{today}_openclaw_skill_experience_{ts}.json"
        build_turn_plan(results, json_file)
        print(f"结构化结果已生成: {json_file}")

    # 失败即退出码 1，给自动调度一个明确信号
    if any(r["status"] == "FAIL" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
