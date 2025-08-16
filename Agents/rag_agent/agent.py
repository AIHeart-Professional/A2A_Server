import logging
import os
import sys

# ADK imports
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH

# Configure API credentials
os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "")
# Alternatively, you can use Vertex AI
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/credentials.json"

# Ensure project root is on sys.path so `mcp_server` can be imported when ADK runs from Agents/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from mcp_server.Tools.Character.adk_tool import (
    create_character_tool,
    update_character_tool,
    get_character_tool,
    delete_character_tool
)

logging.basicConfig(level=logging.INFO)

a2a_app = to_a2a(remote, port=8001)  # serve with uvicorn

character_handler_sub_agent = Agent(
    name="character_handler_sub_agent",
    model="gemini-1.5-flash",
    description="Agent designed to handle character interactions for a roleplaying game.",
    instruction="You are an expert at managing characters for a roleplaying game. You can help with things such as editing character information, creating characters, and deleting characters.",
    tools=[create_character_tool, update_character_tool, get_character_tool, delete_character_tool]
)
def character_agent():
    return Agent(
        name="character_agent",
        model="gemini-1.5-flash",
        description="Agent designed to interact with players characters",
        instruction="You are an expert at managing characters for a roleplaying game. Your role is to only call out to required sub-agents to handle the work.",
        sub_agents=[character_handler_sub_agent]
    )

root_agent = character_agent()
