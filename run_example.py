"""
快速测试脚本 - 仅执行 eth_blockNumber 验证 RPC 连通性
适合在配置 API Key 前或网络异常时排查问题
"""
import sys
from src.config_loader import get_rpc_url, get_wallet_headers, load_config
from src.rpc_client import RPCClient

def main():
    provider = sys.argv[1] if len(sys.argv) > 1 else "public_sepolia"
    wallet = "metamask"

    print(f"测试 RPC: {provider} | 钱包模拟: {wallet}")
    try:
        url = get_rpc_url(provider)
        print(f"  URL: {url}")
    except Exception as e:
        print(f"  配置错误: {e}")
        return 1

    client = RPCClient(provider_id=provider, wallet_id=wallet)
    try:
        block = client.call("eth_blockNumber", [])
        print(f"  当前区块: {block} (十进制: {int(block, 16)})")
        print("  连通性正常")
    except Exception as e:
        print(f"  请求失败: {e}")
        print("  提示: 若在国内，可能需要配置代理访问 Sepolia RPC")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
