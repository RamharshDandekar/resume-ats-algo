from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional

class MongoDBManager:
    """Singleton class to manage MongoDB connections"""
    _instance: Optional["MongoDBManager"] = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self, uri: str = "mongodb://localhost:27017", db_name: str = "intellihire"):
        """Connect to MongoDB"""
        if self._client is None:
            self._client = MongoClient(uri)
            self._db = self._client[db_name]
            print(f"Connected to MongoDB database: {db_name}")

    def disconnect(self):
        """Disconnect from MongoDB"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            print("Disconnected from MongoDB")

    def get_db(self) -> Database:
        """Get the database instance"""
        if self._db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._db

    def get_collection(self, collection_name: str):
        """Get a specific collection"""
        return self.get_db()[collection_name]

# Singleton instance
mongo_manager = MongoDBManager()
