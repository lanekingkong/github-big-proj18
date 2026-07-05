import asyncio
import json
from fastapi import FastAPI,HTTPException,WebSocket,WebSocketDisconnect,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Dict
import logging

from ..core.config import AegisConfig
from ..core.orchestrator import Orchestrator,AgentRequest

logger=logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections:Dict[str,WebSocket]={}

    async def connect(self,client_id:str,websocket:WebSocket):
        await websocket.accept()
        self.active_connections[client_id]=websocket

    def disconnect(self,client_id:str):
        self.active_connections.pop(client_id,None)

    async def send(self,client_id:str,message:dict):
        ws=self.active_connections.get(client_id)
        if ws:
            await ws.send_json(message)

    async def broadcast(self,message:dict):
        for ws in list(self.active_connections.values()):
            try:
                await ws.send_json(message)
            except:
                pass

ws_manager=ConnectionManager()

def create_app(config:AegisConfig)->FastAPI:
    orchestrator=Orchestrator(config)

    @asynccontextmanager
    async def lifespan(app:FastAPI):
        logger.info(f"AegisFlow starting on {config.api_host}:{config.api_port}")
        app.state.orchestrator=orchestrator
        yield
        logger.info("AegisFlow shutting down")
        await orchestrator.shutdown()

    app=FastAPI(
        title="AegisFlow",
        description="Enterprise AI Agent Runtime Governance Platform",
        version="0.1.0",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        return {"status":"ok","version":"0.1.0"}

    @app.post("/api/v1/execute")
    async def execute_agent(request:Request):
        try:
            body=await request.json()
            agent_request=AgentRequest(
                agent_id=body.get("agent_id","unknown"),
                action=body.get("action",""),
                payload=body.get("payload",{}),
                session_id=body.get("session_id")
            )
            result=await orchestrator.execute(agent_request)
            return JSONResponse(content=result)
        except Exception as e:
            logger.error(f"Execute failed:{e}")
            raise HTTPException(status_code=500,detail=str(e))

    @app.get("/api/v1/stats/{agent_id}")
    async def get_stats(agent_id:str):
        stats=await orchestrator.budget_guard.get_stats(agent_id)
        return JSONResponse(content=stats)

    @app.get("/api/v1/audit/{agent_id}")
    async def get_audit(agent_id:str,limit:int=100):
        records=await orchestrator.audit_trail.query(agent_id,limit)
        return JSONResponse(content=records)

    @app.get("/api/v1/approvals")
    async def get_approvals():
        pending=await orchestrator.human_gateway.get_pending()
        return JSONResponse(content=[{
            "id":a.id,"agent_id":a.agent_id,
            "action":a.action,"reason":a.reason,
            "risk_level":a.risk_level,"status":a.status.value
        } for a in pending])

    @app.post("/api/v1/approvals/{request_id}/approve")
    async def approve_request(request_id:str):
        await orchestrator.human_gateway.approve(request_id)
        return {"status":"approved"}

    @app.post("/api/v1/approvals/{request_id}/deny")
    async def deny_request(request_id:str):
        await orchestrator.human_gateway.deny(request_id)
        return {"status":"denied"}

    @app.get("/api/v1/policies")
    async def get_policies():
        return JSONResponse(content={
            "name":orchestrator.policy_engine.policy_set.name,
            "default_action":orchestrator.policy_engine.policy_set.default_action.value,
            "rules":[
                {
                    "name":r.name,"description":r.description,
                    "resource":r.resource.value,"action":r.action.value,
                    "risk_level":r.risk_level,"priority":r.priority,"enabled":r.enabled
                }
                for r in orchestrator.policy_engine.policy_set.rules
            ]
        })

    @app.get("/api/v1/config")
    async def get_config():
        return JSONResponse(content=orchestrator.config.to_dict())

    @app.websocket("/ws/{client_id}")
    async def websocket_endpoint(websocket:WebSocket,client_id:str):
        await ws_manager.connect(client_id,websocket)
        try:
            await websocket.send_json({"type":"connected","client_id":client_id})
            while True:
                data=await websocket.receive_json()
                if data.get("type")=="execute":
                    agent_request=AgentRequest(
                        agent_id=data.get("agent_id","ws_client"),
                        action=data.get("action",""),
                        payload=data.get("payload",{}),
                        session_id=data.get("session_id")
                    )
                    result=await orchestrator.execute(agent_request)
                    await websocket.send_json({"type":"result","data":result})
                else:
                    await websocket.send_json({"type":"echo","data":data})
        except WebSocketDisconnect:
            ws_manager.disconnect(client_id)
        except Exception as e:
            logger.error(f"WebSocket error for {client_id}:{e}")

    return app
