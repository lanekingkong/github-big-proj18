#!/usr/bin/env python3
"""AegisFlow — Enterprise AI Agent Runtime Governance Platform.

Usage:
    python -m aegisflow.main --config config.yaml
    aegisflow --config config.yaml
"""
import argparse
import logging
import sys
import uvicorn

from .core.config import AegisConfig
from .api.server import create_app

def setup_logging(level:str="INFO"):
    logging.basicConfig(
        level=getattr(logging,level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def main():
    parser=argparse.ArgumentParser(description="AegisFlow - AI Agent Runtime Governance")
    parser.add_argument("--config",default="config.yaml",help="Path to config file")
    parser.add_argument("--host",help="API host (overrides config)")
    parser.add_argument("--port",type=int,help="API port (overrides config)")
    parser.add_argument("--log-level",default="INFO",help="Logging level")
    args=parser.parse_args()

    setup_logging(args.log_level)
    logger=logging.getLogger(__name__)

    try:
        config=AegisConfig.from_yaml(args.config)
    except FileNotFoundError:
        logger.warning(f"Config not found:{args.config}, using defaults")
        from .core.config import PolicyConfig,BudgetConfig,SandboxConfig,CompressConfig,AuditConfig,HumanLoopConfig
        config=AegisConfig(
            policy=PolicyConfig(path="policies.json"),
            budget=BudgetConfig(),
            sandbox=SandboxConfig(),
            compress=CompressConfig(),
            audit=AuditConfig(),
            human_loop=HumanLoopConfig()
        )

    if args.host:
        config.api_host=args.host
    if args.port:
        config.api_port=args.port

    app=create_app(config)
    logger.info(f"Starting AegisFlow v0.1.0 on {config.api_host}:{config.api_port}")
    uvicorn.run(app,host=config.api_host,port=config.api_port,log_level=args.log_level.lower())

if __name__=="__main__":
    main()
