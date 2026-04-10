# from fastapi import APIRouter, Request, Response
# from twilio.twiml.messaging_response import MessagingResponse
# import traceback
# import sys
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# from app.services.llm_service import LLMService
# from app.services.input_handler import InputHandler
# from app.services.audio_service import AudioService
# from app.services.stt_service import STTService
# from app.services.finance_service import FinanceService
# from app.services.memory_service import MemoryService
# from app.services.tts_service import TTSService
# from app.core.config import get_ngrok_url


# router = APIRouter()

# @router.post("/whatsapp")
# async def whatsapp_webhook(request: Request):
#     """
#     Main entry point for Twilio WhatsApp Webhook.
#     """
#     print("\n" + "="*50, flush=True)
#     print("🔥 NEW WEBHOOK REQUEST RECEIVED", flush=True)
#     print("="*50, flush=True)
#     logger.info("🔥 Incoming request to /whatsapp")
    
#     try:
#         form_data = await request.form()
#         user_id = form_data.get("From", "unknown")
        
#         print(f"📩 Sender: {user_id}", flush=True)
#         logger.info(f"📩 New Message from {user_id}")
        
#         # 1. Process Input
#         message = InputHandler.process(form_data)
#         user_text = None

#         if message.message_type == "text":
#             user_text = message.text
#             print(f"📝 Text: {user_text}", flush=True)
#             logger.info(f"📝 Text received: {user_text}")
#         elif message.message_type == "audio":
#             print(f"🎤 Audio Media URL: {message.media_url}", flush=True)
#             logger.info("🎤 Audio detected, downloading...")
#             file_path = AudioService.download_audio(message.media_url)
#             print(f"📁 Downloaded to: {file_path}", flush=True)
#             user_text = STTService.transcribe(file_path)
#             print(f"📝 Transcribed: {user_text}", flush=True)
#             logger.info(f"📝 Transcribed text: {user_text}")

#         if not user_text:
#             print("⚠️ Ignoring request: No text content found.", flush=True)
#             logger.warning("⚠️ No text or audio content found in message.")
#             return generate_twiml_response("I couldn't hear or read that correctly. Could you please repeat?")

#         # 2. Intent Detection
#         print("🧠 Detecting Intent...", flush=True)
#         logger.info("🧠 Detecting intent...")
#         intent_data = LLMService.detect_intent(user_text)
#         intent = intent_data.get("intent", "unknown")
#         print(f"🎯 Intent: {intent}", flush=True)
#         logger.info(f"🎯 Intent identified: {intent}")

#         fs = FinanceService()
#         context = ""
#         reply_prefix = ""

#         # 3. Handle Intents
#         if intent == "add_expense":
#             amount = intent_data.get("amount")
#             category_raw = intent_data.get("category")
#             description = intent_data.get("description")
            
#             if amount:
#                 category = fs.match_category(category_raw)
#                 fs.add_expense(category, amount, description)
#                 context = f"Successfully added {amount} for {description} in category {category}."
#                 reply_prefix = "Got it! ✅ "
#                 print(f"✅ Added Expense: {amount} in {category}", flush=True)
#                 logger.info(f"✅ Expense added: {amount} in {category}")
#             else:
#                 context = "User tried to add an expense but the amount was missing."
#                 reply_prefix = "I heard you wanted to add an expense, but I missed the amount. "
#                 print("⚠️ Missing amount in add_expense", flush=True)
#                 logger.warning("⚠️ Missing amount in add_expense intent")

#         elif intent == "get_expense":
#             category_raw = intent_data.get("category")
#             matched_category = fs.match_category(category_raw)
            
#             if matched_category:
#                 data = fs.get_category_expense(matched_category)
#                 context = f"Category: {matched_category}. Total spent: {data['total']}."
#                 print(f"🔍 Found spent for {matched_category}: {data['total']}", flush=True)
#                 logger.info(f"🔍 Fetched expenses for {matched_category}: {data['total']}")
#             else:
#                 context = "No matching category was found."
#                 print(f"⚠️ No category match for {category_raw}", flush=True)
#                 logger.warning(f"⚠️ No matching category for: {category_raw}")

#         elif intent == "summary":
#             summary = fs.get_summary()
#             context = f"Total spending: {summary['total_spent']}. Category breakdown: {summary['category_breakdown']}."
#             print(f"📊 Summary generated: {summary['total_spent']} total", flush=True)
#             logger.info(f"📊 Summary generated: {summary['total_spent']} total")

#         else:
#             context = "General conversation or unknown intent. Help the user with their finances."
#             print("ℹ️ General Conversation", flush=True)
#             logger.info("ℹ️ Proceeding with general conversation")

#         # 4. Generate AI Response
#         print("🤖 Calling LLM for response...", flush=True)
#         logger.info("🤖 Generating AI response...")
#         system_prompt = f"""
# You are an expert, friendly, and highly knowledgeable personal finance assistant.
# Rules:
# - Provide detailed, insightful, and knowledgeable answers in user-friendly terms.
# - Use a supportive and conversational tone, like a trusted human financial advisor.
# - Always try to provide proper, actionable suggestions, tips, or alternatives relevant to the user's query.
# - Keep your response under 1000 characters so it fits neatly into a single WhatsApp message.
# - Make your formatting easy to read (use emojis or short bullet points where appropriate).
# - Reference the current data if provided in context.

# Context:
# {context}
# """
#         history = MemoryService.get_history(user_id)
#         messages = [{"role": "system", "content": system_prompt}] + history
#         messages.append({"role": "user", "content": user_text})

#         ai_reply = LLMService.generate_response(messages)
#         full_reply = f"{reply_prefix}{ai_reply}"
#         print(f"💬 Final AI Reply: {full_reply}", flush=True)
#         logger.info(f"💬 Generated Reply: {full_reply}")

#         # 5. Save History
#         MemoryService.add_message(user_id, "user", user_text)
#         MemoryService.add_message(user_id, "assistant", full_reply)

#         # 6. Send Response
#         audio_filename = None
#         if message.message_type == "audio":
#              print("🎧 Generating audio response...", flush=True)
#              audio_filename = await TTSService.generate_audio(ai_reply)
        
#         print("📤 Sending response to Twilio...", flush=True)
#         return await send_twilio_response(request, full_reply, message.message_type, audio_filename)

#     except Exception as e:
#         print(f"❌ WEBHOOK CRASHED: {e}", flush=True)
#         traceback.print_exc()
#         logger.error(f"❌ Webhook Error: {e}")
#         logger.error(traceback.format_exc())
#         return generate_twiml_response("Sorry, I encountered an error. Let's try again in a moment.")


# @router.get("/health")
# async def health_check():
#     logger.info("🏥 Health check ping")
#     return {"status": "ok"}


# from typing import Optional

# async def send_twilio_response(request: Request, text: str, message_type: str, audio_filename: Optional[str] = None):
#     response = MessagingResponse()
    
#     # Use the current request's base URL to ensure ngrok matches perfectly
#     base_url = str(request.base_url).rstrip("/")
    
#     def chunk_message(msg_text, max_len=1500):
#         chunks = []
#         while len(msg_text) > max_len:
#             split_at = msg_text.rfind('\n', 0, max_len)
#             if split_at == -1:
#                 split_at = msg_text.rfind(' ', 0, max_len)
#             if split_at == -1:
#                 split_at = max_len
#             chunks.append(msg_text[:split_at].strip())
#             msg_text = msg_text[split_at:].strip()
#         if msg_text:
#             chunks.append(msg_text)
#         return chunks

#     if audio_filename:
#         media_url = f"{base_url}/media/{audio_filename}"
#         print(f"🎧 Media URL for Twilio: {media_url}", flush=True)
        
#         # Audio message first (with NO body text to prevent Twilio splitting bugs on WhatsApp)
#         audio_msg = response.message()
#         audio_msg.media(media_url)
        
#         # Then the normal text reply
#         final_text = f"{text}\n\nListen: {media_url}"
#         chunks = chunk_message(final_text)
#         for chunk in chunks:
#             msg = response.message()
#             msg.body(chunk)
#     else:
#         chunks = chunk_message(text)
#         for chunk in chunks:
#             msg = response.message()
#             msg.body(chunk)
            
#     return Response(content=str(response), media_type="application/xml")


# def generate_twiml_response(text: str):
#     response = MessagingResponse()
#     msg = response.message()
#     # Failsafe chunking for simple twiml generator, usually for error messages
#     msg.body(text[:1500])
#     return Response(content=str(response), media_type="application/xml")

from fastapi import APIRouter, Request, Response, BackgroundTasks
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import traceback
import sys
import logging
import os

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
from app.services.response_orchestrator import ResponseOrchestrator
from app.core.config import get_ngrok_url

router = APIRouter()

async def process_and_reply(form_data: dict, base_url: str):
    """
    Background task to process audio/text, talk to LLM, and send response back via REST API.
    """
    user_id = form_data.get("From", "unknown")
    bot_id = form_data.get("To", "unknown")
    
    print("\n" + "="*50, flush=True)
    print("🚀 BACKGROUND TASK STARTED", flush=True)
    print(f"📩 Sender: {user_id}", flush=True)
    print("="*50, flush=True)
    
    try:
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

        # Initialize Twilio Client early to send fallback errors if needed
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if not account_sid or not auth_token:
            logger.error("❌ CRITICAL: TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN is missing from your environment variables!")
            return

        client = Client(account_sid, auth_token)

        if not user_text:
            print("⚠️ Ignoring request: No text content found.", flush=True)
            logger.warning("⚠️ No text or audio content found in message.")
            client.messages.create(
                from_=bot_id,
                to=user_id,
                body="I couldn't hear or read that correctly. Could you please repeat?"
            )
            return

        # 2 & 3. Intent Detection & Handling via Orchestrator
        print("🧠 Routing to Orchestrator...", flush=True)
        logger.info("🧠 Routing to Orchestrator...")
        reply_prefix, context = ResponseOrchestrator.process(user_id, user_text)


        # 4. Generate AI Response
        print("🤖 Calling LLM for response...", flush=True)
        logger.info("🤖 Generating AI response...")
        system_prompt = f"""
You are an expert, friendly, and highly knowledgeable personal finance assistant.
Rules:
- Provide detailed, insightful, and knowledgeable answers in user-friendly terms.
- Use a supportive and conversational tone, like a trusted human financial advisor.
- Always try to provide proper, actionable suggestions, tips, or alternatives relevant to the user's query.
- Keep your response under 1000 characters so it fits neatly into a single WhatsApp message.
- Make your formatting easy to read (use emojis or short bullet points where appropriate).
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
        
        print("📤 Sending response via Twilio REST API...", flush=True)
        
        def chunk_message(msg_text, max_len=1500):
            chunks = []
            while len(msg_text) > max_len:
                split_at = msg_text.rfind('\n', 0, max_len)
                if split_at == -1:
                    split_at = msg_text.rfind(' ', 0, max_len)
                if split_at == -1:
                    split_at = max_len
                chunks.append(msg_text[:split_at].strip())
                msg_text = msg_text[split_at:].strip()
            if msg_text:
                chunks.append(msg_text)
            return chunks

        if audio_filename:
            media_url = f"{base_url}/media/{audio_filename}"
            print(f"🎧 Media URL for Twilio: {media_url}", flush=True)
            
            # Send the Audio File
            client.messages.create(
                from_=bot_id,
                to=user_id,
                media_url=[media_url]
            )
            
            # Send the Text
            final_text = f"{full_reply}\n\nListen: {media_url}"
            chunks = chunk_message(final_text)
            for chunk in chunks:
                client.messages.create(from_=bot_id, to=user_id, body=chunk)
        else:
            # Just text
            chunks = chunk_message(full_reply)
            for chunk in chunks:
                client.messages.create(from_=bot_id, to=user_id, body=chunk)

        print("✅ Background task complete!", flush=True)

    except Exception as e:
        print(f"❌ BACKGROUND TASK CRASHED: {e}", flush=True)
        traceback.print_exc()
        logger.error(f"❌ Background Error: {e}")
        try:
            # Attempt to inform the user something broke
            if 'client' in locals() and 'user_id' in locals() and 'bot_id' in locals():
                client.messages.create(
                    from_=bot_id,
                    to=user_id,
                    body="Sorry, I encountered an error processing your request. Let's try again in a moment."
                )
        except Exception:
            pass


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Main entry point for Twilio WhatsApp Webhook.
    """
    print("\n" + "="*50, flush=True)
    print("🔥 NEW WEBHOOK REQUEST RECEIVED (Fast Acknowledge)", flush=True)
    print("="*50, flush=True)
    logger.info("🔥 Incoming request to /whatsapp")
    
    try:
        # Get data and convert to dictionary safely
        form_data = await request.form()
        form_dict = dict(form_data)
        
        # We need the ngrok base URL for the background task to attach the media correctly
        base_url = str(request.base_url).rstrip("/")
        
        # Hand off the heavy processing to the background!
        background_tasks.add_task(process_and_reply, form_dict, base_url)

        # IMMEDIATELY answer Twilio with a blank TwiML response. 
        # This tells Twilio "I received the message" in < 1 second, avoiding the timeout.
        response = MessagingResponse()
        return Response(content=str(response), media_type="application/xml")

    except Exception as e:
        print(f"❌ WEBHOOK ROUTER CRASHED: {e}", flush=True)
        traceback.print_exc()
        logger.error(f"❌ Webhook Error: {e}")
        return generate_twiml_response("Sorry, I encountered a critical error.")


@router.get("/health")
async def health_check():
    logger.info("🏥 Health check ping")
    return {"status": "ok"}


def generate_twiml_response(text: str):
    """Fallback XML generator for fast router errors"""
    response = MessagingResponse()
    msg = response.message()
    msg.body(text[:1500])
    return Response(content=str(response), media_type="application/xml")