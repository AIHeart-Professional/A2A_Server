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
from .sub_agents import (
    action_parser_sub_agent,
    tactics_planner_sub_agent,
    taget_selector_sub_agent,
    narrative_writer_sub_agent,
    summary_writer_sub_agent
)
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

async def combat_agent():
    # Create main agent using dictionary to avoid shadowing warnings
    return Agent(
        name="combat_agent",
        model="gemini-1.5-flash",
        description="Agent designed to interact with players characters",
        instruction="You are an expert at managing characters for a roleplaying game. You can create and view character information.",
        sub_agents=[action_parser_sub_agent, tactics_planner_sub_agent, taget_selector_sub_agent, narrative_writer_sub_agent, summary_writer_sub_agent]
    )
    
root_agent = combat_agent()
