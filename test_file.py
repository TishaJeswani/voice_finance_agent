from db.mongo import users_collection

users_collection.insert_one({
    "user_id": "test_user",
    "name": "Tisha"
})

print("✅ MongoDB Connected & Inserted")