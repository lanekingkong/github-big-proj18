import uuid
import asyncio
import logging
from typing import Dict,Any,Optional
from dataclasses import dataclass,field
from enum import Enum
from collections import defaultdict

from ..core.context import ExecutionContext

logger=logging.getLogger(__name__)

class ApprovalStatus(Enum):
    PENDING="pending"
    APPROVED="approved"
    DENIED="denied"
    TIMEOUT="timeout"
    AUTO_ESCALATED="auto_escalated"

@dataclass
class ApprovalRequest:
    id:str=field(default_factory=lambda:f"approval_{uuid.uuid4().hex[:8]}")
    agent_id:str=""
    action:str=""
    reason:str=""
    risk_level:str=""
    payload_summary:str=""
    status:ApprovalStatus=ApprovalStatus.PENDING
    created_at:float=field(default_factory=asyncio.get_event_loop().time if asyncio.get_event_loop() else __import__('time').time)

class ApprovalQueue:
    def __init__(self):
        self.queue:Dict[str,ApprovalRequest]={}
        self.callbacks:Dict[str,asyncio.Event]={}
        self.results:Dict[str,ApprovalStatus]={}

    def enqueue(self,request:ApprovalRequest,event:asyncio.Event):
        self.queue[request.id]=request
        self.callbacks[request.id]=event

    def dequeue(self,request_id:str)->Optional[ApprovalRequest]:
        return self.queue.pop(request_id,None)

    def set_result(self,request_id:str,status:ApprovalStatus):
        self.results[request_id]=status
        if request_id in self.callbacks:
            self.callbacks[request_id].set()

    async def wait_result(self,request_id:str,timeout:int=300)->ApprovalStatus:
        if request_id in self.results:
            return self.results.pop(request_id)
        event=asyncio.Event()
        self.callbacks[request_id]=event
        try:
            await asyncio.wait_for(event.wait(),timeout=timeout)
            return self.results.pop(request_id,ApprovalStatus.TIMEOUT)
        except asyncio.TimeoutError:
            self.dequeue(request_id)
            return ApprovalStatus.TIMEOUT

class HumanLoopGateway:
    def __init__(self,config):
        self.config=config
        self.queue=ApprovalQueue()
        self._approval_history:list[ApprovalRequest]=[]

    async def request_approval(self,ctx:ExecutionContext)->Dict[str,Any]:
        if not self.config.enabled:
            return {"approved":True,"reason":"human_loop_disabled"}

        approval=ApprovalRequest(
            agent_id=ctx.agent_id,
            action=ctx.action,
            reason=f"Risk level: {ctx.policy_result.get('risk_level','unknown')}",
            risk_level=ctx.policy_result.get('risk_level','low'),
            payload_summary=str(ctx.payload)[:200]
        )

        result_event=asyncio.Event()
        self.queue.enqueue(approval,result_event)
        logger.info(f"Human approval requested:{approval.id} for {ctx.agent_id}")

        status=await self.queue.wait_result(approval.id,self.config.approval_timeout_sec)
        approval.status=status
        self._approval_history.append(approval)

        if status==ApprovalStatus.TIMEOUT and self.config.auto_escalate:
            logger.warning(f"Auto-escalating approval:{approval.id}")
            status=ApprovalStatus.AUTO_ESCALATED

        return {
            "approved":status in [ApprovalStatus.APPROVED,ApprovalStatus.AUTO_ESCALATED],
            "reason":status.value,
            "approval_id":approval.id
        }

    async def approve(self,request_id:str):
        self.queue.set_result(request_id,ApprovalStatus.APPROVED)

    async def deny(self,request_id:str,reason:str=""):
        self.queue.set_result(request_id,ApprovalStatus.DENIED)

    async def get_pending(self)->list[ApprovalRequest]:
        return [r for r in self.queue.queue.values() if r.status==ApprovalStatus.PENDING]

    async def close(self):
        pass
