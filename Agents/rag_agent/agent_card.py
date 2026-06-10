from google.adk.agents import Agent
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
# This file defines the agent card for the RAG Agent

retrieve_skill = AgentSkill(
    id="retrieve_documents",
    name="Retrieve Documents",
    description="Retrieves relevant documents or passages from a knowledge base.",
    tags=["rag", "retrieve", "search"],
    examples=["Find info about Dragon Slayer sword.", "Retrieve docs on Aincrad history."],
)

answer_with_context_skill = AgentSkill(
    id="answer_with_context",
    name="Answer With Context",
    description="Answers a question using retrieved context with citations.",
    tags=["rag", "answer", "qa"],
    examples=["Using sources, explain who Kirito is.", "Answer: What is the Town of Beginnings?"],
)

agent_card = AgentCard(
    id="rag_agent",
    name="RAG Agent",
    description="An agent that performs retrieval-augmented generation over a knowledge base.",
    url="http://localhost:8001/Agent/rag_agent",
    version="1.0.0",
    defaultInputModes=["text", "text/plain"],
    defaultOutputModes=["text", "text/plain"],
    capabilities=AgentCapabilities(streaming=True, pushNotifications=True),
    skills=[retrieve_skill, answer_with_context_skill],
)
