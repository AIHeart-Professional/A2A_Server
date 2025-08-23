from google.adk.agents import Agent
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from starlette.responses import JSONResponse

# This file defines the agent card for the Character Agent

character_skill = AgentSkill(
    id="character_skill",
    name="Character Skill",
    description="Handles character-related tasks.",
    tags=["character", "level up", "respec", "build"],
    examples=["I want to create a character named Kirito.",
    "I want to level up.",
    "I want to see my stats.",
    "I want to see Kirito's stats.",
    "What's my level?"],
)

inventory_skill = AgentSkill(
    id="inventory_skill",
    name="Inventory Skill",
    description="Handles inventory-related tasks.",
    tags=["inventory", "transfer", "equipment", "use", "drop"],
    examples=["I want to see my inventory", 
    "I want to see Kirito's inventory", 
    "I want to drop a sword", 
    "I want to use a potion", 
    "I want to equip a sword"],
)

async def agent_card(request):
    card = AgentCard(
        id = "mechanics_agent",
        name="Mechanics",
        description="An agent that interacts with mechanics regarding the game.",
        url="http://localhost:8002",
        version="1.0.0",
        defaultInputModes=["text", "text/plain"],
        defaultOutputModes=["text", "text/plain"],
        capabilities = AgentCapabilities(streaming=True, pushNotifications=True),
        skills=[character_skill, inventory_skill],
    )
    return JSONResponse(card.model_dump())