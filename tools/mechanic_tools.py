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
    return {"success": "Character limit check not implemented for mechanics."}