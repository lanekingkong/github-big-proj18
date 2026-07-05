import os
import tempfile
import shutil
import logging
from typing import Dict,Any,Optional
from dataclasses import dataclass,field
from pathlib import Path

from ..core.context import ExecutionContext

logger=logging.getLogger(__name__)

@dataclass
class SandboxResult:
    output:Dict[str,Any]
    token_cost:int=0
    execution_time:float=0.0
    exit_code:int=0
    error:Optional[str]=None

class VirtualFS:
    def __init__(self,root_dir:str,allowed_dirs:list[str]=None,denied_dirs:list[str]=None):
        self.root=Path(root_dir)
        self.allowed_dirs=[Path(d) for d in (allowed_dirs or [])]
        self.denied_dirs=[Path(d) for d in (denied_dirs or [])]
        self.root.mkdir(parents=True,exist_ok=True)

    def resolve(self,path:str)->Path:
        p=Path(path)
        if p.is_absolute():
            return p
        return self.root/p

    def is_allowed(self,path:str)->bool:
        resolved=self.resolve(path)
        resolved_str=str(resolved.resolve())

        for denied in self.denied_dirs:
            if resolved_str.startswith(str(denied.resolve())):
                return False

        if self.allowed_dirs:
            for allowed in self.allowed_dirs:
                if resolved_str.startswith(str(allowed.resolve())):
                    return True
            return False

        return True

    def read_file(self,path:str)->str:
        if not self.is_allowed(path):
            raise PermissionError(f"Access denied:{path}")
        resolved=self.resolve(path)
        return resolved.read_text(encoding='utf-8')

    def write_file(self,path:str,content:str):
        if not self.is_allowed(path):
            raise PermissionError(f"Access denied:{path}")
        resolved=self.resolve(path)
        resolved.parent.mkdir(parents=True,exist_ok=True)
        resolved.write_text(content,encoding='utf-8')

    def list_dir(self,path:str=".")->list[str]:
        if not self.is_allowed(path):
            raise PermissionError(f"Access denied:{path}")
        resolved=self.resolve(path)
        return [str(p.relative_to(self.root)) for p in resolved.iterdir()]

class ProcessIsolator:
    def __init__(self,max_processes:int=10,max_memory_mb:int=512):
        self.max_processes=max_processes
        self.max_memory_mb=max_memory_mb
        self.active_processes:int=0

    def can_spawn(self)->bool:
        return self.active_processes<self.max_processes

    def estimate_memory(self,payload:Dict[str,Any])->int:
        import sys
        return sys.getsizeof(str(payload))//(1024*1024)

class SandboxExecutor:
    def __init__(self,config):
        self.config=config
        self.sandbox_dir=tempfile.mkdtemp(prefix="aegis_sandbox_")
        self.vfs=VirtualFS(
            root_dir=self.sandbox_dir,
            allowed_dirs=config.allowed_dirs or [],
            denied_dirs=config.denied_dirs or [
                "C:\\Windows","C:\\Program Files","C:\\Program Files (x86)",
                "/etc","/sys","/proc","/boot"
            ]
        )
        self.isolator=ProcessIsolator(
            max_processes=config.max_processes,
            max_memory_mb=config.max_memory_mb
        )

    async def execute(self,ctx:ExecutionContext)->SandboxResult:
        import time
        start=time.time()

        if not self.config.enabled:
            return SandboxResult(
                output={"message":"sandbox_disabled","payload":ctx.payload},
                execution_time=time.time()-start
            )

        if not self.isolator.can_spawn():
            return SandboxResult(
                output={},
                error="max_processes_exceeded",
                exit_code=-1,
                execution_time=time.time()-start
            )

        try:
            action=ctx.action
            payload=ctx.compressed_payload or ctx.payload

            if action=="file_access":
                result=await self._handle_file_access(payload)
            elif action=="api_call":
                result=await self._handle_api_call(payload)
            elif action=="process":
                result=await self._handle_process(payload)
            else:
                result={"message":"action_handled","action":action,"payload":payload}

            elapsed=time.time()-start
            token_estimate=len(str(payload))//4

            return SandboxResult(
                output=result,
                token_cost=token_estimate,
                execution_time=elapsed
            )

        except Exception as e:
            logger.error(f"Sandbox execution failed:{e}")
            return SandboxResult(
                output={},
                error=str(e),
                exit_code=-1,
                execution_time=time.time()-start
            )

    async def _handle_file_access(self,payload:Dict[str,Any])->Dict[str,Any]:
        operation=payload.get("operation","read")
        path=payload.get("path","")

        if operation=="read":
            content=self.vfs.read_file(path)
            return {"operation":"read","path":path,"content":content[:10000]}
        elif operation=="write":
            content=payload.get("content","")
            self.vfs.write_file(path,content)
            return {"operation":"write","path":path,"size":len(content)}
        elif operation=="list":
            files=self.vfs.list_dir(path)
            return {"operation":"list","path":path,"files":files}
        else:
            return {"error":f"unknown_operation:{operation}"}

    async def _handle_api_call(self,payload:Dict[str,Any])->Dict[str,Any]:
        return {"message":"api_call_simulated","payload":payload}

    async def _handle_process(self,payload:Dict[str,Any])->Dict[str,Any]:
        return {"message":"process_simulated","payload":payload}

    async def cleanup(self):
        if os.path.exists(self.sandbox_dir):
            shutil.rmtree(self.sandbox_dir,ignore_errors=True)
