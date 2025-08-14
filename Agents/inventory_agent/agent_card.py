from google.adk.agents import Agent
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
# This file defines the agent card for the Inventory Agent

add_inventory_skill = AgentSkill(
    id="add_item",
    name="Add Item",
    description="Adds a new item to the inventory.",
    tags=["add", "insert", "item", "customize"],
    examples=["Add a sword.", "put a health potion in the inventory."],
)

view_inventory_skill = AgentSkill(
    id="view_inventory",
    name="View Inventory",
    description="Views the current inventory.",
    tags=["view", "retrieve", "inventory"],
    examples=["View the inventory.", "show me the items in the inventory."],
)

agent_card = AgentCard(
    id = "inventory_agent",
    name="Inventory Agent",
    description="An agent that interacts with a player's inventory.",
    url="http://localhost:8001/Agent/inventory_agent",
    version="1.0.0",
    defaultInputModes=["text", "text/plain"],
    defaultOutputModes=["text", "text/plain"],
    capabilities = AgentCapabilities(streaming=True, pushNotifications=True),
    skills=[add_inventory_skill, view_inventory_skill],

)