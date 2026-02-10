"""场景3：Uniswap 小额兑换（eth_call 模拟报价）"""
from ..rpc_client import RPCClient
from .base import BaseScenario


# Uniswap V2 swapExactTokensForTokens 等函数会暴露 path、amountIn、amountOutMin 等
# 这里用 getAmountsOut 作为只读调用示例
SWAP_AMOUNTS_OUT_SELECTOR = "0x5c11d795"  # getAmountsOut(uint,address[])


def _encode_address(addr: str) -> str:
    return addr[2:].lower().zfill(64)


def _encode_uint256(value: int) -> str:
    return hex(value)[2:].zfill(64)


def build_get_amounts_out_data(amount_in: int, path: list[str]) -> str:
    """构建 getAmountsOut 的 ABI 编码（简化）"""
    # 简化：仅示意结构，完整 ABI 编码需 eth_abi
    head = SWAP_AMOUNTS_OUT_SELECTOR + _encode_uint256(amount_in)
    # 动态类型 offset 等略，此处用占位
    return head


class UniswapSwapScenario(BaseScenario):
    """Uniswap 小额兑换 - eth_call 获取报价"""

    id = "uniswap_swap"
    name = "Uniswap 小额兑换"
    description = "调用 Uniswap Router 的 getAmountsOut 获取兑换报价"

    def get_privacy_impact(self) -> list[str]:
        return [
            "ip_exposure",
            "address_association",
            "call_params_leak",
            "transaction_tracing",
            "request_header_fingerprint",
        ]

    def run(
        self,
        client: RPCClient,
        router_address: str = None,
        amount_in: int = 10**18,
        **kwargs,
    ) -> dict:
        config = __import__("..config_loader", fromlist=["load_config"]).load_config()
        router = router_address or config["contracts"]["uniswap_v2_router"]
        weth = config["contracts"]["weth_sepolia"]
        # 简化 path: WETH -> 某 ERC20
        path = [weth, config["contracts"]["test_erc20"]]

        # 使用静态 ABI 编码简化版（实际项目可用 web3 的 encode_abi）
        data = build_get_amounts_out_data(amount_in, path)
        call_params = {
            "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
            "to": router,
            "data": data,
            "gas": "0x100000",
        }

        result_hex = client.call("eth_call", [call_params, "latest"])
        return {"result": result_hex, "amount_in": amount_in}
