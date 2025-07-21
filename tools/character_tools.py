import importlib
import json
import logging

logging.basicConfig(level=logging.INFO)

async def check_character_limit(fields: dict, context: dict) -> dict:
    """
    Check if the character limit is exceeded for max number of characters on a server.
    """
    server_id = fields.get("server_id")
    user_id = fields.get("user_id")
    logging.info(f"Character Tool: Checking character limit for server: {server_id}, user: {user_id}")
    return {"success": "Character limit not exceeded"}

async def get_active_character(fields: dict, context: dict) -> dict:
    """
    Get the active character for a user on a server.
    """
    server_id = fields.get("server_id")
    user_id = fields.get("user_id")
    logging.info(f"Character Tool: Getting active character for server: {server_id}, user: {user_id}")
    return {"success": "Active character retrieved", "character_id": "char_123"}

async def create_character(fields: dict, context: dict) -> dict:
    """
    Create a new character for a user on a server.
    """
    logging.info(f"Character Tool: Creating character with details: {fields}")
    character_id = context.get("character_id")
    if character_id:
        logging.info(f"Context check: Found character_id {character_id} in context.")
    return {"success": "Character created"}