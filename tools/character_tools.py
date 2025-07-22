import importlib
import json
import logging
import copy
import yaml
from .database_tools import Database

# TODO: Move these to a configuration file
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "Veritas"

db = Database(mongo_uri=MONGO_URI, db_name=DB_NAME)

logging.basicConfig(level=logging.INFO)

async def check_character_limit(fields: dict, context: dict) -> dict:
    """
    Check if the character limit is exceeded for max number of characters on a server.
    """
    server_id = fields.get("server_id")
    user_id = fields.get("user_id")
    logging.info(f"Character Tool: Checking character limit for server: {server_id}, user: {user_id}")
    query = {"server_id": server_id, "user_id": user_id}
    characters = db.read_many("characters", query)
    if not characters:
        return {"success": "No characters found for this user on this server.", "characters": []}    
    # TODO: Define a maximum character limit for universal servers
    elif len(characters) >= 5:  # Assuming 5 is the max character limit
        return {"error": "Character limit exceeded for this user on this server."}    
    return {"success": f"Found {len(characters)} characters.", "characters": characters}

async def check_for_active_character(fields: dict, context: dict) -> dict:
    """
    Check if there is an active character for a user on a server.
    """
    server_id = fields.get("server_id")
    user_id = fields.get("user_id")
    logging.info(f"Character Tool: Checking for active character for server: {server_id}, user: {user_id}")
    query = {"server_id": server_id, "user_id": user_id}
    active_character = db.read_one("active_characters", query)
    if not active_character:
        return {"success": "No active character found for this user on this server.", "active_character_exists": False}
    return {"success": "Active character retrieved", "character_id": active_character.get("character_id"), "active_character_exists": True}

async def get_current_character(fields: dict, context: dict) -> dict:
    """
    Get the active character for a user on a server.
    """
    server_id = fields.get("server_id")
    user_id = fields.get("user_id")
    logging.info(f"Character Tool: Getting the current character for server: {server_id}, user: {user_id}")
    query = {"server_id": server_id, "user_id": user_id}
    active_character = db.read_one("active_characters", query)
    if not active_character:
        return {"error": "No active character found for this user on this server."}
    return {"success": "Active character retrieved", "character": active_character}

async def get_player_character(fields: dict, context: dict) -> dict:
    """
    Get a characters information from the database.
    """
    logging.info(f"Character Tool: Getting the current player's character for server: {server_id}, user: {user_id}")
    server_id = fields.get("server_id")
    user_id = fields.get("user_id")
    query = {"server_id": server_id, "user_id": user_id}
    active_character = db.read_one("active_characters", query)
    if not active_character:
        return {"error": "No active character found for this user on this server."}
    return {"success": "Active character retrieved", "character": active_character}

async def create_character(fields: dict, context: dict) -> dict:
    """
    Create a new character using a template, with active status logic.
    """
    # Load the character structure from the YAML file just in time
    with open('static/field_structures.yaml', 'r') as file:
        character_template = yaml.safe_load(file)['character_structure']

    user_id = fields.get("user_id")
    server_id = fields.get("server_id")

    # Populate character details
    char_details = character_template["character"]
    for key in char_details:
        if key in fields:
            char_details[key] = fields[key]

    # Populate player details
    player_details = character_template["player"]
    player_details["user_id"] = user_id
    player_details["server_id"] = server_id
    if(context.get("check_for_active_character")[0].get("active_character_exists")):
        player_details["active"] = False
    else:
        player_details["active"] = True

    # 3. Create the character in the database
    try:
        new_char_id = db.create("characters", player_details)
        logging.info(f"Character Tool: Created character with ID: {new_char_id}")
        return {"success": "Character created successfully!"}
    except Exception as e:
        logging.error(f"Error creating character in database: {e}")
        return {"error": f"Failed to create character: {e}"}