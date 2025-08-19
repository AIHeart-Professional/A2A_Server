from google.adk.agents import Agent
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from starlette.responses import JSONResponse

# This file defines the agent card for the Character Agent

creating_character_skill = AgentSkill(
    id="create_character",
    name="Create Character",
    description="Creates a new character.",
    tags=["creation", "make", "create", "customize"],
    examples=["Create a character named Gandalf, a wizard.", "make a character with blue hair named leeroy"],
)

view_character_skill = AgentSkill(
    id="view_character",
    name="View Character",
    description="Views an existing character.",
    tags=["view", "retrieve", "character"],
    examples=["View the character named Gandalf.", "show me the character with blue hair named leeroy."],
)

async def agent_card(request):
    card = AgentCard(
        id = "character_agent",
        name="Character",
        description="An agent that interacts with characters.",
        url="http://localhost:8002",
        version="1.0.0",
        defaultInputModes=["text", "text/plain"],
        defaultOutputModes=["text", "text/plain"],
        capabilities = AgentCapabilities(streaming=True, pushNotifications=True),
        skills=[creating_character_skill, view_character_skill],
    )
    return JSONResponse(card.model_dump())