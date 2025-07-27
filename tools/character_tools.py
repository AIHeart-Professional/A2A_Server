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
    characters = db.read_many("characters", query)
    # No characters found for player
    if not characters:
        return {"success": "No characters found for this user on this server.", "characters": []}    
    # TODO: Define a maximum character limit for universal servers
    # Character limit reached for player
    elif len(characters) >= 5:  # Assuming 5 is the max character limit
        return {"error": "Character limit exceeded for this user on this server."}    
    # Character limit not reached for player
    return {"success": f"Found {len(characters)} characters.", "characters": characters}

# Check if the character name is available for a new character
async def character_name_available(fields: dict, context: dict) -> dict:
    """
    Check if the character name is available for a new character.
    """
    server_id = fields.get("server_id")
    character_name = fields.get("character_name")
    character_tag = fields.get("character_tag")
    logging.info(f"Character Tool: Checking character name availability for server: {server_id}, character: {character_name}")
    query = {"player.server_id": server_id, "character.characters_name": character_name, "character.characters_tag": character_tag}
    characters = db.read_many("characters", query)
    # No characters found with the same name
    if not characters:
        return {"success": "Character name is available.", "character_name_available": True}    
    # Character name already exists
    return {"error": f"Character name '{character_name}' is already taken on this server.", "character_name_available": False}

# Get the character document for the specified character from the database
async def get_character(fields: dict, context: dict) -> dict:
    """
    Dynamically gets character(s) from the database based on provided fields.
    Possible fields: server_id, user_id, character_name, active.
    """
    query = {}
    
    # Map API-friendly names to database field names from the character structure
    # Get server
    if "server_id" in fields:
        query["player.server_id"] = fields["server_id"]
    # get active character for player
    if "user_id" in fields and "active" in fields:
        query["player.user_id"] = fields["user_id"]
        query["player.active"] = fields["active"]
        logging.info(f"Character Tool: Getting currently active character: {query}")
    # get other characters
    if "character_name" in fields and "character_tag" in fields:
        query["character.characters_name"] = fields["character_name"]
        query["character.characters_tag"] = fields["character_tag"]
        logging.info(f"Character Tool: Getting other players character: {query}")
    # If required fields are missing, return an error
    if not query:
        return {"error": "At least one field (server_id, user_id, character_name, active) is required."}
    # Call database to get character document
    try:
        character = db.read_one("characters", query)
        if not character:
            return {"error": "No character found matching the criteria."}
        return {"success": f"Found character on server {fields['server_id']}", "characters": character}
    except Exception as e:
        logging.error(f"Error retrieving character from database: {e}")
        return {"error": f"Failed to retrieve character: {e}"}

# Create a new character using a template
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
    for key in character_template["character"]:
        if key in fields:
            character_template["character"][key] = fields[key]
    # Populate player details
    character_template["player"]["server_id"] = server_id
    character_template["player"]["user_id"] = user_id
    if(context.get("character_name_available")[0].get("character_name_available")):
            character_template["player"]["active"] = False
    else:
        character_template["player"]["active"] = True
    # 3. Create the character in the database
    try:
        new_char_id = db.create("characters", character_template)
        logging.info(f"Character Tool: Created character with ID: {new_char_id}")
        return {"success": "Character created successfully!"}
    except Exception as e:
        logging.error(f"Error creating character in database: {e}")
        return {"error": f"Failed to create character: {e}"}
    
# Update an existing character
async def update_character(fields: dict, context: dict) -> dict:
    """
    Update an existing character in the database.
    """
    # Set character_data from get_character context
    character_data = context.get("get_character", [{}])[0]
    # Convert character_id to ObjectId
    character_id = ObjectId(character_data.get("characters", {}).get("_id"))
    if not character_data:
        return {"error": "No character data found in context."}
    # Update character_data with matching fields inside all top-level keys
    character_document = character_data.get('characters', {})
    new_character_data = copy.deepcopy(character_document)

    for section_key, section_value in new_character_data.items():
        if isinstance(section_value, dict):
            for field_key, field_value in fields.items():
                if field_key in section_value:
                    new_character_data[section_key][field_key] = field_value
    
    # Remove the immutable _id field before updating
    if '_id' in new_character_data:
        del new_character_data['_id']

    # Call database to update character document
    try:
        # Use the MongoDB record _id and set the character object to new_character_data
        modified_count = db.update_one(
            "characters",  # Collection name
            {"_id": character_id},  # Query to find the document
            new_character_data  # Update data (without $set)
        )        
        if modified_count > 0:
            logging.info(f"Character Tool: Updated character with ID: {character_id}")
            return {"success": "Character updated successfully!"}
        else:
            return {"error": "No character found with the provided ID."}
    except Exception as e:
        logging.error(f"Error updating character in database: {e}")
        return {"error": f"Failed to update character: {e}"}
    
# Delete a character
async def delete_character(fields: dict, context: dict) -> dict:
    """
    Delete a character from the database.
    """
    # Set character_data from get_character context
    character_data = context.get("get_character", [{}])[0]
    character_id = ObjectId(character_data.get("characters", {}).get("_id"))
    if not character_id:
        return {"error": "No character id found in context."}
    # Call database to delete character document
    try:
        deleted_count = db.delete_one("characters", {"_id": character_id})
        if deleted_count > 0:
            logging.info(f"Character Tool: Deleted character with ID: {character_id}")
            return {"success": "Character deleted successfully!"}
        else:
            return {"error": "No character found with the provided ID."}
    except Exception as e:
        logging.error(f"Error deleting character from database: {e}")
        return {"error": f"Failed to delete character: {e}"}
    
