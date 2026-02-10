#!/usr/bin/env python3
"""
RPC 隐私泄露分析 - 主入口
用法: python main.py [--dry-run] [--providers infura,alchemy] [--output report.md]
"""
import argparse
import json
from pathlib import Path

from src.collectors.runner import run_all
from src.reporters.report_generator import generate_markdown_report, save_report


def main():
    parser = argparse.ArgumentParser(description="RPC 隐私泄露分析")
    parser.add_argument("--dry-run", action="store_true", help="仅检查配置，不实际请求")
    parser.add_argument(
        "--providers",
        type=str,
        default="public_sepolia",
        help="RPC 提供商，逗号分隔。默认 public_sepolia 无需 API Key",
    )
    parser.add_argument(
        "--wallets",
        type=str,
        default="metamask,trust_wallet,coinbase_wallet",
        help="钱包类型，逗号分隔",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/report.md",
        help="报告输出路径",
    )
    parser.add_argument(
        "--json",
        type=str,
        default="",
        help="同时输出 JSON 数据路径",
    )
    args = parser.parse_args()

    if args.dry_run:
        from src.config_loader import load_config, get_rpc_url, get_wallet_headers
        config = load_config()
        providers = args.providers.split(",")
        for p in providers:
            try:
                url = get_rpc_url(p.strip())
                print(f"[OK] {p}: {url[:50]}...")
            except Exception as e:
                print(f"[FAIL] {p}: {e}")
        return

    providers = [p.strip() for p in args.providers.split(",")]
    wallets = [w.strip() for w in args.wallets.split(",")]

    print("开始执行 RPC 隐私分析...")
    print(f"  Wallets: {wallets}")
    print(f"  Providers: {providers}")

    data = run_all(wallets=wallets, providers=providers)

    # 输出报告
    out_path = Path(args.output)
    save_report(data, out_path)
    print(f"报告已保存: {out_path}")

    if args.json:
        json_path = Path(args.json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        # 简化 JSON（去掉不可序列化内容）
        json_data = {
            "config": data["config"],
            "summary": data["summary"],
            "privacy_analysis": data["privacy_analysis"],
            "errors": data.get("errors", []),
        }
        json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON 已保存: {json_path}")

    print("完成。")


if __name__ == "__main__":
    main()
