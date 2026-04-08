import edge_tts
import time
import os

class TTSService:

    @staticmethod
    async def generate_audio(text: str) -> str:
        try:
            filename = f"tts_{int(time.time())}.mp3"
            output_path = f"app/media/{filename}"


            
            communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
            await communicate.save(output_path)
            
            return filename
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return None


    async def generate_audio_response(text: str):
        return None