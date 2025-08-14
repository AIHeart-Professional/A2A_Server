from google.adk.agents import Agent
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
# This file defines the agent card for the Item Agent

inspect_item_skill = AgentSkill(
    id="inspect_item",
    name="Inspect Item",
    description="Inspects details about an item (stats, rarity, description).",
    tags=["inspect", "item", "details", "metadata"],
    examples=["Inspect the longsword.", "Show info for the health potion."],
)

transfer_item_skill = AgentSkill(
    id="transfer_item",
    name="Transfer Item",
    description="Transfers an item between entities or inventories.",
    tags=["transfer", "move", "item"],
    examples=["Give my longsword to Kirito.", "Move 2 potions to Asuna."],
)

agent_card = AgentCard(
    id="item_agent",
    name="Item Agent",
    description="An agent that manages and inspects items.",
    url="http://localhost:8001/Agent/item_agent",
    version="1.0.0",
    defaultInputModes=["text", "text/plain"],
    defaultOutputModes=["text", "text/plain"],
    capabilities=AgentCapabilities(streaming=True, pushNotifications=True),
    skills=[inspect_item_skill, transfer_item_skill],
)
