import importlib
import json
import logging
import uuid
import os
import sys
import asyncio
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

# ADK imports
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents import Agent
from google.genai import types

# Configure API credentials
os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "")
# Alternatively, you can use Vertex AI
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/credentials.json"

# Ensure project root is on sys.path so `mcp_server` can be imported when ADK runs from Agents/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from mcp_server.Tools.Character import (
    create_character_tool
)

logging.basicConfig(level=logging.INFO)

# Define the root agent that will be exported
# Using a dictionary to avoid shadowing warnings
agent_config = {
    "name": "character_agent",
    "model": "gemini-1.5-flash",
    "description": "Agent designed to interact with players characters",
    "instruction": "You are an expert at managing characters for a roleplaying game. You can create and view character information."
}
root_agent = Agent(**agent_config)

async def execute_agent(request: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point invoked by Agents.app.

    Expected request structure (flexible):
    - request: { run_id?, skill_id?, input? }
    Other keys like agent_cards/agents are ignored here.

    This method is responsible for extracting the nested request payload, creating a session,
    creating an LLM agent with the instruction, and running the agent.

    :param request: The request payload from the client.
    :return: A dictionary containing the run_id of the executed agent.
    """
    session_service = InMemorySessionService()

    # Extract nested request payload if present
    payload = request.get("request", request)
    user_id = payload.get("user_info", {}).get("user_id", str(uuid.uuid4()))
    session_id = payload.get("user_info", {}).get("server_id", str(uuid.uuid4()))
    
    # Create session
    session = await session_service.create_session(
        app_name="Character_app",
        user_id=user_id,
        session_id=session_id,        
    )
    
    # Create content from user query
    content = types.Content(role='user', parts=[types.Part(text=payload.get("user_query", ""))])
    
    # Create sub-agents using dictionaries to avoid shadowing warnings
    create_agent_config = {
        "name": "create_character_sub_agent",
        "model": "gemini-1.5-flash",
        "description": "agent designed to create characters",
        "instruction": "You are an expert at creating characters for a roleplaying game.",
        "tools": [create_character_tool]
    }
    create_character_sub_agent = Agent(**create_agent_config)

    view_agent_config = {
        "name": "view_character_sub_agent",
        "model": "gemini-1.5-flash",
        "description": "agent designed to view characters",
        "instruction": "You are an expert at viewing characters for a roleplaying game."
    }
    view_character_sub_agent = Agent(**view_agent_config)
    
    # Create main agent using dictionary to avoid shadowing warnings
    main_agent_config = {
        "model": "gemini-1.5-flash",
        "name": "character_agent",
        "description": "Agent designed to interact with players characters",
        "instruction": "You are an expert at managing characters for a roleplaying game. You can create and view character information.",
        "sub_agents": [create_character_sub_agent, view_character_sub_agent]
    }
    character_agent = Agent(**main_agent_config)
    
    # Create runner
    runner = Runner(
        session_service=session_service,
        agent=character_agent,
        app_name="Character_app",
    )

    # Run the agent and process events
    final_response_text = ""
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # Process events
        if event.is_final_response():
            if event.content and event.content.parts:
                # Get text response from the first part
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                # Handle potential errors/escalations
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break  # Stop processing events once the final response is found

    return {"run_id": payload, "response": final_response_text}

