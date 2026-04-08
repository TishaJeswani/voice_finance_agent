from app.services.mongo_service import MongoService

# Use the unified MongoService to get collections
db = MongoService.get_db()
users_collection = MongoService.get_collection("users")
transactions_collection = MongoService.get_collection("transactions")
chat_collection = MongoService.get_collection("chat_history")