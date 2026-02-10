"""配置加载模块"""
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

# 加载 .env
load_dotenv(Path(__file__).parent.parent / ".env")


def load_config():
    """加载 config.yaml"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_rpc_url(provider_id: str) -> str:
    """根据 provider 和 env 中的 API Key 构建 RPC URL"""
    config = load_config()
    providers = config["rpc_providers"]
    if provider_id not in providers:
        raise ValueError(f"Unknown provider: {provider_id}")

    prov = providers[provider_id]
    if prov.get("no_api_key"):
        return prov["base_url"]

    env_key_map = {
        "infura": "INFURA_API_KEY",
        "alchemy": "ALCHEMY_API_KEY",
        "chainstack": "CHAINSTACK_API_KEY",
    }
    key = os.getenv(env_key_map.get(provider_id, ""), "")
    base = prov["base_url"]
    return base.replace("{api_key}", key)


def get_wallet_headers(wallet_id: str) -> dict:
    """获取模拟某款钱包的请求头"""
    config = load_config()
    w = config["wallets"][wallet_id]
    headers = {
        "Content-Type": "application/json",
        "User-Agent": w["user_agent"],
        "Origin": w.get("origin", ""),
        **(w.get("headers") or {}),
    }
    return {k: v for k, v in headers.items() if v}
