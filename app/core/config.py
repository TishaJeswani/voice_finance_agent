import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_ngrok_url() -> str:
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=2)
        data = response.json()
        for tunnel in data.get("tunnels", []):
            if tunnel.get("proto") == "https":
                return tunnel["public_url"]
    except:
        pass
    return os.getenv("BASE_URL", "http://localhost:8000")

class Settings:
    APP_NAME: str = "Voice Finance Assistant"
    
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

settings = Settings()
