import json
import yaml
from typing import Dict,Any,List
from .engine import PolicyRule,PolicySet,RuleAction,ResourceType

class PolicyLoader:
    @staticmethod
    def from_json(path:str)->PolicySet:
        with open(path,'r',encoding='utf-8') as f:
            data=json.load(f)
        return PolicyLoader._build_policy_set(data)

    @staticmethod
    def from_yaml(path:str)->PolicySet:
        with open(path,'r',encoding='utf-8') as f:
            data=yaml.safe_load(f)
        return PolicyLoader._build_policy_set(data)

    @staticmethod
    def _build_policy_set(data:Dict[str,Any])->PolicySet:
        ps=PolicySet(
            name=data.get('name','loaded'),
            default_action=RuleAction(data.get('default_action','deny'))
        )
        for rd in data.get('rules',[]):
            ps.rules.append(PolicyRule(
                name=rd['name'],
                description=rd.get('description',''),
                resource=ResourceType(rd['resource']),
                action=RuleAction(rd['action']),
                conditions=rd.get('conditions',{}),
                risk_level=rd.get('risk_level','low'),
                priority=rd.get('priority',0),
                enabled=rd.get('enabled',True)
            ))
        return ps

    @staticmethod
    def export(policy_set:PolicySet,path:str,format:str='json'):
        data={
            'name':policy_set.name,
            'default_action':policy_set.default_action.value,
            'rules':[
                {
                    'name':r.name,
                    'description':r.description,
                    'resource':r.resource.value,
                    'action':r.action.value,
                    'conditions':r.conditions,
                    'risk_level':r.risk_level,
                    'priority':r.priority,
                    'enabled':r.enabled
                }
                for r in policy_set.rules
            ]
        }
        with open(path,'w',encoding='utf-8') as f:
            if format=='json':
                json.dump(data,f,indent=2)
            else:
                yaml.dump(data,f,default_flow_style=False)
