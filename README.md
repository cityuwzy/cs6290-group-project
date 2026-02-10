# RPC 隐私泄露分析项目

聚焦以太坊 Sepolia 测试网下，**3 款主流钱包** × **3 款公共 RPC** 在常规操作场景中的隐私泄露维度分析。

## 项目概述

| 维度 | 内容 |
|------|------|
| **钱包** | MetaMask、Trust Wallet、Coinbase Wallet |
| **RPC** | Infura、Alchemy、Chainstack + 公共 Sepolia 节点 |
| **网络** | 以太坊 Sepolia 测试网（避免主网交易成本） |
| **场景** | 余额查询、代币转账、Uniswap 兑换、区块查询 |
| **隐私维度** | IP 暴露、地址关联、交易溯源、调用参数泄露、请求头指纹 |

**不涉及**：钱包本地存储、私钥泄露等非 RPC 相关维度。

## 快速开始

### 1. 安装依赖

```bash
cd rpc_privacy_analysis
pip install -r requirements.txt
```

### 2. 无需 API Key 快速测试（推荐先用此方式验证）

使用公共 Sepolia RPC，无需申请任何 Key：

```bash
python main.py --providers public_sepolia --wallets metamask
```

### 3. 使用 Infura / Alchemy / Chainstack

1. 复制 `env.example.txt` 为 `.env`
2. 填入从各平台申请的 API Key（测试网有免费额度）
3. 执行：

```bash
python main.py --providers infura,alchemy,chainstack
```

### 4. 生成完整报告

```bash
python main.py --providers public_sepolia --output output/report.md --json output/data.json
```

### 5. 连通性测试

若报告显示错误，可先测试 RPC 连通性：

```bash
python run_example.py public_sepolia
```

若在国内网络环境，可能需要配置代理（在 `.env` 中设置 `HTTP_PROXY`/`HTTPS_PROXY`）。

## 项目结构

```
rpc_privacy_analysis/
├── config/
│   └── config.yaml          # 钱包特征、RPC 端点、合约地址
├── src/
│   ├── config_loader.py     # 配置加载
│   ├── rpc_client.py        # RPC 客户端（模拟钱包请求 + 记录）
│   ├── scenarios/           # 操作场景
│   │   ├── balance_query.py # 余额查询
│   │   ├── token_transfer.py# 代币转账（estimateGas）
│   │   ├── uniswap_swap.py  # Uniswap 兑换（eth_call）
│   │   └── block_query.py   # 区块信息查询
│   ├── analyzers/           # 隐私分析
│   │   └── privacy_analyzer.py
│   ├── collectors/          # 执行器
│   │   └── runner.py
│   └── reporters/           # 报告生成
│       └── report_generator.py
├── main.py                  # 入口
├── requirements.txt
└── README.md
```

## 隐私泄露维度说明

| ID | 名称 | 说明 |
|----|------|------|
| ip_exposure | IP 地址暴露 | RPC 节点可记录请求来源 IP |
| address_association | 钱包地址关联 | eth_getBalance、eth_call 等暴露 from/to |
| transaction_tracing | 交易行为溯源 | eth_sendRawTransaction、eth_getTransactionByHash |
| call_params_leak | 调用参数泄露 | eth_call、eth_estimateGas 的 data 含完整 ABI |
| request_header_fingerprint | 请求头指纹 | User-Agent、Origin 等可识别钱包/设备 |

## 命令行参数

```
python main.py [--dry-run] [--providers P] [--wallets W] [--output O] [--json J]
```

- `--dry-run`：只检查配置，不发起请求
- `--providers`：RPC 提供商，逗号分隔，默认 `public_sepolia`
- `--wallets`：钱包类型，逗号分隔
- `--output`：Markdown 报告路径
- `--json`：JSON 数据输出路径

## 可改进方向

1. **流量抓包**：集成 mitmproxy 抓取真实钱包流量进行对比
2. **Tor/VPN 测试**：验证代理对 IP 暴露的影响
3. **更多 RPC**：QuickNode、Ankr、Pocket Network 等
4. **链上交易**：真实发送 Sepolia 测试交易（需测试 ETH）
5. **HTML 报告**：生成可视化仪表盘

## 许可证

MIT
