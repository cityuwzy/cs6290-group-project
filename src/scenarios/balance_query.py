"""场景1：余额查询"""
from ..rpc_client import RPCClient
from .base import BaseScenario


class BalanceQueryScenario(BaseScenario):
    """余额查询 - eth_getBalance / eth_getCode"""

    id = "balance_query"
    name = "余额查询"
    description = "查询 ETH 余额、ERC20 余额（通过 eth_call）"

    def get_privacy_impact(self) -> list[str]:
        return ["ip_exposure", "address_association", "request_header_fingerprint"]

    def run(self, client: RPCClient, address: str = None, **kwargs) -> dict:
        # 使用 Sepolia 上的常见测试地址（公开水龙头地址）
        addr = address or "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1"
        result = {}

        # eth_getBalance - 暴露 from 地址
        balance_hex = client.call("eth_getBalance", [addr, "latest"])
        result["eth_balance"] = balance_hex

        # eth_getTransactionCount - 暴露地址
        nonce = client.call("eth_getTransactionCount", [addr, "latest"])
        result["nonce"] = nonce

        return result
