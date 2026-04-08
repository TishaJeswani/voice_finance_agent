from fastapi import APIRouter, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
import traceback
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.services.llm_service import LLMService
from app.services.input_handler import InputHandler
from app.services.audio_service import AudioService
from app.services.stt_service import STTService
from app.services.finance_service import FinanceService
from app.services.memory_service import MemoryService
from app.services.tts_service import TTSService
from app.core.config import get_ngrok_url


router = APIRouter()

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Main entry point for Twilio WhatsApp Webhook.
    """
    print("\n" + "="*50, flush=True)
    print("🔥 NEW WEBHOOK REQUEST RECEIVED", flush=True)
    print("="*50, flush=True)
    logger.info("🔥 Incoming request to /whatsapp")
    
    try:
        form_data = await request.form()
        user_id = form_data.get("From", "unknown")
        
        print(f"📩 Sender: {user_id}", flush=True)
        logger.info(f"📩 New Message from {user_id}")
        
        # 1. Process Input
        message = InputHandler.process(form_data)
        user_text = None

        if message.message_type == "text":
            user_text = message.text
            print(f"📝 Text: {user_text}", flush=True)
            logger.info(f"📝 Text received: {user_text}")
        elif message.message_type == "audio":
            print(f"🎤 Audio Media URL: {message.media_url}", flush=True)
            logger.info("🎤 Audio detected, downloading...")
            file_path = AudioService.download_audio(message.media_url)
            print(f"📁 Downloaded to: {file_path}", flush=True)
            user_text = STTService.transcribe(file_path)
            print(f"📝 Transcribed: {user_text}", flush=True)
            logger.info(f"📝 Transcribed text: {user_text}")

        if not user_text:
            print("⚠️ Ignoring request: No text content found.", flush=True)
            logger.warning("⚠️ No text or audio content found in message.")
            return generate_twiml_response("I couldn't hear or read that correctly. Could you please repeat?")

        # 2. Intent Detection
        print("🧠 Detecting Intent...", flush=True)
        logger.info("🧠 Detecting intent...")
        intent_data = LLMService.detect_intent(user_text)
        intent = intent_data.get("intent", "unknown")
        print(f"🎯 Intent: {intent}", flush=True)
        logger.info(f"🎯 Intent identified: {intent}")

        fs = FinanceService()
        context = ""
        reply_prefix = ""

        # 3. Handle Intents
        if intent == "add_expense":
            amount = intent_data.get("amount")
            category_raw = intent_data.get("category")
            description = intent_data.get("description")
            
            if amount:
                category = fs.match_category(category_raw)
                fs.add_expense(category, amount, description)
                context = f"Successfully added {amount} for {description} in category {category}."
                reply_prefix = "Got it! ✅ "
                print(f"✅ Added Expense: {amount} in {category}", flush=True)
                logger.info(f"✅ Expense added: {amount} in {category}")
            else:
                context = "User tried to add an expense but the amount was missing."
                reply_prefix = "I heard you wanted to add an expense, but I missed the amount. "
                print("⚠️ Missing amount in add_expense", flush=True)
                logger.warning("⚠️ Missing amount in add_expense intent")

        elif intent == "get_expense":
            category_raw = intent_data.get("category")
            matched_category = fs.match_category(category_raw)
            
            if matched_category:
                data = fs.get_category_expense(matched_category)
                context = f"Category: {matched_category}. Total spent: {data['total']}."
                print(f"🔍 Found spent for {matched_category}: {data['total']}", flush=True)
                logger.info(f"🔍 Fetched expenses for {matched_category}: {data['total']}")
            else:
                context = "No matching category was found."
                print(f"⚠️ No category match for {category_raw}", flush=True)
                logger.warning(f"⚠️ No matching category for: {category_raw}")

        elif intent == "summary":
            summary = fs.get_summary()
            context = f"Total spending: {summary['total_spent']}. Category breakdown: {summary['category_breakdown']}."
            print(f"📊 Summary generated: {summary['total_spent']} total", flush=True)
            logger.info(f"📊 Summary generated: {summary['total_spent']} total")

        else:
            context = "General conversation or unknown intent. Help the user with their finances."
            print("ℹ️ General Conversation", flush=True)
            logger.info("ℹ️ Proceeding with general conversation")

        # 4. Generate AI Response
        print("🤖 Calling LLM for response...", flush=True)
        logger.info("🤖 Generating AI response...")
        system_prompt = f"""
You are a smart personal finance assistant.
Rules:
- Keep response under 2-3 lines.
- Be conversational and helpful.
- Reference the current data if provided in context.

Context:
{context}
"""
        history = MemoryService.get_history(user_id)
        messages = [{"role": "system", "content": system_prompt}] + history
        messages.append({"role": "user", "content": user_text})

        ai_reply = LLMService.generate_response(messages)
        full_reply = f"{reply_prefix}{ai_reply}"
        print(f"💬 Final AI Reply: {full_reply}", flush=True)
        logger.info(f"💬 Generated Reply: {full_reply}")

        # 5. Save History
        MemoryService.add_message(user_id, "user", user_text)
        MemoryService.add_message(user_id, "assistant", full_reply)

        # 6. Send Response
        audio_filename = None
        if message.message_type == "audio":
             print("🎧 Generating audio response...", flush=True)
             audio_filename = await TTSService.generate_audio(ai_reply)
        
        print("📤 Sending response to Twilio...", flush=True)
        return await send_twilio_response(request, full_reply, message.message_type, audio_filename)

    except Exception as e:
        print(f"❌ WEBHOOK CRASHED: {e}", flush=True)
        traceback.print_exc()
        logger.error(f"❌ Webhook Error: {e}")
        logger.error(traceback.format_exc())
        return generate_twiml_response("Sorry, I encountered an error. Let's try again in a moment.")


@router.get("/health")
async def health_check():
    logger.info("🏥 Health check ping")
    return {"status": "ok"}


from typing import Optional

async def send_twilio_response(request: Request, text: str, message_type: str, audio_filename: Optional[str] = None):
    response = MessagingResponse()
    msg = response.message()
    
    # Use the current request's base URL to ensure ngrok matches perfectly
    base_url = str(request.base_url).rstrip("/")
    
    if audio_filename:
        media_url = f"{base_url}/media/{audio_filename}"
        print(f"🎧 Media URL for Twilio: {media_url}", flush=True)
        
        # Add a clickable link to the text as a foolproof fallback
        final_text = f"{text}\n\nListen: {media_url}"
        msg.body(final_text)
        msg.media(media_url)
    else:
        msg.body(text)
        
    return Response(content=str(response), media_type="application/xml")


def generate_twiml_response(text: str):
    response = MessagingResponse()
    response.message(text)
    return Response(content=str(response), media_type="application/xml")