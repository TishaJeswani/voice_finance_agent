import os

# ✅ Add ffmpeg path (IMPORTANT - before importing whisper)
os.environ["PATH"] += ";C:\\ffmpeg\\bin"

import whisper

# ✅ Load model once (global)
model = whisper.load_model("base")


class STTService:

    @staticmethod
    def transcribe(audio_path: str) -> str:
        try:
            result = model.transcribe(audio_path)
            return result["text"].strip()
        except Exception as e:
            print("STT Error:", e)
            raise Exception("Speech-to-text failed")

