import time
import logging
from typing import Dict,Any,Optional
from dataclasses import dataclass,field
from collections import defaultdict

from ..core.context import ExecutionContext

logger=logging.getLogger(__name__)

@dataclass
class BudgetResult:
    approved:bool
    remaining:int
    daily_used:int
    monthly_used:int
    per_request_limit:int
    reason:str=""

class TokenCounter:
    def __init__(self):
        self.daily_tokens:Dict[str,int]=defaultdict(int)
        self.monthly_tokens:Dict[str,int]=defaultdict(int)
        self.last_reset_day:str=""
        self.last_reset_month:str=""

    def _get_day_key(self)->str:
        return time.strftime("%Y-%m-%d")

    def _get_month_key(self)->str:
        return time.strftime("%Y-%m")

    def _check_reset(self):
        day_key=self._get_day_key()
        month_key=self._get_month_key()
        if day_key!=self.last_reset_day:
            self.daily_tokens.clear()
            self.last_reset_day=day_key
        if month_key!=self.last_reset_month:
            self.monthly_tokens.clear()
            self.last_reset_month=month_key

    def add(self,agent_id:str,tokens:int):
        self._check_reset()
        self.daily_tokens[agent_id]+=tokens
        self.monthly_tokens[agent_id]+=tokens

    def get_daily(self,agent_id:str)->int:
        return self.daily_tokens.get(agent_id,0)

    def get_monthly(self,agent_id:str)->int:
        return self.monthly_tokens.get(agent_id,0)

class ThrottleController:
    def __init__(self,max_requests_per_sec:int=100):
        self.max_rps=max_requests_per_sec
        self.request_times:list[float]=[]

    def can_proceed(self)->bool:
        now=time.time()
        self.request_times=[t for t in self.request_times if now-t<1.0]
        if len(self.request_times)>=self.max_rps:
            return False
        self.request_times.append(now)
        return True

class BudgetGuard:
    def __init__(self,config):
        self.config=config
        self.counter=TokenCounter()
        self.throttle=ThrottleController()
        self._budget_cache:Dict[str,Dict[str,Any]]={}

    async def check(self,ctx:ExecutionContext)->BudgetResult:
        agent_id=ctx.agent_id
        daily=self.counter.get_daily(agent_id)
        monthly=self.counter.get_monthly(agent_id)

        if not self.throttle.can_proceed():
            return BudgetResult(
                approved=False,
                remaining=0,
                daily_used=daily,
                monthly_used=monthly,
                per_request_limit=self.config.per_request_limit,
                reason="rate_limit_exceeded"
            )

        if daily>=self.config.daily_limit:
            return BudgetResult(
                approved=False,
                remaining=0,
                daily_used=daily,
                monthly_used=monthly,
                per_request_limit=self.config.per_request_limit,
                reason="daily_limit_exceeded"
            )

        if monthly>=self.config.monthly_limit:
            return BudgetResult(
                approved=False,
                remaining=0,
                daily_used=daily,
                monthly_used=monthly,
                per_request_limit=self.config.per_request_limit,
                reason="monthly_limit_exceeded"
            )

        remaining_daily=self.config.daily_limit-daily
        remaining_monthly=self.config.monthly_limit-monthly

        return BudgetResult(
            approved=True,
            remaining=min(remaining_daily,remaining_monthly),
            daily_used=daily,
            monthly_used=monthly,
            per_request_limit=self.config.per_request_limit
        )

    async def consume(self,ctx:ExecutionContext,tokens:int):
        self.counter.add(ctx.agent_id,tokens)
        logger.debug(f"Consumed {tokens} tokens for {ctx.agent_id}")

    async def get_stats(self,agent_id:str)->Dict[str,Any]:
        return {
            "daily_used":self.counter.get_daily(agent_id),
            "daily_limit":self.config.daily_limit,
            "monthly_used":self.counter.get_monthly(agent_id),
            "monthly_limit":self.config.monthly_limit,
            "per_request_limit":self.config.per_request_limit,
            "daily_remaining":max(0,self.config.daily_limit-self.counter.get_daily(agent_id)),
            "monthly_remaining":max(0,self.config.monthly_limit-self.counter.get_monthly(agent_id))
        }

    async def close(self):
        pass
