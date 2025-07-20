from .intent import handle_intent, handle_intent_details
from .plans import handle_plan
from .orchestrator import handle_orchestrator
from .validation import validate_request
from cache.cache import cache
import logging
import asyncio
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

async def get_tools() -> str:
    """
    Returns the entire tools.yaml file as a string.
    """
    with open('static/tools.yaml', 'r', encoding='utf-8') as f:
        tools_str = f.read()
    return tools_str