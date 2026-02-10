# RPC 隐私泄露分析报告

**生成时间**: 2026-02-09 13:49:28

## 1. 项目概述

本报告对 **3 款主流钱包** (MetaMask、Trust Wallet、Coinbase Wallet) 与 **3 款公共 RPC** (Infura、Alchemy、Chainstack) 在 **Sepolia 测试网** 下的隐私泄露情况进行模拟分析。

### 操作场景
- 余额查询
- 代币转账（estimateGas）
- Uniswap 小额兑换（eth_call）
- 区块信息查询

### 隐私泄露维度
- IP 地址暴露
- 钱包地址关联
- 交易行为溯源
- 调用参数敏感信息泄露
- 请求头唯一标识泄露

---

## 2. 执行摘要

- 总请求数: **0**
- 错误数: **4**
- 涉及的隐私维度: **0**

---

## 3. 隐私分析详情

---

## 4. 请求记录示例


---

## 5. 结论与改进建议

1. **IP 暴露**：所有 RPC 请求均会暴露 IP，建议使用代理或去中心化 RPC 聚合。
2. **地址关联**：eth_getBalance、eth_call 等必然暴露钱包地址，难以完全避免。
3. **调用参数**：eth_estimateGas、eth_call 的 data 包含完整 ABI，可解析敏感参数。
4. **请求头**：不同钱包的 User-Agent/Origin 差异明显，可被用于指纹识别。
