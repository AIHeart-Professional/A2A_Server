from typing import Dict, Any, Optional
from tools.database_tools import Database
import uuid
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_item_tool(
    item: dict,
    ) -> dict:
    """Creates a new item in the Veritas database.
    
    Args:
        item: Dict containing item information
        server_id: Discord server/guild ID (required)
        character_id: ID of character who owns the item (optional)
        item_type: Category of item (weapon, armor, consumable, etc.)
        rarity: Item rarity (common, uncommon, rare, legendary, etc.)
        inventory_id: ID of inventory if separate from character
        description: Text description of the item
        flavor_text: Optional lore/flavor text
        quantity: Stack amount
        value: Currency worth
        weight: Weight if game uses carry limits
        durability: Dict with current and max durability
        effects: Dict describing item effects
        requirements: Dict describing usage requirements
        source: Where item came from (drop, shop, quest, crafted)
        recipe: Dict of required ingredients if craftable
        tradeable: Whether item can be traded/sold
        consumable: Whether item disappears on use
        equipped: Whether item is currently equipped
    
    Returns:
        Dict with the created item ID or error message
    """
    try:
        # Initialize database connection
        db = Database(mongo_uri="mongodb://localhost:27017/", db_name="veritas")
        
        # Generate unique item ID
        item_id = str(uuid.uuid4())
        
        # Set timestamps
        current_time = datetime.utcnow().isoformat()
        
        # Set default values for optional dictionary fields
        if durability is None:
            durability = {"current": 100, "max": 100}
        
        if effects is None:
            effects = {}
            
        if requirements is None:
            requirements = {}
            
        if recipe is None:
            recipe = {}
        
        # Create item document
        item_document = {
            "item_id": item_id,
            "item_name": item["item_name"],
            "item_type": item["item_type"],
            "rarity": item["rarity"],
            "server_id": item["server_id"],
            "character_id": item["character_id"],
            "inventory_id": item["inventory_id"],
            "description": item["description"],
            "flavor_text": item["flavor_text"],
            "quantity": item["quantity"],
            "value": item["value"],
            "weight": item["weight"],
            "durability": item["durability"],
            "effects": item["effects"],
            "requirements": item["requirements"],
            "created_at": current_time,
            "acquired_at": current_time,
            "equipped": item["equipped"],
            "tradeable": item["tradeable"],
            "consumable": item["consumable"],
            "source": item["source"],
            "recipe": item["recipe"]
        }
        
        # Insert item into database
        result = await db.create("items", item_document)
        
        # Close database connection
        await db.close()
        
        return {"message": f"Item created successfully with ID: {item_id}"}
    
    except Exception as e:
        return {"error": f"Error creating item: {str(e)}"}

async def read_item_tool(item: dict) -> dict:
    """Reads an item from the Veritas database by name (case-insensitive).
    
    Args:
        item: Dict containing search parameters, must include either item_name or item_id
        
    Returns:
        Dict with the found item or error message
    """
    try:
        # Initialize database connection
        db = Database(mongo_uri="mongodb://localhost:27017/", db_name="veritas")
        
        # Build query based on provided parameters
        query = {}
        logger.info(f"item information: {item}")
        if "item_name" in item and item["item_name"]:
            query["item_name"] = item["item_name"]
        logger.info(f"query: {query}")
        result = await db.read_one("items", query)
        
        # Close database connection
        await db.close()
        
        if result:
            return {"item": result}
        else:
            return {"error": "Item not found"}
    
    except Exception as e:
        return {"error": f"Error reading item: {str(e)}"}

def update_item_tool() -> str:
    # Call your MCP tool or DB logic here
    return "successfully called update_item tool"

def delete_item_tool() -> str:
    # Call your MCP tool or DB logic here
    return "successfully called delete_item tool"
    