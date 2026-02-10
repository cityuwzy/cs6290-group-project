"""场景基类"""
from abc import ABC, abstractmethod
from typing import Any

from ..rpc_client import RPCClient


class BaseScenario(ABC):
    """操作场景基类"""

    id: str = ""
    name: str = ""
    description: str = ""

    @abstractmethod
    def run(self, client: RPCClient, **kwargs) -> Any:
        """执行场景，返回结果"""
        pass

    def get_privacy_impact(self) -> list[str]:
        """返回该场景涉及的隐私泄露维度 ID"""
        return []
