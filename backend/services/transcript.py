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
            content_type = "audio/mpeg"
            headers = {
                "Authorization": f"Token {settings.DEEPGRAM_API_KEY}",
                "Content-Type": content_type
            }
            
            audio_size = os.path.getsize(audio_path)
            logger.info(
                f"Sending audio to Deepgram\n"
                f"Audio Path: {audio_path}\n"
                f"Audio Size: {audio_size} bytes\n"
                f"Content-Type: {content_type}\n"
                f"Model: nova-2\n"
                f"API Key Present: {bool(settings.DEEPGRAM_API_KEY)}"
            )
            
            with open(audio_path, "rb") as audio_file:
                response = requests.post(url, headers=headers, data=audio_file, timeout=60)
                
            logger.info(
                f"Deepgram Status: {response.status_code}\n"
                f"Deepgram Headers: {dict(response.headers)}\n"
                f"Deepgram Response:\n{response.text}"
            )
                
            if response.status_code == 429:
                logger.error("Deepgram API rate limit exceeded")
                raise Exception("Deepgram API rate limit exceeded")
                
            response.raise_for_status()
            
            data = response.json()
            channels = data.get("results", {}).get("channels", [])
            alternatives = channels[0].get("alternatives", []) if channels else []
            alternative = alternatives[0] if alternatives else {}
            transcript = alternative.get("transcript", "")
            
            if not transcript:
                logger.warning(
                    f"Empty transcript returned from Deepgram\n"
                    f"Transcript Length: 0\n"
                    f"Confidence: {alternative.get('confidence', 'N/A')}\n"
                    f"Number of channels: {len(channels)}\n"
                    f"Number of alternatives: {len(alternatives)}\n"
                    f"Deepgram JSON:\n{json.dumps(data, indent=2)}"
                )
            else:
                with open(transcript_path, "w", encoding="utf-8") as f:
                    f.write(transcript)
                logger.info(f"Transcript saved to {transcript_path}")
                
            return transcript
            
        except requests.exceptions.RequestException as e:
            import traceback
            logger.error(
                f"Network error during transcription: {type(e).__name__}\n"
                f"Message: {str(e)}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            raise
        except Exception as e:
            import traceback
            logger.error(
                f"Unexpected error during transcription: {type(e).__name__}\n"
                f"Message: {str(e)}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            raise
