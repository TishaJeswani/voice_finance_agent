# import requests
# from app.core.config import settings


# class LLMService:

#     @staticmethod
#     def generate_response(messages: list) -> str:

#         url = "https://openrouter.ai/api/v1/chat/completions"

#         headers = {
#             "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
#             "Content-Type": "application/json"
#         }

#         payload = {
#             "model": "deepseek/deepseek-chat",
#             "temperature": 0.5,
#             "max_tokens": 150,
#             "messages": messages
#         }

#         response = requests.post(url, headers=headers, json=payload)

#         if response.status_code != 200:
#             raise Exception(f"LLM Error: {response.text}")

#         return response.json()["choices"][0]["message"]["content"].strip()




import requests
import re
from app.core.config import settings


class LLMService:

    @staticmethod
    def generate_response(messages: list) -> str:

        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek/deepseek-chat",
            "temperature": 0.5,
            "max_tokens": 150,
            "messages": messages
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"LLM Error: {response.text}")

        # 🔥 RAW OUTPUT FROM LLM
        raw_text = response.json()["choices"][0]["message"]["content"]

        # =========================
        # 🧹 CLEANING LOGIC
        # =========================

        # Remove markdown symbols (*, **, _, #, `)
        clean_text = re.sub(r"[*_`#]", "", raw_text)

        # Replace multiple newlines with space
        clean_text = re.sub(r"\n+", " ", clean_text)

        # Optional: better formatting for "Insight:"
        clean_text = clean_text.replace("Insight:", "\nInsight:")

        # Trim spaces
        clean_text = clean_text.strip()

        return clean_text