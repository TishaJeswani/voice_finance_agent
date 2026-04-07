import os
import requests
from datetime import datetime
from app.core.config import settings


class AudioService:

    @staticmethod
    def download_audio(media_url: str) -> str:
        response = requests.get(
            media_url,
            auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        )

        if response.status_code != 200:
            raise Exception("Failed to download audio")

        filename = f"audio_{datetime.now().timestamp()}.ogg"
        file_path = os.path.join("app", "media", filename)

        with open(file_path, "wb") as f:
            f.write(response.content)

        return file_path