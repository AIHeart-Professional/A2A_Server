from .intent import handle_intent, handle_intent_details
from .plans import handle_plan
from .orchestrator import handle_orchestrator
from .validation import validate_request
async def execute_request(request: dict) -> dict:
    """
    Orchestrates the MCP workflow: determines intent, then executes a plan.
    Args:
        user_query (dict): Contains 'id' and 'request' fields.
    Returns:
        dict: The result of the plan execution.
    """
    # Step 0: Validate the request
    user_query = await validate_request(request)
    if "error" in user_query:
        return user_query
    # Step 1: Determine intent and set user fields
    intent = await handle_intent(user_query)
    # Step 2: Interpret users provided information into intent fields
    intent = await handle_intent_details(intent, user_query)
    # Step 2: Execute plan based on intent
    plans = await handle_plan(intent, user_query)
    # Step 3: Call orchestrator with plans and user query
    result = await handle_orchestrator(plans, intent)
    return result
