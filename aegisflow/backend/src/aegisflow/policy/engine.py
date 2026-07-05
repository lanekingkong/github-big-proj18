import re
import json
import logging
from typing import Dict,Any,List,Optional
from dataclasses import dataclass,field
from enum import Enum

from ..core.context import ExecutionContext

logger=logging.getLogger(__name__)

class RuleAction(Enum):
    ALLOW="allow"
    DENY="deny"
    HUMAN_LOOP="human_loop"
    LOG_ONLY="log_only"

class ResourceType(Enum):
    API_CALL="api_call"
    FILE_ACCESS="file_access"
    NETWORK="network"
    PROCESS="process"
    DATABASE="database"
    LLM_CALL="llm_call"
    TOOL_INVOCATION="tool_invocation"

@dataclass
class PolicyRule:
    name:str
    description:str
    resource:ResourceType
    action:RuleAction
    conditions:Dict[str,Any]=field(default_factory=dict)
    risk_level:str="low"
    priority:int=0
    enabled:bool=True

    def matches(self,ctx:ExecutionContext)->bool:
        if not self.enabled:
            return False
        if self.resource.value!=ctx.action:
            return False
        for key,pattern in self.conditions.items():
            value=ctx.payload.get(key,"")
            if isinstance(pattern,str) and not re.match(pattern,str(value)):
                return False
            elif isinstance(pattern,dict):
                if not self._match_dict(pattern,value):
                    return False
        return True

    def _match_dict(self,pattern:Dict,value:Any)->bool:
        if isinstance(value,dict):
            for k,v in pattern.items():
                if k not in value or value[k]!=v:
                    return False
            return True
        return False

@dataclass
class PolicySet:
    name:str
    rules:List[PolicyRule]=field(default_factory=list)
    default_action:RuleAction=RuleAction.DENY

    def evaluate(self,ctx:ExecutionContext)->Dict[str,Any]:
        matched_rules=[]
        for rule in sorted(self.rules,key=lambda r:r.priority,reverse=True):
            if rule.matches(ctx):
                matched_rules.append(rule)

        if not matched_rules:
            return {
                "allowed":self.default_action==RuleAction.ALLOW,
                "action":self.default_action.value,
                "matched_rules":[],
                "risk_level":"low",
                "reason":"default_policy"
            }

        highest_risk=max(matched_rules,key=lambda r:{"low":0,"medium":1,"high":2,"critical":3}.get(r.risk_level,0))
        final_action=highest_risk.action

        return {
            "allowed":final_action in [RuleAction.ALLOW,RuleAction.LOG_ONLY],
            "action":final_action.value,
            "matched_rules":[r.name for r in matched_rules],
            "risk_level":highest_risk.risk_level,
            "reason":f"matched_{len(matched_rules)}_rules"
        }

class PolicyEngine:
    def __init__(self,policy_path:str):
        self.policy_path=policy_path
        self.policy_set=PolicySet(name="default")
        self._load_policies()

    def _load_policies(self):
        try:
            with open(self.policy_path,'r',encoding='utf-8') as f:
                data=json.load(f)
            self.policy_set=PolicySet(
                name=data.get('name','default'),
                default_action=RuleAction(data.get('default_action','deny'))
            )
            for rule_data in data.get('rules',[]):
                rule=PolicyRule(
                    name=rule_data['name'],
                    description=rule_data.get('description',''),
                    resource=ResourceType(rule_data['resource']),
                    action=RuleAction(rule_data['action']),
                    conditions=rule_data.get('conditions',{}),
                    risk_level=rule_data.get('risk_level','low'),
                    priority=rule_data.get('priority',0),
                    enabled=rule_data.get('enabled',True)
                )
                self.policy_set.rules.append(rule)
            logger.info(f"Loaded {len(self.policy_set.rules)} policy rules")
        except FileNotFoundError:
            logger.warning(f"Policy file not found:{self.policy_path},using defaults")
            self._create_default_policies()
        except Exception as e:
            logger.error(f"Failed to load policies:{e}")
            self._create_default_policies()

    def _create_default_policies(self):
        self.policy_set.rules=[
            PolicyRule(
                name="allow_safe_api",
                description="Allow safe API calls",
                resource=ResourceType.API_CALL,
                action=RuleAction.ALLOW,
                conditions={"method":"^(GET|HEAD|OPTIONS)$"},
                risk_level="low",
                priority=10
            ),
            PolicyRule(
                name="human_loop_write",
                description="Require human approval for write operations",
                resource=ResourceType.API_CALL,
                action=RuleAction.HUMAN_LOOP,
                conditions={"method":"^(POST|PUT|PATCH|DELETE)$"},
                risk_level="medium",
                priority=20
            ),
            PolicyRule(
                name="deny_system_files",
                description="Deny access to system files",
                resource=ResourceType.FILE_ACCESS,
                action=RuleAction.DENY,
                conditions={"path":"^(/etc/|/sys/|/proc/|C:\\\\Windows\\\\)"},
                risk_level="high",
                priority=100
            ),
            PolicyRule(
                name="allow_user_files",
                description="Allow access to user files",
                resource=ResourceType.FILE_ACCESS,
                action=RuleAction.ALLOW,
                conditions={},
                risk_level="low",
                priority=5
            ),
            PolicyRule(
                name="deny_external_network",
                description="Deny external network access by default",
                resource=ResourceType.NETWORK,
                action=RuleAction.DENY,
                conditions={"target":"^(?!localhost|127\\.0\\.0\\.1|10\\.|172\\.|192\\.168\\.).*"},
                risk_level="medium",
                priority=50
            ),
            PolicyRule(
                name="budget_llm_calls",
                description="Allow LLM calls with budget tracking",
                resource=ResourceType.LLM_CALL,
                action=RuleAction.ALLOW,
                conditions={},
                risk_level="low",
                priority=5
            ),
        ]

    async def evaluate(self,ctx:ExecutionContext)->Dict[str,Any]:
        result=self.policy_set.evaluate(ctx)
        ctx.policy_result=result
        logger.debug(f"Policy evaluation for {ctx.request_id}:{result['action']}")
        return result

    async def close(self):
        pass
