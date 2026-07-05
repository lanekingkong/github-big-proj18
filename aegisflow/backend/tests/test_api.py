import pytest
from httpx import AsyncClient,ASGITransport
from aegisflow.core.config import AegisConfig,PolicyConfig,BudgetConfig,SandboxConfig,CompressConfig,AuditConfig,HumanLoopConfig
from aegisflow.api.server import create_app

@pytest.fixture
def app():
    config=AegisConfig(
        policy=PolicyConfig(path="nonexistent.json"),
        budget=BudgetConfig(daily_limit=1000000,monthly_limit=30000000),
        sandbox=SandboxConfig(enabled=True),
        compress=CompressConfig(enabled=True),
        audit=AuditConfig(enabled=True,encrypt=False),
        human_loop=HumanLoopConfig(enabled=False)
    )
    return create_app(config)

@pytest.mark.asyncio
async def test_health_endpoint(app):
    transport=ASGITransport(app=app)
    async with AsyncClient(transport=transport,base_url="http://test") as client:
        response=await client.get("/health")
        assert response.status_code==200
        assert response.json()["status"]=="ok"

@pytest.mark.asyncio
async def test_execute_endpoint(app):
    transport=ASGITransport(app=app)
    async with AsyncClient(transport=transport,base_url="http://test") as client:
        response=await client.post("/api/v1/execute",json={
            "agent_id":"test_agent",
            "action":"api_call",
            "payload":{"method":"GET","url":"/api/test"}
        })
        assert response.status_code==200
        data=response.json()
        assert "success" in data or "error" in data

@pytest.mark.asyncio
async def test_stats_endpoint(app):
    transport=ASGITransport(app=app)
    async with AsyncClient(transport=transport,base_url="http://test") as client:
        response=await client.get("/api/v1/stats/test_agent")
        assert response.status_code==200
        data=response.json()
        assert "daily_used" in data
        assert "daily_limit" in data

@pytest.mark.asyncio
async def test_audit_endpoint(app):
    transport=ASGITransport(app=app)
    async with AsyncClient(transport=transport,base_url="http://test") as client:
        response=await client.get("/api/v1/audit/test_agent?limit=10")
        assert response.status_code==200
        assert isinstance(response.json(),list)

@pytest.mark.asyncio
async def test_policies_endpoint(app):
    transport=ASGITransport(app=app)
    async with AsyncClient(transport=transport,base_url="http://test") as client:
        response=await client.get("/api/v1/policies")
        assert response.status_code==200
        data=response.json()
        assert "rules" in data
        assert len(data["rules"])>0

@pytest.mark.asyncio
async def test_config_endpoint(app):
    transport=ASGITransport(app=app)
    async with AsyncClient(transport=transport,base_url="http://test") as client:
        response=await client.get("/api/v1/config")
        assert response.status_code==200
        data=response.json()
        assert "budget" in data

@pytest.mark.asyncio
async def test_approvals_endpoint(app):
    transport=ASGITransport(app=app)
    async with AsyncClient(transport=transport,base_url="http://test") as client:
        response=await client.get("/api/v1/approvals")
        assert response.status_code==200
        assert isinstance(response.json(),list)
