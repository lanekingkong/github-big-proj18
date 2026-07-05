import pytest
import asyncio
import json
import tempfile
import os
from pathlib import Path

from aegisflow.core.config import AegisConfig,PolicyConfig,BudgetConfig,SandboxConfig,CompressConfig,AuditConfig,HumanLoopConfig
from aegisflow.core.context import ExecutionContext
from aegisflow.core.orchestrator import Orchestrator,AgentRequest
from aegisflow.policy.engine import PolicyEngine,PolicyRule,PolicySet,RuleAction,ResourceType
from aegisflow.budget.guard import BudgetGuard,TokenCounter,ThrottleController
from aegisflow.compress.compressor import ContentCompressor,ContentRouter,CacheAligner,CCRManager
from aegisflow.sandbox.executor import SandboxExecutor,VirtualFS,ProcessIsolator
from aegisflow.audit.trail import AuditTrail,AuditRecord,AuditStorage
from aegisflow.human_loop.gateway import HumanLoopGateway,ApprovalRequest,ApprovalStatus,ApprovalQueue

# ============================================================
# Policy Engine Tests
# ============================================================

class TestPolicyEngine:
    def test_rule_matching(self):
        rule=PolicyRule(
            name="test_rule",
            description="Test",
            resource=ResourceType.API_CALL,
            action=RuleAction.ALLOW,
            conditions={"method":"^GET$"},
            risk_level="low",
            priority=10
        )
        ctx=ExecutionContext(
            request_id="test_001",
            agent_id="agent1",
            action="api_call",
            payload={"method":"GET","url":"/api/test"}
        )
        assert rule.matches(ctx)==True

        ctx2=ExecutionContext(
            request_id="test_002",
            agent_id="agent1",
            action="api_call",
            payload={"method":"POST","url":"/api/test"}
        )
        assert rule.matches(ctx2)==False

    def test_policy_set_evaluate_allow(self):
        ps=PolicySet(
            name="test",
            rules=[
                PolicyRule(
                    name="allow_get",
                    description="Allow GET",
                    resource=ResourceType.API_CALL,
                    action=RuleAction.ALLOW,
                    conditions={"method":"^GET$"},
                    priority=10
                )
            ],
            default_action=RuleAction.DENY
        )
        ctx=ExecutionContext(
            request_id="test_003",
            agent_id="agent1",
            action="api_call",
            payload={"method":"GET"}
        )
        result=ps.evaluate(ctx)
        assert result["allowed"]==True
        assert result["action"]=="allow"

    def test_policy_set_evaluate_deny(self):
        ps=PolicySet(
            name="test",
            rules=[
                PolicyRule(
                    name="deny_post",
                    description="Deny POST",
                    resource=ResourceType.API_CALL,
                    action=RuleAction.DENY,
                    conditions={"method":"^POST$"},
                    priority=20
                )
            ],
            default_action=RuleAction.ALLOW
        )
        ctx=ExecutionContext(
            request_id="test_004",
            agent_id="agent1",
            action="api_call",
            payload={"method":"POST"}
        )
        result=ps.evaluate(ctx)
        assert result["allowed"]==False
        assert result["action"]=="deny"

    def test_policy_priority(self):
        ps=PolicySet(
            name="test",
            rules=[
                PolicyRule(
                    name="low_priority",
                    description="Low",
                    resource=ResourceType.API_CALL,
                    action=RuleAction.ALLOW,
                    conditions={},
                    priority=5
                ),
                PolicyRule(
                    name="high_priority",
                    description="High",
                    resource=ResourceType.API_CALL,
                    action=RuleAction.DENY,
                    conditions={},
                    priority=50
                )
            ],
            default_action=RuleAction.ALLOW
        )
        ctx=ExecutionContext(
            request_id="test_005",
            agent_id="agent1",
            action="api_call",
            payload={}
        )
        result=ps.evaluate(ctx)
        assert result["action"]=="deny"

    def test_human_loop_rule(self):
        ps=PolicySet(
            name="test",
            rules=[
                PolicyRule(
                    name="human_review",
                    description="Need human",
                    resource=ResourceType.DATABASE,
                    action=RuleAction.HUMAN_LOOP,
                    conditions={},
                    risk_level="high",
                    priority=80
                )
            ],
            default_action=RuleAction.ALLOW
        )
        ctx=ExecutionContext(
            request_id="test_006",
            agent_id="agent1",
            action="database",
            payload={"operation":"INSERT"}
        )
        result=ps.evaluate(ctx)
        assert result["action"]=="human_loop"
        assert result["risk_level"]=="high"

# ============================================================
# Budget Guard Tests
# ============================================================

class TestBudgetGuard:
    @pytest.mark.asyncio
    async def test_budget_check_approved(self):
        config=BudgetConfig(daily_limit=1000000,monthly_limit=30000000,per_request_limit=10000)
        guard=BudgetGuard(config)
        ctx=ExecutionContext(
            request_id="budget_001",
            agent_id="agent1",
            action="llm_call",
            payload={"prompt":"hello"}
        )
        result=await guard.check(ctx)
        assert result.approved==True
        assert result.remaining>0

    @pytest.mark.asyncio
    async def test_budget_consume(self):
        config=BudgetConfig(daily_limit=1000000,monthly_limit=30000000)
        guard=BudgetGuard(config)
        ctx=ExecutionContext(
            request_id="budget_002",
            agent_id="agent2",
            action="llm_call",
            payload={}
        )
        await guard.consume(ctx,5000)
        stats=await guard.get_stats("agent2")
        assert stats["daily_used"]==5000

    @pytest.mark.asyncio
    async def test_budget_exceeded_daily(self):
        config=BudgetConfig(daily_limit=100,monthly_limit=30000000)
        guard=BudgetGuard(config)
        ctx=ExecutionContext(
            request_id="budget_003",
            agent_id="agent3",
            action="llm_call",
            payload={}
        )
        await guard.consume(ctx,100)
        result=await guard.check(ctx)
        assert result.approved==False
        assert result.reason=="daily_limit_exceeded"

    def test_token_counter_reset(self):
        counter=TokenCounter()
        counter.add("agent1",100)
        assert counter.get_daily("agent1")==100
        counter._check_reset()
        assert counter.get_daily("agent1")==100

    def test_throttle_controller(self):
        tc=ThrottleController(max_requests_per_sec=3)
        assert tc.can_proceed()==True
        assert tc.can_proceed()==True
        assert tc.can_proceed()==True
        assert tc.can_proceed()==False

# ============================================================
# Compressor Tests
# ============================================================

class TestCompressor:
    def test_content_router_detect_json(self):
        router=ContentRouter()
        assert router._detect_type('{"key":"value"}')=="json"
        assert router._detect_type('[1,2,3]')=="json"

    def test_content_router_detect_code(self):
        router=ContentRouter()
        assert router._detect_type("def foo():\n    pass")=="code"
        assert router._detect_type("import os\nconst x=1")=="code"

    def test_content_router_detect_log(self):
        router=ContentRouter()
        assert router._detect_type("2024-01-01 12:00:00 INFO test")=="log"

    def test_json_compression(self):
        router=ContentRouter()
        original='{"key1":"value1","key2":"","key3":null,"key4":"value4"}'
        compressed=router._compress_json(original)
        assert len(compressed)<len(original)
        assert "key1" in compressed
        assert "key2" not in compressed

    def test_code_compression(self):
        router=ContentRouter()
        original="# comment\ndef foo():\n    # inner comment\n    return 42\n"
        compressed=router._compress_code(original)
        assert "# comment" not in compressed
        assert "def foo()" in compressed

    def test_cache_aligner(self):
        ca=CacheAligner()
        result1=ca.align("hello world this is a test","key1")
        assert result1=="hello world this is a test"
        result2=ca.align("hello world this is a test and more","key1")
        assert result2==" and more"

    def test_ccr_manager(self):
        ccr=CCRManager()
        ccr.store("key1","original content")
        assert ccr.retrieve("key1")=="original content"
        assert ccr.retrieve("nonexistent") is None

    @pytest.mark.asyncio
    async def test_content_compressor(self):
        config=CompressConfig(enabled=True,compression_ratio=0.7)
        compressor=ContentCompressor(config)
        ctx=ExecutionContext(
            request_id="comp_001",
            agent_id="agent1",
            action="llm_call",
            payload={
                "prompt":"hello world",
                "json_data":'{"a":"b","c":"","d":null,"e":"f"}',
                "code":"# comment\ndef foo():\n    return 1"
            }
        )
        result=await compressor.compress(ctx)
        assert "prompt" in result
        assert "json_data" in result
        assert "code" in result

# ============================================================
# Sandbox Tests
# ============================================================

class TestSandbox:
    def test_virtual_fs_allowed(self):
        vfs=VirtualFS(root_dir="/tmp/aegis_test",allowed_dirs=["/tmp/aegis_test"])
        assert vfs.is_allowed("/tmp/aegis_test/file.txt")==True

    def test_virtual_fs_denied(self):
        vfs=VirtualFS(root_dir="/tmp/aegis_test",denied_dirs=["/etc","/sys"])
        assert vfs.is_allowed("/etc/passwd")==False
        assert vfs.is_allowed("/sys/kernel")==False

    def test_process_isolator(self):
        isolator=ProcessIsolator(max_processes=5,max_memory_mb=256)
        assert isolator.can_spawn()==True
        assert isolator.estimate_memory({"data":"x"*1000})<1

# ============================================================
# Audit Trail Tests
# ============================================================

class TestAuditTrail:
    def test_audit_storage_insert(self):
        storage=AuditStorage(db_path=":memory:",encrypt=False)
        record=AuditRecord(
            id="audit_001",
            agent_id="agent1",
            action="api_call",
            result="success",
            token_cost=100
        )
        storage.insert(record)
        results=storage.query(agent_id="agent1")
        assert len(results)==1
        assert results[0]["result"]=="success"

    def test_audit_storage_encrypt(self):
        storage=AuditStorage(db_path=":memory:",encrypt=True)
        record=AuditRecord(
            id="audit_002",
            agent_id="agent2",
            action="file_access",
            result="denied",
            reason="policy"
        )
        storage.insert(record)
        results=storage.query(agent_id="agent2")
        assert len(results)==1
        assert results[0]["result"]=="denied"

# ============================================================
# Human Loop Tests
# ============================================================

class TestHumanLoop:
    @pytest.mark.asyncio
    async def test_approval_queue(self):
        queue=ApprovalQueue()
        request=ApprovalRequest(
            agent_id="agent1",
            action="api_call",
            reason="test",
            risk_level="high"
        )
        event=asyncio.Event()
        queue.enqueue(request,event)
        assert len(queue.queue)==1

        queue.set_result(request.id,ApprovalStatus.APPROVED)
        result=await queue.wait_result(request.id,timeout=1)
        assert result==ApprovalStatus.APPROVED

    @pytest.mark.asyncio
    async def test_approval_timeout(self):
        queue=ApprovalQueue()
        request=ApprovalRequest(
            agent_id="agent1",
            action="test",
            reason="timeout test",
            risk_level="low"
        )
        event=asyncio.Event()
        queue.enqueue(request,event)
        result=await queue.wait_result(request.id,timeout=0.1)
        assert result==ApprovalStatus.TIMEOUT

# ============================================================
# Orchestrator Integration Tests
# ============================================================

class TestOrchestrator:
    @pytest.mark.asyncio
    async def test_orchestrator_execute_safe_action(self):
        config=AegisConfig(
            policy=PolicyConfig(path="nonexistent.json"),
            budget=BudgetConfig(daily_limit=1000000,monthly_limit=30000000),
            sandbox=SandboxConfig(enabled=True),
            compress=CompressConfig(enabled=True),
            audit=AuditConfig(enabled=True,encrypt=False),
            human_loop=HumanLoopConfig(enabled=False)
        )
        orchestrator=Orchestrator(config)
        request=AgentRequest(
            agent_id="test_agent",
            action="api_call",
            payload={"method":"GET","url":"/api/health"}
        )
        result=await orchestrator.execute(request)
        assert "success" in result or "error" in result
        await orchestrator.shutdown()

    @pytest.mark.asyncio
    async def test_orchestrator_policy_deny(self):
        config=AegisConfig(
            policy=PolicyConfig(path="nonexistent.json"),
            budget=BudgetConfig(daily_limit=1000000),
            sandbox=SandboxConfig(enabled=True),
            compress=CompressConfig(enabled=False),
            audit=AuditConfig(enabled=True,encrypt=False),
            human_loop=HumanLoopConfig(enabled=False)
        )
        orchestrator=Orchestrator(config)
        request=AgentRequest(
            agent_id="test_agent",
            action="file_access",
            payload={"path":"C:\\Windows\\System32\\config","operation":"read"}
        )
        result=await orchestrator.execute(request)
        assert result.get("error")=="policy_denied"
        await orchestrator.shutdown()

# ============================================================
# Config Tests
# ============================================================

class TestConfig:
    def test_config_defaults(self):
        config=AegisConfig(
            policy=PolicyConfig(path="test.json"),
            budget=BudgetConfig(),
            sandbox=SandboxConfig(),
            compress=CompressConfig(),
            audit=AuditConfig(),
            human_loop=HumanLoopConfig()
        )
        assert config.budget.daily_limit==1000000
        assert config.sandbox.isolation_level=="moderate"
        assert config.compress.compression_ratio==0.7

    def test_config_to_dict(self):
        config=AegisConfig(
            policy=PolicyConfig(path="test.json"),
            budget=BudgetConfig(),
            sandbox=SandboxConfig(),
            compress=CompressConfig(),
            audit=AuditConfig(),
            human_loop=HumanLoopConfig()
        )
        d=config.to_dict()
        assert "policy" in d
        assert "budget" in d
        assert d["budget"]["daily_limit"]==1000000
