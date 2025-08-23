import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os
from pymongo import MongoClient
from bson import ObjectId
import logging
from config.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "Veritas"

def create_character_tool(
    server_id: str,
    player_id: str, 
    character_name: str,
    character_class: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    cursor_color: Optional[str] = None,
    height: Optional[str] = None,
    physique: Optional[str] = None,
    age: Optional[int] = None,
    birthday: Optional[str] = None,
    bio: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new character with the specified schema and insert into MongoDB.
    
    Required fields:
    - server_id: UUID string for the server
    - player_id: UUID string for the player
    - character_name: Name of the character
    - character_class: Class of the character (e.g., 'warrior', 'mage', etc.)
    
    Optional fields:
    - first_name, last_name, cursor_color, height, physique, age, birthday, bio
    
    Returns:
    - Dict with success status and character ID or error message
    """
    client = None
    try:
        # Validate UUIDs
        try:
            uuid.UUID(server_id)
            uuid.UUID(player_id)
        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid UUID format: {str(e)}"
            }
        
        # Create database connection
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        characters_collection = db.characters
        
        # Check if character name already exists on this server
        existing_character = characters_collection.find_one({
            "characters_name": character_name, 
            "player.server_id": server_id
        })
        
        if existing_character:
            return {
                "success": False,
                "error": f"Character name '{character_name}' already exists on this server"
            }
        
        # Create character document following the specified schema
        character_doc = {
            "character": {
                "first_name": first_name or "",
                "last_name": last_name or "",
                "characters_name": character_name,
                "class_name": character_class,
                "cursor_color": cursor_color,
                "height": height,
                "physique": physique,
                "age": age,
                "birthday": {
                    "date": birthday
                },
                "bio": bio,
                "level": 1,
                "experience": 0,
                "experience_to_next_level": 100
            },
            "inventory": {
                "equipment": [],
                "consumables": [],
                "misc": [],
                "cratable": [],
                "key_items": [],
                "currency": 0
            },
            "equipped": {
                "head": None,
                "chest": None,
                "legs": None,
                "arms": None,
                "accessory1": None,
                "accessory2": None,
                "left_hand": None,
                "right_hand": None
            },
            "group": {
                "guild": None,
                "party": None
            },
            "stats": {
                "hp": 100,
                "str": 5,
                "def": 5,
                "spe": 5,
                "dex": 5,
                "cha": 5,
                "points_to_distribute": 0
            },
            "combat": {
                "status_ailment": None,
                "battle_status": False,
                "damage": 5,
                "defense": 5,
                "current_hp": 100
            },
            "player": {
                "player_id": player_id,
                "server_id": server_id,
                "active": True
            },
            "created_at": datetime.utcnow()
        }
        has_active = _has_active_character_assistant_function(player_id, server_id)
        if has_active:
            character_doc["player"]["active"] = False
        # Insert character into MongoDB
        result = characters_collection.insert_one(character_doc)
        character_id = str(result.inserted_id)
        
        return {
            "success": True,
            "message": f"Character '{character_name}' created successfully",
            "character_id": character_id,
            "character_name": character_name,
            "class_name": character_class,
            "level": 1,
            "server_id": server_id,
            "player_id": player_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create character: {str(e)}"
        }
    finally:
        if client:
            client.close()

def update_character_tool(request: dict):
    # Call the database to find if a players player_id and server_id have a character where active is true
    return True
        
        
def get_character_tool(
    player_id: str,
    server_id: str,
    character_name: Optional[str] = None,
    character_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve a character record from MongoDB.
    
    Required fields:
    - player_id: UUID string for the player
    - server_id: UUID string for the server
    
    Optional fields (at least one must be provided):
    - character_name: Name of the character to retrieve
    - character_id: MongoDB ObjectId of the character
    
    Returns:
    - Dict with success status and character data or error message
    """
    client = None
    try:
        # Validate UUIDs
        try:
            uuid.UUID(server_id)
            uuid.UUID(player_id)
        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid UUID format: {str(e)}"
            }
        
        # Validate that at least one identifier is provided
        if not character_name and not character_id:
            return {
                "success": False,
                "error": "Either character_name or character_id must be provided"
            }
        
        # Create database connection
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        characters_collection = db.characters
        
        # Build query based on provided parameters
        query = {
            "player.player_id": player_id,
            "player.server_id": server_id
        }
        
        if character_id:
            try:
                query["_id"] = ObjectId(character_id)
            except Exception:
                return {
                    "success": False,
                    "error": "Invalid character_id format"
                }
        elif character_name:
            query["character.characters_name"] = character_name
        
        # Find the character
        character = characters_collection.find_one(query)
        
        if not character:
            identifier = character_id if character_id else character_name
            return {
                "success": False,
                "error": f"Character not found: {identifier}"
            }
        
        # Convert ObjectId to string for JSON serialization
        character["_id"] = str(character["_id"])
        
        return {
            "success": True,
            "character": character
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to retrieve character: {str(e)}"
        }
    finally:
        if client:
            client.close()


def update_character_tool(
    request: dict,
    character_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update a character record based on structured request input.
    
    Required fields:
    - request: Dictionary containing field and value to update
      Example: {"field": "age", "value": 25} or {"field": "character.first_name", "value": "John"}
    - character_data: Character record dictionary (from get_character_tool)
    
    Returns:
    - Dict with success status and update details or error message
    """
    client = None
    try:
        # Validate character data
        if not character_data or "_id" not in character_data:
            return {
                "success": False,
                "error": "Invalid character data provided"
            }
        
        # Validate request structure
        if not isinstance(request, dict) or "field" not in request or "value" not in request:
            return {
                "success": False,
                "error": "Request must be a dictionary with 'field' and 'value' keys"
            }
        
        character_obj_id = ObjectId(character_data["_id"])
        field = request["field"]
        value = request["value"]
        
        # Map field names to their MongoDB paths
        field_mappings = {
            # Character basic info
            "first_name": "character.first_name",
            "last_name": "character.last_name", 
            "characters_name": "character.characters_name",
            "character_name": "character.characters_name",
            "name": "character.characters_name",
            "class_name": "character.class_name",
            "class": "character.class_name",
            "cursor_color": "character.cursor_color",
            "height": "character.height",
            "physique": "character.physique",
            "age": "character.age",
            "bio": "character.bio",
            "level": "character.level",
            "experience": "character.experience",
            "exp": "character.experience",
            "experience_to_next_level": "character.experience_to_next_level",
            
            # Stats
            "hp": "stats.hp",
            "str": "stats.str",
            "strength": "stats.str",
            "def": "stats.def",
            "defense": "stats.def",
            "spe": "stats.spe",
            "speed": "stats.spe",
            "dex": "stats.dex",
            "dexterity": "stats.dex",
            "cha": "stats.cha",
            "charisma": "stats.cha",
            "points_to_distribute": "stats.points_to_distribute",
            
            # Combat stats
            "damage": "combat.damage",
            "combat_defense": "combat.defense",
            "current_hp": "combat.current_hp",
            "status_ailment": "combat.status_ailment",
            "battle_status": "combat.battle_status",
            
            # Currency
            "currency": "inventory.currency",
            "money": "inventory.currency",
            "gold": "inventory.currency",
            
            # Special handling for birthday
            "birthday": "character.birthday.date",
            "birth_date": "character.birthday.date",
            
            # Player status
            "active": "player.active"
        }
        
        # Check if field exists in mapping or is already a valid MongoDB path
        if field in field_mappings:
            mongo_field = field_mappings[field]
        elif "." in field:
            # Assume it's already a valid MongoDB path (e.g., "character.first_name")
            mongo_field = field
        else:
            return {
                "success": False,
                "error": f"Unknown field: {field}. Available fields include: {', '.join(sorted(field_mappings.keys()))}"
            }
        
        # Validate value type for specific fields
        numeric_fields = [
            "character.age", "character.level", "character.experience", "character.experience_to_next_level",
            "stats.hp", "stats.str", "stats.def", "stats.spe", "stats.dex", "stats.cha", "stats.points_to_distribute",
            "combat.damage", "combat.defense", "combat.current_hp", "inventory.currency"
        ]
        
        boolean_fields = ["combat.battle_status", "player.active"]
        
        if mongo_field in numeric_fields:
            try:
                value = int(value)
            except (ValueError, TypeError):
                return {
                    "success": False,
                    "error": f"Field '{field}' requires a numeric value, got: {value}"
                }
        elif mongo_field in boolean_fields:
            if isinstance(value, str):
                value = value.lower() in ["true", "1", "yes", "on"]
            else:
                value = bool(value)
        
        updates = {mongo_field: value}
        
        # Perform the update
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        characters_collection = db.characters
        
        result = characters_collection.update_one(
            {"_id": character_obj_id},
            {"$set": updates}
        )
        
        if result.modified_count == 0:
            return {
                "success": False,
                "error": "No changes were made to the character"
            }
        
        # Get the updated character to return current state
        updated_character = characters_collection.find_one({"_id": character_obj_id})
        updated_character["_id"] = str(updated_character["_id"])
        
        return {
            "success": True,
            "message": f"Character updated successfully",
            "updates_made": updates,
            "character": updated_character
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update character: {str(e)}"
        }
    finally:
        if client:
            client.close()


def delete_character_tool(
    player_id: str,
    server_id: str,
    character_name: Optional[str] = None,
    character_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Delete a character record from MongoDB.
    
    Required fields:
    - player_id: UUID string for the player
    - server_id: UUID string for the server
    
    Optional fields (at least one must be provided):
    - character_name: Name of the character to delete
    - character_id: MongoDB ObjectId of the character
    
    Returns:
    - Dict with success status and deletion details or error message
    """
    client = None
    try:
        # Validate UUIDs
        try:
            uuid.UUID(server_id)
            uuid.UUID(player_id)
        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid UUID format: {str(e)}"
            }
        
        # Validate that at least one identifier is provided
        if not character_name and not character_id:
            logger.info("No character name or ID provided")
            return {
                "success": False,
                "error": "Either character_name or character_id must be provided"
            }
        
        # Create database connection
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        characters_collection = db.characters
        
        # Build query based on provided parameters
        query = {
            "character.characters_name": character_name,
            "player.player_id": player_id,
            "player.server_id": server_id
        }
                
        # Delete the character
        result = characters_collection.delete_one(query)
        logger.info("result: ", result)
        if result.deleted_count == 0:
            logger.info("Failed to delete character")
            return {
                "success": False,
                "error": "Failed to delete character"
            }
        
        logger.info("Character deleted successfully")
        return {
            "success": True,
            "message": f"Character '{character_name}' deleted successfully"
        }
        
    except Exception as e:
        logger.info(f"Failed to delete character: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to delete character: {str(e)}"
        }
    finally:
        if client:
            client.close()


def _has_active_character_assistant_function(player_id: str, server_id: str):
    # Call the database to find if a players player_id and server_id have a character where active is true
    client = None
    try:
        # Create database connection
        client = MongoClient(MONGO_URI) 
        db = client[DB_NAME]
        characters_collection = db.characters
        
        # Check if player has an active character on the server
        existing_character = characters_collection.find_one({
            "player.player_id": player_id,
            "player.server_id": server_id,
            "active": True
        })
        
        if existing_character:
            return True
        
    except Exception as e:
        return False
    finally:
        if client:
            client.close()

# Export the synchronous functions
__all__ = ["create_character_tool", "get_character_tool", "update_character_tool", "delete_character_tool"]
