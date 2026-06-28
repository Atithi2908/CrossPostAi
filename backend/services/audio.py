import os
import subprocess
from core.logger import setup_logger
from core.config import settings

logger = setup_logger("audio_service")

class AudioService:
    def extract_audio(self, video_path: str) -> str:
        logger.info(f"Extracting audio from {video_path}")
        
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_path = os.path.join(settings.CACHE_DIR, f"{base_name}.mp3")
        
        if os.path.exists(audio_path):
            audio_size = os.path.getsize(audio_path)
            logger.info(f"Using cached audio\nAudio Path: {audio_path}\nAudio Size: {audio_size} bytes")
            return audio_path
            
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            
            command = [
                ffmpeg_exe,
                "-i", video_path,
                "-q:a", "0",
                "-map", "a",
                "-y", # overwrite output
                audio_path
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg failed: {result.stderr}")
                raise RuntimeError(f"FFmpeg failed to extract audio: {result.stderr}")
                
            audio_exists = os.path.exists(audio_path)
            audio_size = os.path.getsize(audio_path) if audio_exists else 0
            
            logger.info(
                f"Audio extracted successfully\n"
                f"Audio Path: {audio_path}\n"
                f"Audio Exists: {audio_exists}\n"
                f"Audio Size: {audio_size} bytes\n"
                f"FFmpeg Executable: {ffmpeg_exe}"
            )
            return audio_path
            
        except Exception as e:
            logger.error(f"Error during audio extraction: {str(e)}")
            raise
