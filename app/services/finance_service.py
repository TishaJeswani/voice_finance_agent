from rapidfuzz import process
from db.mongo import transactions_collection
from datetime import datetime

DEFAULT_CATEGORIES = ["Groceries", "Dining", "Transport", "Rent", "Entertainment", "Health", "Utilities", "Shopping"]

class FinanceService:

    def match_category(self, category_name):
        """Fuzzy match category against defaults."""
        if not category_name:
            return "Other"
        
        # Use RapidFuzz for better matching
        match = process.extractOne(category_name, DEFAULT_CATEGORIES, score_cutoff=70)
        return match[0] if match else "Other"

    def add_expense(self, category, amount, description):
        """Add a new transaction to MongoDB (Global)."""
        transaction = {
            "category": category,
            "amount": float(amount),
            "description": description,
            "date": datetime.now()
        }
        result = transactions_collection.insert_one(transaction)
        print(f"✅ Transaction added: {result.inserted_id}")
        return transaction

    def get_category_expense(self, category):
        """Get total spent for a category across all users."""
        print(f"📊 Querying expenses for {category}...")
        results = list(transactions_collection.find({
            "category": category
        }))
        
        # Also check capitalized 'Category' if needed for legacy data
        if not results:
             results = list(transactions_collection.find({
                "Category": category
            }))

        total = sum(item.get("amount", 0) or item.get("Amount", 0) for item in results)
        return {"total": round(total, 2), "count": len(results)}

    def get_summary(self):
        """Generate global summary of all spending."""
        print("📊 Generating global summary...")
        results = list(transactions_collection.find({}))
        
        total_spent = sum(item.get("amount", 0) or item.get("Amount", 0) for item in results)
        category_breakdown = {}
        for item in results:
            cat = item.get("category") or item.get("Category") or "Other"
            amount = item.get("amount") or item.get("Amount") or 0
            category_breakdown[cat] = category_breakdown.get(cat, 0) + amount
        
        # Round the values
        for cat in category_breakdown:
            category_breakdown[cat] = round(category_breakdown[cat], 2)

        return {
            "total_spent": round(total_spent, 2),
            "category_breakdown": category_breakdown,
            "transaction_count": len(results)
        }