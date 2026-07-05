import json
import time
import sqlite3
import logging
from typing import Dict,Any,List,Optional
from dataclasses import dataclass,field
from pathlib import Path

from ..core.context import ExecutionContext

logger=logging.getLogger(__name__)

@dataclass
class AuditRecord:
    id:str
    timestamp:float=field(default_factory=time.time)
    agent_id:str=""
    action:str=""
    result:str=""
    reason:str=""
    token_cost:int=0
    duration:float=0.0
    session_id:str=""
    details:Dict[str,Any]=field(default_factory=dict)

class AuditStorage:
    def __init__(self,db_path:str=":memory:",encrypt:bool=True):
        self.db_path=db_path
        self.encrypt=encrypt
        self._conn=None

    def _get_conn(self):
        if self._conn is None:
            self._conn=sqlite3.connect(self.db_path,check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id TEXT PRIMARY KEY,
                    timestamp REAL,
                    agent_id TEXT,
                    action TEXT,
                    result TEXT,
                    reason TEXT,
                    token_cost INTEGER,
                    duration REAL,
                    session_id TEXT,
                    details TEXT
                )
            """)
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON audit_logs(agent_id)")
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_logs(timestamp)")
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON audit_logs(session_id)")
            self._conn.commit()
        return self._conn

    def insert(self,record:AuditRecord):
        conn=self._get_conn()
        details=json.dumps(record.details)
        if self.encrypt:
            details=self._simple_encrypt(details)
        conn.execute(
            """INSERT OR REPLACE INTO audit_logs VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (record.id,record.timestamp,record.agent_id,record.action,
             record.result,record.reason,record.token_cost,record.duration,
             record.session_id,details)
        )
        conn.commit()

    def query(self,agent_id:Optional[str]=None,limit:int=100)->List[Dict[str,Any]]:
        conn=self._get_conn()
        if agent_id:
            rows=conn.execute(
                "SELECT * FROM audit_logs WHERE agent_id=? ORDER BY timestamp DESC LIMIT ?",
                (agent_id,limit)
            ).fetchall()
        else:
            rows=conn.execute(
                "SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            ).fetchall()

        results=[]
        for row in rows:
            details=row[9]
            if self.encrypt:
                details=self._simple_decrypt(details)
            results.append({
                "id":row[0],"timestamp":row[1],"agent_id":row[2],
                "action":row[3],"result":row[4],"reason":row[5],
                "token_cost":row[6],"duration":row[7],"session_id":row[8],
                "details":json.loads(details)
            })
        return results

    def _simple_encrypt(self,text:str)->str:
        return ''.join(chr(ord(c)+1) for c in text)

    def _simple_decrypt(self,text:str)->str:
        return ''.join(chr(ord(c)-1) for c in text)

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn=None

class AuditTrail:
    def __init__(self,config):
        self.config=config
        self.storage=AuditStorage(
            db_path="aegisflow_audit.db",
            encrypt=config.encrypt
        )

    async def record_success(self,ctx:ExecutionContext):
        record=AuditRecord(
            id=f"audit_{ctx.request_id}",
            agent_id=ctx.agent_id,
            action=ctx.action,
            result="success",
            reason="",
            token_cost=ctx.execution_result.get("token_cost",0) if ctx.execution_result else 0,
            duration=ctx.duration,
            session_id=ctx.request_id,
            details=ctx.to_audit_dict()
        )
        self.storage.insert(record)

    async def record_policy_denial(self,ctx:ExecutionContext,reason:str):
        record=AuditRecord(
            id=f"audit_{ctx.request_id}",
            agent_id=ctx.agent_id,
            action=ctx.action,
            result="policy_denied",
            reason=reason,
            session_id=ctx.request_id,
            details=ctx.to_audit_dict()
        )
        self.storage.insert(record)

    async def record_budget_exceeded(self,ctx:ExecutionContext,remaining:int):
        record=AuditRecord(
            id=f"audit_{ctx.request_id}",
            agent_id=ctx.agent_id,
            action=ctx.action,
            result="budget_exceeded",
            reason=f"remaining:{remaining}",
            session_id=ctx.request_id,
            details=ctx.to_audit_dict()
        )
        self.storage.insert(record)

    async def record_human_denial(self,ctx:ExecutionContext,reason:str):
        record=AuditRecord(
            id=f"audit_{ctx.request_id}",
            agent_id=ctx.agent_id,
            action=ctx.action,
            result="human_denied",
            reason=reason,
            session_id=ctx.request_id,
            details=ctx.to_audit_dict()
        )
        self.storage.insert(record)

    async def record_error(self,ctx:ExecutionContext,error:str):
        record=AuditRecord(
            id=f"audit_{ctx.request_id}",
            agent_id=ctx.agent_id,
            action=ctx.action,
            result="error",
            reason=error,
            session_id=ctx.request_id,
            details=ctx.to_audit_dict()
        )
        self.storage.insert(record)

    async def query(self,agent_id:Optional[str]=None,limit:int=100)->List[Dict[str,Any]]:
        return self.storage.query(agent_id,limit)

    async def close(self):
        self.storage.close()
