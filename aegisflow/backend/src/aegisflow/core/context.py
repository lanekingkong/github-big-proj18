from dataclasses import dataclass,field
from typing import Dict,Any,Optional
import uuid
import time

@dataclass
class ExecutionContext:
    request_id:str
    agent_id:str
    action:str
    payload:Dict[str,Any]
    compressed_payload:Optional[Dict[str,Any]]=None
    execution_result:Optional[Dict[str,Any]]=None
    policy_result:Optional[Dict[str,Any]]=None
    budget_result:Optional[Dict[str,Any]]=None
    human_approval:Optional[Dict[str,Any]]=None
    start_time:float=field(default_factory=time.time)
    end_time:Optional[float]=None
    metadata:Dict[str,Any]=field(default_factory=dict)

    def __post_init__(self):
        if not self.request_id:
            self.request_id=f"req_{uuid.uuid4().hex[:8]}"
        self.metadata.setdefault('created_at',time.time())
        self.metadata.setdefault('version','1.0')

    def mark_complete(self,result:Dict[str,Any]=None):
        self.end_time=time.time()
        if result:
            self.execution_result=result

    @property
    def duration(self)->float:
        if self.end_time:
            return self.end_time-self.start_time
        return time.time()-self.start_time

    @property
    def is_complete(self)->bool:
        return self.end_time is not None

    def to_audit_dict(self)->Dict[str,Any]:
        return {
            'request_id':self.request_id,
            'agent_id':self.agent_id,
            'action':self.action,
            'payload_summary':str(self.payload)[:500],
            'compressed':self.compressed_payload is not None,
            'policy_result':self.policy_result,
            'budget_result':self.budget_result,
            'human_approval':self.human_approval,
            'execution_result':self.execution_result,
            'start_time':self.start_time,
            'end_time':self.end_time,
            'duration':self.duration,
            'metadata':self.metadata
        }
