import os
import json
import requests
from core.logger import setup_logger
from core.config import settings

logger = setup_logger("transcript_service")

class TranscriptService:
    def transcribe(self, audio_path: str) -> str:
        logger.info(f"Transcribing audio: {audio_path}")
        
        if not settings.DEEPGRAM_API_KEY:
            logger.error("Deepgram API key is missing")
            raise ValueError("Deepgram API key is missing")
            
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        transcript_path = os.path.join(settings.CACHE_DIR, f"{base_name}_transcript.txt")
        
        if os.path.exists(transcript_path):
            logger.info(f"Transcript already exists: {transcript_path}")
            with open(transcript_path, "r", encoding="utf-8") as f:
                return f.read()
                
        try:
            url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true"
            headers = {
                "Authorization": f"Token {settings.DEEPGRAM_API_KEY}",
                "Content-Type": "audio/mp3"
            }
            
            with open(audio_path, "rb") as audio_file:
                response = requests.post(url, headers=headers, data=audio_file, timeout=60)
                
            if response.status_code == 429:
                logger.error("Deepgram API rate limit exceeded")
                raise Exception("Deepgram API rate limit exceeded")
                
            response.raise_for_status()
            
            data = response.json()
            transcript = data.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
            
            if not transcript:
                logger.warning("Empty transcript returned from Deepgram")
            else:
                with open(transcript_path, "w", encoding="utf-8") as f:
                    f.write(transcript)
                logger.info(f"Transcript saved to {transcript_path}")
                
            return transcript
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during transcription: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {str(e)}")
            raise
