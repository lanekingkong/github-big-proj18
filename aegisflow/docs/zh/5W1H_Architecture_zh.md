# 5W1H 架构文档 — AegisFlow

## 一、WHAT — 是什么？

AegisFlow 是企业级 AI Agent 运行时治理平台，作为统一网关层，在 Agent 执行前进行策略检查、预算审查、内容压缩、人工审批和沙箱隔离，并在执行后保留不可篡改的审计记录。它解决的是 **"AI Agent 如何安全、可控、合规地投入生产"** 这一核心命题。

## 二、WHY — 为什么需要？

### 行业背景
- 2025-2026 年，AI Agent 从"炫酷 Demo"进入"生产落地"阶段
- 企业面临五大生产缺口：成本爆炸 / 可观察不可控 / 安全空白 / 信任鸿沟 / 上下文浪费
- 89% 企业有监控工具，但仅有 32% 能真正控制 Agent 行为质量

### 为什么现有方案不够？
| 方案 | 局限 |
|---|---|
| LangChain/LlamaIndex | 只编排不治理，无安全边界 |
| Guardrails AI | 只管安全护栏，无预算和审计 |
| Datadog/LangSmith | 只能观察不能拦截，滞后响应 |
| 企业自研 | 各自造轮子，无统一标准，维护成本高 |

AegisFlow 的价值：一次性覆盖策略/预算/审计/人机协同/沙箱五大维度，开箱即用。

## 三、WHO — 为谁而建？

| 用户角色 | 核心需求 | AegisFlow 如何满足 |
|---|---|---|
| CTO/技术VP | Agent 生产风险可控 | 统一治理策略 + 风险可视化 |
| AI 平台负责人 | 控制 Token 成本 | 预算封顶 + 实时追踪 + 告警 |
| 安全合规官 | Agent 操作可审计 | 不可篡改加密审计日志 |
| Agent 开发者 | 减少重复造轮子 | 声明式策略，一次配置 |
| SRE/运维 | Agent 行为可监控 | 实时仪表盘 + WebSocket |

适用行业：金融（合规）、医疗（数据安全）、企业服务（多租户）、AI SaaS（成本控制）。

## 四、WHEN — 何时使用？

### 触发时机
1. Agent 从开发环境迁移到生产环境
2. Token 成本月度账单超出预算 3 倍以上
3. 合规审计要求覆盖 Agent 操作
4. 发现 Agent 绕过权限执行敏感操作
5. 需要为关键决策引入人工审批

### 实施四阶段
| 阶段 | 内容 | 周期 |
|---|---|---|
| 监控模式 | 部署网关，仅审计不拦截 | 1-2 周 |
| 策略模式 | 逐步启用 Deny + HumanLoop 规则 | 3-4 周 |
| 成本管控 | 设置预算上限，追踪优化 | 5-6 周 |
| 全量治理 | 沙箱隔离 + 全面压缩 | 7-8 周 |

## 五、WHERE — 部署在哪里？

### 架构定位
AegisFlow 位于客户端应用与 AI Agent 运行时之间，充当**透明代理网关**。所有 Agent 请求必须经过 AegisFlow 的 7 步流水线，任何一个环节拒绝都将终止请求。

### 部署选择
- **Docker Compose**：开发 / 单机 / 小团队
- **Kubernetes**：生产集群 / 高可用
- **嵌入式 SDK**：直接在 Agent 代码中集成 `aegisflow` Python 包

## 六、HOW — 如何实现？

### 技术选型
| 层级 | 技术 | 理由 |
|---|---|---|
| API | FastAPI + Uvicorn | 高性能异步，原生 OpenAPI |
| 实时 | WebSocket | 低延迟双向通信 |
| 存储 | SQLite (WAL) | 零配置，适合嵌入式 |
| 前端 | React 18 + Recharts | 快速构建仪表盘 |
| 容器 | Docker Compose | 一键启动 |

### 核心设计决策

1. **内存预算计数**：日/月统计数据存内存，定期持久化计划支持 Redis
2. **SQLite WAL 审计**：WAL 模式支持并发读写，可后续迁移 PostgreSQL
3. **正则策略匹配**：灵活且高性能，满足 99% 场景
4. **内容类型自动检测**：无需手动标注，自动识别 JSON/Code/Log
5. **异步审批队列**：基于 asyncio.Event，天然非阻塞

### 借鉴的开源精华

| 源项目 | 借鉴内容 | 消化方式 |
|---|---|---|
| Headroom (32K⭐) | CBDCacheAligner + CCR | 重写为纯 Python，嵌入网关 |
| Mirage | VirtualFS + ProcessIsolator | 简化版，专注 Agent 场景 |
| 微软治理工具包 | 策略框架 + 优先级模型 | 扩展为 Allow/Deny/HumanLoop 三元组 |
| Bifrost | 低延迟网关 | 抽取架构思路，FastAPI 实现 |
| MemPalace | 分层记忆 | 转化为 Context 压缩策略 |

### 未来路线
- 分布式预算（Redis 后端）
- 审计迁移 PostgreSQL
- gRPC API
- Kubernetes Operator
- 策略模板市场
- LLM 输出质量自动评估
