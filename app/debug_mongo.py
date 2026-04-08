import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.mongo_service import MongoService

def debug_data():
    db = MongoService.get_db()
    print(f"Connected to: {db.name}")
    
    user_id = "whatsapp:+919370638844"
    print(f"\n--- Checking Collections for {user_id} ---")
    
    for col_name in db.list_collection_names():
        col = db[col_name]
        count = col.count_documents({})
        user_count = col.count_documents({"user_id": user_id})
        alt_user_count = col.count_documents({"userId": user_id})
        
        print(f"Collection: {col_name}")
        print(f"  Total Docs: {count}")
        print(f"  Docs with 'user_id': {user_count}")
        print(f"  Docs with 'userId': {alt_user_count}")
        
        if count > 0:
            sample = col.find_one()
            print(f"  Sample Keys: {list(sample.keys())}")
            print(f"  Sample Data: {sample}")

if __name__ == "__main__":
    debug_data()
