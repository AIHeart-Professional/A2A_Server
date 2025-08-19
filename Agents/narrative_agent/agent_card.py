from google.adk.agents import Agent
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from starlette.responses import JSONResponse
# This file defines the agent card for the Narrative Agent

compose_scene_skill = AgentSkill(
    id="compose_scene",
    name="Compose Scene",
    description="Composes a narrative scene or story beat.",
    tags=["narrative", "story", "scene"],
    examples=["Write a scene where Kirito meets Asuna.", "Describe the marketplace in detail."],
)

summarize_events_skill = AgentSkill(
    id="summarize_events",
    name="Summarize Events",
    description="Summarizes recent events or player actions into narrative.",
    tags=["narrative", "summary", "recap"],
    examples=["Summarize what happened in the last quest.", "Give me a recap of the battle."],
)

async def agent_card(request):
    card = AgentCard(
        id="narrative_agent",
        name="Narrative Agent",
        description="An agent that responds to the request of I want to go fishing.",
        url="http://localhost:8002",
        version="1.0.0",
        defaultInputModes=["text", "text/plain"],
        defaultOutputModes=["text", "text/plain"],
        capabilities=AgentCapabilities(streaming=True, pushNotifications=True),
        skills=[compose_scene_skill, summarize_events_skill],
    )
    return JSONResponse(card.dict())
