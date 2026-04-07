from fastapi import FastAPI
from app.api.routes.whatsapp import router as whatsapp_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(
    title="Voice Finance Assistant",
    version="1.0.0"
)

app.include_router(whatsapp_router)
@app.get("/media/{filename}")
async def get_media(filename: str):
    file_path = f"app/media/{filename}"
    if filename.endswith(".mp3"):
        return FileResponse(file_path, media_type="audio/mpeg")
    return FileResponse(file_path, media_type="audio/ogg")


@app.get("/")
def root():
    return {"message": "Voice Finance Assistant is running 🚀"}