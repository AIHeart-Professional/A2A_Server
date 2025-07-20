from fastapi import FastAPI
from pydantic import BaseModel
from Orchestrator.orchestrator import run_orchestrator


async def execute_orchestrator(request: dict, details: dict):
    return await run_orchestrator(request, details)