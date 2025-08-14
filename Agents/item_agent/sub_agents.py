import os
import sys
from google.adk.agents import Agent
# Configure API credentials
os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "")
# Alternatively, you can use Vertex AI
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/credentials.json"

# Ensure project root is on sys.path so `mcp_server` can be imported when ADK runs from Agents/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from mcp_server.Tools.Item import (
    create_item_tool,
    read_item_tool,
    update_item_tool,
    delete_item_tool
)
query_normalizer_sub_agent = Agent(
    name="query_normalizer_sub_agent",
    model="gemini-1.5-flash",
    description="Agent designed to normalize queries for a roleplaying game.",
    instruction="You are an expert at normalizing queries for a roleplaying game.",
)

modifier_sub_agent = Agent(
    name="modifier_sub_agent",
    model="gemini-1.5-flash",
    description="Agent designed to modify items for a roleplaying game.",
    instruction="You are an expert at modifying items for a roleplaying game.",
    tools=[create_item_tool, update_item_tool, delete_item_tool]
)

search_sub_agent = Agent(
    name="search_sub_agent",
    model="gemini-1.5-flash",
    description="Agent designed to search for items for a roleplaying game.",
    instruction="You are an expert at searching for items for a roleplaying game. You can get any information of an item the user asks for.",
    tools=[read_item_tool]
)

tool_tip_sub_agent = Agent(
    name="tool_tip_sub_agent",
    model="gemini-1.5-flash",
    description="Agent designed to provide tool tips for a roleplaying game.",
    instruction="You are an expert at providing tool tips for a roleplaying game.",
    tools=[read_item_tool]
)

flavor_writer_sub_agent = Agent(
    name="narrative_writer_sub_agent",
    model="gemini-1.5-flash",
    description="Agent designed to write narratives for a roleplaying game.",
    instruction="You are an expert at writing narratives for a roleplaying game.",
    tools=[read_item_tool]
)

recipe_suggestion_sub_agent = Agent(
    name="recipe_suggestion_sub_agent",
    model="gemini-1.5-flash",
    description="Agent designed to suggest recipes for a roleplaying game.",
    instruction="You are an expert at suggesting recipes for a roleplaying game.",
    tools=[read_item_tool]
)