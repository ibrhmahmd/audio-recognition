from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from speech_recognitionr import recognize_speech
import os
from datetime import datetime, timedelta
from functools import lru_cache
import hashlib
from collections import defaultdict
import time
from pydantic import BaseModel, validator
from typing import Optional

app = FastAPI(
    title='Speech Recognition API',
    description='An API for transcribing audio files using Google Speech Recognition.',
    version='1.0.0'
)

requests_store = {}
RATE_LIMIT = 100  # requests per hour

analytics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "average_processing_time": 0,
    "processing_times": []
}

class AudioRequest(BaseModel):
    language: str = "en-US"
    enhance_audio: bool = False
    timeout: int = 30

    @validator("language")
    def validate_language(cls, v):
        supported_languages = ["en-US", "ar-EG", "es-ES"]
        if v not in supported_languages:
            raise ValueError(f"Language must be one of {supported_languages}")
        return v

    @validator("timeout")
    def validate_timeout(cls, v):
        if not (5 <= v <= 300):
            raise ValueError("Timeout must be between 5 and 300 seconds")
        return v

@app.get('/health')
async def health_check():
    return {'status': 'healthy'}

@app.post('/recognize')
async def recognize_audio(
    file: UploadFile = File(...),
    language: str = "en-US",
    enhance_audio: bool = False,
    timeout: int = 30
):
    if file.content_type != 'audio/wav':
        raise HTTPException(status_code=400, detail='Only WAV audio files are supported.')
    
    try:
        # Save the uploaded file temporarily
        temp_file_path = 'temp_audio.wav'
        with open(temp_file_path, 'wb') as buffer:
            buffer.write(await file.read())
        
        # Call your speech recognition function
        result = recognize_speech(temp_file_path)
        
        # Clean up the temporary file
        os.remove(temp_file_path)
        
        return {'transcription': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = datetime.now()
    
    if client_ip in requests_store:
        if len(requests_store[client_ip]) >= RATE_LIMIT:
            oldest_request = min(requests_store[client_ip])
            if current_time - oldest_request < timedelta(hours=1):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            requests_store[client_ip] = {r for r in requests_store[client_ip] 
                                       if current_time - r < timedelta(hours=1)}
    else:
        requests_store[client_ip] = set()
    
    requests_store[client_ip].add(current_time)
    response = await call_next(request)
    return response

@lru_cache(maxsize=100)
def get_cached_transcription(file_hash: str):
    return transcription_cache.get(file_hash)

def compute_file_hash(file_content: bytes) -> str:
    return hashlib.md5(file_content).hexdigest()

@app.get("/stats")
async def get_stats():
    return {
        "total_requests": analytics["total_requests"],
        "success_rate": analytics["successful_requests"] / analytics["total_requests"] if analytics["total_requests"] > 0 else 0,
        "average_processing_time": sum(analytics["processing_times"]) / len(analytics["processing_times"]) if analytics["processing_times"] else 0
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
