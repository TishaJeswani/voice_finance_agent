from db.mongo import memory_collection
from datetime import datetime

class MemoryService:
    @classmethod
    def get_session(cls, user_id: str):
        session = memory_collection.find_one({"session_id": user_id})
        if not session:
            session = {
                "session_id": user_id, "history": [], "pending_intent": None,
                "missing_fields": [], "extracted_data": {}, "updated_at": datetime.now()
            }
            memory_collection.insert_one(session)
        return session

    @classmethod
    def update_session(cls, user_id: str, updates: dict):
        updates["updated_at"] = datetime.now()
        memory_collection.update_one({"session_id": user_id}, {"$set": updates}, upsert=True)

    @classmethod
    def add_message(cls, user_id: str, role: str, content: str):
        memory_collection.update_one(
            {"session_id": user_id}, 
            {"$push": {"history": {"role": role, "content": content}}, "$set": {"updated_at": datetime.now()}},
            upsert=True
        )

    @classmethod
    def get_history(cls, user_id: str):
        session = cls.get_session(user_id)
        return session.get("history", [])[-10:] # Keep recent 10 messages

    @classmethod
    def clear_history(cls, user_id: str):
        memory_collection.update_one({"session_id": user_id}, {"$set": {"history": [], "updated_at": datetime.now()}})