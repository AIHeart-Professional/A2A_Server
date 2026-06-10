from google.adk.agents import Agent

action_parser_sub_agent = Agent(
    name="action_parser_sub_agent",
    model="gemini-1.5-flash",
    description="Agent designed to parse actions for a roleplaying game.",
    instruction="You are an expert at parsing actions for a roleplaying game.",
    tools=[]
)

tactics_planner_sub_agent = Agent(
    name="tactics_planner_sub_agent",
    model="gemini-1.5-flash",
    description="Agent designed to plan tactics for a roleplaying game.",
    instruction="You are an expert at planning tactics for a roleplaying game.",
    tools=[]
)

taget_selector_sub_agent = Agent(
    name="target_selector_sub_agent",
    model="gemini-1.5-flash",
    description="Agent designed to select targets for a roleplaying game.",
    instruction="You are an expert at selecting targets for a roleplaying game.",
    tools=[]
)

narrative_writer_sub_agent = Agent(
    name="narrative_writer_sub_agent",
    model="gemini-1.5-flash",
    description="Agent designed to write narratives for a roleplaying game.",
    instruction="You are an expert at writing narratives for a roleplaying game.",
    tools=[]
)

summary_writer_sub_agent = Agent(
    name="summary_writer_sub_agent",
    model="gemini-1.5-flash",
    description="Agent designed to write summaries for a roleplaying game.",
    instruction="You are an expert at writing summaries for a roleplaying game.",
    tools=[]
)