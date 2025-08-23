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
    agent_delegator_sub_agent
)
# Configure API credentials - ensure we have a valid API key
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    # Try to load from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.environ.get("GOOGLE_API_KEY")
    except ImportError:
        pass

if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is required. Please set it in your environment or .env file.")

os.environ["GOOGLE_API_KEY"] = api_key

logging.basicConfig(level=logging.INFO)

def veritas_agent():
    # Create main agent using dictionary to avoid shadowing warnings
    return Agent(
        name="Veritas_Agent",
        model="gemini-2.0-flash",
        description="Agent designed as a parent agent whose purpose is to delegate tasks to other agents.",
        instruction="You are a parent agent that immediately delegates all user requests to your sub-agent.",
        sub_agents=[agent_delegator_sub_agent],
    )
    
root_agent = veritas_agent()
