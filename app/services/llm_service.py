import requests
import json
import re
from app.core.config import settings

class LLMService:
    MODELS = [
        "deepseek/deepseek-chat",            # Primary
        "google/gemini-2.0-flash-001",       # Robust fallback
        "meta-llama/llama-3.3-70b-instruct"  # Alternative fallback
    ]

    @staticmethod
    def _keyword_detect(user_input: str) -> dict:
        """Basic keyword fall-back if LLMs fail."""
        text = user_input.lower()
        if any(w in text for w in ["summary", "total", "spent so far"]):
            return {"intent": "summary", "category": None, "amount": None, "description": None}
        if any(w in text for w in ["how much", "what did i spend", "check"]):
            # Very basic extraction
            category = None
            if "grocer" in text: category = "Groceries"
            elif "transport" in text or "fuel" in text: category = "Transport"
            return {"intent": "get_expense", "category": category, "amount": None, "description": None}
        return {"intent": "unknown", "category": None, "amount": None, "description": None}

    @staticmethod
    def detect_intent(user_input: str) -> dict:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        system_prompt = """
You are an intent detection system for a personal finance assistant.
Available Intents:
1. get_expense: User wants to know how much they spent.
2. add_expense: User wants to record a new transaction.
3. summary: User wants an overview of total spending.

Return ONLY valid JSON.
Format:
{
  "intent": "get_expense | add_expense | summary | unknown",
  "category": "string or null",
  "amount": number or null,
  "description": "string or null"
}
"""

        for model in LLMService.MODELS:
            payload = {
                "model": model,
                "temperature": 0,
                "max_tokens": 150,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "response_format": {"type": "json_object"}
            }

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"].strip()
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        content = json_match.group(0)
                        print(f"DEBUG: LLM Raw Intent ({model}): {content}")
                        return json.loads(content)
                else:
                    print(f"⚠️ Model {model} failed (Status {response.status_code}): {response.text}")
                    if "429" in str(response.status_code):
                        continue # Try next model if rate limited
            except Exception as e:
                print(f"❌ Exception with model {model}: {e}")
                continue

        # Last resort: Keyword detection
        print("🛠️ Falling back to keyword-based detection")
        return LLMService._keyword_detect(user_input)

    @staticmethod
    def generate_response(messages: list) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        for model in LLMService.MODELS:
            payload = {
                "model": model,
                "temperature": 0.5,
                "max_tokens": 250,
                "messages": messages
            }

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=15)
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"].strip()
                else:
                    print(f"⚠️ Model {model} failed (Status {response.status_code})")
                    if "429" in str(response.status_code):
                        continue
            except Exception as e:
                print(f"❌ Exception with model {model}: {e}")
                continue

        return "I'm having a bit of trouble connecting to my brain right now. Please try again soon!"