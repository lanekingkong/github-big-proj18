# 5W1H Architecture Document — AegisFlow

## 1. WHAT — 项目是什么？

AegisFlow 是一个 **企业级 AI Agent 运行时治理平台**。它提供统一的运行时网关层，在 AI Agent 执行之前，强制执行策略检查、预算管控、人工审批、上下文压缩、沙箱隔离，并在执行后保留完整的不可篡改审计记录。

### 核心功能矩阵
- **策略引擎**：声明式规则系统，支持 Allow/Deny/HumanLoop 三种动作
- **预算管控**：日/月/请求三级 Token 限制 + 频率节流
- **人机协同网关**：结构化审批流程，超时自动升级
- **上下文压缩**：内容类型路由 + 缓存前缀对齐，节省 60-95% Token
- **沙箱执行**：虚拟文件系统 + 进程隔离
- **审计追踪**：不可篡改加密审计日志，支持全量查询

---

## 2. WHY — 为什么需要？

### 2.1 行业痛点分析

| 痛点 | 严重程度 | 数据支撑 |
|---|---|---|
| POC→生产 成本爆炸 | 🔴 紧急 | 月费 $500→$847K，1000x 增长 |
| 可观察≠可控制 | 🟡 严重 | 89% 监控覆盖，但 32% 仍有质量问题 |
| 安全执行缺口 | 🔴 紧急 | Agent 绕过权限直接操作系统/网络/数据库 |
| 人类信任鸿沟 | 🟡 严重 | 缺少结构化信任传递机制 |
| 上下文膨胀浪费 | 🟡 严重 | 60-95% Token 被重复/无用内容消耗 |

### 2.2 为什么现有方案不够？

- **LangChain/LlamaIndex**：只做编排，不做治理
- **Guardrails AI**：只做安全护栏，不涵盖预算和审计
- **Datadog/LangSmith**：只能观察，不能拦截
- **自研方案**：企业各自造轮子，无统一标准

### 2.3 项目价值主张

AegisFlow = 策略引擎 + 预算管控 + 人机协同 + 审计追踪 = **AI Agent 生产化的最后一道防线**

---

## 3. WHO — 谁在用？为谁而建？

### 3.1 目标用户画像

| 角色 | 痛点 | AegisFlow 价值 |
|---|---|---|
| **CTO/技术VP** | Agent 生产事故风险不可控 | 统一治理策略，风险可视化 |
| **AI 平台负责人** | Token 成本每月爆炸 | 预算封顶 + 实时追踪 |
| **安全合规官** | 审计无法覆盖 Agent 操作 | 完整不可篡改审计记录 |
| **Agent 开发者** | 每次都要自建安全检查 | 声明式策略，一次配置 |
| **运维/SRE** | Agent 行为无法监控 | 实时仪表盘 + WebSocket |

### 3.2 适用场景

- 企业内部 AI Agent 平台（HR、财务、客服 Agent）
- AI SaaS 产品的 Agent 层治理
- Agent 安全合规审计
- 多 Agent 协作的预算和策略管理

---

## 4. WHEN — 何时使用？

### 4.1 触发场景

1. **Agent 从开发环境进入生产环境** → 部署 AegisFlow 网关
2. **Token 成本突然飙升** → 启用预算管控模式
3. **合规审计要求** → 开启审计追踪
4. **发现 Agent 越权操作** → 启用策略引擎 + 沙箱
5. **需要人工审批关键操作** → 配置 Human-in-the-Loop 规则

### 4.2 实施路径

| 阶段 | 时间 | 动作 |
|---|---|---|
| Phase 1: 监控模式 | 第 1-2 周 | 部署 AegisFlow，只审计不拦截 |
| Phase 2: 策略模式 | 第 3-4 周 | 逐步启用 Deny 和 HumanLoop 规则 |
| Phase 3: 成本管控 | 第 5-6 周 | 设置预算上限，追踪优化 |
| Phase 4: 全量治理 | 第 7-8 周 | 沙箱隔离 + 全面压缩 |

---

## 5. WHERE — 部署在哪里？

### 5.1 部署架构

```
┌─────────────────────────────────────────────────┐
│                   Client Apps                     │
│          (API calls / WebSocket / SDK)            │
└──────────────────────────┬──────────────────────┘
                           │
┌──────────────────────────▼──────────────────────┐
│              AegisFlow Gateway (FastAPI)           │
│  ┌──────────┬──────────┬──────────┬──────────┐  │
│  │ Policy   │ Budget   │ Compress │ Sandbox  │  │
│  │ Engine   │ Guard    │ Engine   │ Executor │  │
│  └──────────┴──────────┴──────────┴──────────┘  │
│  ┌──────────┬──────────┐                         │
│  │ Human    │ Audit    │                         │
│  │ Gateway  │ Trail    │                         │
│  └──────────┴──────────┘                         │
└──────────────────────────┬──────────────────────┘
                           │
┌──────────────────────────▼──────────────────────┐
│                  AI Agent Runtime                  │
│          (LangChain / CrewAI / Custom)            │
└─────────────────────────────────────────────────┘
```

### 5.2 部署选项

| 方式 | 适用场景 |
|---|---|
| Docker Compose | 单机部署 / 开发测试 |
| Kubernetes | 生产集群部署 |
| 嵌入式 SDK | 直接集成到 Agent 代码中 |

---

## 6. HOW — 如何实现？

### 6.1 技术栈

| 层级 | 技术选型 |
|---|---|
| API 网关 | FastAPI + Uvicorn |
| 实时通信 | WebSocket |
| 数据存储 | SQLite（审计） + 内存（预算） |
| 前端 | React 18 + Recharts |
| 容器化 | Docker + Docker Compose |
| 测试 | pytest + httpx |

### 6.2 核心模块设计

#### Policy Engine
- **PolicySet**：规则集合，按优先级排序
- **PolicyRule**：单条规则，包含 resource/action/conditions/risk_level
- **PolicyEngine**：引擎入口，加载策略 + 执行评估
- **PolicyLoader**：从 JSON/YAML 加载策略

#### Budget Guard
- **BudgetGuard**：预算总控，check + consume
- **TokenCounter**：Token 计数器，支持日/月统计 + 自动重置
- **ThrottleController**：滑动窗口限流器

#### Context Compressor（借鉴 Headroom）
- **ContentRouter**：检测内容类型（JSON/Code/Log/Text）
- **CacheAligner**：前缀缓存对齐，识别重复前缀
- **CCRManager**：可逆压缩存储，支持压缩 ↔ 解压

#### Sandbox Executor（借鉴 Mirage）
- **VirtualFS**：虚拟文件系统，路径白名单/黑名单
- **ProcessIsolator**：进程隔离，限制进程数/内存

#### Human-in-the-Loop Gateway
- **ApprovalQueue**：审批队列，支持异步等待
- **HumanLoopGateway**：网关入口，支持自动升级

#### Audit Trail
- **AuditStorage**：SQLite 持久化，可选加密
- **AuditTrail**：审计业务逻辑层

### 6.3 项目吸取的开源项目精华

| 来源项目 | ⭐ | 借鉴内容 |
|---|---|---|
| Headroom | 32K | CBDCacheAligner + ContentRouter + SmartCrusher 压缩机制 |
| Mirage | - | VirtualFS 虚拟文件系统 + ProcessIsolator 进程隔离 |
| 微软 AI Agent Governance | MIT | 企业级策略框架 + 规则优先级 |
| Bifrost | - | 低延迟网关架构，11μs 执行 |
| MemPalace | - | 分层记忆 + 上下文管理 |

### 6.4 未来路线图

- [ ] Redis 支持分布式预算计数
- [ ] PostgreSQL 审计存储后端
- [ ] gRPC API 支持
- [ ] OIDC/OAuth2 认证集成
- [ ] Kubernetes Operator 自动部署
- [ ] 多租户隔离
- [ ] 策略市场（社区共享策略模板）
- [ ] LLM 评估集成（自动检测有害输出）
