import importlib
import json
import logging

logging.basicConfig(level=logging.INFO)

async def check_character_limit(server_id: str, user_id: str) -> dict:
    """
    Check if the character limit is exceeded for max number of characters on a server.
    """
    logging.info(f"Character Tool: Checking character limit for server: {server_id}, user: {user_id}")
    return {"success": "Character limit not exceeded"}

async def get_active_character(server_id: str, user_id: str) -> dict:
    """
    Get the active character for a user on a server.
    """
    logging.info(f"Character Tool: Getting active character for server: {server_id}, user: {user_id}")
    return {"success": "Active character retrieved"}

async def create_character(details: dict) -> dict:
    """
    Create a new character for a user on a server.
    """
    logging.info(f"Character Tool: Creating character with details: {details}")
    return {"success": "Character created"}