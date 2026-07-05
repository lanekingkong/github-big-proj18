import json
import re
import logging
from typing import Dict,Any,Optional
from dataclasses import dataclass

from ..core.context import ExecutionContext

logger=logging.getLogger(__name__)

@dataclass
class CompressResult:
    compressed:Dict[str,Any]
    original_tokens:int
    compressed_tokens:int
    ratio:float
    algorithm:str

class CacheAligner:
    def __init__(self):
        self.cache:Dict[str,str]={}

    def align(self,content:str,key:str="default")->str:
        if key in self.cache:
            cached=self.cache[key]
            if content.startswith(cached):
                return content[len(cached):]
        self.cache[key]=content
        return content

    def clear(self):
        self.cache.clear()

class ContentRouter:
    def __init__(self):
        self.routes={
            "json":self._compress_json,
            "code":self._compress_code,
            "text":self._compress_text,
            "log":self._compress_log,
        }

    def route(self,content:str,content_type:str="auto")->str:
        if content_type=="auto":
            content_type=self._detect_type(content)
        handler=self.routes.get(content_type,self._compress_text)
        return handler(content)

    def _detect_type(self,content:str)->str:
        content=content.strip()
        if content.startswith('{') or content.startswith('['):
            try:
                json.loads(content)
                return "json"
            except:
                pass
        if re.search(r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',content):
            return "log"
        if re.search(r'(def |class |function |import |from |const |let |var )',content):
            return "code"
        return "text"

    def _compress_json(self,content:str)->str:
        try:
            data=json.loads(content)
            if isinstance(data,dict):
                compressed={k:v for k,v in data.items() if v is not None and v!=""}
                return json.dumps(compressed,separators=(',',':'))
            elif isinstance(data,list):
                if len(data)>10:
                    return json.dumps(data[:10],separators=(',',':'))+f"...[{len(data)-10} more]"
                return json.dumps(data,separators=(',',':'))
        except:
            pass
        return content

    def _compress_code(self,content:str)->str:
        lines=content.split('\n')
        compressed=[]
        for line in lines:
            stripped=line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('//'):
                compressed.append(stripped)
        return '\n'.join(compressed)

    def _compress_text(self,content:str)->str:
        if len(content)>5000:
            return content[:2500]+f"\n...[truncated {len(content)-5000} chars]...\n"+content[-2500:]
        return content

    def _compress_log(self,content:str)->str:
        lines=content.split('\n')
        seen_patterns=set()
        compressed=[]
        for line in lines:
            pattern=re.sub(r'\d+','#',re.sub(r'[a-f0-9]{8,}','ID',line))
            if pattern not in seen_patterns:
                seen_patterns.add(pattern)
                compressed.append(line)
            elif len(compressed)<3:
                compressed.append(line)
        return '\n'.join(compressed)

class CCRManager:
    def __init__(self):
        self.original_store:Dict[str,str]={}

    def store(self,key:str,original:str):
        self.original_store[key]=original

    def retrieve(self,key:str)->Optional[str]:
        return self.original_store.get(key)

    def clear(self):
        self.original_store.clear()

class ContentCompressor:
    def __init__(self,config):
        self.config=config
        self.router=ContentRouter()
        self.cache_aligner=CacheAligner()
        self.ccr=CCRManager()

    async def compress(self,ctx:ExecutionContext)->Dict[str,Any]:
        if not self.config.enabled:
            return ctx.payload

        payload=ctx.payload
        compressed={}
        total_original=0
        total_compressed=0

        for key,value in payload.items():
            if isinstance(value,str):
                original_len=len(value)
                total_original+=original_len

                aligned=self.cache_aligner.align(value,key)
                compressed_value=self.router.route(aligned)

                compressed_len=len(compressed_value)
                total_compressed+=compressed_len

                if compressed_len<original_len:
                    ccr_key=f"{ctx.request_id}:{key}"
                    self.ccr.store(ccr_key,value)
                    compressed[key]=compressed_value
                else:
                    compressed[key]=value
            else:
                compressed[key]=value

        ratio=1.0-(total_compressed/max(total_original,1))
        logger.debug(f"Compression ratio:{ratio:.2%} for {ctx.request_id}")

        return compressed

    async def close(self):
        self.cache_aligner.clear()
        self.ccr.clear()
