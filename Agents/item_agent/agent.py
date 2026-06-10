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
    query_normalizer_sub_agent,
    modifier_sub_agent,
    search_sub_agent
)
# Configure API credentials
os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "")
# Alternatively, you can use Vertex AI

logging.basicConfig(level=logging.INFO)

def item_agent():
    # Create main agent using dictionary to avoid shadowing warnings
    return Agent(
        name="item_agent",
        model="gemini-2.0-flash",
        description="Agent designed to interact with players items",
        instruction="You are an expert at managing items for a roleplaying game. You can create and view item information.",
        sub_agents=[query_normalizer_sub_agent, modifier_sub_agent, search_sub_agent]
    )
    
root_agent = item_agent()
