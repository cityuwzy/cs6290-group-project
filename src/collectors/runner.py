"""
场景执行器 - 遍历钱包 x RPC x 场景，收集数据
"""
from typing import Any

from ..config_loader import load_config
from ..rpc_client import RPCClient, RPCRequestRecord, RPCResponseRecord
from ..scenarios.balance_query import BalanceQueryScenario
from ..scenarios.block_query import BlockQueryScenario
from ..scenarios.token_transfer import TokenTransferScenario
from ..scenarios.uniswap_swap import UniswapSwapScenario
from ..analyzers.privacy_analyzer import analyze_request, aggregate_by_dimension, DimensionResult


SCENARIOS = [
    BalanceQueryScenario(),
    TokenTransferScenario(),
    UniswapSwapScenario(),
    BlockQueryScenario(),
]


def run_all(
    wallets: list[str] = None,
    providers: list[str] = None,
    scenarios: list = None,
) -> dict[str, Any]:
    """执行全部组合，返回收集的数据与分析结果"""
    config = load_config()
    wallets = wallets or list(config["wallets"].keys())
    providers = providers or list(config["rpc_providers"].keys())
    scenarios = scenarios or SCENARIOS

    all_records: list[tuple[RPCRequestRecord, RPCResponseRecord]] = []
    scenario_results: dict[str, Any] = {}
    errors: list[dict] = []

    for wallet_id in wallets:
        for provider_id in providers:
            client = RPCClient(provider_id=provider_id, wallet_id=wallet_id)
            for scenario in scenarios:
                key = f"{wallet_id}_{provider_id}_{scenario.id}"
                try:
                    scenario.run(client)
                    records = client.get_records()
                    all_records.extend(records)
                    scenario_results[key] = {"status": "ok", "requests": len(records)}
                except Exception as e:
                    errors.append({"key": key, "error": str(e)})
                    scenario_results[key] = {"status": "error", "error": str(e)}

    # 隐私分析
    dimension_results: list[list[DimensionResult]] = []
    for req, resp in all_records:
        dimension_results.append(analyze_request(req, resp))

    aggregated = aggregate_by_dimension(dimension_results)

    return {
        "config": {
            "wallets": wallets,
            "providers": providers,
            "scenarios": [s.id for s in scenarios],
        },
        "summary": {
            "total_requests": len(all_records),
            "errors": len(errors),
            "dimensions_affected": len(aggregated),
        },
        "records": [
            {
                "method": req.method,
                "wallet": req.wallet_id,
                "provider": req.provider_id,
                "exposed_addresses": req.exposed_addresses,
            }
            for req, _ in all_records
        ],
        "privacy_analysis": {
            dim_id: {
                "name": r.dimension_name,
                "risk_level": r.risk_level,
                "description": r.description,
                "evidence": r.evidence,
                "recommendation": r.recommendation,
            }
            for dim_id, r in aggregated.items()
        },
        "scenario_results": scenario_results,
        "errors": errors,
    }
