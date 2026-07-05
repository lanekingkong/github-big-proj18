# AegisFlow

<h1 align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue" alt="version">
  <img src="https://img.shields.io/badge/python-3.10+-green" alt="python">
  <img src="https://img.shields.io/badge/license-MIT-brightgreen" alt="license">
  <img src="https://img.shields.io/badge/status-prototype-orange" alt="status">
</h1>

<p align="center">
  <b>Enterprise AI Agent Runtime Governance Platform</b><br>
  Policy-Driven · Budget-Controlled · Human-in-the-Loop · Fully Auditable
</p>

---

## What is AegisFlow?

AegisFlow is an enterprise-grade runtime governance platform for AI agents. It sits between your business logic and AI agent execution, enforcing policies, tracking budgets, managing human approval workflows, compressing context efficiently, and providing full audit trails.

**The Problem**: AI agents in production face 5 critical gaps:
1. **Cost Explosion** — POC → Production cost jumps 1000x ($500/mo → $847K/mo)
2. **Observability without Control** — 89% have monitoring but 32% still have quality issues
3. **Safety Gaps** — Agents executing unguarded writes, network calls, file access
4. **Human Trust Gap**— No structured approval workflows for critical decisions
5. **Context Bloat**— Unlimited context windows wasting 60-95% of tokens

**AegisFlow's Solution**: A unified runtime layer with:
- **Policy Engine**: Declarative rules engine (Allow / Deny / Human Loop) with regex matching
- **Budget Guardian**: Daily/monthly/per-request token caps with throttle control
- **Human-in-the-Loop Gateway**: Structured approval workflows with auto-escalation
- **Context Compressor**: Intelligent content routing + cache alignment inspired by Headroom
- **Sandbox Executor**: Virtual FS + process isolation inspired by Mirage
- **Audit Trail**: Immutable, encrypted audit logging with full query API

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 20+ (for frontend)

### Backend

```bash
cd backend

# Install
pip install -e .

# Run
python -m aegisflow.main --config config.yaml

# Test
pytest tests/ -v
```

API available at `http://localhost:8000`  
API docs at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend

# Install
npm install

# Run
npm start
```

Dashboard at `http://localhost:3000`

### Docker

```bash
docker-compose up -d
```

## Architecture

```
                    ┌─────────────────────────────────┐
                    │        AegisFlow Gateway         │
                    └───────────┬─────────────────────┘
                                │
           ┌────────────────────┼────────────────────┐
           ▼                    ▼                     ▼
   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
   │ Policy Engine │   │ Budget Guard  │   │ Audit Trail   │
   │ (Allow/Deny/  │   │ (Token Cap/   │   │ (Immutable    │
   │  Human-Loop)  │   │  Throttle)    │   │  Encrypted)   │
   └───────────────┘   └───────────────┘   └───────────────┘
           │                    │                    │
           └────────────────────┼────────────────────┘
                                │
           ┌────────────────────┼────────────────────┐
           ▼                    ▼                     ▼
   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
   │Context Compress│   │Sandbox Exec   │   │Human-in-Loop  │
   │(Content Route+ │   │(Virtual FS+   │   │(Approval Queue│
   │ Cache Align)   │   │ Process Iso)  │   │ Auto-Escalate)│
   └───────────────┘   └───────────────┘   └───────────────┘
```

## 7-Step Execution Pipeline

```
Agent Request
    │
    ▼
[1] Policy Check ─── deny? → Reject with reason
    │ allowed
    ▼
[2] Budget Check ─── exceeded? → Reject quota
    │ approved
    ▼
[3] Context Compression ─── optimize payload
    │
    ▼
[4] Human Approval Gateway ─── deny/timeout → Reject
    │ approved
    ▼
[5] Sandbox Execute ─── error? → Record & reject
    │ success
    ▼
[6] Budget Deduction ─── deduct tokens
    │
    ▼
[7] Audit Record ─── immutable log
```

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/api/v1/execute` | POST | Execute agent action |
| `/api/v1/stats/{agent_id}` | GET | Budget stats |
| `/api/v1/audit/{agent_id}` | GET | Audit records |
| `/api/v1/policies` | GET | List policies |
| `/api/v1/approvals` | GET | Pending approvals |
| `/api/v1/approvals/{id}/approve` | POST | Approve request |
| `/api/v1/approvals/{id}/deny` | POST | Deny request |
| `/api/v1/config` | GET | Current config |
| `/ws/{client_id}` | WebSocket | Real-time agent execution |

## Policy Configuration

```yaml
rules:
  - name: "allow_safe_api"
    resource: "api_call"
    action: "allow"
    conditions:
      method: "^(GET|HEAD|OPTIONS)$"
    priority: 10

  - name: "human_loop_write"
    resource: "api_call"
    action: "human_loop"
    conditions:
      method: "^(POST|PUT|PATCH|DELETE)$"
    priority: 20
```

## Project Structure

```
aegisflow/
├── backend/
│   ├── src/aegisflow/
│   │   ├── core/          # Orchestrator, Config, Context
│   │   ├── policy/        # Policy Engine, Rule Matching
│   │   ├── budget/        # Budget Guard, Token Counter
│   │   ├── compress/      # Context Compressor
│   │   ├── sandbox/       # Sandbox Executor
│   │   ├── audit/         # Audit Trail
│   │   ├── human_loop/    # Human-in-the-Loop
│   │   └── api/           # FastAPI Server, WebSocket
│   ├── tests/             # pytest test suite
│   ├── config.yaml        # Default policy config
│   └── pyproject.toml
├── frontend/
│   ├── src/               # React components
│   └── public/
├── docs/                  # Documentation
├── examples/              # Usage examples
├── docker-compose.yml
├── .gitignore
├── LICENSE
└── README.md
```

## Why AegisFlow?

| Feature | Without AegisFlow | With AegisFlow |
|---|---|---|
| Policy Enforcement | Manual code review | Declarative rules, auto-enforced |
| Budget Control | No limits, surprise bills | Token caps, throttle, alerts |
| Audit Trail | Scattered logs | Immutable encrypted trail |
| Human Approval | Ad-hoc Slack messages | Structured workflow with auto-escalation |
| Context Management | Unlimited, wasteful | Intelligent compression 60-95% savings |
| Sandbox Isolation | Direct system access | Virtual FS + process isolation |

## Inspired By

- **Headroom** — Token compression and context optimization
- **Mirage** — Sandbox execution and process isolation
- **Microsoft AI Agent Governance Toolkit** — Enterprise policy framework
- **Bifrost** — Low-latency guardrail gateway
- **MemPalace** — Tiered memory architecture for agents

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License — see [LICENSE](LICENSE) for details. Free for personal and commercial use.

---

<p align="center">
  Built with ♥ for the agent-native enterprise
</p>
