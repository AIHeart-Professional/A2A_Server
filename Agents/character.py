import importlib
import json
import logging
from tools import character_tools
logging.basicConfig(level=logging.INFO)

async def run_agent(action: str, fields: dict) -> dict:
    """
    Call the specific tool requested and get the results.
    """
    logging.info(f"Character Agent: Performing action: {action} with fields: {fields}")
    try:
        # Call the character_tools who's name matches the action
        tool_function = getattr(character_tools, action, None)
        if tool_function:
            return await tool_function(**fields)
        else:
            logging.error(f"Tool function not found for action: {action}")
            return {"error": f"Tool function not found for action: {action}"}
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"error": f"An error occurred: {e}"}
