import importlib
import json
import logging
from tools import character_tools
import os
import yaml
from a2a.types import (
    AgentCard, 
    TaskState, 
    TaskStatus, 
    TaskStatusUpdateEvent
)

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    AgentCard, 
    TaskState, 
    TaskStatus, 
    TaskStatusUpdateEvent
)
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import Session as ADKSession
from google.genai import types as adk_types
from .agent_card import agent

logging.basicConfig(level=logging.INFO)

root_agent = agent

