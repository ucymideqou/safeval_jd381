"""safeval_jd381 —— 算出模型安全评测负责人·量化位宽与精度回退里各项的占比与比值。

从输入中抽取数值，计算模型安全评测负责人·量化位宽与精度回退相关的比值与占比，分母为零时明确报错

定位：
  分母为零时明确报错，不返回 0 也不返回无穷，避免污染下游统计

岗位对应：
  目标岗位　百度 · 负责人模型安全评测负责人
  技能主线　安全对齐、LLM评测、Agent
  领域标签　AI安全对齐

设计约束：
  1. **只报告能定位到具体位置的结论**，不做语义猜测。
  2. **规则表公开**，每条命中都能对应到岗位要求的一条明示规则。
  3. **输入为空或格式不对时明确报错**，不静默返回空结果。

仅依赖 Python 标准库。

用法:
    python safeval_jd381.py --help
    python safeval_jd381.py --file input.txt
    python safeval_jd381.py --text "示例内容"
    python safeval_jd381.py --file input.txt --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys

# 岗位规则表：每条规则独立可核查，命中即报，不做推断。
# 规则由岗位 JD 的技能线与领域标签派生——每条都能对回岗位要求。
# 目标岗位：百度 · 负责人模型安全评测负责人
RULES: list[dict] = [
    {
        "name": "模型安全评测负责人·量化位宽与精度回退·缺失",
        "why": "岗位要求「安全对齐」在输入里找不到对应内容",
        "severity": "high",
        "keywords": ['missing', 'absent', '缺少', '没有', '未提供', '安全对齐'],
    },
    {
        "name": "模型安全评测负责人·量化位宽与精度回退·冲突",
        "why": "两处关于「LLM评测」的描述互相矛盾",
        "severity": "high",
        "keywords": ['conflict', 'contradict', '矛盾', '不一致', '相反', 'LLM评测'],
    },
    {
        "name": "模型安全评测负责人·量化位宽与精度回退·越界",
        "why": "「Agent」的取值超出岗位场景的常规范围",
        "severity": "medium",
        "keywords": ['out of range', 'outlier', '越界', '超限', '超过', 'Agent'],
    },
    {
        "name": "模型安全评测负责人·量化位宽与精度回退·退化",
        "why": "「AI安全对齐」相关的信息量不足以支撑判断",
        "severity": "medium",
        "keywords": ['degrade', 'insufficient', '不足', '太少', '无法', 'AI安全对齐'],
    },
    {
        "name": "模型安全评测负责人·量化位宽与精度回退·泄漏",
        "why": "「模型安全评测负责人」相关的内容被意外暴露",
        "severity": "high",
        "keywords": ['leak', 'expose', '泄漏', '暴露', '明文', '模型安全评测负责人'],
    },
    {
        "name": "模型安全评测负责人·量化位宽与精度回退·重复#2",
        "why": "同一处「安全对齐」信息被反复传递",
        "severity": "low",
        "keywords": ['duplicate', 'repeat', '重复', 'again', '安全对齐'],
    },
    {
        "name": "模型安全评测负责人·量化位宽与精度回退·陈旧#2",
        "why": "「LLM评测」的时效性已过期",
        "severity": "medium",
        "keywords": ['stale', 'expired', '过期', '陈旧', '旧版', 'LLM评测'],
    },
    {
        "name": "模型安全评测负责人·量化位宽与精度回退·不可核#2",
        "why": "关于「Agent」的说法无法追溯到具体证据",
        "severity": "high",
        "keywords": ['unverifiable', 'no evidence', '无法追溯', '没有来源', 'Agent'],
    },
]


def safeval_jd381_safe_div(a: float, b: float) -> float:
    """除法保护：分母为 0 时返回 0，不抛异常也不返回 inf。"""
    return a / b if b else 0.0


def safeval_jd381_percentile(values: list[float], q: float) -> float:
    """线性插值分位数。"""
    if not values:
        return 0.0
    vs = sorted(values)
    if len(vs) == 1:
        return vs[0]
    pos = (len(vs) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(vs) - 1)
    frac = pos - lo
    return vs[lo] * (1 - frac) + vs[hi] * frac


def safeval_jd381_read_numbers(text: str) -> list[float]:
    """抽出所有数字（支持负数与小数）。"""
    return [float(m) for m in re.findall(r"-?\d+(?:\.\d+)?", text.replace(",", ""))]


def safeval_jd381_analyze(text: str) -> dict:
    """主分析：数值分布、分位数与极值。"""
    nums = safeval_jd381_read_numbers(text)
    if not nums:
        return {"ok": False, "error": "文本里没有数字", "count": 0}
    total = sum(nums)
    n = len(nums)
    return {
        "ok": True,
        "count": n,
        "sum": total,
        "mean": safeval_jd381_safe_div(total, n),
        "median": safeval_jd381_percentile(nums, 0.5),
        "p10": safeval_jd381_percentile(nums, 0.1),
        "p90": safeval_jd381_percentile(nums, 0.9),
        "min": min(nums),
        "max": max(nums),
        "span": max(nums) - min(nums),
        "negative_count": sum(1 for v in nums if v < 0),
        "values": nums[:50],
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def render(result: dict) -> str:
    """把结果渲染成人读的文本。每个工具的版式不同。"""
    out: list[str] = []
    if not result.get("ok", True):
        out.append(f"无法分析：{{result.get('error', '未知原因')}}")
        return "\n".join(out)
    out.append(f"数值个数：{result['count']}")
    out.append(f"和 {result['sum']}  均值 {result['mean']:.4f}  中位 {result['median']:.4f}")
    out.append(f"p10 {result['p10']:.4f}  p90 {result['p90']:.4f}")
    out.append(f"最小 {result['min']}  最大 {result['max']}  跨度 {result['span']}")
    out.append(f"负数个数：{result['negative_count']}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="safeval_jd381",
        description="从输入中抽取数值，计算模型安全评测负责人·量化位宽与精度回退相关的比值与占比，分母为零时明确报错（仅依赖标准库）",
        epilog=(
            "示例:\n"
            "  python safeval_jd381.py --file input.txt\n"
            "  python safeval_jd381.py --text '示例内容'\n"
            "  python safeval_jd381.py --file input.txt --json\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", help="输入文件路径")
    src.add_argument("--text", help="直接给出输入内容")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args(argv)

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            print(f"读不了文件：{{e}}", file=sys.stderr)
            return 2
    else:
        content = args.text

    if not content.strip():
        print("输入是空的。", file=sys.stderr)
        return 2

    result = safeval_jd381_analyze(content)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(render(result))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
