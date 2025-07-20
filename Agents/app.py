import importlib
import json
import logging

logging.basicConfig(level=logging.INFO)

async def execute_agent(agent: str, action: str, fields: dict) -> dict:
    """
    Dynamically imports and calls the specified agent.
    """
    try:
        logging.info(f"Executing agent: {agent} with action: {action}")
        agent_module = importlib.import_module(f"Agents.{agent}")
        agent_response = await agent_module.run_agent(action, fields)
        return agent_response
    except ImportError as e:
        logging.error(f"Error importing agent: {e}")
        return { "error": f"Error importing agent: {e}" }
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return { "error": f"An error occurred: {e}" }
