import httpx

async def handle_intent(user_query: dict) -> dict:
    """
    Determines the intent by calling an external plans API.
    Args:
        user_query (dict): Contains 'id' and 'request' fields.
    Returns:
        dict: The intent as returned by the plans API.
    """
    plans_api_url = "http://localhost:8001/llm/intent"  # Update with actual plans API endpoint
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(plans_api_url, json={**user_query})
        response.raise_for_status()
        return response.json()

async def handle_intent_details(intent: dict, user_query: dict) -> dict:
    """
    Determines additional fields for the user based on the intent and user query.
    Args:
        intent (dict): The intent determined previously.
        user_query (dict): The original user query.
    Returns:
        dict: The updated intent with additional fields.
    """
    additional_fields_api_url = "http://localhost:8001/llm/set_fields"  # Update with actual API endpoint
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(additional_fields_api_url, json={**intent, **user_query})
        response.raise_for_status()
        # Add response data to the intent
        intent.update(response.json())
        return intent