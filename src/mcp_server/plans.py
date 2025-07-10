import httpx
import json

async def handle_plan(intent: dict, user_query: dict) -> dict:
    """
    Executes a plan by calling an external plans API.
    Args:
        intent (dict): The intent determined previously.
        user_query (dict): The original user query.
    Returns:
        dict: The result of the plan execution as returned by the plans API.
    """
    plans_api_url = "http://localhost:8002/planner"  # Update with actual plans API endpoint
    
    # The intent from the previous call is a dictionary containing a JSON string.
    # We need to extract the string and parse it.
    intent_str = intent.get('intent', '{}')

    params = {
        "intent": intent_str, # Pass the string directly
        "user_query": json.dumps(user_query)
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(plans_api_url, params=params)
        response.raise_for_status()
        return response.json()
