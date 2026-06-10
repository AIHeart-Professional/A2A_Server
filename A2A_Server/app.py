import sys
import logging
import asyncio
import os
import yaml
import importlib.util
from cache.cache import cache
from pathlib import Path

async def get_agent_card_info() -> dict:
    """
    API endpoint to retrieve agent card information.
    Args:
        request (dict): The incoming request data.
    """
    agent_cards_list = []
    agents_dir = Path(__file__).parent.parent / 'Agents'
    for agent_dir in agents_dir.iterdir():
        if agent_dir.is_dir() and not agent_dir.name.startswith('__'):
            agent_card_path = agent_dir / 'agent_card.py'
            if agent_card_path.exists():
                try:
                    # Construct a module name like Agents.character_agent.agent_card
                    module_name = f"Agents.{agent_dir.name}.agent_card"
                    spec = importlib.util.spec_from_file_location(module_name, agent_card_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        # Add parent directory to sys.path to handle relative imports within the agent card
                        # This is important if agent_card.py imports other things from the agent's folder
                        if str(agents_dir.parent) not in sys.path:
                            sys.path.insert(0, str(agents_dir.parent))
                        spec.loader.exec_module(module)
                        if hasattr(module, 'agent_card'):
                            card = getattr(module, 'agent_card')
                            # Assuming the card object is Pydantic or has a .dict() method
                            agent_cards_list.append(card.dict())
                        else:
                            logging.warning(f"'agent_card' not found in {agent_card_path}")
                except Exception as e:
                    logging.error(f"Error loading agent card from {agent_card_path}: {e}")
    return agent_cards_list

async def instructions() -> dict:
    """
    API endpoint to retrieve instructions for using the agent cards.
    """
    with open("static/instructions/instructions.yaml", "r") as f:
        instructions = yaml.safe_load(f)
    return instructions