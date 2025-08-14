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
# Configure API credentials
os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "")
# Alternatively, you can use Vertex AI

logging.basicConfig(level=logging.INFO)

def veritas_agent():
    # Create main agent using dictionary to avoid shadowing warnings
    return Agent(
        name="Veritas_Agent",
        model="gemini-2.0-flash",
        description="Agent designed as a parent agent whose purpose is to delegate tasks to other agents.",
        instruction="You are an expert at delegating tasks to other agents.",
        sub_agents=[agent_delegator_sub_agent]
    )
    
root_agent = veritas_agent()
