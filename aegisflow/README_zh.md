# AegisFlow 中文说明

<h1 align="center">
  <img src="https://img.shields.io/badge/版本-0.1.0-blue" alt="version">
  <img src="https://img.shields.io/badge/Python-3.10+-green" alt="python">
  <img src="https://img.shields.io/badge/许可证-MIT-brightgreen" alt="license">
</h1>

<p align="center">
  <b>企业级 AI Agent 运行时治理平台</b><br>
  策略驱动 · 预算管控 · 人机协同 · 全程可审计
</p>

---

## 什么是 AegisFlow？

AegisFlow 是一个企业级 AI Agent 运行时治理平台。它位于业务逻辑与 AI Agent 执行之间，强制执行安全策略、追踪预算消耗、管理人机审批流程、智能压缩上下文，并提供完整的审计轨迹。

### 解决的五大痛点

1. **成本爆炸**：概念验证到生产的成本飙升 1000 倍（月费 $500 → $847K）
2. **可观察但不可控**：89% 有监控，但 32% 仍有质量问题
3. **安全缺口**：Agent 无防护地执行写操作、网络调用、文件访问
4. **人类信任鸿沟**：缺少结构化的关键决策审批流程
5. **上下文膨胀**：无限制的上下文窗口浪费 60-95% Token

### 核心能力

| 模块 | 功能 | 技术特色 |
|---|---|---|
| Policy Engine | 策略引擎 | 声明式规则，正则匹配，支持 Allow/Deny/HumanLoop |
| Budget Guard | 预算管控 | 日/月/单次三级限制，频率节流 |
| Human Gateway | 人机协同 | 审批队列，超时自动升级 |
| Context Compress | 上下文压缩 | 内容路由 + 缓存对齐，借鉴 Headroom |
| Sandbox Executor | 沙箱执行 | 虚拟文件系统 + 进程隔离，借鉴 Mirage |
| Audit Trail | 审计追踪 | 不可篡改，加密存储，SQL 查询 |

## 快速开始

### 后端

```bash
cd backend
pip install -e .
python -m aegisflow.main --config config.yaml
```

API 地址：`http://localhost:8000`  
API 文档：`http://localhost:8000/docs`

### 前端

```bash
cd frontend
npm install
npm start
```

仪表盘地址：`http://localhost:3000`

### Docker

```bash
docker-compose up -d
```

## 执行流水线（7 步）

```
Agent 请求
  │
  ▼
[1] 策略检查 ── 拒绝？→ 返回拒绝原因
  │ 通过
  ▼
[2] 预算检查 ── 超限？→ 返回配额不足
  │ 通过
  ▼
[3] 上下文压缩 ── 优化载荷
  │
  ▼
[4] 人工审批 ── 拒绝/超时？→ 返回被拒
  │ 通过
  ▼
[5] 沙箱执行 ── 出错？→ 记录并拒绝
  │ 成功
  ▼
[6] 预算扣减 ── 扣减 Token
  │
  ▼
[7] 审计记录 ── 不可篡改日志
```

## 与同类方案对比

| 功能 | 无 AegisFlow | 有 AegisFlow |
|---|---|---|
| 策略执行 | 人工代码审查 | 声明式规则自动执行 |
| 预算控制 | 无限制/意外账单 | Token 封顶+节流+告警 |
| 审计追踪 | 分散的日志 | 不可篡改加密审计 |
| 人工审批 | 临时 Slack 消息 | 结构化审批+自动升级 |
| 上下文管理 | 无限制浪费 | 智能压缩，节省 60-95% |
| 沙箱隔离 | 直接系统访问 | 虚拟 FS + 进程隔离 |

## 灵感来源

AegisFlow 融合了以下优秀开源项目的核心思想：
- **Headroom**（32K⭐）— Token 压缩与上下文优化
- **Mirage** — 沙箱执行与进程隔离
- **微软 AI Agent 治理工具包** — 企业策略框架
- **Bifrost** — 低延迟护栏网关
- **MemPalace** — 分层记忆架构

## 项目结构

```
aegisflow/
├── backend/
│   ├── src/aegisflow/
│   │   ├── core/          # 编排器、配置、上下文
│   │   ├── policy/        # 策略引擎、规则匹配
│   │   ├── budget/        # 预算管控、Token 计数
│   │   ├── compress/      # 上下文压缩
│   │   ├── sandbox/       # 沙箱执行
│   │   ├── audit/         # 审计追踪
│   │   ├── human_loop/    # 人机协同
│   │   └── api/           # FastAPI 服务、WebSocket
│   ├── tests/             # 测试套件
│   ├── config.yaml        # 默认策略配置
│   └── pyproject.toml
├── frontend/
│   ├── src/               # React 组件
│   └── public/
├── docs/                  # 文档
├── examples/              # 使用示例
├── docker-compose.yml
├── .gitignore
├── LICENSE
└── README.md
```

## 贡献指南

欢迎贡献！详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 开源协议

MIT License — 个人和商业用途均免费。

---

<p align="center">
  为 Agent 原生企业而生
</p>
