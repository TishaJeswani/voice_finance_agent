from db.mongo import transactions_collection
from app.services.finance_service import FinanceService

class TransactionService:
    @classmethod
    def get_recent_transactions(cls, limit: int = 5):
        transactions = list(transactions_collection.find().sort("date", -1).limit(limit))
        if not transactions:
            return "No recent transactions found."
        
        result = []
        for t in transactions:
            date_str = t["date"].strftime("%Y-%m-%d") if "date" in t and hasattr(t["date"], "strftime") else "Unknown Date"
            cat = t.get("category", "Unknown")
            amt = t.get("amount", 0)
            desc = t.get("description", "")
            result.append(f"{date_str} - {cat}: ${amt} {f'({desc})' if desc else ''}")
        return "\n".join(result)

    @classmethod
    def delete_expense(cls, category: str, amount: float):
        # A simple delete for demonstration
        fs = FinanceService()
        cat = fs.match_category(category)
        
        # Try to find the exact match
        result = transactions_collection.delete_one({"category": cat, "amount": amount})
        if result.deleted_count > 0:
            return f"Deleted expense of ${amount} in {cat}."
        else:
            return f"Could not find an expense of ${amount} in {cat}."

    @classmethod
    def update_expense(cls, old_category: str, old_amount: float, new_amount: float):
        fs = FinanceService()
        cat = fs.match_category(old_category)
        
        result = transactions_collection.update_one(
            {"category": cat, "amount": old_amount},
            {"$set": {"amount": new_amount}}
        )
        if result.modified_count > 0:
            return f"Updated expense from ${old_amount} to ${new_amount} in {cat}."
        else:
            return f"Could not find an expense of ${old_amount} in {cat} to update."
