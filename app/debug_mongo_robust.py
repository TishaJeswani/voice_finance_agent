import sys
import os

# Set encoding for Windows stdout
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.services.mongo_service import MongoService

def debug_data():
    try:
        db = MongoService.get_db()
        print(f"Connected to: {db.name}")
        
        user_id = "whatsapp:+919370638844"
        print(f"\n--- Checking Collections for {user_id} ---")
        
        for col_name in db.list_collection_names():
            if col_name.startswith("system."): continue
            
            col = db[col_name]
            count = col.count_documents({})
            user_count = col.count_documents({"user_id": user_id})
            
            print(f"Collection: {col_name} (Total Docs: {count}, Docs for this user: {user_count})")
            
            if count > 0:
                sample = col.find_one()
                # Print keys carefully
                keys = list(sample.keys())
                print(f"  Field Names: {keys}")
                # Print sample without potential problematic chars if possible
                print(f"  Sample ID: {sample.get('_id')}")
                if "category" in sample: print(f"  Sample Category: {sample['category']}")
                if "amount" in sample: print(f"  Sample Amount: {sample['amount']}")
                if "Category" in sample: print(f"  Sample Category (Caps): {sample['Category']}")
                if "Amount" in sample: print(f"  Sample Amount (Caps): {sample['Amount']}")

        print("\n--- Summary check for Groceries ---")
        transactions = db["transactions"]
        query = {"user_id": user_id, "category": "Groceries"}
        g_count = transactions.count_documents(query)
        print(f"Query {query} returning {g_count} docs")
        
        # Check capitalized Category just in case
        query_cap = {"user_id": user_id, "Category": "Groceries"}
        g_count_cap = transactions.count_documents(query_cap)
        print(f"Query {query_cap} returning {g_count_cap} docs")

    except Exception as e:
        print(f"Error during debug: {e}")

if __name__ == "__main__":
    debug_data()
