"""
RPC 客户端 - 模拟不同钱包向不同 RPC 节点发起请求
支持记录请求/响应，供隐私分析使用
"""
import json
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import requests

from .config_loader import get_rpc_url, get_wallet_headers, load_config


@dataclass
class RPCRequestRecord:
    """单次 RPC 请求记录，用于隐私分析"""
    method: str
    params: list
    wallet_id: str
    provider_id: str
    headers_sent: dict
    timestamp: float
    # 隐私相关：请求中暴露的数据
    exposed_addresses: list[str] = field(default_factory=list)
    exposed_params_summary: str = ""


@dataclass
class RPCResponseRecord:
    """RPC 响应记录"""
    request: RPCRequestRecord
    result: Any
    error: Optional[dict]
    elapsed_ms: float


def _extract_addresses_from_params(params: list) -> list[str]:
    """从 RPC 参数中提取可能暴露的钱包地址"""
    addresses = []
    for p in params:
        if isinstance(p, dict):
            for k in ("from", "to", "address"):
                if k in p and p[k] and isinstance(p[k], str) and p[k].startswith("0x"):
                    addresses.append(p[k])
        elif isinstance(p, str) and p.startswith("0x") and len(p) == 42:
            addresses.append(p)
    return list(set(addresses))


def _summarize_call_data(data: str) -> str:
    """简要描述 eth_call data 中的敏感信息（不解析完整 ABI）"""
    if not data or not isinstance(data, str):
        return ""
    if len(data) < 10:
        return data
    # 函数选择器 4 字节 + 参数
    return f"selector={data[:10]}..., len={len(data)}"


class RPCClient:
    """RPC 客户端，支持钱包模拟与请求记录"""

    def __init__(self, provider_id: str, wallet_id: str, timeout: int = 30):
        self.provider_id = provider_id
        self.wallet_id = wallet_id
        self.timeout = timeout
        self._url = get_rpc_url(provider_id)
        self._headers = get_wallet_headers(wallet_id)
        self._records: list[tuple[RPCRequestRecord, RPCResponseRecord]] = []

    def call(self, method: str, params: list, record: bool = True) -> Any:
        """发起 JSON-RPC 调用"""
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}

        req_record = None
        if record:
            exposed = _extract_addresses_from_params(params)
            call_summary = ""
            for p in params:
                if isinstance(p, dict) and "data" in p:
                    call_summary = _summarize_call_data(p.get("data", ""))
                    break

            req_record = RPCRequestRecord(
                method=method,
                params=params,
                wallet_id=self.wallet_id,
                provider_id=self.provider_id,
                headers_sent=dict(self._headers),
                timestamp=time.time(),
                exposed_addresses=exposed,
                exposed_params_summary=call_summary,
            )

        start = time.perf_counter()
        try:
            resp = requests.post(
                self._url,
                headers=self._headers,
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            elapsed = (time.perf_counter() - start) * 1000

            result = data.get("result")
            error = data.get("error")

            if req_record:
                resp_record = RPCResponseRecord(
                    request=req_record,
                    result=result,
                    error=error,
                    elapsed_ms=elapsed,
                )
                self._records.append((req_record, resp_record))

            if error:
                raise RuntimeError(f"RPC error: {error}")
            return result

        except requests.RequestException as e:
            if req_record:
                resp_record = RPCResponseRecord(
                    request=req_record,
                    result=None,
                    error={"message": str(e)},
                    elapsed_ms=(time.perf_counter() - start) * 1000,
                )
                self._records.append((req_record, resp_record))
            raise

    def get_records(self) -> list[tuple[RPCRequestRecord, RPCResponseRecord]]:
        return self._records

    def clear_records(self):
        self._records.clear()
