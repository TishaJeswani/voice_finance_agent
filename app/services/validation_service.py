from typing import Dict, Any, List, Tuple
from app.services.finance_service import FinanceService

class ValidationService:
    REQUIRED_FIELDS = {
        "add_expense": ["amount", "category"],
        "set_budget": ["amount", "category"]
    }
    
    @classmethod
    def validate_intent_data(cls, intent: str, data: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
        # Normalize category
        fs = FinanceService()
        if data.get("category"):
            data["category"] = fs.match_category(data["category"])
            
        required = cls.REQUIRED_FIELDS.get(intent, [])
        missing = [f for f in required if data.get(f) is None]
        
        return len(missing) == 0, missing, data
