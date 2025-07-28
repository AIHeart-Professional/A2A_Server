from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import Dict, Any, List, Optional
import asyncio

class Database:
    """A universal MongoDB database tool for CRUD operations."""

    def __init__(self, mongo_uri: str, db_name: str):
        """Initializes the database connection."""
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]

    def _serialize_doc(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Converts MongoDB's ObjectId to a string for JSON compatibility."""
        if doc and '_id' in doc:
            doc['_id'] = str(doc['_id'])
        return doc

    async def create(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Creates a single document in a collection."""
        result = await self.db[collection_name].insert_one(document)
        return str(result.inserted_id)

    async def create_many(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
        """Creates multiple documents in a collection."""
        result = await self.db[collection_name].insert_many(documents)
        return [str(id) for id in result.inserted_ids]

    async def read_one(self, collection_name: str, query: Dict[str, Any], projection: Optional[Dict[str, int]] = None) -> Optional[Dict[str, Any]]:
        """Reads a single document from a collection, with optional projection."""
        document = await self.db[collection_name].find_one(query, projection)
        return self._serialize_doc(document)

    async def read_many(self, collection_name: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Reads multiple documents from a collection."""
        cursor = self.db[collection_name].find(query)
        docs = []
        async for doc in cursor:
            docs.append(self._serialize_doc(doc))
        return docs

    async def update_one(self, collection_name: str, query: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """Updates a single document in a collection."""
        result = await self.db[collection_name].update_one(query, {'$set': update_data})
        return result.modified_count

    async def update_many(self, collection_name: str, query: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """Updates multiple documents in a collection."""
        result = await self.db[collection_name].update_many(query, {'$set': update_data})
        return result.modified_count

    async def delete_one(self, collection_name: str, query: Dict[str, Any]) -> int:
        """Deletes a single document from a collection."""
        result = await self.db[collection_name].delete_one(query)
        return result.deleted_count

    async def delete_many(self, collection_name: str, query: Dict[str, Any]) -> int:
        """Deletes multiple documents from a collection."""
        result = await self.db[collection_name].delete_many(query)
        return result.deleted_count

    async def close(self):
        """Closes the database connection."""
        await self.client.close()

# Example Usage:
# db = Database(mongo_uri="mongodb://localhost:27017/", db_name="my_game")
#
# # Create
# new_char_id = db.create("characters", {"name": "Gandalf", "level": 99})
# print(f"Created character with ID: {new_char_id}")
#
# # Read
# character = db.read_one("characters", {"name": "Gandalf"})
# print(f"Read character: {character}")
#
# # Update
# updated_count = db.update_one("characters", {"_id": ObjectId(new_char_id)}, {"level": 100})
# print(f"Updated {updated_count} character(s).")
#
# # Delete
# deleted_count = db.delete_one("characters", {"name": "Gandalf"})
# print(f"Deleted {deleted_count} character(s).")
#
# db.close()
