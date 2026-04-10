from db.mongo import transactions_collection, budgets_collection
from datetime import datetime
from app.services.finance_service import FinanceService

class BudgetService:
    @classmethod
    def set_budget(cls, category: str, limit: float):
        fs = FinanceService()
        cat = fs.match_category(category)
        now = datetime.now()
        month_str = f"{now.year}-{now.month:02d}"
        
        budgets_collection.update_one(
            {"month": month_str, "category": cat},
            {"$set": {"limit": float(limit), "updated_at": now}},
            upsert=True
        )
        return f"Budget for {cat} set to ${limit}."

    @classmethod
    def get_budget_status(cls):
        now = datetime.now()
        month_str = f"{now.year}-{now.month:02d}"
        
        budgets = list(budgets_collection.find({"month": month_str}))
        if not budgets:
            return "No active budgets set for this month."
            
        status = []
        for b in budgets:
            limit = b["limit"]
            spent = cls._get_spent(b["category"])
            perc = (spent / limit) * 100 if limit > 0 else 0
            status.append(f"{b['category']}: Spent ${spent} of ${limit} ({perc:.1f}%)")
        return "\n".join(status)

    @classmethod
    def _get_spent(cls, category: str) -> float:
        # Simplistic start of month fetch
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        res = list(transactions_collection.find({
            "category": category, 
            "date": {"$gte": start_of_month}
        }))
        return sum(item.get("amount", 0) or item.get("Amount", 0) for item in res)
