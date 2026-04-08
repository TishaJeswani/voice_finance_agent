import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

try:
    print("Importing LLMService...")
    from app.services.llm_service import LLMService
    print("✅ LLMService imported.")

    print("Importing FinanceService...")
    from app.services.finance_service import FinanceService
    print("✅ FinanceService imported.")

    print("Importing MongoService...")
    from app.services.mongo_service import MongoService
    print("✅ MongoService imported.")

    print("Importing STTService...")
    from app.services.stt_service import STTService
    print("✅ STTService imported.")

    print("Importing TTSService...")
    from app.services.tts_service import TTSService
    print("✅ TTSService imported.")

    print("Importing MemoryService...")
    from app.services.memory_service import MemoryService
    print("✅ MemoryService imported.")

    print("Importing InputHandler...")
    from app.services.input_handler import InputHandler
    print("✅ InputHandler imported.")

    print("\n🎉 All services imported successfully!")
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
