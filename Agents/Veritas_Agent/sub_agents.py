from google.adk.agents import Agent
from ..delegation_tools import discover_available_agents, delegate_to_agent, call_specific_agent

agent_delegator_sub_agent = Agent(
    name="agent_delegator_sub_agent",
    model="gemini-2.0-flash",
    description="Agent that delegates tasks to other A2A agents in the system.",
    instruction="""You are a task delegation specialist. When given a user request, you MUST immediately delegate it using delegate_to_agent().
DO NOT just discover agents - you must actually delegate the task!
For any user request:
1. Call delegate_to_agent(task_description="[user request]") immediately
2. Return the result from the delegated agent
Example: If user says "I want to go fishing", call delegate_to_agent(task_description="I want to go fishing")
Always complete the delegation and return the agent's response.""",
    tools=[discover_available_agents, delegate_to_agent, call_specific_agent]
)