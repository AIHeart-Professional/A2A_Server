from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

# This file defines the agent card for the Veritas Parent A2A Agent

route_task_skill = AgentSkill(
    id="route_task",
    name="Route Task",
    description="Delegates or routes a task to the appropriate child agent.",
    tags=["orchestrate", "route", "delegate"],
    examples=[
        "Send this combat request to the combat agent.",
        "Have the inventory agent add a health potion.",
    ],
)

status_report_skill = AgentSkill(
    id="status_report",
    name="Status Report",
    description="Provides a high-level status of active agents and tasks.",
    tags=["report", "status", "monitor"],
    examples=[
        "What is the current state of all agents?",
        "Give me a summary of ongoing tasks.",
    ],
)

manage_agents_skill = AgentSkill(
    id="manage_agents",
    name="Manage Agents",
    description="Creates, updates, or configures child agents under Veritas.",
    tags=["manage", "configure", "admin"],
    examples=[
        "Register a new lore agent.",
        "Enable streaming for the narrative agent.",
    ],
)

agent_card = AgentCard(
    id="veritas",
    name="Veritas",
    description="Parent A2A agent that orchestrates and coordinates child agents.",
    url="http://localhost:8001/Agent/veritas",
    version="1.0.0",
    defaultInputModes=["text", "text/plain"],
    defaultOutputModes=["text", "text/plain"],
    capabilities=AgentCapabilities(streaming=True, pushNotifications=True),
    skills=[route_task_skill, status_report_skill, manage_agents_skill],
)

# Export alias expected by other modules
agent = agent_card
