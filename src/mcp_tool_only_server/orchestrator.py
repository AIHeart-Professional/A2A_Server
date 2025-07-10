from xmlrpc import client
import httpx

async def handle_orchestrator(request: dict, details: dict):
    """
    Sends the request and details to the orchestrator API.
    Args:
        request (dict): The main request data.
        details (dict): Additional details to send.
    Returns:
        dict: The response from the orchestrator API.
    """
    orchestrator_api_url = "http://localhost:8003/orchestrator"  # Update with actual orchestrator API endpoint
    async with httpx.AsyncClient() as client:
        response = await client.post(orchestrator_api_url, json={"request": request, "details": details})
        response.raise_for_status()
        return response.json()