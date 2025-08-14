from google.adk.agents import Agent
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
# This file defines the agent card for the Lore Agent

query_lore_skill = AgentSkill(
    id="query_lore",
    name="Query Lore",
    description="Answers questions about world lore, factions, history, and places.",
    tags=["lore", "history", "world", "factions"],
    examples=["Who founded Aincrad?", "Tell me about the Black Swordsman legend."],
)

add_lore_entry_skill = AgentSkill(
    id="add_lore_entry",
    name="Add Lore Entry",
    description="Adds or updates a lore entry in the lore database.",
    tags=["lore", "add", "update"],
    examples=["Add lore about the Holy Dragon Alliance.", "Update the entry on the Town of Beginnings."],
)

agent_card = AgentCard(
    id="lore_agent",
    name="Lore Agent",
    description="An agent that answers and manages game/world lore.",
    url="http://localhost:8001/Agent/lore_agent",
    version="1.0.0",
    defaultInputModes=["text", "text/plain"],
    defaultOutputModes=["text", "text/plain"],
    capabilities=AgentCapabilities(streaming=True, pushNotifications=True),
    skills=[query_lore_skill, add_lore_entry_skill],
)
