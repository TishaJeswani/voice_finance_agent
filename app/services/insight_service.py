from app.services.finance_service import FinanceService

class InsightService:
    @classmethod
    def get_insights(cls):
        fs = FinanceService()
        summary = fs.get_summary()
        total_spent = summary.get("total_spent", 0)
        breakdown = summary.get("category_breakdown", {})
        
        if total_spent == 0:
            return "You haven't spent anything yet. Great job saving!"
            
        top_category = max(breakdown, key=breakdown.get) if breakdown else "Unknown"
        top_spent = breakdown.get(top_category, 0)
        
        insights = [
            f"You've spent a total of ${total_spent}.",
            f"Your highest spending category is {top_category} with ${top_spent}."
        ]
        
        # We could also compare against budgets here ideally
        return " ".join(insights)
