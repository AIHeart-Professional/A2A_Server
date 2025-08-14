from google.adk.agents import Agent
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
# This file defines the agent card for the Combat Agent

attack_skill = AgentSkill(
    id="attack",
    name="Attack",
    description="Initiates an attack using a specified weapon or skill.",
    tags=["combat", "attack", "battle"],
    examples=["Attack the goblin with my longsword.", "Use fireball on the ogre."],
)

defend_skill = AgentSkill(
    id="defend",
    name="Defend",
    description="Takes a defensive action, raising shields or evasion.",
    tags=["combat", "defend", "guard"],
    examples=["Defend against the next attack.", "Raise my shield."],
)

use_skill_skill = AgentSkill(
    id="use_skill",
    name="Use Skill",
    description="Uses a named combat skill or ability.",
    tags=["combat", "skill", "ability"],
    examples=["Use heavy strike.", "Cast heal on ally."],
)

agent_card = AgentCard(
    id="combat_agent",
    name="Combat Agent",
    description="An agent that handles combat actions and tactics.",
    url="http://localhost:8001/Agent/combat_agent",
    version="1.0.0",
    defaultInputModes=["text", "text/plain"],
    defaultOutputModes=["text", "text/plain"],
    capabilities=AgentCapabilities(streaming=True, pushNotifications=True),
    skills=[attack_skill, defend_skill, use_skill_skill],
)
