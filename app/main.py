from fastapi import FastAPI, Request
from app.api.routes.whatsapp import router as whatsapp_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import time
import os


app = FastAPI(
    title="Voice Finance Assistant",
    version="1.0.0"
)

# Global Request Middleware for Debugging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    path = request.url.path
    method = request.method
    print(f"\n🚀 [MIDDLEWARE] Processing {method} request to {path}")
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    print(f"🏁 [MIDDLEWARE] Finished {method} {path} - Status: {response.status_code} - Duration: {duration:.2f}s")
    return response

app.include_router(whatsapp_router)

@app.get("/media/{filename}")
async def get_media(filename: str):
    file_path = f"app/media/{filename}"
    print(f"📥 Twilio fetching media: {filename}", flush=True)
    
    if not os.path.exists(file_path):
        print(f"❌ Media not found: {file_path}", flush=True)
        return {"error": "File not found"}
    
    # Simpler MIME type for maximal compatibility
    media_type = "audio/mpeg" if filename.endswith(".mp3") else "audio/ogg"
    return FileResponse(file_path, media_type=media_type)


@app.get("/")
def root():
    return {"message": "Voice Finance Assistant is running 🚀"}