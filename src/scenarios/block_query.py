"""场景4：区块信息查询"""
from ..rpc_client import RPCClient
from .base import BaseScenario


class BlockQueryScenario(BaseScenario):
    """区块信息查询 - eth_blockNumber, eth_getBlockByNumber"""

    id = "block_query"
    name = "区块信息查询"
    description = "查询最新区块号、区块详情"

    def get_privacy_impact(self) -> list[str]:
        # 区块查询一般不直接暴露钱包地址，但仍会暴露 IP 和请求头
        return ["ip_exposure", "request_header_fingerprint"]

    def run(self, client: RPCClient, **kwargs) -> dict:
        block_hex = client.call("eth_blockNumber", [])
        block_num = int(block_hex, 16)
        # 获取最近区块详情（含交易列表）
        block = client.call(
            "eth_getBlockByNumber",
            [hex(block_num), False],  # false = 不返回完整交易
        )
        return {
            "block_number": block_num,
            "block_hash": block.get("hash") if block else None,
            "tx_count": len(block.get("transactions", [])) if block else 0,
        }
