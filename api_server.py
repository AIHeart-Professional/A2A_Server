from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- Application Setup ---

app = FastAPI(title="Discord RP Bot AI API")


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

class QueryRequest(BaseModel):
    user_query: str
    session_context: Optional[Dict[str, Any]] = None

@app.post("/MCP")
async def interpret_query(request: QueryRequest):
    """
    API endpoint to interpret a user query using the MCP workflow.
    """
    user_id = "anonymous"
    if request.session_context and 'user' in request.session_context and 'id' in request.session_context['user']:
        user_id = request.session_context['user']['id']

    # Route the request through the MCP interpreter
    response = await interpreter.route_request(
        user_id=user_id,
        message=request.user_query,
        session_context=request.session_context or {}
    )
    return response
