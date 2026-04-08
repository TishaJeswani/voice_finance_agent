import os

# ✅ Add ffmpeg path (IMPORTANT - before importing whisper)
os.environ["PATH"] += ";C:\\ffmpeg\\bin"

import whisper

# ✅ Lazy load model to prevent startup hangs
_model = None

class STTService:

    @staticmethod
    def get_model():
        global _model
        if _model is None:
            print("🎤 Loading Whisper model (this may take a moment)...")
            _model = whisper.load_model("base")
            print("✅ Whisper model loaded.")
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
