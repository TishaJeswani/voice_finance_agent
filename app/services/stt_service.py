import os

# ✅ Add ffmpeg path (IMPORTANT - before importing whisper)
os.environ["PATH"] += ";C:\\ffmpeg\\bin"

import whisper

# ✅ Eager load model to prevent startup hangs
print("🎤 Pre-loading Whisper model on startup to avoid Twilio timeouts...")
_model = whisper.load_model("base")
print("✅ Whisper model loaded.")

class STTService:

    @staticmethod
    def get_model():
        return _model

    @staticmethod
    def transcribe(audio_path: str) -> str:
        try:
            model = STTService.get_model()
            result = model.transcribe(audio_path)
            return result["text"].strip()
        except Exception as e:
            print(f"❌ STT Error: {e}")
            return "" # Return empty string instead of crashing
