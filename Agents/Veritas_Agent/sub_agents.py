from google.adk.agents import Agent

agent_delegator_sub_agent = Agent(
    name="agent_delegator_sub_agent",
    model="gemini-2.0-flash",
    description="You are only meant to delegate tasks to other agents."
)
    