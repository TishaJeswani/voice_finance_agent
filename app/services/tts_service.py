import edge_tts
import asyncio
import os
import time


class TTSService:

    @staticmethod
    async def text_to_speech(text: str) -> str:
        output_path = f"app/media/tts_{time.time()}.mp3"

        communicate = edge_tts.Communicate(
            text=text,
            voice="en-US-AriaNeural"
        )

        await communicate.save(output_path)

        return output_path

    async def generate_audio_response(text: str):
        return None