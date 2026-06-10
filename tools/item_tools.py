import importlib
import json
import logging
import copy
import yaml
from .database_tools import Database
from bson import ObjectId  # Import ObjectId for MongoDB queries

# TODO: Move these to a configuration file
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "Veritas"

db = Database(mongo_uri=MONGO_URI, db_name=DB_NAME)

logging.basicConfig(level=logging.INFO)

# Check if the character limit is exceeded for max number of characters created per player on a server
async def check_character_limit(fields: dict, context: dict) -> dict:
    """
    Check if the character limit is exceeded for max number of characters on a server.
    """
    server_id = fields.get("server_id")
    user_id = fields.get("user_id")
    logging.info(f"Character Tool: Checking character limit for server: {server_id}, user: {user_id}")
    query = {"server_id": server_id, "user_id": user_id}
    characters = await db.read_many("characters", query)
    # No characters found for player
    if not characters:
        return {"success": "No characters found for this user on this server.", "characters": []}    
    # TODO: Define a maximum character limit for universal servers
    # Character limit reached for player
    elif len(characters) >= 5:  # Assuming 5 is the max character limit
        return {"error": "Character limit exceeded for this user on this server."}    
    # Character limit not reached for player
    return {"success": f"Found {len(characters)} characters.", "characters": characters}
