from .intent import handle_intent, handle_intent_details
from .plans import handle_plan
from .orchestrator import handle_orchestrator
from .validation import validate_request
from cache.cache import cache
import logging
import asyncio
import os
import yaml

async def execute_request(request: dict) -> dict:
    """
    Orchestrates the MCP workflow: validates, gets intent, gets plan (from cache or API), and orchestrates.
    Args:
        request (dict): The incoming request data.
    Returns:
        dict: The result of the plan execution.
    """
    # Step 0: Validate the request
    valid_request = await validate_request(request)
    if not valid_request:
        logging.warning("Invalid request format or missing fields.")
        return {"error": "Invalid request format or missing fields."}

    # Step 1: Determine intent
    intent = await handle_intent(request)

    #TODO: Remove this check
    if intent.get("intent:") == "clear_cache":
        # Clear the cache if the intent is to clear it
        cache.clear()
        return {"message": "Cache cleared successfully."}    
    # Use the intent string (e.g., "create_character") as the cache key
    intent_key = intent.get("intent")
    if not intent_key:
        return {"error": "Could not determine intent from response."}

    # Step 2: Start getting details for the intent (async task)
    intent_details_task = asyncio.create_task(handle_intent_details(intent, request))

    # Step 3: Start getting the plan (async task, using cache if available)
    logging.info("Checking cache for intent: %s", intent_key)
    if intent_key in cache:
        plan_task = asyncio.create_task(asyncio.sleep(0, result=cache[intent_key]))
    else:
        # Wait for intent_details_task to finish before calling handle_plan
        async def get_plan():
            formatted_request = await intent_details_task
            return await handle_plan(formatted_request, request)
        plan_task = asyncio.create_task(get_plan())

    # Wait for both tasks to complete
    formatted_request = await intent_details_task
    formatted_request = {**formatted_request, **request}  # Merge user query into formatted request
    plans = await plan_task

    # If plan was not cached, cache it now
    if intent_key not in cache:
        cache[intent_key] = plans

    # Step 4: Call orchestrator with the static plan and the specific user details
    result = await handle_orchestrator(plans, formatted_request)
    
    return result

async def get_tools(agents: dict, tools: dict) -> dict:
    """
    For each agent, loads its YAML and checks if the specified tools exist.
    Returns a dict mapping agent names to the tools found.
    """
    base_dir = "static"
    result = {}
    tool_names = list(tools.values()) # Get the list of tool names

    for agent in agents.values(): # Iterate over the agent names (values of the dict)
        agent_yaml_path = os.path.join(base_dir, agent, f"{agent}.yaml")
        if not os.path.exists(agent_yaml_path):
            result[agent] = {"error": f"YAML file not found: {agent_yaml_path}"}
            continue

        with open(agent_yaml_path, "r", encoding="utf-8") as f:
            agent_yaml = yaml.safe_load(f)

        # Tools are nested under a 'tools' key in the YAML
        tools_dict = agent_yaml.get('tools', {}) if isinstance(agent_yaml, dict) else {}
        available_tools = tools_dict.keys() if isinstance(tools_dict, dict) else []

        # Collect the definitions of found tools
        found_tool_definitions = {}
        for tool_name in tool_names:
            if tool_name in available_tools:
                found_tool_definitions[tool_name] = tools_dict[tool_name]

        missing_tools = [tool for tool in tool_names if tool not in found_tool_definitions]

        # Format the found tools as a YAML string
        found_tools_yaml_str = ""
        if found_tool_definitions:
            # The `allow_unicode=True` preserves the format, and indent adds readability
            found_tools_yaml_str = yaml.dump(found_tool_definitions, allow_unicode=True, indent=2)

        result[agent] = {
            "found_tools": found_tools_yaml_str,
            "missing_tools": missing_tools
        }

    return result

async def get_intents() -> str:
    """
    Returns the entire intents.yaml file as a string.
    """
    with open('static/intents.yaml', 'r', encoding='utf-8') as f:
        intents_str = f.read()
    return intents_str