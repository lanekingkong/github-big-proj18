# AegisFlow Examples

## Example 1: Basic Agent Execution

```python
import asyncio
from aegisflow.core.config import AegisConfig,PolicyConfig,BudgetConfig,SandboxConfig,CompressConfig,AuditConfig,HumanLoopConfig
from aegisflow.core.orchestrator import Orchestrator,AgentRequest

async def main():
    config=AegisConfig(
        policy=PolicyConfig(path="config.yaml"),
        budget=BudgetConfig(daily_limit=1000000),
        sandbox=SandboxConfig(enabled=True),
        compress=CompressConfig(enabled=True),
        audit=AuditConfig(enabled=True,encrypt=False),
        human_loop=HumanLoopConfig(enabled=False)
    )

    orchestrator=Orchestrator(config)

    # Safe API call — should pass policy check
    request=AgentRequest(
        agent_id="my_agent",
        action="api_call",
        payload={"method":"GET","url":"/api/data"}
    )
    result=await orchestrator.execute(request)
    print(f"Result: {result}")

    # Budget stats
    stats=await orchestrator.budget_guard.get_stats("my_agent")
    print(f"Budget stats: {stats}")

    # Audit trail
    audit=await orchestrator.audit_trail.query("my_agent",limit=5)
    print(f"Audit records: {len(audit)}")

    await orchestrator.shutdown()

asyncio.run(main())
```

## Example 2: Custom Policy Rules

```python
from aegisflow.policy.engine import PolicyEngine,PolicyRule,PolicySet,RuleAction,ResourceType

# Create a custom policy set
custom_policy=PolicySet(
    name="my_custom_policy",
    rules=[
        PolicyRule(
            name="allow_internal_apis",
            description="Allow calls to internal APIs",
            resource=ResourceType.API_CALL,
            action=RuleAction.ALLOW,
            conditions={"url":"^https://internal\\.mycompany\\.com/.*"},
            risk_level="low",
            priority=10
        ),
        PolicyRule(
            name="deny_external_apis",
            description="Deny all external API calls",
            resource=ResourceType.API_CALL,
            action=RuleAction.DENY,
            conditions={},
            risk_level="medium",
            priority=5
        ),
        PolicyRule(
            name="human_review_deletes",
            description="Require human approval for delete operations",
            resource=ResourceType.DATABASE,
            action=RuleAction.HUMAN_LOOP,
            conditions={"operation":"^(DELETE|DROP)$"},
            risk_level="high",
            priority=80
        )
    ],
    default_action=RuleAction.DENY
)

engine=PolicyEngine(config)
engine.policy_set=custom_policy
```

## Example 3: Docker Deployment

```bash
# Start AegisFlow with Docker
docker-compose up -d

# Check health
curl http://localhost:8000/health

# Execute an agent action
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"test","action":"api_call","payload":{"method":"GET","url":"/api/test"}}'

# View stats
curl http://localhost:8000/api/v1/stats/test

# List policies
curl http://localhost:8000/api/v1/policies
```
