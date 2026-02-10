"""
隐私泄露分析器
维度：IP暴露、地址关联、交易溯源、调用参数泄露、请求头指纹
"""
from dataclasses import dataclass, field
from typing import Any

from ..rpc_client import RPCRequestRecord, RPCResponseRecord


@dataclass
class DimensionResult:
    """单维度分析结果"""
    dimension_id: str
    dimension_name: str
    risk_level: str  # low / medium / high / critical
    description: str
    evidence: list[str] = field(default_factory=list)
    recommendation: str = ""


# 各 RPC 方法对应的隐私暴露
METHOD_PRIVACY_MAP = {
    "eth_getBalance": ["address_association"],
    "eth_getTransactionCount": ["address_association"],
    "eth_estimateGas": ["address_association", "call_params_leak"],
    "eth_call": ["address_association", "call_params_leak"],
    "eth_sendRawTransaction": ["address_association", "transaction_tracing", "call_params_leak"],
    "eth_getTransactionByHash": ["transaction_tracing"],
    "eth_getBlockByNumber": [],
    "eth_blockNumber": [],
}


def analyze_request(req: RPCRequestRecord, resp: RPCResponseRecord) -> list[DimensionResult]:
    """分析单次请求的隐私泄露"""
    results = []

    # 1. IP 地址暴露 - 所有请求都有
    results.append(DimensionResult(
        dimension_id="ip_exposure",
        dimension_name="IP 地址暴露",
        risk_level="high",
        description="RPC 节点可记录请求来源 IP，用于地理位置与身份关联",
        evidence=[
            "请求直接发送至 RPC 节点，节点可记录来源 IP",
            f"Provider: {req.provider_id}",
        ],
        recommendation="使用代理/VPN 或 Tor，或使用去中心化 RPC 聚合服务",
    ))

    # 2. 钱包地址关联
    if req.exposed_addresses:
        results.append(DimensionResult(
            dimension_id="address_association",
            dimension_name="钱包地址关联",
            risk_level="high",
            description="RPC 参数中的 from/to 暴露钱包地址，可与 IP 关联",
            evidence=[
                f"Method: {req.method}",
                f"Exposed addresses: {req.exposed_addresses}",
            ],
            recommendation="无法完全避免，可考虑使用多个 RPC 分散请求",
        ))

    # 3. 调用参数敏感信息
    if req.exposed_params_summary and req.method in ("eth_call", "eth_estimateGas"):
        results.append(DimensionResult(
            dimension_id="call_params_leak",
            dimension_name="调用参数敏感信息泄露",
            risk_level="high",
            description="data 字段包含完整 ABI 编码，可解析出函数名、参数值",
            evidence=[
                f"Method: {req.method}",
                f"Params summary: {req.exposed_params_summary}",
            ],
            recommendation="敏感参数可考虑链下加密或零知识证明",
        ))

    # 4. 交易行为溯源（针对交易相关方法）
    if req.method in ("eth_sendRawTransaction", "eth_getTransactionByHash"):
        results.append(DimensionResult(
            dimension_id="transaction_tracing",
            dimension_name="交易行为溯源",
            risk_level="medium",
            description="交易提交与查询可被 RPC 节点记录，用于行为分析",
            evidence=[f"Method: {req.method}"],
            recommendation="使用不同 RPC 提交交易与查询，降低关联度",
        ))

    # 5. 请求头唯一标识
    fingerprint_headers = ["User-Agent", "Origin", "X-Client", "X-Requested-With"]
    found = [h for h in fingerprint_headers if h in req.headers_sent and req.headers_sent.get(h)]
    if found:
        results.append(DimensionResult(
            dimension_id="request_header_fingerprint",
            dimension_name="请求头唯一标识泄露",
            risk_level="medium",
            description="User-Agent、Origin 等可能构成设备/应用指纹",
            evidence=[
                f"Wallet: {req.wallet_id}",
                f"Relevant headers: {[(h, req.headers_sent.get(h, '')[:50]) for h in found]}",
            ],
            recommendation="统一请求头或使用通用客户端减少指纹区分度",
        ))

    return results


def aggregate_by_dimension(
    all_results: list[list[DimensionResult]],
) -> dict[str, DimensionResult]:
    """按维度聚合，取最高风险"""
    by_dim: dict[str, DimensionResult] = {}
    risk_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}

    for results in all_results:
        for r in results:
            if r.dimension_id not in by_dim or risk_order.get(r.risk_level, 0) > risk_order.get(
                by_dim[r.dimension_id].risk_level, 0
            ):
                by_dim[r.dimension_id] = r
                # 合并证据
                if r not in results:
                    pass
                existing = by_dim[r.dimension_id]
                for ev in r.evidence:
                    if ev not in existing.evidence:
                        existing.evidence.append(ev)

    return by_dim
