import yaml
from pathlib import Path
from LLM.llm_service import handle_LLM_request, handle_LLM_response
from LLM.utils import get_agent_card_name_and_description

async def agent_to_use(request: dict) -> dict:
    """
    Determines which agents to use based on the user query and intents.
    Args:
        request (dict): The main request data.
    Returns:
        dict: A list of agents to use.
    """
    # Step 0: Validate the request (placeholder, implement as needed)
    user_query = request["request"]
    agent_cards = request.get("agent_cards", [])
    if not user_query:
        raise ValueError("User query is required.")
    if not agent_cards:
        raise ValueError("Agent cards are required.")
    # Step 1: Obtain agent name and descriptions
    abridged_agent_cards = await get_agent_card_name_and_description(agent_cards)
    # Step 2: Get the desired instructions
    instructions = await _get_instructions("agents_to_use")
    # Step 3: Call the LLM service to get the agents
    result = await handle_LLM_request(user_query, abridged_agent_cards, instructions)
    return result

async def _get_instructions(request: str) -> dict:
    """
    Retrieves instructions from instruction yaml.
    Args:
        request (str): The request string.
    Returns:
        dict: The instructions for using the agent cards.
    """
    instructions_path = Path(__file__).parent.parent / "static" / "instructions" / "instructions.yaml"
    with open(instructions_path, "r", encoding="utf-8") as f:
        all_instructions = yaml.safe_load(f)
    # Return only the instruction that matches the request string
    return all_instructions.get(request, {})