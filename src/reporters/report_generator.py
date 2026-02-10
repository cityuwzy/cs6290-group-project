"""报告生成器 - Markdown / HTML"""
from datetime import datetime
from pathlib import Path
from typing import Any


def generate_markdown_report(data: dict[str, Any]) -> str:
    """生成 Markdown 格式报告"""
    lines = [
        "# RPC 隐私泄露分析报告",
        "",
        f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 1. 项目概述",
        "",
        "本报告对 **3 款主流钱包** (MetaMask、Trust Wallet、Coinbase Wallet) 与 **3 款公共 RPC** (Infura、Alchemy、Chainstack) 在 **Sepolia 测试网** 下的隐私泄露情况进行模拟分析。",
        "",
        "### 操作场景",
        "- 余额查询",
        "- 代币转账（estimateGas）",
        "- Uniswap 小额兑换（eth_call）",
        "- 区块信息查询",
        "",
        "### 隐私泄露维度",
        "- IP 地址暴露",
        "- 钱包地址关联",
        "- 交易行为溯源",
        "- 调用参数敏感信息泄露",
        "- 请求头唯一标识泄露",
        "",
        "---",
        "",
        "## 2. 执行摘要",
        "",
        f"- 总请求数: **{data['summary']['total_requests']}**",
        f"- 错误数: **{data['summary']['errors']}**",
        f"- 涉及的隐私维度: **{data['summary']['dimensions_affected']}**",
        "",
        "---",
        "",
        "## 3. 隐私分析详情",
        "",
    ]

    for dim_id, info in data.get("privacy_analysis", {}).items():
        lines.extend([
            f"### {info['name']} ({dim_id})",
            "",
            f"- **风险等级**: {info['risk_level']}",
            f"- **描述**: {info['description']}",
            "",
            "**证据**:",
            "",
        ])
        for ev in info.get("evidence", []):
            lines.append(f"- {ev}")
        lines.extend([
            "",
            f"**建议**: {info.get('recommendation', '-')}",
            "",
        ])

    lines.extend([
        "---",
        "",
        "## 4. 请求记录示例",
        "",
    ])
    for r in data.get("records", [])[:20]:
        lines.append(f"- `{r['method']}` | {r['wallet']} → {r['provider']} | 暴露地址: {r.get('exposed_addresses', [])}")
    if len(data.get("records", [])) > 20:
        lines.append(f"- ... 共 {len(data['records'])} 条")

    if data.get("errors"):
        lines.extend([
            "",
            "---",
            "",
            "## 5. 执行错误",
            "",
        ])
        for err in data["errors"]:
            lines.append(f"- **{err.get('key', '')}**: {err.get('error', '')}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## 6. 结论与改进建议",
        "",
        "1. **IP 暴露**：所有 RPC 请求均会暴露 IP，建议使用代理或去中心化 RPC 聚合。",
        "2. **地址关联**：eth_getBalance、eth_call 等必然暴露钱包地址，难以完全避免。",
        "3. **调用参数**：eth_estimateGas、eth_call 的 data 包含完整 ABI，可解析敏感参数。",
        "4. **请求头**：不同钱包的 User-Agent/Origin 差异明显，可被用于指纹识别。",
        "",
    ])

    return "\n".join(lines)


def save_report(data: dict[str, Any], output_path: Path) -> None:
    """保存 Markdown 报告到文件"""
    content = generate_markdown_report(data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
