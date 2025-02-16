from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from speech_recognitionr import recognize_speech
import os

app = FastAPI(
    title='Speech Recognition API',
    description='An API for transcribing audio files using Google Speech Recognition.',
    version='1.0.0'
)

@app.get('/health')
async def health_check():
    return {'status': 'healthy'}

@app.post('/recognize')
async def recognize_audio(file: UploadFile = File(..., description='Upload an audio file in WAV format')):
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

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
