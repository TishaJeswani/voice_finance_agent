import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Connect MongoDB
client = MongoClient(MONGO_URI)
db = client["finance_db"]
transactions_collection = db["transactions"]

# Load CSV
df = pd.read_csv("data/transactions.csv")

# Clean column names
df.columns = df.columns.str.lower()

# Convert data to Mongo format
records = []

for _, row in df.iterrows():
    record = {
        "date": datetime.strptime(row["date"], "%Y-%m-%d"),
        "category": row["category"],
        "description": row["description"],
        "amount": float(row["amount"]),
        "payment_method": row["payment_method"],
        
        # 🔥 Important for multi-user support
        "user_id": "demo_user"
    }
    records.append(record)

# Insert into MongoDB
if records:
    transactions_collection.insert_many(records)
    print(f"✅ Inserted {len(records)} records into MongoDB")
else:
    print("❌ No records found")