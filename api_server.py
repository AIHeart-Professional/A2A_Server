from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any
from mcp_server.app import get_tools, get_intents
from typing import List
from fastapi import Query
from Orchestrator.app import execute_orchestrator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- Application Setup ---

app = FastAPI(title="Discord RP Bot MCP Server API")


@app.on_event("startup")
async def startup_event():
    """Handles application startup logic: connect to DB and initialize services."""
    global rag_service, data_service, interpreter, llm_service
    logging.info("Application startup...")

@app.on_event("shutdown")
async def shutdown_event():
    """Handles application shutdown logic: close DB connection."""
    logging.info("Application shutdown...")

# --- API Models and Endpoints ---

class InitialRequest(BaseModel):
    user_query: str
    user_id: str
    server_id: str
class QueryRequest(BaseModel):
    initial_request: InitialRequest    
class OrchestratorRequest(BaseModel):
    request: dict
    details: dict
class ToolsRequest(BaseModel):
    agents: Dict[str, Any]
    tools: Dict[str, Any]

@app.post("/MCPServer/available_tools")
async def interpret_query(request: ToolsRequest):
    """
    API endpoint to interpret a user query using the MCP workflow.
    """
    response = await get_tools(request.agents, request.tools)
    return response

# --- get intents Endpoints ---
@app.get("/MCPServer/available_intents")
async def interpret_query():
    """
    API endpoint to interpret a user query using the MCP workflow.
    """
    # Route the request through the MCP interpreter
    response = await get_intents()
    return response

# --- Orchestrator Endpoint ---
@app.post("/orchestrator")
async def interpret_query(request: OrchestratorRequest):
    """
    API endpoint to initiate orchestrator.
    """
    # Route the request through the MCP interpreter
    response = await execute_orchestrator(request.request, request.details)
    return response