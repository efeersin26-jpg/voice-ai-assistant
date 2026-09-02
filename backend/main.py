from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import io
import logging

# Import service modules
from services.speech_to_text import transcribe_audio
from services.ai_service import get_ai_response
from services.text_to_speech import synthesize_text

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Voice AI Assistant API",
    description="Sesli konuşma destekli AI asistan",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend URL'ini belirt
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class TranscribeResponse(BaseModel):
    text: str
    confidence: float = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class SynthesizeRequest(BaseModel):
    text: str

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}

# Transcribe endpoint - Sesi metne çevir
@app.post("/api/transcribe", response_model=TranscribeResponse)
async def transcribe(audio: UploadFile = File(...)):
    """
    Sesli dosyayı metne çevirir.
    
    - **audio**: WAV veya MP3 formatında ses dosyası
    """
    try:
        logger.info(f"Transcribing file: {audio.filename}")
        
        # Dosya içeriğini oku
        contents = await audio.read()
        
        # Speech-to-Text servisi ile işle
        result = transcribe_audio(contents)
        
        return TranscribeResponse(
            text=result.get("text", ""),
            confidence=result.get("confidence")
        )
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

# Chat endpoint - AI'ye soru sor
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Kullanıcının mesajına AI'nin yanıtını alır.
    
    - **message**: Kullanıcının yazılan veya transcribe edilmiş mesajı
    """
    try:
        logger.info(f"Chat message: {request.message}")
        
        # AI servisi ile yanıt al
        response = get_ai_response(request.message)
        
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

# Synthesize endpoint - Metni sese çevir
@app.post("/api/synthesize")
async def synthesize(request: SynthesizeRequest):
    """
    Metni konuşma sesine çevirir.
    
    - **text**: Sese çevrilecek metin
    
    Returns: MP3 ses dosyası
    """
    try:
        logger.info(f"Synthesizing text: {request.text[:50]}...")
        
        # Text-to-Speech servisi ile ses dosyası oluştur
        audio_content = synthesize_text(request.text)
        
        # Ses dosyasını döndür
        return FileResponse(
            io.BytesIO(audio_content),
            media_type="audio/mp3",
            headers={"Content-Disposition": "attachment; filename=response.mp3"}
        )
    except Exception as e:
        logger.error(f"Synthesis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

# Full pipeline endpoint - Hepsini bir çekin
@app.post("/api/voice-chat")
async def voice_chat(audio: UploadFile = File(...)):
    """
    Tam pipeline: Ses → Metin → AI Yanıtı → Ses
    
    - **audio**: Kullanıcının sesli girdisi
    
    Returns: AI'nin sesli yanıtı
    """
    try:
        logger.info("Starting full voice chat pipeline...")
        
        # 1. Transcribe
        contents = await audio.read()
        transcription = transcribe_audio(contents)
        user_message = transcription.get("text", "")
        logger.info(f"Transcribed: {user_message}")
        
        # 2. Get AI response
        ai_response = get_ai_response(user_message)
        logger.info(f"AI Response: {ai_response}")
        
        # 3. Synthesize
        audio_content = synthesize_text(ai_response)
        
        return FileResponse(
            io.BytesIO(audio_content),
            media_type="audio/mp3",
            headers={"Content-Disposition": "attachment; filename=response.mp3"}
        )
    except Exception as e:
        logger.error(f"Voice chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice chat failed: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Voice AI Assistant API",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "transcribe": "/api/transcribe (POST)",
            "chat": "/api/chat (POST)",
            "synthesize": "/api/synthesize (POST)",
            "voice_chat": "/api/voice-chat (POST)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
