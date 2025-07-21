from pymongo import MongoClient
from bson import ObjectId
from typing import Dict, Any, List, Optional

class Database:
    """A universal MongoDB database tool for CRUD operations."""

    def __init__(self, mongo_uri: str, db_name: str):
        """Initializes the database connection."""
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

    def _serialize_doc(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Converts MongoDB's ObjectId to a string for JSON compatibility."""
        if doc and '_id' in doc:
            doc['_id'] = str(doc['_id'])
        return doc

    def create(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Creates a single document in a collection."""
        result = self.db[collection_name].insert_one(document)
        return str(result.inserted_id)

    def create_many(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
        """Creates multiple documents in a collection."""
        result = self.db[collection_name].insert_many(documents)
        return [str(id) for id in result.inserted_ids]

    def read_one(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Reads a single document from a collection."""
        document = self.db[collection_name].find_one(query)
        return self._serialize_doc(document)

    def read_many(self, collection_name: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Reads multiple documents from a collection."""
        documents = self.db[collection_name].find(query)
        return [self._serialize_doc(doc) for doc in documents]

    def update_one(self, collection_name: str, query: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """Updates a single document in a collection."""
        result = self.db[collection_name].update_one(query, {'$set': update_data})
        return result.modified_count

    def update_many(self, collection_name: str, query: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """Updates multiple documents in a collection."""
        result = self.db[collection_name].update_many(query, {'$set': update_data})
        return result.modified_count

    def delete_one(self, collection_name: str, query: Dict[str, Any]) -> int:
        """Deletes a single document from a collection."""
        result = self.db[collection_name].delete_one(query)
        return result.deleted_count

    def delete_many(self, collection_name: str, query: Dict[str, Any]) -> int:
        """Deletes multiple documents from a collection."""
        result = self.db[collection_name].delete_many(query)
        return result.deleted_count

    def close(self):
        """Closes the database connection."""
        self.client.close()

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
