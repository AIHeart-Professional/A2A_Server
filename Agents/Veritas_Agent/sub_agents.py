from google.adk.agents import Agent
from .delegation_tools import discover_available_agents, delegate_to_agent, call_specific_agent

agent_delegator_sub_agent = Agent(
    name="agent_delegator_sub_agent",
    model="gemini-2.0-flash",
    description="Agent that delegates tasks to other A2A agents in the system.",
    instruction="You are a task delegation specialist. When given a user request, you MUST:",
    tools=[discover_available_agents, delegate_to_agent, call_specific_agent]
)