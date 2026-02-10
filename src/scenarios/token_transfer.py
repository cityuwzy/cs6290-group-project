"""场景2：代币转账（模拟 eth_call estimateGas，不实际发送）"""
from ..rpc_client import RPCClient
from .base import BaseScenario


# ERC20 transfer(address,uint256) 函数选择器
TRANSFER_SELECTOR = "0xa9059cbb"


def _encode_uint256(value: int) -> str:
    return hex(value)[2:].zfill(64)


def _encode_address(addr: str) -> str:
    return addr[2:].lower().zfill(64)


def build_transfer_data(to: str, amount: int) -> str:
    """构建 ERC20 transfer 的 data"""
    return TRANSFER_SELECTOR + _encode_address(to) + _encode_uint256(amount)


class TokenTransferScenario(BaseScenario):
    """代币转账 - eth_estimateGas / eth_call（模拟）"""

    id = "token_transfer"
    name = "代币转账"
    description = "ERC20 转账前的 estimateGas 与 eth_call 预览"

    def get_privacy_impact(self) -> list[str]:
        return [
            "ip_exposure",
            "address_association",
            "call_params_leak",
            "request_header_fingerprint",
        ]

    def run(
        self,
        client: RPCClient,
        token_address: str = None,
        from_address: str = None,
        to_address: str = None,
        amount: int = 1000000,
        **kwargs,
    ) -> dict:
        config = __import__("..config_loader", fromlist=["load_config"]).load_config()
        token = token_address or config["contracts"]["test_erc20"]
        from_addr = from_address or "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1"
        to_addr = to_address or "0x0000000000000000000000000000000000000001"

        data = build_transfer_data(to_addr, amount)
        call_params = {
            "from": from_addr,
            "to": token,
            "data": data,
            "gas": "0x5208",
        }

        # eth_estimateGas - 暴露 from, to, data（含接收地址和金额）
        gas_hex = client.call("eth_estimateGas", [call_params])
        return {"estimated_gas": gas_hex, "from": from_addr, "to": to_addr}
