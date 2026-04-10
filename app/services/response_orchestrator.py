from typing import Dict, Any, Tuple
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.services.validation_service import ValidationService
from app.services.finance_service import FinanceService
from app.services.budget_service import BudgetService
from app.services.transaction_service import TransactionService
from app.services.insight_service import InsightService

class ResponseOrchestrator:
    @classmethod
    def process(cls, user_id: str, user_text: str) -> Tuple[str, str]:
        """
        Coordinates intent parsing, state management, validation, and fulfillment.
        Returns (reply_prefix, context) to be passed to the final generative LLM step.
        """
        # Session Memory
        session = MemoryService.get_session(user_id)
        
        pending_intent = session.get("pending_intent")
        extracted_data = session.get("extracted_data", {})
        
        # 1. Handle Pending Intents (Slot Filling)
        if pending_intent:
            missing_fields = session.get("missing_fields", [])
            
            # Simple assumption: whatever the user said might fulfill the missing field
            # In a real scenario, we'd use LLM to extract the specific missing entity from the user text.
            # Here we just use another intent detection to see if we get the data, OR simply extract via LLM
            
            # Use LLM to extract entities from user_text to fill missing fields
            # For simplicity, if we need an amount, we just ask logic
            intent_data = LLMService.detect_intent(user_text)
            
            for field in missing_fields:
                if intent_data.get(field):
                    extracted_data[field] = intent_data[field]
                elif field == "amount" and any(char.isdigit() for char in user_text):
                    import re
                    # extract first number
                    num = re.findall(r"[-+]?(?:\d*\.*\d+)", user_text)
                    if num:
                        extracted_data["amount"] = float(num[0])
            
            isValid, still_missing, validated_data = ValidationService.validate_intent_data(pending_intent, extracted_data)
            
            if isValid:
                # Fulfill
                reply_prefix, context = cls._fulfill_intent(pending_intent, validated_data)
                MemoryService.update_session(user_id, {"pending_intent": None, "missing_fields": [], "extracted_data": {}})
            else:
                # Still missing
                MemoryService.update_session(user_id, {"missing_fields": still_missing, "extracted_data": validated_data})
                reply_prefix = f"I still need your {still_missing[0]}. "
                context = f"User is trying to {pending_intent} but missing {still_missing[0]}."
                
            return reply_prefix, context
            
        # 2. Detect New Intent
        intent_data = LLMService.detect_intent(user_text)
        intent = intent_data.get("intent", "unknown")
        
        if intent == "unknown":
            return "", "General conversation or unknown intent. Help the user with their finances."
            
        # 3. Validate
        isValid, missing, validated_data = ValidationService.validate_intent_data(intent, intent_data)
        
        if not isValid:
            MemoryService.update_session(user_id, {
                "pending_intent": intent,
                "missing_fields": missing,
                "extracted_data": validated_data
            })
            return f"Got it, but I still need the {missing[0]} for that. ", f"Prompt the user to provide their {missing[0]} for {intent}."
            
        # 4. Fulfill immediately if valid
        return cls._fulfill_intent(intent, validated_data)


    @classmethod
    def _fulfill_intent(cls, intent: str, data: Dict[str, Any]) -> Tuple[str, str]:
        fs = FinanceService()
        
        if intent == "add_expense":
            fs.add_expense(data.get("category"), data.get("amount"), data.get("description", ""))
            return "Got it! ✅ ", f"Successfully added {data.get('amount')} for {data.get('description', '')} in {data.get('category')}."
            
        elif intent == "get_expense":
            res = fs.get_category_expense(data.get("category"))
            return "", f"Category: {data.get('category')}. Total spent: {res['total']}."
            
        elif intent == "summary":
            summ = fs.get_summary()
            return "", f"Total spending: {summ['total_spent']}. Breakdown: {summ['category_breakdown']}."
            
        elif intent == "set_budget":
            res = BudgetService.set_budget(data.get("category"), data.get("amount"))
            return "Budget set! ✅ ", res
            
        elif intent == "get_budget_status":
            res = BudgetService.get_budget_status()
            return "", f"Budget Status:\n{res}"
            
        elif intent == "delete_expense":
            res = TransactionService.delete_expense(data.get("category"), data.get("amount"))
            return "Done. ", res
            
        elif intent == "update_expense":
            # For simplicity, assuming data has old_amount and new_amount, or we just rely on prompt context
            # We'll just say we need more details for now
            return "Note: ", "To update, please provide the new amount specifically. Action not fully implemented in this stub."
            
        elif intent == "get_recent_transactions":
            res = TransactionService.get_recent_transactions()
            return "", f"Recent Transactions:\n{res}"
            
        elif intent == "get_insights":
            res = InsightService.get_insights()
            return "", f"Insights: {res}"
            
        return "", f"Executed {intent}."
