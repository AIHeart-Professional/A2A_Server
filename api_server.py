from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from mcp_server.app import get_tools, get_intents
from typing import List
from fastapi import Query
from Orchestrator.app import execute_orchestrator
from A2A_Server.app import get_agent_card_info, instructions
from LLM.app import agent_to_use
from Agents.app import execute_agent, execute_agent_stream
import logging
import json
import time

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
class AgentsToUseRequest(BaseModel):
    request: str
    agent_cards: List
class HandleRequest(BaseModel):
    request: Dict[str, Any]
    agent_card: list
    agents: Dict[str, Any]

    
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

# --- Agent Card Endpoint ---
@app.get("/A2A/agent.json")
async def get_agent_card():
    """
    API endpoint to retrieve agent card information.
    """
    response = await get_agent_card_info()
    return response

@app.get("/A2A/instructions")
async def get_instructions():
    """
    API endpoint to retrieve instructions for using the agent cards.
    """
    instruction = await instructions()
    return instruction

# --- Agent to use Endpoint ---
@app.post("/LLM/agents_to_use")
async def get_agents_to_use(request: AgentsToUseRequest) -> dict:
    """
    API endpoint to retrieve agents to use based on the user query and intents.
    """
    logging.info(f"Received request: {request.model_dump()}")
    result = await agent_to_use(request.model_dump())
    return result

@app.post("/A2A/handle_request")
async def handle_request(request: HandleRequest) -> dict:
    """
    API endpoint to retrieve agents to use based on the user query and intents.
    """
    logging.info(f"Received request: {request.model_dump()}")
    result = await execute_agent(request.model_dump())
    return result

@app.post("/A2A/handle_request_stream")
async def handle_request_stream(request: HandleRequest):
    """
    Streaming API endpoint that shows real-time agent processing flow.
    Returns Server-Sent Events (SSE) for live updates.
    """
    
    async def event_stream():
        try:
            # Use the same execute_agent_stream from Agents/app.py
            async for event_data in execute_agent_stream(request.model_dump()):
                # Format as Server-Sent Event
                yield f"data: {json.dumps(event_data)}\n\n"
                
        except Exception as e:
            # Send error event
            error_data = {
                'type': 'error',
                'message': f'Streaming failed: {str(e)}',
                'error_type': type(e).__name__
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")