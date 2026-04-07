from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
from fastapi.responses import PlainTextResponse, Response
from app.services.llm_service import LLMService
from app.services.input_handler import InputHandler
from app.services.audio_service import AudioService
from app.services.stt_service import STTService
from app.services.finance_service import FinanceService
from app.services.memory_service import MemoryService
from app.services.tts_service import TTSService

import asyncio

router = APIRouter()


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()

    print("RAW FORM DATA:", form_data)

    message = InputHandler.process(form_data)

    print("Structured Message:", message)
    print("Message Type:", message.message_type)

    reply_text = ""

    try:
        print("Step 1: Processing message")

        user_text = None

        # =========================
        # TEXT HANDLING
        # =========================
        if message.message_type == "text":
            user_text = message.text
            print("✅ TEXT:", user_text)

        # =========================
        # AUDIO HANDLING
        # =========================
        elif message.message_type == "audio":
            print("✅ AUDIO DETECTED")

            file_path = AudioService.download_audio(message.media_url)
            print("Audio saved at:", file_path)

            user_text = STTService.transcribe(file_path)
            print("Transcribed Text:", user_text)

        # =========================
        # SAFETY CHECK
        # =========================
        if not user_text:
            reply_text = "I couldn't understand your message. Please try again."

        else:
            print("Step 2: Finance + Memory + LLM")

            fs = FinanceService()

            # Detect category
            category = fs.extract_category(user_text)

            # Build context
            if category:
                data = fs.get_category_expense(category)

                context = f"""
User asked about category: {category}
Total spent: {data['total']}
"""
            else:
                summary = fs.get_summary()

                context = f"""
Total spending: {summary['total_spent']}
Category breakdown: {summary['category_breakdown']}
"""

            print("Context:", context)

            # =========================
            # 🧠 MEMORY LOGIC
            # =========================

            user_id = message.sender

            system_prompt = f"""
You are a smart and friendly personal finance assistant.

Your responsibilities:
- Understand user intent
- Analyze provided financial data
- Give short, human-like insights

Response style:
- Max 2-3 lines
- Conversational tone
- Always include 1 insight or suggestion

Context:
{context}
"""

            # Get previous chat
            history = MemoryService.get_history(user_id)

            # Build messages
            messages = [{"role": "system", "content": system_prompt}] + history
            messages.append({"role": "user", "content": user_text})

            print("Messages sent to LLM:", messages)

            # Call LLM
            ai_reply = LLMService.generate_response(messages)

            print("AI Reply:", ai_reply)

            # Save memory
            MemoryService.add_message(user_id, "user", user_text)
            MemoryService.add_message(user_id, "assistant", ai_reply)

            reply_text = ai_reply

    except Exception as e:
        print("❌ ERROR:", e)
        reply_text = "Something went wrong ❌"

    # =========================
    # TWILIO RESPONSE
    # =========================

    response = MessagingResponse()

    # 🎯 AUDIO RESPONSE
    if message.message_type == "audio":
        print("Step 3: Generating TTS")

        audio_path = await TTSService.text_to_speech(reply_text)

        filename = audio_path.split("/")[-1]

        # Replace with your ngrok URL
        media_url = f"https://a27a-115-98-233-39.ngrok-free.app/media/{filename}"

        print("Audio URL:", media_url)

        msg = response.message()
        msg.media(media_url)

    else:
        response.message(reply_text)

    return Response(content=str(response), media_type="application/xml")









