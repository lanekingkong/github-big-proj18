import asyncio
import logging
from typing import Dict,Any,Optional
from dataclasses import dataclass
from enum import Enum

from .config import AegisConfig
from .context import ExecutionContext
from ..policy.engine import PolicyEngine
from ..budget.guard import BudgetGuard
from ..sandbox.executor import SandboxExecutor
from ..compress.compressor import ContentCompressor
from ..audit.trail import AuditTrail
from ..human_loop.gateway import HumanLoopGateway

logger=logging.getLogger(__name__)

class AgentRequest:
    def __init__(self,agent_id:str,action:str,payload:Dict[str,Any],session_id:Optional[str]=None):
        self.agent_id=agent_id
        self.action=action
        self.payload=payload
        self.session_id=session_id or f"sess_{agent_id}_{int(asyncio.get_event_loop().time())}"

class Orchestrator:
    def __init__(self,config:AegisConfig):
        self.config=config
        self.policy_engine=PolicyEngine(config.policy_path)
        self.budget_guard=BudgetGuard(config.budget_config)
        self.sandbox=SandboxExecutor(config.sandbox_config)
        self.compressor=ContentCompressor(config.compress_config)
        self.audit_trail=AuditTrail(config.audit_config)
        self.human_gateway=HumanLoopGateway(config.human_loop_config)
        self.active_sessions:Dict[str,ExecutionContext]={}

    async def execute(self,request:AgentRequest)->Dict[str,Any]:
        ctx=ExecutionContext(
            request_id=request.session_id,
            agent_id=request.agent_id,
            action=request.action,
            payload=request.payload
        )
        self.active_sessions[request.session_id]=ctx

        try:
            #1 策略检查
            policy_result=await self.policy_engine.evaluate(ctx)
            if not policy_result.allowed:
                await self.audit_trail.record_policy_denial(ctx,policy_result.reason)
                return {"error":"policy_denied","reason":policy_result.reason}

            #2 预算检查
            budget_check=await self.budget_guard.check(ctx)
            if not budget_check.approved:
                await self.audit_trail.record_budget_exceeded(ctx,budget_check.remaining)
                return {"error":"budget_exceeded","remaining":budget_check.remaining}

            #3 压缩上下文
            compressed_ctx=await self.compressor.compress(ctx)
            ctx.compressed_payload=compressed_ctx

            #4 高风险操作转人工
            if policy_result.risk_level=="high":
                approval=await self.human_gateway.request_approval(ctx)
                if not approval.approved:
                    await self.audit_trail.record_human_denial(ctx,approval.reason)
                    return {"error":"human_denied","reason":approval.reason}

            #5 沙箱执行
            sandbox_result=await self.sandbox.execute(ctx)
            ctx.execution_result=sandbox_result

            #6 扣减预算
            await self.budget_guard.consume(ctx,sandbox_result.token_cost)

            #7 审计记录
            await self.audit_trail.record_success(ctx)

            return {
                "success":True,
                "result":sandbox_result.output,
                "token_cost":sandbox_result.token_cost,
                "execution_time":sandbox_result.execution_time,
                "session_id":request.session_id
            }

        except Exception as e:
            logger.error(f"Orchestration failed for {request.agent_id}:{e}")
            await self.audit_trail.record_error(ctx,str(e))
            return {"error":"execution_failed","reason":str(e)}
        finally:
            self.active_sessions.pop(request.session_id,None)

    async def shutdown(self):
        await self.policy_engine.close()
        await self.budget_guard.close()
        await self.sandbox.cleanup()
        await self.compressor.close()
        await self.audit_trail.close()
        await self.human_gateway.close()
