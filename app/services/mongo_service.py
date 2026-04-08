from pymongo import MongoClient
from app.core.config import settings

class MongoService:
    _client = None
    _db = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = MongoClient(settings.MONGO_URI)
            print("✅ MongoDB Client Initialized")
        return cls._client

    @classmethod
    def get_db(cls):
        if cls._db is None:
            client = cls.get_client()
            # Standardizing on finance_ai as per db/mongo.py but making it configurable if needed
            db_name = getattr(settings, "MONGO_DB_NAME", "finance_ai")
            cls._db = client[db_name]
            print(f"✅ Connected to MongoDB Database: {db_name}")
        return cls._db

    @classmethod
    def get_collection(cls, collection_name: str):
        db = cls.get_db()
        return db[collection_name]