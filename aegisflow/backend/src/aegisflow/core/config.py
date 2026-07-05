from dataclasses import dataclass
from typing import Optional,Dict,Any
import yaml
import os

@dataclass
class PolicyConfig:
    path:str
    auto_reload:bool=True
    default_action:str="deny"

@dataclass
class BudgetConfig:
    daily_limit:int=1000000
    monthly_limit:int=30000000
    per_request_limit:int=10000
    currency:str="USD"
    cost_per_token:float=0.000001

@dataclass
class SandboxConfig:
    enabled:bool=True
    isolation_level:str="moderate"
    allowed_dirs:list[str]=None
    denied_dirs:list[str]=None
    max_processes:int=10
    max_memory_mb:int=512

@dataclass
class CompressConfig:
    enabled:bool=True
    compression_ratio:float=0.7
    min_token_save:int=100
    algorithms:list[str]=None

@dataclass
class AuditConfig:
    enabled:bool=True
    storage_backend:str="sqlite"
    retention_days:int=90
    encrypt:bool=True

@dataclass
class HumanLoopConfig:
    enabled:bool=True
    approval_timeout_sec:int=300
    notification_channels:list[str]=None
    auto_escalate:bool=True

@dataclass
class AegisConfig:
    policy:PolicyConfig
    budget:BudgetConfig
    sandbox:SandboxConfig
    compress:CompressConfig
    audit:AuditConfig
    human_loop:HumanLoopConfig
    log_level:str="INFO"
    api_host:str="0.0.0.0"
    api_port:int=8000

    @property
    def policy_path(self)->str:
        return self.policy.path

    @property
    def budget_config(self)->BudgetConfig:
        return self.budget

    @property
    def sandbox_config(self)->SandboxConfig:
        return self.sandbox

    @property
    def compress_config(self)->CompressConfig:
        return self.compress

    @property
    def audit_config(self)->AuditConfig:
        return self.audit

    @property
    def human_loop_config(self)->HumanLoopConfig:
        return self.human_loop

    @classmethod
    def from_yaml(cls,path:str)->"AegisConfig":
        with open(path,'r',encoding='utf-8') as f:
            data=yaml.safe_load(f)

        return cls(
            policy=PolicyConfig(**data.get('policy',{})),
            budget=BudgetConfig(**data.get('budget',{})),
            sandbox=SandboxConfig(**data.get('sandbox',{})),
            compress=CompressConfig(**data.get('compress',{})),
            audit=AuditConfig(**data.get('audit',{})),
            human_loop=HumanLoopConfig(**data.get('human_loop',{})),
            log_level=data.get('log_level','INFO'),
            api_host=data.get('api_host','0.0.0.0'),
            api_port=data.get('api_port',8000)
        )

    def to_dict(self)->Dict[str,Any]:
        return {
            'policy':self.policy.__dict__,
            'budget':self.budget.__dict__,
            'sandbox':self.sandbox.__dict__,
            'compress':self.compress.__dict__,
            'audit':self.audit.__dict__,
            'human_loop':self.human_loop.__dict__,
            'log_level':self.log_level,
            'api_host':self.api_host,
            'api_port':self.api_port
        }
